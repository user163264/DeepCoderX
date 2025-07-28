#!/usr/bin/env python3
"""
Test cloud provider conversation management
Diagnoses session handling issues
"""

import sys
import os
from pathlib import Path
import json

# Add the project directory to the path
project_dir = Path(__file__).parent
sys.path.insert(0, str(project_dir))

from config_module import config
from models.session import CommandContext
from services.unified_openai_handler import CloudOpenAIHandler
from services.mcpclient import MCPClient
from utils.logging import console

def test_conversation_management():
    """Test conversation flow for cloud providers."""
    
    # Create MCP client
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
    
    # Test DeepSeek conversation management
    console.print(f"[bold blue]Testing DeepSeek Conversation Management[/]")
    console.print("=" * 60)
    
    try:
        # Create handler
        handler = CloudOpenAIHandler(ctx, "deepseek")
        
        # Check initial session state
        console.print(f"[cyan]Initial message history length: {len(handler.message_history)}[/]")
        
        # Print current session file content
        session_file = Path(ctx.root_path) / ".deepcoderx" / "deepseek_session.json"
        console.print(f"[cyan]Session file: {session_file}[/]")
        
        if session_file.exists():
            with open(session_file, 'r') as f:
                session_data = json.load(f)
            console.print(f"[cyan]Session file length: {len(session_data)} messages[/]")
            
            # Show message roles
            roles = [msg.get('role', 'unknown') for msg in session_data]
            console.print(f"[cyan]Message roles: {' → '.join(roles)}[/]")
            
            # Check for conversation flow issues
            user_count = roles.count('user')
            assistant_count = roles.count('assistant')
            console.print(f"[yellow]User messages: {user_count}, Assistant messages: {assistant_count}[/]")
            
            if user_count > assistant_count + 1:  # Allow for one pending user message
                console.print(f"[bold red]❌ CONVERSATION FLOW ISSUE: Too many user messages without responses[/]")
                console.print(f"[red]Expected: user_count <= assistant_count + 1[/]")
                console.print(f"[red]Actual: {user_count} > {assistant_count} + 1[/]")
            else:
                console.print(f"[green]✅ Conversation flow appears normal[/]")
            
        else:
            console.print(f"[yellow]No session file found - clean start[/]")
        
        # Test a simple interaction
        console.print(f"\n[bold blue]Testing Simple Interaction[/]")
        ctx.user_input = "@deepseek test message"
        
        # Check if handler can handle this
        can_handle = handler.can_handle()
        console.print(f"[cyan]can_handle(): {can_handle}[/]")
        
        console.print(f"\n[bold green]✅ Test completed successfully[/]")
        
    except Exception as e:
        console.print(f"[bold red]❌ Test failed: {e}[/]")
        import traceback
        console.print(f"[red]Traceback:[/]")
        console.print(traceback.format_exc())

def fix_conversation_flow():
    """Fix conversation flow issues by cleaning session."""
    console.print(f"\n[bold magenta]Applying Conversation Flow Fix[/]")
    console.print("=" * 60)
    
    # Clean DeepSeek session
    session_file = Path(".deepcoderx/deepseek_session.json")
    if session_file.exists():
        # Backup existing
        backup_file = session_file.with_suffix(".json.backup_conversation_fix")
        session_file.rename(backup_file)
        console.print(f"[yellow]Backed up session to: {backup_file}[/]")
    
    # Create clean session
    clean_session = [
        {
            "role": "system",
            "content": config.DEEPSEEK_SYSTEM_PROMPT + "\n\n**Important: Only respond to the most recent user message. Do not respond to multiple requests at once.**"
        }
    ]
    
    session_file.parent.mkdir(parents=True, exist_ok=True)
    with open(session_file, 'w') as f:
        json.dump(clean_session, f, indent=2)
    
    console.print(f"[green]✅ Created clean session file[/]")
    console.print(f"[green]✅ Added clarification to system prompt[/]")

if __name__ == "__main__":
    console.print("[bold magenta]🔧 CLOUD PROVIDER CONVERSATION MANAGEMENT TEST[/]")
    test_conversation_management()
    fix_conversation_flow()
    console.print(f"\n[bold green]🎉 Conversation management analysis completed![/]")
