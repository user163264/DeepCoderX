import sys
import os
import re
import json
import shutil
import subprocess
import traceback
import contextlib
import requests
from pathlib import Path
from typing import Dict, Any, List, Optional

from config_module import config
from utils.logging import console, log_api_usage
from services.context_builder import CodeContextBuilder
from models.session import CommandContext
from models.router import CommandHandler
from services.nlu_parser import NLUParser
from services.tool_executor import ToolExecutor

# Import new unified OpenAI handlers
from services.unified_openai_handler import LocalOpenAIHandler, CloudOpenAIHandler

class SecurityMiddleware(CommandHandler):
    UNSAFE_PATTERNS = [
        r"rm\s+-rf", r"chmod\s+777", r"dd\s+if=", 
        r"mv\s+/", r"cp\s+/", r"format\s+", r":(){:|:&};:",
        r"curl\s+-X\s+POST", r"wget\s+.*\s+-O"
    ]
    
    SAFE_EXTENSIONS = ['.py', '.js', '.ts', '.java', '.go', '.rs', 
                      '.txt', '.md', '.json', '.yml', '.yaml', '.html',
                      '.css', '.sh', '.bat']
    
    def can_handle(self) -> bool:
        return True
        
    def handle(self) -> None:
        if self.ctx.debug_mode:
            console.print(f"[bold red]DEBUG:[/] Security check: {self.ctx.user_input}", style="dim")
            
        # API key leakage prevention
        if re.search(r'sk-[a-zA-Z0-9]{24}', self.ctx.user_input):
            self.ctx.set_error("Blocked potential API key exposure")
            return
            
        for pattern in self.UNSAFE_PATTERNS:
            if re.search(pattern, self.ctx.user_input, re.IGNORECASE):
                self.ctx.set_error(f"Blocked dangerous pattern: {pattern}")
                return
                
        file_commands = ['edit', 'create', 'run', 'show', 'implement', 'apply']
        if any(cmd in self.ctx.user_input for cmd in file_commands):
            match = re.search(r'\b(?:' + '|'.join(file_commands) + r')\s+([\w\/\.\-]+)', self.ctx.user_input)
            if match:
                file_name = match.group(1)
                file_path = Path(file_name)
                if file_path.suffix and file_path.suffix.lower() not in self.SAFE_EXTENSIONS:
                    self.ctx.set_error(f"Unsupported file type: {file_path.suffix}")

