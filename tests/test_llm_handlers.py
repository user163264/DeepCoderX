import pytest
from unittest.mock import MagicMock, patch
from services.llm_handler import LocalCodingHandler, DeepSeekAnalysisHandler
from models.session import CommandContext

import pytest
try:
    from llama_cpp import Llama
    LLAMA_AVAILABLE = True
except ImportError:
    LLAMA_AVAILABLE = False

pytest_llm_skip = pytest.mark.skipif(not LLAMA_AVAILABLE, reason="llama-cpp-python not available")
# Mock the Llama object so we don't need a real model for tests
@pytest.fixture
def command_context(mocker):
    """Creates a mock CommandContext for handlers."""
    # Mock the MCPClient within the context
    mock_mcp_client = MagicMock()
    mock_mcp_client.read_file.return_value = {"content": "file content"}
    
    ctx = MagicMock(spec=CommandContext)
    ctx.debug_mode = False
    ctx.mcp_client = mock_mcp_client
    return ctx

@patch('services.llm_handler.config')
@patch('services.llm_handler.Llama')
def test_local_handler_initialization(mock_llama, mock_config, command_context):
    """Tests that the LocalCodingHandler initializes correctly."""
    mock_config.ROLE_SYSTEM = "Test system prompt"
    mock_config.LOCAL_MODEL_PATH = "/fake/path/model.gguf"
    
    handler = LocalCodingHandler(command_context)
    assert handler is not None
    # Check that the Llama model was initialized
    mock_llama.assert_called_once()
    assert len(handler.message_history) == 1
    assert handler.message_history[0]['role'] == 'system'

@patch('services.llm_handler.config')
@patch('services.llm_handler.Llama')
def test_local_handler_simple_prompt(mock_llama, mock_config, command_context):
    """Tests a simple prompt without file mentions or tool use."""
    mock_config.ROLE_SYSTEM = "Test system prompt"
    mock_config.LOCAL_MODEL_PATH = "/fake/path/model.gguf"
    
    mock_llama.return_value.create_chat_completion.return_value = {
        'choices': [{'message': {'content': 'Hello from the mock model!'}}]
    }
    handler = LocalCodingHandler(command_context)
    command_context.user_input = "hello"
    
    handler.handle()
    
    # Check that the final response is from the model
    assert handler.ctx.response == "Hello from the mock model!"
    # Check that the user's prompt and the model's response were added to history
    assert len(handler.message_history) == 3
    assert handler.message_history[1]['content'] == "hello"

@patch('services.llm_handler.config')
@patch('services.llm_handler.Llama')
def test_local_handler_with_file_mention(mock_llama, mock_config, command_context):
    """Tests that the handler correctly reads a file and adds it to the prompt."""
    mock_config.ROLE_SYSTEM = "Test system prompt"
    mock_config.LOCAL_MODEL_PATH = "/fake/path/model.gguf"
    
    mock_llama.return_value.create_chat_completion.return_value = {
        'choices': [{'message': {'content': 'File summarized.'}}]
    }
    handler = LocalCodingHandler(command_context)
    command_context.user_input = "@/path/to/file.txt Please summarize this file."
    
    handler.handle()
    
    # Check that the MCPClient was called to read the file
    handler.ctx.mcp_client.read_file.assert_called_with("/path/to/file.txt")
    
    # Check that the file content was included in the prompt sent to the model
    final_prompt = handler.message_history[1]['content']
    assert "Please summarize this file." in final_prompt
    assert "--- Content from @/path/to/file.txt ---" in final_prompt
    assert "file content" in final_prompt

@patch('services.llm_handler.config')
@patch('services.llm_handler.Llama')
def test_clear_history(mock_llama, mock_config, command_context):
    """Tests that the clear_history method resets the conversation."""
    mock_config.ROLE_SYSTEM = "Test system prompt"
    mock_config.LOCAL_MODEL_PATH = "/fake/path/model.gguf"
    
    handler = LocalCodingHandler(command_context)
    
    # Add some messages to the history
    handler.message_history.append({"role": "user", "content": "first message"})
    handler.message_history.append({"role": "assistant", "content": "first response"})
    assert len(handler.message_history) == 3

    # Clear the history
    handler.clear_history()

    # Assert that only the system prompt remains
    assert len(handler.message_history) == 1
    assert handler.message_history[0]['role'] == 'system'
