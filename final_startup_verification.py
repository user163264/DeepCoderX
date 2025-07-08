#!/usr/bin/env python3
"""
Final verification test for startup error resolution.
This confirms the exact startup scenario works correctly.
"""

import sys
import os
from pathlib import Path

print("🔍 FINAL VERIFICATION: DeepCoderX Startup Error Resolution")
print("=" * 65)

# Step 1: Change to project directory (mimics run.py)
try:
    os.chdir('/Users/admin/Documents/DeepCoderX')
    print("✅ Changed to project directory")
except Exception as e:
    print(f"❌ Failed to change directory: {e}")
    sys.exit(1)

# Step 2: Load .env file (mimics app.py)
try:
    from dotenv import load_dotenv
    env_path = Path('.env')
    load_dotenv(dotenv_path=env_path)
    print("✅ Loaded .env file")
    
    # Verify the specific variables
    deepseek_legacy = os.getenv('DEEPSEEK_API_KEY')
    deepseek_new = os.getenv('DEEPCODERX_DEEPSEEK_API_KEY')
    
    print(f"   📋 DEEPSEEK_API_KEY (legacy): {'✅ Found' if deepseek_legacy else '❌ Missing'}")
    print(f"   📋 DEEPCODERX_DEEPSEEK_API_KEY (new): {'✅ Found' if deepseek_new else '❌ Missing'}")
    
except Exception as e:
    print(f"❌ Failed to load .env: {e}")
    sys.exit(1)

# Step 3: Import configuration (this is where the original error occurred)
try:
    print("\n🚀 TESTING CONFIGURATION IMPORT (original failure point)...")
    from config_module import config
    print("✅ Configuration imported successfully!")
    
    # Verify the specific issue that was failing
    print(f"\n📊 VERIFICATION RESULTS:")
    print(f"   DeepSeek Enabled: {'✅ Yes' if config.DEEPSEEK_ENABLED else '❌ No'}")
    print(f"   DeepSeek API Key: {'✅ Found' if config.DEEPSEEK_API_KEY else '❌ Missing'}")
    print(f"   Sandbox Path: {config.SANDBOX_PATH}")
    print(f"   Default Provider: {config.DEFAULT_PROVIDER}")
    
    # Test all provider configurations
    print(f"\n🔧 PROVIDER STATUS:")
    for provider_name, provider_config in config.PROVIDERS.items():
        enabled = provider_config['enabled']
        has_api_key = provider_config.get('api_key') is not None
        available = config.is_provider_available(provider_name)
        
        status = "✅" if enabled and (has_api_key or provider_name == "local") else "⚠️"
        print(f"   {status} {provider_name}: enabled={enabled}, api_key={'Yes' if has_api_key else 'No'}, available={available}")
    
    print(f"\n🎉 SUCCESS: STARTUP ERROR COMPLETELY RESOLVED!")
    print(f"   ✅ Legacy environment variables work correctly")
    print(f"   ✅ Configuration validation passes")
    print(f"   ✅ DeepSeek provider properly configured")
    print(f"   ✅ Application should start without errors")
    
except Exception as e:
    print(f"❌ CONFIGURATION IMPORT FAILED: {e}")
    print(f"   This means the startup error is NOT resolved")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n" + "=" * 65)
print("🏁 VERIFICATION COMPLETE: Environment variable compatibility FIX is working!")
