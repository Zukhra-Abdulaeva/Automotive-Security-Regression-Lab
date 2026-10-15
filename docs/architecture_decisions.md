# Architecture Decisions

This document records the architecture decisions for the Automotive Security Regression Lab.

The decisions documented here describe intentional architecture constraints, design choices, and implementation boundaries.

Accepted architecture decisions remain consistent with the project masterprompt and provide the architectural basis for subsequent implementation and documentation.

---

## ADR-001 — ECU fully simulated

**Status:** Accepted
**Phase:** 1
**Source:** [MASTER]

### Decision

The ECU used by the Automotive Security Regression Lab is fully simulated.

The project does not communicate with a real ECU or a productive automotive system.

### Rationale

A fully simulated ECU provides a controlled, deterministic, reproducible and safe environment for security testing.

### Consequences

* ECU behavior can be executed locally and reproduced under controlled conditions.
* Security-test concepts can be demonstrated without access to real automotive systems.
* Test results and findings describe the behavior of the simulation.
* Simulation results are not evidence of behavior in a real vehicle or productive ECU.

---

## ADR-002 — Security tests are reproducible and automatable

**Status:** Accepted
**Phase:** 1
**Source:** [MASTER]

### Decision

Security tests shall be reproducible and automatable.

The test architecture provides repeatable execution, deterministic behavior, structured results and machine-readable information.

### Rationale

Reproducibility provides a stable basis for security verification and later automated execution.

### Consequences

* Tests can be executed repeatedly under the same defined conditions.
* Test results can be evaluated programmatically.
* Structured results provide a stable basis for evidence generation.
* The test architecture can be used as a foundation for later CI/CD execution.

---

## ADR-003 — No real vehicles or productive systems

**Status:** Accepted
**Phase:** 1
**Source:** [MASTER]

### Decision

The project does not use real vehicles, real ECUs, OEM systems, customer systems, production environments or production data.

### Rationale

The Automotive Security Regression Lab is designed as a controlled laboratory and portfolio environment.

### Consequences

* Security behavior is represented within the simulated test environment.
* No productive automotive infrastructure is required for test execution.
* Test execution can be performed locally without access to customer or production systems.

---

## ADR-004 — Test logic separated from ECU implementation

**Status:** Accepted
**Phase:** 1
**Source:** [MASTER]

### Decision

Security-test logic and ECU implementation are separated.

Security tests communicate with the ECU through the ECU target abstraction and adapter boundary. The ECU models the target behavior, while the test architecture controls test execution and evaluation.

### Rationale

The separation keeps the system under test independent from the security-test implementation.

### Consequences

* ECU behavior can be tested through a defined interface.
* Test execution and security evaluation remain outside the ECU implementation.
* The target implementation can be replaced or extended without moving security-test logic into the ECU model.

---

## ADR-005 — Phase 1 minimal Python/pytest foundation

**Status:** Accepted
**Phase:** 1
**Source:** [MASTER]+[SOURCE]

### Decision

The initial test architecture uses Python and pytest as its implementation and test foundation.

The project uses the Python standard library and pytest where appropriate and avoids unnecessary runtime dependencies.

### Rationale

A small dependency footprint supports maintainability, deterministic local execution and straightforward reproduction of the test environment.

### Consequences

* The implementation remains lightweight.
* Local execution requires only the dependencies justified by the test architecture.
* Additional dependencies require a corresponding technical justification.

---

## ADR-006 — ECU security behavior is deterministic and mode-controlled

**Status:** Accepted
**Phase:** 2
**Source:** [MASTER]

### Decision

The ECU simulator provides explicit security modes:

```text
SECURE
VULNERABLE
```

In `SECURE` mode, protected operation requires authorization.

In `VULNERABLE` mode, the same protected operation is intentionally accessible without authorization.

### Rationale

Explicit security modes provide deterministic control over the security-relevant behavior required by the test scenarios.

### Consequences

* Secure behavior can be tested independently.
* Vulnerable behavior can be reproduced in a controlled manner.
* `VULNERABLE` mode is a simulation mechanism for reproducing the defined security deviation.

