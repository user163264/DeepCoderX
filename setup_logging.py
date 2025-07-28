#!/usr/bin/env python3
"""
Enhanced Model Logging Setup Script for DeepCoderX

This script provides easy configuration of the enhanced model logging system
with predefined profiles for different use cases.
"""

import os
import sys
from pathlib import Path
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

console = Console()

# Logging configuration profiles
LOGGING_PROFILES = {
    "development": {
        "name": "Development (Full Logging)",
        "description": "Complete logging for debugging and development",
        "variables": {
            "DEEPCODERX_LOG_MODEL_PROMPTS": "true",
            "DEEPCODERX_LOG_MODEL_RESPONSES": "true",
            "DEEPCODERX_LOG_SEMANTIC_DETAILS": "true",
            "DEEPCODERX_LOG_TOOL_DETAILS": "true",
            "DEEPCODERX_LOG_CONVERSATION_CONTEXT": "true",
            "DEEPCODERX_LOG_INTERACTION_TRACKING": "true",
            "DEEPCODERX_LOG_STRUCTURED_STORAGE": "true"
        }
    },
    "debugging": {
        "name": "Debugging (Critical Only)",
        "description": "Log only critical information for debugging issues",
        "variables": {
            "DEEPCODERX_LOG_MODEL_PROMPTS": "true",
            "DEEPCODERX_LOG_MODEL_RESPONSES": "true",
            "DEEPCODERX_LOG_SEMANTIC_DETAILS": "true",
            "DEEPCODERX_LOG_TOOL_DETAILS": "false",
            "DEEPCODERX_LOG_CONVERSATION_CONTEXT": "false",
            "DEEPCODERX_LOG_INTERACTION_TRACKING": "true",
            "DEEPCODERX_LOG_STRUCTURED_STORAGE": "true"
        }
    },
    "performance": {
        "name": "Performance Analysis",
        "description": "Log performance metrics and interaction summaries",
        "variables": {
            "DEEPCODERX_LOG_MODEL_PROMPTS": "false",
            "DEEPCODERX_LOG_MODEL_RESPONSES": "false",
            "DEEPCODERX_LOG_SEMANTIC_DETAILS": "false",
            "DEEPCODERX_LOG_TOOL_DETAILS": "false",
            "DEEPCODERX_LOG_CONVERSATION_CONTEXT": "false",
            "DEEPCODERX_LOG_INTERACTION_TRACKING": "true",
            "DEEPCODERX_LOG_STRUCTURED_STORAGE": "true"
        }
    },
    "production": {
        "name": "Production (Minimal)",
        "description": "Minimal logging for production environments",
        "variables": {
            "DEEPCODERX_LOG_MODEL_PROMPTS": "false",
            "DEEPCODERX_LOG_MODEL_RESPONSES": "false",
            "DEEPCODERX_LOG_SEMANTIC_DETAILS": "false",
            "DEEPCODERX_LOG_TOOL_DETAILS": "false",
            "DEEPCODERX_LOG_CONVERSATION_CONTEXT": "false",
            "DEEPCODERX_LOG_INTERACTION_TRACKING": "true",
            "DEEPCODERX_LOG_STRUCTURED_STORAGE": "false"
        }
    },
    "off": {
        "name": "Logging Disabled",
        "description": "Disable all enhanced logging",
        "variables": {
            "DEEPCODERX_LOG_MODEL_PROMPTS": "false",
            "DEEPCODERX_LOG_MODEL_RESPONSES": "false",
            "DEEPCODERX_LOG_SEMANTIC_DETAILS": "false",
            "DEEPCODERX_LOG_TOOL_DETAILS": "false",
            "DEEPCODERX_LOG_CONVERSATION_CONTEXT": "false",
            "DEEPCODERX_LOG_INTERACTION_TRACKING": "false",
            "DEEPCODERX_LOG_STRUCTURED_STORAGE": "false"
        }
    }
}

def show_current_configuration():
    """Display current logging configuration."""
    console.print("[bold blue]Current Logging Configuration[/bold blue]")
    
    table = Table(title="Environment Variables")
    table.add_column("Variable", style="cyan")
    table.add_column("Value", style="green")
    table.add_column("Status", style="yellow")
    
    for profile_name, profile in LOGGING_PROFILES.items():
        if profile_name == "off":
            continue
        for var_name in profile["variables"].keys():
            current_value = os.getenv(var_name, "not set")
            status = "✅ Set" if current_value != "not set" else "❌ Not Set"
            table.add_row(var_name.replace("DEEPCODERX_LOG_", ""), current_value, status)
    
    console.print(table)

def show_available_profiles():
    """Display available logging profiles."""
    console.print("[bold blue]Available Logging Profiles[/bold blue]")
    
    for profile_id, profile in LOGGING_PROFILES.items():
        # Create profile panel
        enabled_count = sum(1 for value in profile["variables"].values() if value == "true")
        total_count = len(profile["variables"])
        
        profile_info = f"[bold]{profile['name']}[/bold]\\n"
        profile_info += f"{profile['description']}\\n"
        profile_info += f"Enabled features: {enabled_count}/{total_count}"
        
        console.print(Panel(profile_info, title=f"Profile: {profile_id}", border_style="cyan"))

