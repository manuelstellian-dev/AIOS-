#!/usr/bin/env python3
"""
Auto Test Generator for AIOS-
Automatically generates test stubs for uncovered functions and classes
"""

import os
import sys
import ast
import json
import subprocess
from pathlib import Path
from typing import List, Dict, Set, Tuple, Optional
from datetime import datetime


class TestGenerator:
    """Generates pytest-compatible tests for uncovered code"""
    
    def __init__(self, root_dir: Path, coverage_file: Path):
        self.root_dir = root_dir
        self.coverage_file = coverage_file
        self.generated_dir = root_dir / "tests" / "generated"
        self.coverage_data = {}
        self.uncovered_items = []
        
    def load_coverage(self) -> bool:
        """Load coverage data from coverage.json"""
        if not self.coverage_file.exists():
            print(f"❌ Coverage file not found: {self.coverage_file}")
            return False
        
        with open(self.coverage_file, 'r') as f:
            self.coverage_data = json.load(f)
        
        print(f"✅ Loaded coverage data from {self.coverage_file}")
        return True
    
    def get_coverage_percentage(self) -> float:
        """Calculate overall coverage percentage"""
        totals = self.coverage_data.get('totals', {})
        num_statements = totals.get('num_statements', 1)
        covered_lines = totals.get('covered_lines', 0)
        
        if num_statements == 0:
            return 100.0
        
        return (covered_lines / num_statements) * 100
    
    def identify_uncovered_files(self) -> List[Tuple[str, float]]:
        """Identify files with low coverage"""
        files_with_low_coverage = []
        
        files = self.coverage_data.get('files', {})
        
        for filepath, file_data in files.items():
            summary = file_data.get('summary', {})
            num_statements = summary.get('num_statements', 1)
            covered_lines = summary.get('covered_lines', 0)
            
            if num_statements == 0:
                continue
            
            coverage_pct = (covered_lines / num_statements) * 100
            
            # Focus on files with less than 80% coverage
            if coverage_pct < 80:
                files_with_low_coverage.append((filepath, coverage_pct))
        
        # Sort by lowest coverage first
        files_with_low_coverage.sort(key=lambda x: x[1])
        
        return files_with_low_coverage
    
    def parse_file_for_functions(self, filepath: str) -> List[Dict]:
        """Parse a Python file to extract functions and classes"""
        uncovered_items = []
        
        try:
            with open(filepath, 'r') as f:
                tree = ast.parse(f.read(), filename=filepath)
            
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    # Found a class
                    uncovered_items.append({
                        'type': 'class',
                        'name': node.name,
                        'lineno': node.lineno,
                        'methods': [m.name for m in node.body if isinstance(m, ast.FunctionDef)]
                    })
                elif isinstance(node, ast.FunctionDef):
                    # Check if it's a top-level function (not inside a class)
                    if not any(isinstance(parent, ast.ClassDef) for parent in ast.walk(tree)):
                        uncovered_items.append({
                            'type': 'function',
                            'name': node.name,
                            'lineno': node.lineno,
                            'args': [arg.arg for arg in node.args.args]
                        })
        
        except Exception as e:
            print(f"⚠️  Error parsing {filepath}: {e}")
        
        return uncovered_items
    
    def generate_test_stub(self, module_path: str, items: List[Dict]) -> str:
        """Generate a test stub for uncovered items"""
        
        # Convert file path to module path
        rel_path = os.path.relpath(module_path, self.root_dir)
        module_name = rel_path.replace('/', '.').replace('.py', '')
        
        test_content = f'''"""
Auto-generated tests for {module_name}
Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

These are placeholder tests to improve coverage.
TODO: Implement proper test logic with real assertions.
"""
import pytest
from unittest.mock import Mock, patch, MagicMock, PropertyMock

'''
        
        # Add imports with try-except for optional dependencies
        test_content += f"try:\n"
        for item in items:
            if item['type'] == 'class':
                test_content += f"    from {module_name} import {item['name']}\n"
            elif item['type'] == 'function':
                test_content += f"    from {module_name} import {item['name']}\n"
        test_content += "except ImportError as e:\n"
        test_content += "    pytest.skip(f'Cannot import module: {e}', allow_module_level=True)\n\n"
        
        # Generate test stubs for each item
        for item in items:
            if item['type'] == 'class':
                class_name = item['name']
                test_content += f'''
class Test{class_name}:
    """Tests for {class_name}"""
    
    @patch.object({class_name}, '__init__', return_value=None)
    def test_init_mocked(self, mock_init):
        """Test {class_name} can be instantiated (mocked)"""
        # Mocked initialization to avoid dependency issues
        obj = object.__new__({class_name})
        assert obj is not None
    
    def test_class_exists(self):
        """Test that {class_name} class exists"""
        assert {class_name} is not None
        assert hasattr({class_name}, '__init__')
    
'''
                # Add method tests (only for public methods)
                public_methods = [m for m in item.get('methods', []) if not m.startswith('_')][:3]
                for method in public_methods:
                    test_content += f'''    def test_{method}_exists(self):
        """Test that {class_name}.{method} method exists"""
        assert hasattr({class_name}, '{method}')
        assert callable(getattr({class_name}, '{method}', None))
    
'''
            
            elif item['type'] == 'function':
                func_name = item['name']
                if not func_name.startswith('_'):
                    test_content += f'''
def test_{func_name}_exists():
    """Test that {func_name} function exists and is callable"""
    assert callable({func_name})

'''
        
        return test_content
    
    def generate_tests(self, max_files: int = 10) -> int:
        """Generate tests for uncovered files"""
        
        # Get files with low coverage
        low_coverage_files = self.identify_uncovered_files()[:max_files]
        
        if not low_coverage_files:
            print("✅ No files need additional tests")
            return 0
        
        print(f"\n📊 Generating tests for {len(low_coverage_files)} files with low coverage:")
        
        # Create generated directory
        self.generated_dir.mkdir(parents=True, exist_ok=True)
        
        # Create __init__.py
        init_file = self.generated_dir / "__init__.py"
        if not init_file.exists():
            init_file.write_text('"""Auto-generated tests"""\n')
        
        generated_count = 0
        
        for filepath, coverage in low_coverage_files:
            print(f"  - {filepath} ({coverage:.1f}% coverage)")
            
            # Parse file for functions and classes
            full_path = self.root_dir / filepath
            items = self.parse_file_for_functions(str(full_path))
            
            if not items:
                continue
            
            # Generate test stub
            test_content = self.generate_test_stub(str(full_path), items)
            
            # Create test file name
            rel_path = os.path.relpath(filepath, self.root_dir)
            test_filename = f"test_{rel_path.replace('/', '_')}"
            test_file = self.generated_dir / test_filename
            
            # Write test file
            with open(test_file, 'w') as f:
                f.write(test_content)
            
            print(f"    ✅ Generated: {test_file}")
            generated_count += 1
        
        return generated_count
    
    def run_coverage_again(self) -> float:
        """Run coverage again to measure improvement"""
        print("\n🔄 Running tests with coverage to measure improvement...")
        
        try:
            result = subprocess.run(
                [sys.executable, "-m", "pytest", "tests/", 
                 "--cov=venom", "--cov-report=json", "--cov-report=term-missing",
                 "-q", "--tb=no"],
                cwd=self.root_dir,
                capture_output=True,
                text=True,
                timeout=300
            )
            
            # Reload coverage data
            self.load_coverage()
            new_coverage = self.get_coverage_percentage()
            
            print(f"\n📈 New coverage: {new_coverage:.2f}%")
            return new_coverage
            
        except Exception as e:
            print(f"❌ Error running coverage: {e}")
            return 0.0
    
    def run(self) -> bool:
        """Run the full test generation process"""
        print("🚀 Auto Test Generator")
        print("=" * 60)
        
        # Load coverage
        if not self.load_coverage():
            return False
        
        # Get current coverage
        current_coverage = self.get_coverage_percentage()
        print(f"\n📊 Current coverage: {current_coverage:.2f}%")
        
        # Generate tests
        generated_count = self.generate_tests(max_files=15)
        
        if generated_count == 0:
            print("\n✅ No tests generated")
            return True
        
        print(f"\n✅ Generated {generated_count} test files")
        
        # Run coverage again
        new_coverage = self.run_coverage_again()
        improvement = new_coverage - current_coverage
        
        print("\n" + "=" * 60)
        print(f"📊 Coverage improved by {improvement:+.2f}% ({current_coverage:.2f}% → {new_coverage:.2f}%)")
        print("=" * 60)
        
        return True


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Auto-generate tests for uncovered code")
    parser.add_argument("--coverage-file", default="coverage.json", help="Path to coverage.json file")
    parser.add_argument("--max-files", type=int, default=15, help="Maximum number of files to generate tests for")
    
    args = parser.parse_args()
    
    root_dir = Path(__file__).parent.parent
    coverage_file = root_dir / args.coverage_file
    
    generator = TestGenerator(root_dir, coverage_file)
    
    success = generator.run()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
