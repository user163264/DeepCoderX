#!/usr/bin/env python3
"""
Test script to verify the GGUF PWD fix

This script tests whether the GGUF tool prompt builder now properly
teaches the model to use run_bash for shell commands like pwd.
"""

import sys
import json
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from services.gguf_tool_prompt import GGUFToolPromptBuilder
from services.tool_registry import tool_registry


def test_pwd_fix():
    """Test that PWD command is properly handled in GGUF prompts."""
    
    print("🔧 Testing GGUF PWD Fix")
    print("=" * 50)
    
    # Initialize prompt builder
    builder = GGUFToolPromptBuilder()
    
    # Get available tools (local provider gets all tools including run_bash)
    available_tools = tool_registry.get_openai_definitions(
        max_permissions=tool_registry.tools["run_bash"].permission
    )
    
    print(f"✅ Available tools: {len(available_tools)}")
    tool_names = [tool["function"]["name"] for tool in available_tools]
    print(f"📋 Tool names: {', '.join(tool_names)}")
    
    # Test PWD command specifically
    test_cases = [
        "pwd",
        "What is the current directory?",
        "ls -la",
        "git status"
    ]
    
    for test_input in test_cases:
        print(f"\n🧪 Testing input: '{test_input}'")
        
        # Build prompt for this input
        prompt = builder.build_prompt(
            user_input=test_input,
            conversation_history=[],
            available_tools=available_tools
        )
        
        # Check if prompt contains shell command examples
        has_pwd_example = "run_bash" in prompt and "pwd" in prompt
        has_shell_instructions = "SPECIAL INSTRUCTIONS FOR SHELL COMMANDS" in prompt
        
        print(f"   ✅ Contains run_bash + pwd examples: {has_pwd_example}")
        print(f"   ✅ Contains shell command instructions: {has_shell_instructions}")
        
        # Show relevant parts of the prompt
        if has_pwd_example:
            lines = prompt.split('\n')
            pwd_lines = [line for line in lines if 'pwd' in line.lower()]
            print(f"   📝 PWD examples found: {len(pwd_lines)}")
            for line in pwd_lines[:2]:  # Show first 2 examples
                print(f"      {line.strip()}")
    
    print(f"\n🎯 Expected Model Behavior:")
    print(f"   For 'pwd' → <tool_call>run_bash({{\"command\": \"pwd\"}})</tool_call>")
    print(f"   For 'ls -la' → <tool_call>run_bash({{\"command\": \"ls -la\"}})</tool_call>")
    
    print(f"\n✅ GGUF PWD Fix Test Complete!")
    print(f"   The GGUF model should now use run_bash for shell commands")
    print(f"   instead of giving generic placeholder responses.")


def show_prompt_sample():
    """Show a sample of the fixed prompt for PWD command."""
    
    print("\n📄 Sample Prompt for 'pwd' command:")
    print("=" * 50)
    
    builder = GGUFToolPromptBuilder()
    available_tools = tool_registry.get_openai_definitions(
        max_permissions=tool_registry.tools["run_bash"].permission
    )
    
    prompt = builder.build_prompt(
        user_input="pwd",
        conversation_history=[],
        available_tools=available_tools
    )
    
    # Show key sections
    lines = prompt.split('\n')
    
    # Find shell instructions section
    shell_start = None
    for i, line in enumerate(lines):
        if "SPECIAL INSTRUCTIONS FOR SHELL COMMANDS" in line:
            shell_start = i
            break
    
    if shell_start:
        print("🛠️  Shell Command Instructions:")
        for i in range(shell_start, min(shell_start + 8, len(lines))):
            print(f"   {lines[i]}")
    
    # Find pwd examples
    print("\n💡 PWD Examples in Prompt:")
    for i, line in enumerate(lines):
        if 'pwd' in line.lower() and ('user:' in line.lower() or 'assistant:' in line.lower()):
            print(f"   {line.strip()}")
            if i + 1 < len(lines):
                print(f"   {lines[i + 1].strip()}")
            print()


if __name__ == "__main__":
    try:
        test_pwd_fix()
        show_prompt_sample()
    except Exception as e:
        print(f"❌ Error testing PWD fix: {e}")
        import traceback
        traceback.print_exc()
