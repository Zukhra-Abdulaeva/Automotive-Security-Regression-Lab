# Architecture

## Purpose

The Automotive Security Regression Lab uses a deterministic software architecture for developing and executing automotive security tests against a simulated ECU.

The architecture separates the following responsibilities:

- security-test definition
- test execution
- target interaction
- simulated ECU behavior
- test-result evaluation
- evidence generation
- automated regression verification
- CI/CD execution and evidence artifact handling

The separation is intentional. A security test defines the expected security behavior, the simulated ECU provides the system-under-test behavior, the Security Test Runner evaluates the execution result, and the Evidence Framework records the resulting observation.

Automated regression tests provide a verification layer around these established components. The CI/CD workflow executes the established regression suite and handles the resulting evidence artifacts.

The project is fully simulated and deterministic. It does not communicate with real vehicles, real ECUs, CAN networks, UDS endpoints, OEM systems, or production systems.

---

## System Context

The project models the relationship between a security tester and an automotive system in a controlled Python environment.

A simplified real-world concept can be represented as:

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

The project does not implement this real-world communication stack.

Instead, the current implementation represents the testing workflow through the following local architecture:

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

Automated security regression tests execute around this established architecture:

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

The CI/CD layer invokes the established regression suite:

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

The CI/CD layer surrounds the existing regression architecture. Security-test execution, target behavior, result evaluation, and evidence generation remain responsibilities of the established Python components.

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
|        ECUSimulator       |
+-------------+-------------+
              |
              v
+---------------------------+
|        ECUResponse        |
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

Each component has a defined responsibility.

The architecture keeps security-test logic, ECU security behavior, result evaluation, and evidence generation separate.

Automated regression verification uses these existing components rather than introducing another target, adapter, runner, response model, or evidence model.

The CI/CD workflow provides the execution environment around the established regression suite. It does not replace the existing security-test architecture.

---

## SecurityTestCase

`SecurityTestCase` represents the definition of a security test.

The current implementation contains:

- `test_id`
- `description`
- `request`
- `expected_status`

The test case defines the request that is sent to the target and the response status expected for the defined security scenario.

For TC-001, the test case represents the protected diagnostic operation and the expected authorization behavior.

The test case does not implement the ECU security policy.

The expected result is therefore defined independently from the concrete implementation of the simulated ECU.

Automated regression scenarios use the same `SecurityTestCase` structure. The dedicated regression suite creates its own test-case instances inside:

```text
04_tests/test_security_regression.py
```

These scenarios use:

```text
test_id = "TC-003"
```

They therefore reuse the established `SecurityTestCase` structure and execution architecture without reusing the same TC-001 `SecurityTestCase` instance or definition.

The relationship is:

```text
Automated Regression Test
       |
       v
04_tests/test_security_regression.py
       |
       v
SecurityTestCase
       |
       +-- test_id = "TC-003"
       |
       +-- request = defined regression scenario
       |
       +-- expected_status = established security behavior
       |
       v
SecurityTestRunner
```

The expected status represents the security behavior required by the test scenario. It is not derived from the current simulator response.

---

## SecurityTestRunner

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

The Test Runner does not access internal ECU state.

It does not implement:

- ECU security policy
- authorization decisions
- security finding management
- evidence storage
- regression orchestration
- CI/CD

The Test Runner executes and evaluates the security test. The target remains responsible for the behavior being tested.

For regression verification, the existing `SecurityTestRunner` performs the expected-versus-actual comparison. No separate regression execution engine is introduced.

---

## ECUTarget

`ECUTarget` defines the target interface used by the Security Test Runner.

The abstraction separates the test infrastructure from the concrete target implementation.

The current relationship is:

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

The target interface defines how the test infrastructure interacts with the system under test.

The current implementation uses the simulated ECU behind this interface.

No real vehicle communication protocol is implemented through `ECUTarget`.

Automated regression tests execute against the existing simulated target through the same target boundary.

