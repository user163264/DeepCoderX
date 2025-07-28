#!/usr/bin/env python3
"""
Enhanced Logging Verification - Prompt and Response Capture Test

This script will definitively test if prompts and model responses are being captured.
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime

# Enable full logging
os.environ.update({
    "DEEPCODERX_LOG_MODEL_PROMPTS": "true",
    "DEEPCODERX_LOG_MODEL_RESPONSES": "true", 
    "DEEPCODERX_LOG_SEMANTIC_DETAILS": "true",
    "DEEPCODERX_LOG_TOOL_DETAILS": "true",
    "DEEPCODERX_LOG_CONVERSATION_CONTEXT": "true",
    "DEEPCODERX_DEBUG_MODE": "true"
})

print("🔍 ENHANCED LOGGING VERIFICATION TEST")
print("=" * 50)

def check_log_files():
    """Check what log files exist and their content."""
    log_dir = Path("logs/model_interactions")
    
    print(f"\n📁 Log Directory: {log_dir}")
    print(f"   Exists: {'✅ YES' if log_dir.exists() else '❌ NO'}")
    
    if not log_dir.exists():
        return False, []
    
    # Find all JSONL files
    jsonl_files = list(log_dir.glob("*.jsonl"))
    print(f"   Total JSONL files: {len(jsonl_files)}")
    
    # Group by type and show details
    file_types = {}
    recent_files = []
    
    now = datetime.now()
    for file in jsonl_files:
        # Get file type
        file_type = file.name.split('_')[0]
        if file_type not in file_types:
            file_types[file_type] = []
        file_types[file_type].append(file)
        
        # Check if recent (last 5 minutes)
        file_time = datetime.fromtimestamp(file.stat().st_mtime)
        if (now - file_time).total_seconds() < 300:  # 5 minutes
            recent_files.append(file)
    
    print("\n📄 File Types:")
    for file_type, files in file_types.items():
        print(f"   - {file_type}: {len(files)} files")
        latest = max(files, key=lambda f: f.stat().st_mtime)
        size = latest.stat().st_size
        print(f"     Latest: {latest.name} ({size} bytes)")
    
    return True, recent_files

def test_logging_functions():
    """Test the logging functions directly."""
    print("\n🧪 TESTING LOGGING FUNCTIONS")
    print("-" * 30)
    
    try:
        from utils.model_logging import (
            log_model_prompt, log_model_response, log_semantic_analysis_attempt
        )
        print("✅ Logging functions imported successfully")
        
        # Test prompt logging
        print("\n1. Testing prompt logging...")
        test_prompt = "You are a helpful assistant. Please respond to: What is Python?"
        interaction_id = log_model_prompt(
            model_name="test-logging-verification",
            prompt=test_prompt,
            parameters={"temperature": 0.7, "max_tokens": 100},
            context="verification_test"
        )
        print(f"   ✅ Prompt logged with ID: {interaction_id}")
        
        # Test response logging
        print("\n2. Testing response logging...")
        test_response = "Python is a high-level programming language known for its readability and versatility."
        log_model_response(
            interaction_id=interaction_id,
            model_name="test-logging-verification",
            response=test_response,
            duration=2.5,
            context="verification_test"
        )
        print("   ✅ Response logged successfully")
        
        # Test semantic analysis logging
        print("\n3. Testing semantic analysis logging...")
        log_semantic_analysis_attempt(
            interaction_id=f"semantic_{interaction_id}",
            user_input="What is Python?",
            raw_response='{"intent_type": "question", "complexity": "simple", "specialist_needed": "local_shortcuts", "confidence": 0.85}',
            parsed_result={"intent_type": "question", "complexity": "simple", "specialist_needed": "local_shortcuts", "confidence": 0.85},
            zone_info={"detected_zone": "conversational", "zone_confidence": 0.9}
        )
        print("   ✅ Semantic analysis logged successfully")
        
        return True, interaction_id
        
    except Exception as e:
        print(f"❌ Logging function test failed: {e}")
        import traceback
        traceback.print_exc()
        return False, None

def verify_log_content(interaction_id):
    """Verify that the logged content actually appears in files."""
    print(f"\n🔍 VERIFYING LOG CONTENT FOR: {interaction_id}")
    print("-" * 40)
    
    log_dir = Path("logs/model_interactions")
    if not log_dir.exists():
        print("❌ Log directory doesn't exist")
        return False
    
    # Check prompt logs
    prompt_files = list(log_dir.glob("prompts_*.jsonl"))
    prompt_found = False
    
    print("1. Checking prompt logs...")
    for file in prompt_files:
        try:
            with open(file, 'r') as f:
                for line in f:
                    data = json.loads(line.strip())
                    if data.get('interaction_id') == interaction_id:
                        print(f"   ✅ Found prompt in: {file.name}")
                        print(f"      Model: {data.get('model_name')}")
                        print(f"      Prompt length: {data.get('prompt_length')} chars")
                        print(f"      Context: {data.get('context')}")
                        prompt_preview = data.get('prompt_text', '')[:100]
                        print(f"      Preview: {prompt_preview}...")
                        prompt_found = True
                        break
        except Exception as e:
            print(f"   ⚠️ Error reading {file.name}: {e}")
    
    if not prompt_found:
        print("   ❌ Prompt not found in any log file")
    
    # Check response logs
    response_files = list(log_dir.glob("responses_*.jsonl"))
    response_found = False
    
    print("\n2. Checking response logs...")
    for file in response_files:
        try:
            with open(file, 'r') as f:
                for line in f:
                    data = json.loads(line.strip())
                    if data.get('interaction_id') == interaction_id:
                        print(f"   ✅ Found response in: {file.name}")
                        print(f"      Model: {data.get('model_name')}")
                        print(f"      Response length: {data.get('response_length')} chars")
                        print(f"      Duration: {data.get('duration_seconds')}s")
                        response_preview = data.get('response_text', '')[:100]
                        print(f"      Preview: {response_preview}...")
                        response_found = True
                        break
        except Exception as e:
            print(f"   ⚠️ Error reading {file.name}: {e}")
    
    if not response_found:
        print("   ❌ Response not found in any log file")
    
    # Check semantic logs
    semantic_files = list(log_dir.glob("semantic_*.jsonl"))
    semantic_found = False
    
    print("\n3. Checking semantic analysis logs...")
    semantic_id = f"semantic_{interaction_id}"
    for file in semantic_files:
        try:
            with open(file, 'r') as f:
                for line in f:
                    data = json.loads(line.strip())
                    if data.get('interaction_id') == semantic_id:
                        print(f"   ✅ Found semantic analysis in: {file.name}")
                        print(f"      User input: {data.get('user_input')}")
                        print(f"      Parsed result: {data.get('parsed_result')}")
                        print(f"      Zone info: {data.get('zone_info')}")
                        semantic_found = True
                        break
        except Exception as e:
            print(f"   ⚠️ Error reading {file.name}: {e}")
    
    if not semantic_found:
        print("   ❌ Semantic analysis not found in any log file")
    
    return prompt_found and response_found and semantic_found

def main():
    """Main verification process."""
    
    # 1. Check current log file status
    log_dir_exists, recent_files = check_log_files()
    
    # 2. Test logging functions
    functions_work, interaction_id = test_logging_functions()
    
    if not functions_work:
        print("\n❌ CONCLUSION: Logging functions are broken")
        return False
    
    # 3. Verify content was actually written
    content_verified = verify_log_content(interaction_id)
    
    # 4. Check for recent activity
    print(f"\n📊 RECENT ACTIVITY")
    print("-" * 20)
    if recent_files:
        print(f"✅ {len(recent_files)} files modified in last 5 minutes:")
        for file in sorted(recent_files, key=lambda f: f.stat().st_mtime, reverse=True):
            size = file.stat().st_size
            mtime = datetime.fromtimestamp(file.stat().st_mtime)
            age = (datetime.now() - mtime).total_seconds()
            print(f"   - {file.name}: {size} bytes ({age:.0f}s ago)")
    else:
        print("⚠️ No recent file activity detected")
    
    # 5. Final conclusion
    print(f"\n🎯 FINAL CONCLUSION")
    print("=" * 20)
    
    if functions_work and content_verified:
        print("✅ SUCCESS: Enhanced logging is FULLY OPERATIONAL")
        print("   - Prompts are being captured ✅")
        print("   - Model responses are being captured ✅") 
        print("   - Semantic analysis is being captured ✅")
        print("   - Log files are being written correctly ✅")
        return True
    else:
        print("❌ ISSUES DETECTED:")
        if not functions_work:
            print("   - Logging functions are not working ❌")
        if not content_verified:
            print("   - Content is not being written to files ❌")
        return False

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n💥 VERIFICATION CRASHED: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
