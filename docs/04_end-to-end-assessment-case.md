# End-to-End Security Assessment Case

## 1. Executive Summary

This document describes one complete, reproducible security-assessment chain for the Automotive Security Regression Lab.

The assessment follows the implemented engineering chain:

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
Evidence
        ↓
Security Finding
        ↓
Root Cause
        ↓
Fix / Secure State
        ↓
Retest
        ↓
Regression Test
        ↓
Automated Test
        ↓
CI/CD
```

The primary security property is:

```text
Protected diagnostic operations shall require authorization.
```

The central assessment case uses `PROTECTED_OPERATION` and an unauthorized requester.

TC-001 demonstrates the security-relevant deviation in the controlled vulnerable simulator mode:

```text
Authorization = false
Operation     = PROTECTED_OPERATION

Expected = ACCESS_DENIED
Actual   = ACCESS_GRANTED
Result   = FAIL
```

The deviation is caused by the implemented control flow of `ECUSimulator`: when `SecurityMode.VULNERABLE` is active, the simulator returns `ACCESS_GRANTED` before evaluating the authorization state.

The secure state is represented by `SecurityMode.SECURE`:

```text
Authorization = false
Operation     = PROTECTED_OPERATION

Expected = ACCESS_DENIED
Actual   = ACCESS_DENIED
Result   = PASS
```

TC-002 provides supporting validation coverage for malformed requests, unsupported operations, parameter boundaries, and the blocked ECU state.

TC-003 turns the established TC-001 security property into an automated regression workflow and additionally verifies structured regression evidence and authorized behavior.

The complete case is limited to the implemented simulation. It is not a real vehicle penetration test, real ECU assessment, OEM assessment, or production-system security assessment.

---

## 2. Scope

### 2.1 In Scope

The assessment covers:

```text
Simulated ECU
Protected diagnostic operation
Authorization state
Secure and controlled vulnerable security modes
ECU operational state
Request validation
Parameter validation
Security-test execution
Structured evidence generation
Security finding derivation
Secure retest
Automated regression testing
CI/CD execution and evidence artifact handling
```

The primary end-to-end path is TC-001.

TC-002 is included as supporting attack-surface and validation coverage.

TC-003 is included as the regression layer for the established TC-001 security property.

### 2.2 Out of Scope

The assessment does not cover:

```text
Real vehicles
Real ECUs
Real CAN communication
Real UDS communication
Real diagnostic networks
OEM systems
Customer systems or data
Production credentials
Production infrastructure
Physical ECU interfaces
Vehicle-network routing
Real-world exploitability
Real-world attack execution
Complete automotive protocol security
Complete ECU hardware security
```

The `VULNERABLE` mode is a deliberate simulation mechanism. Its behavior must not be interpreted as evidence that a corresponding vulnerability exists in a real ECU.

### 2.3 Assessment Boundary

The assessment boundary is the implemented local software chain:

```text
Security Test
      ↓
SecurityTestRunner
      ↓
ECUAdapter
      ↓
ECUSimulator
      ↓
ECUResponse
      ↓
TestResult
      ↓
Evidence
```

No external automotive system is part of the execution boundary.

---

## 3. System / ECU Architecture

### 3.1 Simulated ECU

The simulated ECU is implemented in:

```text
03_src/security_lab/ecu_simulator.py
```

The central request-processing interface is:

```text
ECUSimulator.handle_request(request)
```

The simulator provides:

```text
SecurityMode
    SECURE
    VULNERABLE

ECUState
    READY
    BLOCKED

Operation
    PROTECTED_OPERATION

ResponseStatus
    ACCESS_GRANTED
    ACCESS_DENIED
    INVALID_REQUEST
    UNSUPPORTED_OPERATION
    REQUEST_REJECTED
```

### 3.2 Test Architecture

The assessment uses the existing test architecture rather than introducing a separate execution path.

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
      ↓
TestResult
      ↓
EvidenceGenerator
      ↓
Evidence
```

Responsibilities are separated:

| Component | Responsibility |
| --- | --- |
| `SecurityTestCase` | Defines test condition and expected behavior |
| `SecurityTestRunner` | Executes request and evaluates expected versus actual status |
| `ECUTarget` | Defines target interface |
| `ECUAdapter` | Connects target interface to simulator |
| `ECUSimulator` | Implements simulated ECU behavior |
| `TestResult` | Represents evaluated test outcome |
| `Evidence` | Stores structured execution evidence |

### 3.3 Request Processing Flow

The implemented request-processing sequence is:

