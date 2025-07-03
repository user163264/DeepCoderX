#!/bin/bash
# DeepCoderX Test Script Runner
# This script helps you run all the validation tests for the architectural improvements

echo "🚀 DeepCoderX Architectural Validation Test Suite"
echo "=================================================="
echo

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}📍 Current Directory: $(pwd)${NC}"
echo -e "${BLUE}🐍 Python Version: $(python3 --version)${NC}"
echo

echo "📋 Available Test Categories:"
echo "1. 🔧 Immediate Fixes Validation"
echo "2. 🛠️  Tool Registry Pattern Tests"
echo "3. 🔄 Migration Phase 1 Tests"
echo "4. 🌩️  Cloud Provider Verification"
echo "5. 🏠 LM Studio Integration Tests"
echo "6. 🧪 Full Integration Suite"
echo "7. 🎯 Quick Validation Summary"
echo

# Function to run a test with error handling
run_test() {
    local test_file=$1
    local test_name=$2
    
    echo -e "${YELLOW}Running: $test_name${NC}"
    echo "----------------------------------------"
    
    if [ -f "$test_file" ]; then
        python3 "$test_file"
        local exit_code=$?
        
        if [ $exit_code -eq 0 ]; then
            echo -e "${GREEN}✅ $test_name PASSED${NC}"
        else
            echo -e "${RED}❌ $test_name FAILED (exit code: $exit_code)${NC}"
        fi
        echo
        return $exit_code
    else
        echo -e "${RED}❌ Test file not found: $test_file${NC}"
        echo
        return 1
    fi
}

# Function to check if required dependencies are installed
check_dependencies() {
    echo "🔍 Checking Dependencies..."
    
    # Check if Python is available
    if ! command -v python3 &> /dev/null; then
        echo -e "${RED}❌ Python 3 not found${NC}"
        return 1
    fi
    
    # Check if we're in the right directory
    if [ ! -f "app.py" ] || [ ! -f "config.py" ]; then
        echo -e "${RED}❌ Not in DeepCoderX project directory${NC}"
        echo "Please run this script from the DeepCoderX project root"
        return 1
    fi
    
    echo -e "${GREEN}✅ Dependencies check passed${NC}"
    return 0
}

# Main execution
if ! check_dependencies; then
    exit 1
fi

echo "Please select which tests to run:"
echo "1) Immediate Fixes Validation"
echo "2) Tool Registry Pattern Tests" 
echo "3) Migration Phase 1 Tests"
echo "4) Cloud Provider Verification"
echo "5) LM Studio Integration Tests (requires LM Studio)"
echo "6) Full Integration Suite"
echo "7) Quick Validation Summary"
echo "8) Run ALL tests"
echo "0) Exit"
echo

read -p "Enter your choice (0-8): " choice

case $choice in
    1)
        echo -e "${BLUE}🔧 Running Immediate Fixes Validation${NC}"
        run_test "validate_immediate_fixes.py" "Immediate Fixes Validation"
        ;;
    2)
        echo -e "${BLUE}🛠️  Running Tool Registry Pattern Tests${NC}"
        run_test "test_tool_registry.py" "Tool Registry Pattern"
        ;;
    3)
        echo -e "${BLUE}🔄 Running Migration Phase 1 Tests${NC}"
        run_test "test_migration_phase1.py" "Migration Phase 1"
        ;;
    4)
        echo -e "${BLUE}🌩️  Running Cloud Provider Verification${NC}"
        run_test "test_cloud_provider_verification.py" "Cloud Provider Verification"
        ;;
    5)
        echo -e "${BLUE}🏠 Running LM Studio Integration Tests${NC}"
        echo -e "${YELLOW}⚠️  Note: This requires LM Studio to be running on localhost:1234${NC}"
        run_test "test_lm_studio_integration.py" "LM Studio Integration"
        ;;
    6)
        echo -e "${BLUE}🧪 Running Full Integration Suite${NC}"
        run_test "test_integration.py" "Full Integration Suite"
        ;;
    7)
        echo -e "${BLUE}🎯 Running Quick Validation Summary${NC}"
        run_test "validation_summary.py" "Quick Validation Summary"
        ;;
    8)
        echo -e "${BLUE}🚀 Running ALL Tests${NC}"
        echo "This will run all available tests..."
        echo
        
        total_tests=0
        passed_tests=0
        
        # Run all tests
        tests=(
            "validate_immediate_fixes.py:Immediate Fixes Validation"
            "test_tool_registry.py:Tool Registry Pattern"
            "test_migration_phase1.py:Migration Phase 1"
            "test_cloud_provider_verification.py:Cloud Provider Verification"
            "test_integration.py:Full Integration Suite"
            "validation_summary.py:Quick Validation Summary"
        )
        
        for test_info in "${tests[@]}"; do
            IFS=':' read -r test_file test_name <<< "$test_info"
            total_tests=$((total_tests + 1))
            
            if run_test "$test_file" "$test_name"; then
                passed_tests=$((passed_tests + 1))
            fi
        done
        
        echo "=========================================="
        echo -e "${BLUE}📊 FINAL RESULTS${NC}"
        echo "=========================================="
        echo -e "Tests passed: ${GREEN}$passed_tests${NC}/$total_tests"
        
        if [ $passed_tests -eq $total_tests ]; then
            echo -e "${GREEN}🎉 ALL TESTS PASSED!${NC}"
            echo -e "${GREEN}DeepCoderX architectural improvements are working correctly.${NC}"
        else
            failed_tests=$((total_tests - passed_tests))
            echo -e "${YELLOW}⚠️  $failed_tests tests failed${NC}"
            echo -e "${YELLOW}Review the output above for specific issues.${NC}"
        fi
        ;;
    0)
        echo "Exiting..."
        exit 0
        ;;
    *)
        echo -e "${RED}Invalid choice. Please run the script again.${NC}"
        exit 1
        ;;
esac

echo
echo -e "${BLUE}🏁 Test execution complete!${NC}"
echo "For more details on any failing tests, run them individually with:"
echo "python3 <test_file_name>.py"
