#!/usr/bin/env python3
"""
MODEL SETUP HELPER FOR DEEPCODERX

Creates recommended model directory structure and helps locate/move existing models.
Follows best practices for model storage.
"""

import os
import shutil
from pathlib import Path
import logging

def setup_logging():
    """Setup logging for model setup."""
    logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
    return logging.getLogger(__name__)

def create_model_directories():
    """Create recommended model directory structure."""
    logger = logging.getLogger(__name__)
    
    recommended_dirs = [
        Path.home() / ".cache" / "deepcoderx" / "models",
        Path.home() / ".cache" / "deepcoderx" / "config",
        Path.home() / ".cache" / "deepcoderx" / "logs"
    ]
    
    logger.info("🏗️ Creating recommended directory structure...")
    
    for directory in recommended_dirs:
        try:
            directory.mkdir(parents=True, exist_ok=True)
            logger.info(f"✅ Created: {directory}")
        except Exception as e:
            logger.error(f"❌ Failed to create {directory}: {e}")
            return False
    
    return True

def find_existing_models():
    """Find existing GGUF models in common locations."""
    logger = logging.getLogger(__name__)
    
    search_locations = [
        Path("/Users/admin/Documents/MyProjects/Project_Genesis/models"),
        Path.home() / "Downloads",
        Path.home() / "models",
        Path.home() / ".cache" / "lm-studio" / "models",
        Path.home() / ".cache" / "huggingface" / "hub",
        Path("/Users/admin/Documents/DeepCoderX")
    ]
    
    found_models = []
    
    logger.info("🔍 Searching for existing GGUF models...")
    
    for location in search_locations:
        if location.exists():
            try:
                for model_file in location.rglob("*.gguf"):
                    size_gb = model_file.stat().st_size / (1024**3)
                    found_models.append({
                        'path': model_file,
                        'size_gb': size_gb,
                        'name': model_file.name
                    })
                    logger.info(f"📁 Found: {model_file.name} ({size_gb:.1f}GB) at {model_file.parent}")
            except Exception as e:
                logger.warning(f"⚠️ Error searching {location}: {e}")
    
    return found_models

def move_model_to_recommended_location(model_path, target_name=None):
    """Move a model to the recommended cache location."""
    logger = logging.getLogger(__name__)
    
    if not target_name:
        target_name = model_path.name
    
    recommended_location = Path.home() / ".cache" / "deepcoderx" / "models" / target_name
    
    try:
        if recommended_location.exists():
            logger.warning(f"⚠️ Target already exists: {recommended_location}")
            return False
        
        logger.info(f"📦 Moving {model_path.name} to recommended location...")
        shutil.move(str(model_path), str(recommended_location))
        logger.info(f"✅ Moved to: {recommended_location}")
        return recommended_location
        
    except Exception as e:
        logger.error(f"❌ Failed to move model: {e}")
        return False

def create_model_symlink(source_path, target_name):
    """Create a symlink in the recommended location pointing to existing model."""
    logger = logging.getLogger(__name__)
    
    recommended_location = Path.home() / ".cache" / "deepcoderx" / "models" / target_name
    
    try:
        if recommended_location.exists():
            logger.warning(f"⚠️ Target already exists: {recommended_location}")
            return False
        
        logger.info(f"🔗 Creating symlink for {source_path.name}...")
        recommended_location.symlink_to(source_path)
        logger.info(f"✅ Symlink created: {recommended_location} -> {source_path}")
        return recommended_location
        
    except Exception as e:
        logger.error(f"❌ Failed to create symlink: {e}")
        return False

def setup_qwen_model():
    """Interactive setup for Qwen model."""
    logger = logging.getLogger(__name__)
    
    logger.info("\n🎯 QWEN MODEL SETUP")
    logger.info("=" * 40)
    
    # Find existing models
    found_models = find_existing_models()
    qwen_models = [m for m in found_models if 'qwen' in m['name'].lower()]
    
    if qwen_models:
        logger.info(f"Found {len(qwen_models)} Qwen model(s):")
        for i, model in enumerate(qwen_models):
            logger.info(f"  {i+1}. {model['name']} ({model['size_gb']:.1f}GB)")
            logger.info(f"     Location: {model['path']}")
        
        # Use the first Qwen model found
        selected_model = qwen_models[0]
        logger.info(f"\n📌 Using: {selected_model['name']}")
        
        # Create symlink to recommended location
        target_name = "qwen2.5-coder-1.5b.gguf"
        result = create_model_symlink(selected_model['path'], target_name)
        
        if result:
            logger.info(f"✅ Qwen model ready at: {result}")
            return result
        else:
            logger.error("❌ Failed to set up Qwen model")
            return None
    else:
        logger.warning("⚠️ No Qwen models found in common locations")
        logger.info("\n📋 To get a Qwen model:")
        logger.info("1. Download from HuggingFace:")
        logger.info("   wget https://huggingface.co/Qwen/Qwen2.5-Coder-1.5B-Instruct-GGUF/resolve/main/qwen2.5-coder-1.5b-instruct-q4_k_m.gguf")
        logger.info("2. Move to: ~/.cache/deepcoderx/models/qwen2.5-coder-1.5b.gguf")
        return None

def create_env_file_example():
    """Create example environment file with model configuration."""
    logger = logging.getLogger(__name__)
    
    env_example = """# DEEPCODERX MODEL CONFIGURATION

# Recommended: Use default cache location
# DEEPCODERX_GGUF_MODEL_PATH=~/.cache/deepcoderx/models/qwen2.5-coder-1.5b.gguf

# Alternative: Specify custom location
# DEEPCODERX_GGUF_MODEL_PATH=/path/to/your/model.gguf

# Model selection
DEEPCODERX_GGUF_MODEL_NAME=qwen2.5-coder-1.5b

# Other settings...
DEEPCODERX_DEBUG_MODE=true
"""
    
    env_file = Path.home() / ".cache" / "deepcoderx" / "config" / "model.env.example"
    
    try:
        with open(env_file, 'w') as f:
            f.write(env_example)
        logger.info(f"✅ Created example config: {env_file}")
    except Exception as e:
        logger.error(f"❌ Failed to create example config: {e}")

def main():
    """Main model setup process."""
    logger = setup_logging()
    
    logger.info("🚀 DEEPCODERX MODEL SETUP")
    logger.info("=" * 50)
    
    # Step 1: Create directory structure
    if not create_model_directories():
        logger.error("❌ Failed to create directories")
        return 1
    
    # Step 2: Find and setup models
    qwen_path = setup_qwen_model()
    
    # Step 3: Create example configuration
    create_env_file_example()
    
    # Step 4: Summary
    logger.info("\n🎉 SETUP SUMMARY")
    logger.info("=" * 30)
    
    if qwen_path:
        logger.info(f"✅ Qwen model ready: {qwen_path}")
        logger.info("✅ Directory structure created")
        logger.info("✅ Configuration example created")
        logger.info("\n📋 Next steps:")
        logger.info("1. Update DeepCoderX configuration to use standard location")
        logger.info("2. Test model loading with integration tests")
        return 0
    else:
        logger.error("⚠️ Qwen model not set up")
        logger.info("📋 Manual steps required:")
        logger.info("1. Download Qwen model to ~/.cache/deepcoderx/models/")
        logger.info("2. Update DEEPCODERX_GGUF_MODEL_PATH if needed")
        return 1

if __name__ == "__main__":
    exit_code = main()
    exit(exit_code)
