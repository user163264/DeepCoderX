#!/usr/bin/env python3
"""
Test script to validate the DeepCoderX tool parsing fixes.
"""

from services.structured_tools import StructuredToolParser, EnhancedToolExecutor
from services.tool_executor import ToolExecutor
from models.session import CommandContext
from pathlib import Path

def test_json_parsing():
    """Test the JSON parsing with the problematic case from the debug output."""
    
    # The exact problematic JSON from the debug output
    problematic_json = '''{"tool": "write_file", "path": "word_counter.py", "content": "# Word Counter Script
user_input = input('Enter a phrase: ')
word_count = len(user_input.split())
print(f'Number of words: {word_count}')"}'''
    
    print("Testing JSON parsing fix...")
    print("=" * 50)
    
    parser = StructuredToolParser(debug=True)
    
    try:
        tool_calls = parser.parse_tool_calls(problematic_json)
        
        if tool_calls:
            print(f"✅ Successfully parsed {len(tool_calls)} tool call(s)")
            for call in tool_calls:
                print(f"   Tool: {call.tool_name}")
                print(f"   Path: {call.parameters.get('path', 'N/A')}")
                content = call.parameters.get('content', '')
                print(f"   Content length: {len(content)} chars")
                print(f"   Content preview: {content[:50]}...")
        else:
            print("❌ No tool calls parsed")
            
    except Exception as e:
        print(f"❌ Parsing failed: {e}")
    
    print("=" * 50)

def test_simple_cases():
    """Test simple valid JSON cases to ensure we didn't break anything."""
    
    simple_cases = [
        '{"tool": "read_file", "path": "config.py"}',
        '{"tool": "list_dir", "path": "."}',
        '{"tool": "run_bash", "command": "ls -la"}',
        '{"tool": "write_file", "path": "test.py", "content": "print(\\"hello\\")"}',
    ]
    
    print("Testing simple valid cases...")
    print("=" * 50)
    
    parser = StructuredToolParser(debug=False)
    
    for i, case in enumerate(simple_cases, 1):
        try:
            tool_calls = parser.parse_tool_calls(case)
            if tool_calls:
                call = tool_calls[0]
                print(f"✅ Test {i}: {call.tool_name} - OK")
            else:
                print(f"❌ Test {i}: No tool calls parsed")
        except Exception as e:
            print(f"❌ Test {i}: {e}")
    
    print("=" * 50)

if __name__ == "__main__":
    test_json_parsing()
    test_simple_cases()
    print("Tool parsing tests completed!")
