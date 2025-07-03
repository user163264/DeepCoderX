#!/usr/bin/env python3
"""
Simple Test Runner for DeepSeek Tools Fix Validation
Run this script to verify the MCPClient initialization fix is working
"""

import subprocess
import sys
import os
from pathlib import Path

def run_test_command(command, description, timeout=30):
    """Run a test command and return results"""
    print(f"\n{'='*60}")
    print(f"🧪 {description}")
    print(f"{'='*60}")
    print(f"Command: {command}")
    print("-" * 60)
    
    try:
        # Change to project directory
        project_dir = Path('/Users/admin/Documents/DeepCoderX')
        os.chdir(project_dir)
        
        # Run the command
        result = subprocess.run(
            command.split(),
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=project_dir
        )
        
        # Display output
        if result.stdout:
            print("STDOUT:")
            print(result.stdout)
        
        if result.stderr:
            print("STDERR:")
            print(result.stderr)
        
        print(f"\nReturn Code: {result.returncode}")
        
        # Determine success
        success = result.returncode == 0
        status = "✅ PASSED" if success else "❌ FAILED"
        print(f"Status: {status}")
        
        return success, result
        
    except subprocess.TimeoutExpired:
        print("❌ TIMEOUT: Command took too long to complete")
        return False, None
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False, None

def main():
    """Main test runner"""
    print("🔬 DEEPSEEK TOOLS FIX VALIDATION SUITE")
    print("="*60)
    print("This script will test the MCPClient initialization fix")
    print("and validate that DeepSeek tools testing is working correctly.")
    
    # Test commands to run
    tests = [
        ("python validate_fix.py", "Basic Fix Validation", 20),
        ("python test_deepseek_tools.py", "Full DeepSeek Tools Test Suite", 60),
        ("python test_quick_fix_validation.py", "Quick Integration Test", 15)
    ]
    
    results = []
    
    for command, description, timeout in tests:
        success, result = run_test_command(command, description, timeout)
        results.append((description, success))
    
    # Summary
    print(f"\n{'='*60}")
    print("📊 TEST SUMMARY")
    print(f"{'='*60}")
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for description, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {description}")
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED!")
        print("✅ MCPClient initialization fix is working correctly")
        print("🚀 DeepSeek tools test suite is ready for use")
        print("\n💡 Next steps:")
        print("   1. Test with actual DeepSeek API key: python test_deepseek_live.py")
        print("   2. Run provider switching tests")
        print("   3. Test integration in main application")
    else:
        print(f"\n⚠️ {total - passed} tests failed")
        print("🔧 Review the detailed output above to identify issues")
        print("💡 Common issues:")
        print("   - Missing dependencies (run: pip install -r requirements.txt)")
        print("   - Python path issues (ensure you're in the DeepCoderX directory)")
        print("   - Configuration problems (check config.py settings)")
    
    print(f"\n{'='*60}")
    return passed == total

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n🛑 Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n💥 Unexpected error: {e}")
        sys.exit(1)
