# Architecture

## Purpose

The Automotive Security Regression Lab uses a deterministic software architecture for developing and executing automotive security tests against a simulated ECU.

The architecture separates the following responsibilities:

* security-test definition
* test execution
* target interaction
* simulated ECU behavior
* test-result evaluation
* evidence generation
* automated regression verification
* CI/CD execution and evidence artifact handling

A security test defines the expected security behavior. The simulated ECU provides the system-under-test behavior. The Security Test Runner executes the test through the target boundary and evaluates the returned response. The Evidence Framework records the resulting observation.

Automated regression tests verify established security properties through these existing components. The CI/CD workflow executes the established regression suite and handles the resulting evidence artifacts.

The project is fully simulated and deterministic. The implementation does not communicate with real vehicles, real ECUs, CAN networks, UDS endpoints, OEM systems, or production systems.

---

## System Context

The project models the relationship between a security tester and an automotive system in a controlled Python environment.

A simplified real-world concept is:

```text
Security Tester
       |
       v
Diagnostic Interface
       |
       v
Communication Layer
       |
       v
ECU
```

The project uses a local software architecture instead of implementing this real-world communication stack:

```text
Security Test Case
       |
       v
Security Test Runner
       |
       v
ECU Adapter
       |
       v
Simulated ECU
       |
       v
ECU Response
       |
       v
Test Result
       |
       v
Evidence
```

Automated security regression tests reuse this architecture:

```text
Established Security Properties
       |
       v
04_tests/test_security_regression.py
       |
       v
SecurityTestCase
       |
       v
SecurityTestRunner
       |
       v
ECUAdapter
       |
       v
Fresh Secure ECUSimulator
       |
       v
TestResult
       |
       v
EvidenceGenerator
```

CI/CD surrounds the established regression execution:

```text
GitHub Event
       |
       v
GitHub Actions
       |
       v
Checkout Repository
       |
       v
Python 3.12
       |
       v
Install Dependencies
       |
       v
pytest Security Regression Suite
       |
       v
Existing Regression Execution Path
       |
       v
EvidenceGenerator
       |
       v
Evidence
       |
       v
Evidence.to_json()
       |
       v
CI Evidence JSON Files
       |
       v
GitHub Actions Artifact
```

CI/CD provides the external execution mechanism. Security-test execution, target behavior, result evaluation, and evidence generation remain responsibilities of the established Python components.

---

## Architectural Components

The current architecture consists of the following logical components:

```text
+---------------------------+
|    Security Test Case     |
+-------------+-------------+
              |
              v
+---------------------------+
|     SecurityTestRunner    |
+-------------+-------------+
              |
              v
+---------------------------+
|        ECUTarget          |
+-------------+-------------+
              |
              v
+---------------------------+
|        ECUAdapter         |
+-------------+-------------+
              |
              v
+---------------------------+
|       ECUSimulator        |
+-------------+-------------+
              |
              v
+---------------------------+
|       ECUResponse         |
+-------------+-------------+
              |
              v
+---------------------------+
|        TestResult         |
+-------------+-------------+
              |
              v
+---------------------------+
|    Evidence Framework     |
+---------------------------+
```

### SecurityTestCase

`SecurityTestCase` defines the core information required for a security test:

```text
test_id
description
request
expected_status
```

The expected status is defined independently of the response returned by the ECU.

Automated regression scenarios create their own `SecurityTestCase` instances in:

```text
04_tests/test_security_regression.py
```

These scenarios use:

```text
test_id = "TC-003"
```

The automated regression tests therefore reuse the established test-case structure without reusing the same `TC-001` `SecurityTestCase` instance used by the controlled regression workflow.

### SecurityTestRunner

`SecurityTestRunner` controls the execution of a security test.

Its responsibilities are:

1. accept a `SecurityTestCase`
2. send the request through the target interface
3. receive the ECU response
4. compare the actual response status with the expected status
5. create a structured `TestResult`

The execution flow is:

```text
SecurityTestCase
       |
       v
SecurityTestRunner
       |
       v
Target
       |
       v
ECU Response
       |
       v
Expected vs Actual
       |
       v
TestResult
```

The Security Test Runner does not access internal ECU state and does not implement ECU security policy, authorization decisions, security finding management, evidence storage, regression orchestration, or CI/CD.

