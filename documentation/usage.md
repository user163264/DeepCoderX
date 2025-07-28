# How to Use DeepCoderX

This guide provides examples of how to use the core features of DeepCoderX.

## Basic Commands

DeepCoderX understands several basic commands that are not handled by the AI models:

*   `exit` or `quit`: Exits the application.
*   `dry-run on`/`dry-run off`: Toggles dry-run mode.
*   `set deepseek-key <key>`: Sets your DeepSeek API key for the current session.

## Using the NLU for File Operations

To interact with the file system, you must start your command with `use your tools`. The NLU parser will then interpret your command.

**Examples:**

*   `use your tools list all the files in the current directory`
*   `use your tools create a new file called my_app.py`
*   `use your tools show me the contents of config.py`
*   `use your tools and delete the old_tests.py file`
*   `use your tools cd into the services directory`

## Code Analysis with @deepseek

To perform a deep analysis of your codebase, use the `@deepseek` command. This will trigger the DeepSeek AI agent, which can use tools to analyze your project.

**Examples:**

*   `@deepseek analyze the codebase`
*   `@deepseek review the architecture of the services module`
*   `@deepseek find potential bugs in app.py`

### Building the Project Context

The first time you run an analysis on a project, DeepCoderX will automatically build a context file (`.deepcoderx_context.md`). You can also trigger this manually:

*   `@deepseek --build-context`

## Using the Local AI Agent

If your command is not a file system command or a `@deepseek` command, it will be handled by the local AI agent. This agent can also use tools to answer your questions.

**Example:**

*   `What is the purpose of the MCPClient class?` (The AI will likely use `read_file` on `services/mcpclient.py` to answer this).
*   `Summarize the main loop in app.py`
