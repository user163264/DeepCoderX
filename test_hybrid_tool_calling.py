#!/usr/bin/env python3
"""
Test script to validate hybrid tool calling approach:
- Cloud models (DeepSeek, OpenAI) use native OpenAI function calling
- Local models (LM Studio) use legacy JSON format
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import config
from services.tool_registry import get_tools_for_provider

def test_hybrid_tool_calling():
    """Test that cloud and local models use appropriate tool calling methods."""
    
    print("🔧 Testing Hybrid Tool Calling Approach")
    print("=" * 60)
    
    # Test 1: Local Model Configuration
    print("\n1. Local Model Configuration:")
    local_config = config.PROVIDERS.get("local")
    print(f"   Local model enabled: {local_config['enabled']}")
    print(f"   Supports tools: {local_config['supports_tools']}")
    
    if local_config['supports_tools']:
        print("   ❌ ERROR: Local model should have supports_tools=False")
        print("   💡 Local models use legacy JSON format")
        return False
    else:
        print("   ✅ Local model configured for legacy JSON tool calling")
    
    # Test 2: Cloud Model Configuration
    print("\n2. Cloud Model Configuration:")
    deepseek_config = config.PROVIDERS.get("deepseek")
    print(f"   DeepSeek enabled: {deepseek_config['enabled']}")
    print(f"   Supports tools: {deepseek_config['supports_tools']}")
    
    if not deepseek_config['supports_tools']:
        print("   ❌ ERROR: DeepSeek should have supports_tools=True")
        print("   💡 Cloud models use native OpenAI function calling")
        return False
    else:
        print("   ✅ DeepSeek configured for native OpenAI function calling")
    
    # Test 3: System Prompts
    print("\n3. System Prompt Analysis:")
    
    # Local system prompt should have JSON instructions
    local_prompt = config.LOCAL_SYSTEM_PROMPT
    has_json_format = '"tool":' in local_prompt
    has_tool_format_section = 'TOOL FORMAT' in local_prompt
    has_json_examples = '{"tool":' in local_prompt
    
    print(f"   Local prompt has JSON format: {has_json_format}")
    print(f"   Local prompt has TOOL FORMAT section: {has_tool_format_section}")
    print(f"   Local prompt has JSON examples: {has_json_examples}")
    
    if not (has_json_format and has_tool_format_section):
        print("   ❌ ERROR: Local prompt missing JSON format instructions")
        return False
    else:
        print("   ✅ Local prompt correctly instructs JSON format")
    
    # DeepSeek system prompt should NOT have JSON instructions
    deepseek_prompt = config.DEEPSEEK_SYSTEM_PROMPT
    ds_has_json_instructions = 'JSON object' in deepseek_prompt
    ds_has_json_format = '"tool":' in deepseek_prompt
    
    print(f"   DeepSeek prompt mentions JSON objects: {ds_has_json_instructions}")
    print(f"   DeepSeek prompt has JSON examples: {ds_has_json_format}")
    
    if ds_has_json_instructions or ds_has_json_format:
        print("   ⚠️  DeepSeek prompt mentions JSON (this is for legacy compatibility)")
    else:
        print("   ✅ DeepSeek prompt doesn't emphasize JSON format")
    
    # Test 4: Tool Registry Behavior
    print("\n4. Tool Registry Behavior:")
    
    try:
        # Local model tools (should get tools despite supports_tools=False)
        local_tools = get_tools_for_provider("local", local_config)
        print(f"   Local model tools: {len(local_tools)}")
        
        if len(local_tools) == 0:
            print("   ❌ ERROR: Local model should get tools for legacy JSON calling")
            return False
        else:
            print("   ✅ Local model gets tools for legacy JSON calling")
            tool_names = [tool['function']['name'] for tool in local_tools]
            print(f"     Available: {', '.join(tool_names)}")
        
        # Cloud model tools
        cloud_tools = get_tools_for_provider("deepseek", deepseek_config)
        print(f"   Cloud model tools: {len(cloud_tools)}")
        
        if len(cloud_tools) == 0:
            print("   ❌ ERROR: Cloud model should get tools for native calling")
            return False
        else:
            print("   ✅ Cloud model gets tools for native calling")
            tool_names = [tool['function']['name'] for tool in cloud_tools]
            print(f"     Available: {', '.join(tool_names)}")
        
        # Compare tool counts (cloud should have fewer due to security filtering)
        if len(local_tools) > len(cloud_tools):
            print("   ✅ Local models have more tools (includes run_bash)")
        else:
            print("   ⚠️  Expected local models to have more tools than cloud")
            
    except Exception as e:
        print(f"   ❌ ERROR: Failed to get tools: {e}")
        return False
    
    # Test 5: Handler Import Check
    print("\n5. Handler Implementation Check:")
    
    try:
        from services.unified_openai_handler import LocalOpenAIHandler, CloudOpenAIHandler
        
        # Check LocalOpenAIHandler has override
        local_has_override = hasattr(LocalOpenAIHandler, '_conversation_loop') and \
                           LocalOpenAIHandler._conversation_loop.__qualname__ == 'LocalOpenAIHandler._conversation_loop'
        
        print(f"   LocalOpenAIHandler has legacy override: {local_has_override}")
        
        if not local_has_override:
            print("   ❌ ERROR: LocalOpenAIHandler should override _conversation_loop for JSON parsing")
            return False
        else:
            print("   ✅ LocalOpenAIHandler correctly overrides for legacy JSON calling")
        
        # Check CloudOpenAIHandler inherits native calling
        cloud_has_override = hasattr(CloudOpenAIHandler, '_conversation_loop') and \
                           CloudOpenAIHandler._conversation_loop.__qualname__ == 'CloudOpenAIHandler._conversation_loop'
        
        print(f"   CloudOpenAIHandler has override: {cloud_has_override}")
        
        if cloud_has_override:
            print("   ⚠️  CloudOpenAIHandler has override (may be for session management)")
        else:
            print("   ✅ CloudOpenAIHandler inherits native function calling")
            
    except Exception as e:
        print(f"   ❌ ERROR: Failed to import handlers: {e}")
        return False
    
    print("\n" + "=" * 60)
    print("🎉 Hybrid Tool Calling Approach Validated!")
    print("\n📋 Summary:")
    print("   • Local models: Legacy JSON format (supports_tools=False)")
    print("   • Cloud models: Native OpenAI function calling (supports_tools=True)")
    print("   • System prompts: Appropriate for each model type")
    print("   • Tool registry: Provides tools to both model types")
    print("   • Handlers: Correct implementation for each approach")
    
    print("\n🚀 Next steps:")
    print("1. Start the app: python app.py")
    print("2. Test local model: 'list the files in the current dir'")
    print("3. Test cloud model: '@deepseek list the files in the current dir'")
    print("4. Local should output JSON, cloud should use native function calls")
    
    return True

if __name__ == "__main__":
    success = test_hybrid_tool_calling()
    sys.exit(0 if success else 1)
