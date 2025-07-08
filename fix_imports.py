#!/usr/bin/env python3
"""
Fix the import error by clearing Python cache and verifying the fix.
"""

import os
import sys
import shutil
from pathlib import Path

def remove_cache_files():
    """Remove all Python cache files."""
    project_root = Path(__file__).parent
    cache_dirs_removed = 0
    pyc_files_removed = 0
    
    print("🧹 Cleaning Python cache files...")
    
    # Remove __pycache__ directories
    for cache_dir in project_root.rglob("__pycache__"):
        try:
            shutil.rmtree(cache_dir)
            cache_dirs_removed += 1
            print(f"   Removed: {cache_dir}")
        except Exception as e:
            print(f"   Warning: Could not remove {cache_dir}: {e}")
    
    # Remove .pyc files
    for pyc_file in project_root.rglob("*.pyc"):
        try:
            pyc_file.unlink()
            pyc_files_removed += 1
            print(f"   Removed: {pyc_file}")
        except Exception as e:
            print(f"   Warning: Could not remove {pyc_file}: {e}")
    
    print(f"✅ Cleaned {cache_dirs_removed} cache directories and {pyc_files_removed} .pyc files")

def verify_imports():
    """Verify that imports work correctly."""
    print("\n🔍 Verifying imports...")
    
    try:
        print("   Testing config_module import...")
        from config_module import config
        print("   ✅ config_module import successful")
        
        print("   Testing app.py import...")
        import app
        print("   ✅ app.py import successful")
        
        print("   Testing config object attributes...")
        if hasattr(config, 'DEFAULT_PROVIDER'):
            print(f"   ✅ config.DEFAULT_PROVIDER = {config.DEFAULT_PROVIDER}")
        else:
            print("   ❌ config.DEFAULT_PROVIDER not found")
            
        return True
        
    except ImportError as e:
        print(f"   ❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"   ❌ Other error: {e}")
        return False

def main():
    print("DeepCoderX Import Fix")
    print("=" * 50)
    
    # Step 1: Remove cache files
    remove_cache_files()
    
    # Step 2: Verify imports
    success = verify_imports()
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 SUCCESS! Import fix applied successfully.")
        print("You should now be able to run: deepcoderx")
    else:
        print("❌ Import issues still remain.")
        print("Please check the error messages above.")
    print("=" * 50)

if __name__ == "__main__":
    main()
