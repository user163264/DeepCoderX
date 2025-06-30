# code_utils.py

import re
import pyperclip
from pygments import highlight
from pygments.lexers import GoLexer, BashLexer, PythonLexer
from pygments.formatters.terminal256 import Terminal256Formatter
from rich.text import Text
from rich.console import Console

console = Console()

def highlight_go(code):
    return highlight(code, GoLexer(), Terminal256Formatter())

def highlight_bash(code):
    return highlight(code, BashLexer(), Terminal256Formatter())

def highlight_python(code):
    return highlight(code, PythonLexer(), Terminal256Formatter())

def copy_to_clipboard(code):
    try:
        pyperclip.copy(strip_ansi(code))
        console.print("[green]📋 Copied code to clipboard[/green]")
    except Exception as e:
        console.print(f"[red]⚠️ Could not copy to clipboard: {e}[/red]")

def extract_codeblock(text):
    """Extract code from markdown code blocks"""
    for lang in ["python", "bash", "go", "javascript", "typescript", "java"]:
        pattern = f"```{lang}(.*?)```"
        match = re.search(pattern, text, re.DOTALL)
        if match:
            return match.group(1).strip()
    return None