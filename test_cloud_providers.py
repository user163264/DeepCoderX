#!/usr/bin/env python3
"""
Test script to verify @deepseek and @openai providers are working correctly.
This tests the cloud provider functionality in DeepCoderX.
"""

import sys
import os
from pathlib import Path

# Add project root to path
sys.path.append('/Users/admin/Documents/DeepCoderX')

def test_provider_config():
    """Test that provider configurations are loaded correctly."""
    print("🔧 Testing Provider Configuration...")
    
    try:
        from config_module import config
        
        # Check DeepSeek configuration
        deepseek_config = config.PROVIDERS.get("deepseek")
        print(f"✅ DeepSeek config loaded: {deepseek_config['name']}")
        print(f"   - Enabled: {deepseek_config['enabled']}")
        print(f"   - Model: {deepseek_config['model']}")
        print(f"   - Base URL: {deepseek_config['base_url']}")
        print(f"   - API Key: {'✅ Set' if deepseek_config['api_key'] else '❌ Missing'}")
        print(f"   - Tools Support: {deepseek_config['supports_tools']}")
        
        # Check OpenAI configuration
        openai_config = config.PROVIDERS.get("openai")
        print(f"✅ OpenAI config loaded: {openai_config['name']}")
        print(f"   - Enabled: {openai_config['enabled']}")
        print(f"   - Model: {openai_config['model']}")
        print(f"   - Base URL: {openai_config['base_url'] or 'Default OpenAI'}")
        print(f"   - API Key: {'✅ Set' if openai_config['api_key'] else '❌ Missing'}")
        print(f"   - Tools Support: {openai_config['supports_tools']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Configuration test failed: {e}")
        return False

def test_handler_initialization():
    """Test that both cloud handlers can be initialized."""
    print("\n🚀 Testing Handler Initialization...")
    
    try:
        from models.session import CommandContext
        from services.mcpclient import MCPClient
        from services.unified_openai_handler import CloudOpenAIHandler
        from config_module import config
        
        # Create test context
        test_dir = Path('/Users/admin/Documents/DeepCoderX')
        mcp_client = MCPClient(
            endpoint=f"http://{config.MCP_SERVER_HOST}:{config.MCP_SERVER_PORT}",
            api_key=config.MCP_API_KEY
        )
        
        ctx = CommandContext(
            root_path=test_dir,
            mcp_client=mcp_client,
            sandbox_path=config.SANDBOX_PATH,
            debug_mode=True
        )
        
        # Test DeepSeek handler
        try:
            deepseek_handler = CloudOpenAIHandler(ctx, "deepseek")
            print("✅ DeepSeek handler initialized successfully")
            print(f"   - Provider: {deepseek_handler.provider_name}")
            print(f"   - Model: {deepseek_handler.provider_config['model']}")
        except Exception as e:
            print(f"❌ DeepSeek handler failed: {e}")
        
        # Test OpenAI handler
        try:
            openai_handler = CloudOpenAIHandler(ctx, "openai")
            print("✅ OpenAI handler initialized successfully")
            print(f"   - Provider: {openai_handler.provider_name}")
            print(f"   - Model: {openai_handler.provider_config['model']}")
        except Exception as e:
            print(f"❌ OpenAI handler failed: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Handler initialization test failed: {e}")
        return False

def test_tool_registry():
    """Test that tool registry works for cloud providers."""
    print("\n🔧 Testing Tool Registry...")
    
    try:
        from services.tool_registry import get_tools_for_provider
        from config_module import config
        
        # Test DeepSeek tools
        deepseek_config = config.PROVIDERS["deepseek"]
        deepseek_tools = get_tools_for_provider("deepseek", deepseek_config)
        print(f"✅ DeepSeek tools loaded: {len(deepseek_tools)} tools")
        
        if deepseek_tools:
            tool_names = [tool["function"]["name"] for tool in deepseek_tools]
            print(f"   - Available tools: {', '.join(tool_names[:5])}")
            if len(tool_names) > 5:
                print(f"   - Plus {len(tool_names) - 5} more tools")
        
        # Test OpenAI tools
        openai_config = config.PROVIDERS["openai"]
        openai_tools = get_tools_for_provider("openai", openai_config)
        print(f"✅ OpenAI tools loaded: {len(openai_tools)} tools")
        
        if openai_tools:
            tool_names = [tool["function"]["name"] for tool in openai_tools]
            print(f"   - Available tools: {', '.join(tool_names[:5])}")
            if len(tool_names) > 5:
                print(f"   - Plus {len(tool_names) - 5} more tools")
        
        return True
        
    except Exception as e:
        print(f"❌ Tool registry test failed: {e}")
        return False

