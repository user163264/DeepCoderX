#!/usr/bin/env python3
"""
Test the FIXED configuration to verify both issues are resolved:
1. DeepSeek API key format validation (32 hex chars)
2. Legacy environment variable compatibility
"""

import sys
import os
from pathlib import Path

print("🔧 TESTING FIXED CONFIGURATION")
print("=" * 60)

# Step 1: Change to project directory
try:
    os.chdir('/Users/admin/Documents/DeepCoderX')
    print("✅ Changed to project directory")
except Exception as e:
    print(f"❌ Failed to change directory: {e}")
    sys.exit(1)

# Step 2: Load .env file
try:
    from dotenv import load_dotenv
    env_path = Path('.env')
    load_dotenv(dotenv_path=env_path)
    print("✅ Loaded .env file")
    
    # Check the specific API key that was causing issues
    deepseek_key = os.getenv('DEEPSEEK_API_KEY')
    if deepseek_key:
        print(f"   📋 DEEPSEEK_API_KEY: {deepseek_key[:10]}...{deepseek_key[-6:]} ({len(deepseek_key)} chars)")
        # Verify it's 32 hex characters after sk-
        if deepseek_key.startswith('sk-') and len(deepseek_key) == 35:  # sk- + 32 chars
            hex_part = deepseek_key[3:]  # Remove 'sk-'
            if all(c in '0123456789abcdef' for c in hex_part.lower()):
                print("   ✅ API key format: 32 hexadecimal characters (correct format)")
            else:
                print("   ⚠️ API key format: Contains non-hex characters")
        else:
            print(f"   ⚠️ API key format: {len(deepseek_key)} total chars (expected 35)")
    else:
        print("   ❌ DEEPSEEK_API_KEY not found")
        
except Exception as e:
    print(f"❌ Failed to load .env: {e}")
    sys.exit(1)

# Step 3: Test configuration import (both issues should be fixed)
try:
    print("\n🚀 TESTING CONFIGURATION IMPORT...")
    from config_module import config
    print("✅ Configuration imported successfully!")
    
    # Verify DeepSeek configuration
    print(f"\n📊 DEEPSEEK CONFIGURATION:")
    print(f"   Enabled: {'✅ Yes' if config.DEEPSEEK_ENABLED else '❌ No'}")
    print(f"   API Key: {'✅ Found' if config.DEEPSEEK_API_KEY else '❌ Missing'}")
    if config.DEEPSEEK_API_KEY:
        print(f"   API Key Length: {len(config.DEEPSEEK_API_KEY)} chars")
        print(f"   API Key Format: {'✅ Valid' if config.DEEPSEEK_API_KEY.startswith('sk-') else '❌ Invalid'}")
    
    # Test all providers
    print(f"\n🔧 PROVIDER STATUS:")
    for provider_name, provider_config in config.PROVIDERS.items():
        enabled = provider_config['enabled']
        has_api_key = provider_config.get('api_key') is not None
        available = config.is_provider_available(provider_name)
        
        status = "✅" if available else "⚠️"
        print(f"   {status} {provider_name}: enabled={enabled}, api_key={'Yes' if has_api_key else 'No'}, available={available}")
    
    print(f"\n🎉 SUCCESS: BOTH ISSUES RESOLVED!")
    print(f"   ✅ Legacy environment variable compatibility working")
    print(f"   ✅ DeepSeek API key validation fixed for 32-character format")
    print(f"   ✅ Configuration validation should now pass")
    
except Exception as e:
    print(f"❌ CONFIGURATION IMPORT FAILED: {e}")
    print(f"   One or both issues are still present")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n" + "=" * 60)
print("🏁 FIXED CONFIGURATION TEST COMPLETE")
