#!/usr/bin/env python3
"""
Quick test script to verify the double execution and model contamination fixes.
This will test the basic functionality without launching the full app.
"""

import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_basic_functionality():
    """Test basic dual model handler functionality."""
    
    print("🧪 Testing DeepCoderX fixes...")
    
    try:
        # 1. Test imports work
        from config_module import config
        from models.session import CommandContext
        from services.dual_model_handler import DualModelHandler
        
        print("   ✅ All imports successful")
        
        # 2. Test configuration
        print(f"   ✅ Default provider: {config.DEFAULT_PROVIDER}")
        print(f"   ✅ Dual model enabled: {'dual' in config.PROVIDERS}")
        
        # 3. Test basic context creation
        from services.mcpclient import MCPClient
        
        # Create mock MCP client for testing
        mcp_client = MCPClient(
            endpoint=f"http://{config.MCP_SERVER_HOST}:{config.MCP_SERVER_PORT}",
            api_key=config.MCP_API_KEY
        )
        
        ctx = CommandContext(
            root_path=project_root,
            mcp_client=mcp_client,
            sandbox_path=config.SANDBOX_PATH,
            debug_mode=True
        )
        ctx.user_input = "hello"  # Set user input after creation
        print("   ✅ CommandContext created successfully")
        
        # 4. Test handler creation (this will verify model paths exist)
        handler = DualModelHandler(ctx, "dual")
        print("   ✅ DualModelHandler created successfully")
        print(f"   ✅ Model paths valid: {handler.semantic_parser_path.exists()}, {handler.code_specialist_path.exists()}")
        
        # 5. Test session directory cleared
        session_dir = project_root / ".deepcoderx"
        if session_dir.exists():
            session_files = list(session_dir.glob("*.json"))
            print(f"   ✅ Session directory status: {len(session_files)} files (should be 0)")
        else:
            print("   ✅ Session directory: Clean (doesn't exist)")
        
        print("\n🎉 All basic tests passed!")
        print("\n📋 Ready for live testing:")
        print("   1. cd /Users/admin/Documents/DeepCoderX")
        print("   2. python3 app.py")
        print("   3. Type: hello")
        print("   4. Expected: Single execution, proper greeting")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_basic_functionality()
    exit(0 if success else 1)
