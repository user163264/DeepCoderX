#!/usr/bin/env python3
"""
RECOMMENDED CONFIGURATION UPDATE FOR BEST PRACTICE MODEL LOCATIONS

This script will backup the current config and update it with best practice model locations.
"""

import sys
from pathlib import Path
import logging

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def backup_and_update_config():
    """Backup current config and update with best practice model locations."""
    logger = logging.getLogger(__name__)
    
    config_file = project_root / "config_module.py"
    
    # Create backup
    backup_file = project_root / "config_module.py.BAK6"
    
    try:
        import shutil
        shutil.copy2(config_file, backup_file)
        logger.info(f"✅ Backup created: {backup_file}")
    except Exception as e:
        logger.error(f"❌ Failed to create backup: {e}")
        return False
    
    # Read current config
    try:
        with open(config_file, 'r') as f:
            content = f.read()
    except Exception as e:
        logger.error(f"❌ Failed to read config: {e}")
        return False
    
    # Find and replace the _load_gguf_settings method
    old_method_start = "def _load_gguf_settings(self):"
    old_method_end = "# Legacy compatibility - LOCAL_MODEL_PATH"
    
    new_method = '''def _load_gguf_settings(self):
        """Load GGUF model settings with best practice model locations - QWEN OPTIMIZED."""
        
        # GGUF model configuration - DIRECT INFERENCE ONLY
        self.GGUF_MODEL_NAME = self._get_str_env("DEEPCODERX_GGUF_MODEL_NAME", "qwen2.5-coder-1.5b")
        self.GGUF_QUANTIZATION = self._get_str_env("DEEPCODERX_GGUF_QUANTIZATION", "gguf")
        
        # BEST PRACTICE MODEL LOCATION STRATEGY
        self.GGUF_MODEL_PATH = None
        
        # 1. FIRST PRIORITY: Explicit environment variable override
        custom_path = self._get_str_env("DEEPCODERX_GGUF_MODEL_PATH", None)
        if custom_path:
            model_path = Path(custom_path).expanduser()
            if model_path.exists():
                self.GGUF_MODEL_PATH = model_path
                logger.info(f"Using explicit model path: {self.GGUF_MODEL_PATH}")
        
        if not self.GGUF_MODEL_PATH:
            # 2. STANDARD LOCATIONS (Best Practice Priority Order)
            model_filename = f"{self.GGUF_MODEL_NAME}.gguf"
            
            search_locations = [
                # RECOMMENDED: User cache directory (XDG standard)
                Path.home() / ".cache" / "deepcoderx" / "models" / model_filename,
                
                # ALTERNATIVE: User models directory
                Path.home() / "models" / model_filename,
                
                # COMMON: HuggingFace cache location
                Path.home() / ".cache" / "huggingface" / "hub" / model_filename,
                
                # COMMON: LM Studio models location
                Path.home() / ".cache" / "lm-studio" / "models" / model_filename,
                
                # FALLBACK: Legacy location from previous config
                Path("/Users/admin/Documents/MyProjects/Project_Genesis/models/qwen-coder/qwen2.5-coder-1.5b.gguf"),
                
                # FALLBACK: Downloads folder
                Path.home() / "Downloads" / model_filename,
                
                # LAST RESORT: Project directory (not recommended)
                Path(__file__).parent / "models" / model_filename
            ]
            
            # Search for model file
            for location in search_locations:
                if location.exists():
                    self.GGUF_MODEL_PATH = location
                    logger.info(f"Found model at: {location}")
                    break
            
            # If still not found, try recursive search in cache directories
            if not self.GGUF_MODEL_PATH:
                cache_dirs = [
                    Path.home() / ".cache" / "deepcoderx",
                    Path.home() / ".cache" / "lm-studio",
                    Path.home() / "models",
                    Path("/Users/admin/Documents/MyProjects/Project_Genesis/models")
                ]
                
                for cache_dir in cache_dirs:
                    if cache_dir.exists():
                        # Look for any qwen model files
                        for found_file in cache_dir.rglob("*qwen*.gguf"):
                            self.GGUF_MODEL_PATH = found_file
                            logger.info(f"Found Qwen model via search: {found_file}")
                            break
                    if self.GGUF_MODEL_PATH:
                        break
        
        # VALIDATION: Ensure model was found or provide helpful guidance
        if not self.GGUF_MODEL_PATH:
            logger.error(f"GGUF model not found: {self.GGUF_MODEL_NAME}.gguf")
            logger.error("Searched locations:")
            for location in search_locations:
                logger.error(f"  - {location}")
            logger.error("\\nTo fix this:")
            logger.error(f"1. RECOMMENDED: Download model to ~/.cache/deepcoderx/models/{self.GGUF_MODEL_NAME}.gguf")
            logger.error(f"2. OR set DEEPCODERX_GGUF_MODEL_PATH environment variable")
            logger.error(f"3. OR run: python integration_tests/setup_model_directories.py")
            
            # Don't raise error in development, just warn
            logger.warning("Continuing with None model path - update before actual usage")
        
        # GGUF hardware configuration - QWEN 1.5B OPTIMIZED FOR APPLE SILICON
        self.GGUF_HARDWARE_CONFIG = {
            "n_gpu_layers": -1,        # Use all Metal layers on Apple Silicon
            "n_batch": 256,           # Smaller batch for 1.5B model
            "n_ctx": 4096,            # Full context window
            "n_threads": 8,           # Optimal for Apple Silicon
            "use_mmap": True,         # Fast loading
            "use_mlock": False,       # Don't lock all memory
            "f16_kv": True,           # Half precision KV cache
            "rope_freq_base": 10000.0, # Qwen-specific rope frequency
            "mul_mat_q": True,        # Quantized matrix multiplication
            "offload_kqv": True,      # Offload KQV to GPU
            "verbose": self._get_bool_env("DEEPCODERX_DEBUG_MODE", True)
        }
        
        # GGUF generation parameters - QWEN CODER OPTIMIZED
        self.GGUF_GENERATION_PARAMS = {
            "temperature": 0.0,        # Maximum instruction following for Qwen
            "top_p": 0.85,            # Slightly more focused for code tasks
            "top_k": 40,              # Standard value
            "repeat_penalty": 1.05,   # Reduce repetition (Qwen tends to repeat)
            "max_tokens": 2048,       # Standard max tokens
            "stop": ["Human:", "User:", "\\n\\n---", "```\\n\\n", "Assistant:", "<|endoftext|>"]  # Qwen-specific stops
        }
        
        # Qwen-specific prompting settings
        self.QWEN_OPTIMIZATION = {
            "code_specialization": True,    # Leverage Qwen's code training
            "progressive_intensity": True,  # Escalate prompt intensity on failures
            "max_intensity_level": 5,      # Maximum escalation level
            "tool_call_emphasis": True,     # Extra emphasis on tool call format
            "compiler_analogy": True,       # Use programming analogies
            "visual_separators": "🔥🔥🔥",   # Visual emphasis separators
        }
        
        # Legacy compatibility - LOCAL_MODEL_PATH'''
    
    # Replace the method
    try:
        start_pos = content.find(old_method_start)
        if start_pos == -1:
            logger.error("❌ Could not find _load_gguf_settings method")
            return False
        
        end_pos = content.find(old_method_end, start_pos)
        if end_pos == -1:
            logger.error("❌ Could not find end of _load_gguf_settings method")
            return False
        
        # Include the legacy compatibility line
        end_pos += len(old_method_end)
        
        new_content = content[:start_pos] + new_method + content[end_pos:]
        
        # Write updated config
        with open(config_file, 'w') as f:
            f.write(new_content)
        
        logger.info("✅ Configuration updated with best practice model locations")
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to update config: {e}")
        # Restore backup
        try:
            shutil.copy2(backup_file, config_file)
            logger.info("✅ Backup restored")
        except:
            logger.error("❌ Failed to restore backup")
        return False

def main():
    """Update configuration with best practice model locations."""
    logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
    logger = logging.getLogger(__name__)
    
    logger.info("🔧 UPDATING CONFIG WITH BEST PRACTICE MODEL LOCATIONS")
    logger.info("=" * 60)
    
    success = backup_and_update_config()
    
    if success:
        logger.info("\\n🎉 CONFIGURATION UPDATE COMPLETE")
        logger.info("=" * 40)
        logger.info("✅ Backup created: config_module.py.BAK6")
        logger.info("✅ Configuration updated with best practice locations")
        logger.info("✅ Supports XDG cache directory standard")
        logger.info("✅ Fallback search in multiple locations")
        logger.info("✅ Helpful error messages with setup guidance")
        logger.info("\\n📋 Next steps:")
        logger.info("1. Run: python integration_tests/setup_model_directories.py")
        logger.info("2. Run: python integration_tests/qwen_practical_test.py")
        return 0
    else:
        logger.error("\\n❌ CONFIGURATION UPDATE FAILED")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