For regression verification, the existing `SecurityTestRunner` performs the expected-versus-actual comparison. No separate regression execution engine is introduced.

### ECUTarget

`ECUTarget` defines the target interface used by the Security Test Runner.

The abstraction separates the test infrastructure from the concrete target implementation:

```text
SecurityTestRunner
       |
       v
    ECUTarget
       |
       v
    ECUAdapter
       |
       v
   ECUSimulator
```

The current implementation uses the simulated ECU behind this interface.

No real vehicle communication protocol is implemented through `ECUTarget`.

### ECUAdapter

`ECUAdapter` connects the abstract `ECUTarget` interface to the concrete `ECUSimulator`.

Its responsibility is to forward requests to the configured target and return the resulting response.

The adapter does not define security requirements, implement security-test logic, make authorization decisions, evaluate security findings, generate evidence, or modify test results.

Automated regression execution uses the same adapter boundary. The CI/CD workflow invokes the established regression suite and does not bypass the adapter.

### ECUSimulator

`ECUSimulator` represents the simulated ECU and is the system under test.

Its responsibilities include:

* maintaining the configured security mode
* maintaining the authorization state
* validating incoming requests
* processing the requested operation
* applying the configured security behavior
* returning a deterministic `ECUResponse`

The simulator supports two security modes:

```text
secure
vulnerable
```

#### Secure Mode

Secure mode enforces authorization before granting the protected operation.

#### Vulnerable Mode

Vulnerable mode is used for the controlled regression workflow to reproduce the modeled authorization deviation.

For the controlled unauthorized operation:

```text
authorization = false
operation = PROTECTED_OPERATION
```

the modeled vulnerable behavior is:

```text
ACCESS_GRANTED
```

while the expected security behavior remains:

```text
ACCESS_DENIED
```

### ECUResponse

`ECUResponse` represents the response returned by the simulated ECU.

The response provides the externally observable behavior used by the Security Test Runner for expected-versus-actual evaluation.

### TestResult

`TestResult` represents the evaluated security-test execution.

For the controlled vulnerable authorization scenario:

```text
Expected = ACCESS_DENIED
Actual   = ACCESS_GRANTED
Result   = FAIL
```

For the secure regression retest:

```text
Expected = ACCESS_DENIED
Actual   = ACCESS_DENIED
Result   = PASS
```

The security-test result and the pytest framework result are distinct. A pytest assertion can pass because it correctly detects an expected deviation in a controlled vulnerable scenario.

---

## Test Execution Flow

The standard execution path is:

```text
SecurityTestCase
       |
       v
SecurityTestRunner
       |
       v
ECUTarget
       |
       v
ECUAdapter
       |
       v
ECUSimulator
       |
       v
ECUResponse
       |
       v
TestResult
       |
       v
Evidence
```

A request moves through the target boundary before reaching the simulated ECU:

```text
SecurityTestCase
       |
       | request
       v
SecurityTestRunner
       |
       v
ECUTarget
       |
       v
ECUAdapter
       |
       v
ECUSimulator
       |
       | ECUResponse
       v
ECUAdapter
       |
       v
SecurityTestRunner
       |
       | compare expected / actual
       v
TestResult
```

The Security Test Runner interacts with the target through the defined interface instead of directly calling ECU implementation details.

---

## Request Validation

The simulated ECU validates incoming requests.

The current request validation distinguishes between malformed requests, unsupported operations, and valid operations that violate request or state constraints.

A malformed or missing operation results in:

```text
Invalid or Missing Operation
       |
       v
INVALID_REQUEST
```

An unsupported operation results in:

```text
Unknown Operation
       |
       v
UNSUPPORTED_OPERATION
```

A valid request that violates parameter or ECU-state constraints results in:

```text
Invalid Parameter or ECU State
       |
       v
REQUEST_REJECTED
```

Invalid request handling is part of the ECU simulator. The Security Test Runner evaluates the response returned by the target.

---

## Test Cases

### TC-001 — Diagnostic Authorization

TC-001 verifies authorization behavior for the protected diagnostic operation.

The protected operation is:

```text
PROTECTED_OPERATION
```

The expected behavior is:

```text
Unauthorized → ACCESS_DENIED
Authorized   → ACCESS_GRANTED
```

