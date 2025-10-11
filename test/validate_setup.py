#!/usr/bin/env python3
"""
Test Structure Validator
Validates that all test files and configurations are properly set up.
"""

import os
import json
import sys
from pathlib import Path

def validate_test_structure():
    """Validate the test directory structure and files"""
    test_dir = Path(__file__).parent
    print(f"Validating test structure in: {test_dir}")
    
    errors = []
    warnings = []
    
    # Expected test scenarios
    test_scenarios = ["ESC-01", "ESC-02", "ESC-03"]
    
    # Check main test files
    required_files = [
        "automated_test_suite.py",
        "test_requirements.txt",
        "README.md",
        "run_tests.sh"
    ]
    
    for file in required_files:
        file_path = test_dir / file
        if not file_path.exists():
            errors.append(f"Missing required file: {file}")
        elif file.endswith(".py") or file.endswith(".sh"):
            if not os.access(file_path, os.X_OK):
                warnings.append(f"File not executable: {file}")
    
    # Check each test scenario
    for scenario in test_scenarios:
        scenario_dir = test_dir / scenario
        
        if not scenario_dir.exists():
            errors.append(f"Missing test scenario directory: {scenario}")
            continue
        
        # Check test configuration
        config_file = scenario_dir / "test_config.json"
        if not config_file.exists():
            errors.append(f"Missing config file: {scenario}/test_config.json")
        else:
            try:
                with open(config_file, 'r') as f:
                    config = json.load(f)
                
                # Validate config structure
                required_keys = ["test_id", "test_name", "description", "test_data", "test_steps", "validation_criteria"]
                for key in required_keys:
                    if key not in config:
                        errors.append(f"Missing config key '{key}' in {scenario}/test_config.json")
                
                # Validate test_id matches directory
                if config.get("test_id") != scenario:
                    warnings.append(f"Test ID mismatch in {scenario}: expected {scenario}, got {config.get('test_id')}")
                
            except json.JSONDecodeError as e:
                errors.append(f"Invalid JSON in {scenario}/test_config.json: {e}")
        
        # Check test binary
        binary_file = scenario_dir / "test_binary"
        if not binary_file.exists():
            errors.append(f"Missing test binary: {scenario}/test_binary")
        elif not os.access(binary_file, os.X_OK):
            errors.append(f"Test binary not executable: {scenario}/test_binary")
        
        # Check additional files for ESC-03
        if scenario == "ESC-03":
            input_file = scenario_dir / "test_input.dat"
            if not input_file.exists():
                warnings.append(f"Missing input file: {scenario}/test_input.dat")
    
    # Print validation results
    print("\n" + "="*50)
    print("VALIDATION RESULTS")
    print("="*50)
    
    if not errors and not warnings:
        print("✓ All validation checks passed!")
        return True
    
    if warnings:
        print(f"\n⚠️  WARNINGS ({len(warnings)}):")
        for warning in warnings:
            print(f"  - {warning}")
    
    if errors:
        print(f"\n❌ ERRORS ({len(errors)}):")
        for error in errors:
            print(f"  - {error}")
        print("\nPlease fix the errors before running tests.")
        return False
    
    print(f"\n✓ Structure is valid (with {len(warnings)} warnings)")
    return True

def check_dependencies():
    """Check if required dependencies are available"""
    print("\nChecking dependencies...")
    
    missing_deps = []
    
    try:
        import selenium
        print(f"✓ Selenium: {selenium.__version__}")
    except ImportError:
        missing_deps.append("selenium")
    
    try:
        import requests
        print(f"✓ Requests: {requests.__version__}")
    except ImportError:
        missing_deps.append("requests")
    
    # Check ChromeDriver
    try:
        import subprocess
        result = subprocess.run(['chromedriver', '--version'], 
                              capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            version = result.stdout.strip()
            print(f"✓ ChromeDriver: {version}")
        else:
            missing_deps.append("chromedriver")
    except (subprocess.TimeoutExpired, FileNotFoundError):
        missing_deps.append("chromedriver")
    
    if missing_deps:
        print(f"\n❌ Missing dependencies: {', '.join(missing_deps)}")
        print("\nInstall missing dependencies:")
        if "selenium" in missing_deps or "requests" in missing_deps:
            print("  pip install -r test_requirements.txt")
        if "chromedriver" in missing_deps:
            print("  sudo apt-get install chromium-chromedriver  # Ubuntu/Debian")
            print("  Or download from: https://chromedriver.chromium.org/")
        return False
    
    print("✓ All dependencies are available")
    return True

def main():
    """Main validation function"""
    print("HTCondor Web UI Test Structure Validator")
    print("="*40)
    
    structure_valid = validate_test_structure()
    deps_valid = check_dependencies()
    
    print("\n" + "="*50)
    if structure_valid and deps_valid:
        print("🎉 Everything looks good! You can now run the tests.")
        print("\nTo run tests:")
        print("  ./run_tests.sh                 # Run all tests")
        print("  ./run_tests.sh --test ESC-01   # Run specific test")
        print("  ./run_tests.sh --headless      # Run without GUI")
        sys.exit(0)
    else:
        print("❌ Validation failed. Please fix the issues above.")
        sys.exit(1)

if __name__ == "__main__":
    main()
