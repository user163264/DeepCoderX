#!/usr/bin/env python3
"""
Basic Python import test for DeepCoderX - Assessment Protocol Step 1
"""

# Test basic Python functionality first
print("=== ASSESSMENT PROTOCOL: BASIC ENVIRONMENT TEST ===")
print("Test 1: Python execution - SUCCESS (this message proves it)")

# Test basic imports that should always work
import sys
import os
from pathlib import Path

print(f"Python version: {sys.version_info}")
print(f"Current working directory: {os.getcwd()}")

# Test if we can import the config module
print("\nTest 2: Attempting config_module import...")
try:
    # Add current directory to path
    current_dir = Path(__file__).parent
    sys.path.insert(0, str(current_dir))
    
    import config_module
    print("✅ config_module import: SUCCESS")
    
    # Test if we can access the config object
    try:
        from config_module import config
        print(f"✅ config object access: SUCCESS")
        print(f"   Default provider: {config.DEFAULT_PROVIDER}")
        print(f"   Debug mode: {config.DEBUG_MODE}")
    except Exception as e:
        print(f"❌ config object access: FAILED - {e}")
        
except Exception as e:
    print(f"❌ config_module import: FAILED - {e}")

print("\n=== BASIC ENVIRONMENT TEST COMPLETE ===")
