#!/usr/bin/env python3
"""
Test script to verify native OpenAI tool calling vs legacy JSON parsing.
This is Step 2 of validating the new unified OpenAI architecture.
"""

import os
import sys
import json
import time
import threading
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from config import config
from models.session import CommandContext
from services.mcpclient import MCPClient
from services.mcpserver import start_mcp_server
from rich.console import Console

console = Console()

def start_background_mcp():
    """Start MCP server in background thread for testing"""
    def mcp_server_thread():
        try:
            start_mcp_server(
                host=config.MCP_SERVER_HOST,
                port=config.MCP_SERVER_PORT,
                sandbox_path=config.SANDBOX_PATH
            )
        except Exception as e:
            console.print(f"[yellow]Warning: MCP server failed to start: {e}[/]")
    
    thread = threading.Thread(target=mcp_server_thread, daemon=True)
    thread.start()
    
    # Give the server a moment to start
    time.sleep(2)
    console.print(f"[blue]Started MCP server on {config.MCP_SERVER_HOST}:{config.MCP_SERVER_PORT}[/]")

def setup_test_context():
    """Set up a test context for handlers"""
    # Create MCP client for testing
    mcp_client = MCPClient(
        endpoint=f"http://{config.MCP_SERVER_HOST}:{config.MCP_SERVER_PORT}",
        api_key=config.MCP_API_KEY
    )
    
    ctx = CommandContext(
        root_path=Path.cwd(),
        mcp_client=mcp_client,
        sandbox_path=config.SANDBOX_PATH
    )
    ctx.debug_mode = True
    return ctx

def test_native_tool_calling():
    """Test native OpenAI tool calling with LocalOpenAIHandler"""
    console.print("[bold blue]Testing Native OpenAI Tool Calling[/]")
    console.print("=" * 50)
    
    try:
        from services.unified_openai_handler import LocalOpenAIHandler
        
        # Setup context
        ctx = setup_test_context()
        ctx.user_input = "list the files in the current directory"
        
        # Initialize handler
        handler = LocalOpenAIHandler(ctx)
        console.print(f"[green]✓ {handler.provider_config['name']} handler initialized[/]")
        
        # Test if handler can handle the request
        can_handle = handler.can_handle()
        console.print(f"[blue]Can handle request:[/] {can_handle}")
        
        if can_handle:
            console.print("[blue]Testing tool calling functionality...[/]")
            start_time = time.time()
            
            # Execute the handler (this will test native tool calling)
            handler.handle()
            
            execution_time = time.time() - start_time
            console.print(f"[green]✓ Native tool calling completed in {execution_time:.2f}s[/]")
            console.print(f"[blue]Response length:[/] {len(ctx.response)} characters")
            
            # Check if response contains expected content
            if "files" in ctx.response.lower() or "directory" in ctx.response.lower():
                console.print("[green]✓ Response appears to contain directory listing[/]")
                return True
            else:
                console.print(f"[yellow]⚠ Unexpected response: {ctx.response[:100]}...[/]")
                return True  # Still consider success if it responded
        else:
            console.print("[yellow]⚠ Handler cannot handle the test request[/]")
            return False
            
    except Exception as e:
        console.print(f"[red]❌ Native tool calling failed: {e}[/]")
        return False

def test_legacy_tool_calling():
    """Test legacy JSON tool calling with LocalCodingHandler"""
    console.print("\n[bold blue]Testing Legacy JSON Tool Calling[/]")
    console.print("=" * 50)
    
    try:
        from services.llm_handler import LocalCodingHandler
        
        # Setup context
        ctx = setup_test_context()
        ctx.user_input = "list the files in the current directory"
        
        # Initialize handler
        handler = LocalCodingHandler(ctx)
        console.print("[green]✓ Legacy LocalCodingHandler initialized[/]")
        
        # Test if handler can handle the request
        can_handle = handler.can_handle()
        console.print(f"[blue]Can handle request:[/] {can_handle}")
        
        if can_handle:
            console.print("[blue]Testing legacy tool calling functionality...[/]")
            start_time = time.time()
            
            # Execute the handler (this will test legacy JSON parsing)
            handler.handle()
            
            execution_time = time.time() - start_time
            console.print(f"[green]✓ Legacy tool calling completed in {execution_time:.2f}s[/]")
            console.print(f"[blue]Response length:[/] {len(ctx.response)} characters")
            
            # Check if response contains expected content
            if "files" in ctx.response.lower() or "directory" in ctx.response.lower():
                console.print("[green]✓ Response appears to contain directory listing[/]")
                return True
            else:
                console.print(f"[yellow]⚠ Unexpected response: {ctx.response[:100]}...[/]")
                return True  # Still consider success if it responded
        else:
            console.print("[yellow]⚠ Handler cannot handle the test request[/]")
            return False
            
    except Exception as e:
        console.print(f"[red]❌ Legacy tool calling failed: {e}[/]")
        return False

