# Security Testing Methodology

## Purpose

This methodology defines how an automotive security requirement is translated into a reproducible security test and how the resulting observation is evaluated, recorded, retested, and used for regression verification.

The methodology separates the following activities:

- security requirements
- threat modeling
- attack-surface definition
- attack hypotheses
- security-test definition
- test execution
- expected-versus-actual evaluation
- evidence generation
- security-relevant assessment
- security finding documentation
- remediation
- retesting
- regression testing
- automated regression testing
- CI/CD execution

The current implementation provides a deterministic workflow for security-test execution against a simulated ECU, structured evidence generation, controlled regression testing, example finding documentation, automated regression verification, and CI execution.

Finding management, automated finding ingestion, remediation tracking, historical regression comparison, generalized regression orchestration, and generalized security lifecycle management are outside the current implementation.

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

The workflow uses the established security-test, ECU simulation, test-runner, response-evaluation, and evidence components throughout the process.

The distinction between implemented functionality and future lifecycle capabilities is maintained explicitly.

---

## Methodology Principles

### Define the Security Property First

The expected security behavior is defined before test execution.

A security test evaluates a previously defined security property rather than deriving the expected result from the implementation under test.

For TC-001, the security requirement is:

```text
Protected diagnostic operations shall require authorization.
```

The expected result is therefore defined independently of the ECU implementation.

---

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

The test logic therefore evaluates externally observable target behavior instead of relying on internal ECU implementation details.

---

### Separate Expected and Actual Results

The expected result represents the defined security property.

The actual result represents the response returned by the system under test.

For example:

```text
Expected: ACCESS_DENIED
Actual:   ACCESS_GRANTED
Result:   FAIL
```

The expected result is not modified to make an insecure implementation pass.

---

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

CI therefore collects evidence from the established test and evidence architecture rather than introducing a separate security-test implementation.

---

### Keep Tests Reproducible

A security test should produce the same security-relevant result for the same defined state and input.

The current simulation provides deterministic execution by avoiding:

- physical hardware
- external networks
- external services
- uncontrolled target state
- random security behavior

Execution timestamps are evidence metadata and do not define the security result.

Regression scenarios create a fresh secure ECU simulator and explicitly configure authorization and ECU state. Inputs and expected response statuses are deterministic.

The same properties are preserved when the established regression suite is executed through CI.

---

# Current Methodology

## Step 1 — Security Requirement

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

---

## Step 2 — Threat Model

### TC-001 — Diagnostic Authorization

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

### TC-002 — Message Validation

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

---

## Step 3 — Attack Surface

The relevant request paths are modeled as:

### TC-001

```text
Diagnostic Request
    ↓
Protected Operation
    ↓
Authorization Check
    ↓
ECU Response
```

### TC-002

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

There is no real CAN, UDS, vehicle network, physical diagnostic interface, or production ECU communication.

---

## Step 4 — Attack Hypothesis

### TC-001

If authorization is not correctly enforced, an unauthorized requester may execute a protected operation.

The controlled test therefore executes the protected operation while authorization is disabled.

The expected secure result is:

```text
ACCESS_DENIED
```

The controlled vulnerable behavior is:

```text
ACCESS_GRANTED
```

### TC-002

If malformed, unsupported, or impermissible requests are not correctly validated, invalid input may reach security-relevant processing.

The test uses deterministic invalid or impermissible requests.

Expected responses are:

```text
Invalid request structure → INVALID_REQUEST
Unsupported operation     → UNSUPPORTED_OPERATION
Invalid parameter data    → REQUEST_REJECTED
Blocked ECU state         → REQUEST_REJECTED
```

Validation therefore occurs before protected operation processing.

---

## Step 5 — Security Test

The `SecurityTestCase` defines the core test information:

```text
test_id
description
request
expected_status
```

### TC-001

The protected operation is:

```text
PROTECTED_OPERATION
```

The expected results are:

```text
Unauthorized → ACCESS_DENIED
Authorized   → ACCESS_GRANTED
```

The expected status is defined independently of the response returned by the ECU.

### TC-002

The message-validation scenarios cover invalid request structures, unsupported operations, invalid parameter data, and blocked ECU state.

