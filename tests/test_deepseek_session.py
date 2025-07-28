
import pytest
from unittest.mock import MagicMock, patch
from services.llm_handler import DeepSeekAnalysisHandler
from models.session import CommandContext
from config import config

@pytest.fixture
def command_context(mocker):
    """Provides a mock CommandContext for tests."""
    ctx = MagicMock(spec=CommandContext)
    ctx.debug_mode = False
    ctx.mcp_client = MagicMock()
    mocker.patch('services.llm_handler.ContextManager', return_value=MagicMock())
    return ctx

@patch('services.llm_handler.requests.post')
def test_deepseek_session_persistence(mock_post, command_context):
    """Tests that the DeepSeek handler maintains a persistent session."""
    # 1. First, ask a question.
    mock_post.return_value = MagicMock(status_code=200, json=lambda: {'choices': [{'message': {'content': 'The answer is 42.'}}]})
    command_context.user_input = "@deepseek what is the meaning of life?"
    handler = DeepSeekAnalysisHandler(command_context)
    handler.handle()

    # 2. Then, ask a follow-up question.
    mock_post.return_value = MagicMock(status_code=200, json=lambda: {'choices': [{'message': {'content': 'I have already told you. It is 42.'}}]})
    command_context.user_input = "@deepseek are you sure?"
    handler.handle()

    # 3. Verify that the history was maintained.
    assert len(handler.message_history) == 5 # System, User, Assistant, User, Assistant
    assert "The answer is 42." in handler.message_history[2]['content']

@patch('services.llm_handler.requests.post')
def test_deepseek_clear_history(mock_post, command_context):
    """Tests that the '@deepseek clear' command clears the session history."""
    # 1. First, ask a question.
    mock_post.return_value = MagicMock(status_code=200, json=lambda: {'choices': [{'message': {'content': 'The answer is 42.'}}]})
    command_context.user_input = "@deepseek what is the meaning of life?"
    handler = DeepSeekAnalysisHandler(command_context)
    handler.handle()

    # 2. Verify that the history has content.
    assert len(handler.message_history) > 0

    # 3. Clear the history.
    handler.clear_history()

    # 4. Verify that the history is empty.
    assert len(handler.message_history) == 0
