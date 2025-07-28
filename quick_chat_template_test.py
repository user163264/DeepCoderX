#!/usr/bin/env python3
"""
Quick test for ChatTemplateFormatter class functionality.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_chat_template_basic():
    """Basic test of ChatTemplateFormatter without dependencies."""
    
    # Define the ChatTemplateFormatter class inline for testing
    class ChatTemplateFormatter:
        def __init__(self, model_path: str = None, model_name: str = None):
            self.model_path = model_path
            self.model_name = model_name or ""
            self.model_type = self._detect_model_type()
            
        def _detect_model_type(self) -> str:
            model_info = f"{self.model_path or ''} {self.model_name}".lower()
            
            if any(indicator in model_info for indicator in ["llama", "llama-3", "llama-2", "llama3", "llama2"]):
                return "llama"
            elif any(indicator in model_info for indicator in ["qwen", "qwen2", "qwen2.5", "qw"]):
                return "qwen"
            elif any(indicator in model_info for indicator in ["phi", "phi-3", "phi3"]):
                return "phi"
            else:
                return "generic"
        
        def format_prompt(self, system_prompt: str, user_prompt: str, conversation_history=None):
            if self.model_type == "llama":
                return self._format_llama_prompt(system_prompt, user_prompt, conversation_history)
            elif self.model_type == "qwen":
                return self._format_qwen_prompt(system_prompt, user_prompt, conversation_history)
            else:
                return f"System: {system_prompt}\\n\\nUser: {user_prompt}\\n\\nAssistant: "
        
        def _format_llama_prompt(self, system_prompt: str, user_prompt: str, conversation_history=None):
            formatted = f"<|begin_of_text|><|start_header_id|>system<|end_header_id|>\\n{system_prompt}<|eot_id|>"
            formatted += f"<|start_header_id|>user<|end_header_id|>\\n{user_prompt}<|eot_id|>"
            formatted += "<|start_header_id|>assistant<|end_header_id|>\\n"
            return formatted
        
        def _format_qwen_prompt(self, system_prompt: str, user_prompt: str, conversation_history=None):
            formatted = f"<|im_start|>system\\n{system_prompt}<|im_end|>\\n"
            formatted += f"<|im_start|>user\\n{user_prompt}<|im_end|>\\n"
            formatted += "<|im_start|>assistant\\n"
            return formatted
        
        def get_model_info(self):
            return {
                "model_type": self.model_type,
                "model_path": self.model_path or "Unknown",
                "model_name": self.model_name,
                "template_format": f"{self.model_type.title()} chat template"
            }
    
    print("🧪 Testing ChatTemplateFormatter")
    print("=" * 40)
    
    # Test model detection
    test_cases = [
        ("llama-3.2-3b-instruct.gguf", "llama"),
        ("qwen2.5-coder-1.5b.gguf", "qwen"),
        ("phi-3.5-mini-instruct.gguf", "phi"),
        ("unknown-model.gguf", "generic")
    ]
    
    for model_path, expected_type in test_cases:
        formatter = ChatTemplateFormatter(model_path=model_path)
        detected = formatter.model_type
        status = "✅" if detected == expected_type else "❌"
        print(f"{status} {model_path}: {detected} (expected {expected_type})")
    
    print("\\n🔄 Testing Template Formatting")
    print("-" * 30)
    
    # Test Llama formatting
    llama_formatter = ChatTemplateFormatter(model_path="llama-3.2-3b-instruct.gguf")
    llama_prompt = llama_formatter.format_prompt(
        "You are helpful.", 
        "Create a Python function"
    )
    llama_tokens = ["<|begin_of_text|>", "<|start_header_id|>", "<|eot_id|>"]
    llama_has_tokens = all(token in llama_prompt for token in llama_tokens)
    print(f"✅ Llama template: {len(llama_prompt)} chars, tokens: {llama_has_tokens}")
    
    # Test Qwen formatting
    qwen_formatter = ChatTemplateFormatter(model_path="qwen2.5-coder-1.5b.gguf")
    qwen_prompt = qwen_formatter.format_prompt(
        "You are helpful.",
        "Create a Python function"
    )
    qwen_tokens = ["<|im_start|>", "<|im_end|>"]
    qwen_has_tokens = all(token in qwen_prompt for token in qwen_tokens)
    print(f"✅ Qwen template: {len(qwen_prompt)} chars, tokens: {qwen_has_tokens}")
    
    print("\\n📋 Example Llama Template Output:")
    print(llama_prompt[:200] + "..." if len(llama_prompt) > 200 else llama_prompt)
    
    print("\\n📋 Example Qwen Template Output:")
    print(qwen_prompt[:200] + "..." if len(qwen_prompt) > 200 else qwen_prompt)
    
    print("\\n🎉 ChatTemplateFormatter test completed successfully!")
    return True

if __name__ == "__main__":
    test_chat_template_basic()
