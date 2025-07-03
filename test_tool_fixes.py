#!/usr/bin/env python3
"""
Quick test script to validate the tool fixes.
Tests the enhanced error messages and path resolution.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.structured_tools import StructuredToolParser, EnhancedToolExecutor, StructuredToolCall
from services.tool_executor import ToolExecutor
from pathlib import Path

def test_enhanced_error_messages():
    """Test that error messages are helpful and guide the model correctly."""
    
    print("🧪 Testing Enhanced Error Messages\n")
    
    # Test 1: Invalid tool name
    parser = StructuredToolParser(debug=True)
    
    print("1. Testing invalid tool name...")
    try:
        invalid_call = StructuredToolCall("invalid_tool", {}, '{"tool": "invalid_tool"}')
        invalid_call.validate()
    except Exception as e:
        print(f"✅ Got expected error: {e}\n")
    
    # Test 2: Missing required parameters
    print("2. Testing missing required parameters...")
    try:
        invalid_call = StructuredToolCall("read_file", {}, '{"tool": "read_file"}')
        invalid_call.validate()
    except Exception as e:
        print(f"✅ Got expected error: {e}\n")
    
    # Test 3: JSON parsing with helpful messages
    print("3. Testing JSON parsing errors...")
    invalid_json_responses = [
        '{"tool": "read_file"',  # Missing closing brace
        '{"tool": "read_file", "path":}',  # Invalid JSON
        'read_file config.py',  # Not JSON at all
    ]
    
    for invalid_json in invalid_json_responses:
        tool_calls = parser.parse_tool_calls(invalid_json)
        print(f"   Input: {invalid_json}")
        print(f"   Result: {len(tool_calls)} valid calls found")
    
    print("\n4. Testing valid JSON parsing...")
    valid_responses = [
        '{"tool": "read_file", "path": "config.py"}',
        '{"tool": "write_file", "path": "script.py", "content": "print(\\'hello\\')"}',
        '{"tool": "list_dir", "path": "."}',
    ]
    
    for valid_json in valid_responses:
        tool_calls = parser.parse_tool_calls(valid_json)
        print(f"   Input: {valid_json}")
        print(f"   Result: {len(tool_calls)} valid calls found")
        if tool_calls:
            print(f"   Tool: {tool_calls[0].tool_name}, Params: {tool_calls[0].parameters}")
    
    print("\n✅ Error message testing completed!")

def test_path_resolution_guidance():
    """Test that path resolution errors provide clear guidance."""
    
    print("\n🧪 Testing Path Resolution Guidance\n")
    
    # Mock context class for testing
    class MockContext:
        def __init__(self):
            self.root_path = Path("/Users/admin/Documents/DeepCoderX")
        
        class MockMCPClient:
            def read_file(self, path):
                return {"error": "File not found"}
            def write_file(self, path, content):
                return {"error": "Permission denied"}
            def list_dir(self, path):
                return {"error": "Directory not found"}
        
        mcp_client = MockMCPClient()
    
    mock_ctx = MockContext()
    executor = ToolExecutor(mock_ctx, use_complex_path_resolution=True)
    
    # Test absolute path rejection
    print("1. Testing absolute path rejection...")
    result = executor.execute_tool({"tool": "read_file", "path": "/Users/admin/Documents/example.txt"})
    print(f"   Result: {result[:100]}...\n")
    
    # Test missing path parameter
    print("2. Testing missing path parameter...")
    result = executor.execute_tool({"tool": "read_file"})
    print(f"   Result: {result[:100]}...\n")
    
    # Test valid relative path (should proceed to MCP client)
    print("3. Testing valid relative path...")
    result = executor.execute_tool({"tool": "read_file", "path": "config.py"})
    print(f"   Result: {result[:100]}...\n")
    
    print("✅ Path resolution testing completed!")

if __name__ == "__main__":
    test_enhanced_error_messages()
    test_path_resolution_guidance()
    print("\n🎉 All tests completed! The tool fixes should now provide much better guidance.")
