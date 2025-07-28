{
  `path`: `/Users/admin/Documents/DeepCoderX/documentation/combined_automated_testing_implementation_plan.md`,
  `content`: `# Combined Automated Testing Implementation Plan
## DeepCoderX Model Behavior Analysis & Database Storage System

### Executive Summary

**Objective:** Create a comprehensive automated testing and analysis system for DeepCoderX that systematically monitors model behavior, detects hallucinations, and provides data-driven insights for optimization.

**Approach:** Hybrid JSONL + SQLite storage strategy leveraging existing enhanced logging infrastructure with automated testing engine and real-time analysis pipeline.

**Timeline:** 4-week phased implementation with immediate structured JSON output and progressive analytical capabilities.

---

## Current Infrastructure Analysis

### ✅ Existing Capabilities (Ready for Integration)

**Enhanced Logging System (100% Operational)**
- **Format:** JSONL (JSON Lines) with structured model interaction data
- **Location:** `logs/model_interactions/`
- **Coverage:** All prompts, responses, semantic analysis, tool execution
- **Integration:** 6 core logging functions operational across all handlers
- **Configuration:** Environment variable controls for selective logging

**API Automation Interface (Available)**
- **File:** `api_automation_example.py` provides programmatic DeepCoderX access
- **Capabilities:** Batch command execution, JSON export, all provider support
- **Integration:** Direct access to CommandContext and handler infrastructure

**Multi-Provider Testing Surface**
- **Dual Model System:** Llama 3.2-3B + Qwen2.5-Coder coordination
- **Local GGUF Handler:** Single model processing
- **Cloud Providers:** DeepSeek and OpenAI integration
- **Semantic Zones:** 5 zone types with intelligent routing

### ❌ Implementation Gaps (To Be Developed)

**Systematic Test Generation**
- Need structured test query categories and execution engine
- Automated test scheduling and session management
- Multi-provider systematic testing capabilities

**Automated Analysis Pipeline** 
- Log processing automation for pattern detection
- Behavior analysis and quality scoring systems
- Performance regression tracking and alerting

**Storage and Query Infrastructure**
- SQLite integration for fast complex queries
- Data import pipeline from JSONL to structured database
- Analysis tools and reporting dashboard

---

## Architecture Overview

### Hybrid JSONL + SQLite Storage Strategy

```
Automated Testing Engine → JSONL Logs → SQLite Importer → SQLite Database
                             ↓                              ↓
                        Raw Backup Data              Fast Query Engine
                             ↓                              ↓
                        Manual Inspection           Analysis Dashboard
```

**Benefits of Hybrid Approach:**
- ✅ **Immediate Implementation:** Leverages existing JSONL logging system
- ✅ **Structured JSON Output:** Exactly as requested for automated analysis
- ✅ **Progressive Enhancement:** Add SQLite for complex queries without disrupting current system
- ✅ **Data Safety:** JSONL files serve as authoritative human-readable backup
- ✅ **Performance Scaling:** SQL queries 10-100x faster than Python JSONL processing
- ✅ **Simple Deployment:** SQLite file-based, no database server required

---

## Phase 1: Foundation and Standardized JSON Output (Week 1)

### 1.1 Standardized JSON Schema Design

**Enhanced Test Result Format:**
```json
{
  \"test_session_id\": \"session_20250726_103045\",
  \"interaction_id\": \"20250726_103045_001\",
  \"timestamp\": \"2025-07-26T10:30:45.123Z\",
  \"test_metadata\": {
    \"query_category\": \"conversational\",
    \"test_iteration\": 1,
    \"provider\": \"dual\",
    \"expected_behavior\": \"friendly_greeting\",
    \"semantic_zone_expected\": \"conversational\"
  },
  \"request\": {
    \"query\": \"hello\",
    \"provider\": \"dual\",
    \"parameters\": {
      \"temperature\": 0.7,
      \"max_tokens\": 200,
      \"semantic_zones_enabled\": true
    }
  },
  \"response\": {
    \"content\": \"Hello! How can I help you with your coding projects today?\",
    \"execution_time_ms\": 1234,
    \"tokens_used\": 45,
    \"model_used\": \"Llama-3.2-3B\",
    \"success\": true,
    \"tool_calls_made\": 0,
    \"streaming_enabled\": false
  },
  \"analysis\": {
    \"semantic_zone_detected\": \"conversational\",
    \"zone_confidence\": 0.95,
    \"quality_score\": 0.88,
    \"appropriateness\": true,
    \"hallucination_detected\": false,
    \"consistency_with_previous\": 0.92,
    \"response_length\": 46,
    \"contains_code\": false,
    \"contains_tool_calls\": false
  },
  \"performance\": {
    \"memory_usage_mb\": 5120,
    \"cpu_usage_percent\": 15.5,
    \"gpu_usage_percent\": 45.2,
    \"model_loading_time_ms\": 0,
    \"semantic_analysis_time_ms\": 234
  },
  \"errors\": {
    \"has_errors\": false,
    \"error_type\": null,
    \"error_message\": null,
    \"stack_trace\": null
  }
}
```

### 1.2 Test Query Categories Implementation

**File:** `automation/test_query_definitions.py`

```python
# Comprehensive test query categories
CONVERSATIONAL_QUERIES = {
    \"basic_greetings\": [
        \"hello\",
        \"hi\",
        \"good morning\",
        \"how are you\",
        \"goodbye\"
    ],
    \"capability_questions\": [
        \"what can you do\",
        \"help me code\",
        \"what programming languages do you know\",
        \"can you write Python code\"
    ],
    \"general_knowledge\": [
        \"explain functions\",
        \"what is Python\",
        \"how does recursion work\",
        \"what are design patterns\"
    ],
    \"casual_conversation\": [
        \"tell me a joke\",
        \"what's the weather like\",
        \"why are apples green\",
        \"thank you\"
    ]
}

