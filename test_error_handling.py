#!/usr/bin/env python3
"""
Test script to validate Fix #2: Standardized Error Handling

This test verifies that the new error handling system provides consistent,
helpful error messages across all tool operations.
"""

import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_error_handler_creation():
    """Test that the error handler module and classes work correctly."""
    print("🔧 Testing Error Handler Module")
    print("=" * 32)
    
    try:
        from services.error_handler import (
            ErrorHandler, ErrorType, StandardError,
            tool_error, file_error, validation_error, path_security_error
        )
        
        print("   ✅ Error handler imports successful")
        
        # Test StandardError creation
        error = StandardError(
            type=ErrorType.TOOL_EXECUTION_ERROR,
            message="Test error message",
            suggestions="Test suggestion",
            details={"test": "data"}
        )
        
        print(f"   ✅ StandardError creation works: {error.type}")
        
        # Test ErrorHandler methods
        tool_err = ErrorHandler.create_tool_error("test_tool", "test message", "test suggestion")
        if tool_err.type == ErrorType.TOOL_EXECUTION_ERROR:
            print("   ✅ ErrorHandler.create_tool_error works")
        else:
            print("   ❌ FAIL: ErrorHandler.create_tool_error incorrect type")
            return False
        
        # Test error formatting
        formatted = ErrorHandler.format_error(tool_err)
        if "[red]" in formatted and "test message" in formatted:
            print("   ✅ Error formatting works")
        else:
            print("   ❌ FAIL: Error formatting incorrect")
            return False
        
        # Test convenience functions
        tool_test = tool_error("test", "message", "suggestion")
        file_test = file_error("read", "test.txt", "not found")
        val_test = validation_error("path", None, "string")
        sec_test = path_security_error("/absolute/path")
        
        if all(isinstance(err, str) and "[red]" in err for err in [tool_test, file_test, val_test, sec_test]):
            print("   ✅ All convenience functions work")
        else:
            print("   ❌ FAIL: Some convenience functions not working")
            return False
        
        print("\n✅ Error handler module fully functional")
        return True
        
    except Exception as e:
        print(f"\n❌ Error handler test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_tool_executor_integration():
    """Test that tool executor uses the new error handling."""
    print("\n🔧 Testing Tool Executor Integration")
    print("=" * 37)
    
    try:
        from services.tool_executor import ToolExecutor
        from services.error_handler import ErrorHandler
        
        # Check imports in tool executor
        import inspect
        source = inspect.getsource(ToolExecutor)
        
        if "from services.error_handler import" in source:
            print("   ✅ ToolExecutor imports new error handling")
        else:
            print("   ❌ FAIL: ToolExecutor not using new error handling")
            return False
        
        # Check if key methods use new error functions
        if "tool_error(" in source:
            print("   ✅ ToolExecutor uses tool_error function")
        else:
            print("   ❌ FAIL: ToolExecutor not using tool_error")
            return False
        
        if "file_error(" in source:
            print("   ✅ ToolExecutor uses file_error function")
        else:
            print("   ❌ FAIL: ToolExecutor not using file_error")
            return False
        
        if "validation_error(" in source:
            print("   ✅ ToolExecutor uses validation_error function")
        else:
            print("   ❌ FAIL: ToolExecutor not using validation_error")
            return False
        
        print("\n✅ Tool executor properly integrated with new error handling")
        return True
        
    except Exception as e:
        print(f"\n❌ Tool executor integration test failed: {e}")
        return False

def test_error_message_quality():
    """Test that error messages are helpful and consistent."""
    print("\n🔧 Testing Error Message Quality")
    print("=" * 33)
    
    try:
        from services.error_handler import tool_error, file_error, validation_error
        
        # Test tool error
        tool_err = tool_error("read_file", "File not found", "Check the file path")
        print(f"   Tool error example: {tool_err[:60]}...")
        
        if "Tool Execution Error" in tool_err and "Suggestions:" in tool_err:
            print("   ✅ Tool error has proper structure and suggestions")
        else:
            print("   ❌ FAIL: Tool error missing structure or suggestions")
            return False
        
        # Test file error
        file_err = file_error("read", "config.py", "File not found", "Check spelling")
        print(f"   File error example: {file_err[:60]}...")
        
        if "File Not Found" in file_err and "Suggestions:" in file_err:
            print("   ✅ File error has proper structure and suggestions")
        else:
            print("   ❌ FAIL: File error missing structure or suggestions")
            return False
        
        # Test validation error
        val_err = validation_error("tool", "invalid_tool", "one of: read_file, write_file")
        print(f"   Validation error example: {val_err[:60]}...")
        
        if "Validation Error" in val_err and "expected" in val_err:
            print("   ✅ Validation error has proper structure")
        else:
            print("   ❌ FAIL: Validation error missing structure")
            return False
        
        print("\n✅ Error messages are high quality with helpful information")
        return True
        
    except Exception as e:
        print(f"\n❌ Error message quality test failed: {e}")
        return False

def test_error_consistency():
    """Test that errors are consistent across different scenarios."""
    print("\n🔧 Testing Error Consistency")
    print("=" * 29)
    
    try:
        from services.error_handler import ErrorHandler, ErrorType
        
        # Test that same error types produce consistent formatting
        error1 = ErrorHandler.create_tool_error("tool1", "message1", "suggestion1")
        error2 = ErrorHandler.create_tool_error("tool2", "message2", "suggestion2")
        
        formatted1 = ErrorHandler.format_error(error1)
        formatted2 = ErrorHandler.format_error(error2)
        
        # Both should start with same error type
        if formatted1.startswith("[red]Tool Execution Error:[/]") and formatted2.startswith("[red]Tool Execution Error:[/]"):
            print("   ✅ Tool errors have consistent format prefix")
        else:
            print("   ❌ FAIL: Tool errors have inconsistent format")
            return False
        
        # Both should have suggestions section
        if "💡 Suggestions:" in formatted1 and "💡 Suggestions:" in formatted2:
            print("   ✅ Tool errors consistently include suggestions")
        else:
            print("   ❌ FAIL: Tool errors inconsistently include suggestions")
            return False
        
        # Test API errors
        api_error1 = ErrorHandler.create_api_error("provider1", 401)
        api_error2 = ErrorHandler.create_api_error("provider2", 429)
        
        if api_error1.type == ErrorType.API_AUTHENTICATION_ERROR and api_error2.type == ErrorType.API_RATE_LIMIT_ERROR:
            print("   ✅ API errors correctly categorized by status code")
        else:
            print("   ❌ FAIL: API errors not properly categorized")
            return False
        
        print("\n✅ Error handling is consistent across all scenarios")
        return True
        
    except Exception as e:
        print(f"\n❌ Error consistency test failed: {e}")
        return False

def test_backwards_compatibility():
    """Test that legacy error patterns still work if needed."""
    print("\n🔧 Testing Backwards Compatibility")
    print("=" * 34)
    
    try:
        from services.error_handler import LegacyErrorFormats
        
        # Test legacy format functions
        legacy1 = LegacyErrorFormats.tool_not_found("invalid_tool")
        legacy2 = LegacyErrorFormats.missing_parameter("read_file", "path")
        legacy3 = LegacyErrorFormats.file_not_found("missing.txt")
        
        if all("[red]Error:[/]" in err for err in [legacy1, legacy2, legacy3]):
            print("   ✅ Legacy error formats still work")
        else:
            print("   ❌ FAIL: Legacy error formats broken")
            return False
        
        print("   ✅ Backwards compatibility maintained")
        return True
        
    except Exception as e:
        print(f"\n❌ Backwards compatibility test failed: {e}")
        return False

def main():
    """Run all error handling tests."""
    print("🚀 Testing Fix #2: Standardized Error Handling")
    print("=" * 50)
    
    results = []
    
    # Run tests
    results.append(test_error_handler_creation())
    results.append(test_tool_executor_integration())
    results.append(test_error_message_quality())
    results.append(test_error_consistency())
    results.append(test_backwards_compatibility())
    
    # Summary
    passed = sum(results)
    total = len(results)
    
    print(f"\n📊 ERROR HANDLING TEST SUMMARY")
    print("=" * 32)
    print(f"Tests passed: {passed}/{total}")
    
    if passed == total:
        print("🎉 ALL ERROR HANDLING TESTS PASSED!")
        print("\n✅ Confirmed:")
        print("   - Error handler module fully functional")
        print("   - Tool executor properly integrated")
        print("   - Error messages are helpful and consistent")
        print("   - All error types work correctly")
        print("   - Backwards compatibility maintained")
        return 0
    else:
        print("❌ SOME ERROR HANDLING TESTS FAILED")
        print(f"   Failed tests: {total - passed}")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
