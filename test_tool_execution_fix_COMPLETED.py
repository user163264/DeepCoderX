#!/usr/bin/env python3
"""
Test the tool execution result fix for dual model handler.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from models.session import CommandContext
from pathlib import Path

def test_tool_execution_response():
    """Test if tool execution results are properly set as ctx.response."""
    print("🧪 Testing tool execution response fix...")
    
    try:
        # Create test context  
        test_ctx = CommandContext(
            root_path=Path.cwd(),
            mcp_client=None,
            sandbox_path=Path.cwd(),
            debug_mode=True
        )
        test_ctx.user_input = "pwd"
        
        # Import and test dual model handler
        from services.dual_model_handler import DualModelHandler
        
        print("✅ DualModelHandler import successful")
        
        # Create handler
        handler = DualModelHandler(test_ctx, "dual")
        print("✅ DualModelHandler initialization successful")
        
        # Manually test the direct shortcut path (this should execute pwd)
        intent_mock = type('MockIntent', (), {
            'intent_type': 'file_operation',
            'specialist_needed': 'local_shortcuts',
            'confidence': 0.95
        })()
        
        print("🔧 Testing local shortcuts with pwd command...")
        
        # Test the handle method
        handler.handle()
        
        print(f"✅ Handler execution completed!")
        print(f"   Final response: '{test_ctx.response}'")
        print(f"   Response length: {len(test_ctx.response) if test_ctx.response else 0} characters")
        print(f"   Response type: {type(test_ctx.response)}")
        
        # Check if response was set
        if test_ctx.response and test_ctx.response.strip():
            print("✅ SUCCESS: Tool execution results properly set as response!")
            print(f"   Response preview: {test_ctx.response[:100]}...")
            return True
        else:
            print("❌ FAILURE: Tool execution results not set as response")
            print(f"   Response was: '{test_ctx.response}'")
            return False
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_tool_execution_response()
    sys.exit(0 if success else 1)
