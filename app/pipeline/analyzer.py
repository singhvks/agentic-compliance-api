import json
from typing import List, Dict, Any, Optional

from app.core.llm.base import BaseLLM
from app.core.logging import logger
from app.models.domain_models import ComplianceRule, ChunkMetadata
from app.models.response_models import AnalysisViolation, AnalysisCitation

class ComplianceAnalyzer:
    """Invokes LLM to check relevant text chunks for compliance rule violations."""
    
    def __init__(self, llm_client: BaseLLM):
        self.llm = llm_client
        
    def analyze_chunks(self, rule: ComplianceRule, chunks: List[ChunkMetadata]) -> Optional[AnalysisViolation]:
        """
        Analyze a set of candidate chunks against a compliance rule.
        Returns an AnalysisViolation object if a violation is found, otherwise None.
        """
        if not chunks:
            return None
            
        system_prompt = (
            "You are an expert compliance and security auditor. "
            "Your task is to review the provided text segments from a document and determine if they violate the specified rule.\n"
            "If you detect a violation, provide a structured JSON response with the following keys:\n"
            "- 'violates_rule': (boolean) true if the rule is violated.\n"
            "- 'description': (string) detailed explanation of the violation.\n"
            "- 'severity': (integer 1-10) severity of the violation.\n"
            "- 'citation_page': (integer) the page number where the violation occurs.\n"
            "- 'citation_text': (string) the exact text quote that demonstrates the violation.\n\n"
            "If there is NO violation, respond with: {\"violates_rule\": false}"
        )
        
        # Format the context from candidate chunks
        context_text = ""
        for i, chunk in enumerate(chunks):
            context_text += f"--- SEGMENT {i+1} (Page {chunk.page_number}) ---\n{chunk.text}\n\n"
            
        prompt = (
            f"RULE TO EVALUATE:\n"
            f"ID: {rule.rule_id}\n"
            f"Description: {rule.description or rule.rule}\n\n"
            f"DOCUMENT TEXT SEGMENTS:\n{context_text}\n"
            f"Analyze the document text and output the required JSON format."
        )
        
        try:
            logger.debug(f"Sending prompt to LLM for rule {rule.rule_id}")
            response_json = self.llm.generate_json(prompt=prompt, system_prompt=system_prompt)
            data = json.loads(response_json)
            
            if data.get("violates_rule") is True:
                # We defer confidence and recommendation to the Judge, 
                # but we populate placeholders here to satisfy the internal API contract prior to judging.
                return AnalysisViolation(
                    rule_id=rule.rule_id,
                    description=data.get("description", "Violates compliance rule."),
                    severity=data.get("severity", 5),
                    citation=AnalysisCitation(
                        page=data.get("citation_page", chunks[0].page_number),
                        text=data.get("citation_text", chunks[0].text[:50] + "...")
                    ),
                    confidence=0.0,
                    recommendation=""
                )
            
        except json.JSONDecodeError:
            logger.error(f"Failed to decode LLM JSON response for rule {rule.rule_id}")
        except Exception as e:
            logger.error(f"Error during LLM analysis for rule {rule.rule_id}: {e}")
            
        return None
