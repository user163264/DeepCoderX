import pytest
import os
import time
from services.llm_handler import DeepSeekAnalysisHandler
from models.session import CommandContext
from config import config

from pathlib import Path

import tempfile

import threading

@pytest.fixture
def command_context():
    """Provides a CommandContext for tests with a temporary sandbox and a running MCP server."""
    with tempfile.TemporaryDirectory() as tmpdir:
        from services.mcpserver import start_mcp_server
        from services.mcpclient import MCPClient

        # Start the MCP server in a background thread
        mcp_server_thread = threading.Thread(
            target=start_mcp_server,
            daemon=True,
            kwargs={
                "host": config.MCP_SERVER_HOST,
                "port": config.MCP_SERVER_PORT,
                "sandbox_path": tmpdir
            }
        )
        mcp_server_thread.start()
        time.sleep(1) # Give the server a moment to start

        endpoint = f"http://{config.MCP_SERVER_HOST}:{config.MCP_SERVER_PORT}"
        mcp_client = MCPClient(endpoint, config.MCP_API_KEY)
        ctx = CommandContext(
            root_path=Path(tmpdir),
            sandbox_path=Path(tmpdir),
            mcp_client=mcp_client
        )
        ctx.debug_mode = False  # Enable debug mode for more verbose output
        yield ctx

@pytest.mark.skipif(not config.DEEPSEEK_API_KEY, reason="DEEPSEEK_API_KEY is not set")
def test_deepseek_real_file_read(command_context):
    """Tests that the handler can read a real file using the DeepSeek API."""
    # 1. Create a temporary file inside the sandbox
    file_path = command_context.root_path / "deepseek_test.txt"
    with open(file_path, "w") as f:
        f.write("This is a test file for DeepSeek.")

    # 2. Ask the handler to read the file
    command_context.user_input = f"@deepseek read the file {file_path.name}"
    handler = DeepSeekAnalysisHandler(command_context)
    handler.handle()

    # 3. Verify the response
    assert "This is a test file for DeepSeek" in handler.ctx.response

@pytest.mark.skipif(not config.DEEPSEEK_API_KEY, reason="DEEPSEEK_API_KEY is not set")
def test_deepseek_real_script_execution(command_context):
    """Tests that the handler can create and execute a real shell script."""
    # 1. Define the script content and path inside the sandbox
    script_path = command_context.root_path / "deepseek_test.sh"
    script_content = "echo 'Hello from DeepSeek script!'"

    # 2. Ask the handler to create and run the script
    command_context.user_input = f"@deepseek create a file at {script_path.name} with the content \"{script_content}\" and then run it with bash"
    handler = DeepSeekAnalysisHandler(command_context)
    handler.handle()

    # 3. Verify the response
    assert "Hello from DeepSeek script!" in handler.ctx.response