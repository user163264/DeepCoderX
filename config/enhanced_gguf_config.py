"""
Enhanced GGUF Configuration for DeepCoderX

This module provides configuration options for the enhanced GGUF handler
that uses llama-cpp-python directly.
"""

import os
from pathlib import Path
from typing import Dict, Any, Optional


class EnhancedGGUFConfig:
    """Configuration for enhanced GGUF model handling."""
    
    # Model paths and selection
    DEFAULT_MODEL_NAME = "qwen2.5-coder-1.5b-instruct"
    
    MODEL_PATHS = {
        # Qwen models
        "qwen2.5-coder-1.5b-instruct": {
            "q8_0": "qwen2.5-coder-1.5b-instruct-q8_0.gguf",
            "q6_k": "qwen2.5-coder-1.5b-instruct-q6_k.gguf", 
            "q5_k_m": "qwen2.5-coder-1.5b-instruct-q5_k_m.gguf",
            "q4_k_m": "qwen2.5-coder-1.5b-instruct-q4_k_m.gguf",
        },
        "qwen2.5-coder-7b-instruct": {
            "q8_0": "qwen2.5-coder-7b-instruct-q8_0.gguf",
            "q6_k": "qwen2.5-coder-7b-instruct-q6_k.gguf",
            "q5_k_m": "qwen2.5-coder-7b-instruct-q5_k_m.gguf",
            "q4_k_m": "qwen2.5-coder-7b-instruct-q4_k_m.gguf",
        },
        # CodeLlama models
        "codellama-7b-instruct": {
            "q8_0": "codellama-7b-instruct-q8_0.gguf",
            "q6_k": "codellama-7b-instruct-q6_k.gguf",
            "q5_k_m": "codellama-7b-instruct-q5_k_m.gguf",
            "q4_k_m": "codellama-7b-instruct-q4_k_m.gguf",
        },
        # Mistral models
        "mistral-7b-instruct": {
            "q8_0": "mistral-7b-instruct-v0.2-q8_0.gguf",
            "q6_k": "mistral-7b-instruct-v0.2-q6_k.gguf",
            "q5_k_m": "mistral-7b-instruct-v0.2-q5_k_m.gguf",
            "q4_k_m": "mistral-7b-instruct-v0.2-q4_k_m.gguf",
        }
    }
    
    # Search directories for GGUF models
    MODEL_SEARCH_PATHS = [
        # LM Studio cache
        Path.home() / ".cache" / "lm-studio" / "models",
        # Hugging Face cache  
        Path.home() / ".cache" / "huggingface" / "hub",
        # Local models directory
        Path.home() / "models",
        Path("./models"),
        # DeepCoderX models directory
        Path(__file__).parent.parent / "models",
    ]
    
    # Quantization information
    QUANTIZATION_INFO = {
        "q8_0": {
            "description": "8-bit quantization, highest quality, larger size",
            "relative_size": 1.0,
            "quality": "Highest",
            "speed": "Slower"
        },
        "q6_k": {
            "description": "6-bit quantization, very high quality, medium size", 
            "relative_size": 0.75,
            "quality": "Very High",
            "speed": "Medium"
        },
        "q5_k_m": {
            "description": "5-bit quantization, high quality, good balance",
            "relative_size": 0.625,
            "quality": "High", 
            "speed": "Good"
        },
        "q4_k_m": {
            "description": "4-bit quantization, good quality, smaller size",
            "relative_size": 0.5,
            "quality": "Good",
            "speed": "Fast"
        }
    }
    
    # Hardware-specific configurations
    HARDWARE_CONFIGS = {
        "apple_silicon": {
            "n_gpu_layers": -1,  # Use all Metal layers
            "n_batch": 512,
            "n_threads": None,  # Auto-detect
            "use_mmap": True,
            "use_mlock": False,
            "f16_kv": True,
        },
        "nvidia_gpu": {
            "n_gpu_layers": -1,  # Use all CUDA layers
            "n_batch": 512, 
            "n_threads": None,  # Auto-detect
            "use_mmap": True,
            "use_mlock": False,
            "f16_kv": True,
        },
        "cpu_only": {
            "n_gpu_layers": 0,
            "n_batch": 256,  # Smaller batch for CPU
            "n_threads": None,  # Auto-detect
            "use_mmap": True,
            "use_mlock": False,
            "f16_kv": True,
        },
        "low_memory": {
            "n_gpu_layers": 0,
            "n_batch": 128,  # Very small batch
            "n_threads": 4,   # Limited threads
            "use_mmap": False,  # Don't use memory mapping
            "use_mlock": False,
            "f16_kv": True,
            "n_ctx": 2048,  # Smaller context
        }
    }
    
    # Generation parameters
    DEFAULT_GENERATION_PARAMS = {
        "temperature": 0.0,  # Maximum instruction following
        "top_p": 0.95,
        "top_k": 40,
        "repeat_penalty": 1.1,
        "max_tokens": 2048,
        "stop": ["Human:", "User:", "\n\n---", "```\n\n"],
    }
    
    @classmethod
    def find_model_path(cls, model_name: str, quantization: str = "q8_0") -> Optional[Path]:
        """Find the path to a GGUF model file."""
        if model_name not in cls.MODEL_PATHS:
            return None
            
        if quantization not in cls.MODEL_PATHS[model_name]:
            return None
            
        filename = cls.MODEL_PATHS[model_name][quantization]
        
        # Search in all possible locations
        for search_path in cls.MODEL_SEARCH_PATHS:
            if not search_path.exists():
                continue
                
            # Direct file check
            model_file = search_path / filename
            if model_file.exists():
                return model_file
            
            # Search recursively in subdirectories
            for model_file in search_path.rglob(filename):
                return model_file
        
        return None
    
    @classmethod
    def get_available_models(cls) -> Dict[str, Dict[str, bool]]:
        """Get a dictionary of available models and their quantizations."""
        available = {}
        
        for model_name, quantizations in cls.MODEL_PATHS.items():
            available[model_name] = {}
            for quant_name in quantizations.keys():
                model_path = cls.find_model_path(model_name, quant_name)
                available[model_name][quant_name] = model_path is not None
        
        return available
    
    @classmethod
    def detect_hardware_config(cls) -> str:
        """Detect the best hardware configuration for the current system."""
        import platform
        
        system = platform.system()
        
        # Check for Apple Silicon
        if system == "Darwin":
            try:
                import subprocess
                result = subprocess.run(
                    ["sysctl", "-n", "machdep.cpu.brand_string"], 
                    capture_output=True, text=True
                )
                if "Apple" in result.stdout:
                    return "apple_silicon"
            except:
                pass
        
        # Check for NVIDIA GPU
        try:
            import subprocess
            result = subprocess.run(["nvidia-smi"], capture_output=True, text=True)
            if result.returncode == 0:
                return "nvidia_gpu"
        except FileNotFoundError:
            pass
        
        # Check available memory for low memory systems
        try:
            import psutil
            memory_gb = psutil.virtual_memory().total / (1024**3)
            if memory_gb < 8:
                return "low_memory"
        except ImportError:
            pass
        
        # Default to CPU
        return "cpu_only"
    
    @classmethod
    def get_model_config(cls, hardware_type: Optional[str] = None) -> Dict[str, Any]:
        """Get model configuration for the specified hardware type."""
        if hardware_type is None:
            hardware_type = cls.detect_hardware_config()
        
        config = cls.HARDWARE_CONFIGS.get(hardware_type, cls.HARDWARE_CONFIGS["cpu_only"]).copy()
        
        # Add context window if not specified
        if "n_ctx" not in config:
            config["n_ctx"] = 4096
        
        return config
    
    @classmethod
    def get_generation_params(cls, **overrides) -> Dict[str, Any]:
        """Get generation parameters with optional overrides."""
        params = cls.DEFAULT_GENERATION_PARAMS.copy()
        params.update(overrides)
        return params


# Environment variable overrides
ENHANCED_GGUF_MODEL = os.getenv("ENHANCED_GGUF_MODEL", EnhancedGGUFConfig.DEFAULT_MODEL_NAME)
ENHANCED_GGUF_QUANTIZATION = os.getenv("ENHANCED_GGUF_QUANTIZATION", "q8_0")
ENHANCED_GGUF_HARDWARE = os.getenv("ENHANCED_GGUF_HARDWARE")  # Auto-detect if not set
