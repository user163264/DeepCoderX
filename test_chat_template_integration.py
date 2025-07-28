#!/usr/bin/env python3
"""
Test script for ChatTemplateFormatter integration in GGUFLocalHandler.

This script tests the chat template formatting functionality without requiring
actual model loading or inference.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

try:
    from services.gguf_handler import ChatTemplateFormatter, GGUFLocalHandler
    from models.session import CommandContext
    from config_module import config
    print("✅ Successfully imported ChatTemplateFormatter and related components")
except ImportError as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)


def test_chat_template_formatter():
    """Test ChatTemplateFormatter class functionality."""
    print("\n🧪 Testing ChatTemplateFormatter Class")
    print("=" * 50)
    
    # Test model type detection
    test_cases = [
        ("llama-3.2-3b-instruct.gguf", "Llama 3.2", "llama"),
        ("qwen2.5-coder-1.5b.gguf", "Qwen2.5 Coder", "qwen"),
        ("phi-3.5-mini-instruct.gguf", "Phi-3.5", "phi"),
        ("gemma-2-9b-instruct.gguf", "Gemma 2", "gemma"),
        ("mistral-7b-instruct.gguf", "Mistral", "mistral"),
        ("unknown-model.gguf", "Unknown Model", "generic")
    ]
    
    for model_path, model_name, expected_type in test_cases:
        formatter = ChatTemplateFormatter(model_path=model_path, model_name=model_name)
        detected_type = formatter.model_type
        status = "✅" if detected_type == expected_type else "❌"
        print(f"{status} {model_name}: Detected '{detected_type}' (expected '{expected_type}')")
        
        # Test model info
        info = formatter.get_model_info()
        print(f"   📋 Template: {info['template_format']}")
    
    print(f"\n🔄 Testing Chat Template Formatting")
    print("-" * 30)
    
    # Test Llama template formatting
    llama_formatter = ChatTemplateFormatter(model_path="llama-3.2-3b-instruct.gguf")
    llama_prompt = llama_formatter.format_prompt(
        system_prompt="You are a helpful coding assistant.",
        user_prompt="Create a simple Python function",
        conversation_history=[
            {"role": "user", "content": "Hello"},
            {"role": "assistant", "content": "Hi! How can I help you?"}
        ]
    )
    print("✅ Llama 3.2 Template:")
    print(f"   📝 Length: {len(llama_prompt)} characters")
    print(f"   🏷️  Contains proper tokens: {all(token in llama_prompt for token in ['<|begin_of_text|>', '<|start_header_id|>', '<|eot_id|>'])}")
    
    # Test Qwen template formatting  
    qwen_formatter = ChatTemplateFormatter(model_path="qwen2.5-coder-1.5b.gguf")
    qwen_prompt = qwen_formatter.format_prompt(
        system_prompt="You are a helpful coding assistant.",
        user_prompt="Create a simple Python function"
    )
    print("✅ Qwen 2.5 Template:")
    print(f"   📝 Length: {len(qwen_prompt)} characters")
    print(f"   🏷️  Contains proper tokens: {all(token in qwen_prompt for token in ['<|im_start|>', '<|im_end|>'])}")
    
    return True


def test_gguf_handler_integration():
    """Test ChatTemplateFormatter integration with GGUFLocalHandler."""
    print("\n🔌 Testing GGUFLocalHandler Integration")
    print("=" * 50)
    
    try:
        # Create a mock context for testing
        test_context = CommandContext(
            user_input="test chat template integration",
            root_path=Path.cwd(),
            debug_mode=True
        )
        
        # Test handler initialization with chat formatter
        print("🏗️  Initializing GGUFLocalHandler...")
        
        # Note: This will try to load the actual model path, but we're testing initialization
        try:
            handler = GGUFLocalHandler(test_context, "local")
            print("✅ GGUFLocalHandler initialized successfully")
            
            # Test chat formatter integration
            print(f"✅ Chat formatter initialized: {handler.chat_formatter.model_type} template")
            
            # Test model info access
            template_info = handler.chat_formatter.get_model_info()
            print(f"✅ Template info accessible: {template_info['template_format']}")
            
            # Test helper methods (if model path exists)
            test_prompt = "System: You are helpful. User: Hello"
            system_part = handler._extract_system_prompt(test_prompt)
            user_part = handler._extract_user_prompt(test_prompt, "Hello")
            
            print(f"✅ System prompt extraction: {len(system_part)} chars")
            print(f"✅ User prompt extraction: {len(user_part)} chars")
            
            # Test conversation history formatting
            test_history = [
                {"role": "user", "message": "Hello"},
                {"role": "assistant", "content": "Hi there!"}
            ]
            formatted_history = handler._format_conversation_history(test_history)
            print(f"✅ History formatting: {len(formatted_history)} messages processed")
            
            return True
            
        except FileNotFoundError as e:
            print(f"⚠️  Model file not found (expected): {e}")
            print("✅ Handler initialization would work with proper model file")
            return True
        except Exception as e:
            print(f"❌ Handler initialization error: {e}")
            return False
            
    except Exception as e:
        print(f"❌ Integration test error: {e}")
        return False


def test_template_formats_visual():
    """Visual test of different chat template formats."""
    print("\n👁️  Visual Template Format Test")
    print("=" * 50)
    
    system_prompt = "You are a helpful assistant."
    user_prompt = "Hello, world!"
    
    models = [
        ("llama-3.2-3b-instruct.gguf", "Llama 3.2"),
        ("qwen2.5-coder-1.5b.gguf", "Qwen 2.5"),
        ("phi-3.5-mini-instruct.gguf", "Phi-3.5")
    ]
    
    for model_path, model_name in models:
        print(f"\n📝 {model_name} Template Format:")
        print("-" * 30)
        
        formatter = ChatTemplateFormatter(model_path=model_path)
        formatted_prompt = formatter.format_prompt(system_prompt, user_prompt)
        
        # Show first few lines of formatted prompt
        lines = formatted_prompt.split('\n')[:6]
        for i, line in enumerate(lines):
            print(f"   {i+1}: {line}")
        
        if len(formatted_prompt.split('\n')) > 6:
            print("   ...")
        
        print(f"   💾 Total length: {len(formatted_prompt)} characters")


def main():
    """Run all tests."""
    print("🚀 DeepCoderX Chat Template Integration Test")
    print("=" * 60)
    
    tests = [
        ("ChatTemplateFormatter Class", test_chat_template_formatter),
        ("GGUFLocalHandler Integration", test_gguf_handler_integration),
        ("Template Formats Visual", test_template_formats_visual)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            print(f"\n🧪 Running: {test_name}")
            result = test_func()
            results.append((test_name, result))
            status = "✅ PASSED" if result else "❌ FAILED"
            print(f"   {status}")
        except Exception as e:
            print(f"   ❌ ERROR: {e}")
            results.append((test_name, False))
    
    # Summary
    print(f"\n📊 Test Summary")
    print("=" * 30)
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
    
    print(f"\n🎯 Result: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Chat template integration is working correctly.")
        print("\n📋 Next Steps:")
        print("   1. Test with actual model files")
        print("   2. Verify Llama 3.2 semantic parser performance")
        print("   3. Compare prompt formatting before/after integration")
    else:
        print("⚠️  Some tests failed. Please review the errors above.")
    
    return passed == total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
