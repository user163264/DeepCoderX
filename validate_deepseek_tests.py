#!/usr/bin/env python3
"""
Quick validation of DeepSeek tool testing setup
Run this first to check basic configuration
"""

import sys
sys.path.append('/Users/admin/Documents/DeepCoderX')

def quick_validation():
    """Quick validation of test environment"""
    print("🔍 Quick DeepSeek Tool Test Validation")
    print("=" * 50)
    
    # Test 1: Basic imports
    print("1. Testing imports...")
    try:
        from config import config
        from services.unified_openai_handler import CloudOpenAIHandler
        from models.session import CommandContext
        print("   ✅ All imports successful")
    except Exception as e:
        print(f"   ❌ Import error: {e}")
        return False
    
    # Test 2: DeepSeek configuration
    print("2. Checking DeepSeek config...")
    try:
        deepseek_config = config.PROVIDERS.get("deepseek")
        if not deepseek_config:
            print("   ❌ DeepSeek not configured")
            return False
        
        if not deepseek_config.get("enabled"):
            print("   ❌ DeepSeek not enabled")
            return False
            
        if not deepseek_config.get("supports_tools"):
            print("   ❌ DeepSeek tools not enabled")
            return False
            
        print("   ✅ DeepSeek properly configured")
    except Exception as e:
        print(f"   ❌ Config error: {e}")
        return False
    
    # Test 3: API key
    print("3. Checking API key...")
    try:
        api_key = config.PROVIDERS["deepseek"]["api_key"]
        if not api_key:
            print("   ⚠️ No API key (set DEEPSEEK_API_KEY env var)")
        elif api_key.startswith("sk-"):
            print(f"   ✅ API key configured: {api_key[:8]}...")
        else:
            print("   ⚠️ API key format unusual")
    except Exception as e:
        print(f"   ❌ API key error: {e}")
    
    # Test 4: OpenAI library
    print("4. Checking OpenAI library...")
    try:
        import openai
        print(f"   ✅ OpenAI library version: {openai.__version__}")
    except Exception as e:
        print(f"   ❌ OpenAI library error: {e}")
        return False
    
    print("\n🎯 Validation Results:")
    print("✅ Ready to run: python test_deepseek_tools.py")
    print("🚀 Ready for live tests: python test_deepseek_live.py")
    
    return True

if __name__ == "__main__":
    quick_validation()