---

## ADR-007 — ECU responses use a structured deterministic model

**Status:** Accepted
**Phase:** 2
**Source:** [MASTER]

### Decision

ECU responses are represented by the `ECUResponse` model.

The response provides deterministic status and operation information and supports serialization through `to_dict()`.

### Rationale

A structured response model provides a stable interface between ECU behavior and the test architecture.

### Consequences

* Response values are explicit and machine-readable.
* Response information can be used for result evaluation and evidence generation.
* Serialization provides a deterministic representation for downstream processing.

---

## ADR-008 — Requests are validated before security processing

**Status:** Accepted
**Phase:** 2
**Source:** [MASTER]

### Decision

Requests are validated before security processing.

Validation distinguishes malformed requests, unsupported operations and rejected parameters.

The defined validation semantics are:

```text
Malformed request structure → INVALID_REQUEST
Missing or invalid operation → INVALID_REQUEST
Valid but unsupported operation → UNSUPPORTED_OPERATION
Invalid parameter structure → INVALID_REQUEST
Parameter outside 0..255 → REQUEST_REJECTED
```

### Rationale

Explicit validation categories provide deterministic request handling and distinguish input-format errors from unsupported operations and rejected parameter values.

### Consequences

* Invalid request structures are handled before security processing.
* Unsupported operations have a distinct result.
* Parameter rejection is represented separately from malformed input.
* The validation semantics provide a stable basis for security-test scenarios.

---

## ADR-009 — Security-test evidence uses a structured data model

**Status:** Accepted
**Phase:** 4
**Source:** [MASTER]+[INFERENCE]

### Decision

Security-test evidence uses a structured data model with the following fields:

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

### Rationale

A defined evidence structure records the tested target, execution conditions, input, expected behavior, actual behavior and test result in a machine-readable form.

### Consequences

* Evidence has a stable structure.
* Evidence can be validated independently from the ECU implementation.
* The model can be extended when required by later project functionality.
* The evidence model remains focused on test execution and observed results.

---

## ADR-010 — Evidence is generated outside the ECU and remains separate from target logic

**Status:** Accepted
**Phase:** 4
**Source:** [MASTER]+[INFERENCE]

### Decision

The ECU does not create, validate, serialize or manage test evidence.

Evidence is generated by the security-test architecture after test execution.

The execution relationship is:

```text
Security Test Case → Security Test Runner → ECU Adapter → ECU Simulator → ECU Response → Test Result → Evidence
```

### Rationale

Evidence records observations made by the test architecture and therefore remains separate from the system under test.

### Consequences

* The ECU implementation remains independent of evidence handling.
* Evidence generation is based on executed test information.
* Evidence processing can evolve independently from ECU behavior.

---

## ADR-011 — Evidence uses explicit PASS/FAIL based on expected versus actual

**Status:** Accepted
**Phase:** 4
**Source:** [MASTER]+[INFERENCE]

### Decision

The evidence result is derived from the comparison between expected and actual behavior:

```text
expected == actual → PASS
expected != actual → FAIL
```

Evidence validation also checks that the declared result is consistent with the expected and actual values.

A `FAIL` result represents a test deviation. It does not by itself establish a security vulnerability.

### Rationale

The evidence model records the defined test outcome, while security-finding classification is handled separately.

### Consequences

* Test deviations are represented consistently.
* Evidence result consistency can be validated programmatically.
* Security findings can use test evidence without changing the evidence result semantics.

---

## ADR-012 — Evidence is serialized as JSON

**Status:** Accepted
**Phase:** 4
**Source:** [MASTER]+[INFERENCE]

### Decision

Evidence objects are serialized as JSON.

The serialization flow is:

```text
Evidence object → to_dict() → JSON-compatible data → to_json() → JSON
```

### Rationale

JSON provides a machine-readable representation suitable for automated processing and CI/CD integration.

### Consequences

* Evidence can be processed programmatically.
* The representation is independent of a specific development environment.
* Phase 4 defines the evidence serialization format; CI/CD artifact handling is addressed separately.

