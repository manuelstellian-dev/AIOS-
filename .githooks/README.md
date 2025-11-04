# Git Hooks for VENOM Framework

This directory contains Git hooks to maintain enterprise-grade code quality.

## Pre-commit Hook

The `pre-commit` hook runs automatically before each commit to ensure code meets quality standards.

### Installation

To enable the pre-commit hook:

```bash
# Set Git to use this hooks directory
git config core.hooksPath .githooks

# Verify it's set correctly
git config core.hooksPath
```

### What It Does

The pre-commit hook:
1. Runs comprehensive verification with 97% coverage requirement
2. Checks code syntax
3. Validates imports
4. Runs all tests
5. Verifies coverage meets 97% threshold
6. Reports any quality issues

### Bypassing the Hook (Not Recommended)

If you absolutely must commit without passing the checks (e.g., work-in-progress):

```bash
git commit --no-verify -m "WIP: Your message"
```

⚠️ **Warning:** This should only be used for temporary branches, never for main/develop.

### Manual Verification

You can run the verification manually at any time:

```bash
# Quick check
python scripts/verification_agent.py --coverage-threshold 97

# Full check with static analysis
python scripts/verification_agent.py --full-check --coverage-threshold 97
```

### Troubleshooting

**Issue: Hook doesn't run**
```bash
# Re-configure the hooks path
git config core.hooksPath .githooks

# Make sure the hook is executable
chmod +x .githooks/pre-commit
```

**Issue: Hook fails with coverage below 97%**
```bash
# Generate missing tests
python scripts/auto_generate_tests.py --max-files 20

# Run tests to see what's missing coverage
pytest --cov=venom --cov-report=html
open htmlcov/index.html  # View coverage report
```

**Issue: Hook fails with import errors**
```bash
# Install all dependencies
pip install -r requirements.txt
```

### Enterprise Standards

- ✅ **97% coverage is mandatory** - No exceptions
- ✅ **All checks must pass** - No `--no-verify` commits to main branches
- ✅ **Quality is non-negotiable** - Enterprise-grade standards

### Support

For questions or issues:
- Check [QUALITY_ASSURANCE.md](../QUALITY_ASSURANCE.md)
- Check [VERIFICATION_PLAN.md](../VERIFICATION_PLAN.md)
- Create an issue on GitHub
