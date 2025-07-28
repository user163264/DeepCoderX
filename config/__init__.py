# DEPRECATED - Configuration package no longer needed
# The configuration system has been simplified to a single config_module.py file
# This eliminates sys.path manipulation and cross-file dependencies

# For backward compatibility during transition, redirect to unified config
import warnings
warnings.warn(
    "config package is deprecated. Import directly from config_module instead.",
    DeprecationWarning,
    stacklevel=2
)

# Import from unified config (no sys.path manipulation needed)
from config_module import config, DeepCoderXConfig as Config

# GGUF prompting functionality is now built into the main config
def get_gguf_prompting_config():
    """Get GGUF prompting configuration from unified config."""
    return config.GGUF_PROMPTING_CONFIG

def reload_gguf_prompting_config():
    """Reload GGUF prompting configuration."""
    config._load_prompting_config()

__all__ = [
    'config',
    'Config',
    'get_gguf_prompting_config',
    'reload_gguf_prompting_config'
]