---

## ADR-013 — Evidence validation is lightweight and implemented in the Evidence model

**Status:** Accepted
**Phase:** 4
**Source:** [MASTER]+[INFERENCE]

### Decision

Evidence validation is implemented in the Evidence model.

Validation checks the required identifying fields, target, preconditions, expected value, actual value, result type and result consistency.

Invalid evidence raises `EvidenceValidationError`.

### Rationale

Validation within the evidence model provides deterministic structural and semantic checks without introducing an additional validation framework.

### Consequences

* Invalid evidence records are rejected.
* Evidence consistency is checked close to the evidence representation.
* The implementation remains small and understandable.

---

## ADR-014 — Evidence timestamps use runtime-generated ISO 8601 UTC

**Status:** Accepted
**Phase:** 4
**Source:** [MASTER]+[INFERENCE]

### Decision

Evidence timestamps are generated at runtime in ISO 8601 UTC format.

Tests do not depend on a fixed wall-clock timestamp.

### Rationale

Runtime timestamps represent the actual execution time while avoiding dependencies on a predetermined timestamp value.

### Consequences

* Evidence contains execution-time metadata.
* Timestamp formatting remains consistent.
* Tests remain independent of a fixed wall-clock value.
* The timestamp format is deterministic even though the timestamp value changes between executions.

---

## ADR-015 — Evidence is separate from Security Finding Management

**Status:** Accepted
**Phase:** 4
**Source:** [MASTER]

### Decision

The evidence framework does not implement security-finding management.

Evidence records what was tested, what was expected, what actually occurred and which test result was obtained.

Security-finding documentation records the issue, impact, root cause, remediation and related information separately.

Structured finding documentation was introduced later as a separate documentation layer.

A generalized finding-management implementation may include information such as:

```text
Finding ID
Severity
CVSS
Root Cause
Customer Report
Remediation
Fix Management
```

These fields are outside the responsibility of the evidence model.

### Rationale

Separating test evidence from finding management keeps execution evidence focused on the observed test result and allows findings to reference that evidence without changing its purpose.

### Consequences

* Evidence remains focused on test execution.
* Finding documentation can reference existing tests and evidence.
* The evidence model is not extended into a generalized finding-management system.
* Finding-management capabilities remain outside the evidence architecture.

---

## ADR-016 — Phase 4 does not implement future regression or CI/CD layers

**Status:** Accepted
**Phase:** 4
**Source:** [MASTER]

### Decision

The Phase 4 implementation is limited to the Evidence Framework.

The following functionality belongs to later project development:

```text
Complete regression suite
Regression workflow
GitHub Actions
CI/CD integration
CI/CD artifact handling
End-to-end assessment
```

### Rationale

The project implements the architecture incrementally. Evidence generation is established before the later regression and CI/CD layers are introduced.

### Consequences

* Phase 4 remains limited to its defined evidence scope.
* Later regression and CI/CD functionality builds on the established test and evidence architecture.
* The project history remains traceable through the later architecture decisions.

---

## ADR-017 — Request validation distinguishes malformed, unsupported and rejected input

**Status:** Accepted
**Phase:** 6
**Source:** [MASTER]+[INFERENCE]

### Decision

The request-validation model established earlier is retained and explicitly extended for the TC-002 validation scenarios.

The validation semantics are:

```text
Malformed request structure → INVALID_REQUEST
Missing or invalid operation → INVALID_REQUEST
Valid but unsupported operation → UNSUPPORTED_OPERATION
Invalid parameter structure → INVALID_REQUEST
Parameter outside 0..255 → REQUEST_REJECTED
Boolean parameter → REQUEST_REJECTED
Valid numeric parameter in the inclusive range 0..255 → accepted for parameter validation
```

A boolean value is rejected as a numeric parameter even though Python `bool` is a subclass of `int`.

### Rationale

TC-002 requires deterministic handling of parameter boundaries and explicit distinction between numeric input and boolean values.

