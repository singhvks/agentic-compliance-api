import uuid
import time
from fastapi import APIRouter, BackgroundTasks, Form, UploadFile, File, HTTPException
from typing import Optional

from app.core.logging import logger
from app.core.config import settings
from app.core.llm.factory import get_llm_client
from app.models.response_models import JobStatusResponse, ComplianceReportResponse, AnalysisMetadata
from app.storage.document_store import document_store
from app.pipeline.parser import DocumentParser
from app.pipeline.chunker import StaticChunker
from app.pipeline.embeddings import EmbeddingsGenerator
from app.pipeline.vector_store import FAISSVectorStore
from app.pipeline.retrieval import DocumentRetriever, load_rules
from app.pipeline.analyzer import ComplianceAnalyzer
from app.pipeline.judge import ComplianceJudge

router = APIRouter()

def sync_analysis_pipeline(job_id: str, file_path: str, country: str, industry: Optional[str] = None):
    """
    The main background worker that runs the full RAG and Analysis pipeline.
    """
    logger.info("Starting background analysis task", job_id=job_id)
    start_time = time.time()
    
    try:
        # 1. Parse Document
        logger.debug("Parsing document", job_id=job_id)
        paginated_text = DocumentParser.parse(file_path)
        
        # 2. Chunking
        logger.debug("Chunking document", job_id=job_id)
        chunker = StaticChunker()
        chunks = chunker.chunk_document(document_id=job_id, paginated_text=paginated_text)
        
        if not chunks:
            raise ValueError("Document yielded no text chunks to analyze.")
            
        # 3. Embeddings
        logger.debug("Generating embeddings", job_id=job_id)
        embeddings_gen = EmbeddingsGenerator()
        chunk_texts = [c.text for c in chunks]
        chunk_embeddings = embeddings_gen.generate(chunk_texts)
        
        # 4. Vector Storage
        logger.debug("Storing vectors", job_id=job_id)
        vector_store = FAISSVectorStore(job_id)
        vector_store.add_embeddings(chunk_embeddings, chunks)
        vector_store.save()
        
        # 5. Initialization for Retrieval & Analysis
        llm = get_llm_client()
        retriever = DocumentRetriever(embeddings_gen, vector_store)
        analyzer = ComplianceAnalyzer(llm)
        judge = ComplianceJudge(llm)
        
        rules = load_rules(jurisdiction=country)
        logger.info(f"Loaded {len(rules)} compliance rules for evaluation.", job_id=job_id)
        
        violations = []
        chunks_analyzed = 0
        
        # 6. Evaluation Loop
        for rule in rules:
            logger.debug(f"Evaluating rule", job_id=job_id, rule_id=rule.rule_id)
            # Retrieve relevant chunks with deterministic filter
            relevant_chunks = retriever.retrieve_relevant_chunks(rule)
            
            if not relevant_chunks:
                logger.debug(f"Rule {rule.rule_id} skipped: No relevant high-risk chunks found.")
                continue
                
            chunks_analyzed += len(relevant_chunks)
            
            # Analyze
            violation = analyzer.analyze_chunks(rule, relevant_chunks)
            
            if violation:
                # Judge Validation
                validated_violation = judge.validate_violation(violation)
                violations.append(validated_violation)
                
        # 7. Generate Final Report
        processing_time = time.time() - start_time
        logger.info("Analysis pipeline completed successfully", job_id=job_id, time=processing_time)
        
        report = ComplianceReportResponse(
            document_id=job_id,
            jurisdiction=country,
            violations=violations,
            analysis_metadata=AnalysisMetadata(
                model_used=settings.MODEL_NAME,
                chunks_analyzed=chunks_analyzed
            )
        )
        
        # Save Report
        document_store.save_report(job_id, report.model_dump())

    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        logger.error(f"Pipeline crashed", job_id=job_id, error=str(e), trace=error_trace)
        document_store.save_failed(job_id, error=str(e))

@router.post("/analyze", response_model=JobStatusResponse)
async def start_analysis(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    country: str = Form(...),
    industry: Optional[str] = Form(None)
):
    """
    Upload a document and start the compliance analysis processing pipeline asynchronously.
    """
    job_id = str(uuid.uuid4())
    logger.info("Received analyze request", job_id=job_id, filename=file.filename)
    
    # Init state
    document_store.create_job(job_id)
    content_bytes = await file.read()
    
    # Save file
    file_path = document_store.save_document(job_id, file.filename, content_bytes)
    
    # Schedule background processing
    background_tasks.add_task(sync_analysis_pipeline, job_id, file_path, country, industry)
    
    return JobStatusResponse(job_id=job_id, status="processing")

@router.get("/status/{job_id}", response_model=JobStatusResponse)
def check_status(job_id: str):
    """
    Check the status of a scheduled analysis job.
    """
    status_data = document_store.get_job_status(job_id)
    if not status_data:
        raise HTTPException(status_code=404, detail="Job ID not found")
        
    return JobStatusResponse(job_id=status_data.get("job_id"), status=status_data.get("status"))

@router.get("/report/{job_id}", response_model=ComplianceReportResponse)
def retrieve_report(job_id: str):
    """
    Retrieve the finalized compliance report if processing is completed.
    """
    status_data = document_store.get_job_status(job_id)
    if not status_data:
        raise HTTPException(status_code=404, detail="Job ID not found")
        
    if status_data.get("status") == "failed":
        raise HTTPException(status_code=500, detail=f"Job failed during processing: {status_data.get('error')}")
        
    if status_data.get("status") != "completed":
        raise HTTPException(status_code=400, detail="Report is not yet ready. Check status endpoint.")
        
    report_data = document_store.get_report(job_id)
    if not report_data:
        raise HTTPException(status_code=404, detail="Report file not found")
        
    return ComplianceReportResponse(**report_data)
