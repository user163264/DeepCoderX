

import json
import re
from pathlib import Path
from typing import Dict, Any

from models.session import CommandContext
from utils.logging import console

class ContextManager:
    """
    Manages the creation, reading, and updating of the project context file.
    """
    CONTEXT_FILE_NAME = ".deepcoderx_context.md"

    def __init__(self, context: CommandContext):
        self.ctx = context
        self.context_file_path = self.ctx.root_path / self.CONTEXT_FILE_NAME

    def context_file_exists(self) -> bool:
        """Checks if the context file exists in the project root."""
        return self.context_file_path.exists()

    def read_context_file(self) -> str:
        """Reads the content of the context file."""
        if self.context_file_exists():
            return self.context_file_path.read_text()
        return ""

    def build_and_save_context(self) -> str:
        """
        Performs a deep analysis of the codebase and saves the findings to the context file.
        Returns the content of the newly created context file.
        """
        self.ctx.status = "Building project context for the first time..."
        console.print("[yellow]Performing one-time deep analysis to build project context...[/]")

        file_tree = self._get_file_tree()
        project_description = self._get_project_description()

        context_content = f"""CONTEXT FILE FOR PROJECT.
-----------------------------

## START RULES ##
- 1: read THIS document to understandand the project (location of files, project tree, ...)
- 2: start your entry with[DATE] [NAME-OF-MODEL] [TIME]
- 3: only write what you did to the code. Then - what did you change? why? explain. Stay professional and brief.
- 4: Stay on topic.
- 5: DO NOT ERASE or REPLACE TEXT. Just add. So it becomes a real log file.
- 6: ADD YOUR ENTRY IN THE MEMORY FILE WITHOUT COMPLETELY REWRITING IT.
- 7:keep the file clean.
- 8: NEVER USE MOCK DATA OR MOCK REPLIES

# EXAMPLES: #

EXAMPLE: GOOD

**June 19, 2025 - 14:45**: COMPREHENSIVE CODEBASE ANALYSIS AND IMPLEMENTATION PLAN CREATED - Current state assessment and Phase 2 completion roadmap established
- **Analysis completed**: Thorough review of Genesis project current state via memory file, PROJECT_STATE.json, and filesystem examination
- **Current project status verified**:
  - **Genesis server**: OPERATIONAL on port 11436 with complete conversation system, real AI models (llama3.2:3b, qwen2.5-coder:1.5b), optimized streaming, MCP protocol integration
  - **Genesis CLI**: Advanced orchestration engine complete (2325+ lines), terminal UI operational, but missing versioning service implementation
  - **Phase 2 gap identified**: CLI conversation management commands exist (commit/checkout/log/branch/status) but corresponding server-side versioning service incomplete
- **Critical findings**:
  - Database schema and models for versioning already created (`/genesis-server/ollama/genesis/conversations/versioning/schema.go`, `models.go`)
  - CLI commands implemented and ready (`/genesis-cli/cmd/conversation/`) targeting versioning endpoints



EXAMPLE: BAD



## END RULES ##



## TECHNICAL PROJECT INFO ##


# project structure #

{file_tree}


- PROJECT DEV DIR: {self.ctx.root_path}
- LMStudio is running on port 1234
- [TECH INFORMATION]

## END TECHNICAL PROJECT INFO ##

-----------------------------

YOUR GOAL: Help the user achieve the goals for the project. Write the best code you can.

-----------------------------


## PROJECT DESCRIPTION ##

{project_description}

## END PROJECT DESCRIPTION ##
"""

        self.context_file_path.write_text(context_content)
        console.print(f"[green]Project context saved to {self.CONTEXT_FILE_NAME}[/]")
        return context_content

    def _get_file_tree(self) -> str:
        """Generates a string representation of the file tree."""
        tree = []
        for path in sorted(self.ctx.root_path.rglob('*')):
            depth = len(path.relative_to(self.ctx.root_path).parts) - 1
            indent = "    " * depth
            tree.append(f"{indent}{path.name}")
        return "\n".join(tree)

    def _get_key_files_content(self) -> str:
        """Reads the content of key files like requirements.txt, etc."""
        content = ""
        key_files = ["requirements.txt", "config.py", "app.py", "run.py"]
        for file_name in key_files:
            file_path = self.ctx.root_path / file_name
            if file_path.exists():
                content += f"### {file_name}\n```\n{file_path.read_text()[:1000]}\n```\n\n"
        return content

    def _get_project_description(self) -> str:
        """Reads the project description from the DeepCoderX.md file."""
        description_file = self.ctx.root_path / "DeepCoderX.md"
        if description_file.exists():
            # A simple way to extract the core concept and features
            content = description_file.read_text()
            match = re.search(r"## Core Concept:(.*?)", content, re.DOTALL)
            if match:
                return match.group(1).strip()
        return "No project description found."

