"""
Enhanced Configuration Validation System for DeepCoderX

ADDRESSES AUDIT FINDING: Configuration Loading Chain Risk
- Multiple failure points in complex provider setup
- Explicit validation with clear error messages
- Configuration validation orchestrator

This system creates explicit validation stages with clear error reporting
and recovery mechanisms for configuration loading.
"""

import os
import logging
from pathlib import Path
from typing import Dict, Any, List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum
import re


class ValidationSeverity(Enum):
    """Validation issue severity levels."""
    CRITICAL = "critical"      # Prevents startup
    ERROR = "error"           # Feature disabled
    WARNING = "warning"       # Degraded functionality
    INFO = "info"            # Informational


@dataclass
class ValidationIssue:
    """Represents a configuration validation issue."""
    severity: ValidationSeverity
    component: str
    message: str
    fix_suggestion: Optional[str] = None
    
    def __str__(self) -> str:
        fix_text = f" Fix: {self.fix_suggestion}" if self.fix_suggestion else ""
        return f"[{self.severity.value.upper()}] {self.component}: {self.message}{fix_text}"


class ConfigurationValidator:
    """
    Enhanced configuration validator with explicit error reporting.
    
    Validates configuration in stages with clear error messages
    and actionable fix suggestions.
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.validation_issues: List[ValidationIssue] = []
        self.validated_components: List[str] = []
    
    def validate_complete_configuration(self, config_instance) -> Tuple[bool, List[ValidationIssue]]:
        """
        Validate complete configuration with staged validation.
        
        Returns:
            Tuple of (is_valid, validation_issues)
        """
        self.validation_issues.clear()
        self.validated_components.clear()
        
        # Stage 1: Core Environment Validation
        self._validate_environment_stage()
        
        # Stage 2: Provider Configuration Validation
        self._validate_providers_stage(config_instance)
        
        # Stage 3: Model Path Validation
        self._validate_model_paths_stage(config_instance)
        
        # Stage 4: Security and Permissions Validation
        self._validate_security_stage(config_instance)
        
        # Stage 5: Integration Dependencies Validation
        self._validate_integration_stage(config_instance)
        
        # Determine overall validation result
        has_critical_issues = any(
            issue.severity == ValidationSeverity.CRITICAL 
            for issue in self.validation_issues
        )
        
        is_valid = not has_critical_issues
        
        # Log validation summary
        self._log_validation_summary(is_valid)
        
        return is_valid, self.validation_issues.copy()
    
    def _validate_environment_stage(self) -> None:
        """Stage 1: Validate environment variables and basic setup."""
        self.logger.info("Configuration Validation Stage 1: Environment")
        
        # Check for .env file
        env_path = Path(__file__).parent.parent / '.env'
        if not env_path.exists():
            self.validation_issues.append(ValidationIssue(
                severity=ValidationSeverity.WARNING,
                component="Environment",
                message=".env file not found",
                fix_suggestion="Create .env file with required API keys"
            ))
        
        # Validate critical environment variables
        critical_env_vars = [
            ("DEEPSEEK_API_KEY", "DeepSeek API access"),
            ("SANDBOX_PATH", "File system sandbox")
        ]
        
        for env_var, purpose in critical_env_vars:
            value = os.getenv(env_var)
            if not value:
                self.validation_issues.append(ValidationIssue(
                    severity=ValidationSeverity.ERROR,
                    component="Environment",
                    message=f"Missing {env_var} environment variable ({purpose})",
                    fix_suggestion=f"Set {env_var} in .env file or environment"
                ))
        
        self.validated_components.append("Environment")
    
    def _validate_providers_stage(self, config_instance) -> None:
        """Stage 2: Validate provider configurations."""
        self.logger.info("Configuration Validation Stage 2: Providers")
        
        if not hasattr(config_instance, 'PROVIDERS'):
            self.validation_issues.append(ValidationIssue(
                severity=ValidationSeverity.CRITICAL,
                component="Providers",
                message="PROVIDERS configuration missing",
                fix_suggestion="Check config_module.py provider setup"
            ))
            return
        
        # Validate each provider
        for provider_name, provider_config in config_instance.PROVIDERS.items():
            self._validate_single_provider(provider_name, provider_config)
        
        # Validate default provider
        if hasattr(config_instance, 'DEFAULT_PROVIDER'):
            default_provider = config_instance.DEFAULT_PROVIDER
            if default_provider not in config_instance.PROVIDERS:
                self.validation_issues.append(ValidationIssue(
                    severity=ValidationSeverity.CRITICAL,
                    component="Providers",
                    message=f"Default provider '{default_provider}' not found in available providers",
                    fix_suggestion=f"Set DEFAULT_PROVIDER to one of: {', '.join(config_instance.PROVIDERS.keys())}"
                ))
            elif not config_instance.PROVIDERS[default_provider].get("enabled", False):
                self.validation_issues.append(ValidationIssue(
                    severity=ValidationSeverity.CRITICAL,
                    component="Providers",
                    message=f"Default provider '{default_provider}' is not enabled",
                    fix_suggestion=f"Enable {default_provider} provider or change DEFAULT_PROVIDER"
                ))
        
        self.validated_components.append("Providers")
    
    def _validate_single_provider(self, name: str, config: Dict[str, Any]) -> None:
        """Validate a single provider configuration."""
        if not config.get("enabled", False):
            return  # Skip disabled providers
        
        provider_type = config.get("model_type")
        
        if provider_type == "openai":
            # Validate OpenAI-compatible providers (DeepSeek, OpenAI)
            api_key = config.get("api_key")
            if not api_key:
                self.validation_issues.append(ValidationIssue(
                    severity=ValidationSeverity.ERROR,
                    component=f"Provider-{name}",
                    message=f"API key missing for {name} provider",
                    fix_suggestion=f"Set API key for {name} in environment variables"
                ))
            elif name == "deepseek" and not self._validate_deepseek_api_key_format(api_key):
                self.validation_issues.append(ValidationIssue(
                    severity=ValidationSeverity.ERROR,
                    component=f"Provider-{name}",
                    message="Invalid DeepSeek API key format",
                    fix_suggestion="DeepSeek API key should be sk-XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX (32 hex chars)"
                ))
            
            # Validate base URL if specified
            base_url = config.get("base_url")
            if base_url and not base_url.startswith("http"):
                self.validation_issues.append(ValidationIssue(
                    severity=ValidationSeverity.WARNING,
                    component=f"Provider-{name}",
                    message=f"Base URL may be invalid: {base_url}",
                    fix_suggestion="Ensure base URL starts with https://"
                ))
        
        elif provider_type == "gguf_direct":
            # Local GGUF provider validation handled in model paths stage
            pass
        
        else:
            self.validation_issues.append(ValidationIssue(
                severity=ValidationSeverity.WARNING,
                component=f"Provider-{name}",
                message=f"Unknown provider type: {provider_type}",
                fix_suggestion="Check provider configuration documentation"
            ))
    
    def _validate_deepseek_api_key_format(self, api_key: str) -> bool:
        """Validate DeepSeek API key format."""
        return bool(re.match(r'^sk-[0-9a-f]{32}$', api_key))
    
    def _validate_model_paths_stage(self, config_instance) -> None:
        """Stage 3: Validate model paths and files."""
        self.logger.info("Configuration Validation Stage 3: Model Paths")
        
        # Validate GGUF model path if local provider is enabled
        if hasattr(config_instance, 'PROVIDERS') and config_instance.PROVIDERS.get("local", {}).get("enabled", False):
            if hasattr(config_instance, 'GGUF_MODEL_PATH'):
                model_path = config_instance.GGUF_MODEL_PATH
                
                if not model_path:
                    self.validation_issues.append(ValidationIssue(
                        severity=ValidationSeverity.CRITICAL,
                        component="ModelPaths",
                        message="GGUF model path not configured",
                        fix_suggestion="Set GGUF_MODEL_PATH or place model in .cache directory"
                    ))
                elif not Path(model_path).exists():
                    self.validation_issues.append(ValidationIssue(
                        severity=ValidationSeverity.CRITICAL,
                        component="ModelPaths",
                        message=f"GGUF model file not found: {model_path}",
                        fix_suggestion="Download model file or update GGUF_MODEL_PATH"
                    ))
                elif not Path(model_path).is_file():
                    self.validation_issues.append(ValidationIssue(
                        severity=ValidationSeverity.CRITICAL,
                        component="ModelPaths",
                        message=f"GGUF model path is not a file: {model_path}",
                        fix_suggestion="Ensure GGUF_MODEL_PATH points to .gguf file"
                    ))
                else:
                    # Validate file size (GGUF models should be substantial)
                    file_size = Path(model_path).stat().st_size
                    if file_size < 100_000_000:  # Less than 100MB
                        self.validation_issues.append(ValidationIssue(
                            severity=ValidationSeverity.WARNING,
                            component="ModelPaths",
                            message=f"GGUF model file seems small ({file_size / 1_000_000:.1f}MB)",
                            fix_suggestion="Verify model file is complete and not corrupted"
                        ))
        
        self.validated_components.append("ModelPaths")
    
    def _validate_security_stage(self, config_instance) -> None:
        """Stage 4: Validate security and permissions."""
        self.logger.info("Configuration Validation Stage 4: Security")
        
        # Validate sandbox path
        if hasattr(config_instance, 'SANDBOX_PATH'):
            sandbox_path = Path(config_instance.SANDBOX_PATH)
            
            if not sandbox_path.exists():
                self.validation_issues.append(ValidationIssue(
                    severity=ValidationSeverity.CRITICAL,
                    component="Security",
                    message=f"Sandbox path does not exist: {sandbox_path}",
                    fix_suggestion="Create sandbox directory or update SANDBOX_PATH"
                ))
            elif not sandbox_path.is_dir():
                self.validation_issues.append(ValidationIssue(
                    severity=ValidationSeverity.CRITICAL,
                    component="Security",
                    message=f"Sandbox path is not a directory: {sandbox_path}",
                    fix_suggestion="Ensure SANDBOX_PATH points to a directory"
                ))
            else:
                # Check write permissions
                try:
                    test_file = sandbox_path / ".deepcoderx_test"
                    test_file.write_text("test")
                    test_file.unlink()  # Clean up
                except Exception as e:
                    self.validation_issues.append(ValidationIssue(
                        severity=ValidationSeverity.ERROR,
                        component="Security",
                        message=f"Cannot write to sandbox directory: {e}",
                        fix_suggestion="Check directory permissions for SANDBOX_PATH"
                    ))
        
        # Validate file size limits
        if hasattr(config_instance, 'MAX_FILE_SIZE'):
            max_size = config_instance.MAX_FILE_SIZE
            if max_size < 1024:  # Less than 1KB
                self.validation_issues.append(ValidationIssue(
                    severity=ValidationSeverity.WARNING,
                    component="Security",
                    message=f"MAX_FILE_SIZE very small ({max_size} bytes)",
                    fix_suggestion="Consider increasing MAX_FILE_SIZE"
                ))
        
        self.validated_components.append("Security")
    
    def _validate_integration_stage(self, config_instance) -> None:
        """Stage 5: Validate integration dependencies."""
        self.logger.info("Configuration Validation Stage 5: Integration")
        
        # Check for required Python packages
        required_packages = [
            ("llama_cpp", "GGUF model support"),
            ("openai", "OpenAI API compatibility"),
            ("yaml", "Configuration file parsing"),
            ("dotenv", "Environment variable loading")
        ]
        
        for package_name, purpose in required_packages:
            try:
                __import__(package_name)
            except ImportError:
                severity = ValidationSeverity.CRITICAL if package_name == "llama_cpp" else ValidationSeverity.WARNING
                self.validation_issues.append(ValidationIssue(
                    severity=severity,
                    component="Integration",
                    message=f"Required package '{package_name}' not found ({purpose})",
                    fix_suggestion=f"Install package: pip install {package_name}"
                ))
        
        # Validate MCP server configuration
        if hasattr(config_instance, 'MCP_SERVER_HOST') and hasattr(config_instance, 'MCP_SERVER_PORT'):
            # Basic validation of host/port format
            host = config_instance.MCP_SERVER_HOST
            port = config_instance.MCP_SERVER_PORT
            
            if not isinstance(port, int) or port < 1 or port > 65535:
                self.validation_issues.append(ValidationIssue(
                    severity=ValidationSeverity.WARNING,
                    component="Integration",
                    message=f"Invalid MCP server port: {port}",
                    fix_suggestion="Set MCP_SERVER_PORT to valid port number (1-65535)"
                ))
        
        self.validated_components.append("Integration")
    
    def _log_validation_summary(self, is_valid: bool) -> None:
        """Log validation summary."""
        if is_valid:
            self.logger.info(f"Configuration validation PASSED. Validated components: {', '.join(self.validated_components)}")
        else:
            self.logger.error("Configuration validation FAILED")
        
        # Log issues by severity
        for severity in ValidationSeverity:
            issues = [issue for issue in self.validation_issues if issue.severity == severity]
            if issues:
                self.logger.log(
                    logging.ERROR if severity in [ValidationSeverity.CRITICAL, ValidationSeverity.ERROR] else logging.WARNING,
                    f"{severity.value.upper()} issues ({len(issues)}): {[str(issue) for issue in issues]}"
                )
    
    def get_validation_report(self) -> str:
        """Generate human-readable validation report."""
        if not self.validation_issues:
            return "✅ Configuration validation passed - no issues found"
        
        report_lines = ["🔍 Configuration Validation Report", "=" * 40]
        
        # Group issues by severity
        for severity in ValidationSeverity:
            issues = [issue for issue in self.validation_issues if issue.severity == severity]
            if issues:
                icon = {"critical": "🚨", "error": "❌", "warning": "⚠️", "info": "ℹ️"}[severity.value]
                report_lines.append(f"\n{icon} {severity.value.upper()} ({len(issues)}):")
                for issue in issues:
                    report_lines.append(f"  • {issue.component}: {issue.message}")
                    if issue.fix_suggestion:
                        report_lines.append(f"    Fix: {issue.fix_suggestion}")
        
        # Summary
        critical_count = len([i for i in self.validation_issues if i.severity == ValidationSeverity.CRITICAL])
        if critical_count > 0:
            report_lines.append(f"\n🚨 CRITICAL: {critical_count} issues prevent startup")
        else:
            report_lines.append("\n✅ No critical issues - configuration can be used")
        
        return "\n".join(report_lines)


class ConfigurationRecovery:
    """
    Configuration recovery system for handling validation failures.
    
    Provides mechanisms to fix common configuration issues automatically
    or guide users through manual fixes.
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def attempt_auto_recovery(self, validation_issues: List[ValidationIssue]) -> List[ValidationIssue]:
        """
        Attempt automatic recovery for common configuration issues.
        
        Returns:
            List of remaining issues after recovery attempts
        """
        remaining_issues = []
        
        for issue in validation_issues:
            if self._can_auto_fix(issue):
                if self._attempt_fix(issue):
                    self.logger.info(f"Auto-fixed: {issue.component} - {issue.message}")
                else:
                    remaining_issues.append(issue)
            else:
                remaining_issues.append(issue)
        
        return remaining_issues
    
    def _can_auto_fix(self, issue: ValidationIssue) -> bool:
        """Check if an issue can be automatically fixed."""
        auto_fixable_patterns = [
            "Create sandbox directory",
            "Create .env file template",
            "Set default model path"
        ]
        
        return any(pattern in issue.fix_suggestion or "" for pattern in auto_fixable_patterns)
    
    def _attempt_fix(self, issue: ValidationIssue) -> bool:
        """Attempt to fix a specific issue."""
        try:
            if "sandbox directory" in issue.message.lower():
                # Create sandbox directory
                sandbox_path = Path.home() / "Documents" / "DeepCoderX_Sandbox"
                sandbox_path.mkdir(parents=True, exist_ok=True)
                self.logger.info(f"Created sandbox directory: {sandbox_path}")
                return True
            
            elif ".env file" in issue.message.lower():
                # Create basic .env template
                env_path = Path(__file__).parent.parent / '.env'
                if not env_path.exists():
                    env_template = """# DeepCoderX Configuration
# Copy this template and fill in your values

# API Keys
DEEPSEEK_API_KEY=sk-your-deepseek-api-key-here
OPENAI_API_KEY=sk-your-openai-api-key-here

# Paths
SANDBOX_PATH=/Users/admin/Documents/DeepCoderX_Sandbox

# MCP Configuration
MCP_API_KEY=secure_mcp_key_123
"""
                    env_path.write_text(env_template)
                    self.logger.info(f"Created .env template: {env_path}")
                    return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Auto-fix failed for {issue.component}: {e}")
            return False
    
    def generate_manual_fix_guide(self, validation_issues: List[ValidationIssue]) -> str:
        """Generate manual fix guide for remaining issues."""
        if not validation_issues:
            return "✅ No manual fixes required"
        
        guide_lines = [
            "🔧 Manual Configuration Fix Guide",
            "=" * 35,
            "",
            "Please address the following issues manually:"
        ]
        
        for i, issue in enumerate(validation_issues, 1):
            guide_lines.append(f"\n{i}. {issue.component}: {issue.message}")
            if issue.fix_suggestion:
                guide_lines.append(f"   → {issue.fix_suggestion}")
        
        guide_lines.extend([
            "",
            "After making these changes, restart the application.",
            "Run validation again to confirm all issues are resolved."
        ])
        
        return "\n".join(guide_lines)


# Integration functions for config_module.py
def validate_and_recover_configuration(config_instance) -> Tuple[bool, str]:
    """
    Validate configuration and attempt recovery.
    
    Returns:
        Tuple of (is_valid, status_message)
    """
    validator = ConfigurationValidator()
    is_valid, issues = validator.validate_complete_configuration(config_instance)
    
    if is_valid:
        return True, "✅ Configuration validation passed"
    
    # Attempt auto-recovery
    recovery = ConfigurationRecovery()
    remaining_issues = recovery.attempt_auto_recovery(issues)
    
    # Re-validate after recovery
    is_valid_after_recovery, _ = validator.validate_complete_configuration(config_instance)
    
    if is_valid_after_recovery:
        return True, "✅ Configuration validation passed after auto-recovery"
    
    # Generate reports
    validation_report = validator.get_validation_report()
    fix_guide = recovery.generate_manual_fix_guide(remaining_issues)
    
    status_message = f"{validation_report}\n\n{fix_guide}"
    
    return False, status_message


# Convenience function for external validation
def quick_validate_config(config_instance) -> bool:
    """Quick validation check - returns True if config is usable."""
    validator = ConfigurationValidator()
    is_valid, _ = validator.validate_complete_configuration(config_instance)
    return is_valid
