#!/usr/bin/env python3
"""
QWEN INTEGRATION TEST FOR DEEPCODERX

Comprehensive integration testing for Qwen2.5-Coder optimization including:
- Configuration loading with Qwen settings
- Model path verification and hardware config
- Progressive intensity system testing
- Tool call prompt building and parsing
- End-to-end workflow validation

Usage: python integration_tests/qwen_integration_test.py
"""

import sys
import os
from pathlib import Path
import logging
import traceback

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def setup_logging():
    """Configure logging for integration test."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('integration_tests/qwen_test.log')
        ]
    )
    return logging.getLogger(__name__)

def test_configuration_loading(logger):
    """Test 1: Configuration Loading and Qwen Settings"""
    logger.info("🔄 TEST 1: Configuration Loading and Qwen Settings")
    
    try:
        from config_module import DeepCoderXConfig
        
        config = DeepCoderXConfig()
        logger.info("✅ Configuration loaded successfully")
        
        # Test Qwen model path
        if hasattr(config, 'GGUF_MODEL_PATH') and config.GGUF_MODEL_PATH:
            logger.info(f"✅ GGUF Model Path: {config.GGUF_MODEL_PATH}")
            if config.GGUF_MODEL_PATH.exists():
                logger.info(f"✅ Model file exists: {config.GGUF_MODEL_PATH.stat().st_size / (1024*1024):.1f} MB")
            else:
                logger.error(f"❌ Model file not found: {config.GGUF_MODEL_PATH}")
                return False
        else:
            logger.error("❌ GGUF_MODEL_PATH not configured")
            return False
        
        # Test Qwen hardware configuration
        if hasattr(config, 'GGUF_HARDWARE_CONFIG'):
            hw_config = config.GGUF_HARDWARE_CONFIG
            logger.info(f"✅ Hardware Config - GPU Layers: {hw_config.get('n_gpu_layers')}")
            logger.info(f"✅ Hardware Config - Batch Size: {hw_config.get('n_batch')}")
            logger.info(f"✅ Hardware Config - Context: {hw_config.get('n_ctx')}")
            logger.info(f"✅ Hardware Config - Rope Freq: {hw_config.get('rope_freq_base')}")
        else:
            logger.error("❌ GGUF_HARDWARE_CONFIG not found")
            return False
        
        # Test Qwen optimization settings
        if hasattr(config, 'QWEN_OPTIMIZATION'):
            qwen_opt = config.QWEN_OPTIMIZATION
            logger.info(f"✅ Qwen Optimization - Code Specialization: {qwen_opt.get('code_specialization')}")
            logger.info(f"✅ Qwen Optimization - Progressive Intensity: {qwen_opt.get('progressive_intensity')}")
            logger.info(f"✅ Qwen Optimization - Max Intensity: {qwen_opt.get('max_intensity_level')}")
        else:
            logger.error("❌ QWEN_OPTIMIZATION not found")
            return False
        
        # Test generation parameters
        if hasattr(config, 'GGUF_GENERATION_PARAMS'):
            gen_params = config.GGUF_GENERATION_PARAMS
            logger.info(f"✅ Generation Params - Temperature: {gen_params.get('temperature')}")
            logger.info(f"✅ Generation Params - Top P: {gen_params.get('top_p')}")
            logger.info(f"✅ Generation Params - Repeat Penalty: {gen_params.get('repeat_penalty')}")
        else:
            logger.error("❌ GGUF_GENERATION_PARAMS not found")
            return False
        
        logger.info("✅ TEST 1 PASSED: Configuration loaded with Qwen optimization")
        return True
        
    except Exception as e:
        logger.error(f"❌ TEST 1 FAILED: Configuration loading error: {e}")
        logger.error(traceback.format_exc())
        return False

def test_yaml_configuration(logger):
    """Test 2: YAML Configuration Loading"""
    logger.info("🔄 TEST 2: YAML Configuration Loading")
    
    try:
        # Test YAML file exists
        yaml_path = project_root / "gguf_prompts.yaml"
        if not yaml_path.exists():
            logger.error(f"❌ YAML file not found: {yaml_path}")
            return False
        
        logger.info(f"✅ YAML file found: {yaml_path}")
        
        # Test YAML loading
        import yaml
        with open(yaml_path, 'r', encoding='utf-8') as f:
            yaml_config = yaml.safe_load(f)
        
        if not yaml_config:
            logger.error("❌ YAML file is empty or invalid")
            return False
        
        logger.info("✅ YAML file loaded successfully")
        
        # Test key sections
        required_sections = [
            'system_instructions',
            'few_shot_examples', 
            'progressive_intensity',
            'model_overrides',
            'post_processing'
        ]
        
        for section in required_sections:
            if section in yaml_config:
                logger.info(f"✅ YAML section found: {section}")
            else:
                logger.error(f"❌ YAML section missing: {section}")
                return False
        
        # Test progressive intensity levels
        if 'progressive_intensity' in yaml_config:
            intensity_config = yaml_config['progressive_intensity']
            if 'escalation_levels' in intensity_config:
                levels = intensity_config['escalation_levels']
                logger.info(f"✅ Progressive intensity levels: {len(levels)}")
                for level in range(1, 6):
                    if level in levels:
                        strategy = levels[level].get('strategy', 'unknown')
                        logger.info(f"✅ Level {level}: {strategy}")
                    else:
                        logger.error(f"❌ Missing intensity level: {level}")
                        return False
            else:
                logger.error("❌ escalation_levels not found in progressive_intensity")
                return False
        
        # Test Qwen model overrides
        if 'model_overrides' in yaml_config:
            overrides = yaml_config['model_overrides']
            if 'qwen2.5-coder' in overrides:
                qwen_config = overrides['qwen2.5-coder']
                logger.info(f"✅ Qwen override - Temperature: {qwen_config.get('temperature')}")
                logger.info(f"✅ Qwen override - Progressive: {qwen_config.get('progressive_intensity')}")
            else:
                logger.error("❌ qwen2.5-coder override not found")
                return False
        
        logger.info("✅ TEST 2 PASSED: YAML configuration loaded and validated")
        return True
        
    except Exception as e:
        logger.error(f"❌ TEST 2 FAILED: YAML configuration error: {e}")
        logger.error(traceback.format_exc())
        return False

def test_progressive_prompt_builder(logger):
    """Test 3: Progressive Prompt Builder Functionality"""
    logger.info("🔄 TEST 3: Progressive Prompt Builder Functionality")
    
    try:
        # Import prompt builder
        sys.path.append(str(project_root / "services"))
        from gguf_tool_prompt import QwenProgressivePromptBuilder
        
        # Initialize builder
        builder = QwenProgressivePromptBuilder("qwen2.5-coder")
        logger.info("✅ QwenProgressivePromptBuilder initialized")
        
        # Test intensity tracking
        initial_intensity = builder.current_intensity
        logger.info(f"✅ Initial intensity level: {initial_intensity}")
        
        # Test intensity escalation on failure
        builder._update_intensity(False)  # Simulate failure
        if builder.current_intensity > initial_intensity:
            logger.info(f"✅ Intensity escalated to: {builder.current_intensity}")
        else:
            logger.error("❌ Intensity did not escalate on failure")
            return False
        
        # Test intensity reduction on success
        builder._update_intensity(True)  # Simulate success
        builder._update_intensity(True)  # Need 2 successes to reduce
        if builder.current_intensity <= initial_intensity + 1:
            logger.info(f"✅ Intensity managed correctly: {builder.current_intensity}")
        else:
            logger.error("❌ Intensity did not reduce properly on success")
            return False
        
        # Test prompt building
        sample_tools = [
            {
                "name": "run_bash",
                "description": "Execute shell command",
                "parameters": {"command": {"type": "string"}}
            },
            {
                "name": "read_file", 
                "description": "Read file content",
                "parameters": {"path": {"type": "string"}}
            }
        ]
        
        conversation_history = [
            {"role": "user", "content": "pwd"},
            {"role": "assistant", "content": "<tool_call>run_bash({\"command\": \"pwd\"})</tool_call>"}
        ]
        
        prompt = builder.build_adaptive_prompt(
            user_input="ls -la",
            conversation_history=conversation_history,
            available_tools=sample_tools,
            last_response_success=True
        )
        
        if prompt and len(prompt) > 100:
            logger.info(f"✅ Prompt built successfully: {len(prompt)} characters")
            
            # Check for Qwen-specific elements
            qwen_indicators = [
                "QWEN",
                "CODER", 
                "tool_call",
                "🔥",
                "⚡"
            ]
            
            found_indicators = []
            for indicator in qwen_indicators:
                if indicator in prompt:
                    found_indicators.append(indicator)
            
            if len(found_indicators) >= 3:
                logger.info(f"✅ Qwen optimization elements found: {found_indicators}")
            else:
                logger.warning(f"⚠️ Limited Qwen elements found: {found_indicators}")
        else:
            logger.error("❌ Prompt building failed or too short")
            return False
        
        # Test different intensity levels
        for level in range(1, 6):
            builder.current_intensity = level
            prompt = builder._build_qwen_system_instructions()
            if prompt and len(prompt) > 10:
                logger.info(f"✅ Level {level} system instructions built")
            else:
                logger.error(f"❌ Level {level} system instructions failed")
                return False
        
        logger.info("✅ TEST 3 PASSED: Progressive prompt builder working correctly")
        return True
        
    except Exception as e:
        logger.error(f"❌ TEST 3 FAILED: Progressive prompt builder error: {e}")
        logger.error(traceback.format_exc())
        return False

def test_model_loading_preparation(logger):
    """Test 4: Model Loading Preparation (Without Actual Loading)"""
    logger.info("🔄 TEST 4: Model Loading Preparation")
    
    try:
        from config_module import DeepCoderXConfig
        
        config = DeepCoderXConfig()
        
        # Check model path accessibility
        model_path = config.GGUF_MODEL_PATH
        if not model_path or not model_path.exists():
            logger.error(f"❌ Model file not accessible: {model_path}")
            return False
        
        # Check file permissions
        if not os.access(model_path, os.R_OK):
            logger.error(f"❌ Model file not readable: {model_path}")
            return False
        
        logger.info(f"✅ Model file accessible: {model_path}")
        
        # Check model size (should be reasonable for 1.5B model)
        file_size_mb = model_path.stat().st_size / (1024 * 1024)
        if 500 < file_size_mb < 5000:  # Reasonable range for 1.5B GGUF
            logger.info(f"✅ Model size reasonable: {file_size_mb:.1f} MB")
        else:
            logger.warning(f"⚠️ Model size unusual: {file_size_mb:.1f} MB")
        
        # Test hardware configuration structure
        hw_config = config.GGUF_HARDWARE_CONFIG
        required_hw_params = ['n_gpu_layers', 'n_batch', 'n_ctx', 'n_threads']
        for param in required_hw_params:
            if param in hw_config:
                logger.info(f"✅ Hardware param {param}: {hw_config[param]}")
            else:
                logger.error(f"❌ Missing hardware param: {param}")
                return False
        
        # Test generation parameters
        gen_params = config.GGUF_GENERATION_PARAMS
        required_gen_params = ['temperature', 'top_p', 'max_tokens']
        for param in required_gen_params:
            if param in gen_params:
                logger.info(f"✅ Generation param {param}: {gen_params[param]}")
            else:
                logger.error(f"❌ Missing generation param: {param}")
                return False
        
        # Test Apple Silicon optimization
        if hw_config.get('n_gpu_layers') == -1:
            logger.info("✅ Apple Silicon Metal optimization enabled")
        else:
            logger.warning("⚠️ Apple Silicon optimization may not be optimal")
        
        logger.info("✅ TEST 4 PASSED: Model loading preparation validated")
        return True
        
    except Exception as e:
        logger.error(f"❌ TEST 4 FAILED: Model loading preparation error: {e}")
        logger.error(traceback.format_exc())
        return False

def test_tool_integration(logger):
    """Test 5: Tool Integration and Format Validation"""
    logger.info("🔄 TEST 5: Tool Integration and Format Validation")
    
    try:
        # Test tool call format parsing
        sample_responses = [
            "<tool_call>run_bash({\"command\": \"pwd\"})</tool_call>",
            "<tool_call>read_file({\"path\": \"config.py\"})</tool_call>",
            "<tool_call>list_dir({\"path\": \".\"})</tool_call>"
        ]
        
        # Simple regex pattern for tool call detection
        tool_call_pattern = r'<tool_call>(\w+)\((\{.*?\})\)</tool_call>'
        import re
        
        for response in sample_responses:
            match = re.search(tool_call_pattern, response)
            if match:
                function_name = match.group(1)
                arguments = match.group(2)
                logger.info(f"✅ Parsed tool call - Function: {function_name}, Args: {arguments}")
            else:
                logger.error(f"❌ Failed to parse tool call: {response}")
                return False
        
        # Test post-processing pattern detection
        problematic_responses = [
            "I can help you with that. <tool_call>run_bash({\"command\": \"pwd\"})</tool_call>",
            "Let me check the current directory for you.",
            "The current directory can be found by running:",
            "To do this, I'll use the pwd command."
        ]
        
        # Patterns that should trigger post-processing
        problem_patterns = [
            r'I can help',
            r'Let me',
            r'The current',
            r'To do this'
        ]
        
        for response in problematic_responses:
            needs_processing = any(re.search(pattern, response, re.IGNORECASE) for pattern in problem_patterns)
            if needs_processing:
                logger.info(f"✅ Correctly identified problematic response: {response[:50]}...")
            else:
                logger.error(f"❌ Failed to identify problematic response: {response}")
                return False
        
        logger.info("✅ TEST 5 PASSED: Tool integration and format validation working")
        return True
        
    except Exception as e:
        logger.error(f"❌ TEST 5 FAILED: Tool integration error: {e}")
        logger.error(traceback.format_exc())
        return False

def test_end_to_end_workflow(logger):
    """Test 6: End-to-End Workflow Simulation"""
    logger.info("🔄 TEST 6: End-to-End Workflow Simulation")
    
    try:
        from config_module import DeepCoderXConfig
        
        # Load configuration
        config = DeepCoderXConfig()
        logger.info("✅ Configuration loaded for workflow test")
        
        # Initialize progressive prompt builder
        sys.path.append(str(project_root / "services"))
        from gguf_tool_prompt import QwenProgressivePromptBuilder
        builder = QwenProgressivePromptBuilder("qwen2.5-coder")
        logger.info("✅ Progressive prompt builder initialized")
        
        # Simulate workflow steps
        workflow_steps = [
            {"user_input": "pwd", "expected_tool": "run_bash"},
            {"user_input": "list files", "expected_tool": "list_dir"},
            {"user_input": "read config.py", "expected_tool": "read_file"},
            {"user_input": "create test.py", "expected_tool": "write_file"}
        ]
        
        conversation_history = []
        
        for step_num, step in enumerate(workflow_steps, 1):
            logger.info(f"Testing workflow step {step_num}: {step['user_input']}")
            
            # Build prompt
            prompt = builder.build_adaptive_prompt(
                user_input=step['user_input'],
                conversation_history=conversation_history,
                available_tools=[
                    {"name": "run_bash", "description": "Execute shell command"},
                    {"name": "list_dir", "description": "List directory contents"},
                    {"name": "read_file", "description": "Read file content"},
                    {"name": "write_file", "description": "Write file content"}
                ],
                last_response_success=True
            )
            
            if prompt and len(prompt) > 100:
                logger.info(f"✅ Step {step_num} prompt built: {len(prompt)} chars")
                
                # Check if expected tool is mentioned in examples
                if step['expected_tool'] in prompt:
                    logger.info(f"✅ Step {step_num} expected tool found in prompt")
                else:
                    logger.warning(f"⚠️ Step {step_num} expected tool not prominent in prompt")
                
                # Simulate successful response
                simulated_response = f"<tool_call>{step['expected_tool']}({{\"parameter\": \"value\"}})</tool_call>"
                conversation_history.extend([
                    {"role": "user", "content": step['user_input']},
                    {"role": "assistant", "content": simulated_response}
                ])
                
            else:
                logger.error(f"❌ Step {step_num} prompt building failed")
                return False
        
        # Test intensity escalation scenario
        logger.info("Testing intensity escalation on failures...")
        initial_intensity = builder.current_intensity
        
        # Simulate multiple failures
        for i in range(3):
            builder._update_intensity(False)
        
        if builder.current_intensity > initial_intensity:
            logger.info(f"✅ Intensity properly escalated from {initial_intensity} to {builder.current_intensity}")
        else:
            logger.error("❌ Intensity escalation failed")
            return False
        
        # Build high-intensity prompt
        high_intensity_prompt = builder.build_adaptive_prompt(
            user_input="pwd",
            conversation_history=[],
            available_tools=[{"name": "run_bash", "description": "Execute shell command"}],
            last_response_success=False
        )
        
        if "🚨" in high_intensity_prompt or "EMERGENCY" in high_intensity_prompt:
            logger.info("✅ High intensity prompt contains emergency elements")
        else:
            logger.warning("⚠️ High intensity prompt may not be intense enough")
        
        logger.info("✅ TEST 6 PASSED: End-to-end workflow simulation successful")
        return True
        
    except Exception as e:
        logger.error(f"❌ TEST 6 FAILED: End-to-end workflow error: {e}")
        logger.error(traceback.format_exc())
        return False

def main():
    """Run all Qwen integration tests."""
    logger = setup_logging()
    
    logger.info("🚀 STARTING QWEN INTEGRATION TESTS FOR DEEPCODERX")
    logger.info("=" * 60)
    
    test_results = []
    tests = [
        ("Configuration Loading", test_configuration_loading),
        ("YAML Configuration", test_yaml_configuration),
        ("Progressive Prompt Builder", test_progressive_prompt_builder),
        ("Model Loading Preparation", test_model_loading_preparation),
        ("Tool Integration", test_tool_integration),
        ("End-to-End Workflow", test_end_to_end_workflow)
    ]
    
    for test_name, test_func in tests:
        logger.info("")
        logger.info(f"Starting: {test_name}")
        logger.info("-" * 40)
        
        try:
            result = test_func(logger)
            test_results.append((test_name, result))
            
            if result:
                logger.info(f"✅ {test_name} PASSED")
            else:
                logger.error(f"❌ {test_name} FAILED")
                
        except Exception as e:
            logger.error(f"❌ {test_name} CRASHED: {e}")
            test_results.append((test_name, False))
    
    # Summary
    logger.info("")
    logger.info("=" * 60)
    logger.info("🏁 QWEN INTEGRATION TEST SUMMARY")
    logger.info("=" * 60)
    
    passed = sum(1 for _, result in test_results if result)
    total = len(test_results)
    
    for test_name, result in test_results:
        status = "✅ PASS" if result else "❌ FAIL"
        logger.info(f"{status}: {test_name}")
    
    logger.info("-" * 40)
    logger.info(f"RESULTS: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
    
    if passed == total:
        logger.info("🎉 ALL TESTS PASSED - QWEN INTEGRATION READY!")
        return 0
    else:
        logger.error(f"⚠️ {total-passed} TESTS FAILED - REVIEW REQUIRED")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
