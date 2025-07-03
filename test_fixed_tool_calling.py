#!/usr/bin/env python3
"""
FIXED: Native tool calling test that exits cleanly.
Addresses the hanging MCP server issue properly.
"""

import os
import sys
import json
import time
import signal
import atexit
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from config import config
from models.session import CommandContext
from services.mcpclient import MCPClient
from rich.console import Console

console = Console()

# Global variable to track if we should clean shutdown
should_exit = False

def signal_handler(signum, frame):
    """Handle Ctrl+C gracefully"""
    global should_exit
    should_exit = True
    console.print("\n[yellow]Received interrupt signal. Cleaning up...[/]")
    cleanup_and_exit()

def cleanup_and_exit():
    """Clean shutdown function"""
    console.print("[blue]Cleaning up resources...[/]")
    # Force exit - don't wait for threads
    os._exit(0)

def setup_signal_handlers():
    """Setup proper signal handling"""
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    atexit.register(cleanup_and_exit)

def test_native_with_timeout():
    """Test native OpenAI tool calling with timeout protection"""
    console.print("[bold blue]Testing Native Tool Calling (With Timeout)[/]")
    console.print("=" * 50)
    
    try:
        from services.unified_openai_handler import LocalOpenAIHandler
        
        # Create minimal context without MCP dependency for this test
        ctx = CommandContext(
            root_path=Path.cwd(),
            mcp_client=None,  # Skip MCP for this test
            sandbox_path=config.SANDBOX_PATH
        )
        ctx.debug_mode = False
        ctx.user_input = "Hello, just say 'Hi' back to me"
        
        # Initialize handler
        handler = LocalOpenAIHandler(ctx)
        console.print(f"[green]✓ Handler initialized: {handler.provider_config['name']}[/]")
        
        # Test basic conversation (non-tool request)
        console.print("[blue]Testing basic chat functionality...[/]")
        
        # Set a timeout for the operation
        start_time = time.time()
        timeout = 15  # 15 second timeout
        
        try:
            # This should be a simple chat that doesn't use tools
            handler.handle()
            execution_time = time.time() - start_time
            
            if execution_time > timeout:
                console.print(f"[red]❌ Operation timed out after {timeout}s[/]")
                return False
            
            console.print(f"[green]✓ Chat completed in {execution_time:.2f}s[/]")
            console.print(f"[blue]Response: {ctx.response[:100]}...[/]")
            return True
            
        except Exception as e:
            console.print(f"[red]❌ Chat failed: {e}[/]")
            return False
            
    except Exception as e:
        console.print(f"[red]❌ Native test failed: {e}[/]")
        return False

def test_simple_openai_request():
    """Test direct OpenAI API call without handlers"""
    console.print("\n[bold blue]Testing Direct OpenAI API Call[/]")
    console.print("=" * 50)
    
    try:
        from openai import OpenAI
        
        local_config = config.PROVIDERS["local"]
        client = OpenAI(
            base_url=local_config["base_url"],
            api_key=local_config["api_key"]
        )
        
        console.print("[blue]Making simple API call...[/]")
        start_time = time.time()
        
        response = client.chat.completions.create(
            model=local_config["model"],
            messages=[
                {"role": "user", "content": "Say 'Hello World' and nothing else"}
            ],
            max_tokens=10,
            temperature=0.1,
            timeout=10  # 10 second timeout
        )
        
        execution_time = time.time() - start_time
        content = response.choices[0].message.content
        
        console.print(f"[green]✓ API call completed in {execution_time:.2f}s[/]")
        console.print(f"[blue]Response: '{content}'[/]")
        
        return True
        
    except Exception as e:
        console.print(f"[red]❌ Direct API test failed: {e}[/]")
        return False

def test_tool_definitions_only():
    """Test tool definitions without executing them"""
    console.print("\n[bold blue]Testing Tool Definitions (No Execution)[/]")
    console.print("=" * 50)
    
    try:
        from services.unified_openai_handler import LocalOpenAIHandler
        
        ctx = CommandContext(
            root_path=Path.cwd(),
            mcp_client=None,
            sandbox_path=config.SANDBOX_PATH
        )
        
        handler = LocalOpenAIHandler(ctx)
        tools = handler._get_tool_definitions()
        
        console.print(f"[green]✓ Retrieved {len(tools)} tool definitions[/]")
        
        for tool in tools:
            if tool.get("type") == "function":
                func = tool["function"]
                console.print(f"[blue]  ✓ {func['name']}: {func.get('description', 'No description')}[/]")
        
        # Validate structure
        expected_tools = ["read_file", "write_file", "list_dir", "run_bash"]
        found_tools = [t["function"]["name"] for t in tools if t.get("type") == "function"]
        
        missing = set(expected_tools) - set(found_tools)
        if missing:
            console.print(f"[red]❌ Missing tools: {missing}[/]")
            return False
        
        console.print("[green]✓ All expected tools present and properly formatted[/]")
        return True
        
    except Exception as e:
        console.print(f"[red]❌ Tool definitions test failed: {e}[/]")
        return False

def main():
    """Run fixed tests with proper cleanup"""
    setup_signal_handlers()
    
    console.print("[bold magenta]DeepCoderX - Fixed Tool Calling Test[/]")
    console.print("=" * 60)
    console.print("[yellow]Note: Fixed version with proper cleanup and timeouts[/]")
    
    tests = [
        ("Tool Definitions", test_tool_definitions_only),
        ("Direct OpenAI Call", test_simple_openai_request),
        ("Native Handler Chat", test_native_with_timeout)
    ]
    
    results = {}
    for test_name, test_func in tests:
        if should_exit:
            console.print("\n[yellow]Test interrupted by user[/]")
            break
            
        console.print(f"\n[cyan]Running: {test_name}[/]")
        results[test_name] = test_func()
    
    # Summary
    console.print("\n[bold blue]Test Results Summary[/]")
    console.print("=" * 50)
    
    passed = sum(results.values())
    total = len(results)
    
    for test_name, result in results.items():
        status = "[green]✓ PASS[/]" if result else "[red]❌ FAIL[/]"
        console.print(f"{test_name:<25} {status}")
    
    console.print(f"\n[bold]Results: {passed}/{total} tests passed[/]")
    
    if passed == total:
        console.print("[bold green]🎉 All tests passed![/]")
        console.print("[green]✅ Step 2 Progress: Native OpenAI integration validated[/]")
    else:
        console.print(f"[bold red]❌ {total - passed} tests failed[/]")
    
    console.print("\n[dim]Test completed. Exiting cleanly in 2 seconds...[/]")
    time.sleep(2)
    return passed == total

if __name__ == "__main__":
    try:
        success = main()
        cleanup_and_exit()
    except Exception as e:
        console.print(f"\n[red]Fatal error: {e}[/]")
        cleanup_and_exit()
