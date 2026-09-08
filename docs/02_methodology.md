# Security Testing Methodology

## Purpose

This methodology defines how an automotive security requirement is translated into a reproducible security test and how the resulting observation is evaluated, recorded, retested, and used for regression verification.

The methodology covers:

* security requirements
* threat modeling
* attack-surface definition
* attack hypotheses
* security-test definition
* test execution
* expected-versus-actual evaluation
* evidence generation
* security-relevant assessment
* security finding documentation
* remediation
* retesting
* regression testing
* automated regression testing
* CI/CD execution

The current implementation provides a deterministic workflow for security-test execution against a simulated ECU, structured evidence generation, controlled regression testing, example finding documentation, automated regression verification, and CI execution.

The current implementation does not provide generalized finding management, automated finding ingestion, remediation tracking, historical regression comparison, generalized regression orchestration, or generalized security lifecycle management.

---

## Methodology Overview

The complete methodological chain is:

```text
Security Requirement
        ↓
Threat Model
        ↓
Attack Surface
        ↓
Attack Hypothesis
        ↓
Security Test
        ↓
Test Execution
        ↓
Expected vs Actual
        ↓
Evidence
        ↓
Security Finding
        ↓
Root Cause
        ↓
Recommended Fix
        ↓
Implemented Fix
        ↓
Retest
        ↓
Regression
        ↓
Automated Regression
        ↓
CI/CD
```

The currently implemented workflow is:

```text
Security Requirement
        ↓
Threat Model
        ↓
Attack Surface
        ↓
Attack Hypothesis
        ↓
Security Test
        ↓
Test Execution
        ↓
Expected vs Actual
        ↓
Evidence
        ↓
Controlled Security-Relevant Deviation
        ↓
Secure Retest
        ↓
Regression Evaluation
        ↓
Regression Evidence
        ↓
Example Finding Documentation
        ↓
Automated Security Regression Tests
        ↓
GitHub Actions CI Execution
        ↓
CI Evidence JSON Files
        ↓
GitHub Actions Artifact
```

The workflow uses the established security-test, ECU simulation, test-runner, response-evaluation, and evidence components.

The methodology distinguishes current functionality from future lifecycle capabilities.

---

## Methodology Principles

### Define the Security Property First

The expected security behavior is defined before test execution.

A security test evaluates a previously defined security property rather than deriving the expected result from the implementation under test.

For TC-001, the security requirement is:

```text
Protected diagnostic operations shall require authorization.
```

The expected result is defined independently of the ECU implementation.

### Test Through the Target Boundary

Security tests interact with the target through the established target abstraction.

The execution path is:

```text
Security Test
    ↓
Test Runner
    ↓
ECU Adapter
    ↓
Simulated ECU
    ↓
ECU Response
```

The test logic evaluates externally observable target behavior rather than relying on internal ECU implementation details.

### Separate Expected and Actual Results

The expected result represents the defined security property.

The actual result represents the response returned by the system under test.

For the controlled vulnerable authorization behavior:

```text
Expected: ACCESS_DENIED
Actual:   ACCESS_GRANTED
Result:   FAIL
```

The expected result is not modified to make an insecure implementation pass.

### Keep Evidence Separate from Execution

Evidence is generated after test execution and records the completed observation.

The evidence model does not control the target or execute the security test.

The basic relationship is:

```text
Test Execution
    ↓
Test Result
    ↓
Evidence
```

For CI execution, the existing evidence architecture is reused:

```text
Security Regression Tests
    ↓
EvidenceGenerator
    ↓
Evidence
    ↓
Evidence.to_json()
    ↓
CI Evidence JSON Files
    ↓
GitHub Actions Artifact
```

### Keep Tests Reproducible

A security test should produce the same security-relevant result for the same defined state and input.

The current simulation provides deterministic execution through:

* deterministic ECU behavior
* explicit security modes
* explicit authorization state
* explicit ECU state
* controlled requests
* deterministic response statuses
* structured evidence
* absence of external runtime dependencies

Execution timestamps are evidence metadata and do not define the security result.

Regression scenarios create a fresh secure ECU simulator and explicitly configure authorization and ECU state.

---

## Current Methodology

### Step 1 — Security Requirement

The security property is defined before execution.

TC-001 defines:

```text
Protected diagnostic operations shall require authorization.
```

TC-002 defines:

```text
Invalid diagnostic requests shall be rejected before security-relevant operation processing.
```

For TC-001:

```text
Authorization=false + PROTECTED_OPERATION → ACCESS_DENIED
Authorization=true  + PROTECTED_OPERATION → ACCESS_GRANTED
```

The requirement remains unchanged during execution.

### Step 2 — Threat Model

#### TC-001 — Diagnostic Authorization

```text
Asset:
Protected Diagnostic Operation

Threat:
Unauthorized execution of protected diagnostic operation

Potential Attacker:
Unauthorized diagnostic client

Security Property:
Authorization must be enforced before execution of protected operation.
```

The model is limited to the controlled simulation and does not represent a complete production vehicle threat model.

#### TC-002 — Message Validation

```text
Asset:
Protected ECU Request Processing

Threat:
Malformed or invalid diagnostic input reaching security-relevant processing

Potential Attacker:
Unauthorized or malformed diagnostic client

Security Property:
Invalid requests shall be rejected before security-relevant operation processing.
```

This model is likewise limited to the controlled simulation.

### Step 3 — Attack Surface

The relevant request paths are:

#### TC-001

```text
Diagnostic Request
    ↓
Protected Operation
    ↓
Authorization Check
    ↓
ECU Response
```

#### TC-002

```text
Diagnostic Request
    ↓
Request Validation
    ↓
Operation Processing
    ↓
ECU Response
```

The project uses a simulated ECU request interface.

No real CAN, UDS, vehicle network, physical diagnostic interface, or production ECU communication is implemented.

### Step 4 — Attack Hypothesis

#### TC-001

If authorization is not correctly enforced, an unauthorized requester may execute a protected operation.

The controlled test executes the protected operation while authorization is disabled.

The expected secure result is:

```text
ACCESS_DENIED
```

The controlled vulnerable behavior is:

```text
ACCESS_GRANTED
```

#### TC-002

If malformed, unsupported, or impermissible requests are not correctly validated, invalid input may reach security-relevant processing.

The test uses deterministic invalid or impermissible requests.

Expected responses are:

```text
Invalid request structure → INVALID_REQUEST
Unsupported operation     → UNSUPPORTED_OPERATION
Invalid parameter data    → REQUEST_REJECTED
Blocked ECU state         → REQUEST_REJECTED
```

### Step 5 — Security Test

The `SecurityTestCase` defines:

```text
test_id
description
request
expected_status
```

#### TC-001

The protected operation is:

```text
PROTECTED_OPERATION
```

Expected results are:

```text
Unauthorized → ACCESS_DENIED
Authorized   → ACCESS_GRANTED
```

#### TC-002

The message-validation scenarios cover invalid request structures, unsupported operations, invalid parameter data, and blocked ECU state.

The response semantics are:

```text
Invalid request structure → INVALID_REQUEST
Invalid parameter data    → REQUEST_REJECTED
Unsupported operation     → UNSUPPORTED_OPERATION
Blocked ECU state         → REQUEST_REJECTED
```

The defined validation conditions are:

| Condition                           | Expected Response       |
| ----------------------------------- | ----------------------- |
| Request is not a valid mapping      | `INVALID_REQUEST`       |
| Operation is missing or empty       | `INVALID_REQUEST`       |
| Parameters are not a valid mapping  | `INVALID_REQUEST`       |
| Parameter value is outside `0..255` | `REQUEST_REJECTED`      |
| Parameter value is a boolean        | `REQUEST_REJECTED`      |
| Operation is not supported          | `UNSUPPORTED_OPERATION` |
| ECU is blocked                      | `REQUEST_REJECTED`      |

#### Automated Regression Test Definition

The automated regression suite is implemented in:

```text
04_tests/test_security_regression.py
```

It verifies seven established scenarios:

```text
1. Unauthorized protected operation → ACCESS_DENIED
2. Authorized protected operation   → ACCESS_GRANTED
3. Invalid message                  → INVALID_REQUEST
4. Unsupported operation            → UNSUPPORTED_OPERATION
5. Boundary input 256               → REQUEST_REJECTED
6. Blocked ECU state                → REQUEST_REJECTED
7. Regression evidence              → PASS
```

Each regression scenario uses a fresh secure ECU simulator with explicitly configured conditions.

### Step 6 — Preconditions

#### TC-001

The relevant preconditions are:

```text
Authorization:
false or true

Security Mode:
secure or vulnerable
```

Vulnerable mode is used only for the controlled security-relevant deviation.

#### TC-002

The test uses a secure simulated ECU with deterministic validation conditions:

```text
Invalid request structure
Unsupported operation
Invalid parameter
Blocked ECU state
```

#### Automated Regression

The regression scenarios explicitly configure:

```text
Security Mode:
SECURE

Authorization:
false or true

ECU State:
READY or BLOCKED
```

A fresh simulator is used for each regression scenario.

### Step 7 — Test Execution

The established execution path is:

```text
SecurityTestCase
    ↓
SecurityTestRunner
    ↓
ECUTarget
    ↓
ECUAdapter
    ↓
ECUSimulator
    ↓
ECUResponse
```

The Security Test Runner executes the test through the target boundary and evaluates the returned response.

The runner does not depend on internal simulator state for the expected result.

The automated regression suite wraps the established execution path rather than implementing a second security-test architecture.

### Step 8 — Expected vs Actual

The result evaluation follows:

```text
Expected == Actual → PASS
Expected != Actual → FAIL
```

For a secure unauthorized TC-001 execution:

```text
Expected: ACCESS_DENIED
Actual:   ACCESS_DENIED
Result:   PASS
```

For the controlled vulnerable behavior:

```text
Expected: ACCESS_DENIED
Actual:   ACCESS_GRANTED
Result:   FAIL
```

A `FAIL` identifies a deviation between the defined security property and the observed behavior. It does not by itself create a formal security finding.

In CI, a pytest failure propagates to the GitHub Actions job. The workflow does not use `continue-on-error`.

Evidence generation and artifact upload are configured with:

```text
if: always()
```

### Step 9 — Evidence Generation

Evidence follows the established path:

```text
Test Result
    ↓
Evidence Generator
    ↓
Evidence Model
    ↓
JSON
```

The evidence model contains:

```text
test_id
timestamp
target
preconditions
input
expected
actual
result
notes
```

The result value is:

```text
PASS
FAIL
```

For the secure unauthorized regression scenario:

```text
authorization=false
ecu_state=READY
security_mode=SECURE
expected=ACCESS_DENIED
actual=ACCESS_DENIED
result=PASS
```

The CI execution generates six JSON evidence files:

```text
TC-003_unauthorized_protected_operation.json
TC-003_authorized_protected_operation.json
TC-003_invalid_message.json
TC-003_unsupported_operation.json
TC-003_boundary_input.json
TC-003_unexpected_state.json
```

The generated files are uploaded as:

```text
security-regression-evidence
```

### Step 10 — Security Finding Documentation

A security finding is derived from a security-relevant observation and its evidence.

For SEC-001:

```text
TC-001

Expected = ACCESS_DENIED
Actual   = ACCESS_GRANTED
Result   = FAIL

       |
       v

SEC-001
```

The finding documentation remains separate from test execution and evidence generation.

---

## Regression Methodology

TC-003 covers the controlled regression lifecycle for the diagnostic authorization property.

The controlled workflow is:

```text
Vulnerable Reproduction
    ↓
Secure Retest
    ↓
Regression Evidence
    ↓
Authorized Behavior Verification
```

The vulnerable state is:

```text
authorization = false
PROTECTED_OPERATION
       |
       v
ACCESS_GRANTED
```

The original security expectation remains:

```text
Expected = ACCESS_DENIED
Actual   = ACCESS_GRANTED
Result   = FAIL
```

The secure retest uses the same security condition:

```text
authorization = false
PROTECTED_OPERATION
       |
       v
ACCESS_DENIED
```

The secure result is:

```text
Expected = ACCESS_DENIED
Actual   = ACCESS_DENIED
Result   = PASS
```

Authorized behavior is also verified:

```text
authorization = true
PROTECTED_OPERATION
       |
       v
ACCESS_GRANTED
```

The controlled regression therefore verifies restoration of the security property and preservation of authorized behavior.

---

## Automated Regression

The automated security regression suite is implemented in:

```text
04_tests/test_security_regression.py
```

The suite uses the existing `SecurityTestCase`, `SecurityTestRunner`, `ECUAdapter`, `ECUSimulator`, `TestResult`, and Evidence Framework.

The seven scenarios are:

```text
1. Unauthorized protected operation → ACCESS_DENIED
2. Authorized protected operation   → ACCESS_GRANTED
3. Invalid message                  → INVALID_REQUEST
4. Unsupported operation            → UNSUPPORTED_OPERATION
5. Boundary input 256               → REQUEST_REJECTED
6. Blocked ECU state                → REQUEST_REJECTED
7. Regression evidence              → PASS
```

