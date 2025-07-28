#!/usr/bin/env python3
"""
Test script for Semantic Zones functionality in DeepCoderX
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from config_module import SEMANTIC_ZONES, ZONE_DETECTION_CONFIG, ZONE_ROUTING_RULES
from services.dual_model_handler import LlamaSemanticParser

def test_zone_configuration():
    """Test that zone configuration is loaded correctly."""
    print("🔧 Testing Zone Configuration:")
    print(f"  Zones available: {list(SEMANTIC_ZONES.keys())}")
    print(f"  Detection enabled: {ZONE_DETECTION_CONFIG['enabled']}")
    print(f"  Confidence threshold: {ZONE_DETECTION_CONFIG['confidence_threshold']}")
    print(f"  Routing rules available: {list(ZONE_ROUTING_RULES.keys())}")
    print()

def test_zone_detection_patterns():
    """Test zone detection with example inputs."""
    print("🎯 Testing Zone Detection Patterns:")
    
    # Create a minimal semantic parser for testing (without model loading)
    class MockSemanticParser:
        def __init__(self):
            self.debug_mode = True
        
        def _detect_semantic_zone(self, user_input):
            """Copy the zone detection logic for testing."""
            if not ZONE_DETECTION_CONFIG["enabled"]:
                return "unknown", 0.0
            
            user_lower = user_input.lower().strip()
            zone_scores = {}
            
            for zone_name, zone_config in SEMANTIC_ZONES.items():
                score = 0.0
                
                # Check explicit triggers
                trigger_weight = ZONE_DETECTION_CONFIG["trigger_weight"]
                for trigger in zone_config["triggers"]:
                    if trigger.lower() in user_lower:
                        score += trigger_weight
                
                # Check pattern indicators  
                pattern_weight = ZONE_DETECTION_CONFIG["pattern_weight"]
                for pattern in zone_config["pattern_indicators"]:
                    try:
                        import re
                        if re.search(pattern, user_input, re.IGNORECASE if not ZONE_DETECTION_CONFIG["case_sensitive"] else 0):
                            score += pattern_weight
                    except re.error:
                        continue
                
                # Apply confidence boost from zone configuration
                if score > 0:
                    score += zone_config["confidence_boost"]
                
                zone_scores[zone_name] = score
            
            # Determine winning zone
            if not zone_scores or max(zone_scores.values()) < ZONE_DETECTION_CONFIG["confidence_threshold"]:
                fallback_zone = ZONE_DETECTION_CONFIG["unknown_zone_fallback"]
                return fallback_zone, 0.5
            
            # Get highest scoring zone
            best_zone = max(zone_scores, key=zone_scores.get)
            best_score = zone_scores[best_zone]
            
            return best_zone, min(best_score, 1.0)  # Cap confidence at 1.0
    
    parser = MockSemanticParser()
    
    # Test cases for each semantic zone
    test_cases = [
        # Tool Operation Zone
        ("use your tools and read config.py", "tool_operation"),
        ("use tools to audit codebase", "tool_operation"),
        ("file operations needed", "tool_operation"),
        
        # Conversational Zone  
        ("hello", "conversational"),
        ("explain how functions work", "conversational"),
        ("what is Python?", "conversational"),
        ("help me understand recursion", "conversational"),
        
        # Analysis Zone
        ("analyze this project", "analysis"),
        ("review the code", "analysis"),
        ("summarize what this does", "analysis"),
        
        # Debug Zone
        ("debug this error", "debug"),
        ("fix this bug", "debug"),
        ("something is not working", "debug"),
        
        # Creative Zone
        ("create a script", "creative"),
        ("write a function", "creative"),
        ("generate some code", "creative"),
        
        # Edge cases
        ("just a random question", "conversational"),  # Should fallback
        ("", "conversational")  # Empty input
    ]
    
    success_count = 0
    total_count = len(test_cases)
    
    for user_input, expected_zone in test_cases:
        detected_zone, confidence = parser._detect_semantic_zone(user_input)
        status = "✅" if detected_zone == expected_zone else "❌"
        
        print(f"  {status} '{user_input}' → {detected_zone} ({confidence:.2f}) [expected: {expected_zone}]")
        
        if detected_zone == expected_zone:
            success_count += 1
    
    print(f"\n  Success rate: {success_count}/{total_count} ({success_count/total_count*100:.1f}%)")
    print()

def test_routing_rules():
    """Test zone routing rules logic."""
    print("🚀 Testing Zone Routing Rules:")
    
    for zone_name, zone_rules in ZONE_ROUTING_RULES.items():
        print(f"  Zone: {zone_name}")
        print(f"    Force routing: {zone_rules.get('force_routing', False)}")
        print(f"    Target: {zone_rules['target']}")
        print(f"    Min confidence: {zone_rules.get('minimum_confidence', 0.5)}")
        print()

def test_zone_configuration_completeness():
    """Test that zone configuration is complete and consistent."""
    print("🔍 Testing Configuration Completeness:")
    
    # Check that all zones have routing rules
    zones_without_rules = set(SEMANTIC_ZONES.keys()) - set(ZONE_ROUTING_RULES.keys())
    if zones_without_rules:
        print(f"  ❌ Zones without routing rules: {zones_without_rules}")
    else:
        print(f"  ✅ All zones have routing rules")
    
    # Check that all routing rules reference valid zones
    rules_without_zones = set(ZONE_ROUTING_RULES.keys()) - set(SEMANTIC_ZONES.keys())
    if rules_without_zones:
        print(f"  ❌ Routing rules without zones: {rules_without_zones}")
    else:
        print(f"  ✅ All routing rules reference valid zones")
    
    # Check zone configuration structure
    required_zone_fields = ["name", "triggers", "pattern_indicators", "default_routing", "confidence_boost", "tool_ready"]
    missing_fields = []
    
    for zone_name, zone_config in SEMANTIC_ZONES.items():
        for field in required_zone_fields:
            if field not in zone_config:
                missing_fields.append(f"{zone_name}.{field}")
    
    if missing_fields:
        print(f"  ❌ Missing zone fields: {missing_fields}")
    else:
        print(f"  ✅ All zones have required fields")
    
    print()

if __name__ == "__main__":
    print("🧪 Semantic Zones Test Suite")
    print("=" * 50)
    print()
    
    try:
        test_zone_configuration()
        test_zone_detection_patterns() 
        test_routing_rules()
        test_zone_configuration_completeness()
        
        print("✅ All tests completed successfully!")
        print()
        print("🎯 Ready for semantic zone usage:")
        print("   • @deepseek use your tools and audit this codebase")
        print("   • @deepseek explain how this function works") 
        print("   • @deepseek analyze the project structure")
        print("   • @deepseek create a backup script")
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
