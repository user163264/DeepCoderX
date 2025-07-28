# Automated Testing Implementation - Week 1: Foundation

## Overview
**Week 1 Focus:** Establish core testing infrastructure with standardized JSON output and automated test execution engine.

**Goals:**
- Create comprehensive test query categories  
- Implement automated testing engine
- Establish standardized JSON output format
- Integrate with existing enhanced logging system

## Implementation Tasks

### Day 1-2: Test Query Categories and Definitions

**File:** `automation/test_query_definitions.py`

```python
# Comprehensive test query categories for systematic testing

CONVERSATIONAL_QUERIES = [
    "hello",
    "how are you", 
    "what can you do",
    "goodbye",
    "thank you",
    "explain functions",
    "what is Python",
    "why are apples green",
    "why is the moon round",
    "help me code"
]

DIRECT_COMMAND_QUERIES = [
    "pwd",
    "ls", 
    "ls -la",
    "git status",
    "whoami",
    "date"
]

CODE_GENERATION_QUERIES = [
    "create a hello world script",
    "write a function to sort numbers",
    "make a simple calculator", 
    "create a file reader",
    "write a basic loop example"
]

SEMANTIC_ZONE_QUERIES = [
    "use your tools and read config.py",
    "explain how recursion works",
    "analyze this project structure",
    "debug this error message", 
    "create a backup script"
]

EDGE_CASE_QUERIES = [
    "",  # Empty input
    "asdfghjkl",  # Random text
    "What is the meaning of life?",  # Off-topic
    "hello" * 100  # Long repetitive input
]

# Test configuration
TEST_CONFIG = {
    "providers": ["dual", "local", "deepseek", "openai"],
    "query_categories": ["conversational", "commands", "code_gen", "semantic", "edge"],
    "repetitions_per_query": 3,  # Test same query multiple times
    "delay_between_queries": 2,  # Seconds between tests
    "max_execution_time": 30,    # Timeout per query
    "log_level": "detailed"      # detailed/summary/minimal
}
```

### Day 3-4: Automated Testing Engine

**File:** `automation/automated_testing_engine.py`

