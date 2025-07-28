#!/usr/bin/env python3
"""
Quick test to validate the fix for DeepSeek tools test
"""

import sys
import os
from pathlib import Path

# Add project root to path
sys.path.append('/Users/admin/Documents/DeepCoderX')

print("=" * 50)
print("🔍 TESTING DEEPSEEK TOOLS FIX")
print("=" * 50)

# Test 1: Import config
print("\n1️⃣ Testing config import...")
try:
    from config import config
    print(f"✅ Config imported")
    print(f"   MCP_SERVER_HOST: {config.MCP_SERVER_HOST}")
    print(f"   MCP_SERVER_PORT: {config.MCP_SERVER_PORT}")
    print(f"   MCP_API_KEY: {config.MCP_API_KEY[:10]}...")
except Exception as e:
    print(f"❌ Config import failed: {e}")
    sys.exit(1)

# Test 2: Import MCPClient
print("\n2️⃣ Testing MCPClient import...")
try:
    from services.mcpclient import MCPClient
    print("✅ MCPClient imported")
except Exception as e:
    print(f"❌ MCPClient import failed: {e}")
    sys.exit(1)

# Test 3: Create MCPClient with parameters
print("\n3️⃣ Testing MCPClient creation...")
try:
    mcp_client = MCPClient(
        endpoint=f"http://{config.MCP_SERVER_HOST}:{config.MCP_SERVER_PORT}",
        api_key=config.MCP_API_KEY
    )
    print("✅ MCPClient created successfully")
    print(f"   Endpoint: {mcp_client.endpoint}")
except Exception as e:
    print(f"❌ MCPClient creation failed: {e}")
    sys.exit(1)

# Test 4: Import session
print("\n4️⃣ Testing session import...")
try:
    from models.session import CommandContext
    print("✅ CommandContext imported")
except Exception as e:
    print(f"❌ CommandContext import failed: {e}")
    sys.exit(1)

# Test 5: Create CommandContext
print("\n5️⃣ Testing CommandContext creation...")
try:
    test_dir = Path('/Users/admin/Documents/DeepCoderX')
    ctx = CommandContext(
        root_path=test_dir,
        mcp_client=mcp_client,
        sandbox_path=config.SANDBOX_PATH,
        debug_mode=True
    )
    print("✅ CommandContext created successfully")
except Exception as e:
    print(f"❌ CommandContext creation failed: {e}")
    sys.exit(1)

# Test 6: Import unified handler
print("\n6️⃣ Testing unified handler import...")
try:
    from services.unified_openai_handler import CloudOpenAIHandler
    print("✅ CloudOpenAIHandler imported")
except Exception as e:
    print(f"❌ CloudOpenAIHandler import failed: {e}")
    sys.exit(1)

# Test 7: Create CloudOpenAIHandler
print("\n7️⃣ Testing CloudOpenAIHandler creation...")
try:
    handler = CloudOpenAIHandler(ctx, "deepseek")
    print("✅ CloudOpenAIHandler created successfully")
    print(f"   Provider: {handler.provider_name}")
except Exception as e:
    print(f"❌ CloudOpenAIHandler creation failed: {e}")
    sys.exit(1)

print("\n" + "=" * 50)
print("🎉 ALL TESTS PASSED!")
print("✅ DeepSeek tools test fix is working correctly")
print("🚀 Ready to run the full test suite")
print("=" * 50)
