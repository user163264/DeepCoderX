#!/usr/bin/env python3
"""
Simple verification script for GGUF tool calling implementation.
Tests basic functionality of all components.
"""

import sys
from pathlib import Path

# Add the project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_basic_functionality():
    """Test basic functionality of GGUF components."""
    print("🧪 Testing GGUF Tool Calling Implementation")
    print("=" * 50)
    
    # Test 1: Import all components
    print("\n1. Testing imports...")
    try:
        from services.gguf_tool_prompt import GGUFToolPromptBuilder
        from services.gguf_tool_parser import GGUFToolCallParser
        from services.gguf_context_manager import GGUFContextManager
        from services.gguf_handler import GGUFLocalHandler
        from services.tool_registry import tool_registry
        print("✅ All GGUF components imported successfully")
    except Exception as e:
        print(f"❌ Import failed: {e}")
        return False
    
    # Test 2: Tool Registry
    print("\n2. Testing Tool Registry...")
    try:
        tools = list(tool_registry.tools.keys())
        expected = ["read_file", "write_file", "list_dir", "move_file", "mkdir", "stat", "run_bash"]
        missing = [t for t in expected if t not in tools]
        if missing:
            print(f"❌ Missing tools: {missing}")
            return False
        print(f"✅ Tool Registry has all {len(tools)} expected tools")
    except Exception as e:
        print(f"❌ Tool Registry test failed: {e}")
        return False
    
    # Test 3: Prompt Builder
    print("\n3. Testing Prompt Builder...")
    try:
        builder = GGUFToolPromptBuilder()
        available_tools = builder.get_tools_for_provider("local")
        prompt = builder.build_prompt(
            user_input="create a file called test.txt",
            conversation_history=[],
            available_tools=available_tools
        )
        
        if len(prompt) < 100:
            print("❌ Prompt too short")
            return False
        if "<tool_call>" not in prompt:
            print("❌ Tool call format not in prompt")
            return False
        if "write_file" not in prompt:
            print("❌ write_file tool not documented")
            return False
        
        print(f"✅ Prompt Builder generated {len(prompt)} character prompt with tool examples")
    except Exception as e:
        print(f"❌ Prompt Builder test failed: {e}")
        return False
    
    # Test 4: Tool Parser
    print("\n4. Testing Tool Parser...")
    try:
        parser = GGUFToolCallParser()
        
        # Test parsing a valid tool call
        test_response = 'I will create the file.\n<tool_call>write_file({"path": "test.txt", "content": "Hello"})</tool_call>\nDone!'
        tool_calls = parser.parse_response(test_response)
        
        if len(tool_calls) != 1:
            print(f"❌ Expected 1 tool call, got {len(tool_calls)}")
            return False
        
        if tool_calls[0].function_name != "write_file":
            print(f"❌ Expected write_file, got {tool_calls[0].function_name}")
            return False
        
        if tool_calls[0].arguments.get("path") != "test.txt":
            print(f"❌ Path argument not parsed correctly")
            return False
        
        # Test clean response extraction
        clean = parser.extract_clean_response(test_response)
        if "<tool_call>" in clean:
            print("❌ Tool call not removed from clean response")
            return False
        
        print("✅ Tool Parser correctly parsed tool calls and extracted clean response")
    except Exception as e:
        print(f"❌ Tool Parser test failed: {e}")
        return False
    
    # Test 5: Context Manager
    print("\n5. Testing Context Manager...")
    try:
        manager = GGUFContextManager("test_provider")
        
        # Add some messages
        manager.add_user_message("Hello")
        manager.add_assistant_message("Hi there!", [])
        
        history = manager.get_conversation_history()
        if len(history) < 2:
            print(f"❌ Expected 2+ messages, got {len(history)}")
            return False
        
        if manager.get_token_count() <= 0:
            print("❌ Token counting not working")
            return False
        
        # Clean up
        manager.clear_history()
        print("✅ Context Manager correctly managed conversation history")
    except Exception as e:
        print(f"❌ Context Manager test failed: {e}")
        return False
    
    # Test 6: Configuration Check
    print("\n6. Testing Configuration...")
    try:
        from config import config
        local_config = config.PROVIDERS.get("local", {})
        
        if local_config.get("model_type") != "gguf":
            print("❌ Local provider not configured as GGUF")
            return False
        
        if local_config.get("tool_format") != "manual":
            print("❌ Local provider not configured for manual tool calling")
            return False
        
        print("✅ Configuration updated correctly for GGUF support")
    except Exception as e:
        print(f"❌ Configuration test failed: {e}")
        return False
    
    # All tests passed
    print("\n" + "=" * 50)
    print("🎉 ALL TESTS PASSED!")
    print("✅ GGUF Tool Calling Implementation is working correctly")
    print("✅ Ready to test with actual GGUF model")
    print("\nNext step: Test with 'create a file called ttttttttt.txt' command")
    return True

if __name__ == "__main__":
    success = test_basic_functionality()
    if not success:
        print("\n❌ Some tests failed. Please check the implementation.")
        sys.exit(1)
    else:
        print("\n🚀 GGUF implementation ready for production use!")
        sys.exit(0)
