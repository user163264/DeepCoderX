# DeepCoderX Technical Documentation

This document provides a detailed technical overview of the DeepCoderX application, its architecture, and its key features. It is intended for developers who are working on or contributing to the project.

---

## 1. Core Architecture

DeepCoderX is a sophisticated, CLI-based AI coding assistant built in Python. It is designed to be a powerful and flexible tool for developers, combining the strengths of both local and cloud-based AI models.

The core architecture is built on the following principles:

*   **Modularity**: The application is divided into a set of distinct, single-responsibility modules (e.g., configuration, command processing, session management, UI).
*   **Extensibility**: The command handler system makes it easy to add new commands and capabilities without modifying the core application logic.
*   **Security**: All file system operations are routed through a sandboxed Managed Code Protocol (MCP) server, preventing the AI models from performing dangerous actions.
*   **User Experience**: The application features a rich, interactive command-line interface powered by the `rich` library.

---

## 2. Configuration (`config.py`)

The `config.py` file is the single source of truth for all application settings. It is designed to be both flexible and robust.

### Key Features:

*   **Centralized Settings**: All configuration variables, including API keys, file paths, and system prompts, are defined in this file.
*   **Environment Variable Overrides**: The application uses the `python-dotenv` library to load settings from a `.env` file in the project root. This allows developers to easily override the default settings without modifying the source code.
*   **Automatic `.env` Template Creation**: On its first run, the application will automatically create a `.env` file from a template if one doesn't exist. This makes it easy for new users to get started.
*   **Platform-Agnostic Paths**: The configuration uses `pathlib.Path.home()` to determine the user's home directory, ensuring that the application works correctly on both macOS and Linux.
*   **Dynamic Model Path**: The `LOCAL_MODEL_PATH` is determined dynamically at runtime. When running as a PyInstaller executable, it looks for the model in the same directory as the executable. Otherwise, it uses the path from the environment or a default.

---

## 3. Command Processing

The command processing pipeline is the heart of the application. It is responsible for taking user input, routing it to the correct handler, and executing the corresponding logic.

### Key Components:

*   **`CommandProcessor`**: This class is responsible for managing the command handlers and executing the main command loop.
*   **`CommandHandler` (Base Class)**: An abstract base class that defines the interface for all command handlers.
*   **Concrete Handlers**:
    *   **`DeepSeekAnalysisHandler`**: Manages the powerful cloud-based DeepSeek API. It is pre-loaded with the project's context to perform deep, comprehensive codebase analysis.
    *   **`LocalCodingHandler`**: Manages the local Qwen model. It is used for general-purpose coding tasks and provides a fast, offline-capable experience.
    *   **`FilesystemCommandHandler`**: Handles all file system operations (e.g., `ls`, `cat`, `vim`). It uses the MCP client to ensure that all operations are performed in a secure sandbox.

---

## 4. Session Management

DeepCoderX features a robust, persistent session management system for both the DeepSeek and local models.

### Key Features:

*   **File-Based Persistence**: The conversation history for each model is stored in a JSON file in the `.deepcoderx/` directory in the project root.
*   **Automatic Loading**: When the application starts, it automatically loads the session history from the corresponding file.
*   **Save on Exit**: To ensure good performance, the session history is only saved to disk when the application exits. This provides a good balance between performance and reliability.
*   **History Truncation**: To prevent the context from growing too large, the application automatically truncates the message history, keeping the system prompt and the last 8 messages.
*   **Manual Clearing**: The `clear` and `@deepseek clear` commands allow the user to manually clear the session history for the local and DeepSeek models, respectively.

---

## 5. User Interface (UI)

The user interface is built with the `rich` library to provide a modern, visually appealing, and user-friendly command-line experience.

### Key Features:

*   **Rich Text and Colors**: The application uses `rich` to display colored text, panels, and other UI elements.
*   **Customizable Panels**: The panels for the logo, project info, and assistant responses are all customizable with different colors and styles.
*   **Asynchronous Progress Bar**: A multi-threaded progress bar with a "silly message" updater provides feedback to the user during long-running operations without blocking the UI.
*   **Transient Progress Bar**: The progress bar is configured to be `transient`, meaning it disappears completely after the task is complete, leaving a clean UI.

---

## 6. Build & Distribution

The application can be packaged into a single, standalone executable using `PyInstaller`.

### Key Features:

*   **One-File Executable**: The `pyinstaller --onefile` command bundles the entire application and its dependencies into a single executable file.
*   **Cross-Platform Builds**: The application can be built for both macOS and Linux by running the `pyinstaller` command on the target operating system.
*   **Dynamic Model Loading**: The application is configured to look for the local model file in the same directory as the executable, making it easy to distribute.

---

## 7. Cross-Platform Compatibility

Great care has been taken to ensure that the application runs correctly on both macOS and Ubuntu Linux.

### Key Features:

*   **Platform-Agnostic Paths**: The use of `pathlib.Path` ensures that all file paths are handled correctly on both operating systems.
*   **Conditional Imports**: The application uses `sys.platform == 'darwin'` to conditionally import the `gnureadline` library on macOS, which is not needed on Linux.
*   **Cross-Platform Build Process**: The `INSTALL.md` file provides detailed instructions for building the application on both macOS and Linux.
