#!/usr/bin/env python3
"""
QWEN PRACTICAL INTEGRATION TEST

A streamlined test to verify Qwen2.5-Coder optimization is working correctly.
This test focuses on the key integration points without requiring the full model to run.
"""

import sys
import os
from pathlib import Path
import logging

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def setup_logging():
    """Setup simple logging."""
    logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
    return logging.getLogger(__name__)

def test_qwen_configuration():
    """Test Qwen configuration loading."""
    logger = logging.getLogger(__name__)
    logger.info("🔄 Testing Qwen Configuration...")
    
    try:
        # Test model path exists
        expected_model_path = Path("/Users/admin/Documents/MyProjects/Project_Genesis/models/qwen-coder/qwen2.5-coder-1.5b.gguf")
        
        if expected_model_path.exists():
            size_mb = expected_model_path.stat().st_size / (1024*1024)
            logger.info(f"✅ Qwen model found: {size_mb:.1f} MB")
        else:
            logger.error(f"❌ Qwen model not found: {expected_model_path}")
            return False
        
        # Test YAML configuration
        yaml_path = project_root / "gguf_prompts.yaml"
        if not yaml_path.exists():
            logger.error(f"❌ YAML config not found: {yaml_path}")
            return False
        
        with open(yaml_path, 'r') as f:
            yaml_content = f.read()
        
        # Check for key Qwen elements
        qwen_indicators = [
            "QWEN-OPTIMIZED",
            "progressive_intensity",
            "qwen2.5-coder",
            "CODE MODE ACTIVATED",
            "escalation_levels"
        ]
        
        found_indicators = [indicator for indicator in qwen_indicators if indicator in yaml_content]
        
        if len(found_indicators) >= 4:
            logger.info(f"✅ YAML Qwen optimization found: {len(found_indicators)}/5 indicators")
        else:
            logger.error(f"❌ YAML missing Qwen optimization: {found_indicators}")
            return False
        
        logger.info("✅ Qwen configuration test PASSED")
        return True
        
    except Exception as e:
        logger.error(f"❌ Configuration test failed: {e}")
        return False

def test_progressive_prompt_builder():
    """Test progressive prompt builder functionality."""
    logger = logging.getLogger(__name__)
    logger.info("🔄 Testing Progressive Prompt Builder...")
    
    try:
        # Import the builder
        sys.path.append(str(project_root / "services"))
        from gguf_tool_prompt import QwenProgressivePromptBuilder
        
        # Initialize builder
        builder = QwenProgressivePromptBuilder("qwen2.5-coder")
        logger.info("✅ QwenProgressivePromptBuilder imported and initialized")
        
        # Test basic properties
        if builder.model_name == "qwen2.5-coder":
            logger.info("✅ Model name set correctly")
        else:
            logger.error(f"❌ Wrong model name: {builder.model_name}")
            return False
        
        if builder.max_intensity == 5:
            logger.info("✅ Max intensity level correct (5)")
        else:
            logger.error(f"❌ Wrong max intensity: {builder.max_intensity}")
            return False
        
        # Test intensity escalation
        initial_intensity = builder.current_intensity
        builder._update_intensity(False)  # Simulate failure
        
        if builder.current_intensity > initial_intensity:
            logger.info(f"✅ Intensity escalated: {initial_intensity} → {builder.current_intensity}")
        else:
            logger.error("❌ Intensity did not escalate on failure")
            return False
        
        # Test prompt building (basic)
        sample_tools = [{"name": "run_bash", "description": "Execute shell command"}]
        conversation_history = []
        
        prompt = builder.build_adaptive_prompt(
            user_input="pwd",
            conversation_history=conversation_history,
            available_tools=sample_tools,
            last_response_success=True
        )
        
        if prompt and len(prompt) > 100:
            logger.info(f"✅ Prompt built successfully: {len(prompt)} characters")
            
            # Check for Qwen-specific elements
            if "QWEN" in prompt.upper() or "CODER" in prompt.upper():
                logger.info("✅ Qwen-specific elements found in prompt")
            else:
                logger.warning("⚠️ Qwen-specific elements may be missing")
        else:
            logger.error("❌ Prompt building failed or too short")
            return False
        
        logger.info("✅ Progressive prompt builder test PASSED")
        return True
        
    except ImportError as e:
        logger.error(f"❌ Import error: {e}")
        return False
    except Exception as e:
        logger.error(f"❌ Progressive prompt builder test failed: {e}")
        return False

def test_integration_readiness():
    """Test integration readiness without loading the actual model."""
    logger = logging.getLogger(__name__)
    logger.info("🔄 Testing Integration Readiness...")
    
    try:
        # Check if required imports work
        sys.path.append(str(project_root))
        
        # Test basic configuration import
        try:
            from config_module import DeepCoderXConfig
            config = DeepCoderXConfig()
            logger.info("✅ Configuration class imported successfully")
            
            # Check for Qwen-specific attributes
            if hasattr(config, 'QWEN_OPTIMIZATION'):
                logger.info("✅ QWEN_OPTIMIZATION attribute found")
            else:
                logger.warning("⚠️ QWEN_OPTIMIZATION attribute missing")
            
            if hasattr(config, 'GGUF_MODEL_PATH'):
                logger.info("✅ GGUF_MODEL_PATH attribute found")
            else:
                logger.error("❌ GGUF_MODEL_PATH attribute missing")
                return False
            
        except Exception as e:
            logger.error(f"❌ Configuration import failed: {e}")
            return False
        
        # Test GGUF handler import
        try:
            from services.gguf_handler import GGUFLocalHandler
            logger.info("✅ GGUF handler imported successfully")
        except Exception as e:
            logger.error(f"❌ GGUF handler import failed: {e}")
            return False
        
        # Test tool registry import
        try:
            from services.tool_registry import tool_registry
            logger.info("✅ Tool registry imported successfully")
        except Exception as e:
            logger.error(f"❌ Tool registry import failed: {e}")
            return False
        
        logger.info("✅ Integration readiness test PASSED")
        return True
        
    except Exception as e:
        logger.error(f"❌ Integration readiness test failed: {e}")
        return False

def main():
    """Run practical Qwen integration tests."""
    logger = setup_logging()
    
    logger.info("🚀 QWEN PRACTICAL INTEGRATION TEST")
    logger.info("=" * 50)
    
    tests = [
        ("Qwen Configuration", test_qwen_configuration),
        ("Progressive Prompt Builder", test_progressive_prompt_builder),
        ("Integration Readiness", test_integration_readiness)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        logger.info(f"\n▶️ {test_name}")
        logger.info("-" * 30)
        
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            logger.error(f"❌ {test_name} crashed: {e}")
            results.append((test_name, False))
    
    # Summary
    logger.info("\n" + "=" * 50)
    logger.info("📊 TEST SUMMARY")
    logger.info("=" * 50)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        logger.info(f"{status}: {test_name}")
    
    logger.info(f"\nResults: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
    
    if passed == total:
        logger.info("\n🎉 ALL TESTS PASSED!")
        logger.info("🚀 Qwen integration is ready for testing with actual model")
        logger.info("\n📋 Next steps:")
        logger.info("1. Test actual model loading with app.py")
        logger.info("2. Test progressive intensity with tool calling")
        logger.info("3. Validate Apple Silicon Metal acceleration")
        return 0
    else:
        logger.error(f"\n⚠️ {total-passed} tests failed - fix before proceeding")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
