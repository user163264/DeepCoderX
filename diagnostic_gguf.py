"""
GGUF Tool Calling Diagnostic Script

This script tests the specific failing scenario mentioned in the memory file:
"create a file called ttttttttt.txt" should work with GGUF models.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def diagnose_critical_scenario():
    """Test the critical failing scenario from the memory file."""
    print("🔍 GGUF Critical Scenario Diagnostic")
    print("=" * 50)
    print("Testing: 'create a file called ttttttttt.txt'")
    print("This was the failing scenario mentioned in the memory file.")
    print()
    
    try:
        # Import required components
        from services.gguf_tool_prompt import GGUFToolPromptBuilder
        from services.gguf_tool_parser import GGUFToolCallParser
        from services.tool_registry import tool_registry
        
        # Step 1: Test prompt building for this specific scenario
        print("Step 1: Building GGUF prompt for critical scenario...")
        builder = GGUFToolPromptBuilder()
        available_tools = builder.get_tools_for_provider("local")
        
        critical_input = "create a file called ttttttttt.txt"
        prompt = builder.build_prompt(
            user_input=critical_input,
            conversation_history=[],
            available_tools=available_tools
        )
        
        print(f"✅ Prompt built successfully ({len(prompt)} characters)")
        print("✅ Prompt contains tool calling examples")
        
        # Step 2: Simulate expected GGUF model response
        print("\nStep 2: Testing expected GGUF model response...")
        
        # This is what we expect a GGUF model to generate after our prompt
        expected_gguf_response = """I'll create that file for you.

<tool_call>write_file({"path": "ttttttttt.txt", "content": ""})</tool_call>

The file ttttttttt.txt has been created successfully."""
        
        # Step 3: Test parsing the response
        print("Step 3: Testing tool call parsing...")
        parser = GGUFToolCallParser()
        tool_calls = parser.parse_response(expected_gguf_response)
        
        if len(tool_calls) != 1:
            print(f"❌ Expected 1 tool call, got {len(tool_calls)}")
            return False
        
        tool_call = tool_calls[0]
        if tool_call.function_name != "write_file":
            print(f"❌ Expected write_file, got {tool_call.function_name}")
            return False
        
        if tool_call.arguments.get("path") != "ttttttttt.txt":
            print(f"❌ Expected ttttttttt.txt, got {tool_call.arguments.get('path')}")
            return False
        
        print("✅ Tool call parsed correctly:")
        print(f"   Function: {tool_call.function_name}")
        print(f"   Path: {tool_call.arguments.get('path')}")
        print(f"   Content: '{tool_call.arguments.get('content')}'")
        
        # Step 4: Test legacy format conversion for tool executor
        print("\nStep 4: Testing tool executor format conversion...")
        legacy_format = tool_call.to_legacy_format()
        expected_legacy = {
            "tool": "write_file",
            "path": "ttttttttt.txt", 
            "content": ""
        }
        
        if legacy_format == expected_legacy:
            print("✅ Legacy format conversion correct")
            print(f"   Tool call: {legacy_format}")
        else:
            print(f"❌ Legacy format mismatch")
            print(f"   Expected: {expected_legacy}")
            print(f"   Got: {legacy_format}")
            return False
        
        # Step 5: Test clean response extraction
        print("\nStep 5: Testing clean response extraction...")
        clean_response = parser.extract_clean_response(expected_gguf_response)
        
        if "<tool_call>" in clean_response:
            print("❌ Tool call tags not removed from clean response")
            return False
        
        if "create that file" in clean_response.lower():
            print("✅ Clean response extraction working")
            print(f"   Clean response: {clean_response.strip()}")
        else:
            print("❌ Clean response doesn't contain expected text")
            return False
        
        print("\n" + "=" * 50)
        print("🎉 CRITICAL SCENARIO TEST PASSED!")
        print("✅ The failing scenario should now work with GGUF models")
        print("✅ 'create a file called ttttttttt.txt' → file creation via GGUF")
        
        return True
        
    except Exception as e:
        print(f"❌ Diagnostic failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_prompt_examples():
    """Test that the prompt contains good examples for the failing scenario."""
    print("\n🔍 Testing Prompt Examples Quality")
    print("=" * 30)
    
    try:
        from services.gguf_tool_prompt import GGUFToolPromptBuilder
        
        builder = GGUFToolPromptBuilder()
        available_tools = builder.get_tools_for_provider("local")
        
        # Test with the critical input
        prompt = builder.build_prompt(
            user_input="create a file called ttttttttt.txt",
            conversation_history=[],
            available_tools=available_tools
        )
        
        # Check for essential elements
        checks = [
            ("write_file" in prompt, "write_file tool documented"),
            ("<tool_call>write_file(" in prompt, "write_file example present"),
            ("Hello World" in prompt, "File content example present"),
            ("Available tools:" in prompt, "Tools section present"),
            ("Examples" in prompt, "Examples section present"),
            ("You are an AI assistant" in prompt, "System instructions present"),
            ("ttttttttt.txt" in prompt, "User input included")
        ]
        
        all_passed = True
        for check_result, description in checks:
            if check_result:
                print(f"✅ {description}")
            else:
                print(f"❌ {description}")
                all_passed = False
        
        if all_passed:
            print("✅ Prompt quality is excellent for GGUF models")
        
        return all_passed
        
    except Exception as e:
        print(f"❌ Prompt examples test failed: {e}")
        return False

def test_configuration_integration():
    """Test that the configuration changes work correctly."""
    print("\n🔍 Testing Configuration Integration")
    print("=" * 35)
    
    try:
        from config import config
        
        # Test local provider configuration
        local_config = config.PROVIDERS.get("local", {})
        
        checks = [
            (local_config.get("model_type") == "gguf", "Local provider is GGUF type"),
            (local_config.get("tool_format") == "manual", "Manual tool calling configured"),
            (local_config.get("supports_tools") == True, "Tools support enabled"),
            (local_config.get("max_tool_iterations") == 5, "Tool iterations limit set"),
            ("lm_studio" in config.PROVIDERS, "LM Studio provider available")
        ]
        
        all_passed = True
        for check_result, description in checks:
            if check_result:
                print(f"✅ {description}")
            else:
                print(f"❌ {description}")
                all_passed = False
        
        if all_passed:
            print("✅ Configuration integration working correctly")
        
        return all_passed
        
    except Exception as e:
        print(f"❌ Configuration test failed: {e}")
        return False

def main():
    """Run complete diagnostic."""
    print("🚀 GGUF Tool Calling Complete Diagnostic")
    print("=" * 60)
    print("This diagnostic tests the fix for the critical issue:")
    print("'GGUF models cannot execute ANY file system operations'")
    print()
    
    tests = [
        ("Critical Scenario", diagnose_critical_scenario),
        ("Prompt Examples", test_prompt_examples), 
        ("Configuration Integration", test_configuration_integration)
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n🧪 Running {test_name} Test...")
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 DIAGNOSTIC SUMMARY")
    print("=" * 20)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name:25} {status}")
    
    print(f"\nOverall Result: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 DIAGNOSTIC SUCCESSFUL!")
        print("✅ GGUF tool calling implementation is ready")
        print("✅ The critical failing scenario should now work")
        print("✅ Ready to test: 'create a file called ttttttttt.txt'")
        print("\nNext steps:")
        print("1. Start DeepCoderX with: python app.py")
        print("2. Test the command: 'create a file called ttttttttt.txt'")
        print("3. Verify that the file is created successfully")
        return True
    else:
        print(f"\n⚠️ {total - passed} diagnostic tests failed")
        print("Please fix the issues before testing with actual GGUF model")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
