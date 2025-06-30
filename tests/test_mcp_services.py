import pytest
import requests
from unittest.mock import MagicMock, patch
from services.mcpclient import MCPClient

# This fixture provides a client instance for each test function.
@pytest.fixture
def mcp_client():
    """Provides an MCPClient instance for testing."""
    return MCPClient(endpoint="http://test.server:8080", api_key="test-key")

# --- MCPClient Method Tests ---

@patch('services.mcpclient.requests.get')
def test_read_file_success(mock_get, mcp_client):
    """Tests a successful file read call."""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"content": "hello world"}
    mock_get.return_value = mock_response

    result = mcp_client.read_file("test.txt")

    mock_get.assert_called_once_with(
        "http://test.server:8080/read?file=test.txt",
        headers={"Content-Type": "application/json", "X-API-Key": "test-key"},
        timeout=10
    )
    assert result == {"content": "hello world"}

@patch('services.mcpclient.requests.post')
def test_write_file_success(mock_post, mcp_client):
    """Tests a successful file write call."""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"status": "success"}
    mock_post.return_value = mock_response

    result = mcp_client.write_file("new.txt", "some content")

    mock_post.assert_called_once_with(
        "http://test.server:8080/write",
        headers={"Content-Type": "application/json", "X-API-Key": "test-key"},
        json={"file": "new.txt", "content": "some content"},
        timeout=10
    )
    assert result == {"status": "success"}

@patch('services.mcpclient.requests.post')
def test_list_dir_success(mock_post, mcp_client):
    """Tests a successful directory listing call."""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"files": ["a.txt"], "directories": ["d1"]}
    mock_post.return_value = mock_response

    result = mcp_client.list_dir(".")

    mock_post.assert_called_once_with(
        "http://test.server:8080/list",
        headers={"Content-Type": "application/json", "X-API-Key": "test-key"},
        json={"path": "."},
        timeout=10
    )
    assert result == {"files": ["a.txt"], "directories": ["d1"]}

@patch('services.mcpclient.requests.post')
def test_delete_path_success(mock_post, mcp_client):
    """Tests a successful path deletion call."""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"status": "success"}
    mock_post.return_value = mock_response

    result = mcp_client.delete_path("path/to/delete", recursive=True)

    mock_post.assert_called_once_with(
        "http://test.server:8080/delete",
        headers={"Content-Type": "application/json", "X-API-Key": "test-key"},
        json={"path": "path/to/delete", "recursive": True},
        timeout=10
    )
    assert result == {"status": "success"}

# --- MCPClient Error Handling Tests ---

@patch('services.mcpclient.requests.get')
def test_client_handles_network_error(mock_get, mcp_client):
    """Tests that the client returns a custom error on network issues."""
    mock_get.side_effect = requests.exceptions.RequestException("Connection Error")

    result = mcp_client.read_file("any.txt")

    assert "error" in result
    assert "MCP request failed: Connection Error" in result["error"]

@patch('services.mcpclient.requests.post')
def test_write_file_network_error(mock_post, mcp_client):
    """Tests that write_file handles network errors correctly."""
    mock_post.side_effect = requests.exceptions.RequestException("Network timeout")

    result = mcp_client.write_file("test.txt", "content")

    assert "error" in result
    assert "MCP request failed: Network timeout" in result["error"]

@patch('services.mcpclient.requests.post')
def test_list_dir_network_error(mock_post, mcp_client):
    """Tests that list_dir handles network errors correctly."""
    mock_post.side_effect = requests.exceptions.RequestException("Connection refused")

    result = mcp_client.list_dir(".")

    assert "error" in result
    assert "MCP request failed: Connection refused" in result["error"]

@patch('services.mcpclient.requests.post')
def test_delete_path_network_error(mock_post, mcp_client):
    """Tests that delete_path handles network errors correctly."""
    mock_post.side_effect = requests.exceptions.RequestException("Timeout")

    result = mcp_client.delete_path("test_path")

    assert "error" in result
    assert "MCP request failed: Timeout" in result["error"]

# --- Additional Edge Cases ---

@patch('services.mcpclient.requests.get')
def test_read_file_with_special_characters(mock_get, mcp_client):
    """Tests reading a file with special characters in the path."""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"content": "special content"}
    mock_get.return_value = mock_response

    result = mcp_client.read_file("path with spaces/special-file_123.txt")

    mock_get.assert_called_once_with(
        "http://test.server:8080/read?file=path with spaces/special-file_123.txt",
        headers={"Content-Type": "application/json", "X-API-Key": "test-key"},
        timeout=10
    )
    assert result == {"content": "special content"}

@patch('services.mcpclient.requests.post')
def test_delete_path_without_recursive(mock_post, mcp_client):
    """Tests path deletion without recursive flag."""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"status": "success"}
    mock_post.return_value = mock_response

    result = mcp_client.delete_path("file.txt")

    mock_post.assert_called_once_with(
        "http://test.server:8080/delete",
        headers={"Content-Type": "application/json", "X-API-Key": "test-key"},
        json={"path": "file.txt", "recursive": False},
        timeout=10
    )
    assert result == {"status": "success"}
