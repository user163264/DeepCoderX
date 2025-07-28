import pytest
import json
from unittest.mock import MagicMock, patch
from services.llm_handler import LocalCodingHandler
from models.session import CommandContext

@pytest.fixture
def mock_llama():
    with patch('services.llm_handler.Llama') as mock:
        yield mock

@pytest.fixture
def command_context(mocker):
    mock_mcp_client = MagicMock()
    ctx = MagicMock(spec=CommandContext)
    ctx.debug_mode = False
    ctx.mcp_client = mock_mcp_client
    return ctx

@patch('services.llm_handler.config')
@patch('services.llm_handler.Llama')
def test_single_tool_call_loop(mock_llama, mock_config, command_context):
    """Tests a full, multi-turn conversation with a single tool call."""
    mock_config.ROLE_SYSTEM = "Test system prompt"
    mock_config.LOCAL_MODEL_PATH = "/fake/path/model.gguf"
    
    # The model first asks to read a file, then provides a final answer.
    mock_llama_instance = mock_llama.return_value
    mock_llama_instance.create_chat_completion.side_effect = [
        {'choices': [{'message': {'content': 'I need to read a file. {"tool": "read_file", "path": "a.txt"}'}}]}
        , # First response
        {'choices': [{'message': {'content': 'The file says: file content'}}]} # Second response
    ]
    command_context.mcp_client.read_file.return_value = {"content": "file content"}

    handler = LocalCodingHandler(command_context)
    command_context.user_input = "summarize a.txt"
    handler.handle()

    # Check that the tool was called correctly
    handler.ctx.mcp_client.read_file.assert_called_with("a.txt")
    
    # Check that the final response is the model's second message
    assert handler.ctx.response == "The file says: file content"
    
    # Check that the full conversation history is correct
    assert len(handler.message_history) == 5 # System, User, Assistant (tool), User (result), Assistant (final)
    assert handler.message_history[2]['content'] == 'I need to read a file. {"tool": "read_file", "path": "a.txt"}'
    assert "Tool Results:" in handler.message_history[3]['content']

@patch('services.llm_handler.config')
@patch('services.llm_handler.Llama')
def test_multiple_tool_calls_in_one_turn(mock_llama, mock_config, command_context):
    """Tests that the handler can execute multiple tool calls from a single model response."""
    mock_config.ROLE_SYSTEM = "Test system prompt"
    mock_config.LOCAL_MODEL_PATH = "/fake/path/model.gguf"
    
    mock_llama_instance = mock_llama.return_value
    # The model asks to read two files at once.
    mock_llama_instance.create_chat_completion.side_effect = [
        {'choices': [{'message': {'content': 'I need to read two files.\n{"tool": "read_file", "path": "a.txt"}\n{"tool": "read_file", "path": "b.txt"}'}}]}
        ,
        {'choices': [{'message': {'content': 'OK, I have both files.'}}]}
    ]
    command_context.mcp_client.read_file.side_effect = [
        {"content": "content of a"},
        {"content": "content of b"}
    ]

    handler = LocalCodingHandler(command_context)
    command_context.user_input = "compare a.txt and b.txt"
    handler.handle()

    # Check that read_file was called for both files
    assert command_context.mcp_client.read_file.call_count == 2
    command_context.mcp_client.read_file.assert_any_call("a.txt")
    command_context.mcp_client.read_file.assert_any_call("b.txt")

    # Check that the results for both tools were fed back to the model
    feedback_prompt = handler.message_history[3]['content']
    assert "content of a" in feedback_prompt
    assert "content of b" in feedback_prompt

    assert handler.ctx.response == "OK, I have both files."

@patch('services.llm_handler.Llama')
@patch('services.llm_handler.config')
def test_tool_loop_with_invalid_json(mock_config, mock_llama, command_context):
    """Tests that the loop handles malformed JSON from the model gracefully."""
    mock_config.ROLE_SYSTEM = "Test system prompt"
    mock_config.LOCAL_MODEL_PATH = "/fake/path/model.gguf"
    
    mock_llama_instance = mock_llama.return_value
    # The model returns text that contains malformed JSON
    mock_llama_instance.create_chat_completion.return_value = {
        'choices': [{'message': {'content': 'Here is the file I need: {"tool": "read_file", "path": "a.txt" malformed'}}]
    }

    handler = LocalCodingHandler(command_context)
    command_context.user_input = "read a.txt"
    handler.handle()

    # The handler should not crash. It should treat the invalid JSON as a final response.
    assert "Here is the file I need" in handler.ctx.response
    # Ensure no tools were called since JSON was malformed
    handler.ctx.mcp_client.read_file.assert_not_called()
