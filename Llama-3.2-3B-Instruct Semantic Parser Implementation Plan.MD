# Llama-3.2-3B-Instruct Semantic Parser Implementation Plan

## Executive Summary

**Objective:** Integrate Llama-3.2-3B-Instruct as a semantic parser to enhance DeepCoderX's tool calling consistency and natural language understanding.

**Strategy:** Multi-layer tool call detection system with semantic understanding, progressive correction, and adaptive prompting.

**Timeline:** 4-6 implementation sessions for complete integration and testing.

## Phase 1: Foundation Setup (Session 1)

### 1.1 Model Integration Infrastructure

**Model Configuration:**
- Download Llama-3.2-3B-Instruct GGUF model (Q4_K_S quantization ~2GB)
- Place in `.cache/deepcoderx/models/` directory
- Update `config_module.py` to include semantic parser configuration

**Configuration Updates:**
```python
# Add to config_module.py
SEMANTIC_PARSER_MODEL = "Llama-3.2-3B-Instruct-uncensored.Q4_K_S.gguf"
SEMANTIC_PARSER_ENABLED = True
SEMANTIC_PARSER_MAX_TOKENS = 512  # Fast responses for intent classification
SEMANTIC_PARSER_TEMPERATURE = 0.1  # Consistent, deterministic responses
```

**Hardware Optimization:**
- Apple Silicon Metal acceleration enabled
- Reduced batch size for speed (128 vs 256 for main model)
- Optimized for fast inference (3x faster than Qwen models)
- Memory allocation: ~1.5GB for semantic parser + 3GB for main model = 4.5GB total

### 1.2 Semantic Parser Handler Creation with Zone Support

**File:** `/services/semantic_parser_handler.py`

**Core Responsibilities:**
- Semantic zone detection and classification
- Intent classification (tool_call, file_operation, git_command, analysis_request, general_query)
- Parameter extraction from natural language with zone context
- Command type detection (create, read, update, delete, analyze)
- Provider routing detection (@deepseek, @local, @openai)
- Multi-step operation planning
- Confidence scoring for routing decisions

**Key Methods:**
```python
class SemanticParserHandler:
    def detect_semantic_zones(self, user_input: str) -> Dict[str, Any]
    def classify_intent_with_zones(self, user_input: str, zones: Dict) -> IntentClassification
    def extract_parameters_from_zones(self, zones: Dict, intent: str) -> Dict[str, Any]
    def detect_provider_routing(self, zones: Dict) -> Optional[str]
    def plan_multi_step_operations(self, zones: Dict) -> List[Dict[str, Any]]
    def validate_tool_call_format(self, parsed_result: Dict) -> bool
    def get_confidence_score(self, classification: IntentClassification) -> float
```

**Zone-Aware Processing Pipeline:**
```python
# Enhanced processing with semantic zones
def process_user_input(self, user_input: str) -> Dict[str, Any]:
    # Step 1: Detect semantic zones
    zones = self.detect_semantic_zones(user_input)
    
    # Step 2: Extract provider routing if present
    provider = self.detect_provider_routing(zones)
    
    # Step 3: Classify intent using zone context
    intent = self.classify_intent_with_zones(user_input, zones)
    
    # Step 4: Extract parameters from zones
    parameters = self.extract_parameters_from_zones(zones, intent)
    
    # Step 5: Plan multi-step operations if needed
    operations = self.plan_multi_step_operations(zones)
    
    return {
        "zones": zones,
        "provider": provider,
        "intent": intent,
        "parameters": parameters,
        "operations": operations,
        "confidence": self.get_confidence_score(intent)
    }
```

## Phase 2: Multi-Layer Detection System with Semantic Zones (Session 2)

### 2.1 Enhanced Tool Call Detection Pipeline with Semantic Zones

**Architecture:**
```
User Input → Semantic Zone Detection → Semantic Parser → Intent Classification → Parameter Extraction → Validation → Tool Execution
                      ↓                      ↓                    ↓                     ↓               ↓
              Zone Classification      Primary Parser      Fuzzy Matcher      Format Validator    Error Recovery
```

**File:** `/services/enhanced_tool_detector.py`

**Detection Layers:**
1. **Semantic Zone Classifier:** Pre-processing to identify command zones and patterns
2. **Primary Semantic Parser:** Llama-3.2-3B for natural language understanding
3. **Fuzzy Pattern Matcher:** Regex-based fallback for common patterns
4. **Format Validator:** Ensures proper tool call structure
5. **Progressive Enhancement:** Escalates through multiple prompting strategies

