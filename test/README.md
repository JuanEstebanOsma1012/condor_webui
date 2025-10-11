# HTCondor Web UI Automated Test Suite

This test suite provides automated testing for the HTCondor Web UI application based on the three defined test scenarios (ESC-01, ESC-02, ESC-03).

## Test Structure

```
test/
├── automated_test_suite.py    # Main Selenium test script
├── test_requirements.txt      # Python dependencies
├── README.md                 # This file
├── ESC-01/                   # Grid execution with equal parameters
│   ├── test_config.json      # Test configuration
│   └── test_binary           # Executable test binary
├── ESC-02/                   # Grid execution with parametrizable variables
│   ├── test_config.json      # Test configuration
│   └── test_binary           # Executable test binary
└── ESC-03/                   # Parallel execution
    ├── test_config.json      # Test configuration
    ├── test_binary           # Executable test binary
    └── test_input.dat        # Input data file
```

## Test Scenarios

### ESC-01: Grid Execution with Equal Parameter Repetitions
- **Objective**: Validate vanilla Grid universe execution with repeated identical parameters
- **Requirements**: RF1, RF2, RF3, RF4, RF7, RF8, RNF1, RNF2, RNF3
- **Expected Output**: 5 job output files with identical parameters

### ESC-02: Grid Execution with Parametrizable Variables
- **Objective**: Validate vanilla Grid universe execution with variable parameters
- **Requirements**: RF1, RF2, RF3, RF4, RF7, RF8, RNF1, RNF2, RNF3
- **Expected Output**: 5 job output files with different parameter values (1,3,5,7,9)

### ESC-03: Parallel Execution
- **Objective**: Validate parallel universe execution
- **Requirements**: RF1, RF2, RF3, RF4, RF5, RF6, RF8, RNF1, RNF2, RNF3
- **Expected Output**: 1 job output file from parallel execution

## Prerequisites

1. **Chrome WebDriver**: Install ChromeDriver and ensure it's in your PATH
   ```bash
   # On Ubuntu/Debian:
   sudo apt-get install chromium-chromedriver
   
   # Or download from: https://chromedriver.chromium.org/
   ```

2. **Python Dependencies**: Install required packages
   ```bash
   pip install -r test_requirements.txt
   ```

3. **HTCondor Web Application**: Ensure the Flask application is running on localhost:5000
   ```bash
   cd /home/juan/Documents/trabajo_de_grado/Raspberries/services/app_submit/app/
   python app.py
   ```

4. **HTCondor Environment**: Ensure HTCondor is properly configured and running

## Usage

### Run All Tests
```bash
cd /home/juan/Documents/trabajo_de_grado/Raspberries/services/app_submit/app/test/
python automated_test_suite.py
```

### Run Specific Test
```bash
# Run only ESC-01
python automated_test_suite.py --test ESC-01

# Run only ESC-02
python automated_test_suite.py --test ESC-02

# Run only ESC-03
python automated_test_suite.py --test ESC-03
```

### Run in Headless Mode
```bash
python automated_test_suite.py --headless
```

### Specify Different URL
```bash
python automated_test_suite.py --url http://192.168.1.100:5000
```

## Test Configuration

Each test scenario has a `test_config.json` file that defines:

- **Test metadata**: ID, name, description, requirements
- **Test data**: Job configuration, file paths, expected results
- **Test steps**: Detailed step-by-step actions to perform
- **Validation criteria**: Success criteria for the test

You can modify these configuration files to adjust test parameters without changing the test code.

## Test Results

### Output Files
- **test_results.log**: Detailed execution log
- **test_report.json**: Comprehensive JSON report with results
- **Console output**: Real-time test progress

### Test Status
- **PASSED**: Test completed successfully, all validations passed
- **FAILED**: Test completed but validations failed
- **ERROR**: Test encountered an error during execution

### Report Content
The JSON report includes:
- Test execution summary
- Individual test results
- Step-by-step execution details
- Error messages and debugging information
- Job IDs and status information

## Customization

### Adding New Tests
1. Create a new test directory (e.g., `ESC-04/`)
2. Add `test_config.json` with test configuration
3. Add test files (binaries, input data)
4. Add test method to `automated_test_suite.py`

### Modifying Test Data
- Edit `test_config.json` files to change test parameters
- Replace test binaries with your own executables
- Modify input data files as needed

### Extending Validation
- Add custom validation methods to the test suite
- Modify `validation_criteria` in test configurations
- Add new assertion checks in test methods

## Troubleshooting

### Common Issues

1. **ChromeDriver not found**
   - Install ChromeDriver and add to PATH
   - Use `--headless` flag if running without display

2. **Server not responding**
   - Ensure Flask app is running on correct port
   - Check network connectivity
   - Verify no firewall blocking connections

3. **HTCondor errors**
   - Check HTCondor daemon status
   - Verify cluster configuration
   - Ensure proper permissions

4. **File upload failures**
   - Check file paths in test configuration
   - Ensure test binaries are executable
   - Verify file permissions

### Debug Mode
Add logging level to see more details:
```python
logging.getLogger().setLevel(logging.DEBUG)
```

## Integration with CI/CD

The test suite is designed for integration with continuous integration systems:

```bash
# Exit code 0 = all tests passed
# Exit code 1 = some tests failed
python automated_test_suite.py --headless
echo $?  # Check exit code
```

## Performance Considerations

- Tests include appropriate wait times for job submission and execution
- Timeouts are configurable in test configurations
- Background job monitoring prevents indefinite waits
- Resource cleanup ensures no hanging processes

## Security Notes

- Test binaries are simple shell scripts for safety
- No sensitive data in test configurations
- Local execution only (no remote code execution)
- Proper file permission management
