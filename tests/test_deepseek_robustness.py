
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
        ctx.debug_mode = False
        yield ctx

@pytest.mark.skipif(not config.DEEPSEEK_API_KEY, reason="DEEPSEEK_API_KEY is not set")
def test_deepseek_large_file_handling(command_context):
    """Tests that the handler can handle a large file without crashing."""
    # 1. Create a large temporary file (e.g., 1MB)
    large_file_path = command_context.root_path / "large_file.txt"
    with open(large_file_path, "wb") as f:
        f.write(os.urandom(1024 * 1024)) # 1MB of random data

    # 2. Ask the handler to read and summarize the file
    command_context.user_input = f"@deepseek please summarize the file {large_file_path.name}"
    handler = DeepSeekAnalysisHandler(command_context)
    handler.handle()

    # 3. Verify that the handler provides a response without crashing
    # We are not checking the content of the summary, just that it handled the large file.
    assert "summarized" in handler.ctx.response.lower() or "summary" in handler.ctx.response.lower()