Each scenario uses a fresh secure ECU simulator with explicitly configured authorization and ECU state.

The controlled vulnerable reproduction remains part of the regression methodology and is distinct from the secure automated regression scenarios.

---

## Evidence and Traceability

The primary traceability chain is:

```text
Requirement
    ↓
Threat Model
    ↓
Attack Surface
    ↓
Attack Hypothesis
    ↓
Security Test
    ↓
Test Execution
    ↓
Test Result
    ↓
Evidence
```

For security findings, the chain continues as:

```text
Evidence
    ↓
Security-Relevant Assessment
    ↓
Finding Documentation
```

Automated regression extends the execution path:

```text
Security Test
    ↓
Regression Test
    ↓
Test Result
    ↓
Evidence
```

CI adds the execution and artifact layer:

```text
Automated Regression
    ↓
GitHub Actions
    ↓
Evidence JSON
    ↓
Artifact
```

The project does not implement advanced traceability IDs, historical comparison, generalized finding lifecycle management, or automated finding correlation.

---

## Reproducibility

The methodology is designed around deterministic execution.

Reproducibility is supported by:

* deterministic ECU simulation
* explicit security modes
* explicit authorization state
* explicit ECU state
* controlled requests
* deterministic response statuses
* structured evidence
* absence of external runtime dependencies

The automated regression scenarios use a fresh secure simulator for each scenario.

Expected response statuses are fixed by the test definition.

Execution timestamps change between runs but represent metadata rather than a security-relevant input.

CI executes the same established regression suite without introducing a different security-test path.

---

## Validation of the Test Infrastructure

The test infrastructure is validated through the established test layers:

```text
ECU Simulation Tests
    ↓
Architecture Tests
    ↓
Evidence Tests
    ↓
TC-001 Tests
    ↓
TC-002 Tests
    ↓
TC-003 Regression Workflow Tests
    ↓
Automated Security Regression Suite
    ↓
Complete pytest Suite
    ↓
GitHub Actions CI
```

The complete local pytest suite was verified with:

```text
pytest -v
```

Result:

```text
41 passed in 0.16s
```

The dedicated regression suite was verified with:

```text
pytest .\04_tests\test_security_regression.py -v
```

Result:

```text
7 passed in 0.06s
```

The complete local test distribution is:

| Test Area           |  Tests |
| ------------------- | -----: |
| ECU Simulation      |      6 |
| Evidence            |     14 |
| Foundation          |      1 |
| Security Regression |      7 |
| TC-001              |      4 |
| TC-002              |      5 |
| Test Runner         |      4 |
| **Total**           | **41** |

The CI workflow was verified with a successful push-triggered execution on `main`.

The successful run used:

```text
78c943f
```

The workflow produced:

```text
security-regression-evidence
```

A controlled failure was additionally verified on:

```text
ci/controlled-failure-test
```

The local execution produced:

```text
1 failed, 6 passed
```

The corresponding CI execution propagated the failure with exit code `1`, while the evidence artifact was still uploaded because the evidence upload uses:

```text
if: always()
```

The restoration was completed with:

```text
a604f08
```

The restored regression suite was locally verified with:

```text
7 passed in 0.06s
```

The `pull_request` trigger is configured in the workflow, but a separate pull-request execution has not been independently verified.

---

## CI/CD Execution

The CI workflow executes the established automated regression suite.

The execution path is:

```text
GitHub Actions Trigger
    ↓
Python 3.12
    ↓
pytest
    ↓
04_tests/test_security_regression.py
    ↓
Evidence Generation
    ↓
CI Evidence JSON Files
    ↓
Artifact Upload
```

The workflow is configured for:

```text
push
pull_request
```

The test dependency is:

```text
pytest>=9,<10
```

The workflow uses:

```text
04_tests/test_security_regression.py
```

as the Single Source of Truth for the automated regression scenarios.

The CI evidence path reuses:

```text
EvidenceGenerator
Evidence.to_json()
```

The current CI implementation is limited to automated test execution, evidence generation, and artifact upload.

---

## Security Finding and Remediation

### Security Finding

The project contains structured example findings derived from selected security-test observations.

SEC-001 documents the controlled TC-001 authorization deviation.

SEC-002 documents the TC-002 validation assessment where no security-relevant deviation was reproduced.

The finding documentation is not a generalized finding-management system.

### Root Cause

For SEC-001, the modeled root cause is:

