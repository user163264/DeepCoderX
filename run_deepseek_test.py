#!/usr/bin/env python3
"""Simple test runner to check DeepSeek tools test"""

import subprocess
import sys
import os

def run_test():
    """Run the DeepSeek tools test"""
    try:
        # Change to the project directory
        os.chdir('/Users/admin/Documents/DeepCoderX')
        
        # Run the test
        result = subprocess.run([
            sys.executable, 'test_deepseek_tools.py'
        ], capture_output=True, text=True, timeout=60)
        
        print("=== TEST OUTPUT ===")
        print(result.stdout)
        
        if result.stderr:
            print("=== TEST ERRORS ===")
            print(result.stderr)
        
        print(f"=== RETURN CODE: {result.returncode} ===")
        
        return result.returncode == 0
        
    except subprocess.TimeoutExpired:
        print("❌ TEST TIMEOUT: Test took too long to complete")
        return False
    except Exception as e:
        print(f"❌ TEST ERROR: {e}")
        return False

if __name__ == "__main__":
    success = run_test()
    if success:
        print("✅ Test runner completed successfully")
    else:
        print("❌ Test runner encountered issues")
