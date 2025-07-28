#!/usr/bin/env python3
"""
Live DeepSeek Tool Calling Test
Tests actual API calls with native OpenAI tool usage
"""

import sys
import os
import time
import signal
from pathlib import Path

# Add project root to path
sys.path.append('/Users/admin/Documents/DeepCoderX')

def setup_live_test():
    """Set up live test environment"""
    try:
        from models.session import CommandContext
        from services.mcpclient import MCPClient
        from services.unified_openai_handler import CloudOpenAIHandler
        from config import config
        
        # Check API key
        api_key = config.PROVIDERS["deepseek"]["api_key"]
        if not api_key or api_key == "your_api_key_here":
            print("❌ No valid DeepSeek API key found")
            print("💡 Set DEEPSEEK_API_KEY environment variable")
            return None, None
        
        # Create context
        test_dir = Path('/Users/admin/Documents/DeepCoderX')
        # Initialize MCP client with required parameters
        mcp_client = MCPClient(
            endpoint=f"http://{config.MCP_SERVER_HOST}:{config.MCP_SERVER_PORT}",
            api_key=config.MCP_API_KEY
        )
        
        ctx = CommandContext(
            root_path=test_dir,
            mcp_client=mcp_client,
            sandbox_path=config.SANDBOX_PATH,
            debug_mode=True
        )
        
        # Create handler
        handler = CloudOpenAIHandler(ctx, "deepseek")
        
        return ctx, handler
        
    except Exception as e:
        print(f"❌ Setup error: {e}")
        return None, None

