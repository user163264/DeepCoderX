#!/usr/bin/env python3
"""
Fix model context contamination by clearing all cached models and sessions.
This will force fresh model initialization on next run.
"""

import os
import shutil
from pathlib import Path
import sys

def clear_model_contamination():
    """Clear all model context and session data to fix contamination."""
    
    print("🧹 Fixing model context contamination...")
    
    # 1. Clear all session files
    session_dir = Path("/Users/admin/Documents/DeepCoderX/.deepcoderx")
    if session_dir.exists():
        print(f"   📁 Clearing session directory: {session_dir}")
        shutil.rmtree(session_dir)
        session_dir.mkdir(exist_ok=True)
        print("   ✅ Session files cleared")
    
    # 2. Clear any llama-cpp-python cache
    home_dir = Path.home()
    llama_cache_dirs = [
        home_dir / ".cache" / "llama-cpp-python",
        home_dir / ".llama_cpp",
    ]
    
    for cache_dir in llama_cache_dirs:
        if cache_dir.exists():
            print(f"   📁 Clearing llama cache: {cache_dir}")
            shutil.rmtree(cache_dir)
            print("   ✅ Llama cache cleared")
    
    # 3. Clear any Python __pycache__ that might have cached model instances
    project_dir = Path("/Users/admin/Documents/DeepCoderX")
    for pycache in project_dir.rglob("__pycache__"):
        if pycache.is_dir():
            print(f"   📁 Clearing Python cache: {pycache}")
            shutil.rmtree(pycache)
    
    print("   ✅ Python cache cleared")
    
    # 4. Force garbage collection and memory cleanup
    import gc
    gc.collect()
    print("   ✅ Memory cleanup completed")
    
    print("\n🎉 Model contamination fix completed!")
    print("\n📋 Next steps:")
    print("   1. Launch DeepCoderX: cd /Users/admin/Documents/DeepCoderX && python3 app.py")
    print("   2. Test with: hello")
    print("   3. Expected: Proper greeting response (not Android apps)")
    print("   4. Check logs: Should show single execution (not double)")

if __name__ == "__main__":
    clear_model_contamination()
