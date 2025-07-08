#!/usr/bin/env python3
"""Simple test to check if GGUF prompt includes pwd examples."""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from services.gguf_tool_prompt import GGUFToolPromptBuilder
    from services.tool_registry import tool_registry, ToolPermission
    
    print("Testing GGUF prompt construction...")
    
    # Initialize prompt builder
    builder = GGUFToolPromptBuilder()
    
    # Get available tools
    available_tools = tool_registry.get_openai_definitions(max_permissions=ToolPermission.SYSTEM_ACCESS)
    
    print(f"Available tools: {len(available_tools)}")
    
    # Build prompt for pwd
    prompt = builder.build_prompt(
        user_input="pwd",
        conversation_history=[],
        available_tools=available_tools
    )
    
    print(f"Prompt length: {len(prompt)}")
    
    # Check key elements
    print("\nChecking prompt content:")
    print(f"- Contains 'pwd': {'✅' if 'pwd' in prompt else '❌'}")
    print(f"- Contains 'run_bash': {'✅' if 'run_bash' in prompt else '❌'}")
    print(f"- Contains '<tool_call>': {'✅' if '<tool_call>' in prompt else '❌'}")
    print(f"- Contains pwd example: {'✅' if 'run_bash({\"command\": \"pwd\"})' in prompt else '❌'}")
    
    # Show core examples
    print("\nCore examples from builder:")
    for i, example in enumerate(builder.core_examples):
        if 'pwd' in example['user'] or 'pwd' in example['assistant']:
            print(f"Example {i+1}:")
            print(f"  User: {example['user']}")
            print(f"  Assistant: {example['assistant']}")
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