### Consequences

* The validation categories established by ADR-008 remain unchanged.
* The numeric boundary is explicitly inclusive.
* Boolean values cannot pass numeric parameter validation.
* Future validation rules preserve these distinctions unless an explicit architecture change is accepted.

---

## ADR-018 — TC-003 uses the established TC-001 security property as regression baseline

**Status:** Accepted
**Phase:** 7
**Source:** [TC-003]+[SOURCE]

### Decision

TC-003 verifies the security property established by TC-001.

The automated regression module is:

```text
04_tests/test_security_regression.py
```

The regression scenarios create their own `SecurityTestCase` with:

```text
test_id = TC-003
```

TC-001 establishes the original diagnostic authorization property. TC-003 verifies the established property without reusing the TC-001 test-case instance or TC-001 identifier.

The relationship is:

```text
TC-001
  ↓
establishes security property
  ↓
Established security property
  ↓
TC-003
  ↓
verifies property through regression scenarios
  ↓
SecurityTestCase(test_id="TC-003")
```

The protected-operation property is:

```text
Unauthorized protected operation → ACCESS_DENIED
```

### Rationale

The regression test requires its own test identity while retaining a traceable relationship to the security property established by TC-001.

### Consequences

* TC-003 remains independently identifiable as a regression test.
* The original security property remains traceable to TC-001.
* The regression suite verifies the established property without duplicating the TC-001 test-case identity.

---

## ADR-019 — Vulnerable and secure ECU modes provide controlled lifecycle states

**Status:** Accepted
**Phase:** 7
**Source:** [SOURCE]+[TC-003]

### Decision

`ECUSimulator` provides explicit security modes:

```text
SecurityMode.SECURE
SecurityMode.VULNERABLE
```

TC-003 uses these modes to demonstrate the controlled transition from the reproduced security-relevant deviation to the secure behavior used for regression verification.

The defined behavior is:

```text
VULNERABLE + unauthorized protected operation → ACCESS_GRANTED
SECURE + unauthorized protected operation → ACCESS_DENIED
```

The security mode is selected as part of the test setup. The regression test does not modify the simulator during test execution as a runtime fix mechanism.

### Rationale

Explicit simulator modes provide deterministic reproduction of the defined vulnerable behavior and deterministic verification of the secure behavior.

### Consequences

* The vulnerable behavior can be reproduced under controlled conditions.
* The secure behavior can be verified using the same security property.
* The lifecycle representation is part of the simulation and does not represent an actual software-patch process.
* The mode mechanism does not implement automated finding-to-fix management.

---

## ADR-020 — Regression evidence is generated from the executed TestResult

**Status:** Accepted
**Phase:** 7
**Source:** [TC-003]+[SOURCE]

### Decision

TC-003 generates regression evidence using the existing `EvidenceGenerator`.

Evidence is generated from the executed `SecurityTestCase` and `TestResult`.

The evidence receives its identity and result data from the executed test objects:

```text
test_id → test_case.test_id
expected → TestResult.expected
actual → TestResult.actual
result → comparison of expected and actual
```

The execution flow is:

```text
SecurityTestCase(test_id="TC-003")
→ SecurityTestRunner.run()
→ TestResult
→ EvidenceGenerator.generate()
→ Evidence(test_id="TC-003")
→ Evidence.validate()
```

No separate regression evidence generator or regression-specific evidence model is introduced.

For the secure unauthorized-operation regression scenario, the evidence contains:

```text
test_id=TC-003
target=simulated-ecu
authorization=false
ecu_state=READY
security_mode=SECURE
expected=ACCESS_DENIED
actual=ACCESS_DENIED
result=PASS
```

### Rationale

Generating evidence from the executed test result keeps evidence tied to the actual test execution and independent from the pytest assertion mechanism.

### Consequences

* Regression evidence uses the existing evidence architecture.
* The evidence result is derived from expected versus actual behavior.
* No additional evidence-generation component is required for TC-003.
* Evidence validation remains part of the established evidence model.

---

