#!/usr/bin/env python3
"""
Simple test to isolate configuration loading issue.
Tests the exact import that was failing with environment variables.
"""

import sys
import os
from pathlib import Path

# Change to the project directory (same as run.py does)
os.chdir(Path(__file__).parent)

print("=== DeepCoderX Configuration Test ===")
print(f"Working directory: {os.getcwd()}")
print(f"Python path: {sys.path[0]}")

# Test 1: Check .env file exists and load it
env_path = Path('.env')
if env_path.exists():
    print("✅ .env file found")
    with open(env_path, 'r') as f:
        env_content = f.read()
    print("📋 Environment variables in .env:")
    for line in env_content.strip().split('\n'):
        if line.strip() and not line.startswith('#'):
            key = line.split('=')[0] if '=' in line else line
            print(f"   - {key}")
else:
    print("❌ .env file not found")

# Test 2: Load .env file
print("\n=== Loading .env file ===")
try:
    from dotenv import load_dotenv
    load_dotenv(dotenv_path=env_path)
    print("✅ .env file loaded")
    
    # Check key environment variables
    test_vars = ['DEEPSEEK_API_KEY', 'DEEPCODERX_DEEPSEEK_API_KEY', 'SANDBOX_PATH', 'DEEPCODERX_SANDBOX_PATH']
    for var in test_vars:
        value = os.getenv(var)
        if value:
            print(f"✅ {var} = {value[:10]}..." if len(value) > 10 else f"✅ {var} = {value}")
        else:
            print(f"❌ {var} not found")
            
except Exception as e:
    print(f"❌ Failed to load .env: {e}")

# Test 3: Try to import configuration (this is where the error occurred)
print("\n=== Testing Configuration Import ===")
try:
    from config_module import config
    print("✅ Configuration module imported successfully!")
    
    # Test specific problematic settings
    print(f"✅ DeepSeek API Key: {'Found' if config.DEEPSEEK_API_KEY else 'Missing'}")
    print(f"✅ DeepSeek Enabled: {config.DEEPSEEK_ENABLED}")
    print(f"✅ Sandbox Path: {config.SANDBOX_PATH}")
    print(f"✅ Default Provider: {config.DEFAULT_PROVIDER}")
    
    # Test provider availability
    print("\n📊 Provider Status:")
    for provider_name in config.PROVIDERS:
        available = config.is_provider_available(provider_name)
        enabled = config.PROVIDERS[provider_name]['enabled']
        print(f"   {provider_name}: enabled={enabled}, available={available}")
    
    print(f"\n🎉 SUCCESS: Configuration loaded without startup error!")
    
except Exception as e:
    print(f"❌ FAILED: Configuration import failed: {e}")
    import traceback
    print("\nFull traceback:")
    traceback.print_exc()

print("\n=== Test Complete ===")