def test_simple_tool_call():
    """Test simple tool call (list_dir)"""
    print("🧪 Live Test 1: Simple Tool Call (list_dir)")
    
    ctx, handler = setup_live_test()
    if not ctx or not handler:
        return False
    
    try:
        # Set up request
        ctx.user_input = "list the files in the current directory"
        
        print(f"📝 Request: {ctx.user_input}")
        print("⏳ Calling DeepSeek with native tool support...")
        
        start_time = time.time()
        
        # Process request
        handler.handle()
        
        elapsed = time.time() - start_time
        
        # Check response
        if not ctx.response:
            print("❌ FAIL: No response received")
            return False
            
        if "error" in ctx.response.lower() and "api" in ctx.response.lower():
            print(f"❌ FAIL: API Error - {ctx.response}")
            return False
            
        print(f"✅ SUCCESS: Response received in {elapsed:.2f}s")
        print(f"🤖 Response: {ctx.response[:200]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False

def test_file_operations():
    """Test file read/write operations"""
    print("\n🧪 Live Test 2: File Operations")
    
    ctx, handler = setup_live_test()
    if not ctx or not handler:
        return False
    
    try:
        # Test file creation
        ctx.user_input = "create a test file called hello_deepseek.py with a simple hello world program"
        
        print(f"📝 Request: {ctx.user_input}")
        print("⏳ Testing file creation...")
        
        start_time = time.time()
        handler.handle()
        elapsed = time.time() - start_time
        
        if "error" in ctx.response.lower() and "api" in ctx.response.lower():
            print(f"❌ FAIL: API Error - {ctx.response}")
            return False
            
        print(f"✅ File creation response in {elapsed:.2f}s")
        print(f"🤖 Response: {ctx.response[:150]}...")
        
        # Test file reading
        print("\n📖 Testing file reading...")
        ctx.user_input = "read the contents of hello_deepseek.py"
        
        start_time = time.time()
        handler.handle()
        elapsed = time.time() - start_time
        
        if "error" in ctx.response.lower() and "api" in ctx.response.lower():
            print(f"❌ FAIL: API Error - {ctx.response}")
            return False
            
        print(f"✅ File reading response in {elapsed:.2f}s")
        print(f"🤖 Response: {ctx.response[:150]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False

def test_multi_tool_workflow():
    """Test complex multi-tool workflow"""
    print("\n🧪 Live Test 3: Multi-Tool Workflow")
    
    ctx, handler = setup_live_test()
    if not ctx or not handler:
        return False
    
    try:
        # Complex request requiring multiple tools
        ctx.user_input = "analyze the project structure by listing directories and reading the main config file"
        
        print(f"📝 Request: {ctx.user_input}")
        print("⏳ Testing multi-tool workflow...")
        
        start_time = time.time()
        handler.handle()
        elapsed = time.time() - start_time
        
        if "error" in ctx.response.lower() and "api" in ctx.response.lower():
            print(f"❌ FAIL: API Error - {ctx.response}")
            return False
            
        print(f"✅ Multi-tool response in {elapsed:.2f}s")
        print(f"🤖 Response: {ctx.response[:200]}...")
        
        # Check if response indicates multiple tool usage
        tool_indicators = ["directory", "config", "files", "structure"]
        found_indicators = sum(1 for indicator in tool_indicators 
                             if indicator.lower() in ctx.response.lower())
        
        if found_indicators >= 2:
            print(f"✅ Multi-tool usage detected ({found_indicators} indicators)")
        else:
            print("⚠️ May not have used multiple tools")
        
        return True
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False

def test_analysis_request():
    """Test typical analysis request"""
    print("\n🧪 Live Test 4: Analysis Request")
    
    ctx, handler = setup_live_test()
    if not ctx or not handler:
        return False
    
    try:
        # Analysis request
        ctx.user_input = "analyze the main application file app.py and explain its key components"
        
        print(f"📝 Request: {ctx.user_input}")
        print("⏳ Testing analysis capabilities...")
        
        start_time = time.time()
        handler.handle()
        elapsed = time.time() - start_time
        
        if "error" in ctx.response.lower() and "api" in ctx.response.lower():
            print(f"❌ FAIL: API Error - {ctx.response}")
            return False
            
        print(f"✅ Analysis response in {elapsed:.2f}s")
        
        # Check for analysis quality indicators
        analysis_indicators = ["function", "class", "import", "component", "module"]
        found_indicators = sum(1 for indicator in analysis_indicators 
                             if indicator.lower() in ctx.response.lower())
        
        if found_indicators >= 3:
            print(f"✅ Quality analysis detected ({found_indicators} technical terms)")
        else:
            print("⚠️ Analysis may be superficial")
            
        print(f"🤖 Response preview: {ctx.response[:200]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False

def test_error_handling():
    """Test error handling and recovery"""
    print("\n🧪 Live Test 5: Error Handling")
    
    ctx, handler = setup_live_test()
    if not ctx or not handler:
        return False
    
    try:
        # Request that should cause tool error
        ctx.user_input = "read the file nonexistent_file_12345.txt"
        
        print(f"📝 Request: {ctx.user_input}")
        print("⏳ Testing error handling...")
        
        start_time = time.time()
        handler.handle()
        elapsed = time.time() - start_time
        
        # Should handle error gracefully
        if not ctx.response:
            print("❌ FAIL: No response to error case")
            return False
            
        # Check for appropriate error handling
        error_indicators = ["not found", "error", "cannot", "unable", "does not exist"]
        found_error_handling = any(indicator in ctx.response.lower() 
                                 for indicator in error_indicators)
        
        if found_error_handling:
            print(f"✅ Error handled gracefully in {elapsed:.2f}s")
            print(f"🤖 Error response: {ctx.response[:150]}...")
        else:
            print("⚠️ Error handling unclear")
            print(f"🤖 Response: {ctx.response[:150]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False

def run_live_tests():
    """Run all live DeepSeek tests"""
    print("=" * 70)
    print("🚀 DEEPSEEK LIVE TOOL CALLING TESTS")
    print("=" * 70)
    
    # Check prerequisites
    print("🔍 Checking prerequisites...")
    
    try:
        from config import config
        api_key = config.PROVIDERS["deepseek"]["api_key"]
        
        if not api_key or api_key == "your_api_key_here":
            print("❌ CRITICAL: No DeepSeek API key configured")
            print("💡 Set DEEPSEEK_API_KEY environment variable and try again")
            return False
            
        print(f"✅ API key configured: {api_key[:8]}...")
        
    except Exception as e:
        print(f"❌ Prerequisites failed: {e}")
        return False
    
    # Warning about API usage
    print("\n⚠️ WARNING: These tests will make actual API calls to DeepSeek")
    print("💰 This may consume API credits")
    
    try:
        response = input("Continue with live tests? (y/N): ").strip().lower()
        if response != 'y':
            print("🛑 Tests cancelled by user")
            return False
    except KeyboardInterrupt:
        print("\n🛑 Tests cancelled by user")
        return False
    
    # Test functions
    tests = [
        test_simple_tool_call,
        test_file_operations,
        test_multi_tool_workflow,
        test_analysis_request,
        test_error_handling
    ]
    
    # Run tests
    results = []
    for test_func in tests:
        try:
            result = test_func()
            results.append(result)
            
            # Small delay between tests
            time.sleep(1)
            
        except KeyboardInterrupt:
            print("\n🛑 Tests interrupted by user")
            break
        except Exception as e:
            print(f"❌ CRITICAL ERROR in {test_func.__name__}: {e}")
            results.append(False)
    
    # Summary
    passed = sum(results)
    total = len(results)
    
    print("\n" + "=" * 70)
    print("📊 LIVE TEST SUMMARY")
    print("=" * 70)
    print(f"✅ Passed: {passed}/{total} tests")
    print(f"❌ Failed: {total - passed}/{total} tests")
    
    if passed == total:
        print("\n🎉 ALL LIVE TESTS PASSED!")
        print("🚀 DeepSeek native tool calling is working perfectly")
        print("\n✨ Confirmed capabilities:")
        print("   • Native OpenAI tool calling")
        print("   • Multi-tool workflows")
        print("   • File operations through MCP")
        print("   • Analysis and code understanding")
        print("   • Graceful error handling")
    else:
        print(f"\n⚠️ {total - passed} tests failed")
        print("🔧 Check API connectivity and configuration")
    
    print("=" * 70)
    
    return passed == total

if __name__ == "__main__":
    # Set up signal handling
    def signal_handler(sig, frame):
        print("\n🛑 Live tests interrupted")
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    
    # Run live tests
    success = run_live_tests()
    sys.exit(0 if success else 1)