For the controlled vulnerable execution:

```text
Authorization=false
PROTECTED_OPERATION
       |
       v
Expected = ACCESS_DENIED
Actual   = ACCESS_GRANTED
Result   = FAIL
```

For the secure regression retest:

```text
Authorization=false
PROTECTED_OPERATION
       |
       v
Expected = ACCESS_DENIED
Actual   = ACCESS_DENIED
Result   = PASS
```

Authorized behavior is also verified:

```text
Authorization=true
PROTECTED_OPERATION
       |
       v
ACCESS_GRANTED
```

### TC-002 — Message Validation

TC-002 verifies request validation through the existing target abstraction.

The established response semantics are:

```text
Invalid request structure → INVALID_REQUEST
Unsupported operation     → UNSUPPORTED_OPERATION
Invalid parameter data    → REQUEST_REJECTED
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

The behavior is evaluated through the externally observable ECU response.

### TC-003 — Regression Workflow

TC-003 represents the controlled regression workflow for the diagnostic authorization property.

The lifecycle is:

```text
Vulnerable Reproduction
       |
       v
Secure Retest
       |
       v
Regression Evidence
       |
       v
Authorized Behavior Verification
```

The workflow reuses the established test and evidence architecture and does not introduce a parallel execution path.

---

## Automated Security Regression

The automated regression suite is implemented in:

```text
04_tests/test_security_regression.py
```

The suite uses the established architecture:

```text
Regression Test
       |
       v
SecurityTestCase
       |
       v
SecurityTestRunner
       |
       v
ECUAdapter
       |
       v
Fresh Secure ECUSimulator
       |
       v
TestResult
       |
       v
EvidenceGenerator
```

The suite verifies seven established scenarios:

```text
1. Unauthorized protected operation → ACCESS_DENIED
2. Authorized protected operation   → ACCESS_GRANTED
3. Invalid message                  → INVALID_REQUEST
4. Unsupported operation            → UNSUPPORTED_OPERATION
5. Boundary input 256               → REQUEST_REJECTED
6. Blocked ECU state                → REQUEST_REJECTED
7. Regression evidence              → PASS
```

Each automated regression scenario uses a fresh secure ECU simulator with explicitly configured conditions.

The controlled vulnerable reproduction remains separate from these secure automated regression scenarios.

---

## Evidence Integration

The Evidence Framework records the completed `TestResult` as structured evidence.

The execution relationship is:

```text
Security Test
       |
       v
Test Execution
       |
       v
TestResult
       |
       v
EvidenceGenerator
       |
       v
Evidence
```

The Evidence Framework does not implement ECU security policy and does not control test execution.

Finding documentation consumes existing test and evidence results without modifying target behavior, test execution, or evidence generation.

---

## CI/CD Security Regression Architecture

The CI/CD layer invokes the established regression suite.

The configured execution path is:

```text
GitHub Event
       |
       v
GitHub Actions
       |
       v
Checkout Repository
       |
       v
Python 3.12
       |
       v
Install Dependencies
       |
       v
pytest Security Regression Suite
       |
       v
Generate Evidence
       |
       v
Upload Evidence Artifact
```

The workflow is implemented in:

```text
.github/workflows/security-regression.yml
```

The CI Single Source of Truth for the automated security regression scenarios is:

```text
04_tests/test_security_regression.py
```

The CI evidence path reuses the existing Evidence Framework:

```text
Security Regression Tests
       |
       v
EvidenceGenerator
       |
       v
Evidence
       |
       v
Evidence.to_json()
       |
       v
CI Evidence JSON Files
       |
       v
GitHub Actions Artifact
```

The workflow is configured for:

```text
push
pull_request
```

The configured test dependency is:

```text
pytest>=9,<10
```

The CI workflow does not introduce a second security-test implementation, a second Evidence model, or alternative evidence semantics.

---

## Security Finding Documentation

Security finding documentation is maintained as a documentation layer above the established test and evidence workflow.

The relationship is:

```text
Security Requirement
       |
       v
Security Test
       |
       v
Test Execution
       |
       v
Evidence
       |
       v
Example Finding
       |
       v
Root Cause / Recommendation / Fix / Retest
       |
       v
Regression Relationship
```

For SEC-001, the documented controlled deviation is:

```text
TC-001