---

## ECUAdapter

`ECUAdapter` connects the abstract `ECUTarget` interface to the concrete `ECUSimulator`.

Its responsibility is to forward requests to the configured target and return the resulting response.

The adapter does not:

- define security requirements
- implement security-test logic
- make authorization decisions
- evaluate security findings
- generate evidence
- modify test results

The adapter therefore provides the boundary between the generic test-execution layer and the concrete simulated target.

This separation keeps the test infrastructure independent from the concrete ECU simulator implementation.

Automated regression execution uses the same adapter boundary.

The CI/CD workflow does not bypass the adapter. It invokes the established regression suite, which continues to use the target abstraction and adapter.

---

## ECUSimulator

`ECUSimulator` represents the simulated ECU and is the system under test.

Its responsibilities include:

- maintaining the configured security mode
- maintaining the authorization state
- validating incoming requests
- processing the requested operation
- applying the configured security behavior
- returning a deterministic `ECUResponse`

The simulator supports two security modes:

```text
secure
vulnerable
```

### Secure Mode

Secure mode enforces authorization before granting the protected operation.

Unauthorized access is represented as:

```text
authorization = false
PROTECTED_OPERATION
       |
       v
ACCESS_DENIED
```

Authorized access is represented as:

```text
authorization = true
PROTECTED_OPERATION
       |
       v
ACCESS_GRANTED
```

### Vulnerable Mode

Vulnerable mode intentionally reproduces the authorization deviation used by the security tests:

```text
authorization = false
PROTECTED_OPERATION
       |
       v
ACCESS_GRANTED
```

The vulnerable behavior is a controlled simulation condition. It does not represent a real ECU vulnerability or a claim about a production automotive system.

The simulator remains independent from the Security Test Runner and Evidence Framework.

It does not generate, store, or evaluate test evidence.

Automated regression scenarios use fresh secure simulator instances and explicitly configure the required authorization and ECU state.

---

## ECUResponse

The simulator returns an `ECUResponse`.

The current response model contains:

- `status`
- `operation`

The supported response statuses are:

```text
ACCESS_GRANTED
ACCESS_DENIED
INVALID_REQUEST
UNSUPPORTED_OPERATION
REQUEST_REJECTED
```

The response represents the behavior observed by the security-test infrastructure.

For a given security mode, authorization state, and request, the simulator produces a deterministic response.

The response can be converted into a dictionary representation using:

```text
to_dict()
```

---

## TestResult

`TestResult` represents the evaluated outcome of a security-test execution.

The result is created by comparing the expected status defined by the security test with the actual status returned by the target.

Conceptually:

```text
Expected Status
       |
       +
       |
Actual Status
       |
       v
Comparison
       |
       v
TestResult
```

The `TestResult` forms the boundary between test execution and evidence generation.

The ECU simulator does not determine the final test result. It returns the response representing the behavior of the system under test.

For the controlled vulnerable authorization scenario:

```text
Expected = ACCESS_DENIED
Actual   = ACCESS_GRANTED
Result   = FAIL
```

The resulting `TestResult` is therefore a failed security-test result.

For the secure regression retest:

```text
Expected = ACCESS_DENIED
Actual   = ACCESS_DENIED
Result   = PASS
```

The distinction between the security-test result and the test-framework result is important.

A pytest test can pass because it correctly detects an expected security deviation in a controlled vulnerable scenario. In that situation, the pytest result represents successful verification of the test assertion, while the underlying `TestResult` can still represent `FAIL`.

For a secure regression scenario, the underlying `TestResult` normally represents `PASS` and the corresponding pytest assertion also passes.

The CI workflow preserves this distinction. A successful GitHub Actions job indicates successful execution of the configured pytest verification. It does not introduce different semantics for `TestResult` or `Evidence`.

---

## Evidence Framework

The Evidence Framework records the result of a completed security-test execution in a structured format.

The current Evidence model contains:

