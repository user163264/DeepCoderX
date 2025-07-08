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

from config_module import config
from models.session import CommandContext
from models.router import CommandProcessor, CommandHandler
from services.llm_handler import (
    SecurityMiddleware, 
    FilesystemCommandHandler,
    AutoImplementHandler
)

# Import unified OpenAI-compatible handlers and GGUF handler
try:
    from services.unified_openai_handler import LocalOpenAIHandler, CloudOpenAIHandler
    from services.gguf_handler import GGUFLocalHandler
    OPENAI_HANDLERS_AVAILABLE = True
    GGUF_HANDLER_AVAILABLE = True
    OPENAI_IMPORT_ERROR = None
except ImportError as e:
    OPENAI_HANDLERS_AVAILABLE = False
    GGUF_HANDLER_AVAILABLE = False
    OPENAI_IMPORT_ERROR = str(e)

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
    
    # MIGRATION COMPLETED: Unified Architecture Only
    if not OPENAI_HANDLERS_AVAILABLE:
        console.print(f"[red]Error:[/] OpenAI handlers not available: {OPENAI_IMPORT_ERROR}")
        console.print("[red]DeepCoderX requires OpenAI client. Run: pip install openai>=1.0.0[/]")
        console.print("[red]Legacy handlers have been removed in this version.[/]")
        return
        
    if not GGUF_HANDLER_AVAILABLE:
        console.print("[yellow]Warning:[/] GGUF handler not available. GGUF models may not work properly.")
    
    try:
        # UNIFIED ARCHITECTURE: All AI interactions use unified handlers
        # Register all available provider handlers based on model_type
        enabled_providers = [name for name, cfg in config.PROVIDERS.items() if cfg['enabled']]
        
        for provider_name in enabled_providers:
            provider_config = config.PROVIDERS[provider_name]
            model_type = provider_config.get('model_type', 'openai')
            
            if model_type == 'gguf':
                # Use GGUF handler for GGUF models
                if GGUF_HANDLER_AVAILABLE:
                    processor.add_handler(GGUFLocalHandler(ctx, provider_name))
                    if ctx.debug_mode:
                        console.print(f"[bold blue]✅ Registered GGUF handler for {provider_name}[/]")
                else:
                    console.print(f"[red]Error:[/] GGUF handler not available for {provider_name}")
            elif model_type in ['openai', 'openai_local']:
                # Use OpenAI-compatible handlers
                if provider_name in ['deepseek', 'openai']:
                    processor.add_handler(CloudOpenAIHandler(ctx, provider_name))
                    if ctx.debug_mode:
                        console.print(f"[bold green]✅ Registered cloud handler for {provider_name}[/]")
                else:
                    processor.add_handler(LocalOpenAIHandler(ctx))
                    if ctx.debug_mode:
                        console.print(f"[bold cyan]✅ Registered local OpenAI handler for {provider_name}[/]")
            else:
                console.print(f"[yellow]Warning:[/] Unknown model_type '{model_type}' for provider '{provider_name}'")
        
        # Add AutoImplementHandler for code implementation
        processor.add_handler(AutoImplementHandler(ctx))
        
        if ctx.debug_mode:
            console.print("[bold green]✅ MIGRATION COMPLETED: Unified Architecture + GGUF Support Active[/]")
            console.print(f"[green]✅ Enabled providers: {', '.join(enabled_providers)}[/]")
            console.print(f"[green]✅ Default provider: {config.DEFAULT_PROVIDER}[/]")
            console.print("[dim]All legacy handlers migrated + GGUF tool calling implemented[/]")
            
    except Exception as e:
        console.print(f"[red]Fatal Error:[/] Failed to initialize unified handlers: {e}")
        console.print("[red]Please check your configuration and try again.[/]")
        return

    # Add a fallback handler for unknown commands
    class NotFoundHandler(CommandHandler):
        def can_handle(self) -> bool:
            return True
        def handle(self) -> None:
            self.ctx.response = f"[red]Error:[/] Command not found: {self.ctx.user_input}"
    processor.add_handler(NotFoundHandler(ctx))

    # Display the startup logo
    logo = Text(r"""

#  ██████╗ ███████╗███████╗██████╗  ██████╗ ██████╗ ██████╗ ███████╗██████╗ ██╗  ██╗
#  ██╔══██╗██╔════╝██╔════╝██╔══██╗██╔════╝██╔═══██╗██╔══██╗██╔════╝██╔══██╗╚██╗██╔╝
#  ██║  ██║█████╗  █████╗  ██████╔╝██║     ██║   ██║██║  ██║█████╗  ██████╔╝ ╚███╔╝ 
#  ██║  ██║██╔══╝  ██╔══╝  ██╔═══╝ ██║     ██║   ██║██║  ██║██╔══╝  ██╔══██╗ ██╔██╗ 
#  ██████╔╝███████╗███████╗██║     ╚██████╗╚██████╔╝██████╔╝███████╗██║  ██║██╔╝ ██╗
#  ╚═════╝ ╚══════╝╚══════╝╚═╝      ╚═════╝ ╚═════╝ ╚═════╝ ╚══════╝╚═╝  ╚═╝╚═╝  ╚═╝
#                                                                                   
            """, justify="center", style="bold magenta")
    console.print(Panel(logo, border_style="#9c9a9a"))
    
    # Create status message with provider info and migration status
    enabled_providers = [name for name, cfg in config.PROVIDERS.items() if cfg['enabled']]
    status_parts = [
        f"[bold]DeepCoderX[/] | [green]Project:[/] {project_dir.name}",
        f"[blue]Providers:[/] {', '.join(enabled_providers)}",
        f"[yellow]Default:[/] {config.DEFAULT_PROVIDER}",
        "[green]Architecture:[/] Unified ✅"
    ]
    
    console.print(Panel(
        " | ".join(status_parts),
        border_style="#9c9a9a"
    ))
    
    # Migration completed notification
    console.print("[bold green]🎉 LEGACY MIGRATION + GGUF TOOL CALLING COMPLETED![/]")
    console.print("[dim]• All handlers use unified OpenAI architecture")
    console.print("[dim]• Tool Registry Pattern active")
    console.print("[dim]• Standardized error handling")
    console.print("[dim]• GGUF models support tool calling via manual prompting")
    console.print("[dim]• OpenAI-compatible models use native tool calling")
    console.print("[dim]• Complete OpenAPI 3.1 MCP File System support[/]")
    
    console.print("[dim]Type 'exit' or 'quit' to end the session.[/]")

    while True:
        try:
            user_input = console.input("\n👤 [bold]You:[/] ").strip()
            if not user_input:
                continue
            if user_input.lower() in ('exit', 'quit'):
                raise KeyboardInterrupt
            if user_input.lower() == 'clear':
                cleared_handlers = []
                for handler in processor.handlers:
                    if hasattr(handler, 'clear_history'):
                        handler.clear_history()
                        cleared_handlers.append(type(handler).__name__)
                if cleared_handlers:
                    console.print(f"[green]Conversation history cleared for: {', '.join(cleared_handlers)}[/]")
                else:
                    console.print("[yellow]No handlers with conversation history found.[/]")
                continue
            
            # Handle provider-specific clear commands
            if user_input.lower().startswith('@') and 'clear' in user_input.lower():
                provider_name = user_input.lower().split()[0][1:]  # Remove @ and get provider name
                cleared = False
                for handler in processor.handlers:
                    if hasattr(handler, 'provider_name') and handler.provider_name == provider_name:
                        handler.clear_history()
                        console.print(f"[green]{provider_name.title()} conversation history cleared.[/]")
                        cleared = True
                        break
                    # Also check for GGUF handlers that may use context_manager
                    elif hasattr(handler, 'context_manager') and hasattr(handler, 'provider_name') and handler.provider_name == provider_name:
                        handler.clear_history()
                        console.print(f"[green]{provider_name.title()} GGUF conversation history cleared.[/]")
                        cleared = True
                        break
                if not cleared:
                    console.print(f"[yellow]No {provider_name} handler found.[/]")
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
