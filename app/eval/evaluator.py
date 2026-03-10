import json
from pathlib import Path
from typing import List, Dict, Any

from app.core.logging import logger
from app.models.domain_models import EvaluatorResult

class Evaluator:
    """Evaluates the Architecture Compliance Reviewer against the evaluation dataset."""
    
    def __init__(self):
        self.docs_dir = Path("architecture_docs")
        self.expected_dir = Path("expected_results")
        self.policies_path = Path("policies/security_policies.json")
        
    def _load_expected(self, doc_name: str) -> List[str]:
        """Loads the expected rule violation IDs for a document."""
        expected_file = self.expected_dir / f"{doc_name}.json"
        
        if not expected_file.exists():
            logger.warning(f"No expected results found. Expected at {expected_file}. Returning empty list.")
            return []
            
        try:
            with open(expected_file, "r") as f:
                data = json.load(f)
                return [v.get("rule_id") for v in data.get("violations", []) if "rule_id" in v]
        except Exception as e:
            logger.error(f"Failed to read expected results for {doc_name}: {e}")
            return []

    def evaluate_doc(self, doc_name: str, detected_violations: List[str]) -> EvaluatorResult:
        """Compares detected violations with expected violations."""
        expected = self._load_expected(doc_name)
        
        expected_set = set(expected)
        detected_set = set(detected_violations)
        
        tp = len(expected_set.intersection(detected_set))
        fp = len(detected_set - expected_set)
        fn = len(expected_set - detected_set)
        
        precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
        f1 = (2 * precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0
        
        return EvaluatorResult(
            document=doc_name,
            expected_violations=len(expected_set),
            detected_violations=len(detected_set),
            true_positives=tp,
            false_positives=fp,
            false_negatives=fn,
            precision=precision,
            recall=recall,
            f1_score=f1
        )
        
    def run_evaluation(self, results: Dict[str, List[str]]):
        """Run evaluation across a dictionary of {document_name: [detected_rule_id1, ...]}"""
        eval_results = []
        
        for doc_name, detected in results.items():
            result = self.evaluate_doc(doc_name, detected)
            eval_results.append(result)
            
        # Compute macro averages
        avg_precision = sum(r.precision for r in eval_results) / len(eval_results) if eval_results else 0
        avg_recall = sum(r.recall for r in eval_results) / len(eval_results) if eval_results else 0
        avg_f1 = sum(r.f1_score for r in eval_results) / len(eval_results) if eval_results else 0
        
        logger.info(f"--- Evaluation Complete across {len(eval_results)} documents ---")
        logger.info(f"Macro Precision: {avg_precision:.2f}")
        logger.info(f"Macro Recall: {avg_recall:.2f}")
        logger.info(f"Macro F1 Score: {avg_f1:.2f}")
        
        return {
            "macro_metrics": {
                "precision": avg_precision,
                "recall": avg_recall,
                "f1_score": avg_f1
            },
            "document_results": [r.model_dump() for r in eval_results]
        }
