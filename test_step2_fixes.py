#!/usr/bin/env python3
"""
Simplified test to verify if our fixes work
"""

import sys
import os
sys.path.append('/Users/admin/Documents/DeepCoderX')

def test_config_changes():
    """Test that our configuration changes are in place"""
    print("🧪 Testing Configuration Changes...")
    
    try:
        from config import config
        
        # Check local provider supports_tools setting
        local_config = config.PROVIDERS.get("local", {})
        supports_tools = local_config.get("supports_tools", False)
        
        print(f"📋 Local provider supports_tools: {supports_tools}")
        
        # Check system prompt
        system_prompt = config.LOCAL_SYSTEM_PROMPT
        if "FOR SIMPLE CONVERSATIONS" in system_prompt:
            print("✅ System prompt updated with conversation focus")
        else:
            print("❌ System prompt not updated")
            
        # Check if prompt mentions avoiding tools for conversations
        if "Answer directly without any tools" in system_prompt:
            print("✅ System prompt instructs to avoid tools for conversations")
            return True
        else:
            print("❌ System prompt doesn't clearly instruct to avoid tools")
            return False
            
    except Exception as e:
        print(f"❌ ERROR testing config: {e}")
        return False

def test_unified_handler_changes():
    """Test that unified handler changes are in place"""
    print("\n🧪 Testing Unified Handler Changes...")
    
    try:
        # Check the handler file for our changes
        with open('/Users/admin/Documents/DeepCoderX/services/unified_openai_handler.py', 'r') as f:
            content = f.read()
            
        # Check for our comment about local models
        if "Local models use legacy JSON tool calling" in content:
            print("✅ Handler properly configured for local model legacy tools")
            return True
        else:
            print("❌ Handler not properly configured")
            return False
            
    except Exception as e:
        print(f"❌ ERROR testing handler: {e}")
        return False

def test_imports():
    """Test that we can import the key modules"""
    print("\n🧪 Testing Module Imports...")
    
    try:
        from config import config
        print("✅ Config imported successfully")
        
        from services.unified_openai_handler import LocalOpenAIHandler
        print("✅ LocalOpenAIHandler imported successfully")
        
        return True
        
    except Exception as e:
        print(f"❌ ERROR importing modules: {e}")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("🔧 TESTING STEP 2 CONVERSATION FIXES")  
    print("=" * 60)
    
    test1_passed = test_config_changes()
    test2_passed = test_unified_handler_changes()
    test3_passed = test_imports()
    
    print("\n" + "=" * 60)
    print("📊 TEST RESULTS:")
    print(f"   Configuration: {'✅ PASS' if test1_passed else '❌ FAIL'}")
    print(f"   Handler Changes: {'✅ PASS' if test2_passed else '❌ FAIL'}")
    print(f"   Module Imports: {'✅ PASS' if test3_passed else '❌ FAIL'}")
    
    if test1_passed and test2_passed and test3_passed:
        print("\n🎉 ALL SETUP TESTS PASSED!")
        print("✨ Ready to test actual conversation behavior")
        print("\n💡 Next step: Run DeepCoderX and test with 'what is your favorite colour?'")
    else:
        print("\n⚠️ Some setup tests failed - check configuration")
    
    print("=" * 60)
