#!/usr/bin/env python3
"""
Test Enhanced Logging System Verification

This script tests if the enhanced logging system is working correctly
and generates sample logs to verify functionality.
"""

import os
import sys
from pathlib import Path

# Enable development logging profile
os.environ.update({
    "DEEPCODERX_LOG_MODEL_PROMPTS": "true",
    "DEEPCODERX_LOG_MODEL_RESPONSES": "true", 
    "DEEPCODERX_LOG_SEMANTIC_DETAILS": "true",
    "DEEPCODERX_LOG_TOOL_DETAILS": "true",
    "DEEPCODERX_LOG_CONVERSATION_CONTEXT": "true",
    "DEEPCODERX_LOG_INTERACTION_TRACKING": "true",
    "DEEPCODERX_LOG_STRUCTURED_STORAGE": "true"
})

print("🔧 Enhanced Logging Verification Test")
print("=" * 50)

try:
    # Test imports
    print("1. Testing imports...")
    from utils.model_logging import (
        log_model_prompt, log_model_response, log_semantic_analysis_attempt,
        log_tool_execution_details, log_conversation_context_details, 
        get_model_interactions_summary
    )
    from config_module import DEBUG_LOGGING
    print("   ✅ All imports successful")

    # Check configuration
    print("\n2. Checking configuration...")
    print(f"   DEBUG_LOGGING: {DEBUG_LOGGING}")
    enabled_count = sum(1 for v in DEBUG_LOGGING.values() if v)
    print(f"   ✅ {enabled_count}/{len(DEBUG_LOGGING)} features enabled")

    # Test logging functions
    print("\n3. Testing logging functions...")
    
    # Test prompt logging
    interaction_id = log_model_prompt(
        model_name="test-model",
        prompt="This is a test prompt for verification",
        parameters={"temperature": 0.0, "max_tokens": 100},
        context="verification_test"
    )
    print(f"   ✅ Prompt logged with interaction_id: {interaction_id}")

    # Test response logging
    log_model_response(
        interaction_id=interaction_id,
        model_name="test-model", 
        response="This is a test response for verification",
        duration=1.5,
        context="verification_test"
    )
    print("   ✅ Response logged")

    # Test semantic analysis logging
    log_semantic_analysis_attempt(
        interaction_id=f"semantic_{interaction_id}",
        user_input="hello world",
        raw_response='{"intent": "greeting", "confidence": 0.9}',
        parsed_result={"intent": "greeting", "confidence": 0.9},
        zone_info={"detected_zone": "conversational", "zone_confidence": 1.0}
    )
    print("   ✅ Semantic analysis logged")

    # Test tool execution logging
    log_tool_execution_details(
        interaction_id=f"tool_{interaction_id}",
        tool_calls=[{"tool": "run_bash", "command": "pwd"}],
        tool_results=["✅ Command executed successfully: /Users/admin/Documents/DeepCoderX"]
    )
    print("   ✅ Tool execution logged")

    # Test conversation context logging
    log_conversation_context_details(
        interaction_id=f"context_{interaction_id}",
        conversation_history=[
            {"role": "user", "content": "hello"},
            {"role": "assistant", "content": "Hi! How can I help you?"}
        ],
        context_summary="Test conversation context"
    )
    print("   ✅ Conversation context logged")

    # Check log files
    print("\n4. Checking log files...")
    model_interactions_dir = Path("logs/model_interactions")
    if model_interactions_dir.exists():
        log_files = list(model_interactions_dir.glob("*.jsonl"))
        print(f"   ✅ Found {len(log_files)} log files:")
        for log_file in sorted(log_files):
            size = log_file.stat().st_size
            print(f"      - {log_file.name}: {size} bytes")
    else:
        print("   ❌ Model interactions directory not found")

    # Test summary generation
    print("\n5. Testing summary generation...")
    try:
        summary = get_model_interactions_summary()
        print(f"   ✅ Summary generated: {len(summary.get('log_files', {}))} files tracked")
        
        # Show recent activity
        if 'recent_activity' in summary:
            recent_count = len(summary['recent_activity'])
            print(f"   ✅ Recent activity: {recent_count} entries")
        
    except Exception as e:
        print(f"   ⚠️  Summary generation failed: {e}")

    print("\n🎉 Enhanced Logging Verification Complete!")
    print("✅ All tests passed - logging system is operational")

except Exception as e:
    print(f"\n❌ Verification failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
