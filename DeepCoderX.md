## DeepCoderX - Intelligent Code Assistant with Secure Execution Environment


# project structure:

DeepCoderX/
├── __init__.py
├── __main__.py             # Entry point
├── app.py                  # Main application logic
├── config.py               # Configuration settings
├── run.py                  # Alternative entry point
├── DeepCoderX.md           # Project documentation
│
├── models/                 # Core system components
│   ├── __init__.py
│   ├── router.py           # Command routing/handling
│   └── session.py          # Session context management
│
├── services/               # Functional components
│   ├── __init__.py
│   ├── context_builder.py  # Project context analysis
│   ├── execution.py        # Secure command execution
│   ├── llm_handler.py      # AI integration handlers
│   ├── mcpclient.py        # MCP client implementation
│   └── mcpserver.py        # MCP server implementation
│
└── utils/                  # Helper utilities
    ├── __init__.py
    ├── code_utils.py       # Code highlighting/clipboard
    ├── logging.py          # Rich console logging
    └── security.py         # Security exceptions



--------------------------------------------------------------------------------------
LOCAL INFO: 
--------------------------------------------------------------------------------------

Running on Mac M2 - 8GB Ram
Sandbox = /Users/admin/Documents
Project root = /Users/admin/Documents/DeepCoderX
path to local model Qwen: /Users/admin/.cache/lm-studio/models/Qwen/Qwen2.5-Coder-1.5B-Instruct-GGUF
DeepCoderX cpp engine: LMStudio: http://localhost:1234/v1
DeepSeek API KEY: sk-0698112e6a2e4a338820e13f4233e78f

Alt api:

DeepCoderX:
sk-6ec1a827d2c840ac96dae45a83f96609

--------------------------------------------------------------------------------------
Project Info:
--------------------------------------------------------------------------------------

Project Description:

DeepCoderX is an intelligent CLI-based coding assistant that combines:

AI-powered code generation/analysis using both local (LM Studio) and cloud-based (DeepSeek API) LLMs

Secure execution environment with sandboxing capabilities

Project-aware context building for cross-file analysis

Managed Code Protocol (MCP) for safe file operations

Security-focused design with path traversal protection and extension whitelisting

Core features:

AI Command Processing: Handles natural language commands for code generation, analysis, and modification

DeepSeek Integration: For advanced code analysis, architecture review, and optimization suggestions

Sandboxed Execution: Secure file operations via MCP server/client architecture

Context Awareness: Automatic project context building with dependency analysis

Safety Protocols: Security middleware blocks dangerous patterns and unsafe file types

--------------------------------------------------------------------------------------



## Core Concept:

DeepCoderX is an advanced CLI-based coding assistant that combines AI-powered code generation with secure execution capabilities. It integrates local and cloud-based AI models (DeepSeek API and Ollama) with a robust filesystem sandbox (MCP Server) for safe code execution and project manipulation.


Key Components Breakdown
Command Processing (models/router.py)

CommandProcessor: Routes user input to appropriate handlers

CommandHandler: Base class for command handlers

Middleware support for security checks

Security System (services/llm_handler.py)

Security middleware with pattern matching:

python
UNSAFE_PATTERNS = [
    r"rm\s+-rf", r"chmod\s+777", 
    r"dd\s+if=", r"mv\s+/", ...
]
File extension whitelisting (.py, .js, .md, etc.)

Path traversal protection

AI Integration (services/llm_handler.py)

DeepSeek analysis for architecture reviews

Auto-implementation of AI suggestions

Local model integration via LM Studio

Context-aware responses with markdown code blocks

Managed Code Protocol (services/mcp*.py)

Client/Server architecture for secure file operations

Endpoints:

python
["/read", "/write", "/delete", "/list"]
Sandboxed environment with strict path validation

Project Context (services/context_builder.py)

Automatic file discovery with priority:

python
file_priority = {'.py': 10, '.ts': 9, '.js': 8, ...}
Import graph generation

Code snippet extraction

Execution Environment (services/execution.py)

Safe command execution with user confirmation

File operation handling via MCP

Script generation with automatic backup

Configuration Highlights (config.py)
Dual AI model support (DeepSeek + local)

Security constraints:

python
MAX_FILE_SIZE = 1024 * 1024 * 5  # 5MB
ALLOWED_EXTENSIONS = ['.py', '.js', '.ts', ...]
Sandbox directory with strict permissions

API endpoints and authentication keys

How It Works
User enters natural language command

Security middleware validates input

Command router selects appropriate handler

Context builder gathers project information

AI processes request (local or cloud-based)

MCP executes file operations in sandbox

Results formatted and returned to user

The system combines AI intelligence with enterprise-grade security, making it suitable for both local development and secure remote coding assistance.
