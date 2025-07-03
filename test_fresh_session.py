#!/usr/bin/env python3
"""Test the system prompt with fresh session"""

import sys
import os
from pathlib import Path

# Setup
project_dir = Path('/Users/admin/Documents/DeepCoderX')
os.chdir(project_dir)
sys.path.insert(0, str(project_dir))

print("🔧 TESTING SYSTEM PROMPT WITH FRESH SESSION")
print("=" * 50)

try:
    from config import config
    from models.session import CommandContext
    from services.mcpclient import MCPClient
    from services.unified_openai_handler import CloudOpenAIHandler
    
    # Delete existing session file to force _reset_history()
    session_file = project_dir / ".deepcoderx" / "deepseek_session.json"
    if session_file.exists():
        session_file.unlink()
        print("✅ Deleted existing deepseek_session.json")
    
    # Create fresh handler
    mcp_client = MCPClient(
        endpoint=f"http://{config.MCP_SERVER_HOST}:{config.MCP_SERVER_PORT}",
        api_key=config.MCP_API_KEY
    )
    
    ctx = CommandContext(project_dir, mcp_client, config.SANDBOX_PATH, True)
    handler = CloudOpenAIHandler(ctx, "deepseek")
    
    # Check system prompt
    system_prompt = handler.message_history[0]["content"]
    
    print(f"✅ Fresh system prompt created")
    print(f"   Length: {len(system_prompt)} chars")
    
    # Check for indicators
    indicators = ["Project Context File", "DeepCoderX", "Current Configuration"]
    
    for indicator in indicators:
        if indicator in system_prompt:
            print(f"   ✅ Found: '{indicator}'")
        else:
            print(f"   ❌ Missing: '{indicator}'")
    
    # Show the relevant section
    if "Current Configuration" in system_prompt:
        config_start = system_prompt.find("**Current Configuration**:")
        if config_start > -1:
            config_section = system_prompt[config_start:config_start + 300]
            print(f"\n📄 Configuration section:")
            print(config_section)
    else:
        print(f"\n📄 Last 500 chars of prompt:")
        print(system_prompt[-500:])
    
except Exception as e:
    print(f"❌ ERROR: {e}")
    import traceback
    traceback.print_exc()
