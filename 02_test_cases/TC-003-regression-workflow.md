# TC-003 — Regression Workflow

## Purpose

TC-003 defines the finding-to-regression workflow of the Automotive Security Regression Lab.

The purpose of the workflow is to convert a confirmed security finding into a reproducible regression test that can be executed again after a security-relevant change.

The workflow establishes a traceable relationship between:

* the original security finding
* the affected security property
* the regression test case
* the expected security behavior
* the executed test result
* the generated evidence

TC-003 is therefore not a replacement for TC-001 or TC-002. It defines how an existing security finding is represented as a repeatable regression condition and how the regression result is evaluated.

The current implementation uses the existing security-test architecture, Evidence Framework, and pytest-based regression suite for this workflow.

---

## Scope

The workflow applies to security findings that can be represented by the existing test architecture of the Automotive Security Regression Lab.

The implementation provides the technical foundation required for this workflow:

* `ECUSimulator` provides a deterministic security target.
* `ECUAdapter` provides the target interface.
* `SecurityTestCase` defines the input and expected result of a test.
* `SecurityTestRunner` executes a test case and compares the actual response with the expected response.
* `EvidenceGenerator` creates structured evidence from a completed test execution.
* TC-001 provides the security property currently demonstrated by the implemented regression workflow.
* TC-002 provides an additional validated security-test property for message and request validation. It is not represented as an independent regression baseline in the current regression implementation.
* The regression test suite executes defined regression scenarios through the existing architecture.
* Regression evidence is generated from the executed test result.
* The regression suite is executed by the project's CI/CD workflow.

The workflow does not introduce a separate finding-management or regression-management architecture.

---

## Regression Principle

A security finding becomes a regression test when the security property affected by the finding is expressed as an explicit, reproducible test condition.

The regression test defines at minimum:

1. a unique test identifier
2. the security behavior being protected
3. the relevant preconditions
4. the test input
5. the expected security response
6. the actual security response obtained during execution
7. a deterministic pass/fail evaluation
8. evidence for the executed test

The regression test verifies the security property rather than merely verifying that the test itself can be executed.

---

## Finding-to-Regression Workflow

The implemented workflow follows the following logical sequence:

```text
Security Finding
        |
        v
Identify affected security property
        |
        v
Define regression condition
        |
        v
Define preconditions and input
        |
        v
Define expected security behavior
        |
        v
Represent regression test case
        |
        v
Execute through SecurityTestRunner
        |
        v
Compare actual result with expected result
        |
        v
Generate structured evidence
        |
        v
Evaluate regression result
        |
        +---- PASS ----> Security property remains enforced
        |
        +---- FAIL ----> Regression detected
```

Each regression test remains traceable to the security property established by the corresponding finding.

The current implementation demonstrates this workflow using the existing test architecture and regression scenarios.

---

## Regression Test Case Definition

A regression test case is represented by the existing `SecurityTestCase` model.

The test case contains:

```text
test_id
description
request
expected_status
```

The `test_id` identifies the regression test uniquely.

The `description` identifies the security property or behavior being verified.

The `request` defines the input presented to the target.

The `expected_status` defines the security response required for the test to pass.

The expected response represents the intended secure behavior. It is not derived from the current actual response of the target.

---

## Preconditions

Regression tests establish all security-relevant conditions required to reproduce the affected security property.

Relevant preconditions may include:

```text
authorization state
ECU operational state
security mode
target configuration
other security-relevant test conditions
```

Only preconditions relevant to the security property under test are defined.

Preconditions are explicit enough for the deterministic simulated target to reproduce the test condition.

---

## Input Definition

The regression test input reproduces the condition relevant to the original security finding.

For the current simulated ECU architecture, the input is represented by the request mapping accepted by `ECUSimulator.handle_request()`.

The request is compatible with the target interface and preserves the security-relevant condition represented by the finding.

Where the finding concerns invalid, unauthorized, unsupported, or otherwise security-sensitive input, the regression test preserves that condition explicitly.

---

## Expected Security Behavior

The expected behavior is the security requirement that must remain enforced after a security-relevant change.

