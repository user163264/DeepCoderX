# CONTEXT FILE FOR DEEPCODERX PROJECT (CLAUDE)


CREAD 'MEMORY_FOR_NEXT_CHAT.md'

## AI Instructions (Rules for the Assistant)

1.  **Read this document first** to understand the project's structure and goals.
2.  **Use your tools.** You have access to tools like `read_file`, `write_file`, and `list_dir`. Use them to gather information before answering questions.
3.  **Be professional and brief.** When you make changes to the code, explain what you changed and why.
4.  **Stay on topic.**
5.  **Do not erase or replace text in log files.** Always append.


**Objective:** This document provides the complete context for the DeepCoderX application. It is intended to be used by an AI assistant to understand the project's architecture, goals, and current state.

---

## 1. Core Concept

DeepCoderX is a sophisticated, CLI-based AI coding assistant. It leverages a dual-AI strategy, using a local GGUF model for general-purpose tasks and a powerful cloud-based API (DeepSeek) for high-level analysis. Its core design is secure, routing all file system operations through a sandboxed MCP server.

---

## 2. Key Architectural Features

*   **Dual-AI Architecture:** The application supports two distinct AI models:
    *   A locally-run GGUF model for general-purpose coding assistance and chat.
    *   A cloud-based API (DeepSeek) for high-level, complex codebase analysis.
*   **Tool-Use Conversation Loop:** Both the local and cloud-based AI handlers support a multi-turn conversation loop that allows the models to use tools to gather information and perform actions.
*   **Secure File System Operations:** All file system operations are handled by a sandboxed MCP (Managed Code Protocol) server.
*   **Modular Command Routing:** A `CommandProcessor` routes user input to the appropriate handler (`LocalCodingHandler`, `DeepSeekAnalysisHandler`, etc.).

---

## 3. Project Structure

```
/Users/admin/Documents/DeepCoderX
├── .gitignore
├── .github/
├── .vscode/
├── VENV/
├── app.py
├── config.py
├── run.py
├── run_tests.py
├── requirements.txt
├── pyproject.toml
├── pytest.ini
├── documentation/
│   ├── codebase_analysis_report.md
│   ├── context_loading_behavior.md
│   └── two_model_implementation_plan.md
├── models/
│   ├── router.py
│   └── session.py
├── services/
│   ├── llm_handler.py
│   ├── mcpclient.py
│   ├── mcpserver.py
│   └── context_builder.py
├── tests/
│   ├── test_auto_implement_handler.py
│   ├── test_command_router.py
│   ├── test_filesystem_handler.py
│   ├── test_integration.py
│   ├── test_llm_handlers.py
│   ├── test_mcp_services.py
│   └── test_tool_loop.py
└── utils/
    ├── code_utils.py
    ├── execution.py
    ├── logging.py
    └── security.py
```

---

## 4. Technical Details

*   **Local Model:** The local model is a GGUF file, loaded and run using the `llama-cpp-python` library.
*   **Cloud Model:** The DeepSeek API is accessed via standard HTTPS requests.
*   **Testing:** The project has a comprehensive test suite using `pytest` and `pytest-mock`.
*   **Dependencies:** All dependencies are listed in `requirements.txt`.

---

