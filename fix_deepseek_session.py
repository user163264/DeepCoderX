#!/usr/bin/env python3
"""
Fix DeepSeek session file to comply with OpenAI tool calling standards.
The session file has malformed tool messages without preceding tool_calls.
"""

import json
import os
from pathlib import Path

def fix_deepseek_session():
    """Fix the malformed DeepSeek session file."""
    session_file = Path("/Users/admin/Documents/DeepCoderX/.deepcoderx/deepseek_session.json")
    
    if not session_file.exists():
        print("❌ DeepSeek session file not found")
        return
    
    # Create backup
    backup_file = session_file.with_suffix('.json.BAK')
    if session_file.exists():
        print(f"📁 Creating backup: {backup_file}")
        with open(session_file, 'r') as src, open(backup_file, 'w') as dst:
            dst.write(src.read())
    
    try:
        # Read current session
        with open(session_file, 'r') as f:
            messages = json.load(f)
        
        print(f"📊 Original messages: {len(messages)}")
        
        # Validate OpenAI format and fix issues
        fixed_messages = []
        i = 0
        while i < len(messages):
            msg = messages[i]
            
            # Keep system and user messages as-is
            if msg['role'] in ['system', 'user']:
                fixed_messages.append(msg)
                i += 1
                continue
            
            # Handle assistant messages
            if msg['role'] == 'assistant':
                # Check if this assistant message has tool_calls
                if 'tool_calls' in msg and msg['tool_calls']:
                    # Valid assistant with tool calls - keep it
                    fixed_messages.append(msg)
                    i += 1
                    
                    # Collect matching tool messages
                    tool_call_ids = {tc['id'] for tc in msg['tool_calls']}
                    while i < len(messages) and messages[i]['role'] == 'tool':
                        tool_msg = messages[i]
                        if tool_msg.get('tool_call_id') in tool_call_ids:
                            fixed_messages.append(tool_msg)
                        else:
                            print(f"⚠️  Skipping orphaned tool message: {tool_msg.get('tool_call_id')}")
                        i += 1
                else:
                    # Regular assistant message without tools
                    fixed_messages.append(msg)
                    i += 1
            
            # Skip orphaned tool messages (without preceding tool_calls)
            elif msg['role'] == 'tool':
                print(f"⚠️  Skipping orphaned tool message: {msg.get('tool_call_id')}")
                i += 1
            
            else:
                # Unknown role - keep it
                fixed_messages.append(msg)
                i += 1
        
        print(f"📊 Fixed messages: {len(fixed_messages)}")
        
        # Validate the fixed conversation
        validation_errors = validate_conversation(fixed_messages)
        if validation_errors:
            print("❌ Validation errors after fix:")
            for error in validation_errors:
                print(f"   {error}")
            return False
        
        # Write fixed session
        with open(session_file, 'w') as f:
            json.dump(fixed_messages, f, indent=2)
        
        print("✅ DeepSeek session fixed and validated!")
        print("🔧 Next: Test with '@deepseek how are you today?'")
        return True
        
    except Exception as e:
        print(f"❌ Error fixing session: {e}")
        return False

def validate_conversation(messages):
    """Validate conversation follows OpenAI tool calling standards."""
    errors = []
    
    for i, msg in enumerate(messages):
        if msg['role'] == 'tool':
            # Tool message must have tool_call_id
            if 'tool_call_id' not in msg:
                errors.append(f"Message {i}: tool message missing tool_call_id")
                continue
                
            # Find preceding assistant message with tool_calls
            tool_call_id = msg['tool_call_id']
            found_matching_call = False
            
            # Look backwards for assistant with tool_calls
            for j in range(i-1, -1, -1):
                if messages[j]['role'] == 'assistant' and 'tool_calls' in messages[j]:
                    tool_call_ids = {tc['id'] for tc in messages[j]['tool_calls']}
                    if tool_call_id in tool_call_ids:
                        found_matching_call = True
                        break
                elif messages[j]['role'] == 'user':
                    # Stop searching if we hit a user message
                    break
            
            if not found_matching_call:
                errors.append(f"Message {i}: tool message {tool_call_id} has no matching tool_calls")
    
    return errors

if __name__ == "__main__":
    print("🔧 Fixing DeepSeek session file for OpenAI compliance...")
    fix_deepseek_session()
