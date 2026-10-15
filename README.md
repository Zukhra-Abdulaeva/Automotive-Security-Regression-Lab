# Automotive Security Regression Lab

**From Security Finding to Reproducible Automotive Security Tests**

## Overview

The **Automotive Security Regression Lab** is a local, deterministic simulation environment for developing and demonstrating an automotive cybersecurity testing workflow.

The project demonstrates how a security requirement can be translated into a security test, executed against a simulated ECU, evaluated against expected behavior, captured as structured evidence, documented as a security finding and verified through regression testing.

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

The long-term workflow additionally includes threat modeling, attack hypotheses, root-cause analysis, remediation and regression testing.

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

Detailed verification results, CI history, implementation status, test distribution and technical details are maintained in [`project_status.md`](docs/project_status.md).

---

# Repository Structure

```text
automotive-security-regression-lab/

├── README.md
├── RECRUITER_REVIEW.md
├── pyproject.toml
├── .gitattributes
├── .gitignore
│
├── docs/
│   ├── docs/architecture_decisions.md
│   ├── docs/architecture.md
│   ├── docs/environment-setup.md
│   ├── docs/evidence-format.md
│   ├── docs/methodology.md
│   ├── docs/project_status.md
│   └── docs/end-to-end-assessment-case.md
│
├── 01_threat_model/
│   └── attack_surface.md
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

## Main project documentation

| Markdown file                    | Purpose                                                                                                                                                                          |
| -------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `README.md`                      | Project overview, scope, architecture, security-testing workflow, current test coverage, technology stack, verification summary and repository structure                         |
| `RECRUITER_REVIEW.md`            | A recruiter- and interview-focused review of the project, including strengths, credibility, technical interview questions, an elevator pitch and a longer interview explanation  |
| `docs/project_status.md`         | Detailed project status, implementation phases, test results, CI/CD verification, deliverables, quality gates and links to supporting documentation                              |

## Technical documentation

| Markdown file                        | Purpose                                                                                                                                                                                                                           |
| ------------------------------------ | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `docs/architecture_decisions.md`     | Architecture Decision Records (ADRs) documenting key design choices, their rationale, consequences and the boundaries of the simulated security-testing environment                                                               |
| `docs/architecture.md`               | Detailed system architecture, component responsibilities, test-execution flow, request validation, ECU simulation modes, evidence integration, regression architecture, CI/CD and architectural boundaries                        |
| `docs/end-to-end-assessment-case.md` | End-to-end assessment case connecting security requirements, threat modeling, attack hypotheses, test cases, execution results, evidence, findings, root cause, fixes, retesting, regression verification and CI/CD               |
| `docs/environment-setup.md`          | Local development setup instructions, including repository cloning, Python environment preparation, dependency installation and test execution                                                                                    |
| `docs/evidence-format.md`            | Defines the evidence data model, required fields, timestamps, PASS/FAIL semantics, evidence generation and validation, JSON serialization and the relationship between evidence and the test lifecycle                            |
| `docs/methodology.md`                | Security-testing methodology from defining security requirements and threat models through attack-surface analysis, test execution, expected-versus-actual evaluation, evidence, findings, remediation, retesting and regression  |

## Threat model and attack surface

| Markdown file                       | Purpose                                                                                                                                                                     |
| ----------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `01_threat_model/attack_surface.md` | Defines the simulated ECU's attack surface, security boundaries, modeled inputs and states, threat actor, attack hypotheses and traceability to TC-001, TC-002 and TC-003   |

## Security test case specifications

| Markdown file                                      | Purpose                                                                                                                                                                                                                          |
| -------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `02_test_cases/TC-001-diagnostic-authorization.md` | Specifies TC-001 for diagnostic authorization, including the security requirement, threat model, attack hypothesis, test setup, expected and actual behavior, evidence, root cause, remediation, retest and regression coverage  |
| `02_test_cases/TC-002-message-validation.md`       | Specifies TC-002 for message validation, covering malformed input, unsupported operations, boundary values, unexpected ECU states, expected responses, evidence, remediation, retest and regression considerations               |
| `02_test_cases/TC-003-regression-workflow.md`      | Defines TC-003's finding-to-regression workflow, regression inputs and expected behavior, evidence generation, result interpretation, traceability, determinism and CI/CD integration boundaries                                 |

## Example security findings

| Markdown file                           | Purpose                                                                                                                                                                                                                                        |
| --------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `05_examples/sample_finding_SEC-001.md` | Example security finding for the diagnostic-authorization deviation, documenting the security requirement, reproduction steps, expected versus actual behavior, evidence, impact, root cause, recommendation, fix, retest and regression test  |
| `05_examples/sample_finding_SEC-002.md` | A second structured example finding associated with the message-validation assessment, documenting the scenario, evidence, assessment, impact, root cause, recommendations and retest/regression information                                   |

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

The laboratory is locally executable, deterministic, hardware-independent, network-independent and reproducible.

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
