"""RegressionAgent for deterministic CBAM math regression testing.

This module can be used in CI/CD pipelines or run manually from the terminal.
"""

from __future__ import annotations

import sys
from dataclasses import dataclass
from typing import List

from pydantic import BaseModel, Field

from src.agents.auditor.models import InputPayload, PrecursorInput, ProcessInputs
from src.orchestration import JobStatus, Orchestrator


class RegressionFailureException(Exception):
    """Raised when one or more regression tests fail."""


class TestCase(BaseModel):
    """Regression test contract for baseline comparisons."""

    test_name: str
    payload: InputPayload
    expected_total_emissions: float
    expected_tax_liability: float
    tolerance: float = Field(default=0.01, gt=0.0)


@dataclass
class _AssertionResult:
    """Internal container for per-metric assertion output."""

    metric_name: str
    expected: float
    actual: float
    delta: float
    passed: bool


class RegressionAgent:
    """Runs golden-baseline regression checks against the Orchestrator pipeline."""

    def __init__(self, orchestrator: Orchestrator | None = None) -> None:
        self.orchestrator = orchestrator or Orchestrator()

    def load_synthetic_baselines(self) -> List[TestCase]:
        """Return hardcoded synthetic factory profiles used as golden baselines.

        Note:
            DataQualityGuard currently requires cbam_allocation_rate < 1.0, so the
            heavy-steel scenario uses 0.99 as near-1.0 allocation.
        """
        heavy_steel_payload = InputPayload(
            facility_name="Synthetic Heavy Steel Plant",
            facility_id="SYN-HS-001",
            reporting_period="2026-Q2",
            production_quantity_tons=2000.0,
            electricity_consumption_mwh=2500.0,
            natural_gas_consumption_m3=120000.0,
            coal_consumption_tons=80.0,
            process_inputs=ProcessInputs(
                electrode_consumption_ton=30.0,
                limestone_consumption_ton=100.0,
            ),
            precursors=[
                PrecursorInput(
                    material_name="ferro-manganese",
                    quantity_ton=50.0,
                    embedded_emissions_factor=None,
                ),
                PrecursorInput(
                    material_name="pig-iron",
                    quantity_ton=40.0,
                    embedded_emissions_factor=None,
                ),
            ],
            cbam_allocation_rate=0.99,
            data_source="manual",
        )

        allocated_clean_payload = InputPayload(
            facility_name="Synthetic Allocated Clean Factory",
            facility_id="SYN-CF-002",
            reporting_period="2026-Q2",
            production_quantity_tons=4000.0,
            electricity_consumption_mwh=1200.0,
            natural_gas_consumption_m3=20000.0,
            coal_consumption_tons=0.0,
            process_inputs=ProcessInputs(
                electrode_consumption_ton=5.0,
                limestone_consumption_ton=20.0,
            ),
            precursors=[],
            cbam_allocation_rate=0.5,
            dynamic_grid_factor=0.1,
            data_source="manual",
        )

        return [
            TestCase(
                test_name="Standard Heavy Steel",
                payload=heavy_steel_payload,
                expected_total_emissions=1834.86,
                expected_tax_liability=3899.08,
                tolerance=0.01,
            ),
            TestCase(
                test_name="Allocated Clean Factory",
                payload=allocated_clean_payload,
                expected_total_emissions=94.77,
                expected_tax_liability=201.38,
                tolerance=0.01,
            ),
        ]

    def run_regression_suite(self) -> bool:
        """Execute all regression baselines and raise on failure for CI/CD break."""
        test_cases = self.load_synthetic_baselines()
        failures: List[str] = []

        print("\n" + "=" * 88)
        print("CBAM REGRESSION SUITE")
        print("=" * 88)

        for case in test_cases:
            job_id = self.orchestrator.submit_job(case.payload)
            job = self.orchestrator.get_job_status(job_id)

            if job.status == JobStatus.REJECTED_BY_GUARD:
                failure_line = (
                    f"[FAIL] - {case.test_name} | Rejected by guard: {job.error_message}"
                )
                print(failure_line)
                failures.append(failure_line)
                continue

            self.orchestrator.process_job(job_id, case.payload)
            job = self.orchestrator.get_job_status(job_id)

            if job.status != JobStatus.COMPLETED or job.result is None:
                failure_line = (
                    f"[FAIL] - {case.test_name} | Job status: {job.status.value} "
                    f"| Error: {job.error_message or 'unknown'}"
                )
                print(failure_line)
                failures.append(failure_line)
                continue

            actual_total_emissions = float(
                job.result.audit_summary.get("total_emissions_tco2e", 0.0)
            )
            actual_tax_liability = float(
                job.result.audit_summary.get("effective_liability_eur", 0.0)
            )

            emissions_check = self._assert_metric(
                metric_name="Total Emissions",
                expected=case.expected_total_emissions,
                actual=actual_total_emissions,
                tolerance=case.tolerance,
            )
            tax_check = self._assert_metric(
                metric_name="Effective Liability",
                expected=case.expected_tax_liability,
                actual=actual_tax_liability,
                tolerance=case.tolerance,
            )

            if emissions_check.passed and tax_check.passed:
                print(
                    f"[PASS] - {case.test_name} | "
                    f"Emissions Expected: {emissions_check.expected:.2f} | "
                    f"Actual: {emissions_check.actual:.2f} | "
                    f"Delta: {emissions_check.delta:.4f} || "
                    f"Tax Expected: {tax_check.expected:.2f} | "
                    f"Actual: {tax_check.actual:.2f} | "
                    f"Delta: {tax_check.delta:.4f}"
                )
            else:
                if not emissions_check.passed:
                    failure_line = (
                        f"[FAIL] - {case.test_name} | Emissions Expected: "
                        f"{emissions_check.expected:.2f} | "
                        f"Actual: {emissions_check.actual:.2f} | "
                        f"Delta: {emissions_check.delta:.4f}"
                    )
                    print(failure_line)
                    failures.append(failure_line)

                if not tax_check.passed:
                    failure_line = (
                        f"[FAIL] - {case.test_name} | Tax Expected: "
                        f"{tax_check.expected:.2f} | "
                        f"Actual: {tax_check.actual:.2f} | "
                        f"Delta: {tax_check.delta:.4f}"
                    )
                    print(failure_line)
                    failures.append(failure_line)

        print("-" * 88)
        if failures:
            print(f"Regression suite result: FAILED ({len(failures)} failure(s))")
            raise RegressionFailureException("Regression suite failed.\n" + "\n".join(failures))

        print(f"Regression suite result: PASSED ({len(test_cases)}/{len(test_cases)})")
        return True

    @staticmethod
    def _assert_metric(
        metric_name: str,
        expected: float,
        actual: float,
        tolerance: float,
    ) -> _AssertionResult:
        """Compare expected/actual values with tolerance-aware assertion."""
        delta = abs(actual - expected)
        return _AssertionResult(
            metric_name=metric_name,
            expected=expected,
            actual=actual,
            delta=delta,
            passed=delta <= tolerance,
        )


if __name__ == "__main__":
    agent = RegressionAgent()
    try:
        ok = agent.run_regression_suite()
        sys.exit(0 if ok else 1)
    except RegressionFailureException as exc:
        print(str(exc))
        sys.exit(1)
