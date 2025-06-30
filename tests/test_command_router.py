import pytest
from unittest.mock import MagicMock
from models.router import CommandProcessor, CommandHandler
from models.session import CommandContext

# A fixture to create a basic CommandProcessor with a mock context
@pytest.fixture
def command_processor():
    mock_context = MagicMock(spec=CommandContext)
    mock_context.debug_mode = False
    return CommandProcessor(mock_context)

# Create mock handlers for testing routing logic
class MockHandlerA(CommandHandler):
    def can_handle(self) -> bool:
        return self.ctx.user_input == "handle_a"
    def handle(self) -> None:
        self.ctx.response = "Handled by A"

class MockHandlerB(CommandHandler):
    def can_handle(self) -> bool:
        return self.ctx.user_input == "handle_b"
    def handle(self) -> None:
        self.ctx.response = "Handled by B"

class FallbackHandler(CommandHandler):
    def can_handle(self) -> bool:
        return True # Always handles if no other handler does
    def handle(self) -> None:
        self.ctx.response = "Handled by Fallback"

def test_command_routing(command_processor):
    """Tests that the processor routes to the correct handler."""
    handler_a = MockHandlerA(command_processor.ctx)
    handler_b = MockHandlerB(command_processor.ctx)
    
    command_processor.add_handler(handler_a)
    command_processor.add_handler(handler_b)

    # Test routing to Handler A
    command_processor.ctx.user_input = "handle_a"
    response = command_processor.execute("handle_a")
    assert response == "Handled by A"

    # Test routing to Handler B
    command_processor.ctx.user_input = "handle_b"
    response = command_processor.execute("handle_b")
    assert response == "Handled by B"

def test_fallback_handler(command_processor):
    """Tests that the fallback handler is used when no other handler matches."""
    handler_a = MockHandlerA(command_processor.ctx)
    fallback = FallbackHandler(command_processor.ctx)

    command_processor.add_handler(handler_a)
    command_processor.add_handler(fallback)

    # This input doesn't match Handler A, so it should go to the fallback
    command_processor.ctx.user_input = "unhandled_command"
    response = command_processor.execute("unhandled_command")
    assert response == "Handled by Fallback"

def test_middleware_execution(command_processor):
    """Tests that middleware is executed before handlers."""
    class MockMiddleware(CommandHandler):
        def can_handle(self) -> bool:
            return True # Middleware always runs
        def handle(self) -> None:
            # Middleware sets a flag to show it ran
            self.ctx.middleware_ran = True

    handler_a = MockHandlerA(command_processor.ctx)
    middleware = MockMiddleware(command_processor.ctx)

    command_processor.add_middleware(middleware)
    command_processor.add_handler(handler_a)

    # Initialize the flag
    command_processor.ctx.middleware_ran = False
    
    command_processor.ctx.user_input = "handle_a"
    response = command_processor.execute("handle_a")
    
    # Check that middleware ran and handler executed
    assert command_processor.ctx.middleware_ran == True
    assert response == "Handled by A"
