"""
Legacy Handler Migration Plan for DeepCoderX

This module provides a comprehensive plan and utilities for migrating legacy handlers
to the new unified architecture with tool registry pattern.
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from pathlib import Path
import inspect
import ast


@dataclass
class MigrationIssue:
    """Represents an issue found during migration analysis."""
    severity: str  # "critical", "warning", "info"
    component: str
    description: str
    suggestion: str
    line_number: Optional[int] = None


@dataclass
class MigrationReport:
    """Report generated from migration analysis."""
    handler_name: str
    compatibility_score: float  # 0-100
    issues: List[MigrationIssue]
    estimated_effort: str  # "low", "medium", "high"
    migration_priority: str  # "high", "medium", "low"


class LegacyHandlerAnalyzer:
    """Analyzes legacy handlers for migration readiness."""
    
    def __init__(self):
        self.legacy_patterns = {
            # Patterns that indicate legacy implementation
            "manual_http_requests": r"requests\.(get|post|put|delete)",
            "hardcoded_tools": r"\"tool\":\s*\"(read_file|write_file|list_dir|run_bash)\"",
            "regex_tool_parsing": r"re\.findall.*tool.*JSON",
            "string_error_formatting": r"\[red\]Error:\[/\]",
            "direct_mcp_calls": r"self\.ctx\.mcp_client\.",
            "duplicate_tool_logic": r"def.*execute.*tool",
            "legacy_imports": r"from.*llama_cpp.*import"
        }
        
        self.unified_patterns = {
            # Patterns that indicate unified implementation
            "openai_client": r"from openai import OpenAI",
            "tool_registry": r"from.*tool_registry.*import",
            "error_handler": r"from.*error_handler.*import",
            "unified_handler": r"class.*OpenAIHandler",
            "standardized_errors": r"ErrorHandler\.|tool_error\(|file_error\("
        }
    
    def analyze_handler(self, handler_path: Path) -> MigrationReport:
        """Analyze a legacy handler for migration readiness."""
        if not handler_path.exists():
            return MigrationReport(
                handler_name=handler_path.name,
                compatibility_score=0,
                issues=[MigrationIssue("critical", "file", "Handler file not found", "Create handler file")],
                estimated_effort="high",
                migration_priority="low"
            )
        
        with open(handler_path, 'r') as f:
            content = f.read()
        
        issues = []
        compatibility_score = 100
        
        # Check for legacy patterns (decrease score)
        for pattern_name, pattern in self.legacy_patterns.items():
            matches = self._find_pattern_matches(content, pattern)
            if matches:
                severity = self._get_pattern_severity(pattern_name)
                score_impact = self._get_score_impact(pattern_name)
                compatibility_score -= score_impact
                
                issues.append(MigrationIssue(
                    severity=severity,
                    component=pattern_name,
                    description=f"Uses legacy pattern: {pattern_name}",
                    suggestion=self._get_migration_suggestion(pattern_name),
                    line_number=matches[0] if matches else None
                ))
        
        # Check for unified patterns (increase score)
        for pattern_name, pattern in self.unified_patterns.items():
            matches = self._find_pattern_matches(content, pattern)
            if matches:
                compatibility_score += 5  # Bonus for already having unified patterns
        
        # Ensure score stays within bounds
        compatibility_score = max(0, min(100, compatibility_score))
        
        # Determine effort and priority
        estimated_effort = self._calculate_effort(issues)
        migration_priority = self._calculate_priority(compatibility_score, issues)
        
        return MigrationReport(
            handler_name=handler_path.name,
            compatibility_score=compatibility_score,
            issues=issues,
            estimated_effort=estimated_effort,
            migration_priority=migration_priority
        )
    
    def _find_pattern_matches(self, content: str, pattern: str) -> List[int]:
        """Find line numbers where pattern matches occur."""
        import re
        matches = []
        lines = content.split('\n')
        
        for i, line in enumerate(lines):
            if re.search(pattern, line):
                matches.append(i + 1)
        
        return matches
    
    def _get_pattern_severity(self, pattern_name: str) -> str:
        """Get severity level for a legacy pattern."""
        critical_patterns = ["manual_http_requests", "regex_tool_parsing", "duplicate_tool_logic"]
        warning_patterns = ["hardcoded_tools", "string_error_formatting", "direct_mcp_calls"]
        
        if pattern_name in critical_patterns:
            return "critical"
        elif pattern_name in warning_patterns:
            return "warning"
        else:
            return "info"
    
    def _get_score_impact(self, pattern_name: str) -> int:
        """Get score impact for a legacy pattern."""
        impacts = {
            "manual_http_requests": 30,
            "regex_tool_parsing": 25,
            "duplicate_tool_logic": 20,
            "hardcoded_tools": 15,
            "string_error_formatting": 10,
            "direct_mcp_calls": 10,
            "legacy_imports": 5
        }
        return impacts.get(pattern_name, 5)
    
    def _get_migration_suggestion(self, pattern_name: str) -> str:
        """Get migration suggestion for a legacy pattern."""
        suggestions = {
            "manual_http_requests": "Replace with OpenAI client from unified handler",
            "regex_tool_parsing": "Use native OpenAI tool calling format",
            "duplicate_tool_logic": "Use shared ToolExecutor from services/tool_executor.py",
            "hardcoded_tools": "Use Tool Registry Pattern from services/tool_registry.py",
            "string_error_formatting": "Use standardized error handling from services/error_handler.py",
            "direct_mcp_calls": "Use abstracted tool executor methods",
            "legacy_imports": "Update to use OpenAI-compatible imports"
        }
        return suggestions.get(pattern_name, "Update to use unified architecture")
    
    def _calculate_effort(self, issues: List[MigrationIssue]) -> str:
        """Calculate estimated migration effort."""
        critical_count = sum(1 for issue in issues if issue.severity == "critical")
        warning_count = sum(1 for issue in issues if issue.severity == "warning")
        
        if critical_count >= 3:
            return "high"
        elif critical_count >= 1 or warning_count >= 5:
            return "medium"
        else:
            return "low"
    
    def _calculate_priority(self, compatibility_score: float, issues: List[MigrationIssue]) -> str:
        """Calculate migration priority."""
        critical_count = sum(1 for issue in issues if issue.severity == "critical")
        
        if compatibility_score < 30 or critical_count >= 3:
            return "high"
        elif compatibility_score < 60 or critical_count >= 1:
            return "medium"
        else:
            return "low"


class MigrationPlanner:
    """Plans and coordinates legacy handler migrations."""
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.analyzer = LegacyHandlerAnalyzer()
        
    def analyze_all_handlers(self) -> Dict[str, MigrationReport]:
        """Analyze all legacy handlers in the project."""
        reports = {}
        
        # Legacy handlers to analyze
        legacy_handlers = [
            "services/llm_handler.py",
            "services/mcpclient.py",
            "services/structured_tools.py"
        ]
        
        for handler_path in legacy_handlers:
            full_path = self.project_root / handler_path
            report = self.analyzer.analyze_handler(full_path)
            reports[handler_path] = report
        
        return reports
    
    def generate_migration_plan(self) -> str:
        """Generate a comprehensive migration plan."""
        reports = self.analyze_all_handlers()
        
        plan = ["# DeepCoderX Legacy Handler Migration Plan\n"]
        plan.append("## Executive Summary\n")
        
        total_handlers = len(reports)
        high_priority = sum(1 for r in reports.values() if r.migration_priority == "high")
        medium_priority = sum(1 for r in reports.values() if r.migration_priority == "medium")
        low_priority = sum(1 for r in reports.values() if r.migration_priority == "low")
        
        avg_compatibility = sum(r.compatibility_score for r in reports.values()) / total_handlers if total_handlers > 0 else 0
        
        plan.append(f"- **Total Handlers Analyzed:** {total_handlers}")
        plan.append(f"- **Average Compatibility Score:** {avg_compatibility:.1f}%")
        plan.append(f"- **High Priority Migrations:** {high_priority}")
        plan.append(f"- **Medium Priority Migrations:** {medium_priority}")
        plan.append(f"- **Low Priority Migrations:** {low_priority}")
        plan.append("")
        
        # Prioritized migration order
        plan.append("## Recommended Migration Order\n")
        
        # Sort by priority and compatibility score
        sorted_reports = sorted(
            reports.items(),
            key=lambda x: (
                {"high": 3, "medium": 2, "low": 1}[x[1].migration_priority],
                -x[1].compatibility_score
            ),
            reverse=True
        )
        
        for i, (handler_path, report) in enumerate(sorted_reports, 1):
            plan.append(f"### {i}. {report.handler_name}")
            plan.append(f"**Priority:** {report.migration_priority.title()}")
            plan.append(f"**Compatibility Score:** {report.compatibility_score:.1f}%")
            plan.append(f"**Estimated Effort:** {report.estimated_effort.title()}")
            plan.append(f"**Critical Issues:** {sum(1 for issue in report.issues if issue.severity == 'critical')}")
            
            if report.issues:
                plan.append("\n**Key Issues to Address:**")
                for issue in report.issues[:3]:  # Show top 3 issues
                    plan.append(f"- {issue.description} → {issue.suggestion}")
            
            plan.append("")
        
        # Detailed migration phases
        plan.append("## Migration Phases\n")
        
        plan.append("### Phase 1: High Priority Handlers")
        plan.append("Focus on handlers with critical architectural issues that block unification.")
        for handler_path, report in sorted_reports:
            if report.migration_priority == "high":
                plan.append(f"- {report.handler_name}: {report.estimated_effort} effort")
        plan.append("")
        
        plan.append("### Phase 2: Medium Priority Handlers")
        plan.append("Migrate handlers with significant legacy patterns but lower impact.")
        for handler_path, report in sorted_reports:
            if report.migration_priority == "medium":
                plan.append(f"- {report.handler_name}: {report.estimated_effort} effort")
        plan.append("")
        
        plan.append("### Phase 3: Low Priority Handlers")
        plan.append("Complete migration of remaining handlers for full architectural consistency.")
        for handler_path, report in sorted_reports:
            if report.migration_priority == "low":
                plan.append(f"- {report.handler_name}: {report.estimated_effort} effort")
        plan.append("")
        
        # Implementation guidance
        plan.append("## Implementation Guidance\n")
        plan.append("### Step-by-Step Migration Process")
        plan.append("1. **Backup**: Create .BAK file before making changes")
        plan.append("2. **Import Updates**: Replace legacy imports with unified ones")
        plan.append("3. **Tool Integration**: Replace hardcoded tools with Tool Registry")
        plan.append("4. **Error Handling**: Replace string errors with standardized error handling")
        plan.append("5. **Testing**: Validate functionality with comprehensive tests")
        plan.append("6. **Documentation**: Update documentation and comments")
        plan.append("")
        
        plan.append("### Common Migration Patterns")
        plan.append("```python")
        plan.append("# Before (Legacy)")
        plan.append("response = requests.post(url, json=payload)")
        plan.append("errors = ['[red]Error:[/] Something failed']")
        plan.append("")
        plan.append("# After (Unified)")
        plan.append("response = self.client.chat.completions.create(**params)")
        plan.append("errors = [tool_error('tool_name', 'failure reason', 'helpful suggestion')]")
        plan.append("```")
        plan.append("")
        
        return "\n".join(plan)
    
    def create_migration_template(self, handler_name: str) -> str:
        """Create a migration template for a specific handler."""
        template = f'''"""
{handler_name} - Migrated to Unified Architecture