The response semantics are:

```text
Invalid request structure → INVALID_REQUEST
Invalid parameter data    → REQUEST_REJECTED
Unsupported operation     → UNSUPPORTED_OPERATION
Blocked ECU state         → REQUEST_REJECTED
```

The defined validation conditions are:

| Condition | Expected Response |
|---|---|
| Request is not a valid mapping | `INVALID_REQUEST` |
| Operation is missing or empty | `INVALID_REQUEST` |
| Parameters are not a valid mapping | `INVALID_REQUEST` |
| Parameter value is outside `0..255` | `REQUEST_REJECTED` |
| Parameter value is a boolean | `REQUEST_REJECTED` |
| Operation is not supported | `UNSUPPORTED_OPERATION` |
| ECU is blocked | `REQUEST_REJECTED` |

The TC-002 behavior is evaluated through the externally observable ECU response and is independent of the internal implementation.

### Automated Regression Test Definition

The automated regression suite is implemented in:

```text
04_tests/test_security_regression.py
```

It uses the established architecture and defines seven regression scenarios:

1. unauthorized protected operation → `ACCESS_DENIED`
2. authorized protected operation → `ACCESS_GRANTED`
3. invalid message → `INVALID_REQUEST`
4. unsupported operation → `UNSUPPORTED_OPERATION`
5. out-of-range boundary input `256` → `REQUEST_REJECTED`
6. protected operation in blocked ECU state → `REQUEST_REJECTED`
7. secure regression evidence → expected and actual `ACCESS_DENIED`, Evidence `PASS`

Each regression scenario uses a fresh secure ECU simulator with explicitly configured conditions.

The evidence scenario validates the test ID, target, preconditions, expected result, actual result, result status, and evidence validity.

The automated regression suite reuses the existing target, adapter, runner, response, and evidence architecture.

---

## Step 6 — Preconditions

### TC-001

The relevant preconditions are:

```text
Authorization:
false or true

Security Mode:
secure or vulnerable
```

Vulnerable mode is used only for the controlled security-relevant deviation.

### TC-002

The test uses a secure simulated ECU with deterministic validation conditions:

```text
Invalid request structure
Unsupported operation
Invalid parameter
Blocked ECU state
```

### Automated Regression

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

---

## Step 7 — Test Execution

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

The `SecurityTestRunner` executes the test through the target boundary and evaluates the returned response.

The runner does not depend on internal simulator state for the expected result.

The automated regression suite wraps the established execution path rather than implementing a second security-test architecture.

The file

```text
04_tests/test_security_regression.py
```

is the Single Source of Truth for the automated security regression scenarios.

---

## Step 8 — Expected vs Actual

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

The automated regression tests assert the expected `TestResult`.

In CI, a pytest failure propagates to the GitHub Actions job. The workflow does not use `continue-on-error`.

Evidence generation and artifact upload are configured with `if: always()`, allowing evidence to remain available when the test execution fails.

---

## Step 9 — Evidence Generation

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

For the secure unauthorized regression scenario, the evidence contains the relevant execution conditions:

```text
authorization=false
ecu_state=READY
security_mode=SECURE
expected=ACCESS_DENIED
actual=ACCESS_DENIED
result=PASS
```

The evidence is validated as a completed execution record.

The CI workflow reuses `EvidenceGenerator` and `Evidence.to_json()`.

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

Evidence generation and artifact upload use `if: always()`.

---

## Step 10 — Security Finding Documentation

A security finding is derived from a security-relevant observation and its evidence.

The relationship is:

```text
Security Requirement
    ↓
Security Test
    ↓
Observed Behavior
    ↓
Evidence
    ↓
Security-Relevant Assessment
    ↓
Finding Documentation
```

A test result of `FAIL` is therefore an input to the assessment and does not automatically create a formal finding.

### SEC-001

SEC-001 documents the controlled TC-001 authorization deviation:

```text
Expected: ACCESS_DENIED
Actual:   ACCESS_GRANTED
Result:   FAIL
```

The structured finding contains:

```text
Security Requirement
Threat Model
Preconditions
Reproduction Steps
Expected Behavior
Actual Behavior
Evidence
Security Impact
Exploitability
Root Cause
Recommendation
Fix
Retest
Regression Test
Status
```

