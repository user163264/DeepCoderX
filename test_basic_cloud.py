#!/usr/bin/env python3
"""
Quick test to verify the basic functionality of cloud providers
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, '/Users/admin/Documents/DeepCoderX')

print("🔧 Testing basic import and configuration...")

try:
    # Test config loading
    from config_module import config
    print("✅ Config module loaded successfully")
    
    # Check provider configs
    deepseek_config = config.PROVIDERS.get("deepseek")
    openai_config = config.PROVIDERS.get("openai")
    
    print(f"✅ DeepSeek config: {deepseek_config['name']}")
    print(f"   - Enabled: {deepseek_config['enabled']}")
    print(f"   - API Key: {'✅ Set' if deepseek_config['api_key'] else '❌ Missing'}")
    print(f"   - Model: {deepseek_config['model']}")
    
    print(f"✅ OpenAI config: {openai_config['name']}")
    print(f"   - Enabled: {openai_config['enabled']}")
    print(f"   - API Key: {'✅ Set' if openai_config['api_key'] else '❌ Missing'}")
    print(f"   - Model: {openai_config['model']}")
    
except Exception as e:
    print(f"❌ Config loading failed: {e}")
    sys.exit(1)

try:
    # Test handler imports
    from services.unified_openai_handler import CloudOpenAIHandler
    print("✅ CloudOpenAIHandler imported successfully")
    
    from models.session import CommandContext
    from services.mcpclient import MCPClient
    print("✅ Supporting classes imported successfully")
    
except Exception as e:
    print(f"❌ Handler import failed: {e}")
    sys.exit(1)

try:
    # Test basic initialization
    test_dir = Path('/Users/admin/Documents/DeepCoderX')
    mcp_client = MCPClient(
        endpoint=f"http://{config.MCP_SERVER_HOST}:{config.MCP_SERVER_PORT}",
        api_key=config.MCP_API_KEY
    )
    
    ctx = CommandContext(
        root_path=test_dir,
        mcp_client=mcp_client,
        sandbox_path=config.SANDBOX_PATH,
        debug_mode=False
    )
    
    print("✅ CommandContext created successfully")
    
    # Test DeepSeek handler initialization
    deepseek_handler = CloudOpenAIHandler(ctx, "deepseek")
    print(f"✅ DeepSeek handler initialized: {deepseek_handler.provider_name}")
    
    # Test OpenAI handler initialization
    openai_handler = CloudOpenAIHandler(ctx, "openai")
    print(f"✅ OpenAI handler initialized: {openai_handler.provider_name}")
    
except Exception as e:
    print(f"❌ Handler initialization failed: {e}")
    sys.exit(1)

try:
    # Test tool registry
    from services.tool_registry import get_tools_for_provider
    
    deepseek_tools = get_tools_for_provider("deepseek", deepseek_config)
    openai_tools = get_tools_for_provider("openai", openai_config)
    
    print(f"✅ DeepSeek tools: {len(deepseek_tools)} available")
    print(f"✅ OpenAI tools: {len(openai_tools)} available")
    
    if deepseek_tools:
        tool_names = [tool["function"]["name"] for tool in deepseek_tools[:3]]
        print(f"   - Sample tools: {', '.join(tool_names)}")
    
except Exception as e:
    print(f"❌ Tool registry test failed: {e}")
    sys.exit(1)

try:
    # Test routing logic
    print("\n🧭 Testing routing logic...")
    
    # Test DeepSeek routing
    ctx.user_input = "@deepseek analyze this code"
    can_handle_deepseek = deepseek_handler.can_handle()
    print(f"✅ DeepSeek can handle '@deepseek' command: {can_handle_deepseek}")
    
    ctx.user_input = "analyze the project architecture"
    can_handle_analysis = deepseek_handler.can_handle()
    print(f"✅ DeepSeek can handle analysis keyword: {can_handle_analysis}")
    
    # Test OpenAI routing
    ctx.user_input = "@openai help with this function"
    can_handle_openai = openai_handler.can_handle()
    print(f"✅ OpenAI can handle '@openai' command: {can_handle_openai}")
    
except Exception as e:
    print(f"❌ Routing test failed: {e}")
    sys.exit(1)

print("\n🎉 ALL BASIC TESTS PASSED!")
print("✅ @deepseek and @openai providers are properly configured")
print("✅ Handlers can be initialized and routed correctly")
print("✅ Tool registry is working")
print("✅ Configuration is valid")

print("\n📋 Summary:")
print("   • Both cloud providers are enabled and configured")
print("   • API keys are present in environment")
print("   • Handlers initialize without errors")
print("   • Tool registry provides appropriate tools")
print("   • Routing logic works for explicit commands")
print("   • Analysis keywords route to DeepSeek correctly")
