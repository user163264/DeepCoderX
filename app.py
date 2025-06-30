import sys
import os
import argparse
import threading
from pathlib import Path
from dotenv import load_dotenv

# Load the .env file from the project root
env_path = Path(__file__).parent / '.env'
load_dotenv(dotenv_path=env_path)

# Import gnureadline for arrow key support on macOS
# This MUST be one of the first imports to work correctly.
if sys.platform == 'darwin':
    import gnureadline

from rich.console import Console
from rich.panel import Panel
import time
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.markdown import Markdown
from rich.text import Text
from utils.silly_messages import get_silly_message

from config import config
from models.session import CommandContext
from models.router import CommandProcessor, CommandHandler
from services.llm_handler import (
    SecurityMiddleware, 
    FilesystemCommandHandler,
    DeepSeekAnalysisHandler,
    AutoImplementHandler,
    LocalCodingHandler
)
from services.mcpserver import start_mcp_server
from services.mcpclient import MCPClient

console = Console()

def start_background_mcp():
    """Start MCP server in background thread"""
    threading.Thread(
        target=start_mcp_server,
        daemon=True,
        kwargs={
            "host": config.MCP_SERVER_HOST,
            "port": config.MCP_SERVER_PORT,
            "sandbox_path": config.SANDBOX_PATH
        }
    ).start()

def create_env_template_if_needed():
    """Create a .env file from a template if one doesn't exist."""
    env_path = Path('.env')
    if not env_path.exists():
        template = (
            "# DeepCoderX Configuration\n"
            "# --------------------------\n\n"
            "# Your DeepSeek API key (required for @deepseek commands)\n"
            "DEEPSEEK_API_KEY=\n\n"
            "# The full path to your local model file (e.g., /path/to/your/model.gguf)\n"
            f"LOCAL_MODEL_PATH={config.LOCAL_MODEL_PATH}\n"
        )
        with open(env_path, 'w') as f:
            f.write(template)
        console.print("[bold yellow]Created a new .env file. Please edit it to add your DeepSeek API key.[/]")

def main():
    create_env_template_if_needed()
    parser = argparse.ArgumentParser(description="DeepCoderX - AI Coding Assistant")
    parser.add_argument("--dir", default=os.getcwd(), help="Project directory")
    parser.add_argument("--debug", action="store_true", help="Enable debug mode")
    parser.add_argument("--dry-run", action="store_true", help="Enable dry-run mode")
    parser.add_argument("--auto-confirm", action="store_true", help="Auto-confirm file modifications")
    args = parser.parse_args()
    
    try:
        project_dir = Path(args.dir).resolve()
        os.chdir(project_dir)
    except Exception as e:
        console.print(f"[red]Error:[/] {str(e)}")
        project_dir = Path.cwd()
    
    # Start MCP server
    start_background_mcp()
    
    # Create MCP client
    mcp_client = MCPClient(
        endpoint=f"http://{config.MCP_SERVER_HOST}:{config.MCP_SERVER_PORT}",
        api_key=config.MCP_API_KEY
    )
    
    ctx = CommandContext(
        root_path=project_dir,
        mcp_client=mcp_client,
        sandbox_path=config.SANDBOX_PATH
    )
    ctx.debug_mode = args.debug or config.DEBUG_MODE
    ctx.dry_run = args.dry_run
    ctx.auto_confirm = args.auto_confirm
    
    processor = CommandProcessor(ctx)
    processor.add_middleware(SecurityMiddleware(ctx))
    processor.add_handler(FilesystemCommandHandler(ctx))
    processor.add_handler(DeepSeekAnalysisHandler(ctx))
    processor.add_handler(AutoImplementHandler(ctx))
    processor.add_handler(LocalCodingHandler(ctx))

    # Add a fallback handler for unknown commands
    class NotFoundHandler(CommandHandler):
        def can_handle(self) -> bool:
            return True
        def handle(self) -> None:
            self.ctx.response = f"[red]Error:[/] Command not found: {self.ctx.user_input}"
    processor.add_handler(NotFoundHandler(ctx))

    # Display the startup logo
   
    logo = Text(r"""



            DeepCoderX
                                                                                   

          
                                                                                 
                                                                                 
    """, justify="center", style="bold magenta")
    console.print(Panel(logo, border_style="#9c9a9a"))
    
    console.print(Panel(
        f"[bold]DeepCoderX[/] | [green]Project:[/] {project_dir.name}",
        border_style="#9c9a9a"
    ))
    console.print("[dim]Type 'exit' or 'quit' to end the session.[/]")

    while True:
        try:
            user_input = console.input("\n👤 [bold]You:[/] ").strip()
            if not user_input:
                continue
            if user_input.lower() in ('exit', 'quit'):
                raise KeyboardInterrupt
            if user_input.lower() == 'clear':
                for handler in processor.handlers:
                    if isinstance(handler, LocalCodingHandler):
                        handler.clear_history()
                console.print("[green]Local conversation history cleared.[/]")
                continue
            if user_input.lower() == '@deepseek clear':
                for handler in processor.handlers:
                    if isinstance(handler, DeepSeekAnalysisHandler):
                        handler.clear_history()
                console.print("[green]DeepSeek conversation history cleared.[/]")
                continue

            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                TextColumn("({task.elapsed:.2f}s)"),
                console=console,
                transient=True
            ) as progress:
                task_id = progress.add_task("", total=None)
                
                # Run the AI execution in a separate thread
                response = None
                def ai_task():
                    nonlocal response
                    response = processor.execute(user_input)

                ai_thread = threading.Thread(target=ai_task)
                ai_thread.start()

                # And run the silly message updater in another thread
                stop_silly_updater = threading.Event()
                def silly_updater():
                    while not stop_silly_updater.is_set():
                        color, message = get_silly_message()
                        progress.update(task_id, description=f"[{color}]{message}[/]")
                        time.sleep(7)
                
                silly_thread = threading.Thread(target=silly_updater, daemon=True)
                silly_thread.start()

                # Keep the main thread responsive for the timer
                while ai_thread.is_alive():
                    time.sleep(0.1)

                stop_silly_updater.set()
                ai_thread.join()
                final_message = progress.tasks[task_id].description
                progress.stop_task(task_id)
                total_time = progress.tasks[task_id].elapsed
                
                console.print("\n🤖 [bold]Assistant:[/]")
                console.print(f"{final_message} ({total_time:.2f}s)")
                console.print(Panel(Markdown(response), title=f"🤖 {ctx.model_name}", border_style="#9c9a9a"))

        except (KeyboardInterrupt, EOFError):
            if 'ai_thread' in locals() and ai_thread.is_alive():
                # Give the AI thread a moment to finish
                ai_thread.join(timeout=1.0)
            
            # Save session histories on exit
            for handler in processor.handlers:
                if hasattr(handler, '_save_history'):
                    handler._save_history()

            console.print("\n[bold]Session ended[/]")
            break

if __name__ == "__main__":
    main()