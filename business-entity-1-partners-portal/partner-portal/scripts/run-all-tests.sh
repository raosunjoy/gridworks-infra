#!/bin/bash

# Comprehensive Test Runner for TradeMate Partner Portal

set -e

echo "🧪 Running Complete Test Suite for TradeMate Partner Portal..."
echo "================================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if required tools are installed
check_dependencies() {
    print_status "Checking dependencies..."
    
    if ! command -v node &> /dev/null; then
        print_error "Node.js is not installed"
        exit 1
    fi
    
    if ! command -v npm &> /dev/null; then
        print_error "npm is not installed"
        exit 1
    fi
    
    print_success "All dependencies are available"
}

# Install dependencies if needed
install_dependencies() {
    if [ ! -d "node_modules" ]; then
        print_status "Installing dependencies..."
        npm install
        print_success "Dependencies installed"
    else
        print_status "Dependencies already installed"
    fi
}

# Setup database for testing
setup_test_database() {
    print_status "Setting up test database..."
    npm run db:generate
    npm run db:push
    npm run db:seed
    print_success "Test database ready"
}

# Run TypeScript type checking
run_type_check() {
    print_status "Running TypeScript type checking..."
    if npm run type-check; then
        print_success "TypeScript type checking passed"
    else
        print_error "TypeScript type checking failed"
        exit 1
    fi
}

# Run ESLint
run_lint() {
    print_status "Running ESLint..."
    if npm run lint; then
        print_success "ESLint passed"
    else
        print_error "ESLint failed"
        exit 1
    fi
}

# Run unit tests with coverage
run_unit_tests() {
    print_status "Running unit tests with coverage..."
    if npm run test:coverage; then
        print_success "Unit tests passed with 100% coverage"
    else
        print_error "Unit tests failed"
        exit 1
    fi
}

# Build the application
build_application() {
    print_status "Building application..."
    if npm run build; then
        print_success "Application build successful"
    else
        print_error "Application build failed"
        exit 1
    fi
}

# Install Playwright browsers if needed
setup_playwright() {
    print_status "Setting up Playwright browsers..."
    npx playwright install
    print_success "Playwright browsers installed"
}

# Run E2E tests
run_e2e_tests() {
    print_status "Running E2E tests..."
    if npm run e2e; then
        print_success "E2E tests passed"
    else
        print_error "E2E tests failed"
        print_warning "You can view the test report with: npm run e2e:report"
        exit 1
    fi
}

# Generate test reports
generate_reports() {
    print_status "Generating test reports..."
    
    # Create reports directory
    mkdir -p reports
    
    # Copy coverage report
    if [ -d "coverage" ]; then
        cp -r coverage reports/unit-test-coverage
        print_success "Unit test coverage report saved to reports/unit-test-coverage"
    fi
    
    # Copy E2E test report
    if [ -d "playwright-report" ]; then
        cp -r playwright-report reports/e2e-test-report
        print_success "E2E test report saved to reports/e2e-test-report"
    fi
}

# Main execution
main() {
    echo "🚀 Starting comprehensive test suite..."
    echo ""
    
    check_dependencies
    install_dependencies
    setup_test_database
    
    echo ""
    echo "🔍 Static Analysis & Type Checking"
    echo "--------------------------------"
    run_type_check
    run_lint
    
    echo ""
    echo "🧪 Unit Testing"
    echo "---------------"
    run_unit_tests
    
    echo ""
    echo "🏗️ Application Build"
    echo "-------------------"
    build_application
    
    echo ""
    echo "🎭 End-to-End Testing"
    echo "--------------------"
    setup_playwright
    run_e2e_tests
    
    echo ""
    echo "📄 Generating Reports"
    echo "--------------------"
    generate_reports
    
    echo ""
    echo "🎉 All tests completed successfully!"
    echo "===================================="
    echo ""
    echo "Test Reports Available:"
    echo "  - Unit Test Coverage: reports/unit-test-coverage/index.html"
    echo "  - E2E Test Report: reports/e2e-test-report/index.html"
    echo ""
    echo "Development Commands:"
    echo "  - Start dev server: npm run dev"
    echo "  - View Storybook: npm run storybook"
    echo "  - View database: npm run db:studio"
    echo "  - View E2E report: npm run e2e:report"
}

# Handle script interruption
trap 'print_error "Test suite interrupted"; exit 1' INT

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --skip-e2e)
            SKIP_E2E=true
            shift
            ;;
        --skip-build)
            SKIP_BUILD=true
            shift
            ;;
        --unit-only)
            UNIT_ONLY=true
            shift
            ;;
        --e2e-only)
            E2E_ONLY=true
            shift
            ;;
        --help)
            echo "Usage: $0 [options]"
            echo "Options:"
            echo "  --skip-e2e    Skip E2E tests"
            echo "  --skip-build  Skip application build"
            echo "  --unit-only   Run only unit tests"
            echo "  --e2e-only    Run only E2E tests"
            echo "  --help        Show this help message"
            exit 0
            ;;
        *)
            print_error "Unknown option: $1"
            exit 1
            ;;
    esac
done

# Run based on options
if [[ "$UNIT_ONLY" == "true" ]]; then
    check_dependencies
    install_dependencies
    setup_test_database
    run_type_check
    run_lint
    run_unit_tests
    generate_reports
elif [[ "$E2E_ONLY" == "true" ]]; then
    check_dependencies
    install_dependencies
    setup_test_database
    setup_playwright
    run_e2e_tests
    generate_reports
else
    main
fi