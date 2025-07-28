#!/usr/bin/env python3
"""
Fix DeepSeek Configuration Issues

This script identifies and fixes the critical issues with DeepSeek configuration:
1. Overly aggressive system prompt forcing tool usage
2. Legacy tool format in system prompt vs native OpenAI calling
3. Tool permission inconsistencies
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.append('/Users/admin/Documents/DeepCoderX')

def analyze_deepseek_issues():
    """Analyze the current DeepSeek configuration issues."""
    print("🔍 Analyzing DeepSeek Configuration Issues...")
    
    try:
        from config_module import config
        from services.tool_registry import get_tools_for_provider
        
        # Get DeepSeek configuration
        deepseek_config = config.PROVIDERS["deepseek"]
        
        print(f"✅ DeepSeek Provider Status:")
        print(f"   - Enabled: {deepseek_config['enabled']}")
        print(f"   - Model: {deepseek_config['model']}")
        print(f"   - Tool Support: {deepseek_config['supports_tools']}")
        print(f"   - Tool Format: {deepseek_config['tool_format']}")
        
        # Check tool registry
        tools = get_tools_for_provider("deepseek", deepseek_config)
        tool_names = [tool["function"]["name"] for tool in tools]
        
        print(f"\n🛠️ Available Tools for DeepSeek:")
        for tool_name in tool_names:
            print(f"   - {tool_name}")
        
        # Check if run_bash is available (it shouldn't be for cloud models)
        has_run_bash = "run_bash" in tool_names
        print(f"\n⚠️ Security Check:")
        print(f"   - run_bash available: {'❌ YES (SECURITY ISSUE)' if has_run_bash else '✅ NO (SECURE)'}")
        
        # Analyze system prompt
        system_prompt = config.DEEPSEEK_SYSTEM_PROMPT
        print(f"\n📝 System Prompt Analysis:")
        print(f"   - Length: {len(system_prompt)} characters")
        
        # Check for problematic phrases
        problematic_phrases = [
            "You MUST use the provided tools",
            "gather any additional information you need",
            "step-by-step using the tools",
            'Example: `{"tool": "run_bash"'
        ]
        
        for phrase in problematic_phrases:
            if phrase in system_prompt:
                print(f"   - ❌ Found problematic phrase: '{phrase}'")
            else:
                print(f"   - ✅ No problematic phrase: '{phrase}'")
        
        # Check tool format mismatch
        if '{"tool":' in system_prompt and deepseek_config['tool_format'] == 'native':
            print(f"   - ❌ MISMATCH: Prompt shows legacy JSON format but config says 'native'")
        
        return True
        
    except Exception as e:
        print(f"❌ Analysis failed: {e}")
        return False

def generate_fixed_system_prompt():
    """Generate a fixed system prompt for DeepSeek."""
    print("\n🔧 Generating Fixed System Prompt...")
    
    fixed_prompt = """You are an expert software architect and coding assistant. Your primary goal is to answer the user's request clearly and helpfully.

**Response Guidelines:**
- Provide direct, helpful responses to questions
- Only use tools when explicitly needed for file operations or when the user requests specific file/code analysis
- For general questions, explanations, or conversations, respond directly without tools
- When tools are needed, use them efficiently and purposefully

**When to Use Tools:**
- User asks to read, write, or analyze specific files
- User requests directory listings or file operations
- User asks for code implementation that requires file creation
- User explicitly requests codebase analysis

**When NOT to Use Tools:**
- General questions about programming concepts
- Explanations of code or architecture
- Debugging help or code review discussions
- Conversational responses
- Questions that can be answered with your knowledge