DIRECT_COMMAND_QUERIES = {
    \"file_operations\": [
        \"pwd\",
        \"ls\",
        \"ls -l\",
        \"ls -la\"
    ],
    \"git_operations\": [
        \"git status\",
        \"git log\",
        \"git branch\"
    ],
    \"system_commands\": [
        \"whoami\",
        \"date\",
        \"mkdir test_dir\"
    ]
}

CODE_GENERATION_QUERIES = {
    \"simple_scripts\": [
        \"create a hello world script\",
        \"write a function to add two numbers\",
        \"make a simple calculator\"
    ],
    \"file_operations\": [
        \"create a file reader\",
        \"write a CSV parser\",
        \"make a backup script\"
    ],
    \"data_structures\": [
        \"write a function to sort numbers\",
        \"create a dictionary example\",
        \"implement a simple list\"
    ]
}

SEMANTIC_ZONE_QUERIES = {
    \"tool_operation_zone\": [
        \"use your tools and read config.py\",
        \"file operations: examine the project structure\", 
        \"use tools to analyze the codebase\",
        \"tool usage: check git status\"
    ],
    \"conversational_zone\": [
        \"explain how recursion works\",
        \"what is the difference between async and sync\",
        \"describe object-oriented programming\",
        \"tell me about Python decorators\"
    ],
    \"analysis_zone\": [
        \"analyze this project structure\",
        \"review the code architecture\", 
        \"assess the current implementation\",
        \"examine the file organization\"
    ],
    \"debug_zone\": [
        \"debug this authentication error\",
        \"fix the broken database connection\",
        \"troubleshoot why tests are failing\",
        \"resolve import conflicts\"
    ],
    \"creative_zone\": [
        \"create a backup script\",
        \"generate a REST API endpoint\",
        \"build a simple web scraper\",
        \"design a data processing pipeline\"
    ]
}