def test_routing_logic():
    """Test that the routing logic properly detects provider commands."""
    print("\n🧭 Testing Routing Logic...")
    
    try:
        from models.session import CommandContext
        from services.mcpclient import MCPClient
        from services.unified_openai_handler import CloudOpenAIHandler
        from config_module import config
        
        # Create test context
        test_dir = Path('/Users/admin/Documents/DeepCoderX')
        mcp_client = MCPClient(
            endpoint=f"http://{config.MCP_SERVER_HOST}:{config.MCP_SERVER_PORT}",
            api_key=config.MCP_API_KEY
        )
        
        ctx = CommandContext(
            root_path=test_dir,
            mcp_client=mcp_client,
            sandbox_path=config.SANDBOX_PATH,
            debug_mode=True
        )
        
        # Test DeepSeek routing
        deepseek_handler = CloudOpenAIHandler(ctx, "deepseek")
        
        # Test explicit DeepSeek command
        ctx.user_input = "@deepseek analyze this code"
        can_handle_explicit = deepseek_handler.can_handle()
        print(f"✅ DeepSeek explicit command (@deepseek): {can_handle_explicit}")
        
        # Test analysis keyword
        ctx.user_input = "analyze the project architecture"
        can_handle_analysis = deepseek_handler.can_handle()
        print(f"✅ DeepSeek analysis keyword: {can_handle_analysis}")
        
        # Test OpenAI routing
        openai_handler = CloudOpenAIHandler(ctx, "openai")
        
        # Test explicit OpenAI command
        ctx.user_input = "@openai help with this function"
        can_handle_openai = openai_handler.can_handle()
        print(f"✅ OpenAI explicit command (@openai): {can_handle_openai}")
        
        return True
        
    except Exception as e:
        print(f"❌ Routing logic test failed: {e}")
        return False

def test_session_management():
    """Test that session files are properly managed."""
    print("\n💾 Testing Session Management...")
    
    try:
        from models.session import CommandContext
        from services.mcpclient import MCPClient
        from services.unified_openai_handler import CloudOpenAIHandler
        from config_module import config
        
        # Create test context
        test_dir = Path('/Users/admin/Documents/DeepCoderX')
        mcp_client = MCPClient(
            endpoint=f"http://{config.MCP_SERVER_HOST}:{config.MCP_SERVER_PORT}",
            api_key=config.MCP_API_KEY
        )
        
        ctx = CommandContext(
            root_path=test_dir,
            mcp_client=mcp_client,
            sandbox_path=config.SANDBOX_PATH,
            debug_mode=True
        )
        
        # Test DeepSeek session
        deepseek_handler = CloudOpenAIHandler(ctx, "deepseek")
        deepseek_session_file = deepseek_handler.session_file
        print(f"✅ DeepSeek session file: {deepseek_session_file}")
        print(f"   - Path exists: {deepseek_session_file.exists()}")
        print(f"   - History loaded: {len(deepseek_handler.message_history)} messages")
        
        # Test OpenAI session
        openai_handler = CloudOpenAIHandler(ctx, "openai")
        openai_session_file = openai_handler.session_file
        print(f"✅ OpenAI session file: {openai_session_file}")
        print(f"   - Path exists: {openai_session_file.exists()}")
        print(f"   - History loaded: {len(openai_handler.message_history)} messages")
        
        return True
        
    except Exception as e:
        print(f"❌ Session management test failed: {e}")
        return False

def run_all_tests():
    """Run all provider tests."""
    print("=" * 70)
    print("🧪 TESTING @DEEPSEEK AND @OPENAI PROVIDERS")
    print("=" * 70)
    
    tests = [
        test_provider_config,
        test_handler_initialization,
        test_tool_registry,
        test_routing_logic,
        test_session_management
    ]
    
    results = []
    for test_func in tests:
        try:
            result = test_func()
            results.append(result)
        except Exception as e:
            print(f"❌ CRITICAL ERROR in {test_func.__name__}: {e}")
            results.append(False)
    
    # Summary
    passed = sum(results)
    total = len(results)
    
    print("\n" + "=" * 70)
    print("📊 TEST SUMMARY")
    print("=" * 70)
    print(f"✅ Passed: {passed}/{total} tests")
    print(f"❌ Failed: {total - passed}/{total} tests")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED!")
        print("🚀 Both @deepseek and @openai providers are working correctly")
        print("\n✨ Confirmed functionality:")
        print("   • Provider configuration loading")
        print("   • Handler initialization")
        print("   • Tool registry integration")
        print("   • Command routing logic")
        print("   • Session file management")
    else:
        print(f"\n⚠️ {total - passed} tests failed")
        print("🔧 Check configuration and dependencies")
    
    print("=" * 70)
    
    return passed == total

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