The finding documentation is stored under:

```text
05_examples/
```

### SEC-002

SEC-002 documents the TC-002 message-validation behavior without a security-relevant deviation.

The project provides structured example findings rather than an automated finding-management system.

---

# Security Test Result vs Test Framework Result

The security-test result and the pytest framework result represent different levels of evaluation.

For the controlled vulnerable behavior:

```text
TestResult.passed = false
```

The pytest test can nevertheless pass because the test correctly detects the expected security deviation.

For the secure retest:

```text
TestResult.passed = true
```

and the pytest test also passes.

The distinction is therefore:

```text
TestResult:
Describes whether the system behavior matches the defined security expectation.

pytest result:
Describes whether the automated test correctly verified the intended condition.
```

CI status reflects the pytest result, not the semantic meaning of an individual `TestResult`.

---

# Regression Methodology

Regression testing verifies that a security property remains satisfied after a security-relevant change.

The controlled regression workflow is:

```text
Security Property
    ↓
Existing Test Condition
    ↓
Controlled Vulnerable Behavior
    ↓
Secure Retest
    ↓
Expected vs Actual
    ↓
Regression Result
    ↓
Evidence
```

For TC-001:

```text
Unauthorized protected operation
Expected secure result: ACCESS_DENIED

Controlled vulnerable behavior:
Authorization=false → ACCESS_GRANTED

Secure retest:
Authorization=false → ACCESS_DENIED
```

The regression result is determined by the `SecurityTestRunner` through expected-versus-actual evaluation.

The Evidence Framework records the completed execution.

The regression workflow therefore reuses the existing security-test and evidence architecture.

The automated regression suite extends this methodology by verifying the established secure behavior across seven deterministic scenarios.

The CI workflow executes that existing regression suite and preserves its evidence as JSON artifacts.

No second security-test implementation is introduced for regression or CI execution.

---

# TC-001 Methodology Example

## Requirement

```text
Protected diagnostic operations shall require authorization.
```

## Threat

Unauthorized diagnostic execution of a protected operation.

## Attack Surface

```text
Diagnostic Request
    ↓
Protected Operation
    ↓
Authorization Check
    ↓
ECU Response
```

## Attack Hypothesis

An unauthorized requester may execute the protected operation if authorization is not correctly enforced.

## Preconditions

```text
Authorization=false
Security Mode=SECURE
```

For the controlled vulnerable execution:

```text
Authorization=false
Security Mode=VULNERABLE
```

## Input

```text
PROTECTED_OPERATION
```

## Expected Secure Result

```text
ACCESS_DENIED
```

## Controlled Vulnerable Result

```text
ACCESS_GRANTED
```

## Evaluation

```text
Expected != Actual
Result = FAIL
```

The secure retest restores the expected behavior:

```text
Expected: ACCESS_DENIED
Actual:   ACCESS_DENIED
Result:   PASS
```

## Evidence

The execution result is recorded using the established Evidence model.

The evidence includes the test ID, target, preconditions, input, expected result, actual result, result status, timestamp, and notes.

## Authorized Scenario

Authorization is also tested as a positive case:

```text
Authorization=true
PROTECTED_OPERATION
    ↓
ACCESS_GRANTED
```

This preserves the expected authorized behavior while verifying rejection of unauthorized access.

---

# TC-002 Methodology Example

## Requirement

```text
Invalid diagnostic requests shall be rejected before security-relevant operation processing.
```

## Threat

Malformed or impermissible diagnostic input may reach security-relevant processing.

## Attack Surface

```text
Diagnostic Request
    ↓
Request Validation
    ↓
Operation Processing
    ↓
ECU Response
```

## Attack Hypothesis

Invalid requests may be processed incorrectly if request validation is not enforced before operation processing.

## Preconditions

A secure simulated ECU is used with deterministic validation conditions.

## Input and Expected Result

```text
Invalid request structure → INVALID_REQUEST
Unsupported operation     → UNSUPPORTED_OPERATION
Invalid parameter data    → REQUEST_REJECTED
Blocked ECU state         → REQUEST_REJECTED
```

