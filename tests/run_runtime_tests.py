#!/usr/bin/env python3
"""
Simple runner for the core AnomalyAgent runtime tests
"""

import subprocess
import sys
from pathlib import Path

def run_runtime_tests():
    """Run the essential runtime behavioral risk detection tests"""
    
    print("🧪 AnomalyAgent Runtime Test Suite")
    print("=" * 50)
    
    tests_to_run = [
        {
            "name": "API Health Check",
            "command": ["curl", "-s", "https://8081-i6ebstkn8678no6p36fel-6532622b.e2b.dev/health"]
        },
        {
            "name": "Safe Scenario Test",
            "command": ["python3", "quick_scenario_test.py", "--scenario", "safe_001"]
        },
        {
            "name": "Risky Scenario Test", 
            "command": ["python3", "quick_scenario_test.py", "--scenario", "risky_001"]
        }
    ]
    
    results = []
    
    for test in tests_to_run:
        print(f"\n🔄 Running: {test['name']}")
        try:
            result = subprocess.run(
                test["command"], 
                capture_output=True, 
                text=True, 
                timeout=180
            )
            
            if result.returncode == 0:
                print(f"✅ {test['name']}: PASSED")
                results.append(("PASS", test['name']))
            else:
                print(f"❌ {test['name']}: FAILED")
                print(f"   Error: {result.stderr[:200]}")
                results.append(("FAIL", test['name']))
                
        except subprocess.TimeoutExpired:
            print(f"⏰ {test['name']}: TIMEOUT")
            results.append(("TIMEOUT", test['name']))
        except Exception as e:
            print(f"❌ {test['name']}: ERROR - {e}")
            results.append(("ERROR", test['name']))
    
    # Summary
    print(f"\n{'='*50}")
    print("📊 TEST SUMMARY")
    print(f"{'='*50}")
    
    passed = len([r for r in results if r[0] == "PASS"])
    total = len(results)
    
    for status, name in results:
        status_icon = {"PASS": "✅", "FAIL": "❌", "TIMEOUT": "⏰", "ERROR": "❌"}
        print(f"{status_icon.get(status, '❓')} {name}: {status}")
    
    print(f"\n📊 Overall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All runtime tests passed!")
        return True
    else:
        print("⚠️ Some tests failed - check system status")
        return False

def main():
    """Main entry point"""
    print("🎯 Running AnomalyAgent core runtime tests...")
    print("💡 For comprehensive testing, use: python3 runtime_test_runner.py")
    print("💡 For single scenarios, use: python3 quick_scenario_test.py --scenario <id>")
    print()
    
    success = run_runtime_tests()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()