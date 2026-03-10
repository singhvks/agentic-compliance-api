import os
from fastapi.testclient import TestClient
from app.main import app
from app.core.config import settings
from app.models.domain_models import ComplianceRule

def test_health_check():
    client = TestClient(app)
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "service": settings.PROJECT_NAME}

def test_models_import():
    from app.models.request_models import AnalysisRequest
    from app.models.response_models import JobStatusResponse
    from app.models.domain_models import EvaluatorResult
    
    assert True

def test_load_rules():
    from app.pipeline.retrieval import load_rules
    rules = load_rules()
    # Should load the security_policies.json that was provided
    assert len(rules) > 0
    assert any(r.rule_id == "SEC-001" for r in rules)
    
def test_mock_evaluator():
    from app.eval.evaluator import Evaluator
    evaluator = Evaluator()
    # Provide fake results that mis-match the missing expected_results
    eval_results = evaluator.run_evaluation({
        "arch_doc_01": ["SEC-001", "SEC-002"],
        "arch_doc_02": ["SEC-003"]
    })
    assert "macro_metrics" in eval_results
    assert eval_results["macro_metrics"]["precision"] >= 0.0
