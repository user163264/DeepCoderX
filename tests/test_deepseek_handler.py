import pytest
import json
import requests
from unittest.mock import MagicMock, patch
from services.llm_handler import DeepSeekAnalysisHandler
from models.session import CommandContext

@pytest.fixture
def command_context(mocker):
    ctx = MagicMock(spec=CommandContext)
    ctx.debug_mode = False
    ctx.mcp_client = MagicMock()
    # The handler will call this, so we need to mock it.
    mocker.patch('services.llm_handler.ContextManager', return_value=MagicMock())
    return ctx

@patch('services.llm_handler.requests.post')
def test_deepseek_multi_turn_tool_use(mock_post, command_context):
    """Tests a complex, multi-turn conversation with multiple, different tool calls."""
    # 1. AI asks to list files.
    # 2. AI receives file list and asks to read one.
    # 3. AI receives file content and provides a final answer.
    mock_post.side_effect = [
        MagicMock(status_code=200, json=lambda: {'choices': [{'message': {'content': '{"tool": "list_dir", "path": "."}'}}]}),
        MagicMock(status_code=200, json=lambda: {'choices': [{'message': {'content': '{"tool": "read_file", "path": "app.py"}'}}]}),
        MagicMock(status_code=200, json=lambda: {'choices': [{'message': {'content': 'The app.py file is the main entry point.'}}]})
    ]
    command_context.mcp_client.list_dir.return_value = {"result": {"files": ["app.py"], "directories": []}}
    command_context.mcp_client.read_file.return_value = {"content": "import app"}

    handler = DeepSeekAnalysisHandler(command_context)
    handler.handle()

    assert command_context.mcp_client.list_dir.call_count == 1
    assert command_context.mcp_client.read_file.call_count == 1
    assert "The app.py file is the main entry point." in handler.ctx.response

@patch('services.llm_handler.requests.post')
def test_deepseek_handles_malformed_json(mock_post, command_context):
    """Tests that the handler can gracefully handle invalid JSON from the API."""
    mock_post.return_value = MagicMock(status_code=200, json=lambda: {'choices': [{'message': {'content': 'This is not JSON {"tool": '}}]}
    
    handler = DeepSeekAnalysisHandler(command_context)
    handler.handle()

    # The handler should not crash and should return the raw text as the response
    assert "This is not JSON" in handler.ctx.response

@patch('services.llm_handler.requests.post')
def test_deepseek_handles_api_error(mock_post, command_context):
    """Tests that the handler correctly reports an API network failure."""
    mock_post.side_effect = requests.exceptions.RequestException("API is down")

    handler = DeepSeekAnalysisHandler(command_context)
    handler.handle()

    assert "[red]API Error:[/] API is down" in handler.ctx.response

@patch('services.llm_handler.requests.post')
def test_deepseek_handles_tool_failure(mock_post, command_context):
    """Tests that a tool execution failure is reported back to the AI."""
    mock_post.side_effect = [
        MagicMock(status_code=200, json=lambda: {'choices': [{'message': {'content': '{"tool": "read_file", "path": "not_found.txt"}'}}]}),
        MagicMock(status_code=200, json=lambda: {'choices': [{'message': {'content': 'It seems that file does not exist.'}}]})
    ]
    command_context.mcp_client.read_file.return_value = {"error": "File not found"}

    handler = DeepSeekAnalysisHandler(command_context)
    handler.handle()

    assert command_context.mcp_client.read_file.call_count == 1
    # Check that the error was fed back to the model
    last_message_to_model = mock_post.call_args_list[1][1]['json']['messages'][-1]['content']
    assert "Tool Results:" in last_message_to_model
    assert "File not found" in last_message_to_model
    assert "It seems that file does not exist." in handler.ctx.response