def apply_profile(profile_id: str):
    """Apply a logging profile by setting environment variables."""
    if profile_id not in LOGGING_PROFILES:
        console.print(f"[bold red]❌ Unknown profile: {profile_id}[/bold red]")
        return False
    
    profile = LOGGING_PROFILES[profile_id]
    console.print(f"[bold green]🔧 Applying profile: {profile['name']}[/bold green]")
    console.print(f"Description: {profile['description']}")
    
    # Set environment variables
    for var_name, var_value in profile["variables"].items():
        os.environ[var_name] = var_value
        console.print(f"  ✅ {var_name}={var_value}")
    
    console.print(f"[bold green]✅ Profile '{profile_id}' applied successfully![/bold green]")
    console.print("[yellow]Note: These settings apply only to the current session.[/yellow]")
    console.print("[yellow]For persistent settings, add to your shell profile (.bashrc, .zshrc, etc.)[/yellow]")
    
    return True

def generate_export_commands(profile_id: str):
    """Generate export commands for shell configuration."""
    if profile_id not in LOGGING_PROFILES:
        console.print(f"[bold red]❌ Unknown profile: {profile_id}[/bold red]")
        return
    
    profile = LOGGING_PROFILES[profile_id]
    console.print(f"[bold blue]Shell Export Commands for '{profile['name']}'[/bold blue]")
    console.print("Add these lines to your shell profile (.bashrc, .zshrc, etc.):\\n")
    
    console.print("```bash")
    console.print(f"# DeepCoderX Enhanced Logging - {profile['name']}")
    for var_name, var_value in profile["variables"].items():
        console.print(f"export {var_name}={var_value}")
    console.print("```")

def test_configuration():
    """Test the current logging configuration."""
    console.print("[bold blue]🧪 Testing Current Logging Configuration[/bold blue]")
    
    try:
        # Import logging functions to test
        sys.path.insert(0, str(Path(__file__).parent))
        from utils.logging import get_model_interactions_summary, MODEL_INTERACTIONS_DIR
        
        # Test directory access
        if MODEL_INTERACTIONS_DIR.exists():
            console.print(f"✅ Model interactions directory: {MODEL_INTERACTIONS_DIR}")
        else:
            console.print(f"❌ Model interactions directory not found: {MODEL_INTERACTIONS_DIR}")
            return False
        
        # Test configuration import
        try:
            from config_module import DEBUG_LOGGING
            console.print("✅ Debug logging configuration imported successfully")
            
            # Show current settings
            enabled_features = [key for key, value in DEBUG_LOGGING.items() if value is True]
            console.print(f"✅ Enabled features: {', '.join(enabled_features) if enabled_features else 'None'}")
            
        except ImportError as e:
            console.print(f"❌ Failed to import configuration: {e}")
            return False
        
        # Test log summary
        try:
            summary = get_model_interactions_summary()
            console.print(f"✅ Log summary generated: {len(summary.get('log_files', {}))} files tracked")
        except Exception as e:
            console.print(f"❌ Log summary failed: {e}")
            return False
        
        console.print("[bold green]🎉 Configuration test passed![/bold green]")
        return True
        
    except Exception as e:
        console.print(f"[bold red]❌ Configuration test failed: {e}[/bold red]")
        return False

def main():
    """Main setup interface."""
    console.print("[bold green]🔧 Enhanced Model Logging Setup for DeepCoderX[/bold green]")
    console.print()
    
    if len(sys.argv) < 2:
        console.print("Usage: python3 setup_logging.py <command> [options]")
        console.print()
        console.print("Commands:")
        console.print("  show-current    Display current configuration")
        console.print("  show-profiles   Display available profiles")
        console.print("  apply <profile> Apply a logging profile")
        console.print("  export <profile> Generate shell export commands")
        console.print("  test           Test current configuration")
        console.print()
        console.print("Available profiles:", ", ".join(LOGGING_PROFILES.keys()))
        return 1
    
    command = sys.argv[1].lower()
    
    if command == "show-current":
        show_current_configuration()
        
    elif command == "show-profiles":
        show_available_profiles()
        
    elif command == "apply":
        if len(sys.argv) < 3:
            console.print("[bold red]❌ Profile name required[/bold red]")
            console.print("Available profiles:", ", ".join(LOGGING_PROFILES.keys()))
            return 1
        profile_id = sys.argv[2].lower()
        apply_profile(profile_id)
        
    elif command == "export":
        if len(sys.argv) < 3:
            console.print("[bold red]❌ Profile name required[/bold red]")
            console.print("Available profiles:", ", ".join(LOGGING_PROFILES.keys()))
            return 1
        profile_id = sys.argv[2].lower()
        generate_export_commands(profile_id)
        
    elif command == "test":
        test_configuration()
        
    else:
        console.print(f"[bold red]❌ Unknown command: {command}[/bold red]")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())
