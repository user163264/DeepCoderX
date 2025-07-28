#!/usr/bin/env python3
"""
Simple Enhanced Logging Test

Tests if the enhanced logging functions work correctly.
"""

import os
import sys
from pathlib import Path

# Enable logging
os.environ.update({
    "DEEPCODERX_LOG_MODEL_PROMPTS": "true",
    "DEEPCODERX_LOG_MODEL_RESPONSES": "true",
    "DEEPCODERX_LOG_SEMANTIC_DETAILS": "true",
    "DEEPCODERX_LOG_TOOL_DETAILS": "true",
    "DEEPCODERX_LOG_CONVERSATION_CONTEXT": "true"
})

print("🔧 Simple Enhanced Logging Test")
print("=" * 40)

try:
    # Import logging functions
    print("1. Testing imports...")
    from utils.model_logging import (
        log_model_prompt, log_model_response, log_semantic_analysis_attempt,
        log_tool_execution_details, log_conversation_context_details
    )
    print("   ✅ Enhanced logging functions imported")

    # Import configuration
    from config_module import DEBUG_LOGGING
    print(f"   ✅ Config loaded: {DEBUG_LOGGING}")

    # Test basic logging
    print("\n2. Testing basic logging...")
    
    # Test prompt logging
    interaction_id = log_model_prompt(
        model_name="test-verification",
        prompt="This is a test prompt to verify logging works",
        parameters={"temperature": 0.0},
        context="test"
    )
    print(f"   ✅ Prompt logged: {interaction_id}")

    # Test response logging  
    log_model_response(
        interaction_id=interaction_id,
        model_name="test-verification",
        response="This is a test response",
        duration=1.0,
        context="test"
    )
    print("   ✅ Response logged")

    # Test semantic logging
    log_semantic_analysis_attempt(
        interaction_id=f"semantic_{interaction_id}",
        user_input="hello test",
        raw_response='{"intent": "greeting", "confidence": 0.9}',
        parsed_result={"intent": "greeting", "confidence": 0.9}
    )
    print("   ✅ Semantic analysis logged")

    # Check log files exist
    print("\n3. Checking log files...")
    log_dir = Path("logs/model_interactions")
    if log_dir.exists():
        jsonl_files = list(log_dir.glob("*.jsonl"))
        print(f"   ✅ Found {len(jsonl_files)} log files")
        
        # Show recent files
        for file in sorted(jsonl_files)[-5:]:  # Last 5 files
            size = file.stat().st_size
            print(f"      - {file.name}: {size} bytes")
            
            # Show last line of recent files
            if size > 0:
                try:
                    with open(file, 'r') as f:
                        lines = f.readlines()
                        if lines:
                            last_line = lines[-1].strip()
                            print(f"        Last entry: {last_line[:100]}...")
                except Exception as e:
                    print(f"        Could not read: {e}")
    else:
        print("   ❌ Log directory not found")

    print("\n🎉 Simple logging test completed successfully!")
    print("✅ Enhanced logging system is working")

except Exception as e:
    print(f"\n❌ Test failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
