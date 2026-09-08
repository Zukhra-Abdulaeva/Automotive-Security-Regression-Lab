# Automotive Security Regression Lab

**From Security Finding to Reproducible Automotive Security Tests**

## Overview

The **Automotive Security Regression Lab** is a local, deterministic simulation environment for developing and demonstrating an automotive cybersecurity testing workflow.

The project demonstrates how a security requirement can be translated into a security test, executed against a simulated ECU, evaluated against expected behavior, captured as structured evidence, documented as a security finding, and verified through regression testing.

The laboratory does not connect to real vehicles, ECUs, vehicle networks, OEM infrastructure, or production systems. No real CAN or UDS communication is implemented.

The project is an engineering demonstration within a controlled simulation environment. It does not represent a real penetration-testing engagement, ECU assessment, vehicle assessment, production cybersecurity validation, or professional operational penetration-testing experience.

---

# Workflow

The implemented workflow is:

```text
Security Requirement
        ↓
Security Test Case
        ↓
Test Execution
        ↓
Simulated ECU
        ↓
Test Result
        ↓
Structured Evidence
        ↓
Finding Documentation
        ↓
Secure Retest
        ↓
Automated Regression Verification
        ↓
CI/CD
```

The long-term workflow additionally includes threat modeling, attack hypotheses, root-cause analysis, remediation, and regression testing.

---

# Architecture

The security-test architecture separates test logic from the simulated system under test:

```text
SecurityTestCase
        ↓
SecurityTestRunner
        ↓
ECUAdapter
        ↓
ECUTarget
        ↓
ECUSimulator
        ↓
TestResult
        ↓
Evidence
```

The simulator provides deterministic secure and controlled vulnerable behavior.

The Evidence Framework records structured execution evidence and supports validation and JSON serialization.

The CI workflow executes the existing Security Regression suite rather than implementing a second Security Test.

---

# Current Test Scope

The current implementation contains:

* **TC-001 — Diagnostic Authorization**
* **TC-002 — Message Validation**
* **TC-003 — Regression Workflow**
* automated pytest regression verification
* structured execution evidence
* representative `SEC-001` and `SEC-002` finding documentation
* GitHub Actions execution of the Security Regression suite
* CI evidence generation and artifact upload

The controlled TC-001 vulnerable scenario demonstrates detection of:

```text
Expected = ACCESS_DENIED
Actual   = ACCESS_GRANTED
Result   = FAIL
```

The corrected secure behavior is:

```text
Authorization = false
        ↓
PROTECTED_OPERATION
        ↓
ACCESS_DENIED
        ↓
PASS
```

---

# Verification

The current repository state has been verified locally with:

```text
pytest -v
```

Result:

```text
41 passed
```

The dedicated Security Regression suite reports:

```text
7 passed
```

The CI workflow has a verified successful `push` execution and a separately verified controlled failure execution.

The CI pipeline generates six JSON evidence files and uploads them as the:

```text
security-regression-evidence
```

artifact.

Detailed verification results, CI history, implementation status, test distribution, and technical details are maintained in [`project.md`](project.md).

---

# Repository Structure

```text
automotive-security-regression-lab/

├── README.md
├── project.md
├── PROJECT_STATUS.md
├── ARCHITECTURE_DECISIONS.md
├── pyproject.toml
│
├── docs/
│   ├── 01_architecture.md
│   ├── 02_methodology.md
│   ├── 03_evidence-format.md
│   └── 04_end-to-end-assessment-case.md
│
├── 01_threat_model/
│   └── 01_attack_surface.md
│
├── 02_test_cases/
│   ├── TC-001-diagnostic-authorization.md
│   ├── TC-002-message-validation.md
│   └── TC-003-regression-workflow.md
│
├── 03_src/
│   └── security_lab/
│
├── 04_tests/
│   ├── test_ecu_simulator.py
│   ├── test_evidence.py
│   ├── test_foundation.py
│   ├── test_test_runner.py
│   ├── test_tc001_diagnostic_authorization.py
│   ├── test_tc002_message_validation.py
│   └── test_security_regression.py
│
├── 05_examples/
│   ├── sample_finding_SEC-001.md
│   └── sample_finding_SEC-002.md
│
└── .github/
    └── workflows/
        └── security-regression.yml
```

---

# Documentation

| Document                                | Purpose                                                                  |
| --------------------------------------- | ------------------------------------------------------------------------ |
| `README.md`                             | Concise project overview and entry point                                 |
| `project.md`                            | Detailed implementation, verification, CI/CD status, and project history |
| `PROJECT_STATUS.md`                     | Detailed implementation and verification status                          |
| `ARCHITECTURE_DECISIONS.md`             | Architectural decisions and rationale                                    |
| `docs/01_architecture.md`               | Detailed architecture                                                    |
| `docs/02_methodology.md`                | Security-testing methodology                                             |
| `docs/03_evidence-format.md`            | Evidence Framework and evidence format                                   |
| `docs/04_end-to-end-assessment-case.md` | End-to-end assessment case and traceability                              |
| `02_test_cases/`                        | Detailed security-test specifications                                    |
| `01_threat_model/`                      | Modeled attack-surface information                                       |

---

# Technology

The project currently uses:

* Python
* pytest
* Python standard library components where practical
* GitHub Actions

The CI environment uses:

```text
Python 3.12
pytest>=9,<10
```

The laboratory is locally executable, deterministic, hardware-independent, network-independent, and reproducible.

---

# Scope Boundary

The laboratory does not:

* connect to real vehicles or ECUs
* send traffic to vehicle networks
* interact with OEM infrastructure
* access customer data
* use production credentials
* interact with production systems
* implement real CAN communication
* implement real UDS communication

The vulnerable ECU mode is a controlled simulator condition and must not be interpreted as evidence of a vulnerability in a real vehicle, ECU, OEM system, or production environment.

---

# Technical References

* [Python Documentation](https://docs.python.org/3.14/)
* [pytest Documentation](https://docs.pytest.org/en/stable/)
* [pytest Good Integration Practices](https://docs.pytest.org/en/stable/explanation/goodpractices.html)