For otherwise valid authorized requests, the established boundary values include:

```text
value=0   → ACCESS_GRANTED
value=255 → ACCESS_GRANTED
```

when authorization and ECU state permit the protected operation.

## Evaluation

The returned ECU response is compared with the expected response defined by the test.

## Evidence

The resulting `TestResult` is recorded through the established Evidence Framework.

---

# TC-003 Methodology Example

TC-003 covers the regression workflow and its automated verification.

The controlled regression lifecycle includes:

```text
Vulnerable Reproduction
    ↓
Secure Retest
    ↓
Regression Evidence
    ↓
Authorized Behavior Verification
```

The automated regression suite verifies the established secure security properties through seven scenarios:

```text
Unauthorized protected operation → ACCESS_DENIED
Authorized protected operation   → ACCESS_GRANTED
Invalid message                  → INVALID_REQUEST
Unsupported operation            → UNSUPPORTED_OPERATION
Boundary input 256               → REQUEST_REJECTED
Blocked ECU state                → REQUEST_REJECTED
Regression evidence              → PASS
```

The automated suite uses the established ECU simulator, target abstraction, adapter, runner, response model, and evidence model.

The controlled vulnerable reproduction remains part of the regression methodology and is distinct from the secure automated regression scenarios.

CI executes the automated regression suite and uploads the generated evidence as the `security-regression-evidence` artifact.

---

# Evidence and Traceability

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

The current project does not implement advanced traceability IDs, historical comparison, generalized finding lifecycle management, or automated finding correlation.

---

# Reproducibility

The methodology is designed around deterministic execution.

Reproducibility is supported by:

- deterministic ECU simulation
- explicit security modes
- explicit authorization state
- explicit ECU state
- controlled requests
- deterministic response statuses
- structured evidence
- absence of external runtime dependencies

The automated regression scenarios use a fresh secure simulator for each scenario.

The relevant authorization and ECU state are explicitly configured.

Expected response statuses are fixed by the test definition.

This avoids state leakage between regression scenarios.

Execution timestamps change between runs but represent metadata rather than a security-relevant input.

CI executes the same established regression suite without introducing a different security-test path.

---

# Validation of the Test Infrastructure

The test infrastructure is validated through the following test layers:

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

The automated security regression suite verifies seven defined scenarios.

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

| Test Area | Tests |
|---|---:|
| ECU Simulation | 6 |
| Evidence | 14 |
| Foundation | 1 |
| Security Regression | 7 |
| TC-001 | 4 |
| TC-002 | 5 |
| Test Runner | 4 |
| **Total** | **41** |

The CI workflow was also verified with a successful push-triggered execution on `main`.

The successful run used commit:

```text
78c943f
```

The workflow completed successfully and produced the:

```text
security-regression-evidence
```

artifact.

A controlled failure was additionally verified on the temporary branch:

```text
ci/controlled-failure-test
```

The local execution produced:

```text
1 failed, 6 passed
```

The corresponding CI execution propagated the failure with exit code `1`, while the evidence artifact was still uploaded because the evidence upload uses `if: always()`.

The restoration was completed with:

```text
a604f08
```

The controlled failure therefore verifies both failure propagation and evidence preservation.

The GitHub Actions workflow also defines a pull-request trigger. A separate pull-request execution has not been claimed as independently verified.

---

# CI/CD Execution

The CI workflow executes the established automated regression suite.

Its relevant flow is:

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

The workflow is triggered by:

```text
push
pull_request
```

The test dependency is installed as:

```text
pytest>=9,<10
```

The regression command targets:

```text
04_tests/test_security_regression.py
```

The workflow therefore uses the automated regression suite as its Single Source of Truth.

CI does not introduce:

- production deployment
- vehicle communication
- real ECU communication
- finding management
- historical comparison
- automatic remediation

The current CI implementation is limited to automated test execution, evidence generation, and artifact upload.

---

# Root Cause

For SEC-001, the modeled root cause is:

```text
Authorization state is not enforced before granting the protected operation.
```

This describes the controlled simulator behavior used to reproduce the security deviation.

It is not a claim about a real production ECU.

---

# Recommended Fix