This handler has been migrated from legacy implementation to use:
- OpenAI-compatible client interface
- Tool Registry Pattern for tool management
- Standardized error handling
- Unified configuration system
"""

import os
import json
from typing import Dict, Any, List, Optional
from pathlib import Path

try:
    from openai import OpenAI
except ImportError:
    raise ImportError("OpenAI client not installed. Run: pip install openai>=1.0.0")

from config import config
from utils.logging import console, log_api_usage
from models.session import CommandContext
from models.router import CommandHandler
from services.tool_executor import ToolExecutor
from services.tool_registry import tool_registry, get_tools_for_provider
from services.error_handler import ErrorHandler, tool_error, api_error


class Migrated{handler_name.replace('.py', '').title()}Handler(CommandHandler):
    """
    Migrated version of {handler_name} using unified architecture.
    """
    
    def __init__(self, context: CommandContext, provider: str = None):
        super().__init__(context)
        self.provider_name = provider or config.DEFAULT_PROVIDER
        self.provider_config = config.PROVIDERS.get(self.provider_name)
        
        if not self.provider_config:
            raise ValueError(f"Unknown provider: {{self.provider_name}}")
        
        # Use unified OpenAI client
        self._client = None
        self.tool_executor = ToolExecutor(self.ctx, use_complex_path_resolution=True)
    
    @property
    def client(self) -> OpenAI:
        """Lazy load the OpenAI client."""
        if self._client is None:
            client_kwargs = {{"api_key": self.provider_config["api_key"]}}
            
            if self.provider_config["base_url"]:
                client_kwargs["base_url"] = self.provider_config["base_url"]
            
            self._client = OpenAI(**client_kwargs)
        
        return self._client
    
    def can_handle(self) -> bool:
        """Determine if this handler can process the request."""
        # TODO: Implement specific handling logic
        return True
    
    def handle(self) -> None:
        """Main processing method using unified architecture."""
        # TODO: Implement unified handling logic
        self.ctx.response = "Handler migrated to unified architecture"
    
    def _get_tool_definitions(self) -> List[Dict[str, Any]]:
        """Get tool definitions using Tool Registry."""
        return get_tools_for_provider(self.provider_name, self.provider_config)
    
    def _handle_errors(self, error: Exception) -> str:
        """Handle errors using standardized error handling."""
        if isinstance(error, requests.exceptions.ConnectionError):
            return api_error(self.provider_name, message="Connection failed")
        else:
            return tool_error("unknown", str(error), "Check logs for details")


# Migration Notes:
# 1. Replace manual HTTP requests with OpenAI client
# 2. Use Tool Registry instead of hardcoded tools  
# 3. Use standardized error handling
# 4. Update imports to use unified components
# 5. Test thoroughly before removing legacy handler
'''
        return template


def generate_migration_documentation():
    """Generate comprehensive migration documentation."""
    project_root = Path(__file__).parent
    planner = MigrationPlanner(project_root)
    
    # Generate migration plan
    migration_plan = planner.generate_migration_plan()
    
    # Save to file
    plan_file = project_root / "LEGACY_MIGRATION_PLAN.md"
    with open(plan_file, 'w') as f:
        f.write(migration_plan)
    
    print(f"Migration plan saved to: {plan_file}")
    
    return migration_plan


if __name__ == "__main__":
    # Generate migration documentation
    plan = generate_migration_documentation()
    print("\n" + "="*50)
    print("LEGACY HANDLER MIGRATION PLAN GENERATED")
    print("="*50)
    print(plan[:1000] + "..." if len(plan) > 1000 else plan)
