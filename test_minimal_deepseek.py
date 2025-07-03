#!/usr/bin/env python3
"""
Quick DeepSeek Test - Minimal reproduction of @deepseek command
"""

import sys
import time
import os
from pathlib import Path

# Setup
project_dir = Path('/Users/admin/Documents/DeepCoderX')
os.chdir(project_dir)
sys.path.insert(0, str(project_dir))

def test_minimal_deepseek():
    """Test minimal DeepSeek interaction"""
    print("🧪 MINIMAL DEEPSEEK TEST")
    print("=" * 40)
    
    try:
        # Import everything
        print("1. Importing modules...")
        from config import config
        from models.session import CommandContext
        from services.mcpclient import MCPClient
        from services.unified_openai_handler import CloudOpenAIHandler
        
        # Create setup
        print("2. Creating MCP client...")
        mcp_client = MCPClient(
            endpoint=f"http://{config.MCP_SERVER_HOST}:{config.MCP_SERVER_PORT}",
            api_key=config.MCP_API_KEY
        )
        
        print("3. Creating context...")
        ctx = CommandContext(project_dir, mcp_client, config.SANDBOX_PATH, True)
        ctx.user_input = "how are you today?"
        
        print("4. Creating DeepSeek handler...")
        start_time = time.time()
        handler = CloudOpenAIHandler(ctx, "deepseek")
        handler_time = time.time() - start_time
        print(f"   Handler created in {handler_time:.2f}s")
        
        print("5. Testing client access...")
        start_time = time.time()
        client = handler.client
        client_time = time.time() - start_time
        print(f"   Client initialized in {client_time:.2f}s")
        
        print("6. Testing simple completion...")
        start_time = time.time()
        
        # Create a simple completion without tools
        response = client.chat.completions.create(
            model="deepseek-coder",
            messages=[{"role": "user", "content": "Say hello in exactly 5 words"}],
            max_tokens=20,
            timeout=30
        )
        
        api_time = time.time() - start_time
        print(f"   API call completed in {api_time:.2f}s")
        print(f"   Response: {response.choices[0].message.content}")
        
        print("\n✅ SUCCESS: All components working quickly")
        print(f"📊 Total time: {handler_time + client_time + api_time:.2f}s")
        
        if handler_time + client_time + api_time < 5:
            print("\n💡 The issue is likely in the app's conversation loop")
            print("   Possible causes:")
            print("   - Tool calling loop not terminating")
            print("   - Context building taking too long")
            print("   - Session management issues")
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_minimal_deepseek()