The modeled remediation is:

```text
Enforce authorization before granting the protected operation.
```

The security requirement remains unchanged by the remediation.

---

# Implemented Fix

The test expectation remains:

```text
Unauthorized protected operation → ACCESS_DENIED
```

The expected security property is therefore independent of the implementation change being evaluated.

---

# Retest

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

# Regression

Regression testing preserves the established security property after the secure behavior has been restored.

The project contains:

```text
TC-001 controlled regression workflow
        +
Automated seven-scenario security regression suite
        +
GitHub Actions CI execution
```

The controlled regression demonstrates vulnerable reproduction and secure retest.

The automated regression suite verifies the established secure behavior.

CI executes the automated suite and preserves its evidence.

---

# Automated Regression

The automated regression suite verifies seven established scenarios:

```text
1. Unauthorized protected operation → ACCESS_DENIED
2. Authorized protected operation   → ACCESS_GRANTED
3. Invalid message                  → INVALID_REQUEST
4. Unsupported operation            → UNSUPPORTED_OPERATION
5. Boundary input 256               → REQUEST_REJECTED
6. Blocked ECU state                → REQUEST_REJECTED
7. Regression evidence              → PASS
```

The suite uses deterministic simulated ECU behavior and the existing security-test architecture.

It does not implement historical comparison, automated finding lifecycle management, or generalized regression orchestration.

---

# Security Finding

The project contains structured example findings derived from selected security-test observations.

They demonstrate the relationship between security requirements, observed behavior, evidence, and security assessment.

The finding documentation is not a generalized finding-management system.

---

# Current Scope and Limitations

The methodology operates within the controlled project architecture.

The current scope includes:

- deterministic ECU simulation
- security modes
- authorization behavior
- request validation
- target abstraction
- security-test execution
- test-result evaluation
- structured evidence
- TC-001 diagnostic authorization
- TC-002 message validation
- TC-003 regression workflow
- structured example findings
- automated security regression testing
- GitHub Actions execution
- CI evidence generation
- evidence artifact upload
- controlled CI failure propagation

The following remain outside the current implementation:

- real CAN communication
- real UDS communication
- physical ECU testing
- vehicle-network integration
- OEM production systems
- generalized finding management
- automated finding ingestion
- historical finding tracking
- CVSS management
- historical regression comparison
- generalized regression orchestration
- automatic test generation
- deployment automation
- production CI/CD
- automatic remediation

The target abstraction allows future target extensions conceptually, but no real ECU, CAN, or UDS adapter is implemented.

---

# Future Security Lifecycle

The current methodology establishes a controlled security-test and regression workflow.

Potential future capabilities include:

- generalized finding management
- automated finding ingestion
- remediation tracking
- historical regression comparison
- generalized regression orchestration
- generalized security lifecycle management

These capabilities are future extensions and are not part of the current implementation.

---

# Historical Development

The methodology developed incrementally with the project.

| Phase | Development |
|---|---|
| Phase 0 | Project Definition |
| Phase 1 | Repository Foundation |
| Phase 2 | ECU Simulation |
| Phase 3 | Security Test Architecture |
| Phase 4 | Evidence Framework |
| Phase 5 | TC-001 Diagnostic Authorization |
| Phase 6 | TC-002 Message Validation |
| Phase 7 | TC-003 Regression Workflow |
| Phase 8 | Example Findings |
| Phase 9 | Automated pytest Regression Suite |
| Phase 10 | GitHub Actions / CI/CD |
| Phase 11 | End-to-End Assessment |
| Phase 12 | Professional Documentation |
| Phase 13 | Technical Review |
| Phase 14 | Recruiter / Interview Review |

The technical implementation history currently established in the project architecture covers the development through automated regression and CI/CD.

Later project phases represent the subsequent documentation and review stages of the project and are kept here as project-history information rather than as additional implemented methodology capabilities.

---

# Current Implementation Status

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

# Methodological Principle

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

The current project implements this principle through deterministic ECU simulation, structured security tests, evidence generation, controlled regression, automated regression verification, and CI execution.

The methodology remains deliberately bounded to the implemented architecture and distinguishes current functionality from future lifecycle capabilities.
