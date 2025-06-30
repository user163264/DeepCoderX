import pytest
import sys
from rich.console import Console

console = Console()

def main():
    """Runs the full pytest suite with a user-friendly interface."""
    console.print("\n[bold cyan]🚀 Running DeepCoderX Test Suite...[/bold cyan]")
    console.print("=========================================")

    # pytest.main will exit the process, so we capture the result
    result = pytest.main(["-v", "--disable-warnings"])

    console.print("=========================================")
    if result == 0:
        console.print("[bold green]✅ All tests passed successfully![/bold green]")
    else:
        console.print(f"[bold red]❌ Tests failed with exit code: {result}[/bold red]")
    
    # Exit with the same code as pytest
    sys.exit(result)

if __name__ == "__main__":
    main()
