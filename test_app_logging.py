#!/usr/bin/env python3
"""
Test DeepCoderX Logging Integration

Run a simple command through DeepCoderX to verify the enhanced logging
is working in the actual application.
"""

import os
import subprocess
import sys
from pathlib import Path

# Enable full logging
os.environ.update({
    "DEEPCODERX_LOG_MODEL_PROMPTS": "true",
    "DEEPCODERX_LOG_MODEL_RESPONSES": "true",
    "DEEPCODERX_LOG_SEMANTIC_DETAILS": "true",
    "DEEPCODERX_LOG_TOOL_DETAILS": "true",
    "DEEPCODERX_LOG_CONVERSATION_CONTEXT": "true",
    "DEEPCODERX_DEBUG_MODE": "true"
})

print("🔧 Testing DeepCoderX Application Logging")
print("=" * 50)

try:
    # Get initial log file count
    log_dir = Path("logs/model_interactions")
    initial_files = list(log_dir.glob("*.jsonl")) if log_dir.exists() else []
    initial_count = len(initial_files)
    print(f"Initial log files: {initial_count}")

    # Run a simple command through DeepCoderX
    print("\n1. Running simple command: 'hello'")
    
    # Create input file for non-interactive test
    test_input = "hello\nexit\n"
    
    # Run DeepCoderX with the test input
    process = subprocess.Popen(
        [sys.executable, "app.py"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        cwd=Path.cwd()
    )
    
    stdout, stderr = process.communicate(input=test_input, timeout=30)
    
    print(f"   Return code: {process.returncode}")
    
    if stdout:
        print("   Stdout:")
        print("   " + "\n   ".join(stdout.split('\n')[:10]))  # First 10 lines
    
    if stderr:
        print("   Stderr:")
        print("   " + "\n   ".join(stderr.split('\n')[:5]))   # First 5 lines

    # Check for new log files
    print("\n2. Checking for new log files...")
    current_files = list(log_dir.glob("*.jsonl")) if log_dir.exists() else []
    current_count = len(current_files)
    
    print(f"   Files after test: {current_count}")
    print(f"   New files created: {current_count - initial_count}")
    
    # Find newest files (created in last minute)
    import time
    current_time = time.time()
    recent_files = []
    
    for file in current_files:
        file_time = file.stat().st_mtime
        if current_time - file_time < 60:  # Files created in last minute
            recent_files.append(file)
    
    if recent_files:
        print(f"\n3. Recent log files ({len(recent_files)}):")
        for file in sorted(recent_files):
            size = file.stat().st_size
            print(f"   - {file.name}: {size} bytes")
            
            # Show last few lines
            if size > 0:
                try:
                    with open(file, 'r') as f:
                        lines = f.readlines()
                        print(f"     Entries: {len(lines)}")
                        if lines:
                            # Show first entry
                            print(f"     Sample: {lines[-1].strip()[:100]}...")
                except Exception as e:
                    print(f"     Error reading: {e}")
    else:
        print("\n3. No recent log files found")

    print("\n🎉 Application logging test completed!")
    
    if recent_files:
        print("✅ Enhanced logging is working with the application")
    else:
        print("⚠️  No recent logs detected - check if application ran correctly")

except subprocess.TimeoutExpired:
    print("❌ Test timed out")
    process.kill()
except Exception as e:
    print(f"❌ Test failed: {e}")
    import traceback
    traceback.print_exc()
