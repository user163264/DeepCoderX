#!/usr/bin/env python3
"""
Manual Step-by-Step Test for DeepSeek Fix
Run this to manually verify each component works
"""

def test_step_1():
    """Test 1: Basic imports and config"""
    print("🔧 STEP 1: Testing basic imports and configuration")
    print("-" * 50)
    
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

def test_step_2():
    """Test 2: MCPClient creation with parameters"""
    print("\n🔧 STEP 2: Testing MCPClient initialization")
    print("-" * 50)
    
    try:
        from config import config
        from services.mcpclient import MCPClient
        
        # This is the fix - using parameters instead of MCPClient()
        mcp_client = MCPClient(
            endpoint=f"http://{config.MCP_SERVER_HOST}:{config.MCP_SERVER_PORT}",
            api_key=config.MCP_API_KEY
        )
        
        print("✅ MCPClient created successfully with required parameters")
        print(f"   Endpoint: {mcp_client.endpoint}")
        print(f"   Headers: {list(mcp_client.headers.keys())}")
        return True, mcp_client
    except Exception as e:
        print(f"❌ MCPClient creation failed: {e}")
        return False, None

def test_step_3(mcp_client):
    """Test 3: CommandContext creation"""
    print("\n🔧 STEP 3: Testing CommandContext creation")
    print("-" * 50)
    
    try:
        from pathlib import Path
        from models.session import CommandContext
        from config import config
        
        test_dir = Path('/Users/admin/Documents/DeepCoderX')
        
        ctx = CommandContext(
            root_path=test_dir,
            mcp_client=mcp_client,
            sandbox_path=config.SANDBOX_PATH,
            debug_mode=True
        )
        
        print("✅ CommandContext created successfully")
        print(f"   Root path: {ctx.root_path}")
        print(f"   Has MCP client: {ctx.mcp_client is not None}")
        return True, ctx
    except Exception as e:
        print(f"❌ CommandContext creation failed: {e}")
        return False, None

def test_step_4(ctx):
    """Test 4: CloudOpenAIHandler creation"""
    print("\n🔧 STEP 4: Testing CloudOpenAIHandler creation")
    print("-" * 50)
    
    try:
        from services.unified_openai_handler import CloudOpenAIHandler
        
        handler = CloudOpenAIHandler(ctx, "deepseek")
        
        print("✅ CloudOpenAIHandler created successfully")
        print(f"   Provider: {handler.provider_name}")
        print(f"   Provider config: {handler.provider_config['name']}")
        print(f"   Session file: {handler.session_file}")
        return True
    except Exception as e:
        print(f"❌ CloudOpenAIHandler creation failed: {e}")
        return False

def main():
    """Run all manual tests step by step"""
    print("🔬 MANUAL DEEPSEEK FIX VALIDATION")
    print("=" * 60)
    print("This will test each component step by step to verify the fix.")
    print("If any step fails, the issue will be clearly identified.")
    
    # Step 1: Config
    if not test_step_1():
        print("\n💥 FAILED at Step 1 - Config import issues")
        return False
    
    # Step 2: MCPClient
    success, mcp_client = test_step_2()
    if not success:
        print("\n💥 FAILED at Step 2 - MCPClient initialization issues")
        print("🔧 This was the main bug that has been fixed!")
        return False
    
    # Step 3: CommandContext
    success, ctx = test_step_3(mcp_client)
    if not success:
        print("\n💥 FAILED at Step 3 - CommandContext creation issues")
        return False
    
    # Step 4: Handler
    if not test_step_4(ctx):
        print("\n💥 FAILED at Step 4 - CloudOpenAIHandler creation issues")
        return False
    
    # Success!
    print("\n" + "=" * 60)
    print("🎉 ALL MANUAL TESTS PASSED!")
    print("✅ The MCPClient initialization fix is working perfectly")
    print("🚀 DeepSeek test suite should now run without errors")
    print("\n💡 Ready to run: python test_deepseek_tools.py")
    print("=" * 60)
    
    return True

if __name__ == "__main__":
    import sys
    import os
    from pathlib import Path
    
    # Ensure we're in the right directory
    project_dir = Path('/Users/admin/Documents/DeepCoderX')
    os.chdir(project_dir)
    sys.path.insert(0, str(project_dir))
    
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n🛑 Test interrupted")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
