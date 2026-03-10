from pydantic import BaseModel, Field
from typing import List, Optional

class ComplianceRule(BaseModel):
    """Schema representing a single compliance or security rule."""
    rule_id: str
    rule: Optional[str] = None # Name or short description
    description: Optional[str] = None
    keywords: Optional[List[str]] = Field(default_factory=list)
    severity: str | int # Can be 'critical', 'high' or an integer
    jurisdiction: Optional[str] = None

class ChunkMetadata(BaseModel):
    """Schema representing metadata for a text chunk."""
    chunk_id: str
    document_id: str
    page_number: int
    text: str

class EvaluatorResult(BaseModel):
    """Schema for an evaluator test result."""
    document: str
    expected_violations: int
    detected_violations: int
    true_positives: int
    false_positives: int
    false_negatives: int
    precision: float
    recall: float
    f1_score: float
