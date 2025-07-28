"""
Direct Command Configuration for DeepCoderX

This module defines all direct commands that bypass AI processing entirely.
These commands execute in <100ms with zero AI inference for maximum performance.

SINGLE SOURCE OF TRUTH: All direct command definitions are centralized here.
Any changes to direct commands should be made in this file only.
"""

from typing import Dict, List, Optional

# Core direct commands that execute instantly without AI processing
DIRECT_COMMANDS: Dict[str, str] = {
    # File system commands
    "pwd": "run_bash({\"command\": \"pwd\"})",
    "ls": "run_bash({\"command\": \"ls\"})",
    "ls -l": "run_bash({\"command\": \"ls -l\"})",
    "ls -la": "run_bash({\"command\": \"ls -la\"})",
    
    # Git commands  
    "git status": "run_bash({\"command\": \"git status\"})",
    "git log": "run_bash({\"command\": \"git log --oneline -10\"})",
    
    # System commands
    "whoami": "run_bash({\"command\": \"whoami\"})",
    "date": "run_bash({\"command\": \"date\"})",
}

# Additional command aliases (consolidated from YAML)
COMMAND_ALIASES: Dict[str, str] = {
    "status": "git status",        # 'status' -> 'git status'
    "log": "git log",            # 'log' -> 'git log'
    "current directory": "pwd",    # 'current directory' -> 'pwd'
    "list files": "ls",           # 'list files' -> 'ls'
    # Add more aliases here as needed
}

# Command categories for organization
COMMAND_CATEGORIES = {
    "filesystem": ["pwd", "ls", "ls -l", "ls -la"],
    "git": ["git status", "git log"],
    "system": ["whoami", "date"],
}


def get_direct_commands() -> Dict[str, str]:
    """
    Get all direct commands.
    
    Returns:
        Dictionary mapping command strings to tool call strings
    """
    return DIRECT_COMMANDS.copy()


def get_direct_command_names() -> List[str]:
    """
    Get list of all direct command names.
    
    Returns:
        List of command names that can be executed directly
    """
    return list(DIRECT_COMMANDS.keys())


def is_direct_command(user_input: str) -> bool:
    """
    Check if user input is a direct command.
    
    Args:
        user_input: Raw user input to check
        
    Returns:
        True if this is a direct command, False otherwise
    """
    return user_input.lower().strip() in DIRECT_COMMANDS


def get_direct_command_tool_call(user_input: str) -> Optional[str]:
    """
    Get the tool call string for a direct command.
    
    Args:
        user_input: User input command
        
    Returns:
        Tool call string if it's a direct command, None otherwise
    """
    clean_input = user_input.lower().strip()
    if clean_input in DIRECT_COMMANDS:
        return DIRECT_COMMANDS[clean_input]
    
    # Check aliases
    if clean_input in COMMAND_ALIASES:
        aliased_command = COMMAND_ALIASES[clean_input]
        return DIRECT_COMMANDS.get(aliased_command)
    
    return None


def add_direct_command(command: str, tool_call: str) -> None:
    """
    Add a new direct command (for runtime extensibility).
    
    Args:
        command: Command string (e.g., "pwd")
        tool_call: Tool call string (e.g., "run_bash({\"command\": \"pwd\"})")
    """
    DIRECT_COMMANDS[command.lower().strip()] = tool_call


def remove_direct_command(command: str) -> bool:
    """
    Remove a direct command.
    
    Args:
        command: Command string to remove
        
    Returns:
        True if command was removed, False if it didn't exist
    """
    clean_command = command.lower().strip()
    if clean_command in DIRECT_COMMANDS:
        del DIRECT_COMMANDS[clean_command]
        return True
    return False


def get_command_info() -> Dict[str, any]:
    """
    Get information about direct commands.
    
    Returns:
        Dictionary with command statistics and categories
    """
    return {
        "total_commands": len(DIRECT_COMMANDS),
        "command_names": get_direct_command_names(),
        "categories": COMMAND_CATEGORIES,
        "aliases": COMMAND_ALIASES,
        "performance": "Sub-100ms execution, zero AI processing"
    }


# Export the main functions for easy importing
__all__ = [
    "DIRECT_COMMANDS",
    "get_direct_commands",
    "get_direct_command_names", 
    "is_direct_command",
    "get_direct_command_tool_call",
    "add_direct_command",
    "remove_direct_command",
    "get_command_info"
]
