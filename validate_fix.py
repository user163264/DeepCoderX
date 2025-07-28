#!/usr/bin/env python3
"""Test the DeepSeek tools fix"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path('/Users/admin/Documents/DeepCoderX')
sys.path.insert(0, str(project_root))

def main():
    print("🔧 TESTING DEEPSEEK TOOLS FIX")
    print("=" * 40)
    
    success = True
    
    # Test 1: Import and check config
    print("\n1. Testing config...")
    try:
        from config import config
        assert hasattr(config, 'MCP_SERVER_HOST'), "Missing MCP_SERVER_HOST"
        assert hasattr(config, 'MCP_SERVER_PORT'), "Missing MCP_SERVER_PORT" 
        assert hasattr(config, 'MCP_API_KEY'), "Missing MCP_API_KEY"
        print(f"✅ Config OK - MCP at {config.MCP_SERVER_HOST}:{config.MCP_SERVER_PORT}")
    except Exception as e:
        print(f"❌ Config failed: {e}")
        success = False
        
    # Test 2: Test MCPClient with parameters
    print("\n2. Testing MCPClient initialization...")
    try:
        from services.mcpclient import MCPClient
        from config import config
        
        # This should work now with the fix
        mcp_client = MCPClient(
            endpoint=f"http://{config.MCP_SERVER_HOST}:{config.MCP_SERVER_PORT}",
            api_key=config.MCP_API_KEY
        )
        assert mcp_client.endpoint == f"http://{config.MCP_SERVER_HOST}:{config.MCP_SERVER_PORT}"
        assert 'X-API-Key' in mcp_client.headers
        print("✅ MCPClient created successfully with required parameters")
    except Exception as e:
        print(f"❌ MCPClient creation failed: {e}")
        success = False
        
    # Test 3: Test CommandContext creation
    print("\n3. Testing CommandContext...")
    try:
        from models.session import CommandContext
        
        ctx = CommandContext(
            root_path=project_root,
            mcp_client=mcp_client,
            sandbox_path=config.SANDBOX_PATH,
            debug_mode=True
        )
        assert ctx.mcp_client is not None
        print("✅ CommandContext created successfully")
    except Exception as e:
        print(f"❌ CommandContext creation failed: {e}")
        success = False
        
    # Test 4: Test CloudOpenAIHandler creation
    print("\n4. Testing CloudOpenAIHandler...")
    try:
        from services.unified_openai_handler import CloudOpenAIHandler
        
        handler = CloudOpenAIHandler(ctx, "deepseek")
        assert handler.provider_name == "deepseek"
        assert handler.provider_config is not None
        print("✅ CloudOpenAIHandler created successfully")
    except Exception as e:
        print(f"❌ CloudOpenAIHandler creation failed: {e}")
        success = False
        
    print("\n" + "=" * 40)
    if success:
        print("🎉 ALL TESTS PASSED!")
        print("✅ DeepSeek tools test fix is working!")
        print("🚀 The original error should now be resolved")
    else:
        print("❌ Some tests failed")
        print("🔧 Review the errors above")
        
    return success

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
