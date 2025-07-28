#!/usr/bin/env python3
"""
Complete MCPClient Fix Validation
Tests both test_deepseek_tools.py and test_deepseek_live.py fixes
"""

import subprocess
import sys
import os
from pathlib import Path

def run_test(script_name, description, timeout=60):
    """Run a test script and return results"""
    print(f"\n{'='*60}")
    print(f"🧪 {description}")
    print(f"{'='*60}")
    print(f"Running: {script_name}")
    print("-" * 60)
    
    try:
        # Change to project directory
        project_dir = Path('/Users/admin/Documents/DeepCoderX')
        os.chdir(project_dir)
        
        # Run the test
        result = subprocess.run(
            [sys.executable, script_name],
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=project_dir
        )
        
        # Display results
        if result.stdout:
            print(result.stdout)
        
        if result.stderr:
            print("STDERR:")
            print(result.stderr)
        
        success = result.returncode == 0
        status = "✅ SUCCESS" if success else "❌ FAILED"
        print(f"\n{status} - Return code: {result.returncode}")
        
        return success
        
    except subprocess.TimeoutExpired:
        print("❌ TIMEOUT")
        return False
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False

def main():
    """Test both fixed scripts"""
    print("🔬 COMPLETE MCPCLIENT FIX VALIDATION")
    print("="*60)
    print("Testing both DeepSeek test scripts with MCPClient fixes applied")
    
    tests = [
        ("test_deepseek_tools.py", "DeepSeek Tools Test Suite (Fixed)", 60),
        ("test_deepseek_live.py", "DeepSeek Live API Test (Fixed)", 90)
    ]
    
    results = []
    
    for script, description, timeout in tests:
        print(f"\n📋 About to run: {script}")
        if script == "test_deepseek_live.py":
            print("⚠️  Note: Live test will ask for confirmation before making API calls")
            input("   Press Enter to continue or Ctrl+C to skip...")
        
        success = run_test(script, description, timeout)
        results.append((script, success))
    
    # Summary
    print(f"\n{'='*60}")
    print("📊 FINAL TEST SUMMARY")
    print(f"{'='*60}")
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for script, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {script}")
    
    print(f"\nOverall: {passed}/{total} test scripts passed")
    
    if passed == total:
        print("\n🎉 ALL MCPCLIENT FIXES WORKING!")
        print("✅ Both test suites now run without initialization errors")
        print("🚀 Ready for:")
        print("   - Step 3: Provider switching validation")
        print("   - Step 4: Documentation updates")
        print("   - Step 5: Performance benchmarking")
        print("   - Live DeepSeek API integration testing")
    else:
        print(f"\n⚠️ {total - passed} test scripts still have issues")
        print("🔧 Review the detailed output above")
    
    print(f"\n{'='*60}")
    return passed == total

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n🛑 Testing interrupted")
        sys.exit(1)
