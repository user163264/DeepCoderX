import logging
from rich.console import Console
from rich.logging import RichHandler

# Create logger instance
logger = logging.getLogger("deepcoderx")
logger.setLevel(logging.INFO)

# Configure rich handler
console = Console()
handler = RichHandler(console=console, show_time=False, show_level=False)
handler.setFormatter(logging.Formatter("%(message)s"))
logger.addHandler(handler)

def log_api_usage(provider: str, tokens: int):
    """
    Log API token usage statistics with rich formatting
    """
    # Log to standard logger
    logger.info(f"API Usage: {provider} - {tokens} tokens")
    
    # Also print to console with rich formatting
    console.print(f"[dim]📊 API Usage: [bold]{provider}[/] - {tokens} tokens[/dim]")