Examples represented by the existing test architecture include:

```text
Unauthorized protected operation

    Expected: ACCESS_DENIED

Authorized protected operation

    Expected: ACCESS_GRANTED

Unsupported operation

    Expected: UNSUPPORTED_OPERATION

Malformed request

    Expected: INVALID_REQUEST

Invalid parameter or blocked ECU state

    Expected: REQUEST_REJECTED
```

These properties are represented by the existing security-test architecture. They provide regression coverage where they are included in the implemented regression scenarios.

The current regression implementation uses the diagnostic-authorization security property established by TC-001 as its implemented regression baseline.

---

## Regression Execution

A regression test is executed through the existing test execution abstraction.

The execution flow is:

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
ECUSimulator / target implementation
        |
        v
ECUResponse
        |
        v
actual_status
        |
        v
comparison with expected_status
        |
        v
TestResult
```

The runner determines whether the actual response status matches the expected response status.

A matching result is a passed test.

A non-matching result is a failed test and indicates that the expected security behavior was not observed.

The regression test suite uses this execution and comparison model rather than introducing a separate result mechanism.

---

## Evidence Generation

A completed regression execution is represented as structured evidence using the existing evidence model.

The evidence contains:

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

The `EvidenceGenerator` derives the expected and actual response values from the `SecurityTestCase` and `TestResult`.

The evidence result is `PASS` when expected and actual behavior are equal. Otherwise the evidence result is `FAIL`.

Evidence validation remains consistent with the existing `Evidence` validation rules.

Regression evidence therefore records the result of an actual regression execution using the same evidence architecture used by the security test cases.

## Regression Result

The regression result is determined from the comparison between expected and actual behavior.

```text
Expected behavior == Actual behavior

        |
        v

      PASS

Expected behavior != Actual behavior

        |
        v

      FAIL
```

A `PASS` means that the security behavior defined by the regression test was observed during execution.

A `FAIL` means that the observed behavior differs from the defined security expectation and therefore requires investigation.

A regression failure is an indication that the defined security behavior was not observed during the test execution. Further security analysis is required before drawing a vulnerability conclusion.

## Relationship to Existing Test Cases

TC-001 and TC-002 remain independent security test cases.

TC-001 verifies diagnostic authorization behavior.

TC-002 verifies message validation behavior.

TC-001 provides the security property currently demonstrated by the implemented regression workflow:

```text
Protected operation + unauthorized
        |
        v
ACCESS_DENIED
```

This security property is used as the basis for the controlled TC-003 regression lifecycle and the corresponding automated regression coverage.

TC-002 provides an additional validated security-test property for message and request validation. It remains part of the established security-test coverage, but it is not represented as an independent regression baseline in the current regression implementation.

TC-003 defines the workflow by which an established security property is represented as a regression condition and subsequently executed and evidenced.

The current implemented relationship is therefore:

```text
TC-001
  |
  +-- Diagnostic Authorization Property
          |
          v
     TC-003 Regression Workflow
          |
          v
     Automated Regression Coverage
```

TC-002 remains independently covered by its dedicated security-test implementation and tests:

```text
TC-002
  |
  +-- Message Validation Property
          |
          v
     Dedicated TC-002 Test Coverage
```

TC-003 does not change the security semantics of TC-001 or TC-002.

---

## Determinism

The regression workflow produces reproducible results under equivalent test conditions.

The current project architecture supports deterministic execution through the simulated ECU.

The regression test therefore avoids dependencies on:

* uncontrolled network communication
* external ECU availability
* nondeterministic target behavior
* unspecified environmental state
* manually interpreted response values

The target abstraction keeps the regression workflow independent from the concrete ECU implementation.

---

## Traceability

A regression test remains traceable from the original finding to the executed evidence.

The relationship is:

```text
Finding
  |
  +-- affected security property
          |
          +-- regression test ID
                  |
                  +-- test input
                  |
                  +-- expected behavior
                  |
                  +-- execution result
                          |
                          +-- evidence
