"""
100% Test Coverage Report Generator
Validates and reports test coverage across all TradeMate components
"""

import subprocess
import sys
import os
import json
from pathlib import Path
from typing import Dict, List, Tuple
import coverage
from datetime import datetime


class TestCoverageReporter:
    """Generate comprehensive test coverage reports"""
    
    def __init__(self, project_root: str = "/Users/keerthirao/Documents/GitHub/projects/TradeMate"):
        self.project_root = Path(project_root)
        self.coverage_target = 100.0  # 100% coverage target
        self.test_modules = [
            "app.billing.unified_billing_system",
            "app.black.luxury_billing", 
            "app.admin.dashboard",
            "app.billing.subscription_manager",
            "app.ai_support.support_engine"
        ]
    
    def run_coverage_analysis(self) -> Dict[str, any]:
        """Run comprehensive coverage analysis"""
        
        print("🧪 TradeMate Test Coverage Analysis")
        print("=" * 60)
        
        results = {
            "timestamp": datetime.now().isoformat(),
            "target_coverage": self.coverage_target,
            "modules": {},
            "overall": {},
            "compliance": {}
        }
        
        # Initialize coverage
        cov = coverage.Coverage(
            source=[str(self.project_root / "app")],
            omit=[
                "*/tests/*",
                "*/venv/*",
                "*/__pycache__/*"
            ]
        )
        
        try:
            # Start coverage measurement
            cov.start()
            
            # Run all test suites
            test_results = self._run_all_tests()
            
            # Stop coverage measurement
            cov.stop()
            cov.save()
            
            # Generate coverage report
            coverage_report = self._generate_coverage_report(cov)
            
            results["modules"] = coverage_report["modules"]
            results["overall"] = coverage_report["overall"]
            results["test_results"] = test_results
            results["compliance"] = self._check_compliance(coverage_report)
            
            # Generate detailed reports
            self._generate_html_report(cov)
            self._generate_badge_report(results)
            
            return results
            
        except Exception as e:
            print(f"❌ Coverage analysis failed: {e}")
            return {"error": str(e)}
    
    def _run_all_tests(self) -> Dict[str, any]:
        """Run all test suites and collect results"""
        
        test_suites = [
            {
                "name": "Unified Billing System",
                "path": "tests/billing/test_unified_billing_system.py",
                "module": "app.billing.unified_billing_system"
            },
            {
                "name": "Luxury Billing",
                "path": "tests/billing/test_luxury_billing.py", 
                "module": "app.black.luxury_billing"
            },
            {
                "name": "Admin Dashboard",
                "path": "tests/admin/test_admin_dashboard.py",
                "module": "app.admin.dashboard"
            },
            {
                "name": "Billing Integration",
                "path": "tests/billing/test_billing_integration.py",
                "module": "integration"
            }
        ]
        
        results = {
            "total_suites": len(test_suites),
            "passed": 0,
            "failed": 0,
            "suites": {}
        }
        
        for suite in test_suites:
            print(f"\n🧪 Running {suite['name']} tests...")
            
            try:
                # Run pytest for this suite
                cmd = [
                    sys.executable, "-m", "pytest",
                    str(self.project_root / suite["path"]),
                    "-v",
                    "--tb=short",
                    f"--cov={suite['module']}" if suite['module'] != 'integration' else "",
                    "--no-cov-report"  # We'll generate our own report
                ]
                
                # Filter out empty strings
                cmd = [c for c in cmd if c]
                
                result = subprocess.run(
                    cmd,
                    cwd=self.project_root,
                    capture_output=True,
                    text=True,
                    timeout=300  # 5 minute timeout
                )
                
                suite_result = {
                    "passed": result.returncode == 0,
                    "output": result.stdout,
                    "errors": result.stderr,
                    "return_code": result.returncode
                }
                
                if result.returncode == 0:
                    results["passed"] += 1
                    print(f"✅ {suite['name']} tests passed")
                else:
                    results["failed"] += 1
                    print(f"❌ {suite['name']} tests failed")
                    print(f"Error: {result.stderr}")
                
                results["suites"][suite["name"]] = suite_result
                
            except subprocess.TimeoutExpired:
                print(f"⏰ {suite['name']} tests timed out")
                results["failed"] += 1
                results["suites"][suite["name"]] = {
                    "passed": False,
                    "error": "Test execution timed out"
                }
            
            except Exception as e:
                print(f"❌ Error running {suite['name']}: {e}")
                results["failed"] += 1
                results["suites"][suite["name"]] = {
                    "passed": False,
                    "error": str(e)
                }
        
        return results
    
    def _generate_coverage_report(self, cov: coverage.Coverage) -> Dict[str, any]:
        """Generate detailed coverage report"""
        
        report = {
            "modules": {},
            "overall": {}
        }
        
        try:
            # Get coverage data
            data = cov.get_data()
            
            # Calculate overall statistics
            total_lines = 0
            covered_lines = 0
            missing_lines = []
            
            # Analyze each measured file
            for filename in data.measured_files():
                if self._should_include_file(filename):
                    analysis = cov._analyze(filename)
                    
                    # Extract module name
                    module_name = self._get_module_name(filename)
                    
                    # Calculate coverage percentage
                    executable_lines = len(analysis.statements)
                    covered = len(analysis.statements) - len(analysis.missing)
                    percentage = (covered / executable_lines * 100) if executable_lines > 0 else 100
                    
                    report["modules"][module_name] = {
                        "filename": filename,
                        "executable_lines": executable_lines,
                        "covered_lines": covered,
                        "missing_lines": list(analysis.missing),
                        "coverage_percentage": round(percentage, 2),
                        "excluded_lines": list(analysis.excluded),
                        "branches": getattr(analysis, 'branch_lines', [])
                    }
                    
                    total_lines += executable_lines
                    covered_lines += covered
                    missing_lines.extend(analysis.missing)
            
            # Calculate overall coverage
            overall_percentage = (covered_lines / total_lines * 100) if total_lines > 0 else 100
            
            report["overall"] = {
                "total_lines": total_lines,
                "covered_lines": covered_lines,
                "missing_lines": len(missing_lines),
                "coverage_percentage": round(overall_percentage, 2),
                "target_met": overall_percentage >= self.coverage_target
            }
            
        except Exception as e:
            print(f"❌ Error generating coverage report: {e}")
            report = {"error": str(e)}
        
        return report
    
    def _should_include_file(self, filename: str) -> bool:
        """Check if file should be included in coverage analysis"""
        
        exclude_patterns = [
            "/tests/",
            "__pycache__",
            "/venv/",
            ".pyc",
            "/migrations/",
            "/static/",
            "/templates/"
        ]
        
        for pattern in exclude_patterns:
            if pattern in filename:
                return False
        
        return filename.endswith(".py")
    
    def _get_module_name(self, filename: str) -> str:
        """Extract module name from filename"""
        
        # Convert file path to module name
        relative_path = Path(filename).relative_to(self.project_root)
        module_parts = relative_path.parts[:-1]  # Exclude filename
        module_parts += (relative_path.stem,)  # Add filename without extension
        
        return ".".join(module_parts)
    
    def _check_compliance(self, coverage_report: Dict) -> Dict[str, any]:
        """Check coverage compliance against targets"""
        
        compliance = {
            "overall_compliant": False,
            "module_compliance": {},
            "failing_modules": [],
            "summary": {}
        }
        
        try:
            overall = coverage_report.get("overall", {})
            overall_coverage = overall.get("coverage_percentage", 0)
            
            # Check overall compliance
            compliance["overall_compliant"] = overall_coverage >= self.coverage_target
            
            # Check module compliance
            failing_modules = []
            
            for module, data in coverage_report.get("modules", {}).items():
                module_coverage = data.get("coverage_percentage", 0)
                is_compliant = module_coverage >= self.coverage_target
                
                compliance["module_compliance"][module] = {
                    "coverage": module_coverage,
                    "compliant": is_compliant,
                    "missing_lines": len(data.get("missing_lines", []))
                }
                
                if not is_compliant:
                    failing_modules.append({
                        "module": module,
                        "coverage": module_coverage,
                        "gap": self.coverage_target - module_coverage
                    })
            
            compliance["failing_modules"] = failing_modules
            
            # Generate summary
            total_modules = len(coverage_report.get("modules", {}))
            compliant_modules = sum(1 for m in compliance["module_compliance"].values() if m["compliant"])
            
            compliance["summary"] = {
                "total_modules": total_modules,
                "compliant_modules": compliant_modules,
                "compliance_rate": (compliant_modules / total_modules * 100) if total_modules > 0 else 100,
                "overall_coverage": overall_coverage,
                "target_coverage": self.coverage_target
            }
            
        except Exception as e:
            compliance["error"] = str(e)
        
        return compliance
    
    def _generate_html_report(self, cov: coverage.Coverage):
        """Generate HTML coverage report"""
        
        try:
            report_dir = self.project_root / "coverage_html"
            cov.html_report(directory=str(report_dir))
            print(f"📊 HTML coverage report generated: {report_dir}/index.html")
            
        except Exception as e:
            print(f"❌ Error generating HTML report: {e}")
    
    def _generate_badge_report(self, results: Dict):
        """Generate coverage badge and summary report"""
        
        try:
            overall_coverage = results.get("overall", {}).get("coverage_percentage", 0)
            
            # Determine badge color
            if overall_coverage >= 95:
                badge_color = "brightgreen"
            elif overall_coverage >= 90:
                badge_color = "green"
            elif overall_coverage >= 80:
                badge_color = "yellowgreen"
            elif overall_coverage >= 70:
                badge_color = "yellow"
            elif overall_coverage >= 60:
                badge_color = "orange"
            else:
                badge_color = "red"
            
            # Generate badge URL
            badge_url = f"https://img.shields.io/badge/coverage-{overall_coverage:.1f}%25-{badge_color}"
            
            # Generate summary report
            summary_report = f"""# TradeMate Test Coverage Report
Generated: {results['timestamp']}

## Overall Coverage: {overall_coverage:.1f}%
![Coverage Badge]({badge_url})

## Compliance Status
- **Target Coverage**: {self.coverage_target}%
- **Overall Compliant**: {'✅ YES' if results.get('compliance', {}).get('overall_compliant') else '❌ NO'}
- **Modules Tested**: {len(results.get('modules', {}))}

## Module Coverage
"""
            
            # Add module details
            for module, data in results.get("modules", {}).items():
                coverage_pct = data.get("coverage_percentage", 0)
                status = "✅" if coverage_pct >= self.coverage_target else "❌"
                summary_report += f"- **{module}**: {coverage_pct:.1f}% {status}\n"
            
            # Add test results
            test_results = results.get("test_results", {})
            summary_report += f"""
## Test Execution
- **Total Test Suites**: {test_results.get('total_suites', 0)}
- **Passed**: {test_results.get('passed', 0)}
- **Failed**: {test_results.get('failed', 0)}

## Detailed Reports
- [HTML Coverage Report](coverage_html/index.html)
- [Full JSON Report](coverage_report.json)

---
*Generated by TradeMate Test Coverage Reporter*
"""
            
            # Save reports
            with open(self.project_root / "COVERAGE_REPORT.md", "w") as f:
                f.write(summary_report)
            
            with open(self.project_root / "coverage_report.json", "w") as f:
                json.dump(results, f, indent=2)
            
            print(f"📋 Coverage summary: COVERAGE_REPORT.md")
            print(f"📊 Detailed JSON report: coverage_report.json")
            
        except Exception as e:
            print(f"❌ Error generating badge report: {e}")
    
    def print_summary(self, results: Dict):
        """Print coverage summary to console"""
        
        print("\n" + "=" * 60)
        print("📊 TRADEMATE TEST COVERAGE SUMMARY")
        print("=" * 60)
        
        overall = results.get("overall", {})
        compliance = results.get("compliance", {})
        
        print(f"🎯 Overall Coverage: {overall.get('coverage_percentage', 0):.1f}%")
        print(f"🎯 Target Coverage: {self.coverage_target}%")
        print(f"✅ Target Met: {'YES' if compliance.get('overall_compliant') else 'NO'}")
        
        print(f"\n📈 Statistics:")
        print(f"  Total Lines: {overall.get('total_lines', 0):,}")
        print(f"  Covered Lines: {overall.get('covered_lines', 0):,}")
        print(f"  Missing Lines: {overall.get('missing_lines', 0):,}")
        
        # Module breakdown
        print(f"\n📋 Module Coverage:")
        for module, data in results.get("modules", {}).items():
            coverage_pct = data.get("coverage_percentage", 0)
            status = "✅" if coverage_pct >= self.coverage_target else "❌"
            print(f"  {status} {module}: {coverage_pct:.1f}%")
        
        # Test results
        test_results = results.get("test_results", {})
        print(f"\n🧪 Test Execution:")
        print(f"  Total Suites: {test_results.get('total_suites', 0)}")
        print(f"  Passed: {test_results.get('passed', 0)}")
        print(f"  Failed: {test_results.get('failed', 0)}")
        
        # Compliance summary
        summary = compliance.get("summary", {})
        print(f"\n🏆 Compliance Summary:")
        print(f"  Module Compliance Rate: {summary.get('compliance_rate', 0):.1f}%")
        print(f"  Compliant Modules: {summary.get('compliant_modules', 0)}/{summary.get('total_modules', 0)}")
        
        if compliance.get("failing_modules"):
            print(f"\n⚠️  Modules needing attention:")
            for module in compliance["failing_modules"]:
                print(f"    {module['module']}: {module['coverage']:.1f}% (gap: {module['gap']:.1f}%)")
        
        print("\n" + "=" * 60)


def main():
    """Run coverage analysis and generate reports"""
    
    reporter = TestCoverageReporter()
    
    try:
        # Run comprehensive coverage analysis
        results = reporter.run_coverage_analysis()
        
        if "error" in results:
            print(f"❌ Coverage analysis failed: {results['error']}")
            return 1
        
        # Print summary
        reporter.print_summary(results)
        
        # Check if we met our 100% target
        if results.get("compliance", {}).get("overall_compliant"):
            print("🎉 CONGRATULATIONS! 100% test coverage achieved!")
            return 0
        else:
            overall_coverage = results.get("overall", {}).get("coverage_percentage", 0)
            print(f"⚠️  Coverage target not met. Current: {overall_coverage:.1f}%, Target: 100%")
            return 1
            
    except Exception as e:
        print(f"❌ Coverage analysis failed: {e}")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)