You have access to file system tools through native OpenAI function calling when appropriate."""
    
    print("✅ Fixed System Prompt Generated")
    print(f"   - Length: {len(fixed_prompt)} characters")
    print(f"   - Removes aggressive tool forcing")
    print(f"   - Provides clear guidelines for tool usage")
    print(f"   - Uses native OpenAI tool calling (no legacy JSON)")
    
    return fixed_prompt

def create_backup_and_fix():
    """Create backup and apply fixes."""
    print("\n💾 Creating Backup and Applying Fixes...")
    
    try:
        config_file = Path('/Users/admin/Documents/DeepCoderX/config_module.py')
        
        # Create backup
        backup_file = config_file.with_suffix('.py.BAK_DEEPSEEK_FIX')
        if not backup_file.exists():
            backup_file.write_text(config_file.read_text())
            print(f"✅ Backup created: {backup_file}")
        else:
            print(f"✅ Backup already exists: {backup_file}")
        
        # Read current config
        config_content = config_file.read_text()
        
        # Find and replace the DEEPSEEK_SYSTEM_PROMPT
        fixed_prompt = generate_fixed_system_prompt()
        
        # Look for the prompt definition
        import re
        
        # Find the DEEPSEEK_SYSTEM_PROMPT section
        pattern = r'self\.DEEPSEEK_SYSTEM_PROMPT = self\._get_str_env\(\s*"DEEPCODERX_DEEPSEEK_SYSTEM_PROMPT",\s*""".*?"""\s*\)'
        
        replacement = f'''self.DEEPSEEK_SYSTEM_PROMPT = self._get_str_env(
            "DEEPCODERX_DEEPSEEK_SYSTEM_PROMPT",
            """{fixed_prompt}"""
        )'''
        
        if re.search(pattern, config_content, re.DOTALL):
            new_content = re.sub(pattern, replacement, config_content, flags=re.DOTALL)
            
            # Write the fixed content
            config_file.write_text(new_content)
            print(f"✅ Fixed system prompt applied to {config_file}")
            
        else:
            print(f"❌ Could not find DEEPSEEK_SYSTEM_PROMPT pattern in config file")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Backup and fix failed: {e}")
        return False

def verify_tool_permissions():
    """Verify tool permissions are correct."""
    print("\n🔒 Verifying Tool Permissions...")
    
    try:
        from services.tool_registry import tool_registry, ToolPermission
        
        # Check tool permissions
        tools = tool_registry.tools
        
        for tool_name, tool_def in tools.items():
            permission_level = tool_def.permission.value
            
            if tool_name == "run_bash":
                if tool_def.permission != ToolPermission.SYSTEM_ACCESS:
                    print(f"❌ run_bash has wrong permission: {permission_level} (should be system_access)")
                else:
                    print(f"✅ run_bash has correct permission: {permission_level}")
            
            elif tool_name in ["read_file", "list_dir", "stat"]:
                if tool_def.permission != ToolPermission.READ_ONLY:
                    print(f"❌ {tool_name} has wrong permission: {permission_level} (should be read_only)")
                else:
                    print(f"✅ {tool_name} has correct permission: {permission_level}")
            
            elif tool_name in ["write_file", "move_file", "mkdir"]:
                if tool_def.permission != ToolPermission.WRITE_ALLOWED:
                    print(f"❌ {tool_name} has wrong permission: {permission_level} (should be write_allowed)")
                else:
                    print(f"✅ {tool_name} has correct permission: {permission_level}")
        
        # Verify DeepSeek gets correct tools
        from config_module import config
        from services.tool_registry import get_tools_for_provider
        
        deepseek_config = config.PROVIDERS["deepseek"]
        deepseek_tools = get_tools_for_provider("deepseek", deepseek_config)
        deepseek_tool_names = [tool["function"]["name"] for tool in deepseek_tools]
        
        print(f"\n🔍 DeepSeek Tool Access:")
        
        # Should have
        should_have = ["read_file", "write_file", "list_dir", "move_file", "mkdir", "stat"]
        for tool in should_have:
            if tool in deepseek_tool_names:
                print(f"   ✅ Has access to: {tool}")
            else:
                print(f"   ❌ Missing access to: {tool}")
        
        # Should NOT have
        should_not_have = ["run_bash"]
        for tool in should_not_have:
            if tool in deepseek_tool_names:
                print(f"   ❌ SECURITY ISSUE - Has access to: {tool}")
            else:
                print(f"   ✅ Correctly restricted from: {tool}")
        
        return True
        
    except Exception as e:
        print(f"❌ Permission verification failed: {e}")
        return False

def run_comprehensive_fix():
    """Run comprehensive fix for all DeepSeek issues."""
    print("🚀 DeepSeek Configuration Fix Tool")
    print("=" * 50)
    
    success = True
    
    # Step 1: Analyze current issues
    if not analyze_deepseek_issues():
        success = False
    
    # Step 2: Verify tool permissions
    if not verify_tool_permissions():
        success = False
    
    # Step 3: Create backup and apply fixes
    if not create_backup_and_fix():
        success = False
    
    # Summary
    print("\n" + "=" * 50)
    if success:
        print("🎉 DeepSeek Configuration Fix Completed Successfully!")
        print("\n✅ Issues Fixed:")
        print("   • Overly aggressive system prompt replaced")
        print("   • Tool forcing behavior removed")
        print("   • Native OpenAI tool calling maintained")
        print("   • Clear guidelines for appropriate tool usage")
        print("   • Security permissions verified")
        
        print("\n🔄 Next Steps:")
        print("   1. Restart DeepCoderX application")
        print("   2. Test @deepseek with simple conversational queries")
        print("   3. Verify tools are only used when appropriate")
        print("   4. Check that run_bash is not available to DeepSeek")
        
    else:
        print("❌ DeepSeek Configuration Fix Failed")
        print("   Please review the errors above and fix manually")
    
    return success

if __name__ == "__main__":
    run_comprehensive_fix()
