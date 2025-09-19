#!/usr/bin/env python3
"""
Test runner for all BigQuery AI tests
Run this script to execute all tests in the test folder
"""
import os
import sys
import subprocess
import glob
from pathlib import Path

def run_test_file(test_file):
    """Run a single test file"""
    print(f"\n🧪 Running: {test_file}")
    print("=" * 60)
    
    try:
        # Change to the test directory to ensure relative paths work
        test_dir = Path(__file__).parent
        os.chdir(test_dir)
        
        # Run the test file
        result = subprocess.run([sys.executable, test_file], 
                              capture_output=True, 
                              text=True, 
                              timeout=60)
        
        if result.returncode == 0:
            print("✅ Test completed successfully")
            if result.stdout:
                print("📤 Output:")
                print(result.stdout)
        else:
            print("❌ Test failed")
            if result.stderr:
                print("📤 Error output:")
                print(result.stderr)
            if result.stdout:
                print("📤 Standard output:")
                print(result.stdout)
                
        return result.returncode == 0
        
    except subprocess.TimeoutExpired:
        print("⏰ Test timed out after 60 seconds")
        return False
    except Exception as e:
        print(f"💥 Error running test: {e}")
        return False

def main():
    """Run all test files"""
    print("🚀 BigQuery AI Test Suite")
    print("=" * 60)
    
    # Get the test directory
    test_dir = Path(__file__).parent
    
    # Find all Python test files
    test_files = glob.glob(str(test_dir / "test_*.py"))
    test_files.extend(glob.glob(str(test_dir / "create_test_model.py")))
    test_files.extend(glob.glob(str(test_dir / "minimal_test.py")))
    
    # Sort test files for consistent execution order
    test_files.sort()
    
    print(f"📁 Found {len(test_files)} test files:")
    for test_file in test_files:
        print(f"   - {Path(test_file).name}")
    
    print(f"\n🎯 Starting test execution...")
    
    # Track results
    passed = 0
    failed = 0
    
    # Run each test
    for test_file in test_files:
        success = run_test_file(test_file)
        if success:
            passed += 1
        else:
            failed += 1
    
    # Summary
    print(f"\n📊 Test Summary")
    print("=" * 60)
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")
    print(f"📈 Success Rate: {(passed / (passed + failed) * 100):.1f}%")
    
    if failed == 0:
        print("\n🎉 All tests passed!")
        return 0
    else:
        print(f"\n⚠️  {failed} test(s) failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())
