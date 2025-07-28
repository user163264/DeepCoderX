
import pytest
from unittest.mock import MagicMock, patch
from services.llm_handler import DeepSeekAnalysisHandler
from models.session import CommandContext

@pytest.fixture
def command_context(mocker):
    """Provides a mock CommandContext for tests."""
    ctx = MagicMock(spec=CommandContext)
    ctx.debug_mode = False
    ctx.mcp_client = MagicMock()
    mocker.patch('services.llm_handler.ContextManager', return_value=MagicMock())
    return ctx

@patch('services.llm_handler.requests.post')
def test_deepseek_delete_path_disabled(mock_post, command_context):
    """Tests that the 'delete_path' tool is disabled for the DeepSeek handler."""
    mock_post.return_value = MagicMock(
        status_code=200,
        json=lambda: {'choices': [{'message': {'content': '{"tool": "delete_path", "path": "some_file.txt"}'}}]}
    )

    handler = DeepSeekAnalysisHandler(command_context)
    handler.handle()

    # Check that the tool was not called and an error message was returned
    command_context.mcp_client.delete_path.assert_not_called()
    assert "[red]Error:[/] The 'delete_path' tool is disabled." in handler.ctx.response

@patch('services.llm_handler.subprocess.run')
@patch('services.llm_handler.requests.post')
def test_deepseek_run_bash_timeout(mock_post, mock_run, command_context):
    """Tests that the 'run_bash' tool has a 120-second timeout."""
    mock_post.side_effect = [
        MagicMock(
            status_code=200,
            json=lambda: {'choices': [{'message': {'content': '{"tool": "run_bash", "command": "sleep 1"}'}}]}
        ),
        MagicMock(
            status_code=200,
            json=lambda: {'choices': [{'message': {'content': 'Script executed.'}}]}
        )
    ]
    mock_run.return_value = MagicMock(stdout="Done", stderr="", returncode=0)

    handler = DeepSeekAnalysisHandler(command_context)
    handler.handle()

    # Check that subprocess.run was called with the correct timeout
    mock_run.assert_called_once()
    _, kwargs = mock_run.call_args
    assert kwargs['timeout'] == 120
    assert "Script executed." in handler.ctx.response
