#!/usr/bin/env python3
"""
Generate a detailed coverage report with file-by-file breakdown
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Tuple


def load_coverage_data(coverage_json: Path) -> Dict:
    """Load coverage data from JSON file"""
    if not coverage_json.exists():
        print(f"❌ Coverage file not found: {coverage_json}")
        sys.exit(1)
    
    with open(coverage_json) as f:
        return json.load(f)


def analyze_coverage(data: Dict) -> Tuple[List[Dict], float]:
    """Analyze coverage data and return file statistics"""
    files = []
    total_lines = 0
    covered_lines = 0
    
    for file_path, file_data in data.get("files", {}).items():
        summary = file_data.get("summary", {})
        num_statements = summary.get("num_statements", 0)
        covered = summary.get("covered_lines", 0)
        missing = summary.get("missing_lines", 0)
        
        if num_statements > 0:
            coverage_pct = (covered / num_statements) * 100
        else:
            coverage_pct = 0.0
        
        files.append({
            "path": file_path,
            "statements": num_statements,
            "covered": covered,
            "missing": missing,
            "coverage": coverage_pct
        })
        
        total_lines += num_statements
        covered_lines += covered
    
    overall_coverage = (covered_lines / total_lines * 100) if total_lines > 0 else 0.0
    
    # Sort by coverage (lowest first)
    files.sort(key=lambda x: x["coverage"])
    
    return files, overall_coverage


def print_coverage_report(files: List[Dict], overall: float):
    """Print formatted coverage report"""
    print("\n" + "="*80)
    print("📊 COVERAGE REPORT")
    print("="*80)
    
    print(f"\n{'FILE':<50} {'LINES':>8} {'COVERED':>8} {'MISSING':>8} {'COV %':>8}")
    print("-"*80)
    
    # Show files with lowest coverage first
    low_coverage = [f for f in files if f["coverage"] < 80]
    
    if low_coverage:
        print("\n⚠️  FILES WITH LOW COVERAGE (<80%):")
        for file_info in low_coverage[:20]:  # Top 20 worst
            path_short = Path(file_info["path"]).name
            if len(path_short) > 45:
                path_short = "..." + path_short[-42:]
            
            print(f"{path_short:<50} "
                  f"{file_info['statements']:>8} "
                  f"{file_info['covered']:>8} "
                  f"{file_info['missing']:>8} "
                  f"{file_info['coverage']:>7.1f}%")
    
    # Show summary
    print("\n" + "="*80)
    print("📈 SUMMARY")
    print("="*80)
    
    total_files = len(files)
    files_100 = len([f for f in files if f["coverage"] == 100])
    files_90_plus = len([f for f in files if f["coverage"] >= 90])
    files_80_plus = len([f for f in files if f["coverage"] >= 80])
    files_below_50 = len([f for f in files if f["coverage"] < 50])
    
    print(f"Total files: {total_files}")
    print(f"Files with 100% coverage: {files_100}")
    print(f"Files with ≥90% coverage: {files_90_plus}")
    print(f"Files with ≥80% coverage: {files_80_plus}")
    print(f"Files with <50% coverage: {files_below_50}")
    print(f"\n{'Overall Coverage:':<30} {overall:>6.2f}%")
    
    if overall >= 97:
        print("✅ Coverage meets 97% threshold!")
    elif overall >= 90:
        print("⚠️  Coverage above 90% but below 97% threshold")
    elif overall >= 80:
        print("⚠️  Coverage above 80% but below 97% threshold")
    else:
        print("❌ Coverage below 80%")
    
    print("="*80 + "\n")


def generate_markdown_report(files: List[Dict], overall: float, output_file: Path):
    """Generate markdown coverage report"""
    with open(output_file, 'w') as f:
        f.write("# Coverage Report\n\n")
        f.write(f"**Overall Coverage:** {overall:.2f}%\n\n")
        
        f.write("## Summary\n\n")
        total_files = len(files)
        files_100 = len([fi for fi in files if fi["coverage"] == 100])
        files_90_plus = len([fi for fi in files if fi["coverage"] >= 90])
        files_80_plus = len([fi for fi in files if fi["coverage"] >= 80])
        files_below_50 = len([fi for fi in files if fi["coverage"] < 50])
        
        f.write(f"- Total files: {total_files}\n")
        f.write(f"- Files with 100% coverage: {files_100}\n")
        f.write(f"- Files with ≥90% coverage: {files_90_plus}\n")
        f.write(f"- Files with ≥80% coverage: {files_80_plus}\n")
        f.write(f"- Files with <50% coverage: {files_below_50}\n\n")
        
        f.write("## Files Needing Attention (<80% coverage)\n\n")
        f.write("| File | Statements | Covered | Missing | Coverage |\n")
        f.write("|------|------------|---------|---------|----------|\n")
        
        low_coverage = [fi for fi in files if fi["coverage"] < 80]
        for file_info in low_coverage:
            name = Path(file_info["path"]).name
            f.write(f"| {name} | {file_info['statements']} | "
                   f"{file_info['covered']} | {file_info['missing']} | "
                   f"{file_info['coverage']:.1f}% |\n")
    
    print(f"📄 Markdown report saved to: {output_file}")


def main():
    """Main entry point"""
    root_dir = Path(__file__).parent.parent
    coverage_json = root_dir / "coverage.json"
    
    if not coverage_json.exists():
        print("❌ coverage.json not found. Run tests with coverage first:")
        print("   pytest --cov=venom --cov-report=json")
        sys.exit(1)
    
    data = load_coverage_data(coverage_json)
    files, overall = analyze_coverage(data)
    
    print_coverage_report(files, overall)
    
    # Generate markdown report
    markdown_file = root_dir / "coverage-detailed.md"
    generate_markdown_report(files, overall, markdown_file)


if __name__ == "__main__":
    main()
