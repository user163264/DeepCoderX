#!/usr/bin/env python3
"""
Quick test script to validate enhanced error logging system for DeepCoderX
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_logging_system():
    """Test the enhanced logging system"""
    print("🔧 Testing Enhanced Logging System...")
    
    try:
        # Test logging imports
        from utils.logging import (
            log_error, log_warning, log_info, log_debug, 
            log_model_loading, log_performance, log_routing_decision,
            dual_model_logger, get_log_summary
        )
        print("✅ Logging imports successful")
        
        # Test basic logging functions
        log_info("TestSystem", "Testing enhanced logging system")
        log_debug("TestSystem", "This is a debug message (file only)")
        log_warning("TestSystem", "This is a warning message")
        
        # Test performance logging
        log_performance("TestSystem", "test operation", 1.23, "test details")
        
        # Test model loading simulation
        log_model_loading("TestSystem", "test-model", "~1GB", 2.45)
        
        # Test routing decision logging
        log_routing_decision("conversation", "local_shortcuts", 0.85, "hello world")
        
        # Test error logging
        try:
            raise ValueError("This is a test error")
        except Exception as e:
            log_error("TestSystem", "Testing error logging", e)
        
        print("✅ All logging functions working")
        
        # Check log summary
        log_summary = get_log_summary()
        print("📊 Log files created:")
        for log_file, info in log_summary.items():
            if 'error' not in info:
                print(f"  • {log_file}: {info['size_mb']} MB (modified: {info['modified']})")
            else:
                print(f"  • {log_file}: Error - {info['error']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Logging test failed: {e}")
        return False

def test_dual_model_imports():
    """Test dual model handler imports with logging"""
    print("\n🔧 Testing Dual Model Handler Imports...")
    
    try:
        from services.dual_model_handler import DualModelHandler
        print("✅ DualModelHandler import successful")
        
        # Test component logger
        from utils.logging import dual_model_logger
        dual_model_logger.info("Dual model handler import test completed successfully")
        print("✅ Component logger working")
        
        return True
        
    except Exception as e:
        print(f"❌ Dual model import test failed: {e}")
        return False

def test_syntax_check():
    """Run syntax check on dual model handler"""
    print("\n🔧 Testing Dual Model Handler Syntax...")
    
    import subprocess
    
    try:
        result = subprocess.run([
            "python3", "-m", "py_compile", "services/dual_model_handler.py"
        ], capture_output=True, text=True, cwd=project_root)
        
        if result.returncode == 0:
            print("✅ Dual model handler syntax check passed")
            return True
        else:
            print(f"❌ Syntax error: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Syntax check failed: {e}")
        return False

def main():
    """Run all logging tests"""
    print("🚀 DeepCoderX Enhanced Logging System Test Suite")
    print("=" * 60)
    
    tests = [
        ("Logging System", test_logging_system),
        ("Dual Model Imports", test_dual_model_imports),
        ("Syntax Check", test_syntax_check)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            success = test_func()
            results.append((test_name, success))
        except Exception as e:
            print(f"❌ {test_name} test crashed: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 Test Results Summary:")
    
    passed = 0
    for test_name, success in results:
        status = "✅ PASSED" if success else "❌ FAILED"
        print(f"  {status}: {test_name}")
        if success:
            passed += 1
    
    total = len(results)
    print(f"\n🎯 Overall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Enhanced logging system is ready.")
        print("\n📋 Log files are created in ./logs/ directory:")
        print("  • deepcoderx_errors.log - Error logging with rotation")
        print("  • deepcoderx_debug.log - Debug logging with rotation") 
        print("  • session_YYYYMMDD_HHMMSS.log - Current session log")
        print("\n🚀 Ready for Phase 3 testing with comprehensive error logging!")
    else:
        print("⚠️  Some tests failed. Please review and fix issues before proceeding.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