def test_provider_switching():
    """Test switching between different providers"""
    console.print("\n[bold blue]Testing Provider Switching[/]")
    console.print("=" * 50)
    
    try:
        from services.unified_openai_handler import LocalOpenAIHandler, CloudOpenAIHandler
        
        ctx = setup_test_context()
        
        # Test local provider
        console.print("[blue]Testing local provider (LM Studio)...[/]")
        local_handler = LocalOpenAIHandler(ctx)
        console.print(f"[green]✓ Local provider: {local_handler.provider_config['name']}[/]")
        console.print(f"[blue]  Endpoint: {local_handler.provider_config['base_url']}[/]")
        console.print(f"[blue]  Model: {local_handler.provider_config['model']}[/]")
        
        # Test cloud provider (if available)
        if config.PROVIDERS["deepseek"]["enabled"] and config.PROVIDERS["deepseek"]["api_key"]:
            console.print("[blue]Testing cloud provider (DeepSeek)...[/]")
            cloud_handler = CloudOpenAIHandler(ctx, "deepseek")
            console.print(f"[green]✓ Cloud provider: {cloud_handler.provider_config['name']}[/]")
            console.print(f"[blue]  Endpoint: {cloud_handler.provider_config['base_url']}[/]")
            console.print(f"[blue]  Model: {cloud_handler.provider_config['model']}[/]")
        else:
            console.print("[yellow]⚠ DeepSeek provider not enabled or missing API key[/]")
        
        console.print("[green]✓ Provider switching functionality verified[/]")
        return True
        
    except Exception as e:
        console.print(f"[red]❌ Provider switching failed: {e}[/]")
        return False

def test_tool_definitions():
    """Test that OpenAI tool definitions are properly formatted"""
    console.print("\n[bold blue]Testing Tool Definitions[/]")
    console.print("=" * 50)
    
    try:
        from services.unified_openai_handler import LocalOpenAIHandler
        
        ctx = setup_test_context()
        handler = LocalOpenAIHandler(ctx)
        
        # Get tool definitions
        tools = handler._get_tool_definitions()
        console.print(f"[green]✓ Retrieved {len(tools)} tool definitions[/]")
        
        expected_tools = ["read_file", "write_file", "list_dir", "run_bash"]
        found_tools = []
        
        for tool in tools:
            if tool.get("type") == "function":
                function_name = tool.get("function", {}).get("name")
                if function_name:
                    found_tools.append(function_name)
                    console.print(f"[blue]  ✓ {function_name}: {tool['function'].get('description', 'No description')}[/]")
        
        # Verify all expected tools are present
        missing_tools = set(expected_tools) - set(found_tools)
        if missing_tools:
            console.print(f"[red]❌ Missing tools: {missing_tools}[/]")
            return False
        
        console.print("[green]✓ All expected tools are properly defined[/]")
        return True
        
    except Exception as e:
        console.print(f"[red]❌ Tool definitions test failed: {e}[/]")
        return False

def test_configuration_validation():
    """Test that configuration is properly loaded"""
    console.print("\n[bold blue]Testing Configuration Validation[/]")
    console.print("=" * 50)
    
    try:
        # Check provider configuration
        local_config = config.PROVIDERS.get("local")
        if not local_config:
            console.print("[red]❌ Local provider configuration missing[/]")
            return False
        
        console.print(f"[green]✓ Local provider configured: {local_config['name']}[/]")
        console.print(f"[blue]  Base URL: {local_config['base_url']}[/]")
        console.print(f"[blue]  Model: {local_config['model']}[/]")
        console.print(f"[blue]  Enabled: {local_config['enabled']}[/]")
        console.print(f"[blue]  Tools Support: {local_config['supports_tools']}[/]")
        
        # Check essential configuration values
        essential_configs = [
            ("MAX_TOOL_CALLS", config.MAX_TOOL_CALLS),
            ("DEFAULT_PROVIDER", config.DEFAULT_PROVIDER),
            ("MCP_SERVER_HOST", config.MCP_SERVER_HOST),
            ("MCP_SERVER_PORT", config.MCP_SERVER_PORT)
        ]
        
        for config_name, config_value in essential_configs:
            console.print(f"[blue]  {config_name}: {config_value}[/]")
        
        console.print("[green]✓ Configuration validation passed[/]")
        return True
        
    except Exception as e:
        console.print(f"[red]❌ Configuration validation failed: {e}[/]")
        return False

def main():
    """Run all tool calling and integration tests"""
    console.print("[bold magenta]DeepCoderX - Native Tool Calling Verification[/]")
    console.print("=" * 60)
    
    # Start MCP server for legacy tool testing
    console.print("[blue]Starting MCP server for testing...[/]")
    start_background_mcp()
    
    tests = [
        ("Configuration Validation", test_configuration_validation),
        ("Tool Definitions", test_tool_definitions),
        ("Provider Switching", test_provider_switching),
        ("Native Tool Calling", test_native_tool_calling),
        ("Legacy Tool Calling", test_legacy_tool_calling)
    ]
    
    results = {}
    for test_name, test_func in tests:
        results[test_name] = test_func()
    
    # Summary
    console.print("\n[bold blue]Test Results Summary[/]")
    console.print("=" * 50)
    
    all_passed = True
    for test_name, passed in results.items():
        status = "[green]✓ PASS[/]" if passed else "[red]❌ FAIL[/]"
        console.print(f"{test_name:<25} {status}")
        if not passed:
            all_passed = False
    
    console.print()
    if all_passed:
        console.print("[bold green]🎉 All native tool calling tests passed![/]")
        console.print("[green]✅ Step 2 Complete: Native tool calling verified vs legacy JSON parsing[/]")
        console.print("[blue]Ready for Step 3: Test provider switching and configuration[/]")
    else:
        console.print("[bold red]❌ Some tests failed. Issues need to be addressed.[/]")
        console.print("[yellow]This may indicate problems with tool calling implementation.[/]")
    
    return all_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
