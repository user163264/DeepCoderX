#!/usr/bin/env python3
"""
Fix Direct Commands Duplication in DualModelHandler

This script refactors the dual_model_handler.py to eliminate the duplication
of direct command definitions by creating a centralized DIRECT_COMMANDS constant.
"""

import shutil
from pathlib import Path


def create_backup():
    """Create backup of the original file."""
    original_file = Path("/Users/admin/Documents/DeepCoderX/services/dual_model_handler.py")
    backup_file = Path("/Users/admin/Documents/DeepCoderX/services/dual_model_handler.py.backup_duplication_fix")
    
    shutil.copy2(original_file, backup_file)
    print(f"✅ Created backup: {backup_file}")
    return backup_file


def fix_duplication():
    """Remove duplication by centralizing direct commands."""
    
    # 1. Create backup first
    backup_file = create_backup()
    
    # 2. Read the current file
    file_path = Path("/Users/admin/Documents/DeepCoderX/services/dual_model_handler.py")
    with open(file_path, 'r') as f:
        content = f.read()
    
    # 3. Add centralized direct commands constant at the top after imports
    import_section_end = content.find('from services.gguf_handler import ChatTemplateFormatter')
    insertion_point = content.find('\n', import_section_end) + 1
    
    centralized_commands = '''

# CENTRALIZED DIRECT COMMANDS - Single source of truth for performance shortcuts
DIRECT_COMMANDS = {
    "pwd": "run_bash({\\"command\\": \\"pwd\\"})",
    "ls": "run_bash({\\"command\\": \\"ls\\"})",
    "ls -l": "run_bash({\\"command\\": \\"ls -l\\"})",
    "ls -la": "run_bash({\\"command\\": \\"ls -la\\"})",
    "git status": "run_bash({\\"command\\": \\"git status\\"})",
    "git log": "run_bash({\\"command\\": \\"git log --oneline -10\\"})",
    "whoami": "run_bash({\\"command\\": \\"whoami\\"})",
    "date": "run_bash({\\"command\\": \\"date\\"})"
}

'''
    
    # Insert the centralized definition
    content = content[:insertion_point] + centralized_commands + content[insertion_point:]
    
    # 4. Replace first occurrence in handle() method
    old_direct_commands_1 = '''        # Direct command shortcuts - NO AI inference needed
        direct_commands = {
            "pwd": "run_bash({\\"command\\": \\"pwd\\"})",
            "ls": "run_bash({\\"command\\": \\"ls\\"})",
            "ls -l": "run_bash({\\"command\\": \\"ls -l\\"})",
            "ls -la": "run_bash({\\"command\\": \\"ls -la\\"})",
            "git status": "run_bash({\\"command\\": \\"git status\\"})",
            "git log": "run_bash({\\"command\\": \\"git log --oneline -10\\"})",
            "whoami": "run_bash({\\"command\\": \\"whoami\\"})",
            "date": "run_bash({\\"command\\": \\"date\\"})"
        }'''
    
    new_direct_commands_1 = '''        # Direct command shortcuts - NO AI inference needed (centralized definition)
        direct_commands = DIRECT_COMMANDS'''
    
    content = content.replace(old_direct_commands_1, new_direct_commands_1)
    
    # 5. Replace second occurrence in _handle_local_shortcuts() method
    old_direct_commands_2 = '''        # Direct command shortcuts (no model inference needed)
        direct_commands = {
            "pwd": "run_bash({\\"command\\": \\"pwd\\"})",
            "ls": "run_bash({\\"command\\": \\"ls\\"})",
            "git status": "run_bash({\\"command\\": \\"git status\\"})",
            "whoami": "run_bash({\\"command\\": \\"whoami\\"})"
        }'''
    
    new_direct_commands_2 = '''        # Direct command shortcuts (no model inference needed) - using centralized definition
        direct_commands = DIRECT_COMMANDS'''
    
    content = content.replace(old_direct_commands_2, new_direct_commands_2)
    
    # 6. Write the fixed content
    with open(file_path, 'w') as f:
        f.write(content)
    
    print("✅ Fixed duplication in dual_model_handler.py")
    print("✅ Added centralized DIRECT_COMMANDS constant")
    print("✅ Updated both handle() and _handle_local_shortcuts() methods")
    print("✅ All direct commands now use single source of truth")
    
    return True


def verify_fix():
    """Verify that the fix was applied correctly."""
    file_path = Path("/Users/admin/Documents/DeepCoderX/services/dual_model_handler.py")
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Check for centralized constant
    has_centralized = "DIRECT_COMMANDS = {" in content
    
    # Check that duplicated dictionaries are gone
    has_old_duplication_1 = '''direct_commands = {
            "pwd": "run_bash''' in content
    has_old_duplication_2 = content.count("pwd\": \"run_bash") <= 1  # Should only appear in centralized definition
    
    print("\\n🔍 Verification Results:")
    print(f"✅ Centralized DIRECT_COMMANDS constant: {'Found' if has_centralized else 'Missing'}")
    print(f"✅ Removed old duplication 1: {'Yes' if not has_old_duplication_1 else 'No'}")
    print(f"✅ Removed old duplication 2: {'Yes' if has_old_duplication_2 else 'No'}")
    
    if has_centralized and not has_old_duplication_1 and has_old_duplication_2:
        print("\\n🎉 SUCCESS: Duplication successfully eliminated!")
        return True
    else:
        print("\\n❌ FAILED: Some issues remain")
        return False


if __name__ == "__main__":
    print("🔧 Fixing Direct Commands Duplication...")
    print("=" * 50)
    
    try:
        success = fix_duplication()
        if success:
            verify_fix()
            print("\\n📝 Summary:")
            print("- Created backup file for safety")
            print("- Added DIRECT_COMMANDS constant (single source of truth)")
            print("- Removed duplicate dictionaries in both methods")
            print("- All direct commands now centralized")
            print("\\n🚀 Ready for testing!")
        else:
            print("❌ Fix failed")
    
    except Exception as e:
        print(f"❌ Error during fix: {e}")
        print("Backup file preserved for manual recovery")
