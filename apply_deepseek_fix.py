#!/usr/bin/env python3
"""
Apply DeepSeek System Prompt Fix

This script directly applies the fix to the overly aggressive DeepSeek system prompt.
"""

import re
from pathlib import Path

def apply_deepseek_fix():
    """Apply the DeepSeek system prompt fix."""
    config_file = Path('/Users/admin/Documents/DeepCoderX/config_module.py')
    
    # Create backup
    backup_file = config_file.with_suffix('.py.BAK_DEEPSEEK_FIX')
    if not backup_file.exists():
        backup_file.write_text(config_file.read_text())
        print(f"✅ Backup created: {backup_file}")
    
    # Read current content
    content = config_file.read_text()
    
    # New improved system prompt
    new_prompt = '''"""You are an expert software architect and coding assistant. Your goal is to provide helpful, accurate responses.

**Response Guidelines:**
- Answer questions directly using your knowledge when possible
- Only use tools when the user specifically requests file operations or codebase analysis
- For general programming questions, explanations, or discussions, respond without tools
- When tools are needed, use them efficiently and explain what you're doing

**Appropriate Tool Usage:**
- User asks to read, write, or analyze specific files
- User requests directory listings or file operations  
- User asks for code implementation requiring file creation
- User explicitly requests codebase analysis or project review

**Avoid Tools For:**
- General programming questions or explanations
- Code review discussions
- Debugging help
- Conversational responses
- Questions answerable with your existing knowledge

You have access to file system tools when appropriate."""'''
    
    # Find and replace the DEEPSEEK_SYSTEM_PROMPT section using regex
    pattern = r'(self\.DEEPSEEK_SYSTEM_PROMPT = self\._get_str_env\(\s*"DEEPCODERX_DEEPSEEK_SYSTEM_PROMPT",\s*)""".*?"""'
    
    replacement = f'\\g<1>{new_prompt}'
    
    new_content = re.sub(pattern, replacement, content, flags=re.DOTALL)
    
    if new_content != content:
        config_file.write_text(new_content)
        print("✅ DeepSeek system prompt fixed!")
        print("🔄 Restart DeepCoderX to apply changes")
        return True
    else:
        print("❌ Could not find or replace DEEPSEEK_SYSTEM_PROMPT")
        return False

if __name__ == "__main__":
    apply_deepseek_fix()
