# Quick Start: Verification System

## 🚀 Quick Commands

### During Development (Fast)
```bash
python scripts/quick_check.py
```
**Takes:** ~10-30 seconds  
**Checks:** Syntax, imports, quick test

### Before Commit (Standard)
```bash
python scripts/verification_agent.py --coverage-threshold 75
```
**Takes:** ~2-5 minutes  
**Checks:** All tests + coverage

### Before PR (Complete)
```bash
python scripts/verification_agent.py --full-check
```
**Takes:** ~5-15 minutes  
**Checks:** Everything + static analysis + test generation

### View Coverage Details
```bash
pytest --cov=venom --cov-report=json
python scripts/coverage_report.py
```

## 📊 Coverage Target

**Target:** 97% code coverage

## 🔧 Installation

All dependencies are installed automatically by the verification agent.

Manual installation:
```bash
pip install -r requirements.txt
pip install pytest pytest-cov pytest-asyncio coverage
```

## 📁 Output Files

| File | Description |
|------|-------------|
| `verification-report.md` | Summary report |
| `coverage.xml` | Coverage data (XML) |
| `htmlcov/` | Interactive coverage browser |
| `coverage.json` | Coverage data (JSON) |

## 🔍 What Gets Checked

- ✅ Python syntax (AST parsing)
- ✅ Import statements
- ✅ All unit tests
- ✅ Code coverage
- ✅ Static analysis (with --full-check)
  - flake8 (style)
  - pylint (quality)
  - mypy (types)
  - bandit (security)

## 🤖 CI/CD Integration

The verification runs automatically on:
- ✅ Push to main/develop/master
- ✅ Pull requests
- ✅ Python 3.9, 3.10, 3.11

## 📖 Full Documentation

- **Usage Guide:** `scripts/README.md`
- **System Overview:** `docs/VERIFICATION_SYSTEM.md`
- **Implementation Details:** `IMPLEMENTATION_SUMMARY.md`

## ⚡ Tips

1. **Run quick_check.py frequently** - catches issues early
2. **Use lower threshold during development** - `--coverage-threshold 70`
3. **Review coverage HTML** - `open htmlcov/index.html`
4. **Let CI/CD handle full checks** - no need to run locally every time

## 🆘 Troubleshooting

### Tests fail with import errors
```bash
pip install -r requirements.txt
```

### Coverage too low
```bash
# Review what's not covered
open htmlcov/index.html

# Lower threshold temporarily
python scripts/verification_agent.py --coverage-threshold 70
```

### Static analysis errors
```bash
# Auto-format code
pip install black
black venom/

# Check specific issues
flake8 venom/
```

## 📞 Support

- Check documentation in `scripts/README.md` and `docs/VERIFICATION_SYSTEM.md`
- Review existing GitHub issues
- Create new issue with detailed logs

---

**Version:** 1.0.0  
**Last Updated:** 2024-11-04