- `test_id`
- `timestamp`
- `target`
- `preconditions`
- `input`
- `expected`
- `actual`
- `result`
- `notes`

The Evidence Framework operates after test execution:

```text
Security Test
       |
       v
Test Result
       |
       v
Evidence
```

The Evidence Framework does not implement security behavior.

It does not change the ECU response, modify the expected result, or determine the security policy of the system under test.

Evidence represents the observation produced by a test execution.

Regression verification reuses the existing Evidence Framework. The generated evidence is derived from the executed result.

The CI/CD evidence path is:

```text
Security Regression Execution
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

The CI workflow does not introduce a second evidence model or a second evidence-generation implementation.

The generated JSON files are serialized instances of the existing `Evidence` model.

The CI artifact provides the generated evidence as a workflow output. It is not a separate finding-management or historical evidence system.

---

## Evidence Result Semantics

The Evidence Framework currently supports two result values:

```text
PASS
FAIL
```

The semantics are:

```text
PASS
Expected == Actual
```

and:

```text
FAIL
Expected != Actual
```

For example, if the security requirement requires:

```text
Expected = ACCESS_DENIED
```

but the controlled vulnerable ECU returns:

```text
Actual = ACCESS_GRANTED
```

the resulting evidence represents:

```text
FAIL
```

The `FAIL` indicates that the observed behavior did not match the expected security behavior.

It does not automatically constitute a formal security vulnerability finding.

Finding documentation is maintained separately from the execution and evidence components.

The finding examples document security requirement, observed behavior, security impact, exploitability, root cause where supported, recommendation, fix, retest, and regression relationship.

Generalized finding management, automated finding ingestion, historical finding tracking, and generalized remediation management are not part of the current architecture.

---

## Complete Test Execution Flow

The complete local execution flow is:

```text
SecurityTestCase
       |
       | request
       v
SecurityTestRunner
       |
       | handle_request()
       v
ECUTarget
       |
       v
ECUAdapter
       |
       | handle_request()
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
       |
       v
EvidenceGenerator
       |
       v
Evidence
       |
       v
JSON
```

The execution path separates target behavior from test evaluation and evidence generation.

The ECU simulator therefore remains unaware of the Evidence Framework.

Automated regression tests add assertions around this established execution path. They do not change the request, response, result, or evidence flow.

The CI/CD execution path surrounds the established flow:

```text
GitHub Event
       |
       v
GitHub Actions
       |
       v
pytest
       |
       v
04_tests/test_security_regression.py
       |
       v
Existing Test Execution Flow
       |
       v
EvidenceGenerator
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

The CI/CD layer therefore provides an execution environment for the established test and evidence architecture rather than a parallel security-test implementation.

---

## TC-001 — Diagnostic Authorization

TC-001 verifies the security requirement:

```text
Protected diagnostic operations shall require authorization.
```

The protected operation is:

```text
PROTECTED_OPERATION
```

The secure behavior for an unauthorized request is:

```text
authorization = false
PROTECTED_OPERATION
       |
       v
ACCESS_DENIED
```

The secure behavior for an authorized request is:

```text
authorization = true
PROTECTED_OPERATION
       |
       v
ACCESS_GRANTED
```

The controlled vulnerable behavior is:

```text
authorization = false
PROTECTED_OPERATION
       |
       v
ACCESS_GRANTED
```

The security test evaluates these responses through the existing test architecture.

The test does not access the internal authorization implementation of the simulated ECU.

The diagnostic authorization property established by TC-001 is also used by the regression workflow.

---

## TC-002 — Message Validation

TC-002 verifies message and request validation behavior through the existing target abstraction.

The execution path is:

```text
TC-002
   |
   v
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

TC-002 does not introduce a new communication layer.

The security test does not access internal ECU implementation details.

The expected behavior remains defined by the security-test specification and is evaluated independently from the concrete ECU implementation.

---

## TC-003 — Regression Workflow

TC-003 demonstrates a controlled regression lifecycle for the diagnostic authorization security property.

The workflow uses the established security-test and target architecture:

```text
TC-003
   |
   v
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
EvidenceGenerator
   |
   v
