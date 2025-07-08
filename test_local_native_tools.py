#!/usr/bin/env python3
"""
Test script to validate native OpenAI function calling for local models.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from pathlib import Path
from config import config
from models.session import CommandContext
from services.unified_openai_handler import LocalOpenAIHandler
from services.mcpclient import MCPClient
from services.tool_registry import get_tools_for_provider

def test_local_native_tools():
    """Test that local models use native OpenAI function calling."""
    
    print("🔧 Testing Local Model Native OpenAI Function Calling")
    print("=" * 60)
    
    # Test 1: Configuration Check
    print("\n1. Configuration Check:")
    local_config = config.PROVIDERS.get("local")
    print(f"   Local model enabled: {local_config['enabled']}")
    print(f"   Supports tools: {local_config['supports_tools']}")
    
    if not local_config['supports_tools']:
        print("   ❌ ERROR: Local model should have supports_tools=True")
        return False
    else:
        print("   ✅ Local model configured for native tool calling")
    
    # Test 2: Tool Registry Check
    print("\n2. Tool Registry Check:")
    try:
        tools = get_tools_for_provider("local", local_config)
        print(f"   Available tools: {len(tools)}")
        for tool in tools:
            print(f"     - {tool['function']['name']}")
        
        if len(tools) == 0:
            print("   ❌ ERROR: No tools available for local model")
            return False
        else:
            print("   ✅ Local model has access to tools")
    except Exception as e:
        print(f"   ❌ ERROR: Failed to get tools: {e}")
        return False
    
    # Test 3: System Prompt Check
    print("\n3. System Prompt Check:")
    system_prompt = config.LOCAL_SYSTEM_PROMPT
    if '{"tool"' in system_prompt:
        print("   ❌ ERROR: System prompt still contains JSON format instructions")
        print("   Should use native function calling, not JSON format")
        return False
    elif "native function calling" in system_prompt:
        print("   ✅ System prompt mentions native function calling")
    else:
        print("   ⚠️  System prompt doesn't mention function calling format")
    
    # Test 4: Handler Implementation Check
    print("\n4. Handler Implementation Check:")
    try:
        # Create a mock context
        root_path = Path.cwd()
        mcp_client = MCPClient(timeout=10)
        
        context = CommandContext(
            user_input="list the files in the current directory",
            root_path=root_path,
            mcp_client=mcp_client,
            debug_mode=True
        )
        
        # Create handler
        handler = LocalOpenAIHandler(context)
        
        # Check if handler inherits native tool calling
        has_legacy_override = hasattr(handler, '_conversation_loop') and \
                            handler._conversation_loop.__qualname__ == 'LocalOpenAIHandler._conversation_loop'
        
        if has_legacy_override:
            print("   ❌ ERROR: LocalOpenAIHandler still has legacy tool calling override")
            return False
        else:
            print("   ✅ LocalOpenAIHandler uses parent class native tool calling")
            
    except Exception as e:
        print(f"   ❌ ERROR: Failed to create handler: {e}")
        return False
    
    # Test 5: Tool Definitions Format Check
    print("\n5. Tool Definitions Format Check:")
    try:
        # Check that tools are in OpenAI format
        sample_tool = tools[0] if tools else None
        if not sample_tool:
            print("   ❌ ERROR: No tools to check format")
            return False
        
        # Check OpenAI format structure
        required_keys = ['type', 'function']
        function_keys = ['name', 'description', 'parameters']
        
        if not all(key in sample_tool for key in required_keys):
            print("   ❌ ERROR: Tool definition missing required keys")
            return False
        
        if not all(key in sample_tool['function'] for key in function_keys):
            print("   ❌ ERROR: Tool function definition missing required keys")
            return False
        
        print("   ✅ Tool definitions are in correct OpenAI format")
        
    except Exception as e:
        print(f"   ❌ ERROR: Failed to check tool format: {e}")
        return False
    
    print("\n" + "=" * 60)
    print("🎉 All tests passed! Local model is configured for native OpenAI function calling.")
    print("\nNext steps:")
    print("1. Start the app: python app.py")
    print("2. Test with: 'list the files in the current dir'")
    print("3. The model should use native tool calls, not JSON format")
    
    return True

if __name__ == "__main__":
    success = test_local_native_tools()
    sys.exit(0 if success else 1)
