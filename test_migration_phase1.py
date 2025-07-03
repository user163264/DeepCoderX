#!/usr/bin/env python3
"""
Migration Phase 1 Validation Test

This script validates that the handler migration is working correctly
and that unified handlers are being prioritized over legacy ones.
"""

import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

class MigrationValidator:
    """Validates migration phase 1 implementation."""
    
    def __init__(self):
        self.test_results = []
        
    def test_app_migration_changes(self):
        """Test that app.py has the correct migration changes."""
        print("🔄 Testing App.py Migration Changes")
        print("=" * 35)
        
        try:
            with open('app.py', 'r') as f:
                app_content = f.read()
            
            # Test 1: Check for deprecation comment
            if "# Legacy - deprecated in favor of LocalOpenAIHandler" in app_content:
                print("   ✅ Legacy handler marked as deprecated")
            else:
                print("   ❌ Legacy handler not properly marked as deprecated")
                return False
            
            # Test 2: Check for migration phase comment
            if "MIGRATION PHASE 1: Prioritize Unified Handlers" in app_content:
                print("   ✅ Migration phase comment present")
            else:
                print("   ❌ Migration phase comment missing")
                return False
            
            # Test 3: Check for unified architecture status
            if "Unified Architecture Handlers Active" in app_content:
                print("   ✅ Unified architecture status message present")
            else:
                print("   ❌ Unified architecture status message missing")
                return False
            
            # Test 4: Check for migration notification
            if "Running with Unified Architecture!" in app_content:
                print("   ✅ Migration notification present")
            else:
                print("   ❌ Migration notification missing")
                return False
            
            # Test 5: Check handler order (unified first)
            unified_handler_pos = app_content.find("CloudOpenAIHandler(ctx")
            legacy_handler_pos = app_content.find("LocalCodingHandler(ctx")
            
            if unified_handler_pos < legacy_handler_pos and unified_handler_pos != -1:
                print("   ✅ Unified handlers registered before legacy handlers")
            else:
                print("   ❌ Handler registration order incorrect")
                return False
            
            print("   ✅ App.py migration changes validated")
            return True
            
        except Exception as e:
            print(f"   ❌ App.py migration test failed: {e}")
            return False
    
    def test_backup_files_exist(self):
        """Test that backup files were created."""
        print("\n💾 Testing Backup Files")
        print("=" * 22)
        
        backup_files = [
            "app.py.BAK_MIGRATION",
            "services/unified_openai_handler.py.BAK7",
            "services/tool_executor.py.BAK8"
        ]
        
        all_backups_exist = True
        
        for backup_file in backup_files:
            if Path(backup_file).exists():
                print(f"   ✅ {backup_file} exists")
            else:
                print(f"   ❌ {backup_file} missing")
                all_backups_exist = False
        
        if all_backups_exist:
            print("   ✅ All backup files present")
            return True
        else:
            print("   ❌ Some backup files missing")
            return False
    
    def test_unified_handler_integration(self):
        """Test that unified handlers use tool registry and error handling."""
        print("\n🔧 Testing Unified Handler Integration")
        print("=" * 37)
        
        try:
            with open('services/unified_openai_handler.py', 'r') as f:
                handler_content = f.read()
            
            # Test 1: Tool registry integration
            if "from services.tool_registry import" in handler_content:
                print("   ✅ Tool registry import present")
            else:
                print("   ❌ Tool registry import missing")
                return False
            
            # Test 2: Uses get_tools_for_provider
            if "get_tools_for_provider(self.provider_name, self.provider_config)" in handler_content:
                print("   ✅ Uses tool registry function")
            else:
                print("   ❌ Not using tool registry function")
                return False
            
            # Test 3: Tool Registry Pattern comment
            if "Tool Registry Pattern" in handler_content:
                print("   ✅ Tool Registry Pattern documentation present")
            else:
                print("   ❌ Tool Registry Pattern documentation missing")
                return False
            
            print("   ✅ Unified handler integration validated")
            return True
            
        except Exception as e:
            print(f"   ❌ Unified handler integration test failed: {e}")
            return False
    
    def test_tool_registry_functionality(self):
        """Test that tool registry is functional."""
        print("\n🛠️  Testing Tool Registry Functionality")
        print("=" * 37)
        
        try:
            from services.tool_registry import tool_registry, get_tools_for_provider
            from config import config
            
            # Test 1: Registry has core tools
            tool_names = tool_registry.get_tool_names()
            expected_tools = ["read_file", "write_file", "list_dir", "run_bash"]
            
            if all(tool in tool_names for tool in expected_tools):
                print("   ✅ All core tools registered")
            else:
                missing = [tool for tool in expected_tools if tool not in tool_names]
                print(f"   ❌ Missing core tools: {missing}")
                return False
            
            # Test 2: Provider-specific tools
            local_config = config.PROVIDERS.get("local", {})
            local_tools = get_tools_for_provider("local", local_config)
            
            if len(local_tools) > 0:
                print(f"   ✅ Local provider gets {len(local_tools)} tools")
            else:
                print("   ❌ Local provider gets no tools")
                return False
            
            # Test 3: Tool validation
            valid_call = {"tool": "read_file", "path": "test.txt"}
            validation_result = tool_registry.validate_tool_call(valid_call)
            
            if validation_result["valid"]:
                print("   ✅ Tool validation works")
            else:
                print(f"   ❌ Tool validation failed: {validation_result['errors']}")
                return False
            
            print("   ✅ Tool registry functionality validated")
            return True
            
        except Exception as e:
            print(f"   ❌ Tool registry functionality test failed: {e}")
            return False
    
    def test_error_handling_integration(self):
        """Test that error handling is properly integrated."""
        print("\n🛡️  Testing Error Handling Integration")
        print("=" * 36)
        
        try:
            from services.error_handler import ErrorHandler, tool_error, file_error
            from services.tool_executor import ToolExecutor
            
            # Test 1: Error handler classes exist
            if hasattr(ErrorHandler, 'create_tool_error'):
                print("   ✅ ErrorHandler class functional")
            else:
                print("   ❌ ErrorHandler class missing methods")
                return False
            
            # Test 2: Convenience functions work
            test_error = tool_error("test_tool", "test message", "test suggestion")
            if "[red]" in test_error and "test message" in test_error:
                print("   ✅ Error formatting functions work")
            else:
                print("   ❌ Error formatting functions broken")
                return False
            
            # Test 3: Tool executor uses error handling
            with open('services/tool_executor.py', 'r') as f:
                executor_content = f.read()
            
            if "from services.error_handler import" in executor_content:
                print("   ✅ Tool executor imports error handling")
            else:
                print("   ❌ Tool executor missing error handling import")
                return False
            
            print("   ✅ Error handling integration validated")
            return True
            
        except Exception as e:
            print(f"   ❌ Error handling integration test failed: {e}")
            return False
    
    def test_migration_plan_exists(self):
        """Test that migration plan documentation exists."""
        print("\n📋 Testing Migration Documentation")
        print("=" * 33)
        
        plan_file = Path("LEGACY_MIGRATION_PLAN.md")
        
        if plan_file.exists():
            print("   ✅ Migration plan document exists")
            
            with open(plan_file, 'r') as f:
                plan_content = f.read()
            
            if "Phase 1" in plan_content and "services/llm_handler.py" in plan_content:
                print("   ✅ Migration plan contains phase information")
            else:
                print("   ❌ Migration plan missing phase details")
                return False
            
            if len(plan_content) > 1000:
                print(f"   ✅ Migration plan comprehensive ({len(plan_content)} characters)")
            else:
                print("   ❌ Migration plan too brief")
                return False
            
            return True
        else:
            print("   ❌ Migration plan document missing")
            return False
    
    def run_comprehensive_validation(self):
        """Run all migration validation tests."""
        print("🔄 Migration Phase 1 Validation Test Suite")
        print("=" * 45)
        
        results = []
        
        # Run all tests
        results.append(self.test_app_migration_changes())
        results.append(self.test_backup_files_exist())
        results.append(self.test_unified_handler_integration())
        results.append(self.test_tool_registry_functionality())
        results.append(self.test_error_handling_integration())
        results.append(self.test_migration_plan_exists())
        
        # Summary
        passed = sum(results)
        total = len(results)
        
        print(f"\n📊 MIGRATION VALIDATION SUMMARY")
        print("=" * 33)
        print(f"Tests passed: {passed}/{total}")
        
        if passed == total:
            print("🎉 ALL MIGRATION TESTS PASSED!")
            print("\n✅ Migration Phase 1 Status:")
            print("   - Handler registration prioritizes unified architecture")
            print("   - Tool Registry Pattern fully integrated")
            print("   - Standardized error handling active")
            print("   - Legacy handlers properly marked as deprecated")
            print("   - Migration documentation complete")
            print("   - All backup files created")
            
            print("\n🚀 Ready for Production Testing:")
            print("   - Test with actual LM Studio local model")
            print("   - Verify cloud provider functionality")
            print("   - Begin Phase 2: structured_tools.py migration")
            
            return True
        else:
            print("❌ SOME MIGRATION TESTS FAILED")
            print(f"   Issues: {total - passed} tests")
            print("   Review output above for specific problems")
            return False

def main():
    """Execute migration validation."""
    validator = MigrationValidator()
    success = validator.run_comprehensive_validation()
    
    if success:
        print("\n🎯 MIGRATION PHASE 1 COMPLETE")
        return 0
    else:
        print("\n⚠️  MIGRATION PHASE 1 NEEDS ATTENTION")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