```text
Authorization state is not enforced before granting the protected operation.
```

This describes the controlled simulator behavior used to reproduce the security deviation.

It is not a claim about a real production ECU.

### Recommended Fix

The modeled remediation is:

```text
Enforce authorization before granting the protected operation.
```

The security requirement remains unchanged by the remediation.

### Implemented Fix

The test expectation remains:

```text
Unauthorized protected operation → ACCESS_DENIED
```

The expected security property is independent of the implementation change being evaluated.

### Retest

The retest executes the same security property after the security-relevant change.

For TC-001:

```text
Authorization=false
PROTECTED_OPERATION
    ↓
Expected: ACCESS_DENIED
```

The secure retest confirms that the previously observed deviation is no longer present.

---

## Current Scope and Limitations

The methodology operates within the controlled project architecture.

The current scope includes:

* deterministic ECU simulation
* security modes
* authorization behavior
* request validation
* target abstraction
* security-test execution
* test-result evaluation
* structured evidence
* TC-001 diagnostic authorization
* TC-002 message validation
* TC-003 regression workflow
* structured example findings
* automated security regression testing
* GitHub Actions execution
* CI evidence generation
* evidence artifact upload
* controlled CI failure propagation

The following remain outside the current implementation:

* real CAN communication
* real UDS communication
* physical ECU testing
* vehicle-network integration
* OEM production systems
* generalized finding management
* automated finding ingestion
* historical finding tracking
* CVSS management
* historical regression comparison
* generalized regression orchestration
* automatic test generation
* deployment automation
* production CI/CD
* automatic remediation

The target abstraction allows future target extensions conceptually, but no real ECU, CAN, or UDS adapter is implemented.

---

## Future Security Lifecycle

The current methodology establishes a controlled security-test and regression workflow.

Potential future capabilities include:

* generalized finding management
* automated finding ingestion
* remediation tracking
* historical regression comparison
* generalized regression orchestration
* generalized security lifecycle management

These capabilities are future extensions and are not part of the current implementation.

---

## Historical Development

The methodology developed incrementally with the project.

| Phase    | Development                       |
| -------- | --------------------------------- |
| Phase 0  | Project Definition                |
| Phase 1  | Repository Foundation             |
| Phase 2  | ECU Simulation                    |
| Phase 3  | Security Test Architecture        |
| Phase 4  | Evidence Framework                |
| Phase 5  | TC-001 Diagnostic Authorization   |
| Phase 6  | TC-002 Message Validation         |
| Phase 7  | TC-003 Regression Workflow        |
| Phase 8  | Example Findings                  |
| Phase 9  | Automated pytest Regression Suite |
| Phase 10 | GitHub Actions / CI/CD            |
| Phase 11 | End-to-End Assessment             |
| Phase 12 | Professional Documentation        |
| Phase 13 | Technical Review                  |
| Phase 14 | Recruiter / Interview Review      |

The technical implementation history covers development through automated regression and CI/CD.

Later project phases represent subsequent documentation and review stages and are retained as project-history information rather than additional implemented methodology capabilities.

---

## Current Implementation Status

The implemented methodology currently provides:

```text
Security Requirement Definition
        ↓
Threat and Attack-Surface Definition
        ↓
Security-Test Definition
        ↓
Deterministic ECU Test Execution
        ↓
Expected vs Actual Evaluation
        ↓
Structured Evidence
        ↓
Controlled Regression
        ↓
Example Finding Documentation
        ↓
Automated Security Regression
        ↓
GitHub Actions CI Execution
        ↓
CI Evidence Artifact
```

The current verification status includes:

```text
Complete local pytest suite:
41 passed

Dedicated automated regression suite:
7 passed

Successful push-triggered GitHub Actions execution:
verified

CI evidence artifact:
verified

Controlled CI failure propagation:
verified

Controlled failure evidence upload:
verified

Separate pull-request execution:
not independently verified
```

---

## Methodological Principle

The central methodological principle is:

```text
Define Security Property
    ↓
Model Threat
    ↓
Formulate Attack Hypothesis
    ↓
Test Property
    ↓
Observe Target
    ↓
Record Result
    ↓
Correct Implementation
    ↓
Retest
    ↓
Prevent Regression
```

The project implements this principle through deterministic ECU simulation, structured security tests, evidence generation, controlled regression, automated regression verification, and CI execution.

The methodology remains bounded to the implemented architecture and distinguishes current functionality from future lifecycle capabilities.
