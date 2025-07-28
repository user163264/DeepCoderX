# Getting Started with DeepCoderX

This guide will walk you through the steps to get DeepCoderX up and running on your local machine.

## 1. Installation

DeepCoderX is a Python application. To install it, you will need to have Python 3.10 or higher installed on your system. You can then install the required dependencies using `pip`.

```bash
# Clone the repository (if you haven't already)
# git clone <repository_url>
# cd DeepCoderX

# Create and activate a virtual environment (recommended)
python -m venv VENV
source VENV/bin/activate

# Install the required packages
pip install -r requirements.txt
```

## 2. Configuration

DeepCoderX uses a `.env` file for configuration. You will need to create this file in the root of the project directory.

1.  **Create the `.env` file:**
    ```bash
    touch .env
    ```

2.  **Add the following environment variables to the file:**

    ```
    # The absolute path to the directory you want to use as the sandbox.
    # All file operations will be confined to this directory.
    SANDBOX_PATH=/path/to/your/projects

    # Your API key for the DeepSeek API (optional, but required for @deepseek commands)
    DEEPSEEK_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxx

    # The URL for your local LLM instance (e.g., LM Studio)
    LMSTUDIO_URL=http://localhost:1234/v1/chat/completions
    ```

## 3. Running the Application

Once you have installed the dependencies and configured your `.env` file, you can run the application from the command line.

```bash
python run.py --dir /path/to/the/project/you/want/to/work/on
```

*   The `--dir` argument is required. It tells DeepCoderX which project you want to work on. This directory must be inside the `SANDBOX_PATH` you defined in your `.env` file.

### Command-Line Arguments

You can customize the application's behavior with the following command-line arguments:

*   `--dir`: (Required) The absolute path to the project directory.
*   `--debug`: Enables debug mode, which will print additional information to the console.
*   `--dry-run`: In dry-run mode, the application will not make any changes to the file system.
*   `--auto-confirm`: Automatically confirms any file modification prompts.
