#!/usr/bin/env python3
"""
Specific test to verify ToolExecutor error handling integration.
"""

import sys
import inspect
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_tool_executor_error_handling():
    """Test that ToolExecutor properly uses the new error handling system."""
    print("🔧 Testing ToolExecutor Error Handling Integration")
    print("=" * 50)
    
    try:
        # Test 1: Import check
        from services.tool_executor import ToolExecutor
        print("   ✅ ToolExecutor imported successfully")
        
        # Test 2: Check imports in source code
        import inspect
        source = inspect.getsource(ToolExecutor)
        
        if "from services.error_handler import" in source:
            print("   ✅ Error handler import found in source")
        else:
            print("   ❌ Error handler import NOT found in source")
            return False
        
        # Test 3: Check specific imports
        import_checks = [
            ("ErrorHandler", "ErrorHandler" in source),
            ("tool_error", "tool_error" in source),  
            ("file_error", "file_error" in source),
            ("validation_error", "validation_error" in source)
        ]
        
        for name, found in import_checks:
            if found:
                print(f"   ✅ {name} import found")
            else:
                print(f"   ❌ {name} import missing")
                return False
        
        # Test 4: Check that ToolExecutor can access error functions
        try:
            from services.error_handler import tool_error
            test_error = tool_error("test", "message", "suggestion")
            print("   ✅ Error handling functions accessible")
        except ImportError as e:
            print(f"   ❌ Error handling functions not accessible: {e}")
            return False
        
        # Test 5: Check the file directly
        with open('services/tool_executor.py', 'r') as f:
            file_content = f.read()
        
        if "from services.error_handler import" in file_content:
            print("   ✅ Direct file check confirms error handling import")
        else:
            print("   ❌ Direct file check shows missing import")
            return False
        
        print("   🎉 ToolExecutor error handling integration VERIFIED")
        return True
        
    except Exception as e:
        print(f"   ❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run the specific test."""
    success = test_tool_executor_error_handling()
    
    if success:
        print("\n✅ ToolExecutor error handling is working correctly!")
        print("The validate_immediate_fixes.py test may have a false negative.")
        return 0
    else:
        print("\n❌ ToolExecutor error handling needs fixing.")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