```text
Request received
      ↓
Request is a mapping?
      ├── No  → INVALID_REQUEST
      └── Yes
            ↓
Operation present and non-empty string?
      ├── No  → INVALID_REQUEST
      └── Yes
            ↓
Operation supported?
      ├── No  → UNSUPPORTED_OPERATION
      └── Yes
            ↓
Parameters are a mapping?
      ├── No  → INVALID_REQUEST
      └── Yes
            ↓
Optional value valid?
      ├── No  → REQUEST_REJECTED
      └── Yes
            ↓
ECU state BLOCKED?
      ├── Yes → REQUEST_REJECTED
      └── No
            ↓
Security mode
      ↓
Authorization decision
```

The exact order matters for the primary finding.

For the vulnerable TC-001 request, there is no `parameters` field, so the parameter-validation branch does not reject the request. The ECU remains in the default `READY` state. The vulnerable-mode branch is then reached before the authorization check.

---

## 4. Security Requirements

### 4.1 Primary Security Requirement

The primary security requirement is:

```text
Protected diagnostic operations shall require authorization.
```

For an unauthorized request:

```text
authorization = false
+
PROTECTED_OPERATION
        ↓
ACCESS_DENIED
```

For an authorized request:

```text
authorization = true
+
PROTECTED_OPERATION
        ↓
ACCESS_GRANTED
```

The expected result does not change when the simulator is used to reproduce the vulnerable state.

### 4.2 Supporting Validation Requirements

The implemented request-validation behavior distinguishes:

| Condition | Expected Response |
| --- | --- |
| Request is not a mapping | `INVALID_REQUEST` |
| Operation missing or empty | `INVALID_REQUEST` |
| Unsupported operation | `UNSUPPORTED_OPERATION` |
| Parameters are not a mapping | `INVALID_REQUEST` |
| Parameter outside `0..255` | `REQUEST_REJECTED` |
| Boolean parameter | `REQUEST_REJECTED` |
| ECU state is `BLOCKED` | `REQUEST_REJECTED` |

Valid numeric boundary values are:

```text
0
255
```

The out-of-range examples are:

```text
-1
256
```

TC-002 provides the dedicated coverage for these validation properties.

---

## 5. Threat Model

### 5.1 Threat Actor

The modeled threat actor is:

```text
Unauthorized diagnostic client
```

This is a logical test actor inside the simulation. It does not represent an actual external client connected to a vehicle.

### 5.2 Protected Asset

The modeled protected asset is the operation:

```text
PROTECTED_OPERATION
```

The relevant security property is authorization enforcement before the operation is granted.

### 5.3 Threat Condition

The primary threat condition is:

```text
Authorization = false
+
PROTECTED_OPERATION
```

### 5.4 Security Assumption

The simulated ECU is responsible for enforcing authorization for the protected operation.

The threat model is intentionally limited to behavior represented by the simulator.

### 5.5 Threat Scenario

The assessment asks whether an unauthorized requester can receive a grant for a protected operation.

The secure expectation is:

```text
Unauthorized requester
        ↓
PROTECTED_OPERATION
        ↓
Authorization check
        ↓
ACCESS_DENIED
```

The controlled vulnerable behavior is:

```text
Unauthorized requester
        ↓
PROTECTED_OPERATION
        ↓
VULNERABLE mode
        ↓
ACCESS_GRANTED
```

---

## 6. Attack Surface

The detailed attack-surface model is maintained in:

```text
01_threat_model/01_attack_surface.md
```

For this end-to-end case, the relevant attack-surface elements are:

| Element | Security Relevance | Test Coverage |
| --- | --- | --- |
| Request structure | Determines whether request processing can start | TC-002 |
| Operation selector | Determines requested operation | TC-001, TC-002 |
| Parameter structure | Controls validity of optional parameters | TC-002 |
| Parameter value | Tests range and rejection behavior | TC-002, TC-003 |
| Authorization state | Determines protected-operation access | TC-001, TC-003 |
| ECU state | Restricts operation execution | TC-002, TC-003 |
| Security mode | Models controlled vulnerable and secure states | TC-001, TC-003 |

The primary attack surface is the protected-operation authorization decision.

The assessment does not infer additional attack surfaces that are not represented by the implementation.

---

## 7. Attack Hypothesis

The primary hypothesis is:

> If authorization is missing or incorrectly enforced, an unauthorized diagnostic requester may be able to execute a protected operation.

The concrete test condition is:

```text
authorization = false
operation     = PROTECTED_OPERATION
```

The expected secure response is:

```text
ACCESS_DENIED
```

The controlled vulnerable response is:

```text
ACCESS_GRANTED
```

The hypothesis is therefore evaluated by comparing the actual simulator response with the unchanged security requirement.

---

## 8. Security Test

### 8.1 TC-001 — Diagnostic Authorization

TC-001 is the original security test defining the diagnostic-authorization property.

Implementation:

```text
03_src/security_lab/tc_001_diagnostic_authorization.py
```