### 2.2 Semantic Zones Implementation

**Zone Categories and Patterns:**
```python
SEMANTIC_ZONES = {
    # Tool directive zones
    "TOOL_DIRECTIVE": [
        r"use your tools",
        r"with tools", 
        r"using tools",
        r"tool.*:",
        r"@\w+.*use.*tools"
    ],
    
    # File operation zones
    "FILE_OPERATIONS": [
        r"write\s+(file|report)",
        r"read\s+(file|dir)",
        r"create\s+(file|dir)", 
        r"save\s+(file|to)",
        r"analyse?\s+file"
    ],
    
    # Analysis zones
    "ANALYSIS_OPERATIONS": [
        r"audit\s+codebase",
        r"analyze\s+code",
        r"review\s+project",
        r"examine\s+\w+",
        r"inspect\s+\w+"
    ],
    
    # Path specification zones
    "PATH_SPECIFICATIONS": [
        r"path:\s*(/[\w/.-]+)",
        r"in\s+(/[\w/.-]+)",
        r"at\s+(/[\w/.-]+)",
        r"from\s+(/[\w/.-]+)"
    ],
    
    # Provider routing zones
    "PROVIDER_ROUTING": [
        r"@(\w+)\s+",
        r"using\s+(\w+)\s+provider",
        r"with\s+(\w+)\s+model"
    ]
}
```

**Example Command Patterns:**
```bash
# Complex multi-zone commands
"@deepseek use your tools: audit codebase path: /your/project/here and write report"
"use your tools: read file config.py and analyse for security issues"
"@local with tools: create file main.py and write basic Flask app"
"use tools: read dir /src and audit code then save report to analysis.md"
```

### 2.3 Intent Classification System with Zone Context

**Enhanced Intent Categories:**
- `TOOL_CALL_WITH_ANALYSIS`: Tool usage for analysis tasks
- `TOOL_CALL_WITH_FILE_OPS`: Tool usage for file operations
- `PROVIDER_ROUTED_COMMAND`: Commands with explicit provider routing
- `MULTI_STEP_OPERATION`: Commands requiring sequential tool calls
- `FILE_OPERATION`: File system operations (create, read, write, save)
- `ANALYSIS_REQUEST`: Code analysis and auditing with path context
- `GENERAL_QUERY`: Information requests
- `AMBIGUOUS`: Requires clarification

**Zone-Aware Classification Prompts:**
```yaml
# Add to gguf_prompts.yaml
semantic_parser:
  zone_classification:
    system_prompt: |
      You are a semantic zone classifier. Identify command zones and extract structured information.
      Detect: tool directives, file operations, analysis requests, path specifications, provider routing.
      
    examples:
      - input: "@deepseek use your tools: audit codebase path: /your/project/here and write report"
        zones: {
          "provider": "deepseek",
          "tool_directive": true,
          "analysis": "audit codebase", 
          "path": "/your/project/here",
          "output": "write report"
        }
        
      - input: "use your tools: read file config.py and analyse for security"
        zones: {
          "tool_directive": true,
          "file_operation": "read file config.py",
          "analysis": "security analysis"
        }

  intent_classification:
    system_prompt: |
      You are a semantic parser for a coding assistant. Use detected zones to classify user requests.
      Respond with JSON format: {"intent": "category", "confidence": 0.95, "parameters": {...}, "zones": {...}}
    
    examples:
      - input: "create a new Python file called main.py"
        output: {
          "intent": "FILE_OPERATION", 
          "confidence": 0.98, 
          "parameters": {"action": "create", "file": "main.py", "type": "python"},
          "zones": {"file_operation": "create file"}
        }
      
      - input: "@deepseek use your tools: audit codebase path: /project and write report"
        output: {
          "intent": "TOOL_CALL_WITH_ANALYSIS",
          "confidence": 0.97,
          "parameters": {
            "provider": "deepseek",
            "action": "audit",
            "target": "codebase", 
            "path": "/project",
            "output": "report"
          },
          "zones": {
            "provider": "deepseek",
            "tool_directive": true,
            "analysis": "audit codebase",
            "path": "/project",
            "output": "write report"
          }
        }
```

### 2.4 Semantic Zone Parser Implementation

**File:** `/services/semantic_zone_parser.py`

