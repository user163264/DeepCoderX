# DeepCoderX Architecture

This document provides a detailed overview of the internal architecture of the DeepCoderX application.

## High-Level Overview

DeepCoderX is built on a modular, handler-based architecture. The core of the application is a `CommandProcessor` that routes user input to a series of specialized handlers. This design allows for a clean separation of concerns and makes the application easy to extend.

## The Command Processing Pipeline

1.  **Input:** The user enters a command at the CLI.
2.  **Middleware:** The command first passes through any registered middleware. The `SecurityMiddleware` is a key example, which checks for dangerous patterns and prevents unsafe operations.
3.  **Handler Routing:** The `CommandProcessor` then iterates through its list of registered handlers, calling the `can_handle()` method on each one.
4.  **Execution:** The first handler that returns `True` from `can_handle()` gets to execute the command. The handlers are registered in a specific order to ensure that the most specific handlers are checked first.

## Key Architectural Components

### 1. The MCP Security Sandbox

*   **Files:** `services/mcpserver.py`, `services/mcpclient.py`
*   **Purpose:** To provide a secure, sandboxed environment for all file system and shell operations.
*   **How it Works:** The `mcpserver` runs in a background thread and listens for requests from the `mcpclient`. All file paths are validated to ensure they are within the designated sandbox directory. This prevents any command from accessing or modifying files outside of the project root.

### 2. The NLU Parser

*   **File:** `services/nlu_parser.py`
*   **Purpose:** To convert natural language commands into structured, machine-readable JSON commands.
*   **How it Works:** When the `FilesystemCommandHandler` is triggered (by the "use your tools" prefix), it passes the user's command to the `NLUParser`. The parser uses a specially prompted LLM to identify the user's *intent* (e.g., `read_file`) and extract the required *entities* (e.g., `{"path": "app.py"}`). This allows for a much more flexible and user-friendly command interface.

### 3. Tool-Using AI Agents

*   **Files:** `services/llm_handler.py` (`LocalCodingHandler`, `DeepSeekAnalysisHandler`)
*   **Purpose:** To provide the AI models with the ability to use tools to interact with the file system.
*   **How it Works:** Both the local and DeepSeek handlers are implemented as tool-using agents. They can engage in a multi-step reasoning process:
    1.  The handler sends the user's request and the system prompt to the LLM.
    2.  The LLM can respond with either a final answer or a JSON object requesting a tool call (e.g., `{"tool": "read_file", "path": "app.py"}`).
    3.  If a tool is requested, the handler executes it using the secure `MCPClient`.
    4.  The result of the tool call is then sent back to the LLM.
    5.  This process repeats until the LLM has enough information to provide a final answer to the user.

### 4. The Context Manager

*   **File:** `services/context_manager.py`
*   **Purpose:** To create and manage a persistent context file for each project.
*   **How it Works:** The first time a deep analysis is run on a project, the `ContextManager` performs a one-time analysis and saves a summary of the codebase to a `.deepcoderx_context.md` file. In all subsequent sessions, this file is read and injected into the system prompt, giving the AI immediate, high-level context about the project.