Dedicated tests:

```text
04_tests/test_tc001_diagnostic_authorization.py
```

The TC-001 request is:

```json
{
  "operation": "PROTECTED_OPERATION"
}
```

The four dedicated scenarios are:

| Scenario | Mode | Authorization | Expected |
| --- | --- | ---: | --- |
| Unauthorized secure | `SECURE` | `false` | `ACCESS_DENIED` |
| Authorized secure | `SECURE` | `true` | `ACCESS_GRANTED` |
| Unauthorized vulnerable | `VULNERABLE` | `false` | `ACCESS_DENIED` |
| Vulnerable evidence | `VULNERABLE` | `false` | `FAIL` evidence |

For the vulnerable scenario, the test deliberately keeps the expected result at `ACCESS_DENIED`. The test is not weakened to accommodate the simulated insecure behavior.

### 8.2 TC-002 — Message Validation

TC-002 is supporting attack-surface coverage.

Implementation:

```text
03_src/security_lab/tc_002_message_validation.py
```

Dedicated tests:

```text
04_tests/test_tc002_message_validation.py
```

Scenarios:

| Test ID | Scenario | Expected |
| --- | --- | --- |
| TC-002-A | Invalid input | `INVALID_REQUEST` |
| TC-002-B | Unsupported operation | `UNSUPPORTED_OPERATION` |
| TC-002-C | `value=256` | `REQUEST_REJECTED` |
| TC-002-D | `BLOCKED` ECU state | `REQUEST_REJECTED` |

The dedicated suite also verifies valid parameter values `0` and `255`.

TC-002 does not establish the primary authorization finding.

### 8.3 TC-003 — Regression

TC-003 is implemented in:

```text
04_tests/test_security_regression.py
```

It uses the established TC-001 authorization property as the regression baseline.

The relationship is:

```text
TC-001
  ↓
Established security property
  ↓
TC-003
  ↓
Automated regression
```

TC-003 does not replace TC-001 as the original security-test definition.

---

## 9. Test Execution

### 9.1 Primary Vulnerable Execution

The primary execution condition is:

```text
SecurityMode = VULNERABLE
ECUState     = READY
Authorization = false
Request       = {"operation": "PROTECTED_OPERATION"}
```

The execution path is:

```text
TC-001
  ↓
SecurityTestCase
  ↓
SecurityTestRunner.run()
  ↓
ECUAdapter
  ↓
ECUSimulator.handle_request()
```

Inside `handle_request()`:

```text
1. Request is a mapping
2. Operation is a non-empty string
3. Operation is PROTECTED_OPERATION
4. Parameters default to an empty mapping
5. No invalid parameter value is present
6. ECU state is READY
7. SecurityMode is VULNERABLE
8. ACCESS_GRANTED is returned
```

The authorization state is `false`, but it is not reached as a granting condition because the vulnerable-mode branch returns first.

### 9.2 Test Result Evaluation

The `SecurityTestRunner` compares the actual ECU response status with the expected status.

For the vulnerable condition:

```text
Expected = ACCESS_DENIED
Actual   = ACCESS_GRANTED
```

Therefore:

```text
TestResult.passed = false
```

The security-test result is a failed security condition.

The surrounding lifecycle test can still pass as a pytest test because the test is intentionally verifying that the controlled vulnerable behavior is reproduced and correctly recognized as a failed security result.

These two concepts must not be confused:

```text
Security condition:
    FAIL

Lifecycle/pytest assertion:
    PASS
```

### 9.3 Secure Execution

The secure condition uses the same protected request:

```text
SecurityMode = SECURE
ECUState     = READY
Authorization = false
Request       = {"operation": "PROTECTED_OPERATION"}
```

The flow becomes:

```text
Request validation
      ↓
READY state
      ↓
VULNERABLE branch skipped
      ↓
Authorization = false
      ↓
ACCESS_DENIED
```

The expected and actual results are equal:

```text
Expected = ACCESS_DENIED
Actual   = ACCESS_DENIED
Result   = PASS
```

---

## 10. Evidence

### 10.1 Evidence Model

The Evidence Framework uses the fields:

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

The result semantics are:

```text
PASS → expected == actual
FAIL → expected != actual
```

Evidence validation checks required fields, preconditions, result type, timestamp validity, and expected/actual consistency.

The execution timestamp is generated at runtime as a timezone-aware UTC ISO-8601 timestamp.

### 10.2 Representative Vulnerable Evidence

The following is representative of the TC-001 vulnerable evidence structure. The timestamp shown is a placeholder because this document does not claim a new execution at documentation-generation time.

