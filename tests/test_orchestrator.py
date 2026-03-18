"""Tests for Orchestrator job lifecycle management."""

from src.agents.auditor.models import InputPayload
from src.orchestration import orchestrator as orchestrator_module
from src.orchestration.orchestrator import JobStatus, Orchestrator


def _valid_payload() -> InputPayload:
    return InputPayload(
        facility_name="Test Facility",
        facility_id="TR-TEST-001",
        reporting_period="2026-Q1",
        production_quantity_tons=100.0,
        electricity_consumption_mwh=120.0,
        natural_gas_consumption_m3=5000.0,
        coal_consumption_tons=0.0,
        cbam_allocation_rate=0.5,
    )


def _invalid_payload_for_guard() -> InputPayload:
    return InputPayload(
        facility_name="Invalid Facility",
        facility_id="TR-TEST-002",
        reporting_period="2026-Q1",
        production_quantity_tons=0.0,
        electricity_consumption_mwh=50.0,
        natural_gas_consumption_m3=1000.0,
        coal_consumption_tons=0.0,
        cbam_allocation_rate=0.5,
    )


def test_submit_job_creates_pending_record_for_valid_payload() -> None:
    orchestrator = Orchestrator()
    job_id = orchestrator.submit_job(_valid_payload())

    job = orchestrator.get_job_status(job_id)
    assert job.job_id == job_id
    assert job.status == JobStatus.PENDING
    assert job.error_message is None


def test_submit_job_rejects_invalid_payload_with_guard_error() -> None:
    orchestrator = Orchestrator()
    job_id = orchestrator.submit_job(_invalid_payload_for_guard())

    job = orchestrator.get_job_status(job_id)
    assert job.status == JobStatus.REJECTED_BY_GUARD
    assert job.error_message is not None
    assert "Critical Anomaly" in job.error_message


def test_process_job_marks_completed_and_persists_result(monkeypatch) -> None:
    class FakeChiefConsultantAgent:
        def generate_report(self, payload: InputPayload):
            return "MOCK_REPORT"

    monkeypatch.setattr(
        orchestrator_module,
        "ChiefConsultantAgent",
        FakeChiefConsultantAgent,
    )

    orchestrator = Orchestrator()
    payload = _valid_payload()
    job_id = orchestrator.submit_job(payload)

    orchestrator.process_job(job_id, payload)

    job = orchestrator.get_job_status(job_id)
    assert job.status == JobStatus.COMPLETED
    assert job.result == "MOCK_REPORT"
    assert job.error_message is None


def test_process_job_marks_failed_on_exception(monkeypatch) -> None:
    class FailingChiefConsultantAgent:
        def generate_report(self, payload: InputPayload):
            raise RuntimeError("mock failure")

    monkeypatch.setattr(
        orchestrator_module,
        "ChiefConsultantAgent",
        FailingChiefConsultantAgent,
    )

    orchestrator = Orchestrator()
    payload = _valid_payload()
    job_id = orchestrator.submit_job(payload)

    orchestrator.process_job(job_id, payload)

    job = orchestrator.get_job_status(job_id)
    assert job.status == JobStatus.FAILED
    assert job.error_message is not None
    assert "mock failure" in job.error_message
