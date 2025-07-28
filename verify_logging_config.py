#!/usr/bin/env python3
"""
Verify Enhanced Logging Configuration

This script checks if the enhanced logging configuration is properly loaded.
"""

import os
from pathlib import Path

print("🔍 Enhanced Logging Configuration Verification")
print("=" * 50)

# Check if we're in the right directory
if not Path(".env").exists():
    print("❌ Not in DeepCoderX directory - please run from /Users/admin/Documents/DeepCoderX")
    exit(1)

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

print("1. Environment Variables Check")
print("-" * 30)

logging_vars = [
    "DEEPCODERX_LOG_MODEL_PROMPTS",
    "DEEPCODERX_LOG_MODEL_RESPONSES", 
    "DEEPCODERX_LOG_SEMANTIC_DETAILS",
    "DEEPCODERX_LOG_TOOL_DETAILS",
    "DEEPCODERX_LOG_CONVERSATION_CONTEXT",
    "DEEPCODERX_LOG_INTERACTION_TRACKING",
    "DEEPCODERX_LOG_STRUCTURED_STORAGE"
]

all_enabled = True
for var in logging_vars:
    value = os.getenv(var, "not set")
    status = "✅ ON" if value.lower() == "true" else "❌ OFF" if value.lower() == "false" else "⚠️ UNKNOWN"
    print(f"   {var}: {status}")
    if value.lower() != "true":
        all_enabled = False

print("\n2. Configuration Loading Test")
print("-" * 30)

try:
    from config_module import DEBUG_LOGGING
    print("✅ Configuration module loaded successfully")
    
    enabled_count = sum(1 for v in DEBUG_LOGGING.values() if v)
    total_count = len(DEBUG_LOGGING)
    print(f"✅ Debug logging features: {enabled_count}/{total_count} enabled")
    
    for key, enabled in DEBUG_LOGGING.items():
        status = "✅ ON" if enabled else "❌ OFF"
        print(f"   {key}: {status}")
        
except Exception as e:
    print(f"❌ Configuration loading failed: {e}")
    all_enabled = False

print("\n3. Summary")
print("-" * 10)

if all_enabled:
    print("🎉 SUCCESS: Enhanced logging is fully configured!")
    print("✅ All environment variables are set to 'true'")
    print("✅ Configuration is loaded correctly")
    print("\n🚀 You can now start DeepCoderX and all model interactions will be logged:")
    print("   python3 app.py")
    print("   OR")
    print("   ./start_deepcoderx.sh")
else:
    print("❌ ISSUES DETECTED: Some logging features are not enabled")
    print("💡 Check the .env file or run the setup script again")

print(f"\n📁 Logs will be saved to: {Path('logs/model_interactions').absolute()}")