```json
{
  "test_id": "TC-001",
  "timestamp": "<generated at test execution>",
  "target": "simulated-ecu",
  "preconditions": {
    "authorization": false
  },
  "input": {
    "operation": "PROTECTED_OPERATION"
  },
  "expected": "ACCESS_DENIED",
  "actual": "ACCESS_GRANTED",
  "result": "FAIL",
  "notes": "Unauthorized protected operation was granted in the controlled vulnerable simulation."
}
```

This record expresses the security-relevant observation:

```text
Expected = ACCESS_DENIED
Actual   = ACCESS_GRANTED
Result   = FAIL
```

It does not by itself constitute a complete security finding. The finding adds impact, root cause, and remediation context.

### 10.3 Secure Retest Evidence

The corresponding secure retest has the same security condition but a different simulator security mode:

```json
{
  "test_id": "TC-003",
  "timestamp": "<generated at test execution>",
  "target": "simulated-ecu",
  "preconditions": {
    "authorization": false
  },
  "input": {
    "operation": "PROTECTED_OPERATION"
  },
  "expected": "ACCESS_DENIED",
  "actual": "ACCESS_DENIED",
  "result": "PASS",
  "notes": "Unauthorized protected operation was denied in the secure simulation."
}
```

The expected result remains unchanged between vulnerable execution and secure retest.

### 10.4 Evidence Lifecycle

The implemented evidence flow is:

```text
TestResult
    ↓
EvidenceGenerator
    ↓
Evidence
    ↓
validate()
    ↓
to_dict()
    ↓
to_json()
```

TC-003 verifies that regression evidence represents the executed retest result.

---

## 11. Security Finding

### 11.1 Finding ID

```text
SEC-001
```

### 11.2 Finding Statement

The controlled vulnerable ECU mode grants `PROTECTED_OPERATION` to an unauthorized requester.

The demonstrated condition is:

```text
Authorization = false
Operation     = PROTECTED_OPERATION
Mode          = VULNERABLE

Expected = ACCESS_DENIED
Actual   = ACCESS_GRANTED
```

This is a security-relevant deviation from the defined authorization requirement.

### 11.3 Finding Origin

The finding originates from TC-001.

It is not inferred solely from source-code inspection. The security-test behavior demonstrates the deviation through the target interface and produces an expected-versus-actual mismatch.

TC-002 does not create a second authorization finding. Its results represent deterministic validation behavior.

TC-003 provides regression coverage for the established TC-001 property.

### 11.4 Impact in the Simulation

Within the simulation, the impact is:

```text
An unauthorized requester can receive ACCESS_GRANTED
for the modeled protected operation.
```

No statement is made about impact on a real vehicle, ECU, diagnostic protocol, or production system.

### 11.5 Severity

A formal CVSS score is not claimed because the current project implementation does not establish a CVSS scoring workflow for this assessment case.

The finding is qualitatively security-relevant because it violates the modeled authorization requirement.

---

## 12. Vulnerability Assessment

### 12.1 Observed Behavior

Observed controlled behavior:

```text
authorization = false
PROTECTED_OPERATION
VULNERABLE mode

→ ACCESS_GRANTED
```

Expected secure behavior:

```text
authorization = false
PROTECTED_OPERATION
SECURE mode

→ ACCESS_DENIED
```

### 12.2 Assessment

The difference is deterministic and reproducible within the simulator.

The deviation is not caused by malformed input, unsupported operation handling, or parameter validation.

The TC-001 request contains:

```text
{"operation": "PROTECTED_OPERATION"}
```

There is no invalid parameter value to trigger `REQUEST_REJECTED`.

The ECU remains in the default `READY` state.

The security-relevant difference is therefore the security-mode-dependent authorization decision.

### 12.3 Verification Boundary

The assessment verifies:

```text
Implemented simulated ECU behavior
+
Implemented security-test execution
+
Structured evidence
+
Regression workflow
```

It does not verify:

```text
Real ECU behavior
Real vehicle behavior
Real diagnostic communication
Real-world exploitability
Production security
```

---

## 13. Root Cause Analysis

### 13.1 Direct Technical Cause

The direct cause is the order of the security decision branches in `ECUSimulator.handle_request()`.

After request validation and the `BLOCKED` state check, the implementation evaluates:

```text
SecurityMode.VULNERABLE
        ↓
ACCESS_GRANTED
```

before it evaluates:

```text
authorized
        ↓
ACCESS_GRANTED
```

or:

```text
not authorized
        ↓
ACCESS_DENIED
```

Therefore, when `VULNERABLE` is active, the authorization state is bypassed for the protected operation.

### 13.2 Control-Flow Root Cause

The relevant simplified control flow is:

```text
Validated PROTECTED_OPERATION
        ↓
ECU state BLOCKED?
        ├── Yes → REQUEST_REJECTED
        └── No
              ↓
SecurityMode.VULNERABLE?
              ├── Yes → ACCESS_GRANTED
              └── No
                    ↓
Authorization?
                    ├── Yes → ACCESS_GRANTED
                    └── No  → ACCESS_DENIED
```

The missing authorization enforcement is therefore not a request-validation problem.

It is a security-decision control-flow property of the intentionally vulnerable simulator branch.

### 13.3 Design Cause

The project deliberately provides two deterministic security modes:

```text
SECURE
VULNERABLE
```

The purpose of `VULNERABLE` is to reproduce a known security-relevant pre-fix condition so that TC-001 can demonstrate:

```text
Expected = ACCESS_DENIED
Actual   = ACCESS_GRANTED
```

The vulnerable behavior is consequently intentional within the simulation architecture.

### 13.4 Root Cause Classification

| Level | Root Cause |
| --- | --- |
| Observed behavior | Unauthorized protected operation receives `ACCESS_GRANTED` |
| Implementation behavior | `VULNERABLE` branch returns before authorization evaluation |
| Missing control in vulnerable state | Authorization is not enforced before grant |
| Design reason | Vulnerable mode intentionally models the pre-fix condition |
| Security relevance | Protected-operation authorization property is violated |

This distinction is important: the finding represents a controlled simulated security deviation, not an accidental claim about production ECU code.

---

## 14. Recommended Fix

### 14.1 Security Objective

The corrected security behavior must enforce authorization for the protected operation:

```text
authorization = false
+
PROTECTED_OPERATION
        ↓
ACCESS_DENIED
```

and preserve authorized functionality:

```text
authorization = true
+
PROTECTED_OPERATION
        ↓
ACCESS_GRANTED
```

### 14.2 Fix Principle

The security decision must not grant the protected operation solely because a vulnerable-mode condition is active.

For a production implementation, the authorization control would have to remain mandatory for protected operations.

Within the current simulation architecture, the secure state already represents this behavior.

### 14.3 Retest Requirement

The fix must be evaluated with the same unauthorized security condition.

The expected result must remain:

```text
ACCESS_DENIED
```

The test must not be changed to expect `ACCESS_GRANTED`.

---

## 15. Implemented Fix

### 15.1 Current Secure State

The current simulator already contains the secure behavior in `SecurityMode.SECURE`.

For:

```text
SecurityMode = SECURE
Authorization = false
Operation = PROTECTED_OPERATION
```

the vulnerable branch is skipped and the authorization check produces:

```text
ACCESS_DENIED
```

The controlled vulnerable mode remains available so that the original security deviation can still be reproduced.

### 15.2 Assessment Interpretation

For this end-to-end case, the lifecycle therefore uses:

```text
VULNERABLE
    ↓
reproduce deviation

SECURE
    ↓
represent corrected behavior

same security condition
    ↓
retest
```

No source-code modification is claimed as part of the creation of this documentation.

The distinction is intentional:

```text
Secure behavior exists in the supplied implementation.
A new code change is not claimed merely because the assessment documents the secure state.
```

### 15.3 Fix Verification Boundary

The supplied implementation supports verification that the secure mode denies unauthorized protected access.

It does not establish that a separate production codebase has been patched.

---

## 16. Retest

### 16.1 Retest Condition

The retest preserves the original security condition:

```text
Authorization = false
Operation     = PROTECTED_OPERATION
ECUState      = READY
SecurityMode  = SECURE
```

The request remains:

```json
{
  "operation": "PROTECTED_OPERATION"
}
```

### 16.2 Expected Retest Result

```text
Expected = ACCESS_DENIED
```

The documented TC-003 regression scenario verifies the secure condition as:

```text
Authorization: false
Operation:     PROTECTED_OPERATION
Expected:      ACCESS_DENIED
Actual:        ACCESS_DENIED
Result:        PASS
```

### 16.3 Authorized Retest

The positive authorization condition is also preserved:

```text
Authorization = true
Operation     = PROTECTED_OPERATION
Expected      = ACCESS_GRANTED
Actual        = ACCESS_GRANTED
Result        = PASS
```

This ensures that the security control does not simply block the protected operation for all users.

---

## 17. Regression Test

### 17.1 TC-003 Purpose

TC-003 protects the established TC-001 authorization property against regression.

Implementation:

```text
04_tests/test_security_regression.py
```

The regression workflow is:

```text
Controlled vulnerable behavior
        ↓
Original security condition
        ↓
Secure retest
        ↓
Expected vs. actual evaluation
        ↓
Structured evidence
        ↓
Evidence validation
        ↓
Authorized behavior verification
```

### 17.2 Automated Regression Scenarios

The regression evidence generator creates six scenario records:

