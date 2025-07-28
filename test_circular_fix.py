#!/usr/bin/env python3
"""Test the CURRENT_CONFIG circular reference fix"""

import sys
import os
from pathlib import Path

# Setup
project_dir = Path('/Users/admin/Documents/DeepCoderX')
os.chdir(project_dir)
sys.path.insert(0, str(project_dir))

print("🔧 TESTING CURRENT_CONFIG CIRCULAR REFERENCE FIX")
print("=" * 50)

try:
    # Test if config can be imported without error
    from config import config
    print("✅ Config imported successfully")
    
    # Test if CURRENT_CONFIG works
    current_config = config.CURRENT_CONFIG
    print("✅ config.CURRENT_CONFIG accessed successfully")
    print(f"   Content: {repr(current_config)}")
    
    # Test if export works
    from config import CURRENT_CONFIG
    print("✅ CURRENT_CONFIG export works")
    
    # Test the unified handler
    from models.session import CommandContext
    from services.mcpclient import MCPClient
    from services.unified_openai_handler import CloudOpenAIHandler
    
    mcp_client = MCPClient(
        endpoint=f"http://{config.MCP_SERVER_HOST}:{config.MCP_SERVER_PORT}",
        api_key=config.MCP_API_KEY
    )
    
    ctx = CommandContext(project_dir, mcp_client, config.SANDBOX_PATH, True)
    handler = CloudOpenAIHandler(ctx, "deepseek")
    
    # Check system prompt
    system_prompt = handler.message_history[0]["content"]
    
    if "Current Configuration" in system_prompt:
        print("✅ 'Current Configuration' found in system prompt!")
        
        # Extract the configuration section
        config_start = system_prompt.find("**Current Configuration**:")
        if config_start > -1:
            config_section = system_prompt[config_start:config_start + 500]
            print(f"   Configuration section: {repr(config_section)}")
    else:
        print("❌ 'Current Configuration' still missing from system prompt")
        print(f"   System prompt length: {len(system_prompt)}")
        print(f"   Last 300 chars: {repr(system_prompt[-300:])}")
    
    print("\n🎉 TEST COMPLETE - Should fix Test 6!")
    
except Exception as e:
    print(f"❌ ERROR: {e}")
    import traceback
    traceback.print_exc()