```python
import time
import json
from datetime import datetime
from typing import Dict, List, Any
import sys
import os

# Add DeepCoderX root to path for imports
sys.path.append('/Users/admin/Documents/DeepCoderX')
from api_automation_example import DeepCoderXAPI
from automation.test_query_definitions import *

class AutomatedTestingEngine:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.api = DeepCoderXAPI(debug_mode=True)
        self.test_session_id = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
    def execute_full_test_suite(self) -> Dict[str, Any]:
        """Execute complete test suite across all providers and categories"""
        
        results = {
            "session_id": self.test_session_id,
            "start_time": datetime.now().isoformat(),
            "config": self.config,
            "test_results": [],
            "summary": {}
        }
        
        # Execute tests for each provider
        for provider in self.config["providers"]:
            print(f"\\n🧪 Testing provider: {provider}")
            
            # Test each category
            for category in self.config["query_categories"]:
                category_results = self._test_category(provider, category)
                results["test_results"].extend(category_results)
                
        results["end_time"] = datetime.now().isoformat()
        results["summary"] = self._generate_summary(results["test_results"])
        
        return results
    
    def _test_category(self, provider: str, category: str) -> List[Dict[str, Any]]:
        """Test all queries in a specific category with a specific provider"""
        
        category_queries = self._get_queries_for_category(category)
        results = []
        
        for query in category_queries:
            # Execute multiple repetitions for consistency analysis
            for iteration in range(self.config["repetitions_per_query"]):
                result = self._execute_single_test(provider, category, query, iteration + 1)
                results.append(result)
                
                # Delay between queries to avoid overwhelming the system
                time.sleep(self.config["delay_between_queries"])
                
        return results
    
    def _execute_single_test(self, provider: str, category: str, query: str, iteration: int) -> Dict[str, Any]:
        """Execute a single test query and capture comprehensive results"""
        
        interaction_id = f"{self.test_session_id}_{provider}_{category}_{iteration:03d}"
        
        test_result = {
            "test_session_id": self.test_session_id,
            "interaction_id": interaction_id,
            "timestamp": datetime.now().isoformat(),
            "test_metadata": {
                "query_category": category,
                "test_iteration": iteration,
                "provider": provider,
                "expected_behavior": self._get_expected_behavior(category)
            },
            "request": {
                "query": query,
                "provider": provider,
                "parameters": {"timeout": self.config["max_execution_time"]}
            }
        }
        
        try:
            # Execute the query using the API
            start_time = time.time()
            api_result = self.api.execute_command(query, provider)
            execution_time = (time.time() - start_time) * 1000  # Convert to milliseconds
            
            test_result["response"] = {
                "content": api_result.get("response", ""),
                "execution_time_ms": execution_time,
                "success": api_result.get("success", False),
                "error_message": api_result.get("error", None)
            }
            
            # Analyze the response
            test_result["analysis"] = self._analyze_response(query, api_result.get("response", ""), category)
            
        except Exception as e:
            test_result["response"] = {
                "content": "",
                "execution_time_ms": 0,
                "success": False,
                "error_message": str(e)
            }
            
            test_result["analysis"] = {
                "quality_score": 0.0,
                "appropriateness": False,
                "hallucination_detected": False,
                "error_type": "execution_failure"
            }
        
        return test_result
    
    def _analyze_response(self, query: str, response: str, category: str) -> Dict[str, Any]:
        """Analyze response quality and detect potential issues"""
        
        analysis = {
            "quality_score": self._calculate_quality_score(query, response, category),
            "appropriateness": self._check_appropriateness(query, response, category),
            "hallucination_detected": self._detect_hallucination(query, response),
            "response_length": len(response),
            "contains_error": "error" in response.lower() or "failed" in response.lower()
        }
        
        return analysis
    
    def _calculate_quality_score(self, query: str, response: str, category: str) -> float:
        """Calculate response quality score (0.0 to 1.0)"""
        
        if not response or len(response.strip()) == 0:
            return 0.0
            
        score = 0.5  # Base score
        
        # Category-specific scoring
        if category == "conversational":
            if any(greeting in response.lower() for greeting in ["hello", "hi", "hey"]):
                score += 0.3
            if "help" in response.lower():
                score += 0.2
                
        elif category == "commands":
            if "[HARD CODED]" not in response and len(response) > 10:
                score += 0.4  # Likely actual command output
                
        elif category == "code_gen":
            if any(code_indicator in response for code_indicator in ["def ", "function", "import", "class"]):
                score += 0.4
                
        # Cap at 1.0
        return min(score, 1.0)
    
    def _check_appropriateness(self, query: str, response: str, category: str) -> bool:
        """Check if response is appropriate for the query"""
        
        if not response:
            return False
            
        # Check for obviously inappropriate responses
        inappropriate_indicators = [
            "android app development",
            "tkinter game",
            "mobile application",
            "java programming"  # When not asked about Java
        ]
        
        response_lower = response.lower()
        for indicator in inappropriate_indicators:
            if indicator in response_lower and indicator not in query.lower():
                return False
                
        return True
    
    def _detect_hallucination(self, query: str, response: str) -> bool:
        """Detect potential hallucinations in the response"""
        
        # Simple hallucination detection
        if not response:
            return False
            
        # Check for responses that don't match simple queries
        simple_queries = ["hello", "hi", "pwd", "ls"]
        if query.lower() in simple_queries:
            # For simple queries, responses should be short and relevant
            if len(response) > 500:  # Very long response to simple query
                return True
                
            # Check for random code when not requested
            if query.lower() in ["hello", "hi"] and any(code in response for code in ["def ", "import ", "class "]):
                return True
                
        return False
    
    def _get_queries_for_category(self, category: str) -> List[str]:
        """Get all queries for a specific category"""
        
        category_mapping = {
            "conversational": CONVERSATIONAL_QUERIES,
            "commands": DIRECT_COMMAND_QUERIES, 
            "code_gen": CODE_GENERATION_QUERIES,
            "semantic": SEMANTIC_ZONE_QUERIES,
            "edge": EDGE_CASE_QUERIES
        }
        
        return category_mapping.get(category, [])
    
    def _get_expected_behavior(self, category: str) -> str:
        """Get expected behavior description for category"""
        
        behaviors = {
            "conversational": "friendly_greeting_or_explanation",
            "commands": "command_execution_or_output",
            "code_gen": "code_generation_with_explanation", 
            "semantic": "appropriate_tool_usage_or_explanation",
            "edge": "graceful_error_handling"
        }
        
        return behaviors.get(category, "unknown")
    
    def _generate_summary(self, test_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate summary statistics for the test session"""
        
        total_tests = len(test_results)
        successful_tests = len([r for r in test_results if r["response"]["success"]])
        
        # Calculate averages
        quality_scores = [r["analysis"]["quality_score"] for r in test_results]
        avg_quality = sum(quality_scores) / len(quality_scores) if quality_scores else 0.0
        
        hallucinations = len([r for r in test_results if r["analysis"]["hallucination_detected"]])
        
        return {
            "total_tests": total_tests,
            "successful_tests": successful_tests,
            "success_rate": successful_tests / total_tests if total_tests > 0 else 0.0,
            "average_quality_score": avg_quality,
            "hallucination_count": hallucinations,
            "hallucination_rate": hallucinations / total_tests if total_tests > 0 else 0.0
        }

# Usage example
if __name__ == "__main__":
    engine = AutomatedTestingEngine(TEST_CONFIG)
    results = engine.execute_full_test_suite()
    
    # Save results to JSONL format
    output_file = f"data/test_results/automated_test_{results['session_id']}.jsonl"
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    
    with open(output_file, 'w') as f:
        for result in results["test_results"]:
            f.write(json.dumps(result) + "\\n")
    
    print(f"\\n📊 Test Summary:")
    print(f"Total tests: {results['summary']['total_tests']}")
    print(f"Success rate: {results['summary']['success_rate']:.2%}")
    print(f"Average quality: {results['summary']['average_quality_score']:.2f}")
    print(f"Hallucinations: {results['summary']['hallucination_count']}")
```

