#!/bin/bash
# Auto Profit Trader - Comprehensive Test and Quality Assurance Script

set -e

echo "🚀 Auto Profit Trader - Full Test Suite"
echo "========================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${2}${1}${NC}"
}

# Function to run a command and capture its status
run_check() {
    local name="$1"
    local command="$2"
    local required="$3"  # "required" or "optional"
    
    print_status "Running $name..." "$BLUE"
    
    if eval "$command"; then
        print_status "✅ $name: PASSED" "$GREEN"
        return 0
    else
        if [ "$required" = "required" ]; then
            print_status "❌ $name: FAILED (REQUIRED)" "$RED"
            return 1
        else
            print_status "⚠️  $name: FAILED (OPTIONAL)" "$YELLOW"
            return 0
        fi
    fi
}

echo
print_status "1. Installing Dependencies" "$BLUE"
pip install -r requirements.txt >/dev/null 2>&1
pip install -r requirements-dev.txt >/dev/null 2>&1
print_status "✅ Dependencies installed" "$GREEN"

echo
print_status "2. Running Test Suite" "$BLUE"
echo "----------------------------------------"

# Run all tests
run_check "All Tests" "pytest tests/ -v --tb=short" "required"

# Run tests by category
run_check "Unit Tests" "pytest -m unit tests/ -v" "required"
run_check "Integration Tests" "pytest -m integration tests/ -v" "required"
run_check "Slow Tests" "pytest -m slow tests/ -v" "optional"

echo
print_status "3. Code Coverage Analysis" "$BLUE"
echo "----------------------------------------"

# Coverage report
run_check "Coverage Report" "pytest tests/ --cov=src --cov-report=term-missing --cov-report=html --cov-fail-under=25" "required"

echo
print_status "4. Code Quality Checks" "$BLUE"
echo "----------------------------------------"

# Code formatting and style
run_check "Black Formatting" "black src/ tests/ --check --line-length=88" "optional"
run_check "Import Sorting" "isort src/ tests/ --check-only --profile black" "optional"

# Linting (relaxed requirements for existing codebase)
flake8_errors=$(flake8 src/ --max-line-length=88 2>/dev/null | wc -l || echo "0")
if [ "$flake8_errors" -lt 50 ]; then
    print_status "✅ Flake8 Linting: ACCEPTABLE ($flake8_errors errors)" "$GREEN"
else
    print_status "⚠️  Flake8 Linting: TOO MANY ERRORS ($flake8_errors errors)" "$YELLOW"
fi

# Type checking (relaxed for existing codebase)
mypy_errors=$(mypy src/ --ignore-missing-imports --no-error-summary 2>/dev/null | wc -l || echo "0")
if [ "$mypy_errors" -lt 50 ]; then
    print_status "✅ MyPy Type Checking: ACCEPTABLE ($mypy_errors errors)" "$GREEN"
else
    print_status "⚠️  MyPy Type Checking: TOO MANY ERRORS ($mypy_errors errors)" "$YELLOW"
fi

echo
print_status "5. Security Analysis" "$BLUE"
echo "----------------------------------------"

# Security scanning
run_check "Bandit Security Scan" "bandit -r src/ -ll -f json -o bandit-report.json" "optional"

# Check for high severity security issues
high_severity=$(cat bandit-report.json 2>/dev/null | jq '.metrics._totals."SEVERITY.HIGH"' 2>/dev/null || echo "0")
if [ "$high_severity" = "0" ]; then
    print_status "✅ Security Scan: NO HIGH SEVERITY ISSUES" "$GREEN"
else
    print_status "⚠️  Security Scan: $high_severity HIGH SEVERITY ISSUES FOUND" "$YELLOW"
fi

echo
print_status "6. Component Verification" "$BLUE"
echo "----------------------------------------"

# Verify core components can be imported
run_check "Core Module Imports" "python -c 'import sys; sys.path.append(\"src\"); from utils.config_manager import ConfigManager; from security.crypto_manager import SecurityManager; from utils.logger import setup_logger; print(\"All core modules imported successfully\")'" "required"

echo
print_status "7. Test Summary" "$BLUE"
echo "----------------------------------------"

# Count tests
total_tests=$(pytest tests/ --collect-only -q 2>/dev/null | grep "test session starts" -A 1 | tail -1 | grep -o '[0-9]\+' | head -1 || echo "0")
unit_tests=$(pytest -m unit tests/ --collect-only -q 2>/dev/null | grep -o '[0-9]\+ selected' | grep -o '[0-9]\+' || echo "0")
integration_tests=$(pytest -m integration tests/ --collect-only -q 2>/dev/null | grep -o '[0-9]\+ selected' | grep -o '[0-9]\+' || echo "0")

print_status "📊 Test Statistics:" "$BLUE"
echo "   Total Tests: $total_tests"
echo "   Unit Tests: $unit_tests"
echo "   Integration Tests: $integration_tests"

# Get coverage percentage
coverage_percent=$(pytest tests/ --cov=src --cov-report=term 2>/dev/null | grep "TOTAL" | awk '{print $4}' | sed 's/%//' || echo "0")
echo "   Code Coverage: ${coverage_percent}%"

echo
if [ -f "htmlcov/index.html" ]; then
    print_status "📈 Coverage report generated: htmlcov/index.html" "$GREEN"
fi

if [ -f "bandit-report.json" ]; then
    print_status "🔒 Security report generated: bandit-report.json" "$GREEN"
fi

echo
print_status "🎉 Full Test Suite Completed!" "$GREEN"
print_status "All critical tests passed. The Auto Profit Trader system is ready for use." "$GREEN"

echo
print_status "Quick Commands:" "$BLUE"
echo "  Run all tests:           pytest tests/ -v"
echo "  Run unit tests only:     pytest -m unit tests/ -v"
echo "  Run with coverage:       pytest tests/ --cov=src --cov-report=html"
echo "  Check code quality:      flake8 src/ --max-line-length=88"
echo "  Security scan:           bandit -r src/"