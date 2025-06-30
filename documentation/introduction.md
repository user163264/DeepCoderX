# Introduction to DeepCoderX

DeepCoderX is an advanced, command-line-based AI coding assistant designed for developers who need a powerful, secure, and flexible tool to help them with their daily coding tasks.

## What is DeepCoderX?

At its core, DeepCoderX is a sophisticated CLI application that seamlessly integrates with both local and cloud-based Large Language Models (LLMs). It allows you to interact with your codebase using natural language, perform complex analysis, and execute file system operations in a secure, sandboxed environment.

## Core Concepts

The project is built on a foundation of several key concepts:

*   **Natural Language Understanding (NLU):** Instead of rigid, unforgiving commands, DeepCoderX uses an NLU parser to understand your intent. You can say `use your tools and create a file called 'test.py'` and the system will understand what you mean.

*   **Secure Sandboxed Execution:** All file system operations are handled by the Managed Code Protocol (MCP), a client-server architecture that ensures no command can access or modify files outside of the designated project directory. This provides a critical layer of security.

*   **Tool-Using AI Agents:** Both the local and the cloud-based AI models are not just chatbots; they are true tool-using agents. They can reason about a problem, formulate a plan, and then use the provided tools (like `read_file`, `list_dir`, and `run_bash`) to execute that plan step-by-step.

*   **Persistent Context:** DeepCoderX can create a `.deepcoderx_context.md` file that stores a high-level summary of your project. This allows the AI to have immediate context in future sessions, dramatically improving efficiency and accuracy.

## Key Features

*   **Dual AI Model Support:** Seamlessly switch between a powerful local model for speed and privacy, and the advanced DeepSeek API for complex analysis.
*   **Natural Language Command Interface:** Interact with your file system using conversational language.
*   **Secure MCP Sandbox:** All file and bash operations are sandboxed for your protection.
*   **Tool-Enabled AI:** Both AI models can use tools to read files, list directories, and execute shell commands.
*   **Automatic Project Context:** The system can automatically build and maintain a context file for your projects.
*   **CLI-Native Interface:** Built with `rich` for a modern, user-friendly command-line experience.
