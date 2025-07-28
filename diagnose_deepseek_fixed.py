#!/usr/bin/env python3
"""
Fixed DeepSeek Performance Diagnostic
"""

import sys
import time
import os
from pathlib import Path

# Setup
project_dir = Path('/Users/admin/Documents/DeepCoderX')
os.chdir(project_dir)
sys.path.insert(0, str(project_dir))

def main():
    """Run performance diagnostics step by step"""
    print("🔍 DEEPSEEK PERFORMANCE DIAGNOSTICS - FIXED")
    print("=" * 50)
    
    try:
        # Test 1: Basic imports
        print("1. Testing imports...")
        start = time.time()
        from config import config
        from models.session import CommandContext
        from services.mcpclient import MCPClient
        from services.unified_openai_handler import CloudOpenAIHandler
        print(f"   ✅ Imports: {time.time() - start:.2f}s")
        
        # Test 2: MCP Client
        print("2. Creating MCP client...")
        start = time.time()
        mcp_client = MCPClient(
            endpoint=f"http://{config.MCP_SERVER_HOST}:{config.MCP_SERVER_PORT}",
            api_key=config.MCP_API_KEY
        )
        print(f"   ✅ MCP Client: {time.time() - start:.2f}s")
        
        # Test 3: Context Creation
        print("3. Creating context...")
        start = time.time()
        ctx = CommandContext(project_dir, mcp_client, config.SANDBOX_PATH, True)
        ctx.user_input = "how are you today?"
        print(f"   ✅ Context: {time.time() - start:.2f}s")
        
        # Test 4: Handler Creation
        print("4. Creating DeepSeek handler...")
        start = time.time()
        handler = CloudOpenAIHandler(ctx, "deepseek")
        handler_time = time.time() - start
        print(f"   ✅ Handler: {handler_time:.2f}s")
        
        if handler_time > 10:
            print("   🚨 SLOW: Handler creation is taking too long!")
            print("   This includes context building and session loading")
            return
        
        # Test 5: Client Initialization
        print("5. Initializing OpenAI client...")
        start = time.time()
        client = handler.client
        client_time = time.time() - start
        print(f"   ✅ Client: {client_time:.2f}s")
        
        # Test 6: Simple API call
        print("6. Testing API call...")
        start = time.time()
        response = client.chat.completions.create(
            model="deepseek-coder",
            messages=[{"role": "user", "content": "Hello"}],
            max_tokens=10,
            timeout=10
        )
        api_time = time.time() - start
        print(f"   ✅ API Call: {api_time:.2f}s")
        print(f"   Response: {response.choices[0].message.content}")
        
        total_time = handler_time + client_time + api_time
        print(f"\n📊 TOTAL TIME: {total_time:.2f}s")
        
        if total_time < 5:
            print("✅ All components are fast!")
            print("🔍 The 120s delay must be in the app's conversation loop")
            print("\nLikely causes:")
            print("- Tool calling infinite loop")
            print("- Session management hanging")
            print("- Context rebuilding on every call")
        else:
            print("🚨 Found slow component!")
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
