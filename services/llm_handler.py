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

from llama_cpp import Llama

from config import config
from utils.logging import console, log_api_usage
from services.context_builder import CodeContextBuilder
from models.session import CommandContext
from models.router import CommandHandler
from services.nlu_parser import NLUParser

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
                    timeout=30, # 30-second timeout
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

from services.context_manager import ContextManager

class DeepSeekAnalysisHandler(CommandHandler):
    ANALYSIS_KEYWORDS = {
        r'\barchitecture\b', r'\breview\b', r'\brefactor\b', r'\bdependencies\b',
        r'\bcross-file\b', r'\bcodebase\b', r'\bpattern\b', r'\banalyze\b',
        r'\bexplain\b', r'\bimprove\b', r'\boptimize\b', r'\bdesign\b'
    }

    def __init__(self, context: CommandContext):
        super().__init__(context)
        self.session_file = self.ctx.root_path / ".deepcoderx" / "deepseek_session.json"
        self._load_history()

    def _load_history(self):
        if self.session_file.exists():
            with open(self.session_file, "r") as f:
                self.message_history = json.load(f)
        else:
            self.message_history = []

    def _save_history(self):
        self.session_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.session_file, "w") as f:
            json.dump(self.message_history, f, indent=2)

    def can_handle(self) -> bool:
        if not config.DEEPSEEK_ENABLED:
            return False
        if self.ctx.user_input.lower().startswith("@deepseek"):
            return True
        
        query = self.ctx.user_input.lower()
        if "--build-context" in query:
            return True
            
        if any(re.search(pattern, query) for pattern in self.ANALYSIS_KEYWORDS):
            return True
            
        return False

    def handle(self) -> None:
        self.ctx.model_name = "DeepSeek (Cloud)"
        if "--build-context" in self.ctx.user_input:
            context_manager = ContextManager(self.ctx)
            context_manager.build_and_save_context()
            self.ctx.response = f"[green]Successfully built and saved project context to {context_manager.CONTEXT_FILE_NAME}[/]."
            return

        self.ctx.status = "Analyzing with DeepSeek..."
        if self.ctx.debug_mode:
            console.print("[bold red]DEBUG:[/] Starting DeepSeek analysis", style="dim")

        if not config.DEEPSEEK_API_KEY:
            self.ctx.response = "DeepSeek API key not configured"
            return

        context_manager = ContextManager(self.ctx)
        if context_manager.context_file_exists():
            initial_context = context_manager.read_context_file()
        else:
            initial_context = context_manager.build_and_save_context()

        system_prompt = config.DEEPSEEK_SYSTEM_PROMPT + f"\n\n**Project Context File:**\n{initial_context}\n\n**Current Configuration**:\n{config.CURRENT_CONFIG}"

        user_prompt = self.ctx.user_input.replace("@deepseek", "", 1).strip()

        if not self.message_history:
            self.message_history = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]
        else:
            self.message_history.append({"role": "user", "content": user_prompt})

        max_tool_calls = 50
        for i in range(max_tool_calls):
            # Check if we are about to exceed the limit and prompt the user
            if i == max_tool_calls - 1:
                # Do not prompt for input if running in a test environment
                if "PYTEST_CURRENT_TEST" in os.environ:
                    self.ctx.response = "[red]Operation canceled by test environment to prevent infinite loop.[/]"
                    return

                self.ctx.status_message = "Tool call limit reached. Asking for user confirmation."
                console.print("\n[bold yellow]Warning:[/] The AI has used its tools 49 times and may be in a loop.")
                if input("Do you want to allow it to continue for another 50 calls? (y/N) ").lower() != 'y':
                    self.ctx.response = "[red]Operation canceled by user.[/]"
                    return
                # If the user says yes, we can extend the loop. For now, we'll just let it run one more time.

            self.ctx.status_message = "Thinking with DeepSeek..."
            self.ctx.status = "Thinking with DeepSeek..."
            model_response_text = self._get_model_response(self.message_history)

            # Use findall to capture all tool calls in the response
            tool_call_matches = re.findall(r'\{.*?\}', model_response_text, re.DOTALL)
            
            if tool_call_matches:
                tool_results = []
                for tool_call_json in tool_call_matches:
                    try:
                        response_json = json.loads(tool_call_json)
                        if "tool" in response_json:
                            self.ctx.status = f"Using tool: {response_json['tool']}..."
                            tool_results.append(self._execute_tool(response_json))
                    except json.JSONDecodeError:
                        # Ignore invalid JSON, treat as text
                        tool_results.append(f"Invalid JSON in tool call: {tool_call_json}")
                
                # If any tools were executed, feed all results back to the model
                if tool_results:
                    if self.ctx.debug_mode:
                        console.print("\n[bold blue]-- Model Tool Call --[/]")
                        console.print(model_response_text)
                        console.print("\n[bold blue]-- Tool Results --[/]")
                        console.print("\n".join(tool_results))
                        console.print("\n[bold blue]---------------------[/]")

                    self.message_history.append({"role": "assistant", "content": model_response_text})
                    self.message_history.append({"role": "user", "content": f"Tool Results: \n" + "\n".join(tool_results)})
                    continue

            # If no valid tool call is found, this is the final answer
            self.ctx.response = model_response_text
            self.message_history.append({"role": "assistant", "content": self.ctx.response})
            break
        else:
            self.ctx.response = "[red]Error:[/] Exceeded maximum tool calls (10)."

        # Maintain a reasonable history size
        if len(self.message_history) > 10:
            self.message_history = [self.message_history[0]] + self.message_history[-8:]

    def _get_model_response(self, message_history: List[Dict[str, str]]) -> str:
        try:
            headers = {"Authorization": f"Bearer {config.DEEPSEEK_API_KEY}"}
            payload = {
                "model": "deepseek-coder",
                "messages": message_history,
                "temperature": 0.1,
            }
            response = requests.post(
                config.DEEPSEEK_API_URL, 
                headers=headers, 
                json=payload, 
                timeout=90
            )
            response.raise_for_status()
            log_api_usage("deepseek", response.json().get("usage", {}).get("total_tokens", 0))
            return response.json()["choices"][0]["message"]["content"]
        except Exception as e:
            return f"[red]API Error:[/] {str(e)}"

    def _execute_tool(self, tool_call: Dict[str, Any]) -> str:
        tool_name = tool_call.get("tool")

        if tool_name == "delete_path":
            return "[red]Error:[/] The 'delete_path' tool is disabled."

        if tool_name == "run_bash":
            command = tool_call.get("command")
            if not command:
                return "[red]Error:[/] Command is required for run_bash."
            try:
                process = subprocess.run(
                    command, shell=True, capture_output=True, text=True, timeout=120, cwd=self.ctx.current_dir
                )
                return f"STDOUT:\n{process.stdout}\nSTDERR:\n{process.stderr}"
            except Exception as e:
                return f"[red]Error:[/] Failed to execute command: {e}"
        
        path = tool_call.get("path")
        if not path:
            return "[red]Error:[/] Path is required for file operations."

        if tool_name == "read_file":
            return self.ctx.mcp_client.read_file(path).get("content", "File not found.")
        elif tool_name == "list_dir":
            response = self.ctx.mcp_client.list_dir(path)
            if "result" in response:
                items = response["result"]
                files = items.get("files", [])
                dirs = items.get("directories", [])
                return f"Directory listing for '{path}':\nFiles: {files}\nDirectories: {dirs}"
            else:
                return f"[red]Error:[/] {response.get('error', 'Failed to list directory.')}"
        elif tool_name == "write_file":
            content = tool_call.get("content", "")
            return self.ctx.mcp_client.write_file(path, content).get("status", "Failed")
        else:
            return f"[red]Error:[/] Unknown tool: {tool_name}"

    def clear_history(self):
        """Resets the conversation history and deletes the session file."""
        self.message_history = []
        if self.session_file.exists():
            self.session_file.unlink()
        if self.ctx.debug_mode:
            console.print("[bold red]DEBUG:[/] DeepSeek conversation history cleared.", style="dim")



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