```

The unique test identifier connects the regression test definition with its execution result and evidence.

The current regression implementation also preserves the distinction between the security finding and the regression test itself. Finding management and regression execution remain separate concerns.

---

## Regression Verification

The regression implementation is verified through the project's automated test suite.

The regression coverage includes the established security properties represented by the implemented regression scenarios.

The regression tests verify:

```text
1. The security property is represented by an explicit test condition.

2. The regression condition can be represented by a SecurityTestCase.

3. The test can be executed through the existing target and runner abstractions.

4. The actual result is compared with the defined expected result.

5. The result can be represented as PASS or FAIL.

6. Structured evidence can be generated for the execution.

7. The evidence remains consistent with the executed test result.

8. The simulated ECU remains deterministic.

9. Existing TC-001 functionality remains operational.

10. Existing TC-002 functionality remains operational.
```

The automated regression suite is executed independently from the documentation and therefore does not rely on the presence of this document for its result.

---

## CI/CD Integration

The regression suite is integrated into the project's GitHub Actions workflow.

The relevant execution relationship is:

```text
Repository Change
        |
        v
GitHub Actions
        |
        v
Python Environment
        |
        v
Install Dependencies
        |
        v
pytest Regression Suite
        |
        v
Regression Result
        |
        v
Evidence Generation
        |
        v
Artifact Upload
```

The CI/CD workflow executes the existing regression test implementation and preserves generated evidence as a workflow artifact.

The CI/CD pipeline does not introduce a separate regression-test implementation. It executes and records the existing regression workflow.

---

## Implementation Boundary

The current implementation contains the technical elements required for the demonstrated regression workflow:

```text
ECUSimulator
ECUAdapter
SecurityTestCase
SecurityTestRunner
TestResult
Evidence
EvidenceGenerator
TC-001
TC-002
Regression Test Suite
Regression Evidence
pytest
GitHub Actions
```

The implementation therefore supports:

```text
security property
        |
        v
regression condition
        |
        v
automated regression test
        |
        v
TestResult
        |
        v
regression evidence
        |
        v
CI/CD execution
```

The project deliberately keeps broader security-management functions separate from the regression workflow.

The following functions are not represented as implemented merely by TC-003:

```text
automatic finding ingestion
automatic vulnerability-management workflow
automatic remediation tracking
automatic historical comparison across arbitrary findings
automatic regression-test generation from unstructured findings
automatic regression reporting
```

These functions require separate implementation and verification if they are introduced in the future.

---

## Historical Phase 7 Boundary

The original Phase-7 implementation established the finding-to-regression workflow using the existing security-test and evidence architecture.

At that point, the workflow was implemented incrementally around:

```text
Security Finding
        |
        v
Security Property
        |
        v
Regression Test Case
        |
        v
Test Execution
        |
        v
Evidence
```

The project subsequently extended this workflow with automated regression coverage and CI/CD execution.

The historical Phase 7 boundary is retained to document the development history. It does not imply that the current repository still treats regression execution as a future capability.

---

## Current Status

TC-003 documents and represents the regression workflow currently used by the Automotive Security Regression Lab.

The workflow is based on the existing security-test architecture and Evidence Framework.

The implemented regression coverage is executed through pytest and integrated into the project's CI/CD workflow.

The current regression implementation uses the established diagnostic-authorization security property from TC-001 as its regression baseline.

The automated regression coverage is implemented in:

```text
04_tests/test_security_regression.py
```

The regression implementation reuses the existing:

```text
SecurityTestCase
SecurityTestRunner
ECUAdapter
ECUSimulator
TestResult
EvidenceGenerator
```

The implementation does not introduce a separate TC-003 execution architecture.

TC-002 remains independently covered by its dedicated security-test implementation. Its message-validation properties are not currently represented as an independent regression baseline.

The project continues to distinguish between:

```text
Security Finding Management
        |
        +-- finding-specific information
```

and:

```text
Regression Testing
        |
        +-- reproducible security property
        +-- automated test execution
        +-- result evaluation
        +-- evidence
```

This separation keeps the regression mechanism focused on reproducible verification of security properties.

The workflow remains limited to the controlled simulated automotive environment of the project.
