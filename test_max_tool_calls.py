#!/usr/bin/env python3
"""
Quick test to verify MAX_TOOL_CALLS configuration change.
"""

import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from config import config
from rich.console import Console

console = Console()

def test_max_tool_calls_config():
    """Test that MAX_TOOL_CALLS has been updated to 50"""
    console.print("[bold blue]Testing MAX_TOOL_CALLS Configuration[/]")
    console.print("=" * 50)
    
    max_calls = config.MAX_TOOL_CALLS
    console.print(f"[blue]Current MAX_TOOL_CALLS value: {max_calls}[/]")
    
    if max_calls == 50:
        console.print("[green]✓ MAX_TOOL_CALLS correctly set to 50[/]")
        console.print("[green]✓ Models can now use up to 50 tools before user confirmation[/]")
        return True
    elif max_calls == 5:
        console.print("[red]❌ MAX_TOOL_CALLS still set to 5 (old emergency limit)[/]")
        console.print("[yellow]The configuration change may not have taken effect[/]")
        return False
    else:
        console.print(f"[yellow]⚠ MAX_TOOL_CALLS set to unexpected value: {max_calls}[/]")
        return False

def show_all_tool_configs():
    """Display all tool-related configuration values"""
    console.print("\n[bold blue]All Tool Configuration Values[/]")
    console.print("=" * 50)
    
    tool_configs = [
        ("MAX_TOOL_CALLS", config.MAX_TOOL_CALLS),
        ("COMMAND_TIMEOUT", config.COMMAND_TIMEOUT),
        ("SHORT_COMMAND_TIMEOUT", config.SHORT_COMMAND_TIMEOUT),
        ("API_REQUEST_TIMEOUT", config.API_REQUEST_TIMEOUT),
        ("MCP_CLIENT_TIMEOUT", config.MCP_CLIENT_TIMEOUT)
    ]
    
    for name, value in tool_configs:
        console.print(f"[blue]{name:<25}: {value}[/]")
    
    console.print(f"\n[green]✓ Configuration loaded from config.py[/]")

def main():
    """Test the configuration change"""
    console.print("[bold magenta]MAX_TOOL_CALLS Configuration Test[/]")
    console.print("=" * 60)
    
    success = test_max_tool_calls_config()
    show_all_tool_configs()
    
    if success:
        console.print("\n[bold green]🎉 Configuration successfully updated![/]")
        console.print("[green]Models will now be allowed 50 tool calls before asking for confirmation[/]")
        console.print("[blue]This enables more complex multi-step operations[/]")
    else:
        console.print("\n[bold red]❌ Configuration issue detected[/]")
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
