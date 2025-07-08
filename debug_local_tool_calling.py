#!/usr/bin/env python3
"""
Debug script to investigate local model tool calling behavior.
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

def debug_local_tool_calling():
    """Debug local model tool calling to understand the issue."""
    
    print("🔍 Debugging Local Model Tool Calling")
    print("=" * 50)
    
    # 1. Check what tools are being sent to the model
    print("\n1. Tool Definitions Being Sent to Model:")
    try:
        local_config = config.PROVIDERS["local"]
        tools = get_tools_for_provider("local", local_config)
        
        print(f"   Number of tools: {len(tools)}")
        print(f"   supports_tools: {local_config['supports_tools']}")
        
        if tools:
            print("   First tool definition:")
            import json
            print(json.dumps(tools[0], indent=4))
        else:
            print("   ❌ No tools available!")
            
    except Exception as e:
        print(f"   ❌ Error getting tools: {e}")
    
    # 2. Check system prompt
    print("\n2. System Prompt Analysis:")
    prompt = config.LOCAL_SYSTEM_PROMPT
    print(f"   Length: {len(prompt)} characters")
    
    # Check for problematic patterns
    has_json_instructions = '{"tool"' in prompt
    has_native_mention = "native function calling" in prompt
    has_tool_format = "TOOL FORMAT" in prompt
    
    print(f"   Contains JSON instructions: {has_json_instructions}")
    print(f"   Mentions native function calling: {has_native_mention}")
    print(f"   Has TOOL FORMAT section: {has_tool_format}")
    
    if has_json_instructions:
        print("   ⚠️  System prompt still contains JSON format instructions!")
    
    # 3. Test a simple API call to see what the model returns
    print("\n3. Testing Direct API Call:")
    try:
        from openai import OpenAI
        
        client = OpenAI(
            api_key=local_config["api_key"],
            base_url=local_config["base_url"]
        )
        
        # Test if the model actually supports function calling
        messages = [
            {"role": "system", "content": "You are a helpful assistant. Use the provided tools when needed."},
            {"role": "user", "content": "List files in the current directory"}
        ]
        
        # Try with tools
        response = client.chat.completions.create(
            model=local_config["model"],
            messages=messages,
            tools=tools[:1] if tools else [],  # Just send one tool for testing
            tool_choice="auto"
        )
        
        message = response.choices[0].message
        print(f"   Response content: {message.content}")
        print(f"   Has tool_calls: {hasattr(message, 'tool_calls') and message.tool_calls}")
        
        if hasattr(message, 'tool_calls') and message.tool_calls:
            print("   ✅ Model made native function calls!")
            for tool_call in message.tool_calls:
                print(f"     - {tool_call.function.name}: {tool_call.function.arguments}")
        else:
            print("   ❌ Model did not make native function calls")
            print("   💡 This suggests the model doesn't support OpenAI function calling")
            
    except Exception as e:
        print(f"   ❌ Error testing API: {e}")
    
    # 4. Check if model supports function calling at all
    print("\n4. Model Capability Analysis:")
    try:
        # Try without tools to see baseline behavior
        response_no_tools = client.chat.completions.create(
            model=local_config["model"],
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "List files in the current directory"}
            ]
        )
        
        no_tools_content = response_no_tools.choices[0].message.content
        print(f"   Response without tools: {no_tools_content[:100]}...")
        
        # Check if model mentions tools even without being given any
        mentions_tools = "tool" in no_tools_content.lower()
        print(f"   Mentions tools without being given any: {mentions_tools}")
        
        if mentions_tools:
            print("   💡 Model was likely trained with tool calling patterns")
            print("   💡 But may not support native OpenAI function calling")
            
    except Exception as e:
        print(f"   ❌ Error testing without tools: {e}")
    
    print("\n" + "=" * 50)
    print("🎯 DIAGNOSIS:")
    print("The local model likely doesn't support native OpenAI function calling.")
    print("It was trained on text-based tool patterns, not structured function calls.")
    print("\n💡 SOLUTION:")
    print("We need to revert local models to use legacy JSON parsing.")
    print("Only cloud models (DeepSeek, OpenAI) support native function calling.")
    
    return True

if __name__ == "__main__":
    debug_local_tool_calling()
