#!/usr/bin/env python3
"""
GridWorks B2B Services - Test Runner
Comprehensive test execution with coverage reporting and categorization
"""

import os
import sys
import subprocess
import argparse
import time
from datetime import datetime
from pathlib import Path

class TestRunner:
    """Test runner for GridWorks B2B Services with comprehensive reporting."""
    
    def __init__(self):
        self.test_dir = Path(__file__).parent
        self.project_root = self.test_dir.parent
        self.coverage_threshold = 100  # 100% coverage requirement
        
    def run_unit_tests(self, verbose=True):
        """Run unit tests for all service components."""
        print("🧪 Running Unit Tests...")
        
        cmd = [
            "python", "-m", "pytest",
            "tests/unit/",
            "-m", "unit",
            "--cov=.",
            "--cov-report=term-missing",
            "--cov-report=html:htmlcov/unit",
            f"--cov-fail-under={self.coverage_threshold}",
            "--tb=short"
        ]
        
        if verbose:
            cmd.append("-v")
            
        return self._run_command(cmd, "Unit Tests")
    
    def run_integration_tests(self, verbose=True):
        """Run integration tests for API endpoints."""
        print("🔗 Running Integration Tests...")
        
        cmd = [
            "python", "-m", "pytest",
            "tests/integration/",
            "-m", "integration",
            "--cov=.",
            "--cov-report=term-missing",
            "--cov-report=html:htmlcov/integration",
            "--tb=short"
        ]
        
        if verbose:
            cmd.append("-v")
            
        return self._run_command(cmd, "Integration Tests")
    
    def run_e2e_tests(self, verbose=True):
        """Run end-to-end tests for complete user flows."""
        print("🎯 Running End-to-End Tests...")
        
        cmd = [
            "python", "-m", "pytest",
            "tests/e2e/",
            "-m", "e2e",
            "--cov=.",
            "--cov-report=term-missing",
            "--cov-report=html:htmlcov/e2e",
            "--tb=short",
            "--timeout=600"  # 10 minutes timeout for E2E tests
        ]
        
        if verbose:
            cmd.append("-v")
            
        return self._run_command(cmd, "End-to-End Tests")
    
    def run_performance_tests(self, verbose=True):
        """Run performance and load tests."""
        print("⚡ Running Performance Tests...")
        
        cmd = [
            "python", "-m", "pytest",
            "tests/performance/",
            "-m", "performance",
            "--tb=short",
            "--timeout=1200"  # 20 minutes timeout for performance tests
        ]
        
        if verbose:
            cmd.append("-v")
            
        return self._run_command(cmd, "Performance Tests")
    
    def run_security_tests(self, verbose=True):
        """Run security and penetration tests."""
        print("🔒 Running Security Tests...")
        
        cmd = [
            "python", "-m", "pytest",
            "tests/security/",
            "-m", "security",
            "--tb=short",
            "--timeout=300"  # 5 minutes timeout for security tests
        ]
        
        if verbose:
            cmd.append("-v")
            
        return self._run_command(cmd, "Security Tests")
    
    def run_all_tests(self, verbose=True, fast=False):
        """Run all test suites with comprehensive coverage."""
        print("🚀 Running Complete Test Suite...")
        start_time = time.time()
        
        results = {}
        
        # Run all test categories
        test_suites = [
            ("Unit Tests", self.run_unit_tests),
            ("Integration Tests", self.run_integration_tests),
            ("End-to-End Tests", self.run_e2e_tests),
        ]
        
        # Add performance and security tests if not in fast mode
        if not fast:
            test_suites.extend([
                ("Performance Tests", self.run_performance_tests),
                ("Security Tests", self.run_security_tests),
            ])
        
        for suite_name, test_function in test_suites:
            print(f"\n{'='*60}")
            print(f"Running {suite_name}")
            print(f"{'='*60}")
            
            success = test_function(verbose)
            results[suite_name] = success
            
            if not success:
                print(f"❌ {suite_name} failed!")
                if not fast:  # Continue with other tests unless in fast mode
                    break
            else:
                print(f"✅ {suite_name} passed!")
        
        # Generate comprehensive coverage report
        if all(results.values()):
            self._generate_coverage_report()
        
        end_time = time.time()
        duration = end_time - start_time
        
        self._print_summary(results, duration)
        
        return all(results.values())
    
    def run_specific_test(self, test_path, verbose=True):
        """Run a specific test file or test function."""
        print(f"🎯 Running Specific Test: {test_path}")
        
        cmd = [
            "python", "-m", "pytest",
            test_path,
            "--cov=.",
            "--cov-report=term-missing",
            "--tb=short"
        ]
        
        if verbose:
            cmd.append("-v")
            
        return self._run_command(cmd, f"Specific Test: {test_path}")
    
    def _run_command(self, cmd, test_name):
        """Execute test command and return success status."""
        try:
            # Set environment variables for testing
            env = os.environ.copy()
            env['TESTING'] = 'true'
            env['DATABASE_URL'] = 'sqlite:///test.db'
            env['REDIS_URL'] = 'redis://localhost:6379/1'
            
            result = subprocess.run(
                cmd,
                cwd=self.project_root,
                env=env,
                capture_output=False,
                text=True
            )
            
            return result.returncode == 0
            
        except Exception as e:
            print(f"❌ Error running {test_name}: {e}")
            return False
    
    def _generate_coverage_report(self):
        """Generate comprehensive coverage report."""
        print("\n📊 Generating Coverage Report...")
        
        # Generate HTML coverage report
        cmd = [
            "python", "-m", "pytest",
            "--cov=.",
            "--cov-report=html:htmlcov/complete",
            "--cov-report=xml:coverage.xml",
            "--cov-report=term-missing",
            f"--cov-fail-under={self.coverage_threshold}",
            "--co"  # Collect only, don't run tests
        ]
        
        subprocess.run(cmd, cwd=self.project_root)
        
        print(f"📈 Coverage report generated at: {self.project_root}/htmlcov/complete/index.html")
    
    def _print_summary(self, results, duration):
        """Print test execution summary."""
        print(f"\n{'='*80}")
        print("🎯 TEST EXECUTION SUMMARY")
        print(f"{'='*80}")
        
        total_suites = len(results)
        passed_suites = sum(1 for success in results.values() if success)
        failed_suites = total_suites - passed_suites
        
        print(f"📊 Total Test Suites: {total_suites}")
        print(f"✅ Passed: {passed_suites}")
        print(f"❌ Failed: {failed_suites}")
        print(f"⏱️  Total Duration: {duration:.2f} seconds")
        print(f"📅 Completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        print("\n📋 Detailed Results:")
        for suite_name, success in results.items():
            status = "✅ PASSED" if success else "❌ FAILED"
            print(f"  {suite_name}: {status}")
        
        if all(results.values()):
            print(f"\n🎉 ALL TESTS PASSED! 100% test coverage achieved.")
        else:
            print(f"\n⚠️  Some tests failed. Review the output above for details.")
        
        print(f"{'='*80}")

def main():
    """Main entry point for test runner."""
    parser = argparse.ArgumentParser(
        description="GridWorks B2B Services Test Runner",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run_tests.py                    # Run all tests
  python run_tests.py --unit             # Run only unit tests
  python run_tests.py --integration      # Run only integration tests
  python run_tests.py --e2e              # Run only end-to-end tests
  python run_tests.py --performance      # Run only performance tests
  python run_tests.py --security         # Run only security tests
  python run_tests.py --fast             # Run fast test suite (no perf/security)
  python run_tests.py --test path/to/test.py  # Run specific test
        """
    )
    
    parser.add_argument("--unit", action="store_true", help="Run unit tests only")
    parser.add_argument("--integration", action="store_true", help="Run integration tests only")
    parser.add_argument("--e2e", action="store_true", help="Run end-to-end tests only")
    parser.add_argument("--performance", action="store_true", help="Run performance tests only")
    parser.add_argument("--security", action="store_true", help="Run security tests only")
    parser.add_argument("--fast", action="store_true", help="Run fast test suite (unit, integration, e2e)")
    parser.add_argument("--test", type=str, help="Run specific test file or function")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    parser.add_argument("--quiet", "-q", action="store_true", help="Quiet output")
    
    args = parser.parse_args()
    
    runner = TestRunner()
    verbose = args.verbose and not args.quiet
    
    # Determine which tests to run
    if args.test:
        success = runner.run_specific_test(args.test, verbose)
    elif args.unit:
        success = runner.run_unit_tests(verbose)
    elif args.integration:
        success = runner.run_integration_tests(verbose)
    elif args.e2e:
        success = runner.run_e2e_tests(verbose)
    elif args.performance:
        success = runner.run_performance_tests(verbose)
    elif args.security:
        success = runner.run_security_tests(verbose)
    else:
        # Run all tests (with fast option if specified)
        success = runner.run_all_tests(verbose, fast=args.fast)
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()