# Attack Surface

## Purpose

This document defines the modeled attack surface for the Automotive Security Regression Lab.

The attack surface is intentionally limited to the interfaces and security-relevant behavior represented by the local ECU simulation and its security-test architecture. It provides the threat-model basis for the end-to-end assessment case and connects the modeled attack surface to TC-001, TC-002, and TC-003.

The document does not describe a real vehicle, real ECU, real diagnostic network, CAN bus, UDS communication, OEM infrastructure, or production environment.

---

## Scope and Security Boundary

The Automotive Security Regression Lab uses a fully simulated ECU.

The relevant security boundary is:

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
```

The modeled attack surface therefore exists at the simulated target interface represented by `ECUTarget` / `ECUAdapter` and the request-processing behavior of `ECUSimulator`.

Out of scope:

- real vehicle communication
- real ECU communication
- real CAN communication
- real UDS communication
- vehicle-network interaction
- OEM infrastructure
- customer data
- production credentials
- production systems
- unauthorized security testing
- physical ECU interfaces
- real diagnostic transport protocols

The vulnerable ECU mode is a controlled simulation state used to reproduce a defined security-relevant deviation. It must not be interpreted as evidence of a vulnerability in a real vehicle or ECU.

---

## Modeled Target

The modeled target is the simulated ECU implemented by:

```text
03_src/security_lab/ecu_simulator.py
```

The simulator exposes a request-processing interface through:

```text
handle_request(request)
```

The modeled operation relevant to the security assessment is:

```text
PROTECTED_OPERATION
```

The simulator returns a structured `ECUResponse` containing:

```text
status
operation
```

Relevant response statuses are:

```text
ACCESS_GRANTED
ACCESS_DENIED
INVALID_REQUEST
UNSUPPORTED_OPERATION
REQUEST_REJECTED
```

---

## Attack Surface Overview

The current modeled attack surface consists of the following security-relevant input and control dimensions:

| Attack Surface Element | Modeled Input / State | Security Relevance | Covered By |
| --- | --- | --- | --- |
| Request structure | Mapping / non-mapping input | Determines whether request processing can start | TC-002 |
| Operation selector | `PROTECTED_OPERATION` / unsupported / missing | Determines which operation is requested | TC-001, TC-002 |
| Parameter structure | Mapping / non-mapping | Controls validity of optional parameters | TC-002 |
| Parameter value | Integer range `0..255` | Tests deterministic boundary and rejection behavior | TC-002, TC-003 |
| Authorization state | `true` / `false` | Determines whether protected access is permitted | TC-001, TC-003 |
| ECU operational state | `READY` / `BLOCKED` | Restricts operation execution | TC-002, TC-003 |
| ECU security mode | `SECURE` / `VULNERABLE` | Controls the intentionally modeled pre-fix and secure lifecycle states | TC-001, TC-003 |

---

## Request Entry Point

The primary modeled entry point is:

```text
ECUSimulator.handle_request(request)
```

The request is processed through deterministic validation and security checks.

The relevant processing sequence is:

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
Security mode / authorization decision
```

This sequence is important for the end-to-end assessment because a security-relevant result must be interpreted in the context of the actual control flow.

---

## Protected Operation

`PROTECTED_OPERATION` is the central security-relevant operation in the current assessment.

The security property established by TC-001 is:

```text
Unauthorized protected operation
        ↓
ACCESS_DENIED
```

The authorized positive condition is:

```text
Authorized protected operation
        ↓
ACCESS_GRANTED
```

The controlled vulnerable condition is:

```text
Unauthorized protected operation
        ↓
ACCESS_GRANTED
```

The last condition is the security-relevant deviation used to demonstrate the finding and subsequent regression workflow.

---

## Authorization Attack Surface

Authorization is represented by the simulator state:

```text
authorized = false
authorized = true
```

The security boundary is the decision whether `PROTECTED_OPERATION` may be granted.

Expected secure behavior:

```text
authorization = false
+
PROTECTED_OPERATION
        ↓
ACCESS_DENIED
```

and:

```text
authorization = true
+
PROTECTED_OPERATION
        ↓
ACCESS_GRANTED
```

TC-001 explicitly tests both conditions and additionally exercises the controlled vulnerable mode.

The unauthorized vulnerable condition is therefore not an assumed finding. It is a modeled attack condition that produces a directly observable expected-versus-actual deviation.

---

## Security Mode Attack Surface

The simulator supports two explicit security modes:

```text
SECURE
VULNERABLE
```

`VULNERABLE` is a deliberate simulation mechanism for reproducing the pre-fix security behavior.

In the vulnerable branch, the simulator grants `PROTECTED_OPERATION` before the authorization state is enforced.

Conceptually, the relevant control flow is:

```text
Protected operation accepted
        ↓
SecurityMode.VULNERABLE?
        ├── Yes → ACCESS_GRANTED
        └── No
              ↓
Authorization valid?
              ├── Yes → ACCESS_GRANTED
              └── No  → ACCESS_DENIED
```

