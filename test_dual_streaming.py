#!/usr/bin/env python3
"""
Test script for dual model streaming functionality.
Tests the new streaming implementation for the default @dual provider.
"""

import os
import sys
sys.path.append('/Users/admin/Documents/DeepCoderX')

def test_dual_streaming_triggers():
    """Test dual model streaming trigger detection logic."""
    print("🧪 Testing Dual Model Streaming Trigger Detection...")
    
    # Create a mock context
    from models.session import CommandContext
    from services.dual_model_handler import DualModelHandler
    
    ctx = CommandContext(
        user_input="",
        root_path="/Users/admin/Documents/DeepCoderX",
        debug_mode=True
    )
    
    try:
        handler = DualModelHandler(ctx, "dual")
        
        test_cases = [
            # Should NOT stream (instant commands)
            ("pwd", "local_shortcuts", False, "Direct command should not stream"),
            ("ls", "local_shortcuts", False, "Direct command should not stream"),
            ("git status", "local_shortcuts", False, "Direct command should not stream"),
            ("hello", "conversation", False, "Simple greeting should not stream"),
            
            # Should stream (conversational - complex)
            ("why do cats have fur?", "conversation", True, "Explanatory question should stream"),
            ("explain how Python functions work", "conversation", True, "Educational content should stream"),
            ("tell me about machine learning", "conversation", True, "Complex topic should stream"),
            ("what is the meaning of recursion in programming?", "conversation", True, "Long detailed question should stream"),
            
            # Should stream (code generation)
            ("create a Python calculator script", "qwen_coder", True, "Code creation should always stream"),
            ("write a function to parse JSON", "qwen_coder", True, "Function writing should always stream"),
            ("build a web scraper", "qwen_coder", True, "Complex code task should always stream"),
            ("generate a REST API", "qwen_coder", True, "Code generation should always stream")
        ]
        
        print("\\n📋 Test Results:")
        print("-" * 90)
        print(f"{'Input':<40} {'Target':<15} {'Expected':<10} {'Actual':<10} {'Status':<10}")
        print("-" * 90)
        
        passed = 0
        total = len(test_cases)
        
        for input_text, target, expected, description in test_cases:
            actual = handler._should_stream_response(input_text, target)
            status = "✅ PASS" if actual == expected else "❌ FAIL"
            
            print(f"{input_text[:35]:<40} {target:<15} {str(expected):<10} {str(actual):<10} {status:<10}")
            
            if actual == expected:
                passed += 1
        
        print("-" * 90)
        print(f"Results: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
        
        if passed == total:
            print("🎉 All dual model streaming tests passed!")
        else:
            print("⚠️  Some tests failed - review streaming logic")
            
    except Exception as e:
        print(f"❌ Error testing dual model streaming: {e}")
        return False
    
    return passed == total

def test_environment_setup():
    """Test streaming environment variables."""
    print("\\n🔧 Testing Streaming Environment Setup...")
    
    # Check environment variables
    streaming_vars = [
        "DEEPCODERX_STREAMING_ENABLED",
        "DEEPCODERX_STREAMING_DUAL"
    ]
    
    print("\\n📊 Streaming Environment Variables:")
    print("-" * 50)
    
    all_set = True
    for var in streaming_vars:
        value = os.getenv(var, "not set")
        status = "✅" if value.lower() == "true" else "❌"
        print(f"{status} {var}: {value}")
        if value.lower() != "true":
            all_set = False
    
    print("-" * 50)
    
    if all_set:
        print("🎉 Dual model streaming environment configured correctly!")
    else:
        print("⚠️  Some streaming variables are not enabled")
    
    return all_set

def test_model_availability():
    """Test that required models are available."""
    print("\\n🔍 Testing Model Availability...")
    
    from pathlib import Path
    
    cache_dir = Path("/Users/admin/Documents/DeepCoderX/.cache/deepcoderx/models")
    
    # Check for semantic parser (Llama 3.2-3B)
    llama_models = [
        "Llama-3.2-3B-Instruct-uncensored.Q4_K_S.gguf",
        "llama-3.2-3b-instruct.gguf",
        "Llama-3.2-3B-Instruct.gguf"
    ]
    
    # Check for code specialist (Qwen2.5-Coder)
    qwen_models = [
        "qwen2.5-coder-1.5b-instruct-q8_0.gguf",
        "qwen2.5-coder-1.5b-instruct-q4_k_s.gguf",
        "qwen2.5-coder-1.5b.gguf"
    ]
    
    print("\\n📁 Model Availability:")
    print("-" * 60)
    
    llama_found = False
    qwen_found = False
    
    for model in llama_models:
        model_path = cache_dir / model
        if model_path.exists():
            print(f"✅ Semantic Parser: {model}")
            llama_found = True
            break
    
    if not llama_found:
        print("❌ Semantic Parser: No Llama 3.2-3B model found")
    
    for model in qwen_models:
        model_path = cache_dir / model
        if model_path.exists():
            print(f"✅ Code Specialist: {model}")
            qwen_found = True
            break
    
    if not qwen_found:
        print("❌ Code Specialist: No Qwen2.5-Coder model found")
    
    print("-" * 60)
    
    both_available = llama_found and qwen_found
    if both_available:
        print("🎉 Both models available for dual model streaming!")
    else:
        print("⚠️  Some models missing - dual model system may not work")
    
    return both_available

def main():
    """Run all dual model streaming tests."""
    print("🚀 DeepCoderX Dual Model Streaming Tests")
    print("=" * 70)
    
    tests = [
        ("Environment Setup", test_environment_setup),
        ("Model Availability", test_model_availability),
        ("Streaming Trigger Detection", test_dual_streaming_triggers)
    ]
    
    passed_tests = 0
    total_tests = len(tests)
    
    for test_name, test_func in tests:
        print(f"\\n🧪 Running: {test_name}")
        try:
            success = test_func()
            if success:
                passed_tests += 1
                print(f"✅ {test_name}: PASSED")
            else:
                print(f"❌ {test_name}: FAILED")
        except Exception as e:
            print(f"❌ {test_name}: ERROR - {e}")
    
    print("\\n" + "=" * 70)
    print(f"📊 FINAL RESULTS: {passed_tests}/{total_tests} tests passed")
    
    if passed_tests == total_tests:
        print("🎉 All tests passed! Dual model streaming ready for live testing.")
        print("\\n🚀 Next Steps:")
        print("   1. cd /Users/admin/Documents/DeepCoderX")
        print("   2. python3 app.py")
        print("   3. why do cats have fur?")  # Should stream now!
        print("   4. create a simple calculator script")  # Should stream
        print("   5. pwd")  # Should NOT stream (instant)
    else:
        print(f"⚠️  {total_tests - passed_tests} test(s) failed. Review implementation before live testing.")
    
    return passed_tests == total_tests

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
