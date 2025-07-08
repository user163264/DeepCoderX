#!/usr/bin/env python3

import sys
import os
sys.path.insert(0, '/Users/admin/Documents/DeepCoderX')

try:
    from config import config
    print("✅ SUCCESS: Config imported successfully")
    print(f"Default provider: {config.DEFAULT_PROVIDER}")
    print(f"Sandbox path: {config.SANDBOX_PATH}")
    print(f"Debug mode: {config.DEBUG_MODE}")
except Exception as e:
    print(f"❌ ERROR: {e}")
    import traceback
    traceback.print_exc()
