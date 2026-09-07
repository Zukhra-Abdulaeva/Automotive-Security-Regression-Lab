"""TC-001 — Diagnostic Authorization security test."""

from typing import Any

from security_lab.ecu_adapter import ECUAdapter
from security_lab.ecu_simulator import (
    ECUSimulator,
    ResponseStatus,
    SecurityMode,
)
from security_lab.evidence import Evidence, EvidenceGenerator
from security_lab.test_runner import (
    SecurityTestCase,
    SecurityTestRunner,
    TestResult,
)

TEST_ID = "TC-001"
TARGET = "simulated-ecu"
PROTECTED_OPERATION = "PROTECTED_OPERATION"


def _create_test_case(expected_status: ResponseStatus) -> SecurityTestCase:
    """Create the TC-001 protected-operation test case."""
    return SecurityTestCase(
        test_id=TEST_ID,
        description="Diagnostic authorization for protected operation",
        request={"operation": PROTECTED_OPERATION},
        expected_status=expected_status,
    )


def run_unauthorized_secure_test() -> tuple[SecurityTestCase, Any, Evidence]:
    """Execute TC-001 with authorization disabled on the secure ECU."""
    ecu = ECUSimulator(mode=SecurityMode.SECURE)
    ecu.set_authorized(False)

    adapter = ECUAdapter(ecu)
    runner = SecurityTestRunner(adapter)

    test_case = _create_test_case(ResponseStatus.ACCESS_DENIED)
    result = runner.run(test_case)

    evidence = EvidenceGenerator().generate(
        test_case,
        result,
        target=TARGET,
        preconditions={"authorization": False},
        notes="Unauthorized protected operation must be denied.",
    )

    return test_case, result, evidence


def run_authorized_secure_test() -> tuple[SecurityTestCase, Any, Evidence]:
    """Execute TC-001 with authorization enabled on the secure ECU."""
    ecu = ECUSimulator(mode=SecurityMode.SECURE)
    ecu.set_authorized(True)

    adapter = ECUAdapter(ecu)
    runner = SecurityTestRunner(adapter)

    test_case = _create_test_case(ResponseStatus.ACCESS_GRANTED)
    result = runner.run(test_case)

    evidence = EvidenceGenerator().generate(
        test_case,
        result,
        target=TARGET,
        preconditions={"authorization": True},
        notes="Authorized protected operation must be granted.",
    )

    return test_case, result, evidence


def run_unauthorized_vulnerable_test() -> tuple[SecurityTestCase, Any, Evidence]:
    """Reproduce the controlled vulnerable authorization behavior."""
    ecu = ECUSimulator(mode=SecurityMode.VULNERABLE)
    ecu.set_authorized(False)

    adapter = ECUAdapter(ecu)
    runner = SecurityTestRunner(adapter)

    test_case = _create_test_case(ResponseStatus.ACCESS_DENIED)
    result = runner.run(test_case)

    evidence = EvidenceGenerator().generate(
        test_case,
        result,
        target=TARGET,
        preconditions={"authorization": False},
        notes="Protected operation was accepted without authorization.",
    )

    return test_case, result, evidence