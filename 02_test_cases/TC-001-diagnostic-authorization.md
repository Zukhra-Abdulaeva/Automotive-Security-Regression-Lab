# TC-001 — Diagnostic Authorization

## 1. Scenario

A diagnostic requester attempts to execute a protected diagnostic operation.

The simulated ECU provides an authorization state that determines whether the protected operation may be executed.

TC-001 verifies that authorization is enforced before execution of the protected operation.

Two secure scenarios are tested:

* unauthorized access
* authorized access

The controlled vulnerable ECU variant is additionally used to reproduce the security-relevant deviation in a deterministic local simulation.

The resulting security property is subsequently used as the basis for automated regression coverage.

This test case represents a simulated automotive security concept and does not implement real UDS, CAN communication, a real ECU, or a real vehicle.

---

## 2. Objective

The objective of TC-001 is to verify the following security requirement:

> Protected diagnostic operations shall require authorization.

The test verifies that:

* an unauthorized requester cannot execute the protected operation
* an authorized requester can execute the protected operation
* the controlled vulnerable ECU can reproduce the security-relevant deviation where an unauthorized requester is incorrectly granted access

The test therefore evaluates a security property rather than only normal functional behavior.

The security property established by TC-001 is also used as a regression baseline after the simulated security behavior has been corrected.

---

## 3. Scope

TC-001 is limited to the authorization behavior of the simulated ECU for the protected operation:

```text
PROTECTED_OPERATION
```

In scope:

* authorization state
* protected operation
* authorization enforcement
* secure ECU behavior
* controlled vulnerable ECU behavior
* expected versus actual behavior
* security-test evidence
* retest after the simulated fix
* regression coverage of the established authorization property

Out of scope:

* real vehicle communication
* real ECU communication
* real CAN communication
* real UDS implementation
* external systems
* customer data
* productive systems
* complete security finding management
* CVSS calculation
* generalized vulnerability-management workflows

---

## 4. Information Gathering

The following information is required to execute TC-001.

### Protected operation

The simulated ECU exposes the protected operation:

```text
PROTECTED_OPERATION
```

### Authorization state

The simulated ECU maintains an authorization state represented by:

```text
authorization = false
authorization = true
```

### Security requirement

Protected diagnostic operations shall require authorization.

### Expected unauthorized response

An unauthorized request for the protected operation shall result in:

```text
ACCESS_DENIED
```

### Expected authorized response

An authorized request for the protected operation shall result in:

```text
ACCESS_GRANTED
```

The information used by this test is derived exclusively from the controlled simulation.

No external target or real automotive system is required.

---

## 5. Threat Model

### Asset

Protected Diagnostic Operation

### Threat

Unauthorized execution of a protected diagnostic operation.

### Potential attacker

Unauthorized diagnostic client.

### Security property

Authorization must be enforced before execution of the protected operation.

### Security assumption

The simulated ECU is responsible for enforcing the authorization requirement for the protected operation.

The threat model is intentionally limited to the behavior represented by the simulation.

---

## 6. Attack Surface

The modeled diagnostic attack surface is:

```text
Diagnostic Interface
        |
        v
Protected Operation
        |
        v
Authorization Check
        |
        v
Response
```

The interface represents a simulated test surface.

No real CAN, UDS, vehicle network, ECU, or external diagnostic endpoint is used.

---

## 7. Attack Hypothesis

If the authorization check is missing or incorrectly enforced, an unauthorized diagnostic requester may be able to execute a protected operation.

TC-001 tests this hypothesis by submitting the protected operation with authorization disabled.

The same operation is also tested with authorization enabled to verify the intended positive behavior.

---

## 8. Test Setup

The test uses the existing security-test architecture:

```text
TC-001
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

The test does not directly manipulate internal ECU implementation details.

The ECU remains the system under test.

The Security Test Runner is responsible for executing the security-test logic.

The Evidence Framework is responsible for representing the resulting test observation.

The established security property can also be exercised by the project's automated regression coverage.

---

## 9. Preconditions

### Scenario A — Unauthorized Access

```text
authorization = false
```

The protected operation is available as:

```text
PROTECTED_OPERATION
```

Expected response:

```text
ACCESS_DENIED
```

### Scenario B — Authorized Access

```text
authorization = true
```

The protected operation is available as:

```text
PROTECTED_OPERATION
```

Expected response:

```text
ACCESS_GRANTED
```

### Vulnerable Demonstration

The controlled vulnerable ECU is configured so that:

```text
authorization = false
PROTECTED_OPERATION
```

produces:

```text
ACCESS_GRANTED
```

This behavior is intentionally simulated for security-test demonstration.

---

## 10. Test Execution

### Test A — Unauthorized Access

Input:

```text
authorization = false
PROTECTED_OPERATION
```

Expected behavior:

```text
ACCESS_DENIED
```

The actual ECU response is compared against the expected response.

If the secure ECU returns:

```text
ACCESS_DENIED
```

the test observation is:

```text
PASS
```

because:

```text
Expected == Actual
```

### Test B — Authorized Access

Input:

```text
authorization = true
PROTECTED_OPERATION
```

Expected behavior:

```text
ACCESS_GRANTED
```

If the secure ECU returns:

```text
ACCESS_GRANTED
```

the test observation is:

```text
PASS
```

because:

```text
Expected == Actual
```

### Vulnerable Behavior Demonstration

The controlled vulnerable ECU is executed with:

```text
authorization = false
PROTECTED_OPERATION
```

Expected:

```text
ACCESS_DENIED
```

Observed:

```text
ACCESS_GRANTED
```

Therefore:

```text
Expected != Actual
```

and the resulting Evidence is:

```text
FAIL
```

This `FAIL` represents a mismatch between the required security behavior and the observed simulated behavior.

---

## 11. Expected Behavior

The secure ECU shall enforce authorization before execution of the protected operation.

Expected behavior:

| Authorization | Operation             | Expected Response |
| ------------- | --------------------- | ----------------- |
| `false`       | `PROTECTED_OPERATION` | `ACCESS_DENIED`   |
| `true`        | `PROTECTED_OPERATION` | `ACCESS_GRANTED`  |

The security property is therefore:

```text
Unauthorized
    |
    v
