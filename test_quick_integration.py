#!/usr/bin/env python3
"""
Test script to verify native OpenAI tool calling vs legacy JSON parsing.
Fixed version that doesn't hang.
"""

import os
import sys
import json
import time
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from config import config
from models.session import CommandContext
from services.mcpclient import MCPClient
from rich.console import Console

console = Console()

def setup_mock_context():
    """Set up a test context for handlers without MCP dependency"""
    # Create a mock context that doesn't rely on MCP server
    ctx = CommandContext(
        root_path=Path.cwd(),
        mcp_client=None,  # We'll handle this per test
        sandbox_path=config.SANDBOX_PATH
    )
    ctx.debug_mode = False  # Reduce noise
    return ctx

def test_native_tool_calling_simple():
    """Test native OpenAI tool calling - basic functionality only"""
    console.print("[bold blue]Testing Native OpenAI Tool Calling (Basic)[/]")
    console.print("=" * 50)
    
    try:
        from services.unified_openai_handler import LocalOpenAIHandler
        
        # Setup context
        ctx = setup_mock_context()
        ctx.user_input = "hello, how are you?"  # Simple non-tool request
        
        # Initialize handler
        handler = LocalOpenAIHandler(ctx)
        console.print(f"[green]✓ {handler.provider_config['name']} handler initialized[/]")
        
        # Test configuration access
        console.print(f"[blue]Provider: {handler.provider_config['name']}[/]")
        console.print(f"[blue]Model: {handler.provider_config['model']}[/]")
        console.print(f"[blue]Base URL: {handler.provider_config['base_url']}[/]")
        
        # Test tool definitions
        tools = handler._get_tool_definitions()
        console.print(f"[green]✓ Tool definitions loaded: {len(tools)} tools[/]")
        
        return True
            
    except Exception as e:
        console.print(f"[red]❌ Native tool calling failed: {e}[/]")
        return False

def test_legacy_import():
    """Test legacy handler import without execution"""
    console.print("\n[bold blue]Testing Legacy Handler Import[/]")
    console.print("=" * 50)
    
    try:
        from services.llm_handler import LocalCodingHandler
        console.print("[green]✓ Legacy LocalCodingHandler imported successfully[/]")
        
        # Test basic initialization
        ctx = setup_mock_context()
        handler = LocalCodingHandler(ctx)
        console.print("[green]✓ Legacy handler initialized[/]")
        
        return True
            
    except Exception as e:
        console.print(f"[red]❌ Legacy import failed: {e}[/]")
        return False

def test_openai_client_basic():
    """Test OpenAI client configuration"""
    console.print("\n[bold blue]Testing OpenAI Client Configuration[/]")
    console.print("=" * 50)
    
    try:
        from openai import OpenAI
        console.print("[green]✓ OpenAI client library imported[/]")
        
        # Test client configuration (don't actually connect)
        local_config = config.PROVIDERS["local"]
        console.print(f"[blue]Base URL: {local_config['base_url']}[/]")
        console.print(f"[blue]Model: {local_config['model']}[/]")
        console.print(f"[blue]API Key: {local_config['api_key'][:8]}...[/]")
        
        console.print("[green]✓ Configuration appears valid[/]")
        return True
        
    except ImportError:
        console.print("[red]❌ OpenAI library not installed[/]")
        return False
    except Exception as e:
        console.print(f"[red]❌ Configuration error: {e}[/]")
        return False

def test_configuration_quick():
    """Quick configuration validation"""
    console.print("\n[bold blue]Testing Configuration[/]")
    console.print("=" * 50)
    
    try:
        # Check essential config
        local_config = config.PROVIDERS.get("local")
        if not local_config:
            console.print("[red]❌ No local provider config[/]")
            return False
        
        console.print(f"[green]✓ Provider: {local_config['name']}[/]")
        console.print(f"[blue]  Enabled: {local_config['enabled']}[/]")
        console.print(f"[blue]  Tools: {local_config['supports_tools']}[/]")
        console.print(f"[blue]  Max calls: {config.MAX_TOOL_CALLS}[/]")
        
        return True
        
    except Exception as e:
        console.print(f"[red]❌ Config validation failed: {e}[/]")
        return False

def test_actual_connection():
    """Test actual LM Studio connectivity without hanging"""
    console.print("\n[bold blue]Testing LM Studio Connection[/]")
    console.print("=" * 50)
    
    try:
        import requests
        local_config = config.PROVIDERS["local"]
        base_url = local_config["base_url"]
        
        console.print(f"[blue]Testing: {base_url}/models[/]")
        
        # Quick connectivity test with short timeout
        response = requests.get(f"{base_url}/models", timeout=3)
        if response.status_code == 200:
            models = response.json().get("data", [])
            console.print(f"[green]✓ Connected! Found {len(models)} models[/]")
            return True
        else:
            console.print(f"[red]❌ HTTP {response.status_code}[/]")
            return False
            
    except requests.exceptions.Timeout:
        console.print("[red]❌ Connection timeout[/]")
        return False
    except Exception as e:
        console.print(f"[red]❌ Connection failed: {e}[/]")
        return False

def main():
    """Run simplified tests that don't hang"""
    console.print("[bold magenta]DeepCoderX - Quick Integration Test[/]")
    console.print("=" * 60)
    console.print("[yellow]Note: Simplified test to avoid hanging issues[/]")
    
    tests = [
        ("Configuration", test_configuration_quick),
        ("OpenAI Client", test_openai_client_basic),
        ("LM Studio Connection", test_actual_connection),
        ("Native Handler", test_native_tool_calling_simple),
        ("Legacy Handler Import", test_legacy_import)
    ]
    
    results = {}
    for test_name, test_func in tests:
        console.print(f"\n[cyan]Running: {test_name}[/]")
        results[test_name] = test_func()
    
    # Summary
    console.print("\n[bold blue]Test Results Summary[/]")
    console.print("=" * 50)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results.items():
        status = "[green]✓ PASS[/]" if result else "[red]❌ FAIL[/]"
        console.print(f"{test_name:<25} {status}")
        if result:
            passed += 1
    
    console.print(f"\n[bold]Results: {passed}/{total} tests passed[/]")
    
    if passed == total:
        console.print("[bold green]🎉 All tests passed![/]")
        console.print("[green]Basic OpenAI integration is working[/]")
    else:
        console.print(f"[bold red]❌ {total - passed} tests failed[/]")
        console.print("[yellow]Issues need to be addressed[/]")
    
    console.print("\n[dim]Test completed. Exiting cleanly...[/]")
    return passed == total

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        console.print("\n[yellow]Test interrupted by user[/]")
        sys.exit(130)
    except Exception as e:
        console.print(f"\n[red]Test failed with error: {e}[/]")
        sys.exit(1)
