#!/usr/bin/env python3
"""
Test the app's command routing for @deepseek
"""

import sys
import time
import os
from pathlib import Path

# Setup
project_dir = Path('/Users/admin/Documents/DeepCoderX')
os.chdir(project_dir)
sys.path.insert(0, str(project_dir))

def test_app_routing():
    """Test how the app routes @deepseek commands"""
    print("🧪 TESTING APP ROUTING FOR @DEEPSEEK")
    print("=" * 50)
    
    try:
        # Import app components
        from config import config
        from models.session import CommandContext
        from models.router import CommandProcessor
        from services.mcpclient import MCPClient
        
        print("1. Creating app context...")
        
        # Create MCP client
        mcp_client = MCPClient(
            endpoint=f"http://{config.MCP_SERVER_HOST}:{config.MCP_SERVER_PORT}",
            api_key=config.MCP_API_KEY
        )
        
        # Create context
        ctx = CommandContext(project_dir, mcp_client, config.SANDBOX_PATH, True)
        ctx.user_input = "@deepseek how are you today?"
        
        print("2. Creating command processor...")
        processor = CommandProcessor(ctx)
        
        print("3. Testing routing...")
        start_time = time.time()
        
        # This is what the app does - find the right handler
        for handler_class in processor.handlers:
            if hasattr(handler_class, 'can_handle'):
                handler = handler_class(ctx)
                if handler.can_handle():
                    print(f"   ✅ Routed to: {handler_class.__name__}")
                    
                    # Test the handler creation time
                    handler_start = time.time()
                    try:
                        # Don't actually call handle() - just test setup
                        print(f"   📋 Handler type: {type(handler).__name__}")
                        print(f"   📋 Setup time: {time.time() - handler_start:.2f}s")
                        break
                    except Exception as e:
                        print(f"   ❌ Handler error: {e}")
                        break
        
        routing_time = time.time() - start_time
        print(f"\n📊 Routing completed in: {routing_time:.2f}s")
        
        if routing_time > 5:
            print("🚨 SLOW ROUTING DETECTED!")
        else:
            print("✅ Routing is fast - issue must be in handler.handle()")
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()

def test_handler_handle_method():
    """Test the actual handle() method that's taking 120s"""
    print("\n🧪 TESTING HANDLER.HANDLE() METHOD")
    print("=" * 50)
    
    try:
        from config import config
        from models.session import CommandContext
        from services.mcpclient import MCPClient
        from services.unified_openai_handler import CloudOpenAIHandler
        
        # Create setup
        mcp_client = MCPClient(
            endpoint=f"http://{config.MCP_SERVER_HOST}:{config.MCP_SERVER_PORT}",
            api_key=config.MCP_API_KEY
        )
        
        ctx = CommandContext(project_dir, mcp_client, config.SANDBOX_PATH, True)
        ctx.user_input = "@deepseek how are you today?"
        
        # Create handler but don't call handle()
        handler = CloudOpenAIHandler(ctx, "deepseek")
        
        print("✅ Handler created successfully")
        print("⚠️  NOT calling handle() to avoid 120s delay")
        print("\n💡 The issue is likely in:")
        print("   - handler.handle() method")
        print("   - _conversation_loop() method") 
        print("   - Tool calling loop")
        print("   - Context building during handle()")
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_app_routing()
    test_handler_handle_method()
