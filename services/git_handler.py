"""
Git operations handler for DeepCoderX

Implements basic Git commands through the MCP security system
"""
import os
import re
from typing import Dict, Any
import shlex
from models.session import CommandContext
from models.router import CommandHandler

class GitHandler(CommandHandler):
    """Handles Git version control operations"""
    
    def __init__(self, context: CommandContext):
        super().__init__(context)
        
    def can_handle(self) -> bool:
        """Check if input is a Git command"""
        return self.ctx.user_input.strip().lower().startswith('git ')
    
    def handle(self) -> None:
        try:
            # Use shlex to correctly split the command string
            parts = shlex.split(self.ctx.user_input)
            if not parts or parts[0] != 'git':
                self.ctx.set_error("Invalid git command")
                return

            # The first part is 'git', the rest are the command and args
            command_and_args = parts[1:]
            self.ctx.mcp_client.execute(['git'] + command_and_args)
            self.ctx.response = "Git command executed successfully."

        except Exception as e:
            self.ctx.set_error(f"Failed to execute git command: {e}")
    
    def _execute_git(self, args: list[str]) -> None:
        """Execute Git command through MCP"""
        result = self.ctx.mcp_client.execute(['git'] + args)
        if 'error' in result:
            self.ctx.response = "Git error: " + result['error']
        else:
            self.ctx.response = result.get('output', 'Git command executed successfully')
            
    def _validate_git_url(self, url: str) -> bool:
        """Validate Git URL format"""
        # Basic validation for common Git URL patterns
        patterns = [
            r'^https://.+\.',
            r'^git@.+\.:.+',
            r'^ssh://.+\.'
        ]
        return any(re.match(pattern, url) for pattern in patterns)