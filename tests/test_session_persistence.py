import pytest
import json
from pathlib import Path
from unittest.mock import patch, MagicMock
from services.llm_handler import DeepSeekAnalysisHandler, LocalCodingHandler
from models.session import CommandContext
from config import config

@pytest.fixture
def command_context(tmp_path):
    """Provides a CommandContext for tests with a temporary sandbox."""
    from services.mcpclient import MCPClient
    endpoint = f"http://{config.MCP_SERVER_HOST}:{config.MCP_SERVER_PORT}"
    mcp_client = MCPClient(endpoint, config.MCP_API_KEY)
    ctx = CommandContext(
        root_path=tmp_path,
        sandbox_path=tmp_path,
        mcp_client=mcp_client
    )
    ctx.debug_mode = True
    return ctx

@pytest.mark.parametrize("handler_class, session_file_name", [
    (DeepSeekAnalysisHandler, "deepseek_session.json"),
    (LocalCodingHandler, "local_session.json"),
])
@patch('services.llm_handler.requests.post')
@patch('services.llm_handler.Llama')
def test_session_is_saved_to_file(mock_llama, mock_post, command_context, handler_class, session_file_name):
    """Tests that the session history is saved to a file."""
    # 1. Mock the AI response
    mock_post.return_value = MagicMock(status_code=200, json=lambda: {'choices': [{'message': {'content': 'Test response'}}]})
    mock_llama.return_value.create_chat_completion.return_value = {'choices': [{'message': {'content': 'Test response'}}]}

    # 2. Handle a command
    command_context.user_input = "test command"
    handler = handler_class(command_context)
    handler.handle()

    # 3. Verify that the session file was created
    session_file = command_context.root_path / ".deepcoderx" / session_file_name
    assert session_file.exists()

    # 4. Verify that the session file contains the correct history
    with open(session_file, "r") as f:
        history = json.load(f)
    assert len(history) > 0
    assert history[-1]["content"] == "Test response"

@pytest.mark.parametrize("handler_class, session_file_name", [
    (DeepSeekAnalysisHandler, "deepseek_session.json"),
    (LocalCodingHandler, "local_session.json"),
])
@patch('services.llm_handler.Llama')
def test_session_is_loaded_from_file(mock_llama, command_context, handler_class, session_file_name):
    """Tests that the session history is loaded from a file."""
    # 1. Create a dummy session file
    session_dir = command_context.root_path / ".deepcoderx"
    session_dir.mkdir()
    session_file = session_dir / session_file_name
    dummy_history = [{"role": "system", "content": "dummy_prompt"}, {"role": "user", "content": "dummy_command"}]
    with open(session_file, "w") as f:
        json.dump(dummy_history, f)

    # 2. Initialize the handler
    handler = handler_class(command_context)

    # 3. Verify that the history was loaded
    assert handler.message_history == dummy_history

@pytest.mark.parametrize("handler_class, session_file_name", [
    (DeepSeekAnalysisHandler, "deepseek_session.json"),
    (LocalCodingHandler, "local_session.json"),
])
@patch('services.llm_handler.Llama')
def test_clear_history_deletes_file(mock_llama, command_context, handler_class, session_file_name):
    """Tests that clearing the history also deletes the session file."""
    # 1. Create a dummy session file
    session_dir = command_context.root_path / ".deepcoderx"
    session_dir.mkdir()
    session_file = session_dir / session_file_name
    with open(session_file, "w") as f:
        f.write("[]")

    # 2. Initialize the handler and clear the history
    handler = handler_class(command_context)
    handler.clear_history()

    # 3. Verify that the session file was deleted
    assert not session_file.exists()