| Scenario | Expected |
| --- | --- |
| Unauthorized protected operation | `ACCESS_DENIED` |
| Authorized protected operation | `ACCESS_GRANTED` |
| Invalid message | `INVALID_REQUEST` |
| Unsupported operation | `UNSUPPORTED_OPERATION` |
| `value=256` | `REQUEST_REJECTED` |
| Protected operation in `BLOCKED` state | `REQUEST_REJECTED` |

The automated regression test module contains seven tests in total, including the evidence-consistency verification.

### 17.3 Regression Property

The primary regression property is:

```text
Authorization = false
+
PROTECTED_OPERATION
+
SECURE mode
        ↓
ACCESS_DENIED
```

The authorized positive property is:

```text
Authorization = true
+
PROTECTED_OPERATION
+
SECURE mode
        ↓
ACCESS_GRANTED
```

### 17.4 No Duplicate Security-Test Implementation

TC-003 does not introduce a second independent implementation of the TC-001 security logic.

It reuses the established simulator, adapter, runner, test-case model, and evidence framework.

The distinction is:

```text
TC-001 → establishes the security property

TC-003 → automates regression verification of that property
```

---

## 18. Concrete End-to-End Regression Example

The following example shows one complete execution of the implemented regression property established by TC-001.

The example uses the unauthorized protected-operation condition in the secure simulator mode.

### 18.1 Regression Condition

The regression condition is:

```text
SecurityMode = SECURE
ECUState = READY
Authorization = false
Operation = PROTECTED_OPERATION
```

The security property under test is:

```text
Unauthorized protected operation
        |
        v
ACCESS_DENIED
```

The expected response remains unchanged from the original TC-001 security requirement.

### 18.2 Regression Input

The request submitted to the simulated ECU is:

```json
{
  "operation": "PROTECTED_OPERATION"
}
```

The request is executed through the established test architecture:

```text
SecurityTestCase
        |
        v
SecurityTestRunner
        |
        v
ECUAdapter
        |
        v
ECUSimulator
```

The regression test uses the same security-relevant condition that was established by the original security test.

### 18.3 Expected and Actual Result

The expected response is:

```text
ACCESS_DENIED
```

The secure simulated ECU returns:

```text
ACCESS_DENIED
```

The resulting comparison is:

```text
Expected = ACCESS_DENIED
Actual = ACCESS_DENIED
```

Therefore:

```text
Expected == Actual
        |
        v
TestResult.passed = true
        |
        v
Regression condition = PASS
```

The regression test confirms that the authorization property remains enforced under the tested condition.

### 18.4 Regression Evidence

The executed result is represented by structured evidence:

```json
{
  "test_id": "TC-003",
  "target": "simulated-ecu",
  "preconditions": {
    "authorization": false
  },
  "input": {
    "operation": "PROTECTED_OPERATION"
  },
  "expected": "ACCESS_DENIED",
  "actual": "ACCESS_DENIED",
  "result": "PASS",
  "notes": "Unauthorized protected operation was denied in the secure simulation."
}
```

The timestamp is generated by the Evidence Framework during test execution.

The evidence therefore connects the regression test condition with the actual execution result.

### 18.5 Automated Test Interpretation

The regression lifecycle distinguishes between the security condition being tested and the pytest result that verifies that condition.

For this secure regression scenario:

```text
Security condition:

Expected = ACCESS_DENIED
Actual = ACCESS_DENIED
Result = PASS
```

The corresponding automated test assertion verifies that the expected security behavior was observed.

This produces:

```text
Security condition = PASS
pytest assertion = PASS
```

This is different from the controlled vulnerable demonstration documented earlier, where the vulnerable security condition is intentionally represented as `FAIL` while the surrounding pytest test can still pass because it verifies that the deviation was correctly detected.

### 18.6 End-to-End Regression Chain

The complete example can therefore be summarized as:

```text
TC-001 Security Property
        |
        v
Unauthorized protected operation
        |
        v
Authorization = false
        |
        v
PROTECTED_OPERATION
        |
        v
TC-003 Regression Scenario
        |
        v
SecurityTestRunner
        |
        v
ECUAdapter
        |
        v
Secure ECUSimulator
        |
        v
ACCESS_DENIED
        |
        v
Expected == Actual
        |
        v
TestResult = PASS
        |
        v
EvidenceGenerator
        |
        v
Structured PASS Evidence
        |
        v
pytest Regression Test
        |
        v
CI/CD Execution
```

This example represents the current implemented regression path without introducing a separate regression architecture or a second implementation of the TC-001 security property.

---

## 19. Automated Test Results

### 19.1 Test Inventory

The current supplied project test inventory is:

| Test Module | Tests |
| --- | ---: |
| `test_ecu_simulator.py` | 6 |
| `test_evidence.py` | 14 |
| `test_foundation.py` | 1 |
| `test_security_regression.py` | 7 |
| `test_tc001_diagnostic_authorization.py` | 4 |
| `test_tc002_message_validation.py` | 5 |
| `test_test_runner.py` | 4 |
| **Total** | **41** |

### 19.2 Documented Execution Result

The supplied project documentation records:

```text
pytest -v

41 passed in 0.16s
```

The dedicated TC-003 regression suite is documented as:

```text
pytest .\04_tests\test_security_regression.py -v

7 passed in 0.06s
```

These are documented project results. They are not presented as a new execution performed while generating this document.

### 19.3 TC-001 Result Semantics

TC-001 intentionally contains a vulnerable scenario whose security condition is:

```text
Expected = ACCESS_DENIED
Actual   = ACCESS_GRANTED
```

The corresponding pytest test passes because it verifies that this controlled vulnerable behavior is correctly identified as a failed security result.

Therefore:

```text
pytest test outcome ≠ security result

pytest assertion: PASS
security condition: FAIL
```

This distinction is required for correct interpretation of the regression workflow.

### 19.4 TC-002 Result Semantics

The documented TC-002 dedicated execution is:

```text
pytest -q 04_tests/test_tc002_message_validation.py

5 passed
```

The suite covers invalid input, unsupported operation, out-of-range parameter behavior, blocked state, and valid boundary values.

---

## 20. CI/CD Execution

### 20.1 Workflow

The CI workflow is:

```text
.github/workflows/security-regression.yml
```

The implemented CI flow uses the existing automated regression logic.

Conceptually:

```text
GitHub Actions
      ↓
pytest
      ↓
Regression Evidence Generation
      ↓
JSON Evidence Files
      ↓
Artifact Upload
```

### 20.2 Evidence Artifact

The CI workflow uploads:

```text
security-regression-evidence
```

The evidence uses the same structured Evidence model as local execution.

The artifact upload is configured so that evidence is retained even when the test workflow fails in the controlled failure case.

### 20.3 Successful CI Execution

The supplied project documentation records a successful push-triggered execution on `main` for commit:

```text
78c943f
```

with workflow:

```text
Security Regression
```

and result:

```text
Success
```

The corresponding evidence artifact was:

```text
security-regression-evidence
```

This is project-documented CI evidence, not a new CI execution performed during creation of this document.

### 20.4 Controlled CI Failure

The project documentation also records a controlled failure:

```text
F......
1 failed
6 passed
exit code 1
```

The evidence artifact remained available because the artifact upload uses:

```text
if: always()
```

After restoration, the documented local regression result returned to:

```text
7 passed
```

### 20.5 CI Verification Boundary

The push-triggered workflow execution is documented.

A separate pull-request execution is not claimed as independently verified.

The Node.js 20 deprecation warning documented for GitHub Actions components did not prevent the recorded successful security-regression workflow. It is not a security-test result.

---

## 21. Conclusion

The Phase-11 end-to-end case demonstrates a complete security-testing lifecycle for one concrete security property of the simulated ECU.

The primary chain is:

```text
Protected diagnostic operation
        ↓
Authorization requirement
        ↓
Unauthorized attack condition
        ↓
TC-001
        ↓
Controlled vulnerable behavior
        ↓
Expected ACCESS_DENIED
Actual ACCESS_GRANTED
        ↓
Structured FAIL evidence
        ↓
SEC-001
        ↓
Root cause:
VULNERABLE branch grants before authorization
        ↓
Secure state
        ↓
Retest
        ↓
ACCESS_DENIED
        ↓
TC-003 regression
        ↓
Automated evidence
        ↓
CI/CD
```

The assessment establishes a reproducible and traceable relationship between security requirement, attack surface, test execution, evidence, finding, root cause, secure behavior, retest, regression, and CI/CD.

The conclusion is limited to the implemented simulation and documented project execution results. It does not constitute a real automotive ECU or vehicle security assessment.

---

## Section A — End-to-End Traceability

| Requirement / Property | Attack Surface | Test | Evidence | Finding | Fix / Secure State | Retest | Regression | CI/CD |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Protected operations require authorization | Authorization state / protected operation | TC-001 | TC-001 Evidence | SEC-001 | `SECURE` mode | TC-003 secure condition | TC-003 | Security Regression workflow |
| Unauthorized protected access denied | Authorization state | TC-001 | Expected vs. actual | SEC-001 | Authorization check | `ACCESS_DENIED` | TC-003 | Automated regression |
| Authorized protected access remains available | Authorization state | TC-001 | Expected vs. actual | Supporting condition | `ACCESS_GRANTED` | `ACCESS_GRANTED` | TC-003 | Automated regression |
| Invalid request rejected | Request structure | TC-002 | Structured evidence | None established | Existing validation | Same expected behavior | TC-003 coverage | Automated regression |
| Unsupported operation rejected | Operation selector | TC-002 | Structured evidence | None established | Existing validation | Same expected behavior | TC-003 coverage | Automated regression |
| Parameter range enforced | Parameter value | TC-002 | Structured evidence | None established | Existing validation | Same expected behavior | TC-003 coverage | Automated regression |
| Blocked state rejects operation | ECU state | TC-002 | Structured evidence | None established | Existing state control | Same expected behavior | TC-003 coverage | Automated regression |

