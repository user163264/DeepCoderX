#!/usr/bin/env python3
"""
Test the actual application startup to verify the fixes work.
"""

import subprocess
import sys
import os
from pathlib import Path

# Change to project directory
os.chdir('/Users/admin/Documents/DeepCoderX')

print("🚀 TESTING ACTUAL APPLICATION STARTUP")
print("=" * 50)

# Test 1: Configuration test
print("1️⃣ Running configuration test...")
try:
    result = subprocess.run([sys.executable, 'test_fixed_config.py'], 
                          capture_output=True, text=True, timeout=10)
    
    if result.returncode == 0:
        print("✅ Configuration test PASSED")
        print("   Fixed configuration loads successfully")
    else:
        print("❌ Configuration test FAILED")
        print("STDOUT:", result.stdout[-300:] if result.stdout else "None")
        print("STDERR:", result.stderr[-300:] if result.stderr else "None")
        
except Exception as e:
    print(f"❌ Configuration test error: {e}")

# Test 2: Try importing the main app module
print("\n2️⃣ Testing app.py import...")
try:
    result = subprocess.run([sys.executable, '-c', 
                            'import app; print("✅ app.py imported successfully")'], 
                          capture_output=True, text=True, timeout=10)
    
    if result.returncode == 0:
        print("✅ app.py imports successfully")
        print("   No configuration errors on import")
    else:
        print("❌ app.py import FAILED")
        print("STDOUT:", result.stdout)
        print("STDERR:", result.stderr)
        
except Exception as e:
    print(f"❌ app.py import test error: {e}")

# Test 3: Check if we can run the application with --help
print("\n3️⃣ Testing application help command...")
try:
    result = subprocess.run([sys.executable, 'run.py', '--help'], 
                          capture_output=True, text=True, timeout=10)
    
    if result.returncode == 0:
        print("✅ Application startup successful")
        print("   Help command works - no configuration errors")
        print("   Startup error RESOLVED!")
    else:
        print("❌ Application startup FAILED")
        print("STDOUT:", result.stdout)
        print("STDERR:", result.stderr[-500:] if result.stderr else "None")
        
except Exception as e:
    print(f"❌ Application startup test error: {e}")

print("\n" + "=" * 50)
print("🏁 STARTUP TEST COMPLETE")
