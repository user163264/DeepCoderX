#!/usr/bin/env python3
"""
Test script to verify DeepCoderX configuration loading.
This tests if the startup error with environment variables has been resolved.
"""

import sys
import os
from pathlib import Path

# Add the project root to the Python path
project_root = Path.cwd()
sys.path.insert(0, str(project_root))

try:
    # Try to import and initialize the configuration
    print("Loading DeepCoderX configuration...")
    from config_module import config
    
    print("✅ Configuration loaded successfully!")
    print(f"✅ DeepSeek API Key found: {'Yes' if config.DEEPSEEK_API_KEY else 'No'}")
    print(f"✅ OpenAI API Key found: {'Yes' if config.PROVIDERS['openai']['api_key'] else 'No'}")
    print(f"✅ Sandbox Path: {config.SANDBOX_PATH}")
    print(f"✅ MCP API Key: {config.MCP_API_KEY}")
    
    # Check specific providers
    for provider_name, provider_config in config.PROVIDERS.items():
        enabled = provider_config['enabled']
        available = config.is_provider_available(provider_name)
        print(f"✅ Provider '{provider_name}': enabled={enabled}, available={available}")
    
    print("\n" + config.get_current_config_summary())
    
except Exception as e:
    print(f"❌ Configuration failed: {e}")
    import traceback
    traceback.print_exc()
