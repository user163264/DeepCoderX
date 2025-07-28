#!/usr/bin/env python3
"""
Simple validation of streaming implementation components.
"""

import os
import sys
sys.path.append('/Users/admin/Documents/DeepCoderX')

def test_semantic_zones_import():
    """Test that we can import SEMANTIC_ZONES from config."""
    try:
        from config_module import SEMANTIC_ZONES
        print("✅ SEMANTIC_ZONES import: SUCCESS")
        print(f"   Found {len(SEMANTIC_ZONES)} zones: {list(SEMANTIC_ZONES.keys())}")
        return True
    except Exception as e:
        print(f"❌ SEMANTIC_ZONES import: FAILED - {e}")
        return False

def test_streaming_env_vars():
    """Test streaming environment variables."""
    streaming_vars = [
        "DEEPCODERX_STREAMING_ENABLED",
        "DEEPCODERX_STREAMING_DEEPSEEK", 
        "DEEPCODERX_STREAMING_OPENAI"
    ]
    
    print("\n📊 Streaming Environment Variables:")
    for var in streaming_vars:
        value = os.getenv(var, "not set")
        status = "✅" if value == "true" else "❌"
        print(f"   {status} {var}: {value}")
    
    return all(os.getenv(var, "").lower() == "true" for var in streaming_vars)

def test_basic_imports():
    """Test basic imports needed for streaming."""
    try:
        from models.session import CommandContext
        from services.unified_openai_handler import UnifiedOpenAIHandler
        print("✅ Basic imports: SUCCESS")
        return True
    except Exception as e:
        print(f"❌ Basic imports: FAILED - {e}")
        return False

if __name__ == "__main__":
    print("🔧 Quick Streaming Implementation Validation")
    print("=" * 50)
    
    tests = [
        test_semantic_zones_import,
        test_streaming_env_vars,
        test_basic_imports
    ]
    
    passed = 0
    for test in tests:
        if test():
            passed += 1
    
    print(f"\n📊 Results: {passed}/{len(tests)} tests passed")
    
    if passed == len(tests):
        print("\n🎉 Ready for live testing!")
        print("Try: @deepseek create a simple Python calculator")
    else:
        print("\n⚠️  Some validation failed")
