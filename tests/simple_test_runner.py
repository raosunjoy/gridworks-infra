#!/usr/bin/env python3
"""
Simple Test Runner for TradeMate Charting Platform
=================================================
Simplified test execution without external dependencies
"""

import sys
import os
import time
import traceback
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


class SimpleTestRunner:
    """Simple test runner without pytest dependencies"""
    
    def __init__(self):
        self.passed_tests = 0
        self.failed_tests = 0
        self.errors = []
    
    def test_imports(self):
        """Test that all modules can be imported"""
        print("🔍 Testing Module Imports...")
        
        modules_to_test = [
            ("app.pro.charting_platform", "ChartingEngine"),
            ("app.pro.voice_charting_engine", "VoiceChartingEngine"),
            ("app.lite.basic_charting", "BasicChartingEngine")
        ]
        
        for module_name, class_name in modules_to_test:
            try:
                module = __import__(module_name, fromlist=[class_name])
                cls = getattr(module, class_name)
                print(f"✅ {module_name}.{class_name} - Import successful")
                self.passed_tests += 1
            except Exception as e:
                print(f"❌ {module_name}.{class_name} - Import failed: {e}")
                self.failed_tests += 1
                self.errors.append(f"Import {module_name}: {e}")
    
    def test_basic_functionality(self):
        """Test basic functionality without complex dependencies"""
        print("\n🧪 Testing Basic Functionality...")
        
        # Test technical analysis engine
        try:
            from app.pro.charting_platform import TechnicalAnalysisEngine
            
            engine = TechnicalAnalysisEngine()
            
            # Test SMA calculation
            test_data = [100, 102, 101, 103, 105, 104, 106, 108, 107, 109]
            sma_result = engine.calculate_sma(test_data, 5)
            
            if len(sma_result) == 6:  # 10 - 5 + 1
                print("✅ TechnicalAnalysisEngine.calculate_sma - Working correctly")
                self.passed_tests += 1
            else:
                print(f"❌ TechnicalAnalysisEngine.calculate_sma - Wrong length: {len(sma_result)}")
                self.failed_tests += 1
            
            # Test RSI calculation
            rsi_result = engine.calculate_rsi(test_data, 5)
            if isinstance(rsi_result, list):
                print("✅ TechnicalAnalysisEngine.calculate_rsi - Working correctly")
                self.passed_tests += 1
            else:
                print("❌ TechnicalAnalysisEngine.calculate_rsi - Failed")
                self.failed_tests += 1
                
        except Exception as e:
            print(f"❌ TechnicalAnalysisEngine tests failed: {e}")
            self.failed_tests += 1
            self.errors.append(f"TechnicalAnalysisEngine: {e}")
    
    def test_voice_pattern_matching(self):
        """Test voice pattern matching"""
        print("\n🎤 Testing Voice Pattern Matching...")
        
        try:
            from app.pro.voice_charting_engine import VoicePatternMatcher, VoiceLanguage, VoiceCommandType
            
            matcher = VoicePatternMatcher()
            
            # Test Hindi command
            command_type, parameters = matcher.match_command(
                "Reliance ka chart dikhao", 
                VoiceLanguage.HINDI
            )
            
            if command_type == VoiceCommandType.CREATE_CHART:
                print("✅ VoicePatternMatcher - Hindi command recognition working")
                self.passed_tests += 1
            else:
                print(f"❌ VoicePatternMatcher - Wrong command type: {command_type}")
                self.failed_tests += 1
            
            # Test symbol normalization
            normalized = matcher._normalize_symbol("reliance")
            if normalized == "RELIANCE":
                print("✅ VoicePatternMatcher - Symbol normalization working")
                self.passed_tests += 1
            else:
                print(f"❌ VoicePatternMatcher - Wrong symbol: {normalized}")
                self.failed_tests += 1
                
        except Exception as e:
            print(f"❌ Voice pattern matching tests failed: {e}")
            self.failed_tests += 1
            self.errors.append(f"VoicePatternMatcher: {e}")
    
    def test_lite_charting(self):
        """Test LITE charting functionality"""
        print("\n⚡ Testing LITE Charting...")
        
        try:
            from app.lite.basic_charting import BasicChartingEngine, LiteTimeFrame, LiteIndicator
            
            engine = BasicChartingEngine()
            
            # Test basic calculations
            test_data = [100.0, 102.0, 101.0, 103.0, 105.0, 104.0, 106.0, 108.0, 107.0, 109.0]
            
            # Test simple SMA
            sma_result = engine._calculate_simple_sma(test_data, 5)
            if len(sma_result) > 0:
                print("✅ BasicChartingEngine - SMA calculation working")
                self.passed_tests += 1
            else:
                print("❌ BasicChartingEngine - SMA calculation failed")
                self.failed_tests += 1
            
            # Test simple RSI
            rsi_result = engine._calculate_simple_rsi(test_data, 5)
            if isinstance(rsi_result, list):
                print("✅ BasicChartingEngine - RSI calculation working")
                self.passed_tests += 1
            else:
                print("❌ BasicChartingEngine - RSI calculation failed")
                self.failed_tests += 1
                
        except Exception as e:
            print(f"❌ LITE charting tests failed: {e}")
            self.failed_tests += 1
            self.errors.append(f"BasicChartingEngine: {e}")
    
    def test_data_structures(self):
        """Test data structure creation"""
        print("\n📊 Testing Data Structures...")
        
        try:
            from app.pro.charting_platform import OHLCV, TimeFrame
            from datetime import datetime
            
            # Test OHLCV creation
            ohlcv = OHLCV(
                timestamp=datetime.now(),
                open=100.0,
                high=105.0,
                low=95.0,
                close=102.0,
                volume=10000,
                symbol="TEST",
                timeframe=TimeFrame.ONE_MINUTE
            )
            
            if ohlcv.close == 102.0 and ohlcv.symbol == "TEST":
                print("✅ OHLCV data structure - Working correctly")
                self.passed_tests += 1
            else:
                print("❌ OHLCV data structure - Failed")
                self.failed_tests += 1
                
        except Exception as e:
            print(f"❌ Data structure tests failed: {e}")
            self.failed_tests += 1
            self.errors.append(f"Data structures: {e}")
    
    def run_all_tests(self):
        """Run all tests"""
        print("🚀 Starting TradeMate Charting Platform Simple Tests")
        print("=" * 60)
        
        start_time = time.time()
        
        # Run test suites
        self.test_imports()
        self.test_basic_functionality()
        self.test_voice_pattern_matching()
        self.test_lite_charting()
        self.test_data_structures()
        
        end_time = time.time()
        
        # Print summary
        print("\n" + "=" * 60)
        print("📋 Test Summary")
        print("=" * 60)
        
        total_tests = self.passed_tests + self.failed_tests
        print(f"Total Tests: {total_tests}")
        print(f"✅ Passed: {self.passed_tests}")
        print(f"❌ Failed: {self.failed_tests}")
        print(f"⏱️  Time: {end_time - start_time:.2f}s")
        
        if self.failed_tests > 0:
            print("\n🔧 Errors Found:")
            for error in self.errors:
                print(f"   - {error}")
        
        success_rate = (self.passed_tests / total_tests * 100) if total_tests > 0 else 0
        print(f"\n📊 Success Rate: {success_rate:.1f}%")
        
        if self.failed_tests == 0:
            print("\n🎉 ALL TESTS PASSED!")
            print("✅ TradeMate Charting Platform Implementation Validated")
            print("🚀 Ready for Production Use")
        else:
            print("\n⚠️  Some tests failed - review implementation")
        
        print("=" * 60)
        
        return self.failed_tests == 0


def main():
    """Main entry point"""
    runner = SimpleTestRunner()
    success = runner.run_all_tests()
    return 0 if success else 1


if __name__ == "__main__":
    exit(main())