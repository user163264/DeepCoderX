#!/usr/bin/env python3
"""
Debug script to analyze the GGUF repetition issue
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.gguf_tool_parser import GGUFToolCallParser
from services.gguf_response_postprocessor import GGUFResponsePostProcessor
from services.gguf_tool_prompt import GGUFToolPromptBuilder

def analyze_repetitive_response():
    """Analyze the repetitive response from debug output"""
    
    # The actual problematic response from the debug output
    problematic_response = """<tool_call>run_bash({"command": "pwd"})</tool_call>
<tool_call>run_bash({"command": "pwd"})</tool_call>
<tool_call>run_bash({"command": "pwd"})</tool_call>
<tool_call>run_bash({"command": "pwd"})</tool_call>"""
    
    print("=== ANALYZING REPETITIVE GGUF RESPONSE ===")
    print(f"Raw response: {problematic_response}")
    print()
    
    # Test the parser
    parser = GGUFToolCallParser()
    tool_calls, clean_response = parser.parse_and_execute_format(problematic_response)
    
    print(f"Parser found {len(tool_calls)} tool calls:")
    for i, call in enumerate(tool_calls, 1):
        print(f"  {i}. {call}")
    print()
    
    print(f"Clean response: '{clean_response}'")
    print()
    
    # Test diagnostics
    diagnostics = parser.get_parsing_diagnostics(problematic_response)
    print("=== PARSER DIAGNOSTICS ===")
    print(f"Has tool calls: {diagnostics['has_tool_calls']}")
    print(f"Primary pattern matches: {diagnostics['primary_pattern_matches']}")
    print(f"Successfully parsed: {diagnostics['successfully_parsed']}")
    print()
    
    # The issue: Multiple identical tool calls being executed
    print("=== ISSUE ANALYSIS ===")
    print(f"❌ PROBLEM: {len(tool_calls)} identical tool calls detected")
    print(f"❌ EFFECT: Each tool call executes separately, causing excessive output")
    print(f"❌ SYMPTOM: Multiple 'pwd' commands run in sequence")
    print()
    
    return tool_calls

def test_deduplication_solution():
    """Test a deduplication solution"""
    
    print("=== TESTING DEDUPLICATION SOLUTION ===")
    
    # Sample repetitive tool calls
    repetitive_calls = [
        {"tool": "run_bash", "command": "pwd"},
        {"tool": "run_bash", "command": "pwd"},
        {"tool": "run_bash", "command": "pwd"},
        {"tool": "run_bash", "command": "pwd"},
        {"tool": "run_bash", "command": "pwd"}
    ]
    
    print(f"Original calls: {len(repetitive_calls)}")
    for call in repetitive_calls:
        print(f"  - {call}")
    print()
    
    # Simple deduplication by converting to frozenset of items
    unique_calls = []
    seen = set()
    
    for call in repetitive_calls:
        # Create a hashable representation
        call_signature = tuple(sorted(call.items()))
        if call_signature not in seen:
            seen.add(call_signature)
            unique_calls.append(call)
    
    print(f"After deduplication: {len(unique_calls)}")
    for call in unique_calls:
        print(f"  - {call}")
    print()
    
    print(f"✅ SOLUTION: Reduced from {len(repetitive_calls)} to {len(unique_calls)} calls")
    return unique_calls

def analyze_why_repetition_occurs():
    """Analyze why the model generates repetitive tool calls"""
    
    print("=== WHY REPETITION OCCURS ===")
    print()
    
    print("POSSIBLE CAUSES:")
    print("1. 🎯 Model stops mid-generation, continues with same pattern")
    print("2. 🔄 Progressive prompting adds more examples, confusing model")
    print("3. 📝 Chat template formatting issues")
    print("4. 🛑 Missing proper stop sequences")
    print("5. ⚙️ Temperature/sampling parameters")
    print()
    
    print("EVIDENCE FROM DEBUG OUTPUT:")
    print("- GGUF iteration 1/5: Generated 5 identical tool calls")
    print("- Raw response shows exact repetition")
    print("- Model didn't add any text explanation")
    print("- All tool calls have identical parameters")
    print()
    
    print("LIKELY ROOT CAUSE:")
    print("🎯 The model generates one tool call correctly, then continues the pattern")
    print("   without understanding it should stop or provide explanation text.")
    print()
    
    print("SOLUTIONS TO TEST:")
    print("1. ✅ Add deduplication in parser")
    print("2. 🛑 Improve stop sequences") 
    print("3. 📝 Adjust chat template")
    print("4. 🎲 Fine-tune temperature/top-p")
    print("5. 📏 Limit max_tokens per generation")
    
def test_stop_sequences():
    """Test stop sequence suggestions"""
    
    print("\n=== STOP SEQUENCE ANALYSIS ===")
    
    current_stops = ["Human:", "User:", "\n\n---"]
    print(f"Current stop sequences: {current_stops}")
    print()
    
    suggested_stops = [
        "</tool_call>\n",  # Stop after closing tool call tag
        "<tool_call>",     # Prevent multiple tool calls (controversial)
        "\n\n",           # Stop at double newline
        "Human:",          # Current
        "User:",           # Current  
        "Assistant:",      # Stop if model tries to continue conversation
        "---"              # Current (simplified)
    ]
    
    print("SUGGESTED IMPROVED STOP SEQUENCES:")
    for stop in suggested_stops:
        print(f"  - '{stop}'")
    print()
    
    print("ANALYSIS:")
    print("✅ '</tool_call>\\n' would stop after first tool call completes")
    print("⚠️  '<tool_call>' would prevent multiple calls but might be too restrictive")
    print("✅ '\\n\\n' would stop at natural paragraph breaks")
    print("✅ 'Assistant:' prevents model from role-playing conversation")

if __name__ == "__main__":
    print("🔍 DeepCoderX GGUF Repetition Issue Analysis")
    print("=" * 60)
    print()
    
    # Run analysis
    tool_calls = analyze_repetitive_response()
    unique_calls = test_deduplication_solution()
    analyze_why_repetition_occurs()
    test_stop_sequences()
    
    print("\n" + "=" * 60)
    print("🎯 RECOMMENDED FIXES:")
    print("1. Add tool call deduplication in GGUF handler")
    print("2. Improve stop sequences to prevent repetition")
    print("3. Limit max_tokens for tool call generation")
    print("4. Add explanation text requirements in prompts")
    print("=" * 60)
