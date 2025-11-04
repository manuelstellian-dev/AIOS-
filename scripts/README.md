# AIOS- Verification Scripts

This directory contains automated verification and testing scripts for the AIOS- repository.

## Verification Agent

### Overview

The `verification_agent.py` script is a comprehensive automated testing and verification system that:

- ✅ Installs all required dependencies
- ✅ Verifies Python syntax for all files
- ✅ Checks import statements for validity
- ✅ Runs static code analysis (flake8, pylint, mypy, bandit)
- ✅ Detects files without test coverage
- ✅ Generates missing tests automatically
- ✅ Runs all tests with pytest
- ✅ Calculates and reports code coverage
- ✅ Generates detailed verification reports

### Usage

#### Basic Usage (Quick Verification)

```bash
python scripts/verification_agent.py
```

This runs a quick verification with the default coverage threshold of 97%.

#### Full Verification with Static Analysis

```bash
python scripts/verification_agent.py --full-check
```

This runs the complete verification suite including:
- Static code analysis with flake8, pylint, mypy, and bandit
- Automatic test generation for uncovered files
- Comprehensive security scanning

#### Custom Coverage Threshold

```bash
python scripts/verification_agent.py --coverage-threshold 85
```

Set a custom coverage threshold (useful during development).

#### Combined Options

```bash
python scripts/verification_agent.py --full-check --coverage-threshold 90
```

### Command Line Options

| Option | Description | Default |
|--------|-------------|---------|
| `--coverage-threshold` | Minimum coverage percentage required | 97.0 |
| `--full-check` | Enable full verification with static analysis | False |

### Output Files

The verification agent generates the following files:

- `verification-report.md` - Detailed markdown report with all results
- `coverage.xml` - XML coverage report for CI/CD integration
- `htmlcov/` - HTML coverage report for human review
- `coverage.json` - JSON coverage data for programmatic access
- `.coverage` - Coverage database file

### Exit Codes

- `0` - Verification passed successfully
- `1` - Verification failed (syntax errors, critical import failures)

Note: Coverage below threshold currently returns exit code 0 to allow gradual improvement.

### Integration with CI/CD

The verification agent is integrated with GitHub Actions via the `.github/workflows/comprehensive-verification.yml` workflow.

The workflow runs automatically on:
- Push to `main`, `develop`, or `master` branches
- Pull requests to `main`, `develop`, or `master` branches
- Manual workflow dispatch

### Examples

#### Example 1: Pre-commit Check

Before committing code, run a quick verification:

```bash
python scripts/verification_agent.py --coverage-threshold 80
```

#### Example 2: Full Quality Check

Before creating a pull request, run the full verification:

```bash
python scripts/verification_agent.py --full-check
```

#### Example 3: CI/CD Integration

In GitHub Actions:

```yaml
- name: Run Verification
  run: python scripts/verification_agent.py --full-check --coverage-threshold 97
```

### Features in Detail

#### 1. Dependency Installation

The agent automatically installs:
- Core testing tools: pytest, pytest-cov, pytest-asyncio, coverage
- Code quality tools: flake8, pylint, mypy, bandit, black, isort
- Project dependencies from `requirements.txt`
- CPU-optimized PyTorch for lightweight CI/CD

#### 2. Syntax Verification

Uses Python's `ast` module to parse and verify syntax of all `.py` files in the repository.

#### 3. Import Checking

- Extracts all import statements using AST
- Verifies that modules can be imported
- Skips optional dependencies (cloud SDKs, etc.)
- Reports missing dependencies

#### 4. Static Analysis (--full-check)

- **flake8**: PEP 8 style guide enforcement
- **pylint**: Advanced code quality analysis
- **mypy**: Static type checking
- **bandit**: Security vulnerability scanning

#### 5. Coverage Analysis

- Runs pytest with coverage measurement
- Generates multiple report formats (XML, HTML, JSON, terminal)
- Compares coverage against threshold
- Identifies files with low coverage

#### 6. Automatic Test Generation

When `--full-check` is enabled and uncovered files are detected:
- Parses Python files to find functions and classes
- Generates basic test stubs in `tests/generated/`
- Creates tests that verify existence and basic instantiation
- Does not overwrite existing tests

#### 7. Report Generation

Generates a comprehensive markdown report with:
- Overall statistics
- Pass/fail status
- Error details
- Warning summaries
- Coverage metrics

### Troubleshooting

#### Issue: Tests fail with missing dependencies

**Solution**: Make sure all dependencies are installed:

```bash
pip install -r requirements.txt
```

#### Issue: Coverage is below threshold

**Solution**: Add more tests or lower the threshold during development:

```bash
python scripts/verification_agent.py --coverage-threshold 70
```

#### Issue: Static analysis tools not found

**Solution**: Run with `--full-check` or install them manually:

```bash
pip install flake8 pylint mypy bandit black isort
```

### Contributing

To add new verification features:

1. Add the feature as a method in the `VerificationAgent` class
2. Call the method in `run_full_verification()`
3. Update statistics in `self.stats`
4. Add results to the report generation
5. Update this README with documentation

### Version History

- **v1.0.0** (2024-11-04): Initial implementation with full verification suite
