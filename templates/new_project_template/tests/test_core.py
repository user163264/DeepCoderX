import pytest
from src.core import utils

def test_hello_world(capsys):
    """
    Tests the hello_world function.
    """
    utils.hello_world()
    captured = capsys.readouterr()
    assert "Hello from the core utility module!" in captured.out
