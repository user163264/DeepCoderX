#!/usr/bin/env python3
"""Simple diagnostic to test just the setup function"""

import sys
import os
from pathlib import Path

# Add project root to path
sys.path.append('/Users/admin/Documents/DeepCoderX')

def test_basic_imports():
    """Test if we can import the basic modules"""
    print("🔍 Testing basic imports...")
    
    try:
        from config import config
        print("✅ Config imported successfully")
        print(f"   MCP_SERVER_HOST: {config.MCP_SERVER_HOST}")
        print(f"   MCP_SERVER_PORT: {config.MCP_SERVER_PORT}")
        print(f"   MCP_API_KEY: {config.MCP_API_KEY}")
        return True
    except Exception as e:
        print(f"❌ Config import failed: {e}")
        return False

def test_mcp_client_creation():
    """Test MCP client creation"""
    print("\n🔍 Testing MCP client creation...")
    
    try:
        from config import config
        from services.mcpclient import MCPClient
        
        # Create MCP client with proper parameters
        mcp_client = MCPClient(
            endpoint=f"http://{config.MCP_SERVER_HOST}:{config.MCP_SERVER_PORT}",
            api_key=config.MCP_API_KEY
        )
        
        print("✅ MCPClient created successfully")
        print(f"   Endpoint: {mcp_client.endpoint}")
        print(f"   Has headers: {bool(mcp_client.headers)}")
        return True
    except Exception as e:
        print(f"❌ MCPClient creation failed: {e}")
        return False

def test_command_context_creation():
    """Test CommandContext creation"""
    print("\n🔍 Testing CommandContext creation...")
    
    try:
        from config import config
        from models.session import CommandContext
        from services.mcpclient import MCPClient
        
        # Create MCP client
        mcp_client = MCPClient(
            endpoint=f"http://{config.MCP_SERVER_HOST}:{config.MCP_SERVER_PORT}",
            api_key=config.MCP_API_KEY
        )
        
        # Create test directory
        test_dir = Path('/Users/admin/Documents/DeepCoderX')
        
        # Create context
        ctx = CommandContext(
            root_path=test_dir,
            mcp_client=mcp_client,
            sandbox_path=config.SANDBOX_PATH,
            debug_mode=True
        )
        
        print("✅ CommandContext created successfully")
        print(f"   Root path: {ctx.root_path}")
        print(f"   Sandbox path: {ctx.sandbox_path}")
        print(f"   Has MCP client: {bool(ctx.mcp_client)}")
        return True
    except Exception as e:
        print(f"❌ CommandContext creation failed: {e}")
        return False

def test_unified_handler_creation():
    """Test CloudOpenAIHandler creation"""
    print("\n🔍 Testing CloudOpenAIHandler creation...")
    
    try:
        from config import config
        from models.session import CommandContext
        from services.mcpclient import MCPClient
        from services.unified_openai_handler import CloudOpenAIHandler
        
        # Create full setup
        mcp_client = MCPClient(
            endpoint=f"http://{config.MCP_SERVER_HOST}:{config.MCP_SERVER_PORT}",
            api_key=config.MCP_API_KEY
        )
        
        test_dir = Path('/Users/admin/Documents/DeepCoderX')
        
        ctx = CommandContext(
            root_path=test_dir,
            mcp_client=mcp_client,
            sandbox_path=config.SANDBOX_PATH,
            debug_mode=True
        )
        
        # Create handler
        handler = CloudOpenAIHandler(ctx, "deepseek")
        
        print("✅ CloudOpenAIHandler created successfully")
        print(f"   Provider: {handler.provider_name}")
        print(f"   Provider config: {bool(handler.provider_config)}")
        print(f"   Session file: {handler.session_file}")
        return True
    except Exception as e:
        print(f"❌ CloudOpenAIHandler creation failed: {e}")
        return False

def run_diagnostics():
    """Run all diagnostic tests"""
    print("=" * 60)
    print("🔬 DEEPSEEK SETUP DIAGNOSTICS")
    print("=" * 60)
    
    tests = [
        test_basic_imports,
        test_mcp_client_creation,
        test_command_context_creation,
        test_unified_handler_creation
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"❌ CRITICAL ERROR in {test.__name__}: {e}")
            results.append(False)
    
    # Summary
    passed = sum(results)
    total = len(results)
    
    print("\n" + "=" * 60)
    print("📊 DIAGNOSTIC SUMMARY")
    print("=" * 60)
    print(f"✅ Passed: {passed}/{total} tests")
    print(f"❌ Failed: {total - passed}/{total} tests")
    
    if passed == total:
        print("\n🎉 ALL DIAGNOSTICS PASSED!")
        print("🔧 Setup environment is working correctly")
    else:
        print(f"\n⚠️ {total - passed} diagnostics failed")
        print("🔧 Review issues above before running full test")
    
    return passed == total

if __name__ == "__main__":
    success = run_diagnostics()
    sys.exit(0 if success else 1)