This control-flow ordering is the direct technical basis for the TC-001 vulnerable result.

The `VULNERABLE` mode is therefore part of the modeled attack surface for lifecycle testing, but it is not a claim that an equivalent defect exists in a real ECU.

---

## Message-Validation Attack Surface

TC-002 extends the attack surface model to request and parameter validation.

The implemented validation semantics are:

| Condition | Response |
| --- | --- |
| Request is not a mapping | `INVALID_REQUEST` |
| Operation is missing or empty | `INVALID_REQUEST` |
| Operation is unsupported | `UNSUPPORTED_OPERATION` |
| Parameters are not a mapping | `INVALID_REQUEST` |
| Parameter value outside `0..255` | `REQUEST_REJECTED` |
| Parameter value is boolean | `REQUEST_REJECTED` |
| ECU is `BLOCKED` | `REQUEST_REJECTED` |

Valid numeric boundary values are:

```text
0
255
```

Out-of-range examples are:

```text
-1
256
```

The intended classification is:

```text
-1    → REQUEST_REJECTED
0     → accepted
255   → accepted
256   → REQUEST_REJECTED
```

Boolean values are explicitly rejected even though Python treats `bool` as a subclass of `int`.

These validation controls are part of the attack surface because malformed, unsupported, or invalid requests must not be allowed to bypass the intended request-processing constraints.

---

## ECU State Attack Surface

The simulator models two ECU operational states:

```text
READY
BLOCKED
```

A protected operation issued while the ECU is `BLOCKED` is rejected:

```text
ECU state = BLOCKED
+
PROTECTED_OPERATION
        ↓
REQUEST_REJECTED
```

The state check occurs before the security-mode branch.

Therefore, within the current implementation, `BLOCKED` also prevents the controlled vulnerable-mode grant for the tested request condition.

This distinction is relevant to the assessment because authorization behavior and ECU-state restrictions are separate controls.

---

## Attack Surface by Test Case

### TC-001 — Diagnostic Authorization

TC-001 addresses the primary security boundary:

```text
Unauthorized requester
        ↓
PROTECTED_OPERATION
        ↓
Authorization enforcement
        ↓
Expected: ACCESS_DENIED
```

The four dedicated TC-001 tests cover:

| Scenario | Mode | Authorization | Expected / Observed Behavior |
| --- | --- | --- | --- |
| Unauthorized secure | `SECURE` | `false` | `ACCESS_DENIED` |
| Authorized secure | `SECURE` | `true` | `ACCESS_GRANTED` |
| Unauthorized vulnerable | `VULNERABLE` | `false` | Expected `ACCESS_DENIED`, actual `ACCESS_GRANTED` |
| Vulnerable evidence | `VULNERABLE` | `false` | Machine-readable `FAIL` evidence |

TC-001 is the primary source of the security finding used by the end-to-end case.

### TC-002 — Message Validation

TC-002 addresses the request-validation portion of the attack surface:

| Scenario | Input / State | Expected |
| --- | --- | --- |
| TC-002-A | Invalid input | `INVALID_REQUEST` |
| TC-002-B | Unsupported operation | `UNSUPPORTED_OPERATION` |
| TC-002-C | `value=256` | `REQUEST_REJECTED` |
| TC-002-D | `BLOCKED` ECU state | `REQUEST_REJECTED` |

The dedicated test suite also verifies that valid boundary values `0` and `255` are accepted for the protected operation.

TC-002 does not establish the authorization finding. Its purpose is to verify deterministic message and state validation.

### TC-003 — Regression Workflow

TC-003 uses the established diagnostic-authorization security property as its regression baseline.

The regression lifecycle is:

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

The automated regression module additionally covers invalid requests, unsupported operations, an out-of-range parameter, and the blocked ECU state.

The relationship is:

```text
TC-001
  ↓
Security property
  ↓
TC-003
  ↓
Regression verification
```

TC-003 does not replace TC-001 as the original security-test definition.

---

## Primary Threat Actor

The modeled threat actor is:

```text
Unauthorized diagnostic client
```

This is a logical test actor inside the simulation.

No real diagnostic client or vehicle communication is involved.

The relevant threat condition is:

```text
Authorization = false
+
Request = PROTECTED_OPERATION
```

---

## Attack Hypothesis

The primary attack hypothesis is:

> If authorization is missing or incorrectly enforced, an unauthorized diagnostic requester may be able to execute a protected operation.

The hypothesis is tested through the controlled simulator condition:

```text
authorization = false
PROTECTED_OPERATION
```

Expected secure result:

```text
ACCESS_DENIED
```

Controlled vulnerable result:

```text
ACCESS_GRANTED
```

This expected-versus-actual difference provides the basis for the security finding documented later in the end-to-end assessment.

---

## Security-Relevant Trust Boundary

