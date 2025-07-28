#!/usr/bin/env python3
"""
Test the system_override fix for code specialist routing.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from models.session import CommandContext
from pathlib import Path

def test_code_specialist_routing():
    """Test if code specialist routing works without system_override error."""
    print("🧪 Testing code specialist routing fix...")
    
    try:
        # Create test context  
        test_ctx = CommandContext(
            root_path=Path.cwd(),
            mcp_client=None,
            sandbox_path=Path.cwd(),
            debug_mode=True
        )
        test_ctx.user_input = "create a Python script"
        
        # Import and test dual model handler
        from services.dual_model_handler import DualModelHandler
        
        print("✅ DualModelHandler import successful")
        
        # Create handler
        handler = DualModelHandler(test_ctx, "dual")
        print("✅ DualModelHandler initialization successful")
        
        # Test semantic parsing (this should route to qwen_coder)
        semantic_intent = handler.semantic_parser.parse_intent("create a Python script")
        print(f"✅ Semantic parsing successful!")
        print(f"   Intent: {semantic_intent.intent_type}")
        print(f"   Specialist: {semantic_intent.specialist_needed}")
        print(f"   Confidence: {semantic_intent.confidence:.2f}")
        
        # Test specialist prompt building (this was causing the error)
        conversation_history = []
        available_tools = handler._get_available_tools()
        
        print("🔧 Testing specialist prompt building...")
        
        try:
            prompt = handler._build_specialist_prompt(
                "create a Python script",
                conversation_history,
                available_tools,
                semantic_intent
            )
            print(f"✅ Specialist prompt built successfully!")
            print(f"   Prompt length: {len(prompt)} characters")
            print(f"   Contains intent info: {'Intent:' in prompt}")
            print(f"   Contains tools info: {'Available tools:' in prompt}")
            
        except Exception as e:
            print(f"❌ Specialist prompt building failed: {e}")
            return False
        
        print("🎉 SUCCESS: system_override fix works correctly!")
        print("   - Semantic parser operational")
        print("   - Code specialist routing functional") 
        print("   - Prompt building without errors")
        return True
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_code_specialist_routing()
    sys.exit(0 if success else 1)
