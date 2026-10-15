# Evidence Format

## Purpose

The Evidence Framework provides a structured, reproducible, and machine-readable representation of a completed security test execution in the Automotive Security Regression Lab.

An evidence record documents:

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

The Evidence Framework is used by the implemented security test scenarios and regression test workflows.

Evidence records the relationship between a security test, its observed execution result, and the structured evidence derived from that result:

```text
Security Test
      |
      v
Observation
      |
      v
Evidence
```

The framework documents what was tested, under which conditions, what was expected, what was actually observed, and whether the observed behavior matched the expected behavior.

Evidence is generated exclusively from the simulated test environment. No real ECU data, production credentials, vehicle data, network traffic, or customer data is required.

---

## Evidence Model

Evidence is represented by the `Evidence` model in `security_lab.evidence`.

Each evidence record represents one executed security test case.

The current evidence model contains:

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

| Field           | Description                                                   |
| --------------- | ------------------------------------------------------------- |
| `test_id`       | Identifier of the security test associated with the execution |
| `timestamp`     | UTC timestamp of the evidence creation                        |
| `target`        | Test target against which the test was executed               |
| `preconditions` | Conditions established before execution                       |
| `input`         | Input used by the security test                               |
| `expected`      | Behavior expected by the test                                 |
| `actual`        | Behavior actually observed                                    |
| `result`        | Evidence result: `PASS` or `FAIL`                             |
| `notes`         | Additional execution context or observations                  |

The `test_id` identifies the security test associated with the execution.

The `timestamp` records when the evidence was generated.

The `target` identifies the security target used for the execution.

The `preconditions` record security-relevant conditions established before execution.

The `input` contains the request presented to the target.

The `expected` value represents the security behavior defined by the test case.

The `actual` value represents the response observed during execution.

The `result` represents the evaluated evidence result.

The `notes` field provides additional execution context.

The model is intentionally simple.

Optional fields such as `software_version`, `test_environment`, or `execution_id` may be considered for a later extension of the evidence model.

---

## Required Fields

All fields of the current evidence model are mandatory:

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

Evidence without the mandatory fields is not valid evidence.

The Evidence Framework validates the required structure before evidence is accepted or serialized.

---

## Timestamp

The timestamp is generated dynamically when evidence is created.

It uses an ISO 8601 UTC representation.

Example:

```text
2026-08-23T21:52:16.789923Z
```

Tests must not depend on a fixed timestamp.

The timestamp is part of the execution evidence and identifies when the evidence record was generated.

---

## Result Semantics

Evidence supports two result values:

```text
PASS
FAIL
```

### PASS

`PASS` means:

```text
expected == actual
```

The observed behavior matched the behavior expected by the test.

### FAIL

`FAIL` means:

```text
expected != actual
```

The observed behavior did not match the behavior expected by the test.

A `FAIL` result documents a deviation between expected and observed behavior. The result alone does not establish a security vulnerability.

Security assessment, finding classification, root-cause analysis, and impact assessment are outside the scope of the Evidence Framework.

---

## Evidence Generation

Evidence is generated through `EvidenceGenerator`.

The generator receives:

```text
SecurityTestCase
TestResult
target
preconditions
notes
```

The expected and actual response values are derived from the executed test result.

The evidence result is derived from the comparison of expected and actual behavior:

```text
expected == actual
        |
        v
      PASS

expected != actual
        |
        v
      FAIL
```

The generated evidence is validated before it is returned.

`EvidenceGenerator` connects the executed security test result with the structured `Evidence` model.

Test execution remains the responsibility of the security-test infrastructure, and ECU security policy remains the responsibility of the ECU simulation.

---

## Evidence Validation

`Evidence.validate()` verifies the structural and semantic consistency of an evidence record.

The validation includes:

```text
required fields are present
preconditions are a mapping
result is PASS or FAIL
timestamp is valid ISO-8601 with timezone information
result matches the expected/actual comparison
```

An evidence record is valid when its declared result is consistent with the recorded expected and actual behavior.

For example:

```text
expected = ACCESS_DENIED
actual   = ACCESS_DENIED
result   = PASS
```

is consistent.

The following is inconsistent:

```text
expected = ACCESS_DENIED
actual   = ACCESS_GRANTED
result   = PASS
```

because the expected and actual values differ.

An invalid evidence record causes evidence validation to fail and is not treated as a valid evidence artifact.

---

## JSON Serialization

Evidence can be converted into a JSON-compatible dictionary using `Evidence.to_dict()` and serialized using `Evidence.to_json()`.

Evidence can also be reconstructed from a dictionary using `Evidence.from_dict()`.

Example:

```json
{
  "actual": "ACCESS_DENIED",
  "expected": "ACCESS_DENIED",
  "input": {
    "operation": "PROTECTED_OPERATION"
  },
  "notes": "Unauthorized protected operation was rejected.",
  "preconditions": {
    "authorization": false
  },
  "result": "PASS",
  "target": "simulated-ecu",
  "test_id": "TC-001",
  "timestamp": "2026-08-23T21:52:16.789923Z"
}
```

The timestamp in an actual evidence record is generated at runtime and is not a fixed value.

JSON serialization provides a machine-readable representation that can be consumed by automation or stored as a test artifact.