**Core Methods:**
```python
class SemanticZoneParser:
    def detect_zones(self, user_input: str) -> Dict[str, Any]
    def extract_provider_routing(self, zones: Dict) -> Optional[str]
    def extract_tool_directives(self, zones: Dict) -> List[str]
    def extract_file_operations(self, zones: Dict) -> List[Dict]
    def extract_analysis_requests(self, zones: Dict) -> List[Dict]
    def extract_path_specifications(self, zones: Dict) -> List[str]
    def build_structured_command(self, zones: Dict) -> Dict[str, Any]
```

**Zone Detection Algorithm:**
1. **Pattern Matching:** Apply regex patterns to identify semantic zones
2. **Context Extraction:** Extract parameters and targets from each zone
3. **Relationship Mapping:** Understand relationships between zones (path → analysis)
4. **Command Structuring:** Build structured command representation
5. **Validation:** Ensure extracted information is consistent and complete

## Phase 3: Context-Aware Processing (Session 3)

### 3.1 Context Manager Enhancement

**File:** `/services/semantic_context_manager.py`

**Context Tracking:**
- Previous commands and their outcomes
- Current project structure awareness
- User preference learning
- Common command patterns

**Features:**
- **Command History Analysis:** Learn user patterns and preferences
- **Project Context Integration:** Understand current working directory and project structure
- **Disambiguation Logic:** Resolve ambiguous requests using context
- **Adaptive Behavior:** Improve classification accuracy over time

### 3.2 Progressive Correction System

**Multi-Stage Validation:**
1. **Initial Classification:** Semantic parser first pass
2. **Context Validation:** Check against project state and history
3. **Format Verification:** Ensure tool call format compatibility
4. **Confidence Thresholding:** Route to appropriate handler based on confidence

**Correction Pipeline:**
```python
def progressive_correction(self, user_input: str, initial_classification: IntentClassification):
    if initial_classification.confidence < 0.7:
        # Re-process with enhanced context
        enhanced_result = self.reclassify_with_context(user_input)
        
    if enhanced_result.confidence < 0.5:
        # Fallback to fuzzy matching
        fallback_result = self.fuzzy_pattern_match(user_input)
        
    if all_results_low_confidence:
        # Request clarification from user
        return self.request_clarification(user_input)
```

## Phase 4: Tool Call Enhancement (Session 4)

### 4.1 Semantic-Enhanced Tool Calling

**File:** `/services/semantic_tool_caller.py`

**Enhanced Features:**
- **Natural Language to Tool Call Translation:** Convert human requests to structured tool calls
- **Parameter Inference:** Fill in missing parameters using context and defaults
- **Multi-Step Command Planning:** Break complex requests into sequential tool calls
- **Error Recovery:** Intelligent retry with corrected parameters

### 4.2 Model Behavior Profiling

**Adaptive Learning System:**
- Track semantic parser accuracy over time
- Identify common failure patterns
- Adjust prompting strategies based on performance
- Build user-specific preference profiles

**Profiling Metrics:**
```python
class SemanticParserMetrics:
    def track_classification_accuracy(self, predicted: str, actual: str)
    def monitor_response_time(self, inference_duration: float)
    def analyze_failure_patterns(self, failed_classifications: List[Dict])
    def update_prompting_strategy(self, performance_data: Dict)
```

## Phase 5: Integration and Testing (Session 5)

### 5.1 Handler Integration

**File Updates:**
- `app.py`: Add semantic parser to handler registration
- `gguf_handler.py`: Integrate semantic preprocessing
- `command_processor.py`: Route through semantic parser first

**Integration Points:**
```python
# In command processing pipeline
user_input → semantic_parser.classify_intent() → route_to_appropriate_handler() → execute_command()
```

### 5.2 Comprehensive Testing Suite

**Test Files:**
- `test_semantic_parser.py`: Unit tests for intent classification
- `test_integration_semantic.py`: Integration tests with existing handlers  
- `test_performance_semantic.py`: Performance and speed benchmarks
- `test_accuracy_semantic.py`: Classification accuracy validation

**Test Scenarios:**
- Natural language tool requests
- Ambiguous command resolution
- Multi-step command planning
- Error recovery and correction
- Performance under various loads

## Phase 6: Performance Optimization (Session 6)

### 6.1 Speed Optimization

**Target Performance:**
- Intent classification: <200ms response time
- Tool call generation: <500ms end-to-end
- Memory efficiency: <2GB additional RAM usage
- CPU optimization: Leverage M4 Neural Engine