class FilesystemCommandHandler(CommandHandler):
    def can_handle(self) -> bool:
        return self.ctx.user_input.lower().startswith("use your tools")

    def handle(self) -> None:
        self.ctx.status = "Parsing command..."
        command_text = self.ctx.user_input[len("use your tools "):].strip()
        
        parser = NLUParser(self.ctx)
        parsed_command = parser.parse_intent(command_text)
        
        intent = parsed_command.get("intent")
        entities = parsed_command.get("entities", {})
        
        if intent == "clarify":
            self.ctx.response = f"""[yellow]Clarification needed:[/] 
{entities.get('reason', 'Could not understand the command.')}"""
            return

        if not intent:
            self.ctx.response = f"""[red]Error:[/] 
Could not determine the intent of the command."""
            return

        # --- Dispatch to MCP Client based on intent ---
        self.ctx.status = f"Executing: {intent}..."
        response = None
        if intent == "change_directory":
            path = entities.get("path", ".")
            # Note: This operation is client-side and doesn't need the MCP server
            new_dir = (self.ctx.current_dir / path).resolve()
            # Security check: Ensure the new path is still within the sandbox root
            if self.ctx.root_path in new_dir.parents or self.ctx.root_path == new_dir:
                if new_dir.is_dir():
                    self.ctx.current_dir = new_dir
                    self.ctx.response = f"Current directory: {self.ctx.current_dir.relative_to(self.ctx.root_path)}"
                else:
                    self.ctx.response = f"[red]Error:[/] Not a directory: {path}"
            else:
                self.ctx.response = f"[red]Error:[/] Cannot 'cd' outside the project root."

        elif intent == "list_dir":
            path = entities.get("path", ".")
            response = self.ctx.mcp_client.list_dir(path)
            if "result" in response:
                items = response["result"]
                files = items.get("files", [])
                dirs = items.get("directories", [])
                self.ctx.response = "\n".join([f"[blue]{d}/[/blue]"
for d in sorted(dirs)] + [f"[green]{f}[/green]"
for f in sorted(files)])
            else:
                self.ctx.response = f"""[red]Error:[/] 
{response.get('error', 'Failed to list directory.')}"""

        elif intent == "read_file":
            path = entities.get("path")
            if not path:
                self.ctx.response = """[red]Error:[/] 
No file path specified for reading."""
                return
            response = self.ctx.mcp_client.read_file(path)
            self.ctx.response = response.get("content", f"""[red]Error:[/] 
{response.get('error', 'Could not read file.')}""")

        elif intent == "write_file":
            path = entities.get("path")
            content = entities.get("content", "")
            if not path:
                self.ctx.response = """[red]Error:[/] 
No file path specified for writing."""
                return
            response = self.ctx.mcp_client.write_file(path, content)
            if response.get("status") == "success":
                self.ctx.response = f"Successfully wrote to {path}"
            else:
                self.ctx.response = f"""[red]Error:[/] 
{response.get('error', 'Could not write to file.')}"""

        elif intent == "delete_path":
            path = entities.get("path")
            if not path:
                self.ctx.response = """[red]Error:[/] 
No path specified for deletion."""
                return
            response = self.ctx.mcp_client.delete_path(path, recursive=True)
            if response.get("status") == "success":
                self.ctx.response = f"Successfully deleted {path}"
            else:
                self.ctx.response = f"""[red]Error:[/] 
{response.get('error', 'Could not delete path.')}"""

        elif intent == "run_bash":
            command = entities.get("command")
            if not command:
                self.ctx.response = """[red]Error:[/] 
No command specified for execution."""
                return
            
            # Security: Disallow certain dangerous commands, even in the sandbox
            for pattern in SecurityMiddleware.UNSAFE_PATTERNS:
                if re.search(pattern, command, re.IGNORECASE):
                    self.ctx.response = f"[red]Error:[/] Blocked dangerous command pattern: {pattern}"
                    return

            try:
                # Execute the command within the current directory
                process = subprocess.run(
                    command, 
                    shell=True, 
                    capture_output=True, 
                    text=True, 
                    timeout=config.SHORT_COMMAND_TIMEOUT,
                    cwd=self.ctx.current_dir
                )
                stdout = process.stdout.strip()
                stderr = process.stderr.strip()
                if process.returncode == 0:
                    self.ctx.response = f"""[green]Command executed successfully:[/] 
{stdout}"""
                else:
                    self.ctx.response = f"""[red]Command failed with exit code {process.returncode}:[/] 
{stderr}"""
            except subprocess.TimeoutExpired:
                self.ctx.response = "[red]Error:[/] Command timed out after 30 seconds."
            except Exception as e:
                self.ctx.response = f"[red]Error:[/] Failed to execute command: {e}"

        else:
            self.ctx.response = f"""[yellow]Warning:[/] 
The command intent '{intent}' is not yet implemented."""

class AutoImplementHandler(CommandHandler):
    IMPLEMENT_KEYWORDS = {'implement', 'apply', 'execute', 'make changes'}
    
    def can_handle(self) -> bool:
        query = self.ctx.user_input.lower()
        return any(kw in query for kw in self.IMPLEMENT_KEYWORDS)
        
    def handle(self) -> None:
        if self.ctx.debug_mode:
            console.print("[bold red]DEBUG:[/] Starting implementation", style="dim")
        if 'deepseek_response' not in self.ctx.metadata:
            self.ctx.response = "No suggestions to implement"
            return
            
        # Safety confirmation prompt
        if not self.ctx.dry_run and not self.ctx.auto_confirm:
            console.print("[bold yellow]WARNING:[/] This will modify files. Continue? (y/N)", end=" ")
            if input().strip().lower() != 'y':
                self.ctx.response = "Implementation canceled"
                return
                
        changes = self._parse_response(self.ctx.metadata['deepseek_response'])
        self.ctx.response = "Implementation Report:\n"
        for file_path, content in changes.items():
            result = self._apply_change(file_path, content)
            self.ctx.response += f"- {result}\n"
        self.ctx.response += "\n✅ Operation completed"
        
    def _parse_response(self, response: str) -> Dict[Path, str]:
        changes = {}
        pattern = r'```(\w+)?:([^\n]+)\n(.*?)```'
        if self.ctx.debug_mode:
            console.print("[bold red]DEBUG:[/] Parsing DeepSeek response", style="dim")
        for match in re.finditer(pattern, response, re.DOTALL):
            _, rel_path, code = match.groups()
            try:
                abs_path = self.ctx.get_relative_path(rel_path.strip())
                changes[abs_path] = code.strip()
                if self.ctx.debug_mode:
                    console.print(f"[bold red]DEBUG:[/] Found: {abs_path}", style="dim")
            except Exception as e:
                self.ctx.response += f"\n⚠️ Skipped: {str(e)}"
                if self.ctx.debug_mode:
                    console.print(f"[bold red]DEBUG:[/] Parse error: {str(e)}", style="dim")
        return changes
    
    def _apply_change(self, path: Path, content: str) -> str:
        if self.ctx.dry_run:
            action = "Would create" if not path.exists() else "Would update"
            return f"DRY RUN: {action} {path.relative_to(self.ctx.root_path)}"

        target_path = str(path.relative_to(self.ctx.root_path))
        response = self.ctx.mcp_client.write_file(target_path, content)

        if "error" in response:
            return f"❌ Failed {path.name}: {response['error']}"

        return f"✅ Updated {target_path}"

