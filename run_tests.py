"""
TradeMate Test Runner - 100% Coverage Validator
Execute all tests and ensure 100% coverage compliance
"""

import sys
import subprocess
import os
from pathlib import Path
import time


def run_test_suite():
    """Run complete test suite with coverage validation"""
    
    print("🚀 TradeMate 100% Test Coverage Validation")
    print("=" * 60)
    
    # Set test environment
    os.environ["ENVIRONMENT"] = "test"
    
    # Load test environment variables
    test_env_file = Path(__file__).parent / ".env.test"
    if test_env_file.exists():
        with open(test_env_file) as f:
            for line in f:
                if line.strip() and not line.startswith("#"):
                    key, value = line.strip().split("=", 1)
                    os.environ[key] = value
    
    project_root = Path(__file__).parent
    
    # Test suites to run
    test_suites = [
        {
            "name": "Unified Billing System Tests",
            "path": "tests/billing/test_unified_billing_system.py",
            "module": "app.billing.unified_billing_system"
        },
        {
            "name": "Luxury Billing Tests", 
            "path": "tests/billing/test_luxury_billing.py",
            "module": "app.black.luxury_billing"
        },
        {
            "name": "Admin Dashboard Tests",
            "path": "tests/admin/test_admin_dashboard.py",
            "module": "app.admin.dashboard"
        },
        {
            "name": "Billing Integration Tests",
            "path": "tests/billing/test_billing_integration.py",
            "module": "integration"
        }
    ]
    
    total_passed = 0
    total_failed = 0
    
    print(f"🧪 Running {len(test_suites)} test suites...\n")
    
    for i, suite in enumerate(test_suites, 1):
        print(f"[{i}/{len(test_suites)}] {suite['name']}")
        print("-" * 40)
        
        start_time = time.time()
        
        # Build pytest command
        cmd = [
            sys.executable, "-m", "pytest",
            str(project_root / suite["path"]),
            "-v",
            "--tb=short",
            f"--cov={suite['module']}" if suite['module'] != 'integration' else "",
            "--cov-report=term-missing",
            "--cov-fail-under=100" if suite['module'] != 'integration' else ""
        ]
        
        # Filter out empty strings
        cmd = [c for c in cmd if c]
        
        try:
            result = subprocess.run(
                cmd,
                cwd=project_root,
                text=True,
                timeout=300  # 5 minute timeout
            )
            
            execution_time = time.time() - start_time
            
            if result.returncode == 0:
                print(f"✅ PASSED in {execution_time:.2f}s")
                total_passed += 1
            else:
                print(f"❌ FAILED in {execution_time:.2f}s")
                total_failed += 1
                
        except subprocess.TimeoutExpired:
            print(f"⏰ TIMEOUT after 5 minutes")
            total_failed += 1
            
        except Exception as e:
            print(f"❌ ERROR: {e}")
            total_failed += 1
        
        print()
    
    # Summary
    print("=" * 60)
    print("📊 TEST EXECUTION SUMMARY")
    print("=" * 60)
    print(f"Total Suites: {len(test_suites)}")
    print(f"Passed: {total_passed}")
    print(f"Failed: {total_failed}")
    print(f"Success Rate: {(total_passed / len(test_suites) * 100):.1f}%")
    
    if total_failed == 0:
        print("\n🎉 ALL TESTS PASSED! 100% Coverage Achieved!")
        
        # Run coverage report generator
        print("\n📊 Generating comprehensive coverage report...")
        try:
            coverage_cmd = [sys.executable, "tests/test_coverage_report.py"]
            subprocess.run(coverage_cmd, cwd=project_root)
        except Exception as e:
            print(f"❌ Coverage report generation failed: {e}")
        
        return True
    else:
        print(f"\n⚠️  {total_failed} test suite(s) failed. Please fix before proceeding.")
        return False


def install_dependencies():
    """Install required test dependencies"""
    
    print("📦 Installing test dependencies...")
    
    dependencies = [
        "pytest>=7.0.0",
        "pytest-asyncio>=0.21.0", 
        "pytest-cov>=4.0.0",
        "coverage>=7.0.0",
        "httpx>=0.24.0",  # For FastAPI testing
        "fastapi[all]>=0.100.0"
    ]
    
    for dep in dependencies:
        try:
            subprocess.run([
                sys.executable, "-m", "pip", "install", dep
            ], check=True, capture_output=True)
            print(f"✅ Installed {dep}")
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to install {dep}: {e}")
            return False
    
    return True


def validate_project_structure():
    """Validate project structure for testing"""
    
    print("🔍 Validating project structure...")
    
    project_root = Path(__file__).parent
    
    required_paths = [
        "app/billing/unified_billing_system.py",
        "app/black/luxury_billing.py",
        "app/admin/dashboard.py",
        "tests/billing/test_unified_billing_system.py",
        "tests/billing/test_luxury_billing.py",
        "tests/admin/test_admin_dashboard.py",
        "tests/billing/test_billing_integration.py"
    ]
    
    missing_files = []
    
    for path in required_paths:
        full_path = project_root / path
        if not full_path.exists():
            missing_files.append(path)
        else:
            print(f"✅ {path}")
    
    if missing_files:
        print(f"\n❌ Missing required files:")
        for file in missing_files:
            print(f"   - {file}")
        return False
    
    print("✅ Project structure validated")
    return True


def main():
    """Main test execution function"""
    
    print("🧪 TradeMate Test Suite Runner")
    print("🎯 Target: 100% Test Coverage")
    print("=" * 60)
    
    # Step 1: Validate project structure
    if not validate_project_structure():
        print("❌ Project structure validation failed")
        return 1
    
    # Step 2: Install dependencies
    if not install_dependencies():
        print("❌ Dependency installation failed")
        return 1
    
    # Step 3: Run test suite
    if not run_test_suite():
        print("❌ Test suite execution failed")
        return 1
    
    print("\n🎉 SUCCESS: All tests passed with 100% coverage!")
    print("🚀 Ready for Beta Launch!")
    
    return 0


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)