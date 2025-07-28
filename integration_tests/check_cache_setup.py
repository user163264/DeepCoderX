#!/usr/bin/env python3
"""
CACHE DIRECTORY CHECKER AND SETUP

Checks for existing .cache directory and sets up model storage structure.
Run this to see what cache directories exist and create the recommended structure.
"""

import os
from pathlib import Path
import subprocess

def check_cache_directories():
    """Check what cache directories already exist."""
    print("🔍 CHECKING EXISTING CACHE DIRECTORIES")
    print("=" * 40)
    
    cache_base = Path.home() / ".cache"
    
    if cache_base.exists():
        print(f"✅ .cache directory exists: {cache_base}")
        
        # List existing cache contents
        try:
            subdirs = [d for d in cache_base.iterdir() if d.is_dir()]
            if subdirs:
                print(f"\n📁 Existing cache subdirectories ({len(subdirs)}):")
                for subdir in sorted(subdirs)[:10]:  # Show first 10
                    size_info = ""
                    try:
                        # Get directory size info if possible
                        result = subprocess.run(['du', '-sh', str(subdir)], 
                                              capture_output=True, text=True, timeout=5)
                        if result.returncode == 0:
                            size_info = f" ({result.stdout.split()[0]})"
                    except:
                        pass
                    print(f"   - {subdir.name}{size_info}")
                
                if len(subdirs) > 10:
                    print(f"   ... and {len(subdirs) - 10} more")
            else:
                print("\n📁 .cache directory is empty")
                
        except Exception as e:
            print(f"⚠️ Could not list cache contents: {e}")
    else:
        print(f"❌ .cache directory does not exist: {cache_base}")
        print("   (This is normal - we'll create it)")
    
    # Check for ML/AI related cache directories
    ai_cache_dirs = [
        cache_base / "huggingface",
        cache_base / "lm-studio", 
        cache_base / "ollama",
        cache_base / "pytorch",
        cache_base / "transformers"
    ]
    
    print(f"\n🤖 AI/ML Cache Directories:")
    for ai_dir in ai_cache_dirs:
        if ai_dir.exists():
            try:
                result = subprocess.run(['du', '-sh', str(ai_dir)], 
                                      capture_output=True, text=True, timeout=5)
                size_info = f" ({result.stdout.split()[0]})" if result.returncode == 0 else ""
                print(f"   ✅ {ai_dir.name}{size_info}")
            except:
                print(f"   ✅ {ai_dir.name}")
        else:
            print(f"   ❌ {ai_dir.name}")

def create_deepcoderx_cache():
    """Create DeepCoderX cache directory structure."""
    print(f"\n🏗️ CREATING DEEPCODERX CACHE STRUCTURE")
    print("=" * 40)
    
    deepcoderx_dirs = [
        Path.home() / ".cache" / "deepcoderx" / "models",
        Path.home() / ".cache" / "deepcoderx" / "config", 
        Path.home() / ".cache" / "deepcoderx" / "logs",
        Path.home() / ".cache" / "deepcoderx" / "temp"
    ]
    
    created_dirs = []
    
    for directory in deepcoderx_dirs:
        try:
            directory.mkdir(parents=True, exist_ok=True)
            print(f"✅ Created: {directory}")
            created_dirs.append(directory)
        except Exception as e:
            print(f"❌ Failed to create {directory}: {e}")
    
    return created_dirs

def find_existing_models():
    """Find existing GGUF models in common locations."""
    print(f"\n🔍 SEARCHING FOR EXISTING GGUF MODELS")
    print("=" * 40)
    
    search_locations = [
        Path.home() / "Downloads",
        Path.home() / "Documents",
        Path.home() / "Desktop",
        Path("/Users/admin/Documents/MyProjects/Project_Genesis/models"),
        Path.home() / ".cache" / "lm-studio" / "models",
        Path.home() / ".cache" / "huggingface" / "hub"
    ]
    
    found_models = []
    
    for location in search_locations:
        if location.exists():
            try:
                print(f"🔍 Searching: {location}")
                gguf_files = list(location.rglob("*.gguf"))
                
                for model_file in gguf_files:
                    try:
                        size_gb = model_file.stat().st_size / (1024**3)
                        found_models.append({
                            'path': model_file,
                            'size_gb': size_gb,
                            'name': model_file.name,
                            'location': location
                        })
                        print(f"   📁 Found: {model_file.name} ({size_gb:.1f}GB)")
                    except Exception as e:
                        print(f"   ⚠️ Error checking {model_file.name}: {e}")
                        
            except Exception as e:
                print(f"   ⚠️ Could not search {location}: {e}")
    
    return found_models

def show_copy_commands(found_models):
    """Show commands to copy models to cache directory."""
    if not found_models:
        print(f"\n❌ No GGUF models found to copy")
        return
    
    print(f"\n📋 COPY COMMANDS FOR FOUND MODELS")
    print("=" * 40)
    
    cache_models_dir = Path.home() / ".cache" / "deepcoderx" / "models"
    
    qwen_models = [m for m in found_models if 'qwen' in m['name'].lower()]
    other_models = [m for m in found_models if 'qwen' not in m['name'].lower()]
    
    if qwen_models:
        print("🎯 QWEN MODELS (for DeepCoderX):")
        for model in qwen_models:
            target_name = "qwen2.5-coder-1.5b.gguf"  # Standardized name
            print(f"   cp '{model['path']}' '{cache_models_dir}/{target_name}'")
    
    if other_models:
        print(f"\n🤖 OTHER MODELS:")
        for model in other_models[:5]:  # Show first 5
            print(f"   cp '{model['path']}' '{cache_models_dir}/{model['name']}'")
        
        if len(other_models) > 5:
            print(f"   ... and {len(other_models) - 5} more models")

def show_download_instructions():
    """Show instructions for downloading Qwen model if not found."""
    print(f"\n📥 DOWNLOAD QWEN MODEL (if not found)")
    print("=" * 40)
    
    cache_models_dir = Path.home() / ".cache" / "deepcoderx" / "models"
    
    print("If no Qwen model was found, download one:")
    print()
    print("Option 1 - HuggingFace (recommended):")
    print(f"   cd '{cache_models_dir}'")
    print("   wget https://huggingface.co/Qwen/Qwen2.5-Coder-1.5B-Instruct-GGUF/resolve/main/qwen2.5-coder-1.5b-instruct-q4_k_m.gguf")
    print("   mv qwen2.5-coder-1.5b-instruct-q4_k_m.gguf qwen2.5-coder-1.5b.gguf")
    print()
    print("Option 2 - Smaller model:")
    print(f"   cd '{cache_models_dir}'")
    print("   wget https://huggingface.co/Qwen/Qwen2.5-Coder-0.5B-Instruct-GGUF/resolve/main/qwen2.5-coder-0.5b-instruct-q4_k_m.gguf")
    print("   mv qwen2.5-coder-0.5b-instruct-q4_k_m.gguf qwen2.5-coder-1.5b.gguf")

def main():
    """Main cache setup process."""
    print("🚀 DEEPCODERX CACHE DIRECTORY SETUP")
    print("=" * 50)
    
    # Check existing cache
    check_cache_directories()
    
    # Create DeepCoderX structure
    created_dirs = create_deepcoderx_cache()
    
    # Find existing models
    found_models = find_existing_models()
    
    # Show copy commands
    show_copy_commands(found_models)
    
    # Show download instructions
    show_download_instructions()
    
    # Summary
    print(f"\n🎉 SETUP SUMMARY")
    print("=" * 30)
    print(f"✅ Created {len(created_dirs)} cache directories")
    print(f"🔍 Found {len(found_models)} GGUF models")
    
    cache_models_dir = Path.home() / ".cache" / "deepcoderx" / "models"
    print(f"\n📁 Target directory: {cache_models_dir}")
    
    qwen_models = [m for m in found_models if 'qwen' in m['name'].lower()]
    if qwen_models:
        print(f"🎯 Ready to copy {len(qwen_models)} Qwen model(s)")
        print("\n📋 Next steps:")
        print("1. Run the copy commands shown above")
        print("2. Run: python integration_tests/qwen_practical_test.py")
    else:
        print("⚠️ No Qwen models found - download required")
        print("\n📋 Next steps:")
        print("1. Use download commands shown above")
        print("2. Or manually copy existing Qwen model to cache directory")

if __name__ == "__main__":
    main()
