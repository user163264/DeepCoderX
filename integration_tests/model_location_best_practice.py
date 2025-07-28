"""
RECOMMENDED MODEL LOCATION CONFIGURATION UPDATE

Update config_module.py _load_gguf_settings() method with best practice model locations.
"""

def _load_gguf_settings(self):
    """Load GGUF model settings with best practice model locations."""
    
    # Model configuration
    self.GGUF_MODEL_NAME = self._get_str_env("DEEPCODERX_GGUF_MODEL_NAME", "qwen2.5-coder-1.5b")
    self.GGUF_QUANTIZATION = self._get_str_env("DEEPCODERX_GGUF_QUANTIZATION", "gguf")
    
    # BEST PRACTICE MODEL LOCATION STRATEGY
    self.GGUF_MODEL_PATH = None
    
    # 1. FIRST PRIORITY: Explicit environment variable override
    custom_path = self._get_str_env("DEEPCODERX_GGUF_MODEL_PATH", None)
    if custom_path:
        model_path = Path(custom_path)
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
            
            # FALLBACK: Other common locations
            Path("/Users/admin/Documents/MyProjects/Project_Genesis/models/qwen-coder") / model_filename,
            Path.home() / "Downloads" / model_filename,
            
            # LAST RESORT: Project directory (not recommended for production)
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
                Path.home() / "models"
            ]
            
            for cache_dir in cache_dirs:
                if cache_dir.exists():
                    for found_file in cache_dir.rglob(f"*{self.GGUF_MODEL_NAME}*.gguf"):
                        self.GGUF_MODEL_PATH = found_file
                        logger.info(f"Found model via search: {found_file}")
                        break
                if self.GGUF_MODEL_PATH:
                    break
    
    # VALIDATION: Ensure model was found
    if not self.GGUF_MODEL_PATH:
        logger.error(f"GGUF model not found: {model_filename}")
        logger.error("Searched locations:")
        for location in search_locations:
            logger.error(f"  - {location}")
        logger.error("\nTo fix this:")
        logger.error(f"1. Download model to: ~/.cache/deepcoderx/models/{model_filename}")
        logger.error(f"2. Or set DEEPCODERX_GGUF_MODEL_PATH environment variable")
        raise FileNotFoundError(f"GGUF model not found: {model_filename}")
    
    # Rest of hardware configuration...
