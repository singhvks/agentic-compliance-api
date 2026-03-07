from pydantic import BaseModel, Field
from typing import List, Optional

class JobStatusResponse(BaseModel):
    """Response schema for job status check."""
    job_id: str = Field(..., description="Unique identifier for the analysis job")
    status: str = Field(..., description="Current status: processing | completed | failed")

class AnalysisCitation(BaseModel):
    """Schema for a citation to a specific part of a document."""
    page: int = Field(..., description="The page number where the violation was found")
    text: str = Field(..., description="The exact text snippet that violates the rule")

class AnalysisViolation(BaseModel):
    """Schema for a single compliance violation found by the LLM."""
    rule_id: str = Field(..., description="The ID of the compliance rule that was violated")
    description: str = Field(..., description="Description of the violation")
    severity: int = Field(..., description="Severity score from 1 to 10")
    citation: AnalysisCitation = Field(..., description="Citation to the exact text in the document")
    confidence: float = Field(..., description="Judge's confidence score between 0.0 and 1.0")
    recommendation: str = Field(..., description="Recommendation to fix the violation")

class AnalysisMetadata(BaseModel):
    """Schema for analysis run metadata."""
    model_used: str = Field(..., description="The LLM model used for the analysis")
    chunks_analyzed: int = Field(..., description="Number of text chunks that were sent to the LLM")

class ComplianceReportResponse(BaseModel):
    """Full structured compliance report response schema."""
    document_id: str = Field(..., description="Identifier for the analyzed document")
    jurisdiction: str = Field(..., description="The requested jurisdiction (country/region)")
    violations: List[AnalysisViolation] = Field(..., description="List of detected compliance violations")
    analysis_metadata: AnalysisMetadata = Field(..., description="Metadata about the analysis process")