# ================================================================================================
# LEGACY HANDLERS - DEPRECATED 
# ================================================================================================
# These handlers have been migrated to unified OpenAI handlers for better maintainability.
# They are preserved here only for backward compatibility and will be removed in a future version.
# NEW DEPLOYMENTS SHOULD USE:
# - CloudOpenAIHandler instead of DeepSeekAnalysisHandler 
# - LocalOpenAIHandler instead of LocalCodingHandler
# ================================================================================================

def _show_deprecation_warning(handler_name: str, replacement: str):
    """Show deprecation warning for legacy handlers."""
    console.print(f"[bold yellow]⚠️  DEPRECATION WARNING:[/] {handler_name} is deprecated")
    console.print(f"[yellow]    Please use {replacement} instead for better performance and reliability[/]")
    console.print(f"[yellow]    Legacy handlers will be removed in a future version[/]")

# Legacy DeepSeek handler - DEPRECATED
# Use CloudOpenAIHandler(ctx, "deepseek") instead
class DeepSeekAnalysisHandler(CommandHandler):
    """
    DEPRECATED: Use CloudOpenAIHandler(ctx, "deepseek") instead.
    
    This legacy handler is preserved for backward compatibility only.
    It will be removed in a future version.
    """
    
    def __init__(self, context: CommandContext):
        super().__init__(context)
        _show_deprecation_warning("DeepSeekAnalysisHandler", "CloudOpenAIHandler(ctx, 'deepseek')")
        
        # Redirect to unified handler
        try:
            self._unified_handler = CloudOpenAIHandler(context, "deepseek")
            self._use_unified = True
        except Exception as e:
            console.print(f"[red]Failed to initialize unified handler: {e}[/]")
            console.print("[yellow]Falling back to legacy implementation[/]")
            self._use_unified = False
            # Legacy initialization code would go here if needed
    
    def can_handle(self) -> bool:
        if self._use_unified:
            return self._unified_handler.can_handle()
        # Legacy can_handle logic would go here
        return False
    
    def handle(self) -> None:
        if self._use_unified:
            return self._unified_handler.handle()
        # Legacy handle logic would go here
        self.ctx.response = "[red]Error:[/] Legacy handler not fully implemented. Please use CloudOpenAIHandler."

# Legacy Local handler - DEPRECATED 
# Use LocalOpenAIHandler instead
class LocalCodingHandler(CommandHandler):
    """
    DEPRECATED: Use LocalOpenAIHandler instead.
    
    This legacy handler is preserved for backward compatibility only.
    It will be removed in a future version.
    """
    
    def __init__(self, context: CommandContext):
        super().__init__(context)
        _show_deprecation_warning("LocalCodingHandler", "LocalOpenAIHandler")
        
        # Redirect to unified handler
        try:
            self._unified_handler = LocalOpenAIHandler(context)
            self._use_unified = True
        except Exception as e:
            console.print(f"[red]Failed to initialize unified handler: {e}[/]")
            console.print("[yellow]Falling back to legacy implementation[/]")
            self._use_unified = False
            # Legacy initialization code would go here if needed
    
    def can_handle(self) -> bool:
        if self._use_unified:
            return self._unified_handler.can_handle()
        # Legacy can_handle logic would go here
        return False
    
    def handle(self) -> None:
        if self._use_unified:
            return self._unified_handler.handle()
        # Legacy handle logic would go here
        self.ctx.response = "[red]Error:[/] Legacy handler not fully implemented. Please use LocalOpenAIHandler."
