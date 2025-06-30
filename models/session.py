# models/session.py

from pathlib import Path
from typing import Dict, Any
from utils.security import SecurityError  # Use absolute import

class CommandContext:
    def __init__(self, root_path, mcp_client, sandbox_path, debug_mode=False):
        self.root_path = root_path
        self.current_dir = root_path # Start at the project root
        self.mcp_client = mcp_client
        self.sandbox_path = sandbox_path
        self.status_message: str = "Idle"
        self.model_name: str = "Assistant"
        self.user_input: str = ""
        self.agent: str = "local"
        self.response: str = ""
        self.metadata: Dict[str, Any] = {}
        self.abort: bool = False
        self.abort_reason: str = ""
        self.dry_run = False
        self.auto_confirm = False
        self.debug_mode = debug_mode
        self.status = "Processing..."
        
    def set_error(self, reason: str):
        self.abort = True
        self.abort_reason = reason
        if self.debug_mode:
            from utils.logging import console
            console.print(f"[bold red]DEBUG:[/] ERROR: {reason}", style="dim")
        
    def get_relative_path(self, path_str: str) -> Path:
        try:
            path = (self.current_dir / path_str).resolve()
            if not path.is_relative_to(self.root_path):
                raise SecurityError(f"Blocked path traversal: {path}")  # Use SecurityError
            return path
        except Exception as e:
            if self.debug_mode:
                from utils.logging import console
                console.print(f"[bold red]DEBUG:[/] Path error: {str(e)}", style="dim")
            raise