Regression Evidence
```

The controlled vulnerable state reproduces the modeled authorization deviation:

```text
VULNERABLE

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

The failed security result demonstrates that the original security condition is detected by the established execution architecture.

The same unauthorized condition is then executed against the secure simulator:

```text
SECURE

authorization = false
PROTECTED_OPERATION
       |
       v
ACCESS_DENIED
```

The regression retest produces:

```text
Expected = ACCESS_DENIED
Actual   = ACCESS_DENIED
Result   = PASS
```

The resulting `TestResult` is used to generate and validate regression evidence.

Authorized behavior is also verified:

```text
authorization = true
PROTECTED_OPERATION
       |
       v
ACCESS_GRANTED
```

This verifies both restoration of the security property and preservation of the intended authorized operation.

The vulnerable-state reproduction and secure retest form the controlled regression lifecycle represented by TC-003.

---

## Automated Security Regression Suite

The automated security regression suite is implemented in:

```text
04_tests/test_security_regression.py
```

The suite reuses the existing security-test execution architecture:

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

Each regression scenario creates a fresh `ECUSimulator` in secure mode and explicitly configures the required authorization state and, where required, the ECU state.

The dedicated suite verifies the following established behaviors:

```text
1. Unauthorized protected operation

   Expected = ACCESS_DENIED

2. Authorized protected operation

   Expected = ACCESS_GRANTED

3. Invalid message

   Expected = INVALID_REQUEST

4. Unsupported operation

   Expected = UNSUPPORTED_OPERATION

5. Boundary input outside the accepted parameter range

   Expected = REQUEST_REJECTED

6. Protected operation in blocked ECU state

   Expected = REQUEST_REJECTED

7. Regression evidence for the secure unauthorized retest

   Expected = ACCESS_DENIED
   Actual   = ACCESS_DENIED
   Evidence Result = PASS
```

The boundary-input regression scenario uses an out-of-range parameter value of `256` and verifies that validation cannot be bypassed.

The blocked-state regression scenario verifies that an authorized request does not enable protected behavior when the ECU is in the blocked state.

The evidence regression scenario generates evidence from the executed secure retest and validates the resulting evidence object.

The regression suite does not introduce:

```text
A new target implementation

A new adapter

A new test runner

A new response model

A new evidence model

A generalized regression engine

Historical result comparison

Automatic finding management

CI/CD integration
```

The vulnerable-state reproduction remains part of the controlled regression workflow. The dedicated automated regression suite verifies established secure behavior.

---

## CI/CD Security Regression Architecture

The CI/CD workflow is implemented in:

```text
.github/workflows/security-regression.yml
```

The configured event triggers are:

```text
push
pull_request
```

The workflow execution path is:

```text
GitHub Event
       |
       v
Checkout Repository
       |
       v
Set up Python 3.12
       |
       v
Install Project Dependencies
       |
       v
Run Security Regression Tests
       |
       v
Generate CI Evidence
       |
       v
Upload CI Evidence
```

The security regression test execution is:

```text
GitHub Actions
       |
       v
pytest -v 04_tests/test_security_regression.py
       |
       v
04_tests/test_security_regression.py
       |
       v
Existing SecurityTestCase / SecurityTestRunner /
ECUAdapter / ECUSimulator / TestResult Path
```

The CI evidence path is:

```text
Security Regression Execution
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
ci-evidence/*.json
       |
       v
security-regression-evidence
```

The workflow uses Python 3.12, matching the project requirement:

```text
requires-python = ">=3.12"
```

The workflow installs the project's current development test dependency:

```text
pytest>=9,<10
```

The CI workflow does not contain separate security assertions for the individual security scenarios.

The security regression assertions remain in:

```text
04_tests/test_security_regression.py
```

