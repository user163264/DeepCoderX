import pytest
from unittest.mock import MagicMock, patch
from services.llm_handler import FilesystemCommandHandler
from models.session import CommandContext

@pytest.fixture
def command_context():
    ctx = MagicMock(spec=CommandContext)
    ctx.debug_mode = False
    ctx.mcp_client = MagicMock()
    return ctx

# By patching the NLUParser, we can directly control the output for testing
@patch('services.llm_handler.config')
@patch('services.llm_handler.NLUParser')
def test_filesystem_handler_list_dir(MockNLUParser, mock_config, command_context):
    """Tests that the handler correctly calls list_dir based on NLU output."""
    # Configure the mock parser to return a specific intent
    mock_parser_instance = MockNLUParser.return_value
    mock_parser_instance.parse_intent.return_value = {
        "intent": "list_dir",
        "entities": {"path": "/some/path"}
    }

    handler = FilesystemCommandHandler(command_context)
    command_context.user_input = "use your tools to list files in /some/path"
    handler.handle()

    # Check that the correct MCPClient method was called
    handler.ctx.mcp_client.list_dir.assert_called_once_with("/some/path")

@patch('services.llm_handler.config')
@patch('services.llm_handler.NLUParser')
def test_filesystem_handler_read_file(MockNLUParser, mock_config, command_context):
    """Tests that the handler correctly calls read_file."""
    mock_parser_instance = MockNLUParser.return_value
    mock_parser_instance.parse_intent.return_value = {
        "intent": "read_file",
        "entities": {"path": "/a/file.txt"}
    }

    handler = FilesystemCommandHandler(command_context)
    command_context.user_input = "use your tools to read /a/file.txt"
    handler.handle()

    handler.ctx.mcp_client.read_file.assert_called_once_with("/a/file.txt")