The Evidence Framework provides the evidence representation and serialization. CI/CD orchestration is implemented at the workflow level.

---

## Security Testing Context

A security test may establish a security requirement such as:

```text
Protected operation requires authorization.
```

A corresponding test may use:

```text
Authorization = false
Operation = PROTECTED_OPERATION
Expected = ACCESS_DENIED
```

If the simulated ECU returns:

```text
Actual = ACCESS_GRANTED
```

the resulting evidence is:

```text
result = FAIL
```

This evidence documents the observed test result.

It does not automatically create a security finding.

The conceptual relationship is:

```text
Security Test
      |
      v
Observation
      |
      v
Evidence
      |
      v
Security Finding
```

Finding management is outside the scope of the Evidence Framework.

---

## Architectural Boundary

The Evidence Framework is separated from the ECU simulation.

The ECU remains the System Under Test and has no knowledge of evidence generation.

The execution and evidence flow is:

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
ECU Simulator
        |
        v
Response
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

The Evidence Framework consumes the result of test execution and represents the observation in a structured form.

It does not implement ECU security policy.

The responsibility boundaries are:

```text
Security Test Case
    defines the test and expected behavior

Security Test Runner
    executes the test case

ECU Adapter
    connects the test infrastructure with the target

ECU Simulator
    implements the simulated ECU behavior

TestResult
    represents the execution result

EvidenceGenerator
    converts the execution result into evidence

Evidence
    stores the structured execution record
```

The Evidence Framework does not access internal ECU state.

---

## Determinism

Evidence generation does not require:

```text
network access
physical hardware
a real ECU
external services
random test data
```

The Evidence Framework can therefore be tested locally and reproducibly.

Evidence generation is deterministic with respect to the test input, expected behavior, actual behavior, and explicitly supplied preconditions.

The timestamp is intentionally runtime-generated and is the time-dependent field in the evidence record.

The current regression implementation uses the deterministic `ECUSimulator` as its target.

No external network communication or external ECU availability is required for the automated regression evidence tests.

---

## Historical Development of the Evidence Framework

The following sections document how the existing Evidence Framework was introduced and subsequently reused by the security-test and regression implementation.

The historical descriptions distinguish changes to the evidence model from later changes in how the existing model is used.

### Phase 4 — Evidence Framework

Phase 4 introduced the structured Evidence Framework.

Implemented in Phase 4:

```text
structured evidence model
mandatory field validation
PASS / FAIL semantics
runtime timestamp
JSON serialization
integration with the existing Phase 3 test result
deterministic local evidence tests
```

The Phase-4 implementation established the evidence model used by later security-test and regression workflows.

The following capabilities were outside the Phase-4 implementation:

```text
security finding management
severity management
CVSS calculation
root-cause management
fix tracking
retest workflow
complete security regression suite
CI/CD pipeline
real ECU communication
real vehicle communication
```

Later phases extended the use of the existing Evidence Framework without changing its fundamental evidence model.

### Phase 5 — TC-001 Evidence Integration

Phase 5 introduced the first dedicated security test:

```text
TC-001 — Diagnostic Authorization
```

The existing Evidence Framework was reused to record TC-001 executions.

TC-001 evidence represents the relationship between:

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
Expected vs Actual
       |
       v
TestResult
       |
       v
Evidence
```

For the unauthorized TC-001 scenario, the expected secure behavior is:

```text
ACCESS_DENIED
```

A controlled vulnerable execution may produce:

```text
Actual = ACCESS_GRANTED
```

which results in:

```text
result = FAIL
```

The Evidence Framework records the deviation. It does not determine whether the deviation constitutes a formal security finding.

No separate evidence architecture was introduced for TC-001.

### Phase 6 — TC-002 Evidence Integration

Phase 6 introduced:

```text
TC-002 — Message Validation
```

The existing Evidence Framework is reused for TC-002 executions.

For a malformed or otherwise invalid request, the expected response is:

```text
INVALID_REQUEST
```

For an unsupported operation:

```text
UNSUPPORTED_OPERATION
```

If the target returns a different response:

```text
Expected != Actual
Result   = FAIL
```

TC-002 uses the same evidence model and serialization mechanism established in Phase 4.

No separate evidence format is introduced for TC-002.

### Phase 7 — TC-003 Regression Evidence Integration

Phase 7 introduced:

```text
TC-003 — Regression Workflow
```

TC-003 reuses the established evidence architecture to record the controlled regression lifecycle.

The workflow includes:

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

The existing Evidence Framework remains the common evidence representation.

---

## Current Evidence Framework Scope

The current Evidence Framework provides one common evidence representation for the implemented security-test and regression execution paths.

The evidence structure remains:

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

The current project uses this structure with:

```text
TC-001 — Diagnostic Authorization

TC-002 — Message Validation

TC-003 — Automated Security Regression
```

The Phase-7 controlled regression workflow also uses the same evidence structure while reusing the `TC-001` `SecurityTestCase`.

The evidence workflow is:

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
Evidence Model
      |
      v
Evidence.validate()
      |
      v
JSON
```

Test-specific information is represented through the existing fields such as `test_id`, `preconditions`, `input`, `expected`, `actual`, and `notes`.

The framework provides a common evidence representation across the implemented security-test and regression paths. It does not require a separate evidence schema for each test case.