class LocalCodingHandler(CommandHandler):
    def __init__(self, context: CommandContext):
        super().__init__(context)
        self.session_file = self.ctx.root_path / ".deepcoderx" / "local_session.json"
        self._load_history()

        # Initialize the model, suppressing the noisy startup logs
        with open(os.devnull, 'w') as f, contextlib.redirect_stdout(f), contextlib.redirect_stderr(f):
            self.llm = Llama(model_path=config.LOCAL_MODEL_PATH, n_ctx=8192, verbose=False)

    def _load_history(self):
        if self.session_file.exists():
            with open(self.session_file, "r") as f:
                self.message_history = json.load(f)
        else:
            # Start with a clean system prompt without pre-loading the entire project context.
            # This creates the 'new buffer' you requested and prevents exceeding the token limit on startup.
            system_prompt = config.LOCAL_SYSTEM_PROMPT + f"\n\n**Current Configuration**:\n{config.CURRENT_CONFIG}"
            self.message_history = [
                {"role": "system", "content": system_prompt},
            ]

    def _save_history(self):
        self.session_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.session_file, "w") as f:
            json.dump(self.message_history, f, indent=2)


    def can_handle(self) -> bool:
        return True

    def handle(self) -> None:
        self.ctx.model_name = "Qwen (Local)"
        # --- Input Parsing ---
        words = self.ctx.user_input.split()
        file_paths, message_words = [], []
        for word in words:
            if word.startswith('@') and word.lower() not in ['@qwen', '@deepseek']:
                file_paths.append(word[1:])
            elif word.lower() not in ['@qwen', '@deepseek']:
                message_words.append(word)
        
        cleaned_input = " ".join(message_words)
        file_contents = []
        for path in file_paths:
            try:
                response = self.ctx.mcp_client.read_file(path)
                if "content" in response:
                    file_contents.append(f"""--- Content from @{path} ---
{response['content']}
--- End of content ---""")
                else:
                    file_contents.append(f"--- Error reading @{path}: {response.get('error')} ---")
            except Exception as e:
                file_contents.append(f"--- Exception reading @{path}: {e} ---")

        user_prompt = cleaned_input
        if file_contents:
            user_prompt += "\n\n" + "\n\n".join(file_contents)

        self.message_history.append({"role": "user", "content": user_prompt})

        # --- Tool-Use Loop ---
        max_tool_calls = 50
        for i in range(max_tool_calls):
            # Check if we are about to exceed the limit and prompt the user
            if i == max_tool_calls - 1:
                # Do not prompt for input if running in a test environment
                if "PYTEST_CURRENT_TEST" in os.environ:
                    self.ctx.response = "[red]Operation canceled by test environment to prevent infinite loop.[/]"
                    return

                self.ctx.status_message = "Tool call limit reached. Asking for user confirmation."
                console.print("\n[bold yellow]Warning:[/] The AI has used its tools 49 times and may be in a loop.")
                if input("Do you want to allow it to continue for another 50 calls? (y/N) ").lower() != 'y':
                    self.ctx.response = "[red]Operation canceled by user.[/]"
                    return

            self.ctx.status_message = "Thinking..."
            model_response_text = self._generate_response()

            # Use findall to capture all tool calls in the response
            tool_call_matches = re.findall(r'\{.*?\}', model_response_text, re.DOTALL)
            
            if tool_call_matches:
                tool_results = []
                for tool_call_json in tool_call_matches:
                    try:
                        response_json = json.loads(tool_call_json)
                        if "tool" in response_json:
                            self.ctx.status = f"Using tool: {response_json['tool']}..."
                            tool_results.append(self._execute_tool(response_json))
                    except json.JSONDecodeError:
                        # Ignore invalid JSON, treat as text
                        tool_results.append(f"Invalid JSON in tool call: {tool_call_json}")
                
                # If any tools were executed, feed all results back to the model
                if tool_results:
                    self.message_history.append({"role": "assistant", "content": model_response_text})
                    self.message_history.append({"role": "user", "content": f"Tool Results: \n" + "\n".join(tool_results)})
                    continue

            # If no valid tool call is found, this is the final answer
            self.ctx.response = model_response_text
            self.message_history.append({"role": "assistant", "content": self.ctx.response})
            break
        else:
            self.ctx.response = "[red]Error:[/] Exceeded maximum tool calls (5)."

        # Maintain a reasonable history size
        if len(self.message_history) > 10:
            self.message_history = [self.message_history[0]] + self.message_history[-8:]

    def _generate_response(self) -> str:
        try:
            output = self.llm.create_chat_completion(messages=self.message_history)
            return output['choices'][0]['message']['content']
        except Exception as e:
            return f"[red]Model Generation Error:[/] {str(e)}"

    def _execute_tool(self, tool_call: Dict[str, Any]) -> str:
        tool_name = tool_call.get("tool")
        path = tool_call.get("path")
        content = tool_call.get("content")

        if not path and tool_name != "run_bash":
            return "[red]Error:[/] Path is required for file operations."

        if tool_name == "read_file":
            response = self.ctx.mcp_client.read_file(path)
            return response.get("content", f"[red]Error:[/] {response.get('error', 'Could not read file.')}")
        elif tool_name == "write_file":
            response = self.ctx.mcp_client.write_file(path, content or "")
            return response.get("status", f"[red]Error:[/] {response.get('error', 'Could not write to file.')}")
        elif tool_name == "list_dir":
            response = self.ctx.mcp_client.list_dir(path)
            if "result" in response:
                return json.dumps(response["result"])
            else:
                return f"[red]Error:[/] {response.get('error', 'Failed to list directory.')}"
        else:
            return f"[red]Error:[/] Unknown tool: {tool_name}"

    def clear_history(self):
        """Resets the conversation history and deletes the session file."""
        # The system prompt is always the first message.
        if self.message_history:
            system_prompt = self.message_history[0]
            self.message_history = [system_prompt]
        if self.session_file.exists():
            self.session_file.unlink()
        if self.ctx.debug_mode:
            console.print("[bold red]DEBUG:[/] Conversation history cleared.", style="dim")

