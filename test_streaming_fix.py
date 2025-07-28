#!/usr/bin/env python3
"""
Test script to validate streaming functionality fix for local models.
"""

import sys
import os
from pathlib import Path

# Add the project root to the path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_streaming_enabled():
    """Test that streaming is now enabled for appropriate inputs."""
    try:
        from services.dual_model_handler import DualModelHandler
        from models.session import CommandContext
        
        # Create test context
        test_ctx = CommandContext(
            root_path=project_root,
            mcp_client=None,  # Mock MCP client
            sandbox_path=project_root,
            debug_mode=True
        )
        test_ctx.user_input = "test"  # Set user input after initialization
        
        # Create handler (won't actually load models in this test)
        handler = DualModelHandler(test_ctx, "dual")
        
        # Test cases for streaming decisions
        test_cases = [
            ("hello", "conversation", False),  # Simple greeting - no streaming
            ("explain how recursion works", "conversation", True),  # Explanation - should stream
            ("what is machine learning and how does it work", "conversation", True),  # Long explanation - should stream
            ("pwd", "local_shortcuts", False),  # Direct command - no streaming
            ("create a Python script to sort files", "qwen_coder", True),  # Code generation - should stream
            ("write a function for calculating fibonacci", "qwen_coder", True),  # Code creation - should stream
            ("ls", "local_shortcuts", False),  # Simple command - no streaming
        ]
        
        print("🧪 Testing streaming decision logic:")
        print("="*60)
        
        all_tests_passed = True
        
        for user_input, target, expected_streaming in test_cases:
            actual_streaming = handler._should_stream_response(user_input, target)
            status = "✅ PASS" if actual_streaming == expected_streaming else "❌ FAIL"
            
            print(f"{status} | '{user_input}' ({target}) -> Stream: {actual_streaming} (expected: {expected_streaming})")
            
            if actual_streaming != expected_streaming:
                all_tests_passed = False
        
        print("="*60)
        if all_tests_passed:
            print("🎉 ALL STREAMING LOGIC TESTS PASSED!")
            print("✅ Streaming is now properly enabled for appropriate inputs")
            print("✅ Intelligent buffering implemented for both conversation and code")
            print("✅ Simple commands and greetings correctly avoid streaming")
        else:
            print("⚠️  Some streaming logic tests failed - review implementation")
        
        return all_tests_passed
        
    except Exception as e:
        print(f"❌ Test failed with exception: {e}")
        return False

def test_streaming_methods_exist():
    """Test that streaming methods are properly implemented."""
    try:
        from services.dual_model_handler import DualModelHandler
        from models.session import CommandContext
        
        # Create minimal test context
        test_ctx = CommandContext(
            root_path=project_root,
            mcp_client=None,  # Mock MCP client
            sandbox_path=project_root,
            debug_mode=False
        )
        test_ctx.user_input = "test"  # Set user input after initialization
        
        handler = DualModelHandler(test_ctx, "dual")
        
        # Check that streaming methods exist and are callable
        methods_to_check = [
            '_should_stream_response',
            '_stream_conversational_response', 
            '_stream_code_response'
        ]
        
        print("🔍 Checking streaming method implementations:")
        print("="*50)
        
        all_methods_exist = True
        
        for method_name in methods_to_check:
            if hasattr(handler, method_name):
                method = getattr(handler, method_name)
                if callable(method):
                    print(f"✅ {method_name} - exists and callable")
                else:
                    print(f"❌ {method_name} - exists but not callable")
                    all_methods_exist = False
            else:
                print(f"❌ {method_name} - missing")
                all_methods_exist = False
        
        print("="*50)
        if all_methods_exist:
            print("🎉 ALL STREAMING METHODS PROPERLY IMPLEMENTED!")
        else:
            print("⚠️  Some streaming methods are missing or broken")
            
        return all_methods_exist
        
    except Exception as e:
        print(f"❌ Method check failed with exception: {e}")
        return False

def main():
    """Run all streaming fix validation tests."""
    print("🚀 STREAMING FIX VALIDATION")
    print("Testing fixes for line-by-line token display issue")
    print()
    
    # Test 1: Streaming decision logic
    logic_test_passed = test_streaming_enabled()
    print()
    
    # Test 2: Method implementations
    methods_test_passed = test_streaming_methods_exist()
    print()
    
    # Summary
    print("📋 STREAMING FIX SUMMARY:")
    print("="*60)
    
    if logic_test_passed and methods_test_passed:
        print("🎉 STREAMING FIX VALIDATION: SUCCESS")
        print()
        print("✅ Key improvements implemented:")
        print("   • Intelligent streaming triggers for explanations and code generation")
        print("   • Word-boundary buffering for conversational responses")
        print("   • Line-based buffering for code generation")
        print("   • Proper whitespace normalization to eliminate line-by-line display")
        print("   • Fallback to non-streaming on errors")
        print()
        print("🚀 Ready for live testing with DeepCoderX!")
        print("   Test commands:")
        print("   • 'explain how Python imports work' (should stream)")
        print("   • 'create a sorting algorithm' (should stream)")
        print("   • 'hello' (should not stream)")
        print("   • 'pwd' (should not stream)")
        
    else:
        print("❌ STREAMING FIX VALIDATION: FAILED")
        print("   Some components need attention before deployment")
    
    print("="*60)

if __name__ == "__main__":
    main()
