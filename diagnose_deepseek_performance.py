#!/usr/bin/env python3
"""
DeepSeek Performance Diagnostic
Identify why @deepseek commands are taking 120 seconds
"""

import sys
import time
import os
from pathlib import Path

# Setup
project_dir = Path('/Users/admin/Documents/DeepCoderX')
os.chdir(project_dir)
sys.path.insert(0, str(project_dir))

def time_operation(name, func):
    """Time an operation and report results"""
    print(f"⏱️  Testing: {name}")
    start_time = time.time()
    try:
        result = func()
        elapsed = time.time() - start_time
        print(f"   ✅ {name}: {elapsed:.2f}s")
        return result, elapsed
    except Exception as e:
        elapsed = time.time() - start_time
        print(f"   ❌ {name}: {elapsed:.2f}s - ERROR: {e}")
        return None, elapsed

def test_basic_imports():
    """Test basic imports"""
    from config import config
    from models.session import CommandContext
    from services.mcpclient import MCPClient
    from services.unified_openai_handler import CloudOpenAIHandler
    return True

def test_mcp_client_creation():
    """Test MCP client creation"""
    from config import config
    from services.mcpclient import MCPClient
    
    mcp_client = MCPClient(
        endpoint=f"http://{config.MCP_SERVER_HOST}:{config.MCP_SERVER_PORT}",
        api_key=config.MCP_API_KEY
    )
    return mcp_client

def test_context_creation():
    """Test CommandContext creation"""
    from config import config
    from models.session import CommandContext
    
    mcp_client = test_mcp_client_creation()[0]
    ctx = CommandContext(project_dir, mcp_client, config.SANDBOX_PATH, True)
    return ctx

def test_handler_creation():
    """Test CloudOpenAIHandler creation (without client access)"""
    from services.unified_openai_handler import CloudOpenAIHandler
    
    ctx = test_context_creation()[0]
    handler = CloudOpenAIHandler(ctx, "deepseek")
    return handler

def test_openai_client_initialization():
    """Test OpenAI client initialization"""
    handler = test_handler_creation()[0]
    client = handler.client  # This triggers lazy loading
    return client

def test_context_building():
    """Test context building process"""
    from services.context_manager import ContextManager
    
    ctx = test_context_creation()[0]
    context_manager = ContextManager(ctx)
    
    # Test if context file exists
    if context_manager.context_file_exists():
        context = context_manager.read_context_file()
    else:
        context = context_manager.build_and_save_context()
    
    return len(context)

def test_simple_api_call():
    """Test a simple API call to DeepSeek"""
    from config import config
    import requests
    
    # Simple API connectivity test
    headers = {
        "Authorization": f"Bearer {config.PROVIDERS['deepseek']['api_key']}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": "deepseek-coder",
        "messages": [{"role": "user", "content": "Hello"}],
        "max_tokens": 10
    }
    
    response = requests.post(
        "https://api.deepseek.com/v1/chat/completions",
        headers=headers,
        json=payload,
        timeout=30
    )
    
    return response.status_code == 200

def main():
    """Run performance diagnostics"""
    print("🔍 DEEPSEEK PERFORMANCE DIAGNOSTICS")
    print("=" * 50)
    print("Identifying why @deepseek takes 120 seconds...")
    
    # Test each component
    tests = [
        ("Basic Imports", test_basic_imports),
        ("MCP Client Creation", test_mcp_client_creation),
        ("Context Creation", test_context_creation),
        ("Handler Creation", test_handler_creation),
        ("OpenAI Client Init", test_openai_client_initialization),
        ("Context Building", test_context_building),
        ("Simple API Call", test_simple_api_call),
    ]
    
    results = []
    total_time = 0
    
    for name, test_func in tests:
        result, elapsed = time_operation(name, test_func)
        results.append((name, elapsed, result is not None))
        total_time += elapsed
        
        # Stop if any test takes too long
        if elapsed > 30:
            print(f"\n🚨 BOTTLENECK FOUND: '{name}' took {elapsed:.2f}s")
            print("   This is likely the cause of the 120s delay")
            break
    
    print(f"\n📊 SUMMARY")
    print("=" * 50)
    print(f"Total time: {total_time:.2f}s")
    
    for name, elapsed, success in results:
        status = "✅" if success else "❌"
        print(f"{status} {name}: {elapsed:.2f}s")
    
    # Recommendations
    print(f"\n💡 RECOMMENDATIONS")
    print("=" * 50)
    
    if any(elapsed > 10 for _, elapsed, _ in results):
        slow_tests = [(name, elapsed) for name, elapsed, _ in results if elapsed > 10]
        print("🔧 Slow operations found:")
        for name, elapsed in slow_tests:
            print(f"   - {name}: {elapsed:.2f}s")
            
            if "API Call" in name:
                print("     → Check network connectivity to DeepSeek")
                print("     → Verify API key is valid")
            elif "Context Building" in name:
                print("     → Context file may be too large")
                print("     → Consider optimizing context generation")
            elif "Client Init" in name:
                print("     → OpenAI client initialization issue")
    else:
        print("✅ All individual operations are fast")
        print("🔍 Issue may be in the conversation loop or tool calling")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n🛑 Diagnostic interrupted")
    except Exception as e:
        print(f"\n💥 Diagnostic error: {e}")
        import traceback
        traceback.print_exc()
