#!/usr/bin/env python3
"""
Simple syntax test to validate the fixes.
"""

import sys
import os
import ast

def check_syntax(file_path):
    """Check if a Python file has valid syntax."""
    try:
        with open(file_path, 'r') as f:
            content = f.read()
        
        # Try to parse the AST
        ast.parse(content)
        print(f"✅ {file_path} - Syntax is valid")
        return True
    except SyntaxError as e:
        print(f"❌ {file_path} - Syntax error on line {e.lineno}: {e.msg}")
        return False
    except Exception as e:
        print(f"⚠️ {file_path} - Error checking syntax: {e}")
        return False

if __name__ == "__main__":
    files_to_check = [
        "services/tool_executor.py",
        "services/structured_tools.py",
        "config.py"
    ]
    
    print("🔍 Checking syntax of fixed files...\n")
    
    all_good = True
    for file_path in files_to_check:
        if os.path.exists(file_path):
            if not check_syntax(file_path):
                all_good = False
        else:
            print(f"⚠️ {file_path} - File not found")
            all_good = False
    
    if all_good:
        print("\n🎉 All files have valid syntax! The startup error should be fixed.")
    else:
        print("\n❌ Some files still have syntax errors that need to be fixed.")
