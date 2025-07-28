#!/usr/bin/env python3
"""
Quick Migration Analysis for DeepCoderX Legacy Handlers

This script performs a rapid analysis of legacy handlers and generates
a migration plan for the next phase of architectural improvements.
"""

import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def quick_analysis():
    """Perform quick analysis of legacy handlers."""
    print("📋 DeepCoderX Legacy Handler Quick Analysis")
    print("=" * 48)
    
    # Analyze key legacy files
    legacy_files = {
        "services/llm_handler.py": "Legacy LLM handlers with manual HTTP requests",
        "services/mcpclient.py": "Legacy MCP client implementation", 
        "services/structured_tools.py": "Legacy tool parsing with regex"
    }
    
    analysis_results = {}
    
    for file_path, description in legacy_files.items():
        full_path = project_root / file_path
        
        if not full_path.exists():
            print(f"   ⚠️  {file_path}: FILE NOT FOUND")
            continue
        
        print(f"\n🔍 Analyzing {file_path}")
        
        try:
            with open(full_path, 'r') as f:
                content = f.read()
            
            # Count legacy patterns
            legacy_indicators = {
                "Manual HTTP requests": content.count("requests.post") + content.count("requests.get"),
                "Hardcoded tool definitions": content.count('"tool":'),
                "Regex tool parsing": content.count("re.findall") + content.count("re.search"),
                "String error formatting": content.count("[red]Error:[/]"),
                "Direct MCP calls": content.count("mcp_client."),
                "Legacy imports": content.count("llama_cpp") + content.count("from llama_cpp")
            }
            
            # Count unified patterns  
            unified_indicators = {
                "OpenAI client usage": content.count("OpenAI(") + content.count("from openai"),
                "Tool registry usage": content.count("tool_registry") + content.count("get_tools_for_provider"),
                "Error handler usage": content.count("ErrorHandler") + content.count("tool_error("),
                "Unified handler inheritance": content.count("OpenAIHandler")
            }
            
            # Calculate scores
            legacy_count = sum(legacy_indicators.values())
            unified_count = sum(unified_indicators.values())
            
            # Determine migration priority
            if legacy_count >= 10:
                priority = "HIGH"
            elif legacy_count >= 5:
                priority = "MEDIUM"
            else:
                priority = "LOW"
            
            compatibility_score = max(0, 100 - (legacy_count * 10) + (unified_count * 5))
            compatibility_score = min(100, compatibility_score)
            
            print(f"   📊 Legacy patterns found: {legacy_count}")
            print(f"   📊 Unified patterns found: {unified_count}")
            print(f"   📊 Compatibility score: {compatibility_score}%")
            print(f"   🎯 Migration priority: {priority}")
            
            # Store results
            analysis_results[file_path] = {
                "legacy_count": legacy_count,
                "unified_count": unified_count,
                "compatibility_score": compatibility_score,
                "priority": priority,
                "description": description
            }
            
        except Exception as e:
            print(f"   ❌ Analysis failed: {e}")
            continue
    
    return analysis_results

def generate_migration_plan(analysis_results):
    """Generate a practical migration plan."""
    print(f"\n📋 MIGRATION PLAN GENERATION")
    print("=" * 30)
    
    # Sort by priority and compatibility score
    priority_order = {"HIGH": 3, "MEDIUM": 2, "LOW": 1}
    sorted_files = sorted(
        analysis_results.items(),
        key=lambda x: (priority_order.get(x[1]["priority"], 0), -x[1]["compatibility_score"]),
        reverse=True
    )
    
    migration_plan = []
    migration_plan.append("# DeepCoderX Legacy Handler Migration Plan")
    migration_plan.append(f"Generated: {sys.version}")
    migration_plan.append("")
    
    migration_plan.append("## Executive Summary")
    migration_plan.append(f"- Total handlers analyzed: {len(analysis_results)}")
    
    high_priority = sum(1 for _, data in analysis_results.items() if data["priority"] == "HIGH")
    medium_priority = sum(1 for _, data in analysis_results.items() if data["priority"] == "MEDIUM") 
    low_priority = sum(1 for _, data in analysis_results.items() if data["priority"] == "LOW")
    
    migration_plan.append(f"- High priority migrations: {high_priority}")
    migration_plan.append(f"- Medium priority migrations: {medium_priority}")
    migration_plan.append(f"- Low priority migrations: {low_priority}")
    migration_plan.append("")
    
    migration_plan.append("## Recommended Migration Order")
    migration_plan.append("")
    
    for i, (file_path, data) in enumerate(sorted_files, 1):
        migration_plan.append(f"### {i}. {file_path}")
        migration_plan.append(f"**Priority:** {data['priority']}")
        migration_plan.append(f"**Compatibility Score:** {data['compatibility_score']}%")
        migration_plan.append(f"**Description:** {data['description']}")
        migration_plan.append(f"**Legacy Patterns:** {data['legacy_count']}")
        migration_plan.append(f"**Unified Patterns:** {data['unified_count']}")
        migration_plan.append("")
    
    migration_plan.append("## Implementation Steps")
    migration_plan.append("")
    migration_plan.append("### Phase 1: High Priority (Immediate)")
    for file_path, data in sorted_files:
        if data["priority"] == "HIGH":
            migration_plan.append(f"- Migrate {file_path}")
            migration_plan.append(f"  - Replace manual HTTP with OpenAI client")
            migration_plan.append(f"  - Integrate Tool Registry Pattern")
            migration_plan.append(f"  - Standardize error handling")
    migration_plan.append("")
    
    migration_plan.append("### Phase 2: Medium Priority (Next Sprint)")
    for file_path, data in sorted_files:
        if data["priority"] == "MEDIUM":
            migration_plan.append(f"- Update {file_path}")
            migration_plan.append(f"  - Remove legacy patterns")
            migration_plan.append(f"  - Adopt unified architecture")
    migration_plan.append("")
    
    migration_plan.append("### Phase 3: Low Priority (Maintenance)")
    for file_path, data in sorted_files:
        if data["priority"] == "LOW":
            migration_plan.append(f"- Polish {file_path}")
            migration_plan.append(f"  - Minor architectural updates")
    migration_plan.append("")
    
    return "\n".join(migration_plan)

def main():
    """Execute migration analysis and planning."""
    # Perform analysis
    results = quick_analysis()
    
    if not results:
        print("\n❌ No files analyzed successfully")
        return 1
    
    # Generate plan
    plan = generate_migration_plan(results)
    
    # Save plan
    plan_file = project_root / "LEGACY_MIGRATION_PLAN.md"
    try:
        with open(plan_file, 'w') as f:
            f.write(plan)
        print(f"\n📄 Migration plan saved to: {plan_file}")
    except Exception as e:
        print(f"\n❌ Failed to save plan: {e}")
    
    print("\n📊 MIGRATION ANALYSIS COMPLETE")
    print("=" * 32)
    
    # Summary
    high_priority_files = [f for f, d in results.items() if d["priority"] == "HIGH"]
    
    if high_priority_files:
        print("🔥 HIGH PRIORITY MIGRATIONS NEEDED:")
        for file_path in high_priority_files:
            print(f"   - {file_path}")
        print("\n🚀 RECOMMENDATION: Start migration immediately")
    else:
        print("✅ NO HIGH PRIORITY MIGRATIONS")
        print("🚀 RECOMMENDATION: Proceed with medium priority migrations")
    
    return 0

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