This establishes the CI Single Source of Truth:

```text
04_tests/test_security_regression.py
             |
             v
Security Regression Logic
             |
             +--------------------+
             |                    |
             v                    v
        Local pytest       GitHub Actions
                                  |
                                  v
                                pytest
```

Local execution and CI execution therefore use the same regression test module.

The CI evidence generation also reuses the existing regression execution path and `EvidenceGenerator`.

The workflow does not introduce:

```text
A second security-test runner

A second Evidence model

Alternative evidence semantics
```

The workflow is limited to:

```text
Test execution

Evidence generation

Evidence artifact upload
```

The following functions are outside this CI/CD architecture:

```text
Deployment

Production integration

Vehicle communication

External security systems

Finding management

Historical regression comparison

Automatic remediation

Generalized regression orchestration
```

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

For SEC-001, the finding documents the controlled vulnerable authorization behavior reproduced by TC-001:

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

The root cause is traced to the deliberate vulnerable branch in the simulated ECU implementation.

For SEC-002, the finding documentation records that the TC-002 validation scenarios did not reproduce a security-relevant deviation:

```text
TC-002

Expected == Actual

       |
       v

No security-relevant deviation reproduced

       |
       v

SEC-002 example documentation
```

SEC-002 therefore does not represent a demonstrated vulnerability.

The finding documents do not introduce a finding-management engine, database, automated finding ingestion, or generalized vulnerability lifecycle.

---

## Security Test Result and Test Framework Result

The architecture distinguishes between the result of a security test and the result of the framework executing an assertion about that test.

For the controlled vulnerable behavior:

```text
SecurityTestCase expected: ACCESS_DENIED
ECUSimulator actual:       ACCESS_GRANTED
TestResult.passed:         False
```

A pytest test can pass because it verifies that this deviation was correctly detected.

Therefore:

```text
pytest PASS
```

does not necessarily mean:

```text
SecurityTestResult PASS
```

for the vulnerable-state demonstration.

For the secure regression retest:

```text
SecurityTestCase expected: ACCESS_DENIED
ECUSimulator actual:       ACCESS_DENIED
TestResult.passed:          True
pytest test:                PASS
```

The same distinction applies to CI execution.

A successful GitHub Actions job means that the configured pytest execution completed successfully. It does not introduce a new security-result semantic.

A failed pytest assertion causes the CI job to fail because the workflow does not treat a failed security regression assertion as a successful pipeline result.

---

## Request and Response Flow

A request moves through the target boundary before reaching the simulated ECU.

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

This preserves the separation between test execution and system-under-test behavior.

---

## Invalid Requests

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

Invalid request handling is part of the ECU simulator.

The Security Test Runner does not implement request validation. It evaluates the response returned by the target.

Automated regression verification checks these established validation behaviors through the existing execution architecture.

---

## Determinism

Deterministic behavior is a core property of the architecture.

For the same:

- security mode
- authorization state
- request

the simulator produces the same response.

This allows security tests to be repeated under equivalent conditions and makes test results reproducible.

The current architecture does not depend on:

- physical hardware
- vehicle networks
- external services
- network access
- random test data

The Evidence Framework generates a runtime timestamp. The timestamp is therefore expected to differ between executions.

The remaining evidence fields are derived from the test execution and target state.

The controlled regression workflow remains deterministic because the vulnerable and secure target states are explicitly configured and the same defined security condition is evaluated through the established execution architecture.

Automated regression tests preserve this determinism by using deterministic inputs and fresh, explicitly configured secure ECU simulator instances for individual scenarios.

CI execution uses the same defined regression inputs and simulated target behavior.

---

## Architectural Separation

The central architectural separation is:

```text
Security Test Definition
          |
          v
    Test Execution
          |
          v
    Target Boundary
          |
          v
    System Under Test
          |
          v
      Test Result
          |
          v
       Evidence
```

The security test does not depend on internal simulator attributes.

The test infrastructure does not directly manipulate internal state such as:

