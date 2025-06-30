# config.py
import os
import re
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load the .env file from the project root
env_path = Path(__file__).parent / '.env'
load_dotenv(dotenv_path=env_path)

class Config:
    # Core settings
    DEBUG_MODE = os.getenv("DEBUG_MODE", "false").lower() == "true"
    SANDBOX_PATH = os.getenv("SANDBOX_PATH", str(Path.home() / "Documents"))
    MAX_FILE_SIZE = int(os.getenv("MAX_FILE_SIZE", "1048576"))  # 1MB file size limit
    ALLOWED_EXTENSIONS = ['.py', '.js', '.ts', '.go', '.rs', '.java', 
                         '.txt', '.md', '.json', '.yml', '.yaml', 
                         '.html', '.css', '.sh']
    SCRIPTS_DIR = os.getenv("SCRIPTS_DIR", "scripts")

    # DeepSeek API configuration
    DEEPSEEK_ENABLED = os.getenv("DEEPSEEK_ENABLED", "true").lower() == "true"
    DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
    DEEPSEEK_API_URL = "https://api.deepseek.com/v1/chat/completions"
    
    # Local model configuration
    DUAL_MODEL_MODE = os.getenv("DUAL_MODEL_MODE", "true").lower() == "true"
    LANGUAGE_MODEL_PATH = os.getenv("LANGUAGE_MODEL_PATH", "/path/to/your/language_model.gguf")
    if getattr(sys, 'frozen', False):
        # The application is running as a PyInstaller bundle
        executable_dir = Path(sys.executable).parent
        LOCAL_MODEL_PATH = executable_dir / "qwen2.5-coder-1.5b-instruct-q8_0.gguf"
    else:
        # The application is running in a normal Python environment
        default_model_path = Path.home() / ".cache" / "lm-studio" / "models" / "Qwen" / "Qwen2.5-Coder-1.5B-Instruct-GGUF" / "qwen2.5-coder-1.5b-instruct-q8_0.gguf"
        LOCAL_MODEL_PATH = os.getenv("LOCAL_MODEL_PATH", str(default_model_path))
    
    # System role definition
    DEEPSEEK_SYSTEM_PROMPT = os.getenv(
        "DEEPSEEK_SYSTEM_PROMPT",
        """You are an expert software architect. Your primary goal is to answer the user's request. 
        You have been provided with a project context file to start your analysis. Read it carefully. 
        You MUST use the provided tools to gather any additional information you need. 
        Formulate a plan and execute it step-by-step using the tools until you have enough information to provide a final answer.\n\n
        To use a tool, you must respond with a JSON object matching the tool's signature.\n\n
        **Available Tools:**\n
        - `run_bash(command: str)`: Executes a shell command. Example: `{\"tool\": \"run_bash\", \"command\": \"ls -l\"}`\n
        - `read_file(path: str)`: Reads the content of a file.\n
        - `write_file(path: str, content: str)`: Writes content to a file.\n
        - `list_dir(path: str)`: Lists the contents of a directory.\n
        - `delete_path(path: str)`: Deletes a file or directory. This tool is disabled for you.\n\n
        """
    )
    LOCAL_SYSTEM_PROMPT = os.getenv(
        "LOCAL_SYSTEM_PROMPT", 
        """You are an expert programmer. You have access to a set of tools to interact with the local file system. 
When you need to access files, you must use these tools. You can only use one tool at a time.

**Available Tools:**
- `read_file(path: str)`: Reads the content of a file.
- `write_file(path: str, content: str)`: Writes content to a file.
- `list_dir(path: str)`: Lists the contents of a directory.

To use a tool, respond with a JSON object like this: 
{\"tool\": \"read_file\", \"path\": \"/path/to/file.py\"}

After you use a tool, the system will provide you with the result, and you can then continue the conversation.
If you have enough information to answer the user's request, provide the final answer directly without using a tool."""
    )
    # MCP server configuration
    MCP_SERVER_HOST = os.getenv("MCP_SERVER_HOST", "localhost")
    MCP_SERVER_PORT = int(os.getenv("MCP_SERVER_PORT", "8080"))
    MCP_API_KEY = os.getenv("MCP_API_KEY", "secure_mcp_key_123")
    
    # Current configuration
    CURRENT_CONFIG = f"""
    DEBUG_MODE: {DEBUG_MODE}
    SANDBOX_PATH: {SANDBOX_PATH}
    MAX_FILE_SIZE: {MAX_FILE_SIZE}
    ALLOWED_EXTENSIONS: {ALLOWED_EXTENSIONS}
    SCRIPTS_DIR: {SCRIPTS_DIR}
    DEEPSEEK_ENABLED: {DEEPSEEK_ENABLED}
    DEEPSEEK_API_URL: {DEEPSEEK_API_URL}
    DUAL_MODEL_MODE: {DUAL_MODEL_MODE}
    LOCAL_MODEL_PATH: {LOCAL_MODEL_PATH}
    MCP_SERVER_HOST: {MCP_SERVER_HOST}
    MCP_SERVER_PORT: {MCP_SERVER_PORT}
    """
    
    def __init__(self):
        self.validate_paths()
        
    def validate_paths(self):
        """Validate critical file paths on initialization"""
        sandbox = Path(self.SANDBOX_PATH)
        if not sandbox.exists():
            raise ValueError(f"Sandbox path does not exist: {self.SANDBOX_PATH}")
        if not sandbox.is_dir():
            raise ValueError(f"Sandbox path is not a directory: {self.SANDBOX_PATH}")
        
        scripts_dir = Path(self.SCRIPTS_DIR)
        if not scripts_dir.exists():
            scripts_dir.mkdir(parents=True, exist_ok=True)
    
    def __setattr__(self, name, value):
        """Validate critical settings before assignment"""
        # Sandbox path validation
        if name == "SANDBOX_PATH" and value:
            path = Path(value)
            if not path.exists():
                raise ValueError(f"Invalid sandbox path: {value}")
                
        # API key validation
        if name == "DEEPSEEK_API_KEY" and value:
            if not re.match(r'^sk-[a-zA-Z0-9]{24}$', value):
                raise ValueError("Invalid DeepSeek API key format")
                
        super().__setattr__(name, value)

# Initialize validated configuration
config = Config()

# Backward compatibility exports
DEBUG_MODE = config.DEBUG_MODE
DEEPSEEK_ENABLED = config.DEEPSEEK_ENABLED
SANDBOX_PATH = config.SANDBOX_PATH
MCP_SERVER_HOST = config.MCP_SERVER_HOST
MCP_SERVER_PORT = config.MCP_SERVER_PORT
MCP_API_KEY = config.MCP_API_KEY
MAX_FILE_SIZE = config.MAX_FILE_SIZE
ALLOWED_EXTENSIONS = config.ALLOWED_EXTENSIONS
DEEPSEEK_SYSTEM_PROMPT = config.DEEPSEEK_SYSTEM_PROMPT
LOCAL_SYSTEM_PROMPT = config.LOCAL_SYSTEM_PROMPT