#!/usr/bin/env python3
"""
Test script for validating conversation behavior fixes.

This script tests the specific issues reported:
1. "Explain why it rains" - should provide natural explanation without artificial formatting
2. "Explain why cats purr" - should provide biology answer, not coding-related content

Expected behavior after fixes:
- No more "coding assistant" contamination for general questions
- Proper JSON parsing without errors
- Clean, appropriate responses to conversational queries
"""

import sys
import os
from pathlib import Path

# Add the project directory to Python path
project_dir = Path(__file__).parent
sys.path.insert(0, str(project_dir))

from models.session import CommandContext
from services.dual_model_handler import DualModelHandler

def test_conversation_fixes():
    """Test the conversation behavior fixes."""
    print("🧪 Testing Conversation Behavior Fixes")
    print("=" * 60)
    
    # Test cases from the error report
    test_cases = [
        {
            "input": "Explain why it rains.",
            "description": "Should provide natural weather explanation without artificial steps"
        },
        {
            "input": "Explain why cats purr.",
            "description": "Should provide biology answer, NOT coding content"
        },
        {
            "input": "hello",
            "description": "Should provide friendly greeting without coding focus"
        },
        {
            "input": "What is photosynthesis?",
            "description": "Should provide biology explanation, not algorithm discussion"
        }
    ]
    
    results = []
    
    try:
        # Create test context
        test_ctx = CommandContext(
            user_input="test",
            root_path=project_dir,
            debug_mode=False  # Reduced debug output for cleaner testing
        )
        
        handler = DualModelHandler(test_ctx, "dual")
        
        for i, test_case in enumerate(test_cases, 1):
            print(f"\n🔬 Test {i}: {test_case['input']}")
            print(f"📝 Expected: {test_case['description']}")
            print("-" * 40)
            
            try:
                # Update context with test input
                handler.ctx.user_input = test_case["input"]
                handler.ctx.response = ""
                
                # Test semantic analysis first
                semantic_intent = handler.semantic_parser.parse_intent(test_case["input"])
                print(f"🧠 Semantic Analysis:")
                print(f"   Intent: {semantic_intent.intent_type}")
                print(f"   Specialist: {semantic_intent.specialist_needed}")
                print(f"   Confidence: {semantic_intent.confidence:.2f}")
                print(f"   Zone: {semantic_intent.zone}")
                
                # Test full conversation handling
                if semantic_intent.specialist_needed in ["local_shortcuts", "conversation"]:
                    handler._handle_conversational(semantic_intent)
                else:
                    handler._conversation_loop_with_specialist(None, semantic_intent)
                
                print(f"🤖 Response: {handler.ctx.response}")
                
                # Basic validation
                response_lower = handler.ctx.response.lower()
                has_coding_contamination = any(term in response_lower for term in [
                    "algorithm", "finite state machine", "markov chain", "coding approach",
                    "data structure", "programming", "script", "function", "class"
                ])
                
                has_step_formatting = "step 1:" in response_lower or "step 2:" in response_lower
                
                is_truncated = handler.ctx.response.endswith("There is no") or len(handler.ctx.response) < 10
                
                # Assessment
                issues = []
                if has_coding_contamination and "coding" not in test_case["input"].lower():
                    issues.append("❌ Coding contamination detected")
                if has_step_formatting:
                    issues.append("❌ Artificial step formatting detected")
                if is_truncated:
                    issues.append("❌ Response appears truncated")
                if "[HARD CODED]" in handler.ctx.response:
                    issues.append("ℹ️ Hard-coded response used")
                
                if not issues:
                    print("✅ Response looks appropriate")
                else:
                    for issue in issues:
                        print(issue)
                
                results.append({
                    "input": test_case["input"],
                    "semantic_intent": semantic_intent.__dict__,
                    "response": handler.ctx.response,
                    "issues": issues,
                    "success": len(issues) == 0 or all("Hard-coded" in issue for issue in issues)
                })
                
            except Exception as e:
                print(f"❌ Test failed with error: {str(e)}")
                results.append({
                    "input": test_case["input"],
                    "error": str(e),
                    "success": False
                })
    
    except Exception as e:
        print(f"❌ Handler initialization failed: {str(e)}")
        return {"overall_success": False, "error": str(e)}
    
    # Summary
    print(f"\n📊 Test Summary")
    print("=" * 60)
    successful_tests = sum(1 for result in results if result.get("success", False))
    total_tests = len(results)
    
    print(f"✅ Successful: {successful_tests}/{total_tests}")
    print(f"❌ Failed: {total_tests - successful_tests}/{total_tests}")
    
    if successful_tests == total_tests:
        print("🎉 All conversation behavior fixes are working correctly!")
    else:
        print("⚠️  Some issues remain - additional fixes may be needed")
    
    return {
        "overall_success": successful_tests == total_tests,
        "successful_tests": successful_tests,
        "total_tests": total_tests,
        "test_results": results
    }

if __name__ == "__main__":
    print("🚀 DeepCoderX Conversation Behavior Fix Validation")
    print("Testing fixes for inappropriate coding responses and formatting issues")
    print()
    
    try:
        results = test_conversation_fixes()
        
        # Exit with appropriate code
        sys.exit(0 if results["overall_success"] else 1)
        
    except Exception as e:
        print(f"❌ Test script failed: {str(e)}")
        sys.exit(1)
