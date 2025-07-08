#!/usr/bin/env python3
"""Quick validation of the enhanced GGUF prompt."""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

def quick_test():
    try:
        from services.gguf_tool_prompt import GGUFToolPromptBuilder
        
        builder = GGUFToolPromptBuilder()
        
        # Check examples
        print("Enhanced Prompt Validation:")
        print("=" * 50)
        
        # Check that pwd is first example
        first_example = builder.core_examples[0]
        print(f"✅ First example user: '{first_example['user']}'")
        print(f"✅ First example assistant: '{first_example['assistant']}'")
        
        # Check format
        pwd_correct = first_example['user'] == 'pwd' and 'run_bash' in first_example['assistant']
        print(f"✅ PWD example correct: {pwd_correct}")
        
        # Check system instructions
        instructions = builder._build_system_instructions()
        has_critical = '🚨 CRITICAL INSTRUCTIONS' in instructions
        has_never = 'NEVER respond with JSON blocks' in instructions
        has_examples = 'User says "pwd"' in instructions
        
        print(f"✅ Has critical instructions: {has_critical}")
        print(f"✅ Has NEVER instructions: {has_never}")
        print(f"✅ Has pwd examples: {has_examples}")
        
        if all([pwd_correct, has_critical, has_never, has_examples]):
            print("\n🎉 ALL VALIDATIONS PASSED!")
            print("🚀 Enhanced prompt is ready for testing!")
        else:
            print("\n⚠️ Some validations failed")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    quick_test()