Expected = ACCESS_DENIED
Actual   = ACCESS_GRANTED
Result   = FAIL

       |
       v

SEC-001

Unauthorized access to protected diagnostic operation
```

The modeled root cause is:

```text
Authorization state is not enforced before granting the protected operation.
```

The modeled remediation is:

```text
Enforce authorization before granting the protected operation.
```

These statements describe the controlled simulator behavior and are not claims about a real production ECU.

For SEC-002, the documentation records the TC-002 validation assessment where no security-relevant deviation was reproduced.

The finding documentation does not introduce a finding-management engine, database, automated finding ingestion, or generalized vulnerability lifecycle.

---

## Determinism

Deterministic behavior is a core property of the architecture.

For the same:

* security mode
* authorization state
* request

the simulator produces the same response.

The architecture does not depend on:

* physical hardware
* vehicle networks
* external services
* network access
* random test data

The Evidence Framework generates a runtime timestamp. The timestamp can therefore differ between executions. The remaining evidence fields are derived from the test execution and target state.

The controlled regression workflow remains deterministic because the vulnerable and secure target states are explicitly configured.

Automated regression tests use deterministic inputs and fresh, explicitly configured secure ECU simulator instances for individual scenarios.

---

## Architectural Boundaries

The current implementation maintains the following boundaries:

```text
Security Test Definition
        |
        v
Security Test Execution
        |
        v
Target Interface
        |
        v
Simulated System Under Test
        |
        v
Observed ECU Response
        |
        v
Test Result
        |
        v
Evidence
```

Automated regression verification operates around the established security-test architecture:

```text
Established Security Properties
        |
        v
Automated pytest Verification
        |
        v
Existing Security-Test Architecture
```

CI/CD remains outside the security-test implementation:

```text
GitHub Event
        |
        v
GitHub Actions
        |
        v
Existing Regression Suite
        |
        v
Existing Evidence Generation
        |
        v
CI Artifact
```

Finding documentation remains outside test execution:

```text
Test Execution
        |
        v
Evidence
        |
        v
Finding Documentation
```

---

## Simulation Boundary

The current implementation is completely local and simulated.

The following are outside the current implementation:

* real CAN communication
* real UDS communication
* physical ECU access
* vehicle-network communication
* production-system testing
* OEM-system integration

The `ECUTarget` abstraction provides a software boundary for target interaction. No real-world communication adapter is implemented.

The CI/CD environment executes the same simulated Python environment and does not provide a connection to a real vehicle, ECU, CAN network, UDS endpoint, OEM system, or production system.

---

## Future Target Extension

The target abstraction provides an extension point for future compatible test targets.

Conceptually:

```text
                       +------------------+
                       |                  |
                       v                  v
                ECUSimulator       Future Target
                       |                  |
                       +--------+---------+
                                |
                                v
                            ECUTarget
                                ^
                                |
                         SecurityTestRunner
                                |
                                v
                         Evidence Framework