```text
_internal_state

_authorized

_security_policy
```

Communication with the target occurs through the defined target interface.

The Evidence Framework also does not access internal ECU state.

The architecture therefore maintains clear boundaries between:

- what is being tested
- how the test is executed
- how the target behaves
- how the result is evaluated
- how the observation is recorded

The controlled regression workflow follows the same separation.

Finding documentation consumes existing test and evidence results without modifying target behavior, test execution, or evidence generation.

Automated regression tests configure and evaluate the target through its defined public behavior and existing execution architecture.

CI/CD provides the external execution mechanism while the established Python architecture remains responsible for security-test execution, result evaluation, and evidence generation.

---

## Simulation Boundary

The current implementation is completely local and simulated.

It does not provide:

- real CAN communication
- real UDS communication
- physical ECU access
- vehicle-network communication
- production-system testing
- OEM-system integration

The `ECUTarget` abstraction provides a software boundary for target interaction, but no real-world communication adapter is currently implemented.

The project therefore demonstrates the testing architecture and workflow without introducing external automotive communication.

The CI/CD environment executes the same simulated Python environment. It does not provide a connection to a real vehicle, ECU, CAN network, UDS endpoint, OEM system, or production system.

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

The following capabilities are outside the current implementation:

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

These capabilities are not part of the current architecture.

---

## Architectural Principles

The architecture follows the following principles.

### 1. Separate the Test from the System Under Test

The security test must not depend directly on the internal implementation of the ECU simulator.

The target abstraction provides the boundary between test execution and the system under test.

### 2. Keep Security Behavior in the Target

The simulated ECU is responsible for its security behavior.

The Security Test Runner evaluates that behavior rather than implementing or replacing it.

### 3. Separate Execution from Evidence

The Security Test Runner produces a `TestResult`.

The Evidence Framework consumes the completed result and records the observation.

Evidence generation therefore does not control test execution.

### 4. Keep Expected Security Behavior Independent from the Implementation

The expected result is derived from the security requirement represented by the test case.

The expected result must not be changed simply to make an insecure implementation pass.

The same principle applies to the controlled regression workflow. The original security expectation remains `ACCESS_DENIED` during both vulnerable-state reproduction and secure retest.

Automated regression tests preserve the same principle by defining expected statuses independently from the concrete simulator response.

The CI workflow invokes the established regression suite without redefining its expected security behavior.

### 5. Keep the Simulation Deterministic

Equivalent input and target state must produce equivalent target behavior.

This is required for reproducible local security testing.

Automated regression scenarios maintain this property through deterministic inputs and explicitly configured secure simulator instances.

CI execution uses the same established regression scenarios.

### 6. Reuse Existing Architectural Boundaries for Regression Testing

Regression verification uses the established security-test and target architecture.

It does not introduce a separate communication path, target abstraction, or test-result mechanism solely for regression testing.

The regression workflow operates on the existing test definition, target behavior, `TestResult`, and Evidence Framework.

Automated regression tests follow the same principle by reusing the existing test-case, runner, target, simulator, result, and evidence components.

CI/CD extends this principle to automated execution. GitHub Actions invokes the established regression suite and evidence-generation path rather than implementing separate CI-specific security-test logic or evidence semantics.

### 7. Keep Workflow Boundaries Explicit

Each layer is responsible for its defined function.

The target provides system-under-test behavior.

The Security Test Runner executes and evaluates security tests.

The Evidence Framework records completed observations.

Automated regression tests verify established security properties.

The CI/CD workflow provides automated execution and evidence artifact handling.

Finding documentation records security observations without becoming part of the execution architecture.

---

## Architecture and Project Scope

The architecture is intentionally smaller than a real automotive cybersecurity test environment.

The purpose of the project is to demonstrate:

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

The architecture provides the separation required for the demonstrated workflow while keeping the implementation deterministic, local, and understandable.

