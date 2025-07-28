#!/usr/bin/env python3
"""
Test syntax compilation of all Python files.
"""

import ast
import sys
from pathlib import Path

def test_syntax(file_path):
    """Test if a Python file has valid syntax."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Try to parse the AST
        ast.parse(content, filename=str(file_path))
        return True, None
        
    except SyntaxError as e:
        return False, f"Syntax Error: {e}"
    except Exception as e:
        return False, f"Error: {e}"

def main():
    """Check syntax of all Python files in the project."""
    project_root = Path.cwd()
    python_files = list(project_root.rglob("*.py"))
    
    print(f"=== Checking syntax of {len(python_files)} Python files ===")
    
    failed_files = []
    
    for py_file in python_files:
        # Skip __pycache__ and .venv directories
        if "__pycache__" in str(py_file) or ".venv" in str(py_file) or "VENV" in str(py_file):
            continue
            
        print(f"Checking {py_file.relative_to(project_root)}...", end=" ")
        
        success, error = test_syntax(py_file)
        
        if success:
            print("✅")
        else:
            print("❌")
            print(f"  Error: {error}")
            failed_files.append((py_file, error))
    
    print(f"\n=== SUMMARY ===")
    if failed_files:
        print(f"❌ {len(failed_files)} files failed syntax check:")
        for file_path, error in failed_files:
            print(f"  {file_path.relative_to(project_root)}: {error}")
        return False
    else:
        print("✅ All files passed syntax check!")
        return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
