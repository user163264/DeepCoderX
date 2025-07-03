#!/usr/bin/env python3
"""
Debug script to understand why @deepseek commands aren't working in app.py
"""

import sys
import os
from pathlib import Path

# Add project to path
sys.path.insert(0, str(Path(__file__).parent))

from config import config
from models.session import CommandContext
from models.router import CommandProcessor
from services.mcpclient import MCPClient

def test_deepseek_routing():
    """Test DeepSeek command routing"""
    print("=== DeepSeek Routing Debug ===\n")
    
    # Check configuration
    print("1. Configuration Check:")
    print(f"   DEFAULT_PROVIDER: {config.DEFAULT_PROVIDER}")
    print(f"   DeepSeek enabled: {config.PROVIDERS['deepseek']['enabled']}")
    print(f"   DeepSeek API key set: {'Yes' if config.PROVIDERS['deepseek']['api_key'] else 'No'}")
    print()
    
    # Check OpenAI imports
    print("2. OpenAI Import Check:")
    try:
        from services.unified_openai_handler import LocalOpenAIHandler, CloudOpenAIHandler
        print("   ✓ OpenAI handlers imported successfully")
        OPENAI_AVAILABLE = True
    except ImportError as e:
        print(f"   ✗ OpenAI import failed: {e}")
        OPENAI_AVAILABLE = False
    print()
    
    # Test handler creation
    print("3. Handler Creation Test:")
    try:
        # Create mock context
        mcp_client = MCPClient(
            endpoint=f"http://{config.MCP_SERVER_HOST}:{config.MCP_SERVER_PORT}",
            api_key=config.MCP_API_KEY
        )
        
        ctx = CommandContext(
            root_path=Path.cwd(),
            mcp_client=mcp_client,
            sandbox_path=config.SANDBOX_PATH
        )
        
        processor = CommandProcessor(ctx)
        
        if OPENAI_AVAILABLE:
            # Try to create handlers
            try:
                cloud_handler = CloudOpenAIHandler(ctx, "deepseek")
                print("   ✓ CloudOpenAIHandler created successfully")
                processor.add_handler(cloud_handler)
                
                local_handler = LocalOpenAIHandler(ctx)
                print("   ✓ LocalOpenAIHandler created successfully")
                processor.add_handler(local_handler)
                
            except Exception as e:
                print(f"   ✗ Handler creation failed: {e}")
                return
        else:
            print("   ⚠ Skipping handler creation (OpenAI not available)")
            return
            
    except Exception as e:
        print(f"   ✗ Context setup failed: {e}")
        return
    print()
    
    # Test command routing
    print("4. Command Routing Test:")
    test_commands = [
        "@deepseek hello",
        "@deepseek analyze this project",
        "hello",
        "analyze this code"
    ]
    
    for cmd in test_commands:
        print(f"   Testing: '{cmd}'")
        ctx.user_input = cmd
        
        # Find which handler would handle this
        for i, handler in enumerate(processor.handlers):
            if handler.can_handle():
                handler_name = type(handler).__name__
                print(f"     → Handler {i}: {handler_name}")
                break
        else:
            print("     → No handler found")
        print()

if __name__ == "__main__":
    test_deepseek_routing()
