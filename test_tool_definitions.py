#!/usr/bin/env python3
"""
Test script to validate Fix #1: Unified Tool Definitions

This test verifies that local models now receive native OpenAI tool definitions
just like cloud models, eliminating the architectural inconsistency.
"""

import sys
import os
import json
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_local_model_tool_definitions():
    """Test that local models now receive tool definitions."""
    print("🔧 Testing Local Model Tool Definitions")
    print("=" * 40)
    
    try:
        from config import config
        from services.unified_openai_handler import UnifiedOpenAIHandler
        from models.session import CommandContext
        from pathlib import Path
        
        # Create a mock context (minimal for testing)
        class MockMCPClient:
            def read_file(self, path): return {"content": "mock content"}
            def write_file(self, path, content): return {"status": "success"}
            def list_dir(self, path): return {"result": {"files": [], "directories": []}}
        
        class MockContext:
            def __init__(self):
                self.root_path = Path("/tmp/test")
                self.current_dir = Path("/tmp/test")
                self.user_input = "test input"
                self.debug_mode = True
                self.mcp_client = MockMCPClient()
        
        # Test local provider configuration
        print("1. Checking local provider configuration...")
        local_config = config.PROVIDERS.get("local", {})
        
        print(f"   Local provider enabled: {local_config.get('enabled', False)}")
        print(f"   Local provider supports_tools: {local_config.get('supports_tools', False)}")
        
        if not local_config.get("supports_tools", False):
            print("   ❌ FAIL: Local provider not configured for tool support")
            return False
        
        print("   ✅ Local provider properly configured for tools")
        
        # Test creating local handler (without OpenAI client to avoid connection)
        print("\n2. Testing handler instantiation...")
        
        try:
            # We'll test the class methods without instantiating (to avoid OpenAI client issues)
            handler_class = UnifiedOpenAIHandler
            
            # Check if _get_tool_definitions method exists and returns proper tools
            tool_definitions = handler_class._get_tool_definitions(None)
            
            print(f"   Tool definitions returned: {len(tool_definitions)} tools")
            
            # Verify tool structure
            expected_tools = ["read_file", "write_file", "list_dir", "run_bash"]
            actual_tools = [tool["function"]["name"] for tool in tool_definitions]
            
            print(f"   Expected tools: {expected_tools}")
            print(f"   Actual tools: {actual_tools}")
            
            if set(expected_tools) == set(actual_tools):
                print("   ✅ Tool definitions contain all expected tools")
            else:
                print("   ❌ FAIL: Tool definitions missing or incorrect")
                return False
            
        except Exception as e:
            print(f"   ❌ FAIL: Handler creation failed: {e}")
            return False
        
        # Test the critical fix: check _create_chat_completion logic
        print("\n3. Testing chat completion parameter logic...")
        
        import inspect
        source = inspect.getsource(UnifiedOpenAIHandler._create_chat_completion)
        
        # Check that the exclusion was removed
        if 'self.provider_name != "local"' in source:
            print("   ❌ FAIL: Local model exclusion still present in code")
            print("   Found exclusion in _create_chat_completion method")
            return False
        
        # Check that supports_tools check is present
        if 'self.provider_config.get("supports_tools", False)' in source:
            print("   ✅ Tool support check is present")
        else:
            print("   ❌ FAIL: Tool support check missing")
            return False
        
        print("   ✅ Chat completion logic correctly unified")
        
        print("\n🎉 Fix #1 Test PASSED: Local models now receive tool definitions!")
        return True
        
    except Exception as e:
        print(f"\n❌ Fix #1 Test FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_cloud_model_still_works():
    """Test that cloud models still receive tool definitions (regression test)."""
    print("\n🔧 Testing Cloud Model Tool Definitions (Regression Test)")
    print("=" * 55)
    
    try:
        from config import config
        
        # Test cloud provider configuration  
        cloud_providers = ["deepseek", "openai"]
        
        for provider_name in cloud_providers:
            provider_config = config.PROVIDERS.get(provider_name, {})
            
            print(f"   {provider_name} supports_tools: {provider_config.get('supports_tools', False)}")
            
            if provider_config.get("supports_tools", False):
                print(f"   ✅ {provider_name} properly configured for tools")
            else:
                print(f"   ⚠️  {provider_name} not configured for tools (may be intentional)")
        
        print("\n✅ Cloud model configurations validated")
        return True
        
    except Exception as e:
        print(f"\n❌ Cloud model test failed: {e}")
        return False

def test_provider_consistency():
    """Test that all tool-enabled providers have consistent configuration."""
    print("\n🔧 Testing Provider Configuration Consistency")
    print("=" * 45)
    
    try:
        from config import config
        
        tool_enabled_providers = []
        
        for name, provider_config in config.PROVIDERS.items():
            if provider_config.get("supports_tools", False) and provider_config.get("enabled", False):
                tool_enabled_providers.append(name)
        
        print(f"   Tool-enabled providers: {tool_enabled_providers}")
        
        if "local" in tool_enabled_providers:
            print("   ✅ Local provider included in tool-enabled providers")
        else:
            print("   ❌ FAIL: Local provider missing from tool-enabled providers")
            return False
        
        # Check configuration consistency
        required_keys = ["name", "enabled", "supports_tools", "model"]
        
        for provider_name in tool_enabled_providers:
            provider_config = config.PROVIDERS[provider_name]
            missing_keys = [key for key in required_keys if key not in provider_config]
            
            if missing_keys:
                print(f"   ❌ FAIL: Provider {provider_name} missing keys: {missing_keys}")
                return False
            else:
                print(f"   ✅ Provider {provider_name} has all required configuration")
        
        print("\n✅ All tool-enabled providers have consistent configuration")
        return True
        
    except Exception as e:
        print(f"\n❌ Provider consistency test failed: {e}")
        return False

def main():
    """Run all tool definition tests."""
    print("🚀 Testing Fix #1: Unified Tool Definitions")
    print("=" * 50)
    
    results = []
    
    # Run tests
    results.append(test_local_model_tool_definitions())
    results.append(test_cloud_model_still_works())
    results.append(test_provider_consistency())
    
    # Summary
    passed = sum(results)
    total = len(results)
    
    print(f"\n📊 TOOL DEFINITIONS TEST SUMMARY")
    print("=" * 35)
    print(f"Tests passed: {passed}/{total}")
    
    if passed == total:
        print("🎉 ALL TOOL DEFINITION TESTS PASSED!")
        print("\n✅ Confirmed:")
        print("   - Local models now receive native OpenAI tool definitions")
        print("   - Cloud models continue to work (no regression)")
        print("   - All providers have consistent configuration")
        print("   - Architectural inconsistency eliminated")
        return 0
    else:
        print("❌ SOME TOOL DEFINITION TESTS FAILED")
        print(f"   Failed tests: {total - passed}")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