ACCESS_DENIED
```

and:

```text
Authorized
    |
    v
ACCESS_GRANTED
```

---

## 12. Actual Behavior

### Secure ECU

For:

```text
authorization = false
PROTECTED_OPERATION
```

the secure ECU produces:

```text
ACCESS_DENIED
```

For:

```text
authorization = true
PROTECTED_OPERATION
```

the secure ECU produces:

```text
ACCESS_GRANTED
```

### Vulnerable ECU

The controlled vulnerable ECU intentionally produces:

```text
authorization = false
PROTECTED_OPERATION
        |
        v
ACCESS_GRANTED
```

This is the security-relevant deviation reproduced by TC-001.

The actual execution results are taken from the test execution rather than hard-coded into the test case documentation.

---

## 13. Evidence

TC-001 uses the Evidence Framework established for the project.

A vulnerable execution is represented conceptually as:

```json
{
  "test_id": "TC-001",
  "target": "simulated-ecu",
  "preconditions": {
    "authorization": false
  },
  "input": "PROTECTED_OPERATION",
  "expected": "ACCESS_DENIED",
  "actual": "ACCESS_GRANTED",
  "result": "FAIL",
  "notes": "Protected operation was accepted without authorization."
}
```

The timestamp is generated by the existing Evidence Framework at execution time.

Evidence documents the test observation.

It does not by itself constitute a formal security finding.

The established evidence model is also reused for automated regression execution.

---

## 14. Vulnerability Assessment

If the vulnerable ECU produces:

```text
ACCESS_GRANTED
```

for:

```text
authorization = false
PROTECTED_OPERATION
```

the observed behavior violates the security requirement:

> Protected diagnostic operations shall require authorization.

The security-relevant observation is therefore:

```text
Unauthorized request
        |
        v
Protected operation accepted
        |
        v
Security requirement violated
```

No CVSS score or formal severity classification is assigned in TC-001.

Formal Security Finding Management is represented separately from the test-case execution and evidence model.

---

## 15. Root Cause

For the controlled vulnerable simulation, the root cause is:

The authorization state is not enforced before execution of the protected operation.

This statement is limited to the behavior represented by the simulated ECU.

It does not make claims about real automotive systems or real ECU implementations.

---

## 16. Recommendation

The modeled security behavior should enforce authorization before executing protected diagnostic operations.

Recommendation:

Enforce authorization before executing protected diagnostic operations.

The authorization decision must occur before the protected operation is granted.

---

## 17. Fix

The secure variant of the simulated ECU enforces the authorization requirement.

Required behavior:

### Unauthorized

```text
authorization = false
PROTECTED_OPERATION
        |
        v
ACCESS_DENIED
```

### Authorized

```text
authorization = true
PROTECTED_OPERATION
        |
        v
ACCESS_GRANTED
```

The fix is implemented in the simulated ECU behavior rather than by modifying the expected result of the security test.

The Security Test Runner and Evidence Framework remain responsible for test execution and evidence representation respectively.

---

## 18. Retest

After the simulated fix, TC-001 is executed again.

The same security test case is used.

The retest does not replace the original security test with a new test that only produces the desired result.

Retest flow:

```text
Vulnerable Behavior
        |
        v
Evidence
        |
        v
Fix
        |
        v
Same TC-001
        |
        v
Retest
        |
        v
Expected Secure Behavior
```

The expected retest results are:

```text
authorization = false
PROTECTED_OPERATION
        |
        v
ACCESS_DENIED
```

and:

```text
authorization = true
PROTECTED_OPERATION
        |
        v
ACCESS_GRANTED
```

Both secure scenarios must therefore produce matching expected and actual results.

The resulting secure behavior forms the regression baseline for the authorization property.

---

## 19. Regression Test

The security property established by TC-001 is covered by the project's regression testing.

The essential security property is:

```text
Protected operation + unauthorized
        |
        v
must result in ACCESS_DENIED
```

and:

```text
Protected operation + authorized
        |
        v
must result in ACCESS_GRANTED
```

The regression test executes the security property through the existing test architecture and evaluates the resulting behavior against the defined expected response.

The regression execution produces a `TestResult` and corresponding structured evidence.

The regression coverage therefore verifies that the authorization behavior remains enforced after subsequent changes.

The regression workflow does not require a separate ECU, target abstraction, or evidence model.

---

## Historical Phase 5 Boundary

The following boundary describes the original scope of TC-001 when the test case was introduced:

```text
TC-001
    |
    +-- diagnostic authorization
    +-- vulnerable behavior reproduction
    +-- secure behavior
    +-- retest
    +-- security-test evidence
```

At that time, the complete regression suite and CI/CD pipeline were outside the scope of TC-001.

The project has since extended the established test and evidence architecture with automated regression coverage and CI/CD execution.

The historical Phase 5 boundary is retained to document the development history. It does not describe the current overall repository capability.

TC-001 remains a controlled automotive security simulation and does not represent:

```text
a real penetration test
a real ECU assessment
a real vehicle test
a real UDS implementation
a complete vulnerability-management process
```

The vulnerable behavior exists only to provide a deterministic security-test observation.

Evidence documents the observation; formal Security Finding Management remains a separate concern.
