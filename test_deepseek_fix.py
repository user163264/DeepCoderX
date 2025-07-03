#!/usr/bin/env python3
"""
Test script to validate DeepSeek tool message fix
"""

import sys
import os
sys.path.append('/Users/admin/Documents/DeepCoderX')

import json
from pathlib import Path
from models.session import CommandContext
from services.unified_openai_handler import CloudOpenAIHandler

def test_deepseek_clean_session():
    """Test that DeepSeek starts with clean session without tool message errors."""
    
    print("=== DeepSeek Clean Session Test ===")
    
    # Create test context
    class MockMCPClient:
        def read_file(self, path):
            return {"content": f"Mock content for {path}"}
    
    context = CommandContext()
    context.user_input = "@deepseek hello there!"
    context.debug_mode = True
    context.root_path = Path('/Users/admin/Documents/DeepCoderX')
    context.mcp_client = MockMCPClient()
    
    try:
        # Initialize CloudOpenAIHandler for DeepSeek
        print("1. Initializing CloudOpenAIHandler for DeepSeek...")
        handler = CloudOpenAIHandler(context, "deepseek")
        
        print("2. Checking message history...")
        print(f"   Message count: {len(handler.message_history)}")
        
        # Validate no tool messages without proper tool_calls
        tool_issues = []
        for i, message in enumerate(handler.message_history):
            if message.get("role") == "tool":
                if i == 0 or handler.message_history[i-1].get("role") != "assistant" or "tool_calls" not in handler.message_history[i-1]:
                    tool_issues.append(f"Message {i}: Tool message without proper tool_calls")
        
        if tool_issues:
            print("❌ FAILED: Found tool message issues:")
            for issue in tool_issues:
                print(f"   - {issue}")
            return False
        else:
            print("✅ PASSED: No tool message format issues found")
        
        print("3. Checking session file content...")
        session_file = Path('/Users/admin/Documents/DeepCoderX/.deepcoderx/deepseek_session.json')
        if session_file.exists():
            with open(session_file, 'r') as f:
                session_data = json.load(f)
            print(f"   Session file has {len(session_data)} messages")
            
            # Check for tool issues in session file
            session_tool_issues = []
            for i, message in enumerate(session_data):
                if message.get("role") == "tool":
                    if i == 0 or session_data[i-1].get("role") != "assistant" or "tool_calls" not in session_data[i-1]:
                        session_tool_issues.append(f"Session message {i}: Tool message without proper tool_calls")
            
            if session_tool_issues:
                print("❌ FAILED: Found tool message issues in session file:")
                for issue in session_tool_issues:
                    print(f"   - {issue}")
                return False
            else:
                print("✅ PASSED: Session file has no tool message format issues")
        
        print("4. Testing provider configuration...")
        print(f"   Provider name: {handler.provider_name}")
        print(f"   Provider enabled: {handler.provider_config.get('enabled', False)}")
        print(f"   Supports tools: {handler.provider_config.get('supports_tools', False)}")
        
        print("\n🎉 ALL TESTS PASSED!")
        print("DeepSeek handler should now work without tool message format errors.")
        
        return True
        
    except Exception as e:
        print(f"❌ FAILED: Exception during test: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_deepseek_clean_session()
    sys.exit(0 if success else 1)
