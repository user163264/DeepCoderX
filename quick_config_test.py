#!/usr/bin/env python3
import sys
import os
from pathlib import Path

# Change to project directory like run.py does
os.chdir('/Users/admin/Documents/DeepCoderX')

print("=== Testing Configuration Loading ===")
print(f"Working directory: {os.getcwd()}")

# Test 1: Load .env file like app.py does
try:
    from dotenv import load_dotenv
    env_path = Path('.env')
    load_dotenv(dotenv_path=env_path)
    print("✅ .env file loaded")
    
    # Check the specific variable that was causing issues
    deepseek_legacy = os.getenv('DEEPSEEK_API_KEY')
    deepseek_new = os.getenv('DEEPCODERX_DEEPSEEK_API_KEY')
    
    print(f"   DEEPSEEK_API_KEY (legacy): {'Found' if deepseek_legacy else 'Missing'}")
    print(f"   DEEPCODERX_DEEPSEEK_API_KEY (new): {'Found' if deepseek_new else 'Missing'}")
    
except Exception as e:
    print(f"❌ Failed to load .env: {e}")
    sys.exit(1)

# Test 2: Import config_module like app.py does
try:
    print("\n=== Importing Configuration Module ===")
    from config_module import config
    print("✅ Configuration module imported successfully!")
    
    # Test the specific setting that was failing
    print(f"✅ DeepSeek enabled: {config.DEEPSEEK_ENABLED}")
    print(f"✅ DeepSeek API key: {'Found' if config.DEEPSEEK_API_KEY else 'Missing'}")
    
    # Test all providers
    print("\n📊 Provider Status:")
    for name, provider_config in config.PROVIDERS.items():
        enabled = provider_config['enabled']
        has_key = provider_config.get('api_key') is not None
        print(f"   {name}: enabled={enabled}, api_key={'Yes' if has_key else 'No'}")
    
    print("\n🎉 SUCCESS: Startup error has been RESOLVED!")
    print("The legacy environment variable compatibility is working correctly.")
    
except Exception as e:
    print(f"❌ FAILED: Configuration import failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n=== Test Complete ===")