The established architectural boundaries provide the basis for additional workflow stages without changing the fundamental responsibilities of the existing components.

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

```text
ECU Simulation Tests:               6

Evidence Framework Tests:          14

Foundation Tests:                   1

Security Regression Tests:          7

TC-001 Diagnostic Authorization:    4

TC-002 Message Validation:          5

Test Runner Tests:                  4

-------------------------------------

Total:                              41
```

The dedicated regression suite contains seven automated scenarios.

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

The evidence records contain the established fields:

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

The GitHub Actions workflow has been successfully executed through a push-triggered run on `main`.

The documented successful CI execution was:

```text
Workflow: Security Regression

Trigger: push

Commit: 78c943f

Status: Success

Artifact: security-regression-evidence
```

The artifact was successfully uploaded by the workflow.

A controlled failure test was also executed on a temporary branch. The regression expectation was deliberately changed so that the first security regression assertion failed while the remaining six tests passed locally:

```text
F......

1 failed, 6 passed
```

The corresponding GitHub Actions workflow run failed with exit code `1`, as expected.

The CI evidence artifact was still produced and uploaded during the failed workflow because evidence generation and artifact upload use:

```text
if: always()
```

The controlled failure state was subsequently restored.

The restored regression suite was executed locally again with:

```text
7 passed
```

The temporary failure branch remains intentionally retained as portfolio evidence of the controlled CI failure path.

The successful CI run and the controlled failure run verify the implemented push-triggered CI behavior, failure propagation, and evidence artifact handling.

The workflow also contains a `pull_request` trigger. Configuration of this trigger is part of the implemented workflow, but a separate pull-request execution is not claimed here as an executed verification result.

The GitHub Actions runner reported a Node.js 20 deprecation warning for the currently used GitHub Actions components. The warning did not prevent the workflow from completing successfully and is not part of the security-test result.

---

## Historical Architecture Development

The following section records how the current architecture developed. These entries are historical information and are kept separate from the current architectural description.

### Phase 1 — Repository Foundation

Phase 1 established the project and development foundation.

It introduced:

- Python project configuration
- pytest-based verification
- repository structure
- documentation structure
- project scope
- initial architectural decisions
- deterministic local development environment

### Phase 2 — ECU Simulation

Phase 2 implemented the deterministic simulated ECU.

It introduced:

- secure mode
- vulnerable mode
- authorization state
- protected operation handling
- request validation
- deterministic response statuses
- structured ECU responses

### Phase 3 — Security Test Architecture

Phase 3 separated security-test execution from the simulated ECU.

It introduced:

- `SecurityTestCase`
- `SecurityTestRunner`
- `TestResult`
- `ECUTarget`
- `ECUAdapter`

The resulting architecture established the target boundary used by later security tests.

### Phase 4 — Evidence Framework

Phase 4 introduced structured evidence generation.

It added:

- the Evidence model
- mandatory evidence fields
- evidence validation
- `PASS` / `FAIL` semantics
- runtime timestamps
- JSON serialization
- evidence generation from `TestResult`

The Evidence Framework was deliberately kept separate from the ECU and Test Runner.

### Phase 5 — TC-001 Diagnostic Authorization

Phase 5 introduced the first dedicated security test case:

```text
TC-001 — Diagnostic Authorization
```

TC-001 reused the established test architecture and Evidence Framework.

No new communication layer was required.

The test evaluates the authorization behavior of the simulated ECU and provides the security property used by the subsequent regression workflow.

### Phase 6 — TC-002 Message Validation

Phase 6 introduced the second dedicated security test case:

```text
TC-002 — Message Validation
```

TC-002 reused the existing security-test architecture and Evidence Framework.

The test validates message and request handling through the existing target abstraction and does not introduce real automotive communication.

### Phase 7 — TC-003 Regression Workflow

Phase 7 introduced the controlled regression workflow:

```text
TC-003 — Regression Workflow
```

TC-003 reused the established security-test and evidence architecture to verify the regression lifecycle for the diagnostic authorization security property.

