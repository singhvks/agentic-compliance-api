import json
from typing import Optional

from app.core.llm.base import BaseLLM
from app.core.logging import logger
from app.models.response_models import AnalysisViolation

class ComplianceJudge:
    """Second-pass validation of the Analyzer LLM output to assign confidence and recommendations."""
    
    def __init__(self, llm_client: BaseLLM):
        self.llm = llm_client
        
    def validate_violation(self, violation: AnalysisViolation) -> AnalysisViolation:
        """
        Ask the LLM to judge the identified violation, providing a confidence score and a recommendation.
        Updates and returns the AnalysisViolation object.
        """
        system_prompt = (
            "You are a senior compliance auditor and AI verifier.\n"
            "Review the provided AI-generated compliance violation report and evaluate its validity, completeness, and logical consistency.\n"
            # Format requirements...
            "Respond in strictly JSON format with exactly 2 keys:\n"
            "- 'confidence': (float 0.0 to 1.0) your confidence that the violation is accurately reported and justified by the cited text.\n"
            "- 'recommendation': (string) actionable advice on how to remediate the violation."
        )
        
        prompt = (
            f"VIOLATION ANALYSIS REPORT:\n"
            f"Rule ID: {violation.rule_id}\n"
            f"Severity: {violation.severity}/10\n"
            f"Description: {violation.description}\n"
            f"Cited Text (Page {violation.citation.page}): \"{violation.citation.text}\"\n\n"
            f"Please evaluate this analysis and return the required JSON."
        )
        
        try:
            logger.debug(f"Validating violation for rule {violation.rule_id} via Judge LLM.")
            response_json = self.llm.generate_json(prompt=prompt, system_prompt=system_prompt)
            data = json.loads(response_json)
            
            violation.confidence = float(data.get("confidence", 0.5))
            violation.recommendation = str(data.get("recommendation", "Review the highlighted section for compliance."))
            
        except json.JSONDecodeError:
            logger.error(f"Failed to decode Judge LLM JSON response for rule {violation.rule_id}")
            violation.confidence = 0.5
            violation.recommendation = "Manual review required due to evaluation error."
        except Exception as e:
            logger.error(f"Error during Judge LLM validation for rule {violation.rule_id}: {e}")
            violation.confidence = 0.0
            violation.recommendation = f"Validation failed: {str(e)}"
            
        return violation
