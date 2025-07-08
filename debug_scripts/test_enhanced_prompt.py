#!/usr/bin/env python3
"""
Test the enhanced GGUF prompt to verify it contains all necessary elements.
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from services.gguf_tool_prompt import GGUFToolPromptBuilder
    from services.tool_registry import tool_registry, ToolPermission
    
    print("🧪 Testing Enhanced GGUF Prompt...")
    print("=" * 60)
    
    # Initialize prompt builder
    builder = GGUFToolPromptBuilder()
    
    # Get available tools
    available_tools = tool_registry.get_openai_definitions(max_permissions=ToolPermission.SYSTEM_ACCESS)
    
    # Build prompt for pwd
    prompt = builder.build_prompt(
        user_input="pwd",
        conversation_history=[],
        available_tools=available_tools
    )
    
    print(f"📏 Prompt length: {len(prompt)} characters\n")
    
    # Critical checks
    critical_checks = [
        ("🚨 Critical instructions", "🚨 CRITICAL INSTRUCTIONS" in prompt),
        ("❌ Never examples", "NEVER respond with generic text" in prompt),
        ("✅ Always examples", "ALWAYS use the <tool_call> format" in prompt),
        ("🎯 Exact examples", "🎯 EXACT EXAMPLES TO FOLLOW" in prompt),
        ("pwd example present", 'User: pwd' in prompt),
        ("run_bash tool call", 'run_bash({"command": "pwd"})' in prompt),
        ("Format reminder", "REMEMBER: You MUST respond with" in prompt),
        ("Strong emphasis", "🔴" in prompt or "🚫" in prompt),
    ]
    
    print("🔍 CRITICAL CHECKS:")
    print("-" * 40)
    all_passed = True
    for check_name, result in critical_checks:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {check_name}")
        if not result:
            all_passed = False
    
    if all_passed:
        print("\n🎉 ALL CRITICAL CHECKS PASSED!")
        print("✅ The enhanced prompt should work much better!")
    else:
        print("\n⚠️  Some checks failed - prompt may need more work")
    
    # Show a sample of the prompt
    print("\n" + "=" * 60)
    print("📝 PROMPT PREVIEW (first 800 chars):")
    print("-" * 60)
    print(prompt[:800] + "..." if len(prompt) > 800 else prompt)
    
    print("\n" + "=" * 60)
    print("🚀 READY TO TEST:")
    print("=" * 60)
    print("Run: python app.py")
    print("Then type: pwd")
    print("Expected: <tool_call>run_bash({\"command\": \"pwd\"})</tool_call>")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
