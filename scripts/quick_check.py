#!/usr/bin/env python3
"""
Quick verification script for rapid development feedback
Performs basic checks without full test suite
"""

import sys
import subprocess
from pathlib import Path


def run_command(cmd, description):
    """Run a command and report results"""
    print(f"\n{'='*60}")
    print(f"🔍 {description}")
    print(f"{'='*60}")
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode == 0:
        print(f"✅ {description} - PASSED")
        if result.stdout:
            print(result.stdout)
        return True
    else:
        print(f"❌ {description} - FAILED")
        if result.stderr:
            print(result.stderr)
        if result.stdout:
            print(result.stdout)
        return False


def main():
    """Run quick checks"""
    root_dir = Path(__file__).parent.parent
    
    print("\n" + "="*60)
    print("🚀 AIOS- Quick Check")
    print("="*60)
    
    checks = []
    
    # Check 1: Python syntax
    checks.append(run_command(
        [sys.executable, "-m", "py_compile"] + 
        [str(f) for f in root_dir.glob("venom/**/*.py")],
        "Python Syntax Check"
    ))
    
    # Check 2: Import verification
    checks.append(run_command(
        [sys.executable, "-c", "from venom import Arbiter; print('✓ Main imports OK')"],
        "Import Check"
    ))
    
    # Check 3: Quick test
    checks.append(run_command(
        [sys.executable, "-m", "pytest", "tests/test_ledger.py", "-v", "--tb=short"],
        "Quick Test (Ledger)"
    ))
    
    # Summary
    print("\n" + "="*60)
    print("📊 SUMMARY")
    print("="*60)
    passed = sum(checks)
    total = len(checks)
    print(f"Checks passed: {passed}/{total}")
    
    if passed == total:
        print("✅ All quick checks passed!")
        sys.exit(0)
    else:
        print("❌ Some checks failed. Run full verification for details:")
        print("   python scripts/verification_agent.py")
        sys.exit(1)


if __name__ == "__main__":
    main()