```

This diagram represents an architectural possibility, not a current implementation.

The repository currently uses the simulated ECU only.

No real ECU adapter, CAN adapter, or UDS adapter is implemented.

A future target would need to satisfy the defined target interaction contract without requiring changes to the fundamental security-test execution model.

---

## Current Architectural Scope

The current implementation provides:

```text
Deterministic ECU simulation
Secure and vulnerable security modes
Authorization handling
Protected operation handling
Request validation
Target abstraction
Security-test execution
Expected-versus-actual evaluation
Structured test results
Structured evidence
Evidence validation
JSON serialization
TC-001 Diagnostic Authorization
TC-002 Message Validation
TC-003 Regression Workflow
Controlled regression evidence generation
Authorized-behavior verification during the regression workflow
SEC-001 example finding documentation
SEC-002 example finding documentation
Finding documentation linked to existing test and evidence results
Automated pytest security regression verification
Seven automated regression scenarios
Regression-evidence verification for the secure retest
Minimal GitHub Actions CI/CD execution of the security regression suite
Push-triggered CI execution
Configured pull-request CI triggering
CI evidence generation
CI evidence JSON serialization
GitHub Actions evidence artifact upload
CI failure propagation for a failed regression assertion
```

The following capabilities remain outside the current implementation:

```text
Real CAN communication
Real UDS communication
Physical ECU communication
Vehicle-network communication
Production-system testing
OEM-system integration
Generalized security-finding management
Automated finding ingestion
Historical finding tracking
CVSS calculation
Historical regression comparison
Generalized regression orchestration
Automatic regression-test generation
Deployment automation
Production CI/CD integration
Automatic remediation
```

---

## Architectural Principles

The architecture follows these principles.

### 1. Separate the Test from the System Under Test

The security test does not depend directly on the internal implementation of the ECU simulator.

The target abstraction provides the boundary between test execution and the system under test.

### 2. Keep Security Behavior in the Target

The simulated ECU is responsible for its security behavior.

The Security Test Runner evaluates that behavior rather than implementing or replacing it.

### 3. Separate Execution from Evidence

The Security Test Runner produces a `TestResult`.

The Evidence Framework consumes the completed result and records the observation.

### 4. Keep Expected Security Behavior Independent from the Implementation

The expected result is derived from the security requirement represented by the test case.

The original security expectation remains `ACCESS_DENIED` during both vulnerable-state reproduction and secure retest.

### 5. Keep the Simulation Deterministic

Equivalent input and target state produce equivalent target behavior.

Automated regression scenarios maintain this property through deterministic inputs and explicitly configured secure simulator instances.

### 6. Reuse Existing Architectural Boundaries for Regression Testing

Regression verification uses the established security-test and target architecture.

It does not introduce a separate communication path, target abstraction, or test-result mechanism solely for regression testing.

### 7. Keep Workflow Boundaries Explicit

Each layer is responsible for its defined function.

The target provides system-under-test behavior.

The Security Test Runner executes and evaluates security tests.

The Evidence Framework records completed observations.

Automated regression tests verify established security properties.

The CI/CD workflow provides automated execution and evidence artifact handling.

Finding documentation records security observations without becoming part of the execution architecture.

---

## Verification

The current repository has been locally verified with:

```text
pytest -v
```

Result:

```text
41 passed in 0.16s
```

The dedicated automated security regression suite has also been verified with:

```text
pytest .\04_tests\test_security_regression.py -v
```

Result:

```text
7 passed in 0.06s
```

The verified full-suite test distribution is:

| Test Area                       |  Tests |
| ------------------------------- | -----: |
| ECU Simulation                  |      6 |
| Evidence Framework              |     14 |
| Foundation                      |      1 |
| Security Regression             |      7 |
| TC-001 Diagnostic Authorization |      4 |
| TC-002 Message Validation       |      5 |
| Test Runner                     |      4 |
| **Total**                       | **41** |

The local CI execution sequence has also been verified:

```text
pytest -v 04_tests/test_security_regression.py
       |
       v
generate_regression_evidence(...)
       |
       v
6 CI evidence JSON files
```

The generated evidence uses the existing `Evidence` model and its JSON serialization path.

The GitHub Actions workflow has been successfully executed through a push-triggered run on `main`.

The documented successful CI execution was:

```text
Workflow: Security Regression
Trigger: push
Commit: 78c943f
Status: Success
Artifact: security-regression-evidence
```

A controlled failure test was also executed on a temporary branch. The regression expectation was deliberately changed so that the first security regression assertion failed while the remaining six tests passed locally:

```text
F......

1 failed, 6 passed
```

The corresponding GitHub Actions workflow run failed with exit code `1`, as expected.

The CI evidence artifact was still produced and uploaded because evidence generation and artifact upload use:

```text
if: always()
```

The controlled failure state was subsequently restored.

The restored regression suite was locally verified with:

```text
7 passed
```

The `pull_request` trigger is configured in the workflow, but a separate pull-request execution has not been independently verified.

GitHub Actions reported a Node.js 20 deprecation warning for the currently used GitHub Actions components. The warning did not prevent the verified CI executions.

---

## Architecture and Project Scope

The architecture is intentionally smaller than a real automotive cybersecurity test environment.

The demonstrated workflow is:

```text
Security Requirement
       |
       v
Reproducible Security Test
       |
       v
Controlled Test Execution
       |
       v
Expected-versus-Actual Evaluation
       |
       v
Structured Evidence
       |
       v
Controlled Regression Retest
       |
       v
Automated Regression Verification
       |
       v
