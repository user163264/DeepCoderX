#!/usr/bin/env python3
"""
Tool Registry Pattern Test Suite

This script validates that the Tool Registry Pattern is working correctly
and provides the intended benefits of centralized tool management.
"""

import sys
import os
import json
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

class ToolRegistryTester:
    """Test harness for Tool Registry Pattern functionality."""
    
    def __init__(self):
        self.test_results = []
        
    def test_tool_registry_creation(self):
        """Test that the tool registry can be created and initialized."""
        print("🔧 Testing Tool Registry Creation")
        print("=" * 33)
        
        try:
            from services.tool_registry import ToolRegistry, ToolDefinition, ToolCategory, ToolPermission
            
            # Test registry creation
            registry = ToolRegistry()
            print("   ✅ Tool registry created successfully")
            
            # Test that core tools are registered
            tool_names = registry.get_tool_names()
            expected_tools = ["read_file", "write_file", "list_dir", "run_bash"]
            
            print(f"   📋 Registered tools: {tool_names}")
            
            for expected_tool in expected_tools:
                if expected_tool in tool_names:
                    print(f"   ✅ {expected_tool} registered")
                else:
                    print(f"   ❌ {expected_tool} missing")
                    return False
            
            # Test tool categories
            categories = list(ToolCategory)
            print(f"   📂 Available categories: {[c.value for c in categories]}")
            
            # Test tool permissions
            permissions = list(ToolPermission)
            print(f"   🔒 Available permissions: {[p.value for p in permissions]}")
            
            print("   ✅ Tool registry creation test passed")
            return True
            
        except Exception as e:
            print(f"   ❌ Tool registry creation test failed: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def test_tool_definition_structure(self):
        """Test tool definition structure and validation."""
        print("\n🔍 Testing Tool Definition Structure")
        print("=" * 37)
        
        try:
            from services.tool_registry import tool_registry
            
            # Test read_file tool definition
            read_file_tool = tool_registry.get_tool("read_file")
            
            if not read_file_tool:
                print("   ❌ read_file tool not found in registry")
                return False
            
            print(f"   📋 Testing read_file tool:")
            print(f"      Name: {read_file_tool.name}")
            print(f"      Description: {read_file_tool.description}")
            print(f"      Category: {read_file_tool.category.value}")
            print(f"      Permission: {read_file_tool.permission.value}")
            print(f"      Parameters: {len(read_file_tool.parameters)}")
            
            # Test parameter structure
            if read_file_tool.parameters:
                param = read_file_tool.parameters[0]
                print(f"         - {param.name} ({param.type}): {param.description}")
                print(f"           Required: {param.required}")
            
            # Test OpenAI format conversion
            openai_format = read_file_tool.to_openai_format()
            
            if "type" in openai_format and openai_format["type"] == "function":
                print("   ✅ OpenAI format conversion works")
            else:
                print("   ❌ OpenAI format conversion failed")
                return False
            
            # Test validation
            valid_call = {"tool": "read_file", "path": "test.txt"}
            invalid_call = {"tool": "read_file"}  # Missing path
            
            valid_errors = read_file_tool.validate_call(valid_call)
            invalid_errors = read_file_tool.validate_call(invalid_call)
            
            if len(valid_errors) == 0:
                print("   ✅ Valid tool call validation passed")
            else:
                print(f"   ❌ Valid tool call incorrectly flagged: {valid_errors}")
                return False
            
            if len(invalid_errors) > 0:
                print("   ✅ Invalid tool call correctly detected")
            else:
                print("   ❌ Invalid tool call not detected")
                return False
            
            print("   ✅ Tool definition structure test passed")
            return True
            
        except Exception as e:
            print(f"   ❌ Tool definition structure test failed: {e}")
            return False
    
    def test_provider_specific_tool_access(self):
        """Test that different providers get appropriate tools."""
        print("\n🔒 Testing Provider-Specific Tool Access")
        print("=" * 39)
        
        try:
            from services.tool_registry import get_tools_for_provider
            from config import config
            
            # Test local provider tools
            local_config = config.PROVIDERS.get("local", {})
            local_tools = get_tools_for_provider("local", local_config)
            
            print(f"   🏠 Local provider tools: {len(local_tools)}")
            local_tool_names = [tool["function"]["name"] for tool in local_tools]
            print(f"      Tools: {local_tool_names}")
            
            # Local provider should get system access tools
            if "run_bash" in local_tool_names:
                print("   ✅ Local provider has system access tools")
            else:
                print("   ⚠️  Local provider missing system access tools")
            
            # Test cloud provider tools
            deepseek_config = config.PROVIDERS.get("deepseek", {})
            if deepseek_config:
                cloud_tools = get_tools_for_provider("deepseek", deepseek_config)
                
                print(f"   ☁️  Cloud provider tools: {len(cloud_tools)}")
                cloud_tool_names = [tool["function"]["name"] for tool in cloud_tools]
                print(f"      Tools: {cloud_tool_names}")
                
                # Cloud providers should have restricted access
                if "read_file" in cloud_tool_names and "write_file" in cloud_tool_names:
                    print("   ✅ Cloud provider has basic file operations")
                else:
                    print("   ❌ Cloud provider missing basic file operations")
                    return False
            
            # Test provider without tool support
            no_tools_config = {"supports_tools": False}
            no_tools = get_tools_for_provider("test", no_tools_config)
            
            if len(no_tools) == 0:
                print("   ✅ Providers without tool support get no tools")
            else:
                print("   ❌ Providers without tool support incorrectly got tools")
                return False
            
            print("   ✅ Provider-specific tool access test passed")
            return True
            
        except Exception as e:
            print(f"   ❌ Provider-specific tool access test failed: {e}")
            return False
    
    def test_unified_handler_integration(self):
        """Test that unified handlers use the tool registry correctly."""
        print("\n🔗 Testing Unified Handler Integration")
        print("=" * 37)
        
        try:
            from services.unified_openai_handler import UnifiedOpenAIHandler
            import inspect
            
            # Check that the unified handler imports tool registry
            source = inspect.getsource(UnifiedOpenAIHandler)
            
            if "from services.tool_registry import" in source:
                print("   ✅ Unified handler imports tool registry")
            else:
                print("   ❌ Unified handler missing tool registry import")
                return False
            
            # Check that _get_tool_definitions uses registry
            method_source = inspect.getsource(UnifiedOpenAIHandler._get_tool_definitions)
            
            if "get_tools_for_provider" in method_source:
                print("   ✅ _get_tool_definitions uses tool registry")
            else:
                print("   ❌ _get_tool_definitions not using tool registry")
                return False
            
            # Check that hardcoded tools were removed
            if "read_file" not in method_source or "type\": \"function" not in method_source:
                print("   ✅ Hardcoded tool definitions removed")
            else:
                print("   ❌ Hardcoded tool definitions still present")
                return False
            
            # Test that the method can be called
            tools = UnifiedOpenAIHandler._get_tool_definitions(None)
            
            if isinstance(tools, list) and len(tools) > 0:
                print(f"   ✅ Tool definitions method returns {len(tools)} tools")
            else:
                print("   ❌ Tool definitions method not returning tools")
                return False
            
            print("   ✅ Unified handler integration test passed")
            return True
            
        except Exception as e:
            print(f"   ❌ Unified handler integration test failed: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def test_tool_validation_system(self):
        """Test the tool validation system."""
        print("\n✅ Testing Tool Validation System")
        print("=" * 34)
        
        try:
            from services.tool_registry import tool_registry
            
            # Test valid tool calls
            valid_calls = [
                {"tool": "read_file", "path": "test.txt"},
                {"tool": "write_file", "path": "output.txt", "content": "test"},
                {"tool": "list_dir", "path": "."},
                {"tool": "run_bash", "command": "ls"}
            ]
            
            for call in valid_calls:
                result = tool_registry.validate_tool_call(call)
                if result["valid"]:
                    print(f"   ✅ Valid call validated: {call['tool']}")
                else:
                    print(f"   ❌ Valid call rejected: {call['tool']} - {result['errors']}")
                    return False
            
            # Test invalid tool calls
            invalid_calls = [
                {"tool": "nonexistent_tool"},
                {"tool": "read_file"},  # Missing path
                {"path": "test.txt"},  # Missing tool name
                {"tool": "write_file", "path": "test.txt"}  # Missing content
            ]
            
            for call in invalid_calls:
                result = tool_registry.validate_tool_call(call)
                if not result["valid"]:
                    tool_name = call.get("tool", "missing")
                    print(f"   ✅ Invalid call rejected: {tool_name}")
                else:
                    print(f"   ❌ Invalid call incorrectly accepted: {call}")
                    return False
            
            # Test error messages and suggestions
            result = tool_registry.validate_tool_call({"tool": "read_file"})
            if result.get("suggestions"):
                print("   ✅ Validation provides helpful suggestions")
            else:
                print("   ⚠️  Validation missing suggestions")
            
            print("   ✅ Tool validation system test passed")
            return True
            
        except Exception as e:
            print(f"   ❌ Tool validation system test failed: {e}")
            return False
    
    def test_tool_documentation_export(self):
        """Test tool documentation export functionality."""
        print("\n📚 Testing Tool Documentation Export")
        print("=" * 37)
        
        try:
            from services.tool_registry import tool_registry
            
            # Test documentation export
            docs = tool_registry.export_tool_documentation()
            
            if isinstance(docs, str) and len(docs) > 100:
                print(f"   ✅ Documentation exported: {len(docs)} characters")
            else:
                print("   ❌ Documentation export failed or too short")
                return False
            
            # Check that documentation contains expected sections
            expected_sections = ["read_file", "write_file", "list_dir", "run_bash"]
            
            for section in expected_sections:
                if section in docs:
                    print(f"   ✅ Documentation includes {section}")
                else:
                    print(f"   ❌ Documentation missing {section}")
                    return False
            
            # Check for parameter documentation
            if "Parameters:" in docs and "Examples:" in docs:
                print("   ✅ Documentation includes parameters and examples")
            else:
                print("   ❌ Documentation missing parameters or examples")
                return False
            
            print("   ✅ Tool documentation export test passed")
            return True
            
        except Exception as e:
            print(f"   ❌ Tool documentation export test failed: {e}")
            return False
    
    def test_extensibility(self):
        """Test that the tool registry is extensible."""
        print("\n🔧 Testing Tool Registry Extensibility")
        print("=" * 37)
        
        try:
            from services.tool_registry import ToolRegistry, ToolDefinition, ToolCategory, ToolPermission, ToolParameter
            
            # Create a test registry
            test_registry = ToolRegistry()
            
            # Create a custom tool
            custom_tool = ToolDefinition(
                name="test_tool",
                description="A test tool for extensibility testing",
                category=ToolCategory.UTILITY_TOOLS,
                permission=ToolPermission.READ_ONLY,
                parameters=[
                    ToolParameter("input", "string", "Test input parameter")
                ],
                examples=['{"tool": "test_tool", "input": "test"}']
            )
            
            # Register the custom tool
            test_registry.register_tool(custom_tool)
            
            # Verify it was registered
            if "test_tool" in test_registry.get_tool_names():
                print("   ✅ Custom tool registration works")
            else:
                print("   ❌ Custom tool registration failed")
                return False
            
            # Test tool retrieval
            retrieved_tool = test_registry.get_tool("test_tool")
            if retrieved_tool and retrieved_tool.name == "test_tool":
                print("   ✅ Custom tool retrieval works")
            else:
                print("   ❌ Custom tool retrieval failed")
                return False
            
            # Test tool unregistration
            if test_registry.unregister_tool("test_tool"):
                print("   ✅ Tool unregistration works")
            else:
                print("   ❌ Tool unregistration failed")
                return False
            
            # Verify it was removed
            if "test_tool" not in test_registry.get_tool_names():
                print("   ✅ Tool successfully removed")
            else:
                print("   ❌ Tool removal failed")
                return False
            
            print("   ✅ Tool registry extensibility test passed")
            return True
            
        except Exception as e:
            print(f"   ❌ Tool registry extensibility test failed: {e}")
            return False
    
    def run_comprehensive_test(self):
        """Run all tool registry tests."""
        print("🛠️  Tool Registry Pattern Comprehensive Test")
        print("=" * 48)
        
        results = []
        
        # Run all tests
        results.append(self.test_tool_registry_creation())
        results.append(self.test_tool_definition_structure())
        results.append(self.test_provider_specific_tool_access())
        results.append(self.test_unified_handler_integration())
        results.append(self.test_tool_validation_system())
        results.append(self.test_tool_documentation_export())
        results.append(self.test_extensibility())
        
        # Summary
        passed = sum(results)
        total = len(results)
        
        print(f"\n📊 TOOL REGISTRY TEST SUMMARY")
        print("=" * 31)
        print(f"Tests passed: {passed}/{total}")
        
        if passed == total:
            print("🎉 ALL TOOL REGISTRY TESTS PASSED!")
            print("\n✅ Tool Registry Pattern Benefits Achieved:")
            print("   - Centralized tool management")
            print("   - Eliminated hardcoded tool definitions")
            print("   - Provider-specific tool permissions")
            print("   - Comprehensive validation system")
            print("   - Automatic documentation generation")
            print("   - Extensible architecture for new tools")
            
            print("\n🎯 Architectural Improvements:")
            print("   - Single source of truth for all tools")
            print("   - Consistent tool definitions across handlers")
            print("   - Easy to add/remove/modify tools")
            print("   - Better security through permission levels")
            print("   - Improved error messages and validation")
            
            return True
        else:
            print("❌ SOME TOOL REGISTRY TESTS FAILED")
            print(f"   Issues: {total - passed} tests")
            return False

def main():
    """Main test execution."""
    tester = ToolRegistryTester()
    success = tester.run_comprehensive_test()
    
    if success:
        print("\n🚀 TOOL REGISTRY PATTERN SUCCESSFULLY IMPLEMENTED")
        return 0
    else:
        print("\n⚠️  REVIEW TOOL REGISTRY ISSUES")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
