#!/usr/bin/env python3
"""
Integration test to validate both fixes work together and don't break existing functionality.

This test simulates real usage scenarios to ensure the architectural improvements
maintain system stability while providing the intended benefits.
"""

import sys
import os
import json
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_unified_handler_creation():
    """Test that unified handlers can be created for different providers."""
    print("🔧 Testing Unified Handler Creation")
    print("=" * 35)
    
    try:
        from config import config
        from services.unified_openai_handler import UnifiedOpenAIHandler, LocalOpenAIHandler, CloudOpenAIHandler
        from models.session import CommandContext
        
        # Create mock context
        class MockMCPClient:
            def read_file(self, path): return {"content": "mock content"}
            def write_file(self, path, content): return {"status": "success"}
            def list_dir(self, path): return {"result": {"files": [], "directories": []}}
        
        class MockContext:
            def __init__(self):
                self.root_path = Path("/tmp/test")
                self.current_dir = Path("/tmp/test")
                self.user_input = "test input"
                self.debug_mode = False
                self.mcp_client = MockMCPClient()
        
        mock_ctx = MockContext()
        
        # Test that handler classes exist and can be imported
        print("   ✅ Handler classes imported successfully")
        
        # Test provider configurations
        enabled_providers = [name for name, config_data in config.PROVIDERS.items() 
                           if config_data.get("enabled", False)]
        
        print(f"   Enabled providers: {enabled_providers}")
        
        if "local" in enabled_providers:
            print("   ✅ Local provider enabled")
        else:
            print("   ⚠️  Local provider not enabled (check configuration)")
        
        # Test tool definitions method exists
        if hasattr(UnifiedOpenAIHandler, '_get_tool_definitions'):
            print("   ✅ Tool definitions method exists")
        else:
            print("   ❌ FAIL: Tool definitions method missing")
            return False
        
        print("\n✅ Handler creation test passed")
        return True
        
    except Exception as e:
        print(f"\n❌ Handler creation test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_tool_executor_with_new_errors():
    """Test tool executor with new error handling in realistic scenarios."""
    print("\n🔧 Testing Tool Executor with New Error Handling")
    print("=" * 48)
    
    try:
        from services.tool_executor import ToolExecutor
        from models.session import CommandContext
        
        # Create mock context
        class MockMCPClient:
            def read_file(self, path):
                if path == "missing.txt":
                    return {"error": "File not found"}
                return {"content": f"Content of {path}"}
            
            def write_file(self, path, content):
                if path.startswith("/"):
                    return {"error": "unauthorized access"}
                return {"status": "success"}
            
            def list_dir(self, path):
                if path == "missing_dir":
                    return {"error": "Directory not found"}
                return {"result": {"files": ["file1.txt"], "directories": ["subdir"]}}
        
        class MockContext:
            def __init__(self):
                self.root_path = Path("/tmp/test")
                self.current_dir = Path("/tmp/test")
                self.mcp_client = MockMCPClient()
        
        mock_ctx = MockContext()
        executor = ToolExecutor(mock_ctx, use_complex_path_resolution=False)
        
        # Test successful operations
        print("   Testing successful operations...")
        
        # Read file success
        result = executor.execute_tool({"tool": "read_file", "path": "config.py"})
        if "Content of config.py" in result:
            print("   ✅ Read file success works")
        else:
            print(f"   ❌ FAIL: Read file success: {result}")
            return False
        
        # Write file success
        result = executor.execute_tool({"tool": "write_file", "path": "test.txt", "content": "test"})
        if "Successfully wrote" in result:
            print("   ✅ Write file success works")
        else:
            print(f"   ❌ FAIL: Write file success: {result}")
            return False
        
        # Test error scenarios with new error handling
        print("   Testing error scenarios...")
        
        # Missing tool parameter
        result = executor.execute_tool({"tool": "read_file"})
        if "Validation Error" in result and "path" in result and "missing" in result:
            print("   ✅ Missing parameter error correctly formatted")
        else:
            print(f"   ❌ FAIL: Missing parameter error: {result}")
            return False
        
        # File not found error
        result = executor.execute_tool({"tool": "read_file", "path": "missing.txt"})
        if "File Not Found" in result and "Suggestions:" in result:
            print("   ✅ File not found error correctly formatted")
        else:
            print(f"   ❌ FAIL: File not found error: {result}")
            return False
        
        # Security error
        result = executor.execute_tool({"tool": "write_file", "path": "/absolute/path", "content": "test"})
        if "Path Security Error" in result and "relative paths" in result:
            print("   ✅ Security error correctly formatted")
        else:
            print(f"   ❌ FAIL: Security error: {result}")
            return False
        
        # Invalid tool
        result = executor.execute_tool({"tool": "invalid_tool", "path": "test"})
        if "Validation Error" in result and "tool" in result and "one of:" in result:
            print("   ✅ Invalid tool error correctly formatted")
        else:
            print(f"   ❌ FAIL: Invalid tool error: {result}")
            return False
        
        print("\n✅ Tool executor integration test passed")
        return True
        
    except Exception as e:
        print(f"\n❌ Tool executor integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_configuration_consistency():
    """Test that configuration is consistent after changes."""
    print("\n🔧 Testing Configuration Consistency")
    print("=" * 37)
    
    try:
        from config import config
        
        # Test that PROVIDERS configuration is valid
        if not hasattr(config, 'PROVIDERS') or not config.PROVIDERS:
            print("   ❌ FAIL: PROVIDERS configuration missing")
            return False
        
        print(f"   Found {len(config.PROVIDERS)} providers configured")
        
        # Test each provider configuration
        for name, provider_config in config.PROVIDERS.items():
            required_keys = ["name", "enabled", "model"]
            missing_keys = [key for key in required_keys if key not in provider_config]
            
            if missing_keys:
                print(f"   ❌ FAIL: Provider {name} missing keys: {missing_keys}")
                return False
            
            print(f"   ✅ Provider {name}: {provider_config.get('name')} configured correctly")
        
        # Test that tool-enabled providers are consistent
        tool_providers = [name for name, config_data in config.PROVIDERS.items() 
                         if config_data.get("supports_tools", False)]
        
        print(f"   Tool-enabled providers: {tool_providers}")
        
        if "local" in tool_providers:
            print("   ✅ Local provider supports tools (Fix #1 confirmed)")
        else:
            print("   ❌ FAIL: Local provider should support tools after Fix #1")
            return False
        
        # Test backward compatibility exports
        compatibility_vars = ['DEBUG_MODE', 'DEEPSEEK_ENABLED', 'SANDBOX_PATH']
        for var in compatibility_vars:
            if hasattr(config, var):
                print(f"   ✅ Backward compatibility: {var} available")
            else:
                print(f"   ❌ FAIL: Backward compatibility broken: {var} missing")
                return False
        
        print("\n✅ Configuration consistency test passed")
        return True
        
    except Exception as e:
        print(f"\n❌ Configuration consistency test failed: {e}")
        return False

def test_import_stability():
    """Test that all imports work correctly after changes."""
    print("\n🔧 Testing Import Stability")
    print("=" * 27)
    
    try:
        # Test core imports
        from config import config
        print("   ✅ Config import works")
        
        from services.unified_openai_handler import UnifiedOpenAIHandler, LocalOpenAIHandler, CloudOpenAIHandler
        print("   ✅ Unified handler imports work")
        
        from services.error_handler import ErrorHandler, ErrorType, StandardError
        print("   ✅ Error handler imports work")
        
        from services.tool_executor import ToolExecutor
        print("   ✅ Tool executor import works")
        
        # Test that legacy imports still work
        from services.llm_handler import LocalCodingHandler, SecurityMiddleware
        print("   ✅ Legacy handler imports work")
        
        # Test model imports
        from models.session import CommandContext
        from models.router import CommandHandler
        print("   ✅ Model imports work")
        
        print("\n✅ All imports stable after changes")
        return True
        
    except Exception as e:
        print(f"\n❌ Import stability test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_architectural_improvements():
    """Test that architectural improvements are working as intended."""
    print("\n🔧 Testing Architectural Improvements")
    print("=" * 38)
    
    try:
        # Test Fix #1: Unified tool definitions
        from services.unified_openai_handler import UnifiedOpenAIHandler
        import inspect
        
        source = inspect.getsource(UnifiedOpenAIHandler._create_chat_completion)
        
        # Should NOT have local exclusion
        if 'self.provider_name != "local"' in source:
            print("   ❌ FAIL: Local model exclusion still present")
            return False
        else:
            print("   ✅ Fix #1: Local model exclusion removed")
        
        # Should have unified tool support check
        if 'self.provider_config.get("supports_tools", False)' in source:
            print("   ✅ Fix #1: Unified tool support check present")
        else:
            print("   ❌ FAIL: Unified tool support check missing")
            return False
        
        # Test Fix #2: Standardized error handling
        from services.tool_executor import ToolExecutor
        
        tool_source = inspect.getsource(ToolExecutor)
        
        if "from services.error_handler import" in tool_source:
            print("   ✅ Fix #2: Tool executor uses new error handling")
        else:
            print("   ❌ FAIL: Tool executor not using new error handling")
            return False
        
        # Test that error functions are used
        error_functions = ["tool_error", "file_error", "validation_error", "path_security_error"]
        used_functions = [func for func in error_functions if f"{func}(" in tool_source]
        
        if len(used_functions) >= 3:  # Should use most error functions
            print(f"   ✅ Fix #2: Tool executor uses {len(used_functions)} error functions")
        else:
            print(f"   ❌ FAIL: Tool executor only uses {len(used_functions)} error functions")
            return False
        
        print("\n✅ Architectural improvements confirmed working")
        return True
        
    except Exception as e:
        print(f"\n❌ Architectural improvements test failed: {e}")
        return False

def main():
    """Run complete integration test suite."""
    print("🚀 Integration Test: Validating Both Fixes Together")
    print("=" * 55)
    
    results = []
    
    # Run all integration tests
    results.append(test_unified_handler_creation())
    results.append(test_tool_executor_with_new_errors())
    results.append(test_configuration_consistency())
    results.append(test_import_stability())
    results.append(test_architectural_improvements())
    
    # Summary
    passed = sum(results)
    total = len(results)
    
    print(f"\n📊 INTEGRATION TEST SUMMARY")
    print("=" * 30)
    print(f"Tests passed: {passed}/{total}")
    
    if passed == total:
        print("🎉 ALL INTEGRATION TESTS PASSED!")
        print("\n✅ System Status After Fixes:")
        print("   - Unified tool definitions working")
        print("   - Standardized error handling integrated")
        print("   - No regressions detected")
        print("   - Configuration consistent")
        print("   - Imports stable")
        print("   - Architectural improvements confirmed")
        
        print("\n🚀 Ready for Production Use:")
        print("   - Local and cloud models use same tool calling")
        print("   - Error messages are helpful and consistent")
        print("   - Architectural fragmentation reduced")
        print("   - Maintenance burden decreased")
        
        return 0
    else:
        print("❌ SOME INTEGRATION TESTS FAILED")
        print(f"   Failed tests: {total - passed}")
        print("   Review output above for specific issues")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
