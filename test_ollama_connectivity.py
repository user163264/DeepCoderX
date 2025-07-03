#!/usr/bin/env python3
"""
Test script to verify Ollama endpoint connectivity and OpenAI compatibility.
This is the first step in validating the new unified OpenAI architecture.
"""

import os
import sys
import requests
import json
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from config import config
from rich.console import Console

console = Console()

def test_ollama_endpoint():
    """Test Ollama endpoint connectivity at localhost:11434/v1"""
    console.print("[bold blue]Testing Ollama Endpoint Connectivity[/]")
    console.print("=" * 50)
    
    ollama_config = config.PROVIDERS.get("local")
    if not ollama_config:
        console.print("[red]❌ No local provider configuration found[/]")
        return False
    
    base_url = ollama_config["base_url"]
    console.print(f"[blue]Testing endpoint:[/] {base_url}")
    
    # Test 1: Basic connectivity
    try:
        response = requests.get(f"{base_url.rstrip('/v1')}/api/tags", timeout=5)
        if response.status_code == 200:
            console.print("[green]✓ Ollama server is running[/]")
            models = response.json().get("models", [])
            console.print(f"[green]✓ Available models: {len(models)}[/]")
            for model in models[:3]:  # Show first 3 models
                console.print(f"  - {model.get('name', 'Unknown')}")
        else:
            console.print(f"[red]❌ Ollama server responded with status {response.status_code}[/]")
            return False
    except requests.exceptions.RequestException as e:
        console.print(f"[red]❌ Cannot connect to Ollama server: {e}[/]")
        console.print("[yellow]Make sure Ollama is running: `ollama serve`[/]")
        return False
    
    # Test 2: OpenAI compatibility endpoint
    try:
        models_response = requests.get(f"{base_url}/models", timeout=5)
        if models_response.status_code == 200:
            console.print("[green]✓ OpenAI-compatible /v1/models endpoint working[/]")
            openai_models = models_response.json().get("data", [])
            console.print(f"[green]✓ OpenAI format models: {len(openai_models)}[/]")
        else:
            console.print(f"[yellow]⚠ OpenAI /v1/models endpoint returned {models_response.status_code}[/]")
    except requests.exceptions.RequestException as e:
        console.print(f"[red]❌ OpenAI compatibility endpoint failed: {e}[/]")
        return False
    
    # Test 3: Chat completions endpoint
    test_model = ollama_config["model"]
    console.print(f"[blue]Testing chat completions with model:[/] {test_model}")
    
    try:
        chat_data = {
            "model": test_model,
            "messages": [
                {"role": "user", "content": "Hello, respond with just 'OK' if you can understand this."}
            ],
            "max_tokens": 10,
            "temperature": 0.1
        }
        
        chat_response = requests.post(
            f"{base_url}/chat/completions",
            json=chat_data,
            timeout=30
        )
        
        if chat_response.status_code == 200:
            response_data = chat_response.json()
            message_content = response_data.get("choices", [{}])[0].get("message", {}).get("content", "")
            console.print(f"[green]✓ Chat completions working. Response: '{message_content.strip()}'[/]")
            return True
        else:
            console.print(f"[red]❌ Chat completions failed with status {chat_response.status_code}[/]")
            console.print(f"Response: {chat_response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        console.print(f"[red]❌ Chat completions request failed: {e}[/]")
        return False

def test_openai_client_import():
    """Test if OpenAI client can be imported and configured"""
    console.print("\n[bold blue]Testing OpenAI Client Import[/]")
    console.print("=" * 50)
    
    try:
        from openai import OpenAI
        console.print("[green]✓ OpenAI client library imported successfully[/]")
        
        # Test client initialization
        client = OpenAI(
            base_url=config.PROVIDERS["local"]["base_url"],
            api_key=config.PROVIDERS["local"]["api_key"]
        )
        console.print("[green]✓ OpenAI client configured for Ollama[/]")
        return True
        
    except ImportError as e:
        console.print(f"[red]❌ Cannot import OpenAI client: {e}[/]")
        console.print("[yellow]Run: pip install openai>=1.0.0[/]")
        return False
    except Exception as e:
        console.print(f"[red]❌ Error configuring OpenAI client: {e}[/]")
        return False

def test_unified_handler_import():
    """Test if unified handlers can be imported"""
    console.print("\n[bold blue]Testing Unified Handler Import[/]")
    console.print("=" * 50)
    
    try:
        from services.unified_openai_handler import LocalOpenAIHandler, CloudOpenAIHandler
        console.print("[green]✓ Unified OpenAI handlers imported successfully[/]")
        return True
    except ImportError as e:
        console.print(f"[red]❌ Cannot import unified handlers: {e}[/]")
        return False
    except Exception as e:
        console.print(f"[red]❌ Error with unified handlers: {e}[/]")
        return False

def main():
    """Run all connectivity tests"""
    console.print("[bold magenta]DeepCoderX - OpenAI Integration Test Suite[/]")
    console.print("=" * 60)
    
    tests = [
        ("Ollama Endpoint", test_ollama_endpoint),
        ("OpenAI Client", test_openai_client_import),
        ("Unified Handlers", test_unified_handler_import)
    ]
    
    results = {}
    for test_name, test_func in tests:
        results[test_name] = test_func()
    
    # Summary
    console.print("\n[bold blue]Test Results Summary[/]")
    console.print("=" * 50)
    
    all_passed = True
    for test_name, passed in results.items():
        status = "[green]✓ PASS[/]" if passed else "[red]❌ FAIL[/]"
        console.print(f"{test_name:<20} {status}")
        if not passed:
            all_passed = False
    
    console.print()
    if all_passed:
        console.print("[bold green]🎉 All tests passed! OpenAI integration is ready.[/]")
        console.print("[green]You can now proceed with testing native tool calling.[/]")
    else:
        console.print("[bold red]❌ Some tests failed. Please fix the issues before proceeding.[/]")
        console.print("[yellow]Common fixes:[/]")
        console.print("- Start Ollama: `ollama serve`")
        console.print("- Install OpenAI: `pip install openai>=1.0.0`")
        console.print("- Pull a model: `ollama pull qwen2.5-coder:1.5b`")
    
    return all_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