### 6.2 Accuracy Tuning

**Optimization Strategies:**
- Fine-tune prompting templates based on testing results
- Implement confidence threshold optimization
- Add domain-specific intent categories
- Enhance parameter extraction accuracy

## Implementation Architecture

### Core Components

```
┌─ SemanticParserHandler ─────────────────────────────────────┐
│  ├─ Intent Classification (Llama-3.2-3B)                   │
│  ├─ Parameter Extraction                                    │
│  ├─ Confidence Scoring                                      │
│  └─ Format Validation                                       │
└─────────────────────────────────────────────────────────────┘
                                ↓
┌─ Enhanced Tool Detector ────────────────────────────────────┐
│  ├─ Multi-Layer Detection                                   │
│  ├─ Progressive Correction                                  │
│  ├─ Fuzzy Pattern Matching                                  │
│  └─ Context-Aware Routing                                   │
└─────────────────────────────────────────────────────────────┘
                                ↓
┌─ Semantic Context Manager ──────────────────────────────────┐
│  ├─ Command History Analysis                                │
│  ├─ Project Structure Awareness                             │
│  ├─ User Preference Learning                                │
│  └─ Disambiguation Logic                                    │
└─────────────────────────────────────────────────────────────┘
```

### Integration with Existing System

**Before (Current):**
```
User Input → Provider Router → GGUF Handler → Tool Execution
```

**After (With Semantic Parser):**
```
User Input → Semantic Parser → Intent Classification → Enhanced Router → Optimized Handler → Tool Execution
```

## Success Metrics

### Quantitative Goals
- **Intent Classification Accuracy:** >95% for common coding tasks
- **Response Time:** <200ms for semantic parsing
- **Tool Call Success Rate:** >90% first-attempt success
- **Memory Efficiency:** <2GB additional RAM usage

### Qualitative Goals
- **Natural Language Understanding:** Handle conversational coding requests
- **Context Awareness:** Understand project state and user patterns
- **Error Recovery:** Graceful handling of ambiguous or unclear requests
- **User Experience:** Seamless integration with existing workflow

## Risk Mitigation

### Technical Risks
- **Model Loading Overhead:** Mitigated by optimized quantization and caching
- **Classification Accuracy:** Addressed through extensive testing and fine-tuning
- **Integration Complexity:** Managed through phased implementation approach
- **Performance Impact:** Minimized through speed optimization and efficient architecture

### Fallback Strategies
- **Model Loading Failure:** Graceful degradation to existing tool calling system
- **Low Confidence Classifications:** Automatic fallback to pattern matching
- **Memory Constraints:** Dynamic model loading/unloading based on availability
- **Performance Issues:** Configurable semantic parser enable/disable option

## File Structure Changes

### New Files Created
```
/services/
├── semantic_parser_handler.py          # Core semantic parser logic
├── enhanced_tool_detector.py           # Multi-layer detection system
├── semantic_context_manager.py         # Context awareness and learning
└── semantic_tool_caller.py            # Enhanced tool calling with semantics

/tests/
├── test_semantic_parser.py            # Unit tests
├── test_integration_semantic.py       # Integration tests
├── test_performance_semantic.py       # Performance benchmarks
└── test_accuracy_semantic.py          # Accuracy validation

/config/
└── semantic_parser_config.yaml        # Semantic parser prompting strategies
```

### Modified Files
```
config_module.py                        # Add semantic parser configuration
gguf_prompts.yaml                      # Add semantic parsing prompts
app.py                                 # Handler registration updates
command_processor.py                   # Integration with semantic parser
```

## Deployment Strategy

### Development Environment
- Test with existing Qwen2.5-Coder model initially
- Add Llama-3.2-3B semantic parser alongside
- Validate multi-model concurrent operation
- Performance testing on M4 24GB system

### Production Deployment
- Gradual rollout with feature flag control
- A/B testing between semantic and traditional parsing
- Monitoring and metrics collection
- User feedback integration for continuous improvement

## Conclusion

This implementation plan provides a comprehensive roadmap for integrating Llama-3.2-3B-Instruct as a semantic parser in DeepCoderX. The phased approach ensures systematic development, thorough testing, and seamless integration with the existing architecture while maintaining performance and reliability standards.

The semantic parser will significantly enhance DeepCoderX's natural language understanding capabilities, making it more intuitive and powerful for coding tasks while preserving the robust foundation already established.