The principal modeled trust boundary is between the security-test layer and the simulated ECU target:

```text
Security Test / Test Runner
          │
          │ request
          ▼
      ECUAdapter
          │
          │ target interface
          ▼
     ECUSimulator
          │
          │ ECUResponse
          ▼
 Security Test / Evidence
```

The test architecture deliberately separates:

- security-test definition
- test execution
- target adaptation
- ECU behavior
- result evaluation
- evidence generation

The security test therefore does not directly modify the simulator's internal result.

---

## Attack Surface and Evidence Flow

The modeled attack surface connects directly to the evidence workflow:

```text
Attack Surface
      ↓
Attack Hypothesis
      ↓
Security Test
      ↓
ECUSimulator
      ↓
ECUResponse
      ↓
TestResult
      ↓
Evidence
      ↓
Security Finding
```

For the primary TC-001 deviation:

```text
Authorization = false
+
PROTECTED_OPERATION
+
VULNERABLE mode
        ↓
ECUSimulator
        ↓
ACCESS_GRANTED
        ↓
Expected = ACCESS_DENIED
Actual   = ACCESS_GRANTED
        ↓
Result = FAIL
        ↓
SEC-001
```

The evidence result is derived from expected-versus-actual comparison and is validated by the Evidence Framework.

---

## Attack Surface Assessment

The current modeled attack surface supports the following assessment statements:

| Area | Assessment |
| --- | --- |
| Protected-operation authorization | Security-relevant deviation is reproducible in controlled `VULNERABLE` mode |
| Secure unauthorized access | Denied in `SECURE` mode |
| Secure authorized access | Granted in `SECURE` mode |
| Request structure validation | Deterministic |
| Unsupported operation handling | Deterministic |
| Parameter range validation | Deterministic |
| Boolean parameter handling | Explicitly rejected |
| Blocked ECU state | Protected operation rejected |
| Evidence generation | Structured and machine-readable |
| Regression baseline | Established from TC-001 |
| Real automotive interfaces | Out of scope |

---

## Traceability

| Attack Surface Element | Requirement / Property | Test | Evidence / Finding | Regression |
| --- | --- | --- | --- | --- |
| Protected operation | Authorization required | TC-001 | SEC-001 | TC-003 |
| Authorization state | Unauthorized access denied | TC-001 | SEC-001 | TC-003 |
| Security mode | Controlled vulnerable / secure lifecycle | TC-001 | SEC-001 | TC-003 |
| Request structure | Malformed input rejected | TC-002 | TC-002 evidence | TC-003 coverage |
| Operation selector | Unsupported operation rejected | TC-002 | TC-002 evidence | TC-003 coverage |
| Parameter value | Valid range enforced | TC-002 | TC-002 evidence | TC-003 coverage |
| ECU state | Blocked state rejects operation | TC-002 | TC-002 evidence | TC-003 coverage |

---

## Limitations

This attack-surface model is intentionally narrow.

It does not establish coverage of:

- CAN frames
- UDS services
- diagnostic sessions
- transport protocols
- authentication protocols
- cryptographic mechanisms
- key management
- secure boot
- firmware update mechanisms
- vehicle-network routing
- gateway behavior
- ECU hardware interfaces
- physical attacks
- real-world exploitability
- production-system security

The current attack surface therefore represents the implemented simulation and its defined security-test scenarios, not a complete automotive ECU attack-surface analysis.

---

## Evidence Classification

The following classification applies to statements in this document:

| Statement Type | Classification |
| --- | --- |
| Implemented simulator behavior | `[SOURCE]` |
| Defined project requirement | `[MASTER]` / `[STANDARD]` where applicable |
| Directly documented test behavior | `[FACT]` |
| Interpretation of behavior for threat modeling | `[INFERENCE]` |
| Deliberate simulation design choice | `[DESIGN]` |
| Unverified execution claim | `[UNVERIFIED]` |

No real-vehicle security claim is derived from this attack-surface model.

---

## Relationship to the End-to-End Assessment Case

This document provides the attack-surface foundation for:

```text
Security Requirement
        ↓
Threat Model
        ↓
Attack Surface
        ↓
Attack Hypothesis
        ↓
TC-001 / TC-002
        ↓
Evidence
        ↓
Security Finding
        ↓
Root Cause
        ↓
Fix
        ↓
Retest
        ↓
TC-003 Regression
        ↓
CI/CD
```

For the Phase-11 end-to-end assessment, the primary path is the TC-001 authorization scenario.

TC-002 provides supporting validation coverage and demonstrates that message-validation behavior is deterministic.

TC-003 provides the regression layer for the established TC-001 security property.

---

## Verification Status

**Document status:** Phase 11 End-to-End Assessment.

**Repository status:** This document content has been prepared from the currently supplied project sources.

**Technical boundary:** The document describes the currently modeled attack surface supported by the supplied simulator, test cases, regression tests, and project architecture.
