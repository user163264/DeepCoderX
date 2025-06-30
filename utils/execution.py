# execution.py

import sys
import os
import subprocess
from datetime import datetime
from rich.console import Console
from rich.text import Text
from .code_utils import highlight_bash
from config import SCRIPTS_DIR

console = Console()

def execute_file_operation(command, mcp_client):
    """Handle file operations using MCP server"""
    if not mcp_client:
        return "[red]❌ MCP client not available for file operations[/red]"
    
    try:
        # File read operation
        if command.startswith("cat "):
            path = command.split("cat ", 1)[1].strip()
            response = mcp_client.read_file(path)
            if 'result' in response:
                return f"📄 Contents of {path}:\n{response['result']}"
            else:
                return f"[red]❌ {response.get('error', 'Unknown error')}[/red]"
        
        # File write operation
        elif command.startswith("echo "):
            parts = command.split(">", 1)
            if len(parts) < 2:
                return "❌ Invalid write format. Use: echo 'content' > file.txt"
            
            content = parts[0].replace("echo", "", 1).strip()
            # Remove quotes if present
            if (content.startswith('"') and content.endswith('"')) or (content.startswith("'") and content.endswith("'")):
                content = content[1:-1]
            path = parts[1].strip()
            
            response = mcp_client.write_file(path, content)
            if 'result' in response:
                return f"✅ {response['result']}"
            else:
                return f"[red]❌ {response.get('error', 'Unknown error')}[/red]"
        
        # Directory creation
        elif command.startswith("mkdir "):
            dir_path = command.split("mkdir ", 1)[1].strip()
            # Create temp file to force directory creation
            temp_file = f"{dir_path}/.mcp_temp"
            write_res = mcp_client.write_file(temp_file, "")
            if 'error' in write_res:
                return f"[red]❌ Failed to create directory: {write_res['error']}[/red]"
            
            # Delete temp file
            del_res = mcp_client.delete_path(temp_file)
            if 'error' in del_res:
                return f"[yellow]⚠️ Directory created but temp file removal failed: {del_res['error']}[/yellow]"
            return f"📂 Created directory: {dir_path}"
        
        # File deletion
        elif command.startswith("rm "):
            path = command.split("rm ", 1)[1].strip()
            response = mcp_client.delete_path(path)
            if 'result' in response:
                return f"🗑️ {response['result']}"
            else:
                return f"[red]❌ {response.get('error', 'Unknown error')}[/red]"
        
        # Directory deletion
        elif command.startswith("rmdir "):
            path = command.split("rmdir ", 1)[1].strip()
            response = mcp_client.delete_path(path, recursive=True)
            if 'result' in response:
                return f"🗑️ {response['result']}"
            else:
                return f"[red]❌ {response.get('error', 'Unknown error')}[/red]"
        
        # List directory contents
        elif command.startswith("ls "):
            path = command.split("ls ", 1)[1].strip()
            response = mcp_client.list_dir(path)
            if 'result' in response:
                files = response['result'].get('files', [])
                dirs = [d + "/" for d in response['result'].get('directories', [])]
                return "📂 Directory listing:\n" + "\n".join(dirs + files)
            else:
                return f"[red]❌ {response.get('error', 'Unknown error')}[/red]"
        
        return f"❌ Unsupported operation: {command}"
    except Exception as e:
        return f"[red]❌ Operation failed: {e}[/red]"

# @deepseek: check the function below for errors.

        def execute_tool_command(command: str, mcp_client: MCPClient, ctx: CommandContext) -> str:
            """Handle 'use your tools:' syntax"""
            # Extract actual command after "tools:"
            cmd = command.split(":", 1)[1].strip() if ":" in command else command.replace("use your tools", "").strip()
            
            # Execute MCP command if recognized pattern
            if cmd.startswith(("read_file(", "write_file(", "list_dir(", "delete_path(")):
                return execute_mcp_function(cmd, mcp_client)
            
            # Execute as bash command
            return execute_bash_command(cmd, ctx)

# @deepseek: check the code below: the '# ... similar handlers for list_dir/delete_path ...' is that function complete?

        def execute_mcp_function(cmd, mcp_client):
            """Execute direct MCP function calls"""
            try:
                # Simple parsing of function calls
                if cmd.startswith("read_file("):
                    path = cmd.split("(")[1].split(")")[0].strip("'\"")
                    return mcp_client.read_file(path)
                
                elif cmd.startswith("write_file("):
                    parts = cmd.split("(", 1)[1].rsplit(")", 1)[0].split(",", 1)
                    path = parts[0].strip("'\"")
                    content = parts[1].strip(" '\"")
                    return mcp_client.write_file(path, content)
                
                # ... similar handlers for list_dir/delete_path ...
                
                return f"❌ Unsupported MCP function: {cmd}"
            except Exception as e:
                return f"❌ MCP execution error: {str(e)}"