The workflow included:

- controlled reproduction of the original vulnerable behavior
- preservation of the original security expectation
- secure retest of the same unauthorized condition
- expected-versus-actual evaluation through `SecurityTestRunner`
- generation of regression evidence from the executed result
- validation of the generated evidence
- verification that authorized behavior remains available

The implementation was a controlled local regression workflow.

### Phase 8 — Example Findings

Phase 8 introduced structured security finding documentation based on the established TC-001, TC-002, and TC-003 test and evidence workflow.

It introduced:

- SEC-001 example finding documentation for the controlled TC-001 authorization deviation
- SEC-002 example finding documentation for the TC-002 validation assessment where no security-relevant deviation was reproduced
- structured security impact documentation
- qualitative exploitability assessment
- root-cause documentation where supported by implementation evidence
- recommendation and fix documentation
- retest documentation
- regression-test relationship documentation

The finding documentation remained separate from the execution architecture.

### Phase 9 — Automated Security Regression Suite

Phase 9 introduced the dedicated pytest security regression suite:

```text
04_tests/test_security_regression.py
```

The suite verified established security properties using the existing:

- `SecurityTestCase`
- `SecurityTestRunner`
- `ECUAdapter`
- `ECUSimulator`
- `TestResult`
- Evidence Framework

The automated regression suite verified:

- unauthorized protected operation is denied
- authorized protected operation remains allowed
- invalid messages are rejected
- unsupported operations are rejected
- out-of-range boundary input does not bypass validation
- blocked ECU state does not enable protected behavior
- regression evidence correctly represents the secure retest

Each regression scenario used a fresh secure ECU simulator with explicitly configured authorization and ECU state.

The vulnerable-state reproduction remained part of the controlled regression workflow.

### Phase 10 — CI/CD Security Regression Pipeline

Phase 10 introduced the minimal GitHub Actions CI/CD pipeline for the established security regression suite.

The workflow was implemented in:

```text
.github/workflows/security-regression.yml
```

The configured execution path was:

```text
GitHub Event
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

The CI/CD layer reused the established regression suite and evidence architecture.

The Single Source of Truth remained:

```text
04_tests/test_security_regression.py
```

GitHub Actions executed this existing regression logic and did not implement a second security-test implementation.

The CI evidence path reused the existing `EvidenceGenerator` and `Evidence.to_json()` serialization:

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

The workflow was configured for both `push` and `pull_request` events.

The implemented CI/CD layer was intentionally limited to automated security regression execution and evidence artifact collection.

The documented Phase-10 verification included:

- successful push-triggered GitHub Actions execution
- successful execution of the seven security regression tests in CI
- generated CI evidence
- uploaded `security-regression-evidence` artifact
- controlled CI failure behavior
- evidence artifact availability after the controlled failure
- restoration of the secure regression expectation
- successful local re-execution after restoration

A separate pull-request workflow execution was not documented as an executed verification result.

---

## Architectural Boundaries

The following boundaries define the current implementation:

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

Automated regression verification remains outside the target behavior:

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

These boundaries prevent the supporting workflow layers from replacing or duplicating the responsibilities of the core security-test architecture.

---

## Summary

The current architecture provides a deterministic and local environment for automotive security regression testing against a simulated ECU.

The core execution path is:

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

The architecture separates security-test definition, execution, target interaction, simulated ECU behavior, result evaluation, and evidence generation.

The established regression workflow reuses these boundaries rather than introducing a parallel execution architecture.

Automated pytest verification provides repeatable verification of established security properties.

GitHub Actions executes the same regression suite and collects machine-readable evidence artifacts.

The simulation boundary remains local and deterministic. No real vehicle, ECU, CAN network, UDS endpoint, OEM system, or production system is involved.

The architecture therefore provides the required foundation for reproducible automotive security testing while keeping the implementation intentionally controlled, understandable, and separate from production automotive communication systems.