CI/CD Execution
       |
       v
Machine-Readable Evidence Artifact
```

The project does not attempt to reproduce a complete automotive communication stack, production ECU, or real vehicle environment.

The established architectural boundaries provide the separation required for the demonstrated workflow while keeping the implementation deterministic and local.

---

## Historical Architecture Development

The following section records how the current architecture developed. These entries are historical information and are separate from the current architectural description.

### Phase 1 — Repository Foundation

Phase 1 established the project and development foundation.

It introduced:

* Python project configuration
* pytest-based verification
* repository structure
* documentation structure
* project scope
* initial architectural decisions
* deterministic local development environment

### Phase 2 — ECU Simulation

Phase 2 implemented the deterministic simulated ECU.

It introduced:

* secure mode
* vulnerable mode
* authorization state
* protected operation handling
* request validation
* deterministic response statuses
* structured ECU responses

### Phase 3 — Security Test Architecture

Phase 3 separated security-test execution from the simulated ECU.

It introduced:

* `SecurityTestCase`
* `SecurityTestRunner`
* `TestResult`
* `ECUTarget`
* `ECUAdapter`

The resulting architecture established the target boundary used by later security tests.

### Phase 4 — Evidence Framework

Phase 4 introduced structured evidence generation.

It added:

* the Evidence model
* mandatory evidence fields
* evidence validation
* `PASS` / `FAIL` semantics
* runtime timestamps
* JSON serialization
* evidence generation from `TestResult`

The Evidence Framework remained separate from the ECU and Test Runner.

### Phase 5 — TC-001 Diagnostic Authorization

Phase 5 introduced the first dedicated security test case:

```text
TC-001 — Diagnostic Authorization
```

TC-001 reused the established test architecture and Evidence Framework.

No new communication layer was required.

### Phase 6 — TC-002 Message Validation

Phase 6 introduced the second dedicated security test case:

```text
TC-002 — Message Validation
```

TC-002 reused the existing security-test architecture and Evidence Framework.

### Phase 7 — TC-003 Regression Workflow

Phase 7 introduced the controlled regression workflow:

```text
TC-003 — Regression Workflow
```

The workflow included:

* controlled reproduction of the original vulnerable behavior
* preservation of the original security expectation
* secure retest of the same unauthorized condition
* expected-versus-actual evaluation through `SecurityTestRunner`
* generation of regression evidence
* validation of generated evidence
* verification that authorized behavior remains available

The implementation was a controlled local regression workflow.

### Phase 8 — Example Findings

Phase 8 introduced structured security finding documentation based on the established TC-001, TC-002, and TC-003 test and evidence workflow.

It introduced:

* SEC-001 example finding documentation
* SEC-002 example finding documentation
* structured security impact documentation
* qualitative exploitability assessment
* root-cause documentation where supported by implementation evidence
* recommendation and fix documentation
* retest documentation
* regression-test relationship documentation

The finding documentation remained separate from the execution architecture.

### Phase 9 — Automated Security Regression Suite

Phase 9 introduced the dedicated pytest security regression suite:

```text
04_tests/test_security_regression.py
```

The suite reused the existing security-test and evidence architecture and verified the established secure behavior through seven automated scenarios.

### Phase 10 — CI/CD Security Regression Pipeline

Phase 10 introduced the minimal GitHub Actions CI/CD pipeline for the established security regression suite.

The workflow was implemented in:

```text
.github/workflows/security-regression.yml
```

The CI workflow reused the established regression suite and Evidence Framework.

The workflow was configured for both `push` and `pull_request` events.

The documented Phase-10 verification included successful push-triggered execution, successful execution of the seven security regression tests in CI, generated CI evidence, evidence artifact upload, controlled CI failure behavior, and restoration of the secure regression expectation.

A separate pull-request workflow execution was not documented as an executed verification result.

### Later Project Phases

The project history also contains:

| Phase    | Development                  |
| -------- | ---------------------------- |
| Phase 11 | End-to-End Assessment        |
| Phase 12 | Professional Documentation   |
| Phase 13 | Technical Review             |
| Phase 14 | Recruiter / Interview Review |

These phases represent subsequent assessment, documentation, and review stages. They are retained as project-history information and do not represent additional implemented architecture capabilities.
