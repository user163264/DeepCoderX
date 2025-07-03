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
    DEBUG_MODE = os.getenv("DEBUG_MODE", "true").lower() == "true"
    SANDBOX_PATH = os.getenv("SANDBOX_PATH", str(Path.home() / "Documents"))
    MAX_FILE_SIZE = int(os.getenv("MAX_FILE_SIZE", "1048576"))  # 1MB file size limit
    ALLOWED_EXTENSIONS = ['.py', '.js', '.ts', '.go', '.rs', '.java', 
                         '.txt', '.md', '.json', '.yml', '.yaml', 
                         '.html', '.css', '.sh']
    SCRIPTS_DIR = os.getenv("SCRIPTS_DIR", "scripts")

    # OpenAI-Compatible Provider Configuration
    DEFAULT_PROVIDER = os.getenv("DEFAULT_PROVIDER", "local")
    
    # Provider definitions - OpenAI compatible endpoints
    PROVIDERS = {
        "local": {
            "name": "Local LM Studio",
            "base_url": os.getenv("LOCAL_BASE_URL", "http://localhost:1234/v1"),
            "api_key": os.getenv("LOCAL_API_KEY", "lm-studio"),  # LM Studio doesn't require real key
            "model": os.getenv("LOCAL_MODEL", "qwen2.5-coder-1.5b-instruct"),
            "enabled": os.getenv("LOCAL_ENABLED", "true").lower() == "true",
            "supports_tools": True,
            "temperature": 0.1,
            "max_tokens": 2048
        },
        "deepseek": {
            "name": "DeepSeek Cloud",
            "base_url": os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com/v1"),
            "api_key": os.getenv("DEEPSEEK_API_KEY"),
            "model": os.getenv("DEEPSEEK_MODEL", "deepseek-coder"),
            "enabled": os.getenv("DEEPSEEK_ENABLED", "true").lower() == "true",
            "supports_tools": True,
            "temperature": 0.1,
            "max_tokens": 4096
        },
        "openai": {
            "name": "OpenAI",
            "base_url": None,  # Use default OpenAI endpoint
            "api_key": os.getenv("OPENAI_API_KEY"),
            "model": os.getenv("OPENAI_MODEL", "gpt-4"),
            "enabled": os.getenv("OPENAI_ENABLED", "false").lower() == "true",
            "supports_tools": True,
            "temperature": 0.1,
            "max_tokens": 4096
        }
    }
    
    # Legacy compatibility
    DEEPSEEK_ENABLED = PROVIDERS["deepseek"]["enabled"]
    DEEPSEEK_API_KEY = PROVIDERS["deepseek"]["api_key"]
    DEEPSEEK_API_URL = PROVIDERS["deepseek"]["base_url"] + "/chat/completions"
    
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
    
    # SIMPLIFIED LOCAL SYSTEM PROMPT - Focus on natural conversation
    LOCAL_SYSTEM_PROMPT = os.getenv(
        "LOCAL_SYSTEM_PROMPT", 
        """You are a helpful programming assistant. Your goal is to provide clear, helpful responses.

**FOR SIMPLE CONVERSATIONS:** Answer directly without any tools.
Examples: "hello" → "Hello! How can I help you today?"
          "what is Python?" → Direct explanation about Python
          "what's your favorite color?" → "I don't have personal preferences, but I can help you with programming tasks!"

**FOR FILE/CODE TASKS:** Use the appropriate tool once, then explain what you did.
Examples: "create a script" → Use write_file tool, then explain
          "list files" → Use list_dir tool, then show results
          "read config.py" → Use read_file tool, then summarize

**TOOL FORMAT (when needed):**
{"tool": "tool_name", "parameter": "value"}

**Available Tools:**
- read_file(path): Read file content
- write_file(path, content): Create/write file  
- list_dir(path): List directory contents
- run_bash(command): Execute command

**KEY RULES:**
1. Most questions are conversations - answer directly
2. Only use tools when actually creating/reading/listing files
3. Use relative paths: "script.py", not "/full/path"
4. After using a tool, explain what you did in plain language
"""
    )
    
    # MCP server configuration
    MCP_SERVER_HOST = os.getenv("MCP_SERVER_HOST", "localhost")
    MCP_SERVER_PORT = int(os.getenv("MCP_SERVER_PORT", "8080"))
    MCP_API_KEY = os.getenv("MCP_API_KEY", "secure_mcp_key_123")
    
    # Tool execution configuration constants
    MAX_TOOL_CALLS = int(os.getenv("MAX_TOOL_CALLS", "50"))  # Allow up to 50 tool calls before asking user confirmation
    COMMAND_TIMEOUT = int(os.getenv("COMMAND_TIMEOUT", "120"))
    SHORT_COMMAND_TIMEOUT = int(os.getenv("SHORT_COMMAND_TIMEOUT", "30"))
    MODEL_CONTEXT_SIZE = int(os.getenv("MODEL_CONTEXT_SIZE", "4096"))
    HISTORY_TRIM_SIZE = int(os.getenv("HISTORY_TRIM_SIZE", "10"))
    HISTORY_KEEP_SIZE = int(os.getenv("HISTORY_KEEP_SIZE", "8"))
    API_REQUEST_TIMEOUT = int(os.getenv("API_REQUEST_TIMEOUT", "90"))
    MCP_CLIENT_TIMEOUT = int(os.getenv("MCP_CLIENT_TIMEOUT", "10"))
    
    # Current configuration
    CURRENT_CONFIG = f"""
    SANDBOX_PATH: {SANDBOX_PATH}
    LOCAL_MODEL_PATH: {LOCAL_MODEL_PATH}
    DEFAULT_PROVIDER: {DEFAULT_PROVIDER}
    AVAILABLE_PROVIDERS: {', '.join([p for p, provider_config in PROVIDERS.items() if provider_config['enabled']])}
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
CURRENT_CONFIG = config.CURRENT_CONFIG

# Tool execution constants
MAX_TOOL_CALLS = config.MAX_TOOL_CALLS
COMMAND_TIMEOUT = config.COMMAND_TIMEOUT
SHORT_COMMAND_TIMEOUT = config.SHORT_COMMAND_TIMEOUT
MODEL_CONTEXT_SIZE = config.MODEL_CONTEXT_SIZE
HISTORY_TRIM_SIZE = config.HISTORY_TRIM_SIZE
HISTORY_KEEP_SIZE = config.HISTORY_KEEP_SIZE
API_REQUEST_TIMEOUT = config.API_REQUEST_TIMEOUT
MCP_CLIENT_TIMEOUT = config.MCP_CLIENT_TIMEOUT