## ADR-021 — TC-003 distinguishes lifecycle demonstration from regression retest

**Status:** Accepted
**Phase:** 7
**Source:** [TC-003]+[SOURCE]

### Decision

TC-003 separates the controlled lifecycle demonstration from the actual secure regression retest.

The relevant scenarios are:

```text
Lifecycle Demonstration
→ test_tc003_reproduces_original_vulnerable_behavior()

Regression / Retest
→ test_tc003_retest_confirms_secure_behavior()
→ test_tc003_regression_evidence_matches_retest_result()
→ test_tc003_regression_preserves_authorized_behavior()
```

The vulnerable-behavior test intentionally produces a non-passing `TestResult` because the vulnerable ECU returns `ACCESS_GRANTED` where `ACCESS_DENIED` is required.

The pytest test itself passes because it verifies that the defined security deviation was detected.

### Rationale

The lifecycle demonstration establishes the controlled reproduction of the original deviation, while the secure retest verifies the expected corrected behavior.

### Consequences

* The lifecycle demonstration and security regression have distinct purposes.
* A pytest `PASS` indicates that the test assertion succeeded.
* The underlying `TestResult` can independently represent the detected security deviation.
* The secure retest provides the actual regression verification of the expected security behavior.

---

## ADR-022 — Phase 8 uses structured example findings as a documentation layer

**Status:** Accepted
**Phase:** 8
**Source:** [MASTER]+[INFERENCE]

### Decision

Phase 8 uses structured example findings as a documentation layer.

The example finding files are:

```text
05_examples/sample_finding_SEC-001.md
05_examples/sample_finding_SEC-002.md
```

`SEC-001` documents the controlled authorization deviation associated with TC-001:

```text
Expected → ACCESS_DENIED
Actual → ACCESS_GRANTED
Result → FAIL
```

`SEC-002` documents the validation assessment represented by TC-002 scenarios, where no security-relevant deviation is reproduced.

Finding documents reference existing tests and evidence without modifying the Evidence model.

### Rationale

The finding examples provide a structured representation of requirement, reproduction, evidence, impact, root cause, recommendation, fix, retest and regression relationship without introducing unsupported real-vehicle claims.

### Consequences

* Finding documentation remains separate from the evidence data model.
* The example findings provide representative security-finding documentation.
* Finding examples are static project artifacts.
* The examples do not implement generalized finding ingestion, finding history or automated finding management.
* Finding-specific information remains at the documentation layer.

---

## ADR-023 — Automated regression verifies security behavior and evidence consistency

**Status:** Accepted
**Phase:** 9
**Source:** [SOURCE]

### Decision

The automated regression suite verifies both the expected security behavior and the consistency of the generated evidence.

The dedicated regression scenarios cover:

```text
Unauthorized protected operation
Authorized protected operation
Invalid message
Unsupported operation
Boundary input
Blocked ECU state
Regression evidence
```

The evidence verification flow is:

```text
Execute secure regression scenario
→ Obtain TestResult
→ Generate Evidence
→ Check evidence fields
→ Evidence.validate()
```

The regression suite verifies the evidence identity, target, preconditions, expected value, actual value and result.

`evidence.validate()` is part of the automated regression verification.

### Rationale

Regression verification covers both the behavior under test and the integrity of the evidence produced from that execution.

### Consequences

* Security behavior is verified through automated regression scenarios.
* Evidence consistency is verified as part of the regression suite.
* The existing Evidence model remains responsible for evidence validation.
* Evidence consistency does not by itself establish vulnerability, severity or impact.
* The regression suite does not implement historical baseline comparison, finding ingestion, remediation tracking or CI/CD artifact management.

---

## Change Policy

Architecture changes are documented in this document before they are accepted.

Later phases may add further ADRs when a meaningful architectural decision is introduced.

Later implementation and documentation changes must remain consistent with accepted decisions unless the affected decision is explicitly changed.

A change to an existing architectural decision is documented and reviewed explicitly.

A meaningful new implementation architecture decision receives a new ADR rather than being silently appended to an existing historical decision.
