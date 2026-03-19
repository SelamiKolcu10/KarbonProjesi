"""API tests for orchestrator endpoints in src/api.py."""

import sys
import importlib.util
from pathlib import Path

from fastapi.testclient import TestClient

project_root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(project_root / "src"))

api_file = project_root / "src" / "api.py"
spec = importlib.util.spec_from_file_location("project_api", api_file)
if spec is None or spec.loader is None:
    raise RuntimeError(f"API module yuklenemedi: {api_file}")
api_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(api_module)
import src.orchestration.orchestrator as orchestrator_module
from src.agents.strategist import (
    ComplianceRiskReport,
    ExecutiveConsultingReport,
    Recommendation,
)
from src.orchestration.orchestrator import Orchestrator


def _valid_payload_dict() -> dict:
    return {
        "facility_name": "API Test Facility",
        "facility_id": "TR-API-001",
        "reporting_period": "2026-Q1",
        "production_quantity_tons": 100.0,
        "electricity_consumption_mwh": 150.0,
        "natural_gas_consumption_m3": 4000.0,
        "coal_consumption_tons": 0.0,
        "cbam_allocation_rate": 0.5,
    }


def _invalid_payload_dict() -> dict:
    return {
        "facility_name": "API Invalid Facility",
        "facility_id": "TR-API-002",
        "reporting_period": "2026-Q1",
        "production_quantity_tons": 0.0,
        "electricity_consumption_mwh": 50.0,
        "natural_gas_consumption_m3": 1000.0,
        "coal_consumption_tons": 0.0,
        "cbam_allocation_rate": 0.5,
    }


def test_orchestrator_submit_rejected_by_guard() -> None:
    api_module.orchestrator = Orchestrator()
    client = TestClient(api_module.app)

    response = client.post("/api/orchestrator/jobs", json=_invalid_payload_dict())
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "REJECTED_BY_GUARD"
    assert data["error_message"] is not None

    status_response = client.get(f"/api/orchestrator/jobs/{data['job_id']}")
    assert status_response.status_code == 200
    status_data = status_response.json()
    assert status_data["status"] == "REJECTED_BY_GUARD"


def test_orchestrator_manual_process_completed(monkeypatch) -> None:
    class FakeChiefConsultantAgent:
        def generate_report(self, payload):
            return ExecutiveConsultingReport(
                facility_name=payload.facility_name,
                reporting_period=payload.reporting_period,
                audit_summary={"total_emissions_tco2e": 10.0},
                compliance_risk=ComplianceRiskReport(
                    readiness_score=95.0,
                    missing_mandatory_fields=[],
                    estimated_penalty_eur=0.0,
                    threshold_warnings=[],
                    deadline_status="On Time",
                    supplier_benchmark_warnings=[],
                    cost_of_dirty_supply_eur=0.0,
                ),
                top_recommendations=[
                    Recommendation(
                        strategy_name="Green Shift",
                        action_plan="Switch to renewable electricity",
                        co2_reduction_tons=5.0,
                        annual_savings_eur=1000.0,
                        estimated_capex_eur=2000.0,
                        payback_period_years=2.0,
                        implementation_difficulty="Medium",
                        potential_subsidies=[],
                    )
                ],
                five_year_projection={2026: 100.0, 2027: 150.0, 2028: 200.0, 2029: 300.0, 2030: 400.0},
                stress_test_scenarios={"Base Case": 100.0, "Best Case": 80.0, "Worst Case": 130.0},
                ai_consultant_summary="Risk low, optimization opportunity available.",
            )

    monkeypatch.setattr(
        orchestrator_module,
        "ChiefConsultantAgent",
        FakeChiefConsultantAgent,
    )

    api_module.orchestrator = Orchestrator()
    client = TestClient(api_module.app)
    payload = _valid_payload_dict()

    submit_response = client.post("/api/orchestrator/jobs", json=payload)
    assert submit_response.status_code == 200
    job_id = submit_response.json()["job_id"]

    process_response = client.post(f"/api/orchestrator/jobs/{job_id}/process", json=payload)
    assert process_response.status_code == 200
    process_data = process_response.json()
    assert process_data["status"] == "COMPLETED"
    assert process_data["result"]["facility_name"] == "API Test Facility"


def test_orchestrator_manual_process_failed(monkeypatch) -> None:
    class FailingChiefConsultantAgent:
        def generate_report(self, payload):
            raise RuntimeError("api mock failure")

    monkeypatch.setattr(
        orchestrator_module,
        "ChiefConsultantAgent",
        FailingChiefConsultantAgent,
    )

    api_module.orchestrator = Orchestrator()
    client = TestClient(api_module.app)
    payload = _valid_payload_dict()

    submit_response = client.post("/api/orchestrator/jobs", json=payload)
    assert submit_response.status_code == 200
    job_id = submit_response.json()["job_id"]

    process_response = client.post(f"/api/orchestrator/jobs/{job_id}/process", json=payload)
    assert process_response.status_code == 200
    process_data = process_response.json()
    assert process_data["status"] == "FAILED"
    assert "api mock failure" in process_data["error_message"]


def test_orchestrator_status_not_found() -> None:
    api_module.orchestrator = Orchestrator()
    client = TestClient(api_module.app)

    response = client.get("/api/orchestrator/jobs/not-a-real-id")
    assert response.status_code == 404
