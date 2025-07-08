#!/usr/bin/env python3
"""
Debug script to capture and display the exact prompt being sent to GGUF model.
This will help us see if our enhanced instructions are actually reaching the model.
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

def debug_actual_prompt():
    """Debug the actual prompt construction for 'what is the current directory.'"""
    
    try:
        from services.gguf_tool_prompt import GGUFToolPromptBuilder
        from services.tool_registry import tool_registry, ToolPermission
        
        print("🔍 DEBUGGING ACTUAL PROMPT SENT TO GGUF MODEL")
        print("=" * 80)
        
        # Initialize prompt builder (same as GGUF handler does)
        builder = GGUFToolPromptBuilder()
        
        # Get available tools (same as GGUF handler does)
        available_tools = tool_registry.get_openai_definitions(max_permissions=ToolPermission.SYSTEM_ACCESS)
        
        print(f"Available tools count: {len(available_tools)}")
        for tool in available_tools:
            func_def = tool.get("function", {})
            print(f"  - {func_def.get('name', 'unknown')}")
        
        # Build prompt for the failing case
        test_input = "what is the current directory."
        conversation_history = []
        
        print(f"\nTest input: '{test_input}'")
        print("Building prompt...")
        
        # Build the full prompt (exactly as GGUF handler does)
        prompt = builder.build_prompt(
            user_input=test_input,
            conversation_history=conversation_history,
            available_tools=available_tools
        )
        
        print(f"\nPrompt length: {len(prompt)} characters")
        
        # Show the COMPLETE prompt
        print("\n" + "=" * 80)
        print("COMPLETE PROMPT SENT TO MODEL:")
        print("=" * 80)
        print(prompt)
        print("=" * 80)
        
        # Critical analysis
        print("\n🔍 CRITICAL ANALYSIS:")
        print("-" * 50)
        
        critical_checks = [
            ("🚨 Critical instructions present", "🚨 CRITICAL INSTRUCTIONS" in prompt),
            ("❌ Never JSON warning present", "NEVER respond with JSON blocks" in prompt), 
            ("✅ Always tool_call instruction", "ALWAYS use the <tool_call> format" in prompt),
            ("🎯 Exact examples header", "🎯 EXACT EXAMPLES TO FOLLOW" in prompt),
            ("pwd example in prompt", 'User: pwd' in prompt and 'Assistant: <tool_call>run_bash' in prompt),
            ("Current directory example", 'What is the current directory?' in prompt),
            ("run_bash example present", 'run_bash({"command": "pwd"})' in prompt),
            ("Format reminder at end", "REMEMBER: You MUST respond with <tool_call>" in prompt),
            ("Strong visual emphasis", "🔴" in prompt and "🚫" in prompt),
        ]
        
        all_passed = True
        for check_name, result in critical_checks:
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"{status} {check_name}")
            if not result:
                all_passed = False
        
        if all_passed:
            print("\n✅ All critical elements are present in the prompt!")
            print("🤔 The issue might be with the GGUF model itself or the model configuration.")
        else:
            print("\n❌ Some critical elements are missing from the prompt!")
            print("📝 The prompt building is not working correctly.")
        
        # Show the specific examples section
        print("\n" + "=" * 80)
        print("EXAMPLES SECTION EXTRACTED:")
        print("=" * 80)
        
        if "🎯 EXACT EXAMPLES TO FOLLOW" in prompt:
            examples_start = prompt.find("🎯 EXACT EXAMPLES TO FOLLOW")
            examples_end = prompt.find("Previous conversation:", examples_start)
            if examples_end == -1:
                examples_end = prompt.find("User: what is the current directory.", examples_start)
            
            examples_section = prompt[examples_start:examples_end]
            print(examples_section)
        else:
            print("❌ Examples section not found!")
        
        return prompt
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    prompt = debug_actual_prompt()
    
    print("\n" + "=" * 80)
    print("NEXT STEPS:")
    print("=" * 80)
    
    if prompt:
        print("✅ Prompt captured successfully")
        print("🔧 If all checks passed but model still fails:")
        print("   1. The GGUF model might be ignoring instructions")
        print("   2. Try a different/better GGUF model")
        print("   3. Try adjusting temperature (lower = more instruction following)")
        print("   4. The model might need even more extreme prompting")
    else:
        print("❌ Failed to capture prompt - check imports and dependencies")
