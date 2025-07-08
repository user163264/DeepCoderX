#!/usr/bin/env python3
"""
Quick syntax check for GGUF implementation files.
"""

import ast
import sys
from pathlib import Path

def check_syntax(file_path):
    """Check syntax of a Python file."""
    try:
        with open(file_path, 'r') as f:
            source = f.read()
        
        # Try to parse the AST
        ast.parse(source)
        return True, None
    except SyntaxError as e:
        return False, f"Syntax error: {e}"
    except Exception as e:
        return False, f"Error: {e}"

def main():
    """Check syntax of all GGUF files."""
    project_root = Path(__file__).parent
    
    gguf_files = [
        'services/gguf_tool_prompt.py',
        'services/gguf_tool_parser.py',
        'services/gguf_context_manager.py',
        'services/gguf_handler.py'
    ]
    
    all_good = True
    
    print("🔍 Checking GGUF implementation syntax...")
    
    for file_path in gguf_files:
        full_path = project_root / file_path
        if full_path.exists():
            is_valid, error = check_syntax(full_path)
            if is_valid:
                print(f"✅ {file_path}")
            else:
                print(f"❌ {file_path}: {error}")
                all_good = False
        else:
            print(f"❌ {file_path}: File not found")
            all_good = False
    
    if all_good:
        print("\n🎉 All GGUF files have valid syntax!")
        return True
    else:
        print("\n❌ Some files have syntax errors. Please fix them.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
