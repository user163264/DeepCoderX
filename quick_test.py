#!/usr/bin/env python3
"""
Quick test to verify config import fix.
Run this from the DeepCoderX directory.
"""

try:
    print("Testing config import...")
    from config_module import config
    print("✅ Config import successful!")
    
    print("Testing app import...")
    import app
    print("✅ App import successful!")
    
    print("\n🎉 All imports working! DeepCoderX should now start properly.")
    print("Try running: deepcoderx")
    
except Exception as e:
    print(f"❌ Import error: {e}")
    print("There may be additional import issues to fix.")
