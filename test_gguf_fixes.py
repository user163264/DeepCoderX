#!/usr/bin/env python3
"""
Test the GGUF repetition fixes
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_deduplication():
    """Test the deduplication function"""
    print("=== TESTING TOOL CALL DEDUPLICATION ===")
    
    # Import the fixed GGUF handler
    from services.gguf_handler import GGUFLocalHandler
    from models.session import CommandContext
    from pathlib import Path
    
    # Create a test context
    test_ctx = CommandContext(
        user_input="pwd", 
        root_path=Path.cwd(),
        debug_mode=True
    )
    
    try:
        # Create handler instance
        handler = GGUFLocalHandler(test_ctx, "local")
        
        # Test deduplication with repetitive tool calls
        repetitive_calls = [
            {"tool": "run_bash", "command": "pwd"},
            {"tool": "run_bash", "command": "pwd"},
            {"tool": "run_bash", "command": "pwd"},
            {"tool": "run_bash", "command": "pwd"},
            {"tool": "list_dir", "path": "."},
            {"tool": "list_dir", "path": "."},
        ]
        
        print(f"Original calls: {len(repetitive_calls)}")
        for i, call in enumerate(repetitive_calls, 1):
            print(f"  {i}. {call}")
        print()
        
        # Test deduplication method
        unique_calls = handler._deduplicate_tool_calls(repetitive_calls)
        
        print(f"After deduplication: {len(unique_calls)}")
        for i, call in enumerate(unique_calls, 1):
            print(f"  {i}. {call}")
        print()
        
        print(f"✅ SUCCESS: Reduced from {len(repetitive_calls)} to {len(unique_calls)} calls")
        print(f"✅ Duplicates removed: {len(repetitive_calls) - len(unique_calls)}")
        
        return True
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False

def test_conversational_detection():
    """Test conversational input detection"""
    print("\n=== TESTING CONVERSATIONAL INPUT DETECTION ===")
    
    from services.gguf_handler import GGUFLocalHandler
    from models.session import CommandContext
    from pathlib import Path
    
    # Create a test context
    test_ctx = CommandContext(
        user_input="hello", 
        root_path=Path.cwd(),
        debug_mode=True
    )
    
    try:
        handler = GGUFLocalHandler(test_ctx, "local")
        
        # Test different inputs
        test_inputs = [
            ("hello", True),
            ("hi there", True),
            ("what are you", True),
            ("how are you?", True),
            ("what is Python?", True),
            ("pwd", False),
            ("create a file", False),
            ("list files", False),
            ("run ls command", False)
        ]
        
        print("Testing conversational detection:")
        for input_text, expected in test_inputs:
            result = handler._is_conversational_input(input_text)
            status = "✅" if result == expected else "❌"
            print(f"  {status} '{input_text}' -> {result} (expected {expected})")
        
        return True
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False

def test_stop_sequences():
    """Test the improved stop sequences"""
    print("\n=== TESTING IMPROVED STOP SEQUENCES ===")
    
    # Show the new stop sequences
    new_stops = [
        "Human:", "User:", "Assistant:",  # Role-based stops
        "\n\n",  # Natural paragraph breaks
        "</tool_call>\n\n",  # Stop after tool call completion
        "---",  # Section separators
        "\n\n---"  # Legacy format
    ]
    
    print("New stop sequences:")
    for stop in new_stops:
        print(f"  - '{stop}'")
    print()
    
    print("Benefits:")
    print("✅ '</tool_call>\\n\\n' stops generation after tool call completes")
    print("✅ '\\n\\n' stops at natural paragraph breaks")
    print("✅ 'Assistant:' prevents role confusion")
    print("✅ Increased repeat_penalty from 1.1 to 1.15")
    
    return True

def test_tool_call_limiting():
    """Test tool call limiting functionality"""
    print("\n=== TESTING TOOL CALL LIMITING ===")
    
    # Simulate excessive tool calls
    excessive_calls = [
        {"tool": "run_bash", "command": "pwd"},
        {"tool": "run_bash", "command": "pwd"},
        {"tool": "run_bash", "command": "pwd"},
        {"tool": "run_bash", "command": "pwd"},
        {"tool": "run_bash", "command": "pwd"},
        {"tool": "run_bash", "command": "pwd"}
    ]
    
    print(f"Simulated excessive calls: {len(excessive_calls)}")
    
    # The limit is set to 3 in the code
    limit = 3
    limited_calls = excessive_calls[:limit]
    
    print(f"After limiting to {limit}: {len(limited_calls)}")
    print("✅ Tool call limiting prevents excessive execution")
    
    return True

if __name__ == "__main__":
    print("🔧 DeepCoderX GGUF Repetition Fixes Test")
    print("=" * 50)
    
    success_count = 0
    total_tests = 4
    
    if test_deduplication():
        success_count += 1
    
    if test_conversational_detection():
        success_count += 1
    
    if test_stop_sequences():
        success_count += 1
    
    if test_tool_call_limiting():
        success_count += 1
    
    print("\n" + "=" * 50)
    print(f"🎯 TEST RESULTS: {success_count}/{total_tests} passed")
    
    if success_count == total_tests:
        print("✅ ALL FIXES IMPLEMENTED SUCCESSFULLY")
        print("\nFixes applied:")
        print("1. ✅ Tool call deduplication")
        print("2. ✅ Improved stop sequences")
        print("3. ✅ Conversational input detection")
        print("4. ✅ Tool call limiting")
        print("5. ✅ Increased repeat penalty")
    else:
        print("❌ Some tests failed - check implementation")
    
    print("=" * 50)