##  Section B — Target / Actual Verification

| Requirement | Target | Actual | Verification Status |
| --- | --- | --- | --- |
| Protected operation requires authorization | Unauthorized access returns `ACCESS_DENIED` | `SECURE` mode returns `ACCESS_DENIED`; `VULNERABLE` mode intentionally reproduces the deviation | Verified at implementation/test-design level |
| Unauthorized vulnerable behavior is detectable | Expected `ACCESS_DENIED` must differ from actual insecure behavior | TC-001 produces `ACCESS_GRANTED` in `VULNERABLE` mode | Verified by supplied test implementation |
| Authorized access remains available | Authorized request returns `ACCESS_GRANTED` | `SECURE` mode returns `ACCESS_GRANTED` when authorized | Verified by supplied test implementation |
| Invalid requests are rejected | Invalid structure returns `INVALID_REQUEST` | Implemented and covered by TC-002 | Verified by supplied test documentation |
| Unsupported operations are rejected | Unsupported operation returns `UNSUPPORTED_OPERATION` | Implemented and covered by TC-002 | Verified by supplied test documentation |
| Invalid parameter values are rejected | Values outside `0..255` are rejected | Implemented and covered by TC-002 / TC-003 | Verified by supplied test documentation |
| Blocked ECU rejects operation | Protected operation is rejected in `BLOCKED` state | Returns `REQUEST_REJECTED` | Verified by supplied test implementation |
| Evidence is structured | Evidence contains defined fields and validates expected/actual consistency | Implemented in `evidence.py` and exercised by tests | Verified by supplied test implementation |
| Regression reuses established security property | TC-003 protects TC-001 property | TC-003 uses the established authorization condition | Verified by supplied test implementation |
| CI publishes regression evidence | Regression execution produces evidence artifact | `security-regression-evidence` documented | Verified by supplied CI documentation |
| Real automotive security is not claimed | Simulation must remain clearly bounded | Scope explicitly excludes real vehicles/ECUs/OEM systems | Verified by document scope |

##  Section C — Quality Gate

| Quality Criterion | Status |
| --- | --- |
| All 20 required assessment sections present | PASS |
| TC-001 explicitly forms the primary finding path | PASS |
| TC-002 used as supporting validation coverage | PASS |
| TC-003 used as regression layer | PASS |
| Attack surface linked to implemented behavior | PASS |
| Root cause tied to actual control flow | PASS |
| No invented CVSS score | PASS |
| Evidence follows project Evidence model | PASS |
| No fabricated current execution | PASS |
| CI claims limited to documented execution | PASS |
| Real automotive claims excluded | PASS |
| No separate customer report introduced | PASS |
| No Phase-12 work introduced | PASS |
| Repository file/commit status falsely claimed | PASS |
| Repository-level Phase-11 completion | NOT VERIFIED |

## Section D — Phase Status

The document content for Phase 11 has been prepared.

The repository-level Phase-11 Definition of Done requires, in addition to the document content:

```text
docs/04_end-to-end-assessment-case.md exists
PROJECT_STATUS.md reflects Phase 11 completion
SOLL/IST verification is completed against the repository state
```

This generated document does not claim that those repository changes have been made.

Accordingly:

```text
Phase Status:
INCOMPLETE at repository level

Verification Status:
PARTIALLY VERIFIED
```

##  Section E — Proposed Git Commit Message

```text
docs: add phase 11 end-to-end security assessment case
```

---

## Verification Summary

The end-to-end assessment case is technically aligned with the supplied implementation and project documentation.

The central security finding is derived from the actual modeled TC-001 behavior:

```text
VULNERABLE + unauthorized + PROTECTED_OPERATION
→ ACCESS_GRANTED
```

The secure retest condition is:

```text
SECURE + unauthorized + PROTECTED_OPERATION
→ ACCESS_DENIED
```

TC-002 provides deterministic message-validation coverage.

TC-003 provides automated regression coverage and structured evidence.

The documented automated test inventory is 41 tests, with the supplied project documentation recording successful execution.

The remaining repository-level verification is intentionally not represented as completed because creation of this standalone document does not itself modify or verify the Git repository's `PROJECT_STATUS.md` or commit state.
