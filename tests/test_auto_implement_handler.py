import pytest
from unittest.mock import MagicMock
from pathlib import Path
from services.llm_handler import AutoImplementHandler
from models.session import CommandContext

@pytest.fixture
def command_context():
    ctx = MagicMock(spec=CommandContext)
    ctx.debug_mode = False
    ctx.dry_run = False
    ctx.auto_confirm = True
    ctx.mcp_client = MagicMock()
    # The get_relative_path method needs to return a Path object
    ctx.get_relative_path.side_effect = lambda p: Path("/test/root") / p
    return ctx

# This is a sample response from the AI model that the handler needs to parse
SAMPLE_MODEL_RESPONSE = """
I have analyzed the request and here are the required changes.

First, I will update the main application file.
```python:app.py
print("Hello, World!")
```

Next, I need to create a new utility file.
```python:utils/new_util.py
def new_function():
    return True
```
"""

def test_parse_response(command_context):
    """Tests that the handler correctly parses code blocks from the model's response."""
    handler = AutoImplementHandler(command_context)
    changes = handler._parse_response(SAMPLE_MODEL_RESPONSE)

    # Check that two changes were parsed
    assert len(changes) == 2

    # Check the details of the first change
    app_py_path = Path("/test/root/app.py")
    assert app_py_path in changes
    assert changes[app_py_path] == 'print("Hello, World!")'

    # Check the details of the second change
    util_path = Path("/test/root/utils/new_util.py")
    assert util_path in changes
    assert changes[util_path] == 'def new_function():\n    return True'

def test_apply_change(command_context):
    """Tests that the handler correctly calls the MCPClient to write files."""
    handler = AutoImplementHandler(command_context)
    handler.ctx.root_path = Path("/test/root")
    
    # Simulate applying a change
    test_path = Path("/test/root/a/b.py")
    test_content = "some new content"
    handler._apply_change(test_path, test_content)

    # Assert that the mcp_client's write_file method was called with the correct relative path
    handler.ctx.mcp_client.write_file.assert_called_once_with(
        "a/b.py", "some new content"
    )
