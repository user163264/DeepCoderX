#!/usr/bin/env python3
"""Quick test to verify CURRENT_CONFIG fix"""

import sys
from pathlib import Path

# Setup
project_dir = Path('/Users/admin/Documents/DeepCoderX')
sys.path.insert(0, str(project_dir))

print("🔧 TESTING CURRENT_CONFIG FIX")
print("=" * 40)

try:
    from config import config
    
    # Test 1: Check if CURRENT_CONFIG exists in config object
    if hasattr(config, 'CURRENT_CONFIG'):
        print("✅ config.CURRENT_CONFIG exists")
        print(f"   Content preview: {config.CURRENT_CONFIG[:100]}...")
    else:
        print("❌ config.CURRENT_CONFIG missing")
    
    # Test 2: Check if CURRENT_CONFIG is exported
    try:
        from config import CURRENT_CONFIG
        print("✅ CURRENT_CONFIG exported successfully")
        print(f"   Content preview: {CURRENT_CONFIG[:100]}...")
    except ImportError:
        print("❌ CURRENT_CONFIG not exported")
    
    # Test 3: Test the unified handler context loading
    from models.session import CommandContext
    from services.mcpclient import MCPClient
    from services.unified_openai_handler import CloudOpenAIHandler
    
    # Create test context
    mcp_client = MCPClient(
        endpoint=f"http://{config.MCP_SERVER_HOST}:{config.MCP_SERVER_PORT}",
        api_key=config.MCP_API_KEY
    )
    
    ctx = CommandContext(project_dir, mcp_client, config.SANDBOX_PATH, True)
    handler = CloudOpenAIHandler(ctx, "deepseek")
    
    # Check system prompt
    system_prompt = handler.message_history[0]["content"]
    
    # Test for the indicators
    context_indicators = [
        "Project Context File",
        "DeepCoderX", 
        "Current Configuration"
    ]
    
    missing = []
    for indicator in context_indicators:
        if indicator not in system_prompt:
            missing.append(indicator)
    
    if missing:
        print(f"❌ Still missing indicators: {missing}")
        print(f"   System prompt length: {len(system_prompt)} chars")
        
        # Show what's actually in the prompt
        if "Current Configuration" in system_prompt:
            print("✅ 'Current Configuration' found in prompt")
        else:
            print("❌ 'Current Configuration' still missing from prompt")
    else:
        print("✅ All context indicators found!")
        print("🎉 Test 6 should now pass!")
    
except Exception as e:
    print(f"❌ ERROR: {e}")
    import traceback
    traceback.print_exc()