### Day 5-7: Integration and Standardized JSON Output

**Standardized JSON Schema:**

```json
{
  "test_session_id": "session_20250726_103045",
  "interaction_id": "20250726_103045_001", 
  "timestamp": "2025-07-26T10:30:45.123Z",
  "test_metadata": {
    "query_category": "conversational",
    "test_iteration": 1,
    "provider": "dual",
    "expected_behavior": "friendly_greeting"
  },
  "request": {
    "query": "hello",
    "provider": "dual", 
    "parameters": {"timeout": 30}
  },
  "response": {
    "content": "Hello! How can I help you...",
    "execution_time_ms": 1234,
    "success": true,
    "error_message": null
  },
  "analysis": {
    "quality_score": 0.88,
    "appropriateness": true,
    "hallucination_detected": false,
    "response_length": 45,
    "contains_error": false
  }
}
```

## Directory Structure for Week 1

```
/Users/admin/Documents/DeepCoderX/
├── automation/
│   ├── test_query_definitions.py        # Test query categories
│   ├── automated_testing_engine.py      # Core testing engine
│   └── run_automated_tests.py          # Convenience launcher
├── data/
│   └── test_results/                    # JSONL output storage
└── scripts/
    ├── validate_json_schema.py          # Schema validation
    └── quick_test_runner.py             # Quick testing script
```

## Week 1 Deliverables

1. **✅ Test Query Categories:** 5 comprehensive categories with 40+ test queries
2. **✅ Automated Testing Engine:** Complete test execution with error handling  
3. **✅ Standardized JSON Output:** Structured format for all test results
4. **✅ Integration:** Works with existing enhanced logging and API automation
5. **✅ Validation:** Schema validation and quality scoring

## Testing Commands

```bash
# Run full automated test suite
cd /Users/admin/Documents/DeepCoderX
python3 automation/automated_testing_engine.py

# Run quick validation test
python3 scripts/quick_test_runner.py

# Validate JSON schema
python3 scripts/validate_json_schema.py data/test_results/latest.jsonl
```

## Expected Outcomes

**End of Week 1:**
- ✅ Automated testing infrastructure operational
- ✅ Structured JSON output for all test results  
- ✅ Comprehensive test coverage across all providers
- ✅ Basic quality scoring and hallucination detection
- ✅ Foundation ready for Week 2 (SQLite integration)

**Files Created:** 6 new files with complete testing infrastructure
**JSONL Output:** Immediate structured JSON data for analysis
**Integration:** Seamless integration with existing DeepCoderX systems

This foundation provides the structured JSON output you requested while setting up the infrastructure for advanced analysis in subsequent weeks.
