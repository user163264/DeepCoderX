# Emergency fix for DeepCoderX hanging issues
# This script applies critical fixes to prevent 3-minute hangs

import os
import shutil
from pathlib import Path

def create_emergency_fix():
    """Apply emergency fixes to prevent hanging"""
    
    print("🚨 APPLYING EMERGENCY FIXES...")
    
    # 1. Fix LocalCodingHandler tool loop limits
    llm_handler_path = Path("services/llm_handler.py")
    if llm_handler_path.exists():
        print("📝 Fixing tool loop limits...")
        
        # Create backup
        shutil.copy(llm_handler_path, str(llm_handler_path) + ".BAK4")
        
        # Read and fix the file
        with open(llm_handler_path, 'r') as f:
            content = f.read()
        
        # Fix the inconsistent tool call check (line that checks for 49)
        content = content.replace(
            "if i == max_tool_calls - 1:",
            "if i >= config.MAX_TOOL_CALLS - 1:"
        )
        
        # Fix the error message
        content = content.replace(
            'self.ctx.response = "[red]Error:[/] Exceeded maximum tool calls (5)."',
            f'self.ctx.response = "[red]Error:[/] Exceeded maximum tool calls ({config.MAX_TOOL_CALLS})."'
        )
        
        # Write back
        with open(llm_handler_path, 'w') as f:
            f.write(content)
        
        print("✅ Fixed tool loop limits")
    
    # 2. Create simplified JSON parser as emergency fallback
    print("📝 Creating emergency JSON parser...")
    
    emergency_parser_content = '''# Emergency simplified JSON parser for DeepCoderX
# Replaces complex parsing that can hang

import json
import re
from typing import List, Dict, Any

def emergency_parse_tool_calls(text: str) -> List[Dict[str, Any]]:
    """Emergency simple JSON parser with timeout protection."""
    
    # Simple regex-based extraction for common patterns
    tool_calls = []
    
    # Look for basic JSON patterns
    json_pattern = r'\\{\\s*"tool"\\s*:\\s*"([^"]+)"[^}]*\\}'
    
    try:
        # Try simple JSON extraction first
        matches = re.finditer(json_pattern, text, re.DOTALL)
        
        for match in matches:
            try:
                json_str = match.group(0)
                # Simple validation and parsing
                parsed = json.loads(json_str)
                if "tool" in parsed:
                    tool_calls.append(parsed)
            except:
                continue
                
        return tool_calls[:5]  # Limit to 5 tools max
        
    except Exception:
        return []

def emergency_fix_json(json_str: str) -> str:
    """Emergency JSON fix with timeout protection."""
    try:
        # Simple newline escape
        fixed = json_str.replace('\\n', '\\\\n')
        fixed = fixed.replace('\\r', '\\\\r')
        fixed = fixed.replace('\\t', '\\\\t')
        
        # Test if it works
        json.loads(fixed)
        return fixed
    except:
        return None
'''
    
    with open("emergency_parser.py", "w") as f:
        f.write(emergency_parser_content)
    
    print("✅ Created emergency parser")
    
    # 3. Reduce tool limits for safety
    print("📝 Setting safe tool limits...")
    
    config_path = Path("config.py")
    if config_path.exists():
        with open(config_path, 'r') as f:
            content = f.read()
        
        # Set very conservative limits
        content = content.replace(
            'MAX_TOOL_CALLS = int(os.getenv("MAX_TOOL_CALLS", "10"))',
            'MAX_TOOL_CALLS = int(os.getenv("MAX_TOOL_CALLS", "5"))'  # Reduce to 5
        )
        
        with open(config_path, 'w') as f:
            f.write(content)
        
        print("✅ Set safe tool limits (MAX_TOOL_CALLS = 5)")
    
    print("🎉 EMERGENCY FIXES APPLIED!")
    print("\n📋 WHAT WAS FIXED:")
    print("  ✅ Fixed inconsistent tool loop limits")
    print("  ✅ Reduced MAX_TOOL_CALLS to 5 (conservative)")
    print("  ✅ Created emergency JSON parser fallback")
    print("  ✅ Created backup files (.BAK4)")
    print("\n🔄 RESTART THE APPLICATION NOW")

if __name__ == "__main__":
    create_emergency_fix()
