#!/usr/bin/env python3
"""
Simple validation of DeepSeek session clean state
"""

import json
from pathlib import Path

def check_deepseek_session():
    """Check if DeepSeek session is in clean state."""
    
    session_file = Path('/Users/admin/Documents/DeepCoderX/.deepcoderx/deepseek_session.json')
    
    print("=== DeepSeek Session Validation ===")
    
    if not session_file.exists():
        print("❌ DeepSeek session file does not exist")
        return False
    
    try:
        with open(session_file, 'r') as f:
            session_data = json.load(f)
        
        print(f"✅ Session file loaded successfully")
        print(f"   Messages in session: {len(session_data)}")
        
        # Check for tool message issues
        tool_issues = []
        for i, message in enumerate(session_data):
            role = message.get("role", "unknown")
            print(f"   Message {i}: role='{role}'")
            
            if role == "tool":
                # Check if previous message has tool_calls
                if i == 0:
                    tool_issues.append(f"Message {i}: Tool message at start of conversation")
                elif session_data[i-1].get("role") != "assistant":
                    tool_issues.append(f"Message {i}: Tool message not following assistant message")
                elif "tool_calls" not in session_data[i-1]:
                    tool_issues.append(f"Message {i}: Tool message without preceding tool_calls")
        
        if tool_issues:
            print("❌ FOUND TOOL MESSAGE ISSUES:")
            for issue in tool_issues:
                print(f"   - {issue}")
            return False
        else:
            print("✅ NO TOOL MESSAGE ISSUES FOUND")
            
        # Check if session starts with system message
        if not session_data or session_data[0].get("role") != "system":
            print("❌ Session does not start with system message")
            return False
        else:
            print("✅ Session starts with proper system message")
        
        print("\n🎉 DEEPSEEK SESSION IS CLEAN!")
        return True
        
    except json.JSONDecodeError as e:
        print(f"❌ JSON decode error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

if __name__ == "__main__":
    success = check_deepseek_session()
    print(f"\nResult: {'PASS' if success else 'FAIL'}")
