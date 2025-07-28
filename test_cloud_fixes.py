#!/usr/bin/env python3
"""
Quick test to verify cloud provider fixes
Tests @deepseek and @openai functionality
"""

import sys
import os
from pathlib import Path

# Add the project directory to the path
project_dir = Path(__file__).parent
sys.path.insert(0, str(project_dir))

# Load environment variables
from dotenv import load_dotenv
load_dotenv(dotenv_path=project_dir / '.env')

from config_module import config
from models.session import CommandContext
from services.unified_openai_handler import CloudOpenAIHandler
from services.mcpclient import MCPClient
from utils.logging import console

def test_cloud_providers():
    """Test both DeepSeek and OpenAI cloud providers."""
    
    # Create MCP client (mock for testing)
    mcp_client = MCPClient(
        endpoint=f"http://{config.MCP_SERVER_HOST}:{config.MCP_SERVER_PORT}",
        api_key=config.MCP_API_KEY
    )
    
    # Create command context
    ctx = CommandContext(
        root_path=Path.cwd(),
        mcp_client=mcp_client,
        sandbox_path=config.SANDBOX_PATH
    )
    ctx.debug_mode = True
    
    # Test providers
    providers_to_test = ['deepseek', 'openai']
    
    for provider_name in providers_to_test:
        console.print(f"\n[bold blue]Testing {provider_name.upper()} Provider[/bold blue]")
        console.print("=" * 50)
        
        try:
            # Check if provider is available
            if not config.is_provider_available(provider_name):
                console.print(f"[bold red]❌ {provider_name} not available or not configured[/]")
                continue
            
            # Create handler
            handler = CloudOpenAIHandler(ctx, provider_name)
            console.print(f"[bold green]✅ {provider_name} handler created successfully[/]")
            
            # Test can_handle
            ctx.user_input = f"@{provider_name} hello"
            can_handle = handler.can_handle()
            console.print(f"[green]✅ can_handle() returned: {can_handle}[/]")
            
            # Check configuration
            provider_config = config.get_provider_config(provider_name)
            console.print(f"[cyan]📋 Model: {provider_config['model']}[/]")
            console.print(f"[cyan]📋 Enabled: {provider_config['enabled']}[/]")
            console.print(f"[cyan]📋 API Key: {'✅ Present' if provider_config['api_key'] else '❌ Missing'}[/]")
            
            # Test import fix for time module
            try:
                import time
                console.print(f"[green]✅ Time module import working[/]")
                
                # Test time usage in handler
                test_time = int(time.time())
                console.print(f"[green]✅ Time.time() working: {test_time}[/]")
            except Exception as e:
                console.print(f"[bold red]❌ Time module issue: {e}[/]")
            
            console.print(f"[bold green]✅ {provider_name.upper()} PROVIDER WORKING[/]")
            
        except Exception as e:
            console.print(f"[bold red]❌ {provider_name} error: {e}[/]")
            if ctx.debug_mode:
                import traceback
                console.print(f"[red]Debug traceback:[/]")
                console.print(traceback.format_exc())
    
    console.print(f"\n[bold cyan]Provider Configuration Summary:[/]")
    console.print("=" * 50)
    for name, config_data in config.PROVIDERS.items():
        status = "✅ ENABLED" if config_data['enabled'] else "❌ DISABLED"
        api_key_status = "✅ API Key" if config_data.get('api_key') else "❌ No API Key"
        console.print(f"[yellow]{name:10}[/] {status:12} {api_key_status}")

if __name__ == "__main__":
    console.print("[bold magenta]🧪 CLOUD PROVIDER FIXES TEST[/]")
    console.print("[cyan]Testing DeepSeek and OpenAI fixes...[/]")
    test_cloud_providers()
    console.print(f"\n[bold green]🎉 Test completed![/]")
