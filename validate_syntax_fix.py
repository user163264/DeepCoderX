#!/usr/bin/env python3
"""
Quick syntax validation for tool_executor.py fix
"""

import sys
import ast

def validate_syntax():
    """Test that tool_executor.py has valid Python syntax."""
    
    print("🔍 Validating tool_executor.py syntax fix...")
    
    try:
        # Read the file
        with open('/Users/admin/Documents/DeepCoderX/services/tool_executor.py', 'r') as f:
            content = f.read()
        
        # Parse with AST to check syntax
        ast.parse(content)
        
        print("✅ SUCCESS: tool_executor.py syntax is now valid!")
        print("✅ The unmatched ')' error has been resolved")
        
        # Check the specific line that was problematic
        lines = content.split('\n')
        line_60 = lines[59]  # 0-indexed
        
        print(f"\n📋 Fixed line 60:")
        print(f"   {line_60.strip()}")
        
        # Count parentheses to confirm balance
        open_parens = line_60.count('(')
        close_parens = line_60.count(')')
        
        print(f"\n🔢 Parentheses count:")
        print(f"   Open: {open_parens}")
        print(f"   Close: {close_parens}")
        print(f"   Balanced: {'✅ YES' if open_parens == close_parens else '❌ NO'}")
        
        return True
        
    except SyntaxError as e:
        print(f"❌ SYNTAX ERROR: {e}")
        print(f"   Line {e.lineno}: {e.text}")
        return False
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False

if __name__ == "__main__":
    success = validate_syntax()
    sys.exit(0 if success else 1)
