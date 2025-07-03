#!/usr/bin/env python3
"""Quick one-liner test for the DeepSeek fix"""

import sys, os
from pathlib import Path

# Setup
project_dir = Path('/Users/admin/Documents/DeepCoderX')
os.chdir(project_dir)
sys.path.insert(0, str(project_dir))

print("🧪 QUICK DEEPSEEK FIX TEST")
print("=" * 40)

try:
    # The exact code that was failing before the fix
    from config import config
    from services.mcpclient import MCPClient
    from models.session import CommandContext
    from services.unified_openai_handler import CloudOpenAIHandler
    
    # This line was causing the error - now fixed
    mcp_client = MCPClient(
        endpoint=f"http://{config.MCP_SERVER_HOST}:{config.MCP_SERVER_PORT}",
        api_key=config.MCP_API_KEY
    )
    
    ctx = CommandContext(project_dir, mcp_client, config.SANDBOX_PATH, True)
    handler = CloudOpenAIHandler(ctx, "deepseek")
    
    print("✅ SUCCESS: All components created without errors!")
    print(f"✅ MCPClient: {mcp_client.endpoint}")
    print(f"✅ Handler: {handler.provider_name}")
    print("🎉 The fix is working correctly!")
    
except Exception as e:
    print(f"❌ FAILED: {e}")
    print("🔧 The fix may need additional work")
    sys.exit(1)
