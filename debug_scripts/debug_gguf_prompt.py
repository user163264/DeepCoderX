#!/usr/bin/env python3
"""
Debug script to examine the exact prompt being sent to GGUF models.
This will help identify why the model isn't generating proper tool calls.
"""

import sys
import os
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from services.gguf_tool_prompt import GGUFToolPromptBuilder
from services.tool_registry import tool_registry, ToolPermission


def debug_prompt_construction():
    """Debug the prompt construction for pwd command."""
    print("=" * 80)
    print("GGUF PROMPT CONSTRUCTION DEBUG")
    print("=" * 80)
    
    # Initialize prompt builder
    builder = GGUFToolPromptBuilder()
    
    # Get available tools (same as local handler would get)
    available_tools = tool_registry.get_openai_definitions(max_permissions=ToolPermission.SYSTEM_ACCESS)
    
    print(f"\nAvailable tools count: {len(available_tools)}")
    for tool in available_tools:
        func_def = tool.get("function", {})
        print(f"  - {func_def.get('name', 'unknown')}: {func_def.get('description', 'No description')}")
    
    # Test the specific failing case
    test_input = "pwd"
    conversation_history = []
    
    print(f"\nTest input: '{test_input}'")
    print("\nBuilding prompt...")
    
    # Build the full prompt
    prompt = builder.build_prompt(
        user_input=test_input,
        conversation_history=conversation_history,
        available_tools=available_tools
    )
    
    print(f"\nPrompt length: {len(prompt)} characters")
    print("\n" + "=" * 80)
    print("FULL PROMPT CONTENT:")
    print("=" * 80)
    print(prompt)
    print("=" * 80)
    
    # Check if the prompt contains the expected examples
    print("\nPROMPT ANALYSIS:")
    print("-" * 40)
    
    checks = [
        ("Contains run_bash tool", "run_bash" in prompt),
        ("Contains pwd example", "pwd" in prompt.lower()),
        ("Contains tool_call format", "<tool_call>" in prompt),
        ("Contains shell command instructions", "shell command" in prompt.lower()),
        ("Contains run_bash example", 'run_bash({"command": "pwd"})' in prompt),
    ]
    
    for check_name, result in checks:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {check_name}")
    
    # Extract and show the core examples section
    print("\n" + "=" * 80)
    print("CORE EXAMPLES SECTION:")
    print("=" * 80)
    
    if "Examples of how to use tools:" in prompt:
        examples_start = prompt.find("Examples of how to use tools:")
        examples_section = prompt[examples_start:examples_start + 2000]  # Show first 2000 chars
        print(examples_section)
    else:
        print("❌ Examples section not found!")
    
    # Test specific pwd example
    print("\n" + "=" * 80)
    print("PWD EXAMPLE ANALYSIS:")
    print("=" * 80)
    
    pwd_examples = [
        'User: pwd',
        'run_bash({"command": "pwd"})',
        'User: What is the current directory?',
    ]
    
    for example in pwd_examples:
        found = example in prompt
        status = "✅ FOUND" if found else "❌ MISSING"
        print(f"{status} '{example}'")
    
    print("\n" + "=" * 80)
    print("RECOMMENDATIONS:")
    print("=" * 80)
    
    if 'run_bash({"command": "pwd"})' not in prompt:
        print("❌ CRITICAL: The pwd example is missing from the prompt!")
        print("   This explains why the model doesn't know to use run_bash for pwd.")
    
    if "<tool_call>" not in prompt:
        print("❌ CRITICAL: Tool call format examples are missing!")
    
    if "shell command" not in prompt.lower():
        print("❌ CRITICAL: Shell command instructions are missing!")
    
    return prompt


def test_prompt_with_variations():
    """Test prompt building with different variations."""
    print("\n" + "=" * 80)
    print("TESTING PROMPT VARIATIONS:")
    print("=" * 80)
    
    builder = GGUFToolPromptBuilder()
    available_tools = tool_registry.get_openai_definitions(max_permissions=ToolPermission.SYSTEM_ACCESS)
    
    test_cases = [
        "pwd",
        "ls -la", 
        "What is the current directory?",
        "git status",
        "create a file called test.txt"
    ]
    
    for test_input in test_cases:
        print(f"\nTest: '{test_input}'")
        prompt = builder.build_prompt(test_input, [], available_tools)
        
        # Quick analysis
        has_examples = "<tool_call>" in prompt
        has_shell_instr = "shell command" in prompt.lower()
        
        print(f"  Examples present: {'✅' if has_examples else '❌'}")
        print(f"  Shell instructions: {'✅' if has_shell_instr else '❌'}")
        print(f"  Prompt length: {len(prompt)} chars")


if __name__ == "__main__":
    try:
        prompt = debug_prompt_construction()
        test_prompt_with_variations()
        
        print("\n" + "=" * 80)
        print("DEBUG COMPLETE")
        print("=" * 80)
        print("\nNext steps:")
        print("1. Check if pwd example is properly included in prompt")
        print("2. Verify tool call format is correct")
        print("3. Test with actual GGUF model to see response")
        print("\nTo test with actual model, run:")
        print("  python app.py")
        print("  # Then type: pwd")
        
    except Exception as e:
        print(f"❌ Error during debug: {e}")
        import traceback
        traceback.print_exc()
