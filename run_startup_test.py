#!/usr/bin/env python3
"""
Execute the startup test and show results.
"""

import subprocess
import sys
import os
from pathlib import Path

# Change to project directory
os.chdir('/Users/admin/Documents/DeepCoderX')

print("🧪 Running DeepCoderX startup configuration test...")
print("=" * 60)

try:
    # Run the test script
    result = subprocess.run([
        sys.executable, 'test_startup_fix.py'
    ], capture_output=True, text=True, timeout=30)
    
    print("STDOUT:")
    print(result.stdout)
    
    if result.stderr:
        print("\nSTDERR:")
        print(result.stderr)
    
    print(f"\nExit code: {result.returncode}")
    
    if result.returncode == 0:
        print("\n🎉 TEST PASSED: Startup error appears to be RESOLVED!")
    else:
        print("\n❌ TEST FAILED: Startup error still exists")
        
except subprocess.TimeoutExpired:
    print("❌ Test timed out after 30 seconds")
except Exception as e:
    print(f"❌ Error running test: {e}")

print("=" * 60)
