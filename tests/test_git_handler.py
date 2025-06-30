"""
Tests for Git operations handler
"""

import pytest
from unittest.mock import MagicMock, patch
from pathlib import Path
from ..services.git_handler import GitHandler
from ..models.session import CommandContext

@pytest.fixture
def git_handler():
    mock_mcp = MagicMock()
    mock_ctx = CommandContext(
        root_path=Path("/test/project"),
        mcp_client=mock_mcp,
        sandbox_path=Path("/sandbox")
    )
    return GitHandler(mock_ctx)

def test_git_init(git_handler):
    git_handler.ctx.user_input = "git init /test/path"
    git_handler.handle()
    git_handler.ctx.mcp_client.execute.assert_called_with(
        ['git', 'init', '/test/path']
    )

def test_git_clone(git_handler):
    git_handler.ctx.user_input = "git clone https://github.com/test/repo.git /clone/path"
    git_handler.handle()
    git_handler.ctx.mcp_client.execute.assert_called_with(
        ['git', 'clone', 'https://github.com/test/repo.git', '/clone/path']
    )