#!/usr/bin/env python3
"""Simple diagnostic to understand the CURRENT_CONFIG issue"""

import sys
import os
from pathlib import Path

# Change to project directory and add to path
project_dir = Path('/Users/admin/Documents/DeepCoderX')
os.chdir(project_dir)
sys.path.insert(0, str(project_dir))

print("🔍 DEBUGGING CURRENT_CONFIG ISSUE")
print("=" * 50)

# Test 1: Check config imports
print("1. Testing config imports...")
try:
    from config import config
    print(f"✅ Config imported: {type(config)}")
    
    # Check if CURRENT_CONFIG exists
    if hasattr(config, 'CURRENT_CONFIG'):
        current_config = config.CURRENT_CONFIG
        print(f"✅ config.CURRENT_CONFIG exists")
        print(f"   Type: {type(current_config)}")
        print(f"   Length: {len(current_config)} chars")
        print(f"   Preview: {repr(current_config[:200])}")
    else:
        print("❌ config.CURRENT_CONFIG does not exist")
        print(f"   Available attributes: {[attr for attr in dir(config) if not attr.startswith('_')]}")
except Exception as e:
    print(f"❌ Config import error: {e}")
    exit(1)

# Test 2: Check exports
print("\n2. Testing CURRENT_CONFIG export...")
try:
    from config import CURRENT_CONFIG
    print("✅ CURRENT_CONFIG exported successfully")
    print(f"   Content: {repr(CURRENT_CONFIG[:200])}")
except ImportError as e:
    print(f"❌ CURRENT_CONFIG not exported: {e}")

# Test 3: Check what unified handler creates
print("\n3. Testing unified handler system prompt...")
try:
    from models.session import CommandContext
    from services.mcpclient import MCPClient
    from services.unified_openai_handler import CloudOpenAIHandler
    
    # Create test setup
    mcp_client = MCPClient(
        endpoint=f"http://{config.MCP_SERVER_HOST}:{config.MCP_SERVER_PORT}",
        api_key=config.MCP_API_KEY
    )
    
    ctx = CommandContext(project_dir, mcp_client, config.SANDBOX_PATH, True)
    handler = CloudOpenAIHandler(ctx, "deepseek")
    
    # Get the system prompt
    system_prompt = handler.message_history[0]["content"]
    print(f"✅ System prompt created")
    print(f"   Length: {len(system_prompt)} chars")
    
    # Check for each indicator
    indicators = ["Project Context File", "DeepCoderX", "Current Configuration"]
    
    for indicator in indicators:
        if indicator in system_prompt:
            print(f"   ✅ Found: '{indicator}'")
        else:
            print(f"   ❌ Missing: '{indicator}'")
    
    # Show the end of the prompt to see what's actually there
    print(f"\n   Last 500 chars of prompt:")
    print(f"   {repr(system_prompt[-500:])}")
    
except Exception as e:
    print(f"❌ Handler test error: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 50)
