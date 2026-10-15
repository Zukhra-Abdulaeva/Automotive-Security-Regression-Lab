# Environment Setup — Automotive Security Regression Lab

## 1. Purpose and Scope

This guide describes how to set up and run the tests for the Automotive Security Regression Lab locally.

The project uses Python and pytest. The ECU is simulated; the project does not establish a connection to real vehicles, ECUs or vehicle networks.

The details regarding Python and pytest versions, as well as the test configuration, are taken from `pyproject.toml` and `.github/workflows/security-regression.yml`. The commands for local setup are written for Windows PowerShell.

## 2. Prerequisites

- Git
- Python 3.12 or later (`pyproject.toml`: `requires-python = ‘>=3.12’`)
- PowerShell
- Access to the repository

The development dependency is specified in `pyproject.toml` as `pytest>=9,<10`. The CI workflow uses Python 3.12 and also installs `pytest>=9,<10`.

## 3. Open the repository

If the repository is already present locally, open PowerShell in the project directory. Example:

```powershell
Set-Location ‘C:\Users\<User>\GitHub_Automotive-Security\Automotive-Security-Regression-Lab’
```

If you haven’t cloned the repository yet:

```powershell
git clone https://github.com/Zukhra-Abdulaeva/Automotive-Security-Regression-Lab.git
Set-Location ‘Automotive-Security-Regression-Lab’
```

Check that you are in the repository’s root directory:

```powershell
git status
```

## 4. Check Python

```powershell
python --version
python -m pip --version
```

The project configuration requires Python 3.12 or later. Python 3.12 also corresponds to the version configured in the CI workflow.

In Windows PowerShell, this guide uses the `python` command rather than `python3`.

## 5. Setting up a virtual environment

Only create the virtual environment if `.venv` does not already exist:

```powershell
python -m venv .venv
```

Activate it in PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

If `(.venv)` is already at the start of the PowerShell command line, the environment is usually already activated. It does not need to be recreated.

Check which interpreter is actually being used:

```powershell
python -c ‘import sys; print(sys.executable)’
```

The path should point to the project-local file `.venv\Scripts\python.exe`. The `.venv` environment is local and must not be checked into the repository; `.gitignore` already contains the relevant exclusions.

## 6. Install pytest

Run the installation within the activated virtual environment:

```powershell
python -m pip install --upgrade pip
python -m pip install ‘pytest>=9,<10’
```

Check the installed version:

```powershell
python -m pytest --version
```

## 7. Running tests

Run all commands from the root directory of the repository with the project's virtual environment activated.

### Run the full test suite

Execute all tests discovered under `04_tests/`:

```powershell
python -m pytest -v
```

### Run tests by test module

The test suite is organized into the following seven test modules:

| Test module | Purpose |
|---|---|
| `test_ecu_simulator.py` | ECU simulator tests |
| `test_evidence.py` | Evidence handling tests |
| `test_foundation.py` | Foundation tests |
| `test_security_regression.py` | Security regression tests |
| `test_tc001_diagnostic_authorization.py` | Diagnostic authorization tests (TC001) |
| `test_tc002_message_validation.py` | Message validation tests (TC002) |
| `test_test_runner.py` | Test runner tests |

Run an individual test module using its path relative to the repository root:

```powershell
python -m pytest -v 04_tests/test_ecu_simulator.py
python -m pytest -v 04_tests/test_evidence.py
python -m pytest -v 04_tests/test_foundation.py
python -m pytest -v 04_tests/test_security_regression.py
python -m pytest -v 04_tests/test_tc001_diagnostic_authorization.py
python -m pytest -v 04_tests/test_tc002_message_validation.py
python -m pytest -v 04_tests/test_test_runner.py
```

### Verify the test results

Pytest reports the number of tests collected, the outcome of each test, and the total execution time.

`pyproject.toml` configures `04_tests` as the test directory and adds `03_src` for Python imports.

## 8. CI configuration

The workflow is located at `.github/workflows/security-regression.yml`. It is configured to run on `ubuntu-latest` with Python 3.12 upon pushes and pull requests. It installs `pytest>=9,<10`, executes `04_tests/test_security_regression.py` and creates or uploads regression evidence as an artefact.

This describes the **configuration** of the workflow, not the success of a specific CI run. A successful CI run must be verified in GitHub Actions by referring to the relevant run and its logs.

## 9. Reproducibility and Git status

Before committing, it is recommended that you run:

```powershell
python -m pytest -v
git status
git diff
```

`.venv/` and `.pytest_cache/` are local and generated files respectively and should not be committed; the existing `.gitignore` file excludes them.