EDGE_CASE_QUERIES = {
    \"empty_invalid\": [
        \"\",  # Empty input
        \" \",  # Whitespace only
        \"\
\
\",  # Newlines only
    ],
    \"random_text\": [
        \"asdfghjkl\",
        \"random meaningless text here\",
        \"xyz123abc\",
        \"!@#$%^&*()\"
    ],
    \"off_topic\": [
        \"What is the meaning of life?\",
        \"How do I bake a cake?\",
        \"What's the capital of France?\",
        \"Tell me about quantum physics\"
    ],
    \"potentially_harmful\": [
        \"sudo rm -rf /\",
        \"delete all files\",
        \"format my hard drive\",
        \"how to hack systems\"
    ],
    \"repetitive_long\": [
        \"hello \" * 50,
        \"write code \" * 25,
        \"explain \" * 30 + \"functions\"
    ]
}
```

### 1.3 Automated Testing Engine Core

**File:** `automation/automated_testing_engine.py`

```python
import asyncio
import json
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass

from api_automation_example import DeepCoderXAPI
from automation.test_query_definitions import *

@dataclass
class TestConfiguration:
    providers: List[str] = None
    query_categories: List[str] = None
    repetitions_per_query: int = 3
    delay_between_queries: float = 2.0
    max_execution_time: int = 30
    log_level: str = \"detailed\"
    session_id: str = None
    
    def __post_init__(self):
        if self.providers is None:
            self.providers = [\"dual\", \"local\", \"deepseek\"]
        if self.query_categories is None:
            self.query_categories = [\"conversational\", \"commands\", \"code_gen\", \"semantic\", \"edge\"]
        if self.session_id is None:
            self.session_id = f\"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}\"

class AutomatedTestingEngine:
    def __init__(self, config: TestConfiguration):
        self.config = config
        self.api = DeepCoderXAPI(debug_mode=True)
        self.results = []
        self.session_start_time = datetime.now()
        
    async def run_comprehensive_test_suite(self):
        \"\"\"Execute complete test suite across all providers and categories\"\"\"
        print(f\"🚀 Starting automated test suite: {self.config.session_id}\")
        print(f\"📊 Testing {len(self.config.providers)} providers with {len(self.config.query_categories)} categories\")
        
        for provider in self.config.providers:
            await self._test_provider(provider)
            
        self._generate_session_summary()
        self._save_results()
        
    async def _test_provider(self, provider: str):
        \"\"\"Test all query categories for a specific provider\"\"\"
        print(f\"\
🔧 Testing provider: {provider}\")
        
        for category in self.config.query_categories:
            await self._test_category(provider, category)
            
    async def _test_category(self, provider: str, category: str):
        \"\"\"Test all queries in a category for a provider\"\"\"
        queries = self._get_queries_for_category(category)
        
        for query in queries:
            await self._test_single_query(provider, category, query)
            
            # Delay between queries to avoid overwhelming the system
            if self.config.delay_between_queries > 0:
                await asyncio.sleep(self.config.delay_between_queries)
                
    async def _test_single_query(self, provider: str, category: str, query: str):
        \"\"\"Execute a single test query with comprehensive result capture\"\"\"
        for iteration in range(self.config.repetitions_per_query):
            interaction_id = f\"{self.config.session_id}_{provider}_{category}_{hash(query)}_{iteration}\"
            
            test_start_time = time.time()
            
            try:
                # Execute query through API
                result = self.api.execute_command(query, provider)
                execution_time_ms = (time.time() - test_start_time) * 1000
                
                # Analyze result and create structured test record
                test_record = self._create_test_record(
                    interaction_id=interaction_id,
                    provider=provider,
                    category=category,
                    query=query,
                    iteration=iteration,
                    result=result,
                    execution_time_ms=execution_time_ms
                )
                
                self.results.append(test_record)
                
                # Log progress
                status = \"✅\" if result.get(\"success\", False) else \"❌\"
                print(f\"{status} {provider}:{category} '{query}' -> {execution_time_ms:.0f}ms\")
                
            except Exception as e:
                # Handle and log errors
                error_record = self._create_error_record(
                    interaction_id=interaction_id,
                    provider=provider,
                    category=category,
                    query=query,
                    iteration=iteration,
                    error=e,
                    execution_time_ms=(time.time() - test_start_time) * 1000
                )
                
                self.results.append(error_record)
                print(f\"❌ {provider}:{category} '{query}' -> ERROR: {str(e)}\")
                
    def _save_results(self):
        \"\"\"Save test results to JSONL file\"\"\"
        output_dir = Path(\"logs/automated_testing\")
        output_dir.mkdir(exist_ok=True)
        
        output_file = output_dir / f\"{self.config.session_id}_results.jsonl\"
        
        with open(output_file, 'w') as f:
            for result in self.results:
                f.write(json.dumps(result) + '\
')
                
        print(f\"\
📁 Results saved to: {output_file}\")
        print(f\"📊 Total test records: {len(self.results)}\")
```

---

## Phase 2: SQLite Integration and Storage Infrastructure (Week 2)

### 2.1 SQLite Database Schema Design

**File:** `database/schema.sql`

```sql
-- Test sessions table for managing test runs
CREATE TABLE test_sessions (
    session_id TEXT PRIMARY KEY,
    start_time TIMESTAMP NOT NULL,
    end_time TIMESTAMP,
    total_queries INTEGER DEFAULT 0,
    successful_queries INTEGER DEFAULT 0,
    failed_queries INTEGER DEFAULT 0,
    providers_tested TEXT,  -- JSON array of providers
    categories_tested TEXT, -- JSON array of categories
    test_config TEXT,       -- JSON configuration used
    session_notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Main test results table
CREATE TABLE test_results (
    interaction_id TEXT PRIMARY KEY,
    session_id TEXT NOT NULL,
    timestamp TIMESTAMP NOT NULL,
    
    -- Test metadata
    query_category TEXT NOT NULL,
    test_iteration INTEGER NOT NULL,
    provider TEXT NOT NULL,
    expected_behavior TEXT,
    semantic_zone_expected TEXT,
    
    -- Request details
    query TEXT NOT NULL,
    request_parameters TEXT, -- JSON
    
    -- Response details
    response_content TEXT,
    execution_time_ms INTEGER,
    tokens_used INTEGER,
    model_used TEXT,
    success BOOLEAN NOT NULL,
    tool_calls_made INTEGER DEFAULT 0,
    streaming_enabled BOOLEAN DEFAULT FALSE,
    
    -- Analysis results
    semantic_zone_detected TEXT,
    zone_confidence REAL,
    quality_score REAL,
    appropriateness BOOLEAN,
    hallucination_detected BOOLEAN,
    consistency_with_previous REAL,
    response_length INTEGER,
    contains_code BOOLEAN,
    contains_tool_calls BOOLEAN,
    
    -- Performance metrics
    memory_usage_mb REAL,
    cpu_usage_percent REAL,
    gpu_usage_percent REAL,
    model_loading_time_ms INTEGER,
    semantic_analysis_time_ms INTEGER,
    
    -- Error information
    has_errors BOOLEAN DEFAULT FALSE,
    error_type TEXT,
    error_message TEXT,
    stack_trace TEXT,
    
    FOREIGN KEY (session_id) REFERENCES test_sessions(session_id)
);

-- Performance trends tracking
CREATE TABLE performance_trends (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    query_hash TEXT NOT NULL,  -- Hash of normalized query
    provider TEXT NOT NULL,
    timestamp TIMESTAMP NOT NULL,
    execution_time_ms INTEGER,
    quality_score REAL,
    success_rate REAL,
    sample_size INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Quality regression tracking
CREATE TABLE quality_regressions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    detection_time TIMESTAMP NOT NULL,
    provider TEXT NOT NULL,
    query_category TEXT NOT NULL,
    regression_type TEXT NOT NULL, -- 'hallucination', 'performance', 'quality'
    severity TEXT NOT NULL,        -- 'low', 'medium', 'high', 'critical'
    description TEXT,
    sample_interactions TEXT,      -- JSON array of interaction_ids
    resolved BOOLEAN DEFAULT FALSE,
    resolution_notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for optimal query performance
CREATE INDEX idx_test_results_provider ON test_results(provider);
CREATE INDEX idx_test_results_category ON test_results(query_category);
CREATE INDEX idx_test_results_timestamp ON test_results(timestamp);
CREATE INDEX idx_test_results_quality ON test_results(quality_score);
CREATE INDEX idx_test_results_hallucination ON test_results(hallucination_detected);
CREATE INDEX idx_test_results_success ON test_results(success);
CREATE INDEX idx_test_results_session ON test_results(session_id);
```

### 2.2 Data Import Pipeline Implementation

**File:** `database/data_importer.py`

```python
import sqlite3
import json
import time
from pathlib import Path
from typing import Dict, List
from datetime import datetime
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class TestDataImporter:
    \"\"\"Import test results from JSONL files into SQLite database\"\"\"
    
    def __init__(self, db_path: str = \"data/test_results.db\"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(exist_ok=True)
        self._initialize_database()
        
    def _initialize_database(self):
        \"\"\"Initialize SQLite database with schema\"\"\"
        conn = sqlite3.connect(self.db_path)
        
        # Read and execute schema
        schema_path = Path(__file__).parent / \"schema.sql\"
        with open(schema_path, 'r') as f:
            schema_sql = f.read()
            
        conn.executescript(schema_sql)
        conn.close()
        
    def import_jsonl_file(self, jsonl_path: str) -> Dict[str, int]:
        \"\"\"Import complete JSONL file into database\"\"\"
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        imported_count = 0
        error_count = 0
        
        try:
            with open(jsonl_path, 'r') as f:
                for line_num, line in enumerate(f, 1):
                    try:
                        test_record = json.loads(line.strip())
                        
                        # Insert session if not exists
                        self._insert_session_if_not_exists(cursor, test_record)
                        
                        # Insert test result
                        self._insert_test_result(cursor, test_record)
                        
                        # Update performance trends
                        self._update_performance_trends(cursor, test_record)
                        
                        imported_count += 1
                        
                    except json.JSONDecodeError as e:
                        print(f\"JSON error on line {line_num}: {e}\")
                        error_count += 1
                    except Exception as e:
                        print(f\"Import error on line {line_num}: {e}\")
                        error_count += 1
                        
            conn.commit()
            
        finally:
            conn.close()
            
        return {
            \"imported\": imported_count,
            \"errors\": error_count,
            \"total_lines\": imported_count + error_count
        }
        
    def _insert_test_result(self, cursor: sqlite3.Cursor, record: Dict):
        \"\"\"Insert test result record into database\"\"\"
        
        cursor.execute(\"\"\"
            INSERT OR REPLACE INTO test_results (
                interaction_id, session_id, timestamp, query_category, test_iteration,
                provider, expected_behavior, semantic_zone_expected, query,
                request_parameters, response_content, execution_time_ms, tokens_used,
                model_used, success, tool_calls_made, streaming_enabled,
                semantic_zone_detected, zone_confidence, quality_score, appropriateness,
                hallucination_detected, consistency_with_previous, response_length,
                contains_code, contains_tool_calls, memory_usage_mb, cpu_usage_percent,
                gpu_usage_percent, model_loading_time_ms, semantic_analysis_time_ms,
                has_errors, error_type, error_message, stack_trace
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        \"\"\", (
            record[\"interaction_id\"],
            record[\"test_session_id\"],
            record[\"timestamp\"],
            record[\"test_metadata\"][\"query_category\"],
            record[\"test_metadata\"][\"test_iteration\"],
            record[\"test_metadata\"][\"provider\"],
            record[\"test_metadata\"].get(\"expected_behavior\"),
            record[\"test_metadata\"].get(\"semantic_zone_expected\"),
            record[\"request\"][\"query\"],
            json.dumps(record[\"request\"][\"parameters\"]),
            record[\"response\"][\"content\"],
            record[\"response\"][\"execution_time_ms\"],
            record[\"response\"][\"tokens_used\"],
            record[\"response\"][\"model_used\"],
            record[\"response\"][\"success\"],
            record[\"response\"][\"tool_calls_made\"],
            record[\"response\"][\"streaming_enabled\"],
            record[\"analysis\"][\"semantic_zone_detected\"],
            record[\"analysis\"][\"zone_confidence\"],
            record[\"analysis\"][\"quality_score\"],
            record[\"analysis\"][\"appropriateness\"],
            record[\"analysis\"][\"hallucination_detected\"],
            record[\"analysis\"][\"consistency_with_previous\"],
            record[\"analysis\"][\"response_length\"],
            record[\"analysis\"][\"contains_code\"],
            record[\"analysis\"][\"contains_tool_calls\"],
            record[\"performance\"][\"memory_usage_mb\"],
            record[\"performance\"][\"cpu_usage_percent\"],
            record[\"performance\"][\"gpu_usage_percent\"],
            record[\"performance\"][\"model_loading_time_ms\"],
            record[\"performance\"][\"semantic_analysis_time_ms\"],
            record[\"errors\"][\"has_errors\"],
            record[\"errors\"][\"error_type\"],
            record[\"errors\"][\"error_message\"],
            record[\"errors\"][\"stack_trace\"]
        ))
        
    def real_time_import(self, jsonl_directory: str):
        \"\"\"Watch JSONL directory and import new files in real-time\"\"\"
        
        class JSONLHandler(FileSystemEventHandler):
            def __init__(self, importer):
                self.importer = importer
                
            def on_created(self, event):
                if event.is_file and event.src_path.endswith('.jsonl'):
                    time.sleep(1)  # Wait for file to be fully written
                    result = self.importer.import_jsonl_file(event.src_path)
                    print(f\"📥 Auto-imported {result['imported']} records from {event.src_path}\")
                    
        event_handler = JSONLHandler(self)
        observer = Observer()
        observer.schedule(event_handler, jsonl_directory, recursive=False)
        observer.start()
        
        print(f\"👀 Watching {jsonl_directory} for new JSONL files...\")
        return observer
```

### 2.3 Behavior Analysis Pipeline

**File:** `analysis/behavior_analyzer.py`

```python
import sqlite3
from typing import Dict, List, Tuple
from datetime import datetime, timedelta
import numpy as np
from dataclasses import dataclass

@dataclass
class HallucinationAlert:
    provider: str
    query: str
    response: str
    confidence: float
    timestamp: datetime
    interaction_id: str

@dataclass
class PerformanceRegression:
    provider: str
    query_category: str
    avg_time_before: float
    avg_time_after: float
    regression_percent: float
    sample_size: int

class BehaviorAnalyzer:
    \"\"\"Analyze model behavior patterns and detect issues\"\"\"
    
    def __init__(self, db_path: str = \"data/test_results.db\"):
        self.db_path = db_path
        
    def detect_hallucinations(self, days: int = 7) -> List[HallucinationAlert]:
        \"\"\"Detect potential hallucinations in recent responses\"\"\"
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Query for potential hallucinations
        cursor.execute(\"\"\"
            SELECT provider, query, response_content, quality_score, 
                   timestamp, interaction_id, hallucination_detected
            FROM test_results 
            WHERE timestamp > date('now', '-{} days')
            AND (hallucination_detected = true 
                 OR quality_score < 0.3
                 OR (query_category = 'conversational' 
                     AND response_length > 500)
                 OR (query LIKE '%hello%' 
                     AND response_content LIKE '%android%'))
            ORDER BY timestamp DESC
        \"\"\".format(days))
        
        results = cursor.fetchall()
        conn.close()
        
        alerts = []
        for row in results:
            provider, query, response, quality, timestamp, interaction_id, detected = row
            
            # Calculate confidence based on multiple factors
            confidence = 1.0 - quality if quality else 0.8
            if detected:
                confidence = max(confidence, 0.9)
                
            alerts.append(HallucinationAlert(
                provider=provider,
                query=query,
                response=response[:200] + \"...\" if len(response) > 200 else response,
                confidence=confidence,
                timestamp=datetime.fromisoformat(timestamp),
                interaction_id=interaction_id
            ))
            
        return alerts
        
    def measure_consistency(self, query: str, days: int = 30) -> Dict[str, float]:
        \"\"\"Measure response consistency for identical queries across providers\"\"\"
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute(\"\"\"
            SELECT provider, response_content, quality_score
            FROM test_results
            WHERE query = ? 
            AND timestamp > date('now', '-{} days')
            AND success = true
            ORDER BY provider, timestamp
        \"\"\".format(days), (query,))
        
        results = cursor.fetchall()
        conn.close()
        
        # Group by provider
        provider_responses = {}
        for provider, response, quality in results:
            if provider not in provider_responses:
                provider_responses[provider] = []
            provider_responses[provider].append((response, quality))
            
        # Calculate consistency scores
        consistency_scores = {}
        for provider, responses in provider_responses.items():
            if len(responses) < 2:
                consistency_scores[provider] = 1.0  # Perfect consistency with single response
                continue
                
            # Simple consistency: standard deviation of quality scores
            qualities = [r[1] for r in responses]
            consistency = 1.0 - (np.std(qualities) / np.mean(qualities) if np.mean(qualities) > 0 else 0)
            consistency_scores[provider] = max(0.0, min(1.0, consistency))
            
        return consistency_scores
        
    def analyze_semantic_routing_accuracy(self, days: int = 7) -> Dict[str, Dict[str, float]]:
        \"\"\"Analyze semantic zone detection accuracy\"\"\"
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute(\"\"\"
            SELECT semantic_zone_expected, semantic_zone_detected, 
                   zone_confidence, provider, query_category
            FROM test_results
            WHERE timestamp > date('now', '-{} days')
            AND semantic_zone_expected IS NOT NULL
        \"\"\".format(days))
        
        results = cursor.fetchall()
        conn.close()
        
        accuracy_by_provider = {}
        
        for expected, detected, confidence, provider, category in results:
            if provider not in accuracy_by_provider:
                accuracy_by_provider[provider] = {
                    \"correct\": 0,
                    \"total\": 0,
                    \"avg_confidence\": [],
                    \"category_accuracy\": {}
                }
                
            accuracy_by_provider[provider][\"total\"] += 1
            accuracy_by_provider[provider][\"avg_confidence\"].append(confidence or 0.0)
            
            if expected == detected:
                accuracy_by_provider[provider][\"correct\"] += 1
                
            # Track category-specific accuracy
            if category not in accuracy_by_provider[provider][\"category_accuracy\"]:
                accuracy_by_provider[provider][\"category_accuracy\"][category] = {\"correct\": 0, \"total\": 0}
                
            accuracy_by_provider[provider][\"category_accuracy\"][category][\"total\"] += 1
            if expected == detected:
                accuracy_by_provider[provider][\"category_accuracy\"][category][\"correct\"] += 1
                
        # Calculate final scores
        for provider in accuracy_by_provider:
            data = accuracy_by_provider[provider]
            data[\"accuracy\"] = data[\"correct\"] / data[\"total\"] if data[\"total\"] > 0 else 0.0
            data[\"avg_confidence\"] = np.mean(data[\"avg_confidence\"]) if data[\"avg_confidence\"] else 0.0
            
            # Calculate category accuracies
            for category in data[\"category_accuracy\"]:
                cat_data = data[\"category_accuracy\"][category]
                cat_data[\"accuracy\"] = cat_data[\"correct\"] / cat_data[\"total\"] if cat_data[\"total\"] > 0 else 0.0
                
        return accuracy_by_provider
        
    def detect_performance_regressions(self, comparison_days: int = 7, baseline_days: int = 14) -> List[PerformanceRegression]:
        \"\"\"Detect performance regressions by comparing recent vs baseline performance\"\"\"
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get recent performance
        cursor.execute(\"\"\"
            SELECT provider, query_category, AVG(execution_time_ms) as avg_time, COUNT(*) as count
            FROM test_results
            WHERE timestamp > date('now', '-{} days')
            AND success = true
            GROUP BY provider, query_category
            HAVING count >= 5
        \"\"\".format(comparison_days))
        
        recent_performance = {(row[0], row[1]): (row[2], row[3]) for row in cursor.fetchall()}
        
        # Get baseline performance
        cursor.execute(\"\"\"
            SELECT provider, query_category, AVG(execution_time_ms) as avg_time, COUNT(*) as count
            FROM test_results
            WHERE timestamp BETWEEN date('now', '-{} days') AND date('now', '-{} days')
            AND success = true
            GROUP BY provider,`
}



#-----------------------
# this is where you left off.
#-----------------------