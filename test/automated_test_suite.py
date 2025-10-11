#!/usr/bin/env python3
"""
Automated Test Suite for HTCondor Web UI
Test scenarios: ESC-01, ESC-02, ESC-03

This script uses Selenium WebDriver to automate the testing process
of the HTCondor web application according to the defined test cases.
"""

import os
import sys
import json
import time
import logging
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import requests
import subprocess

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('test_results.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class HTCondorWebUITestSuite:
    def __init__(self, base_url="http://172.30.27.11:5000", headless=False):
        self.base_url = base_url
        self.test_dir = os.path.dirname(os.path.abspath(__file__))
        self.results = []
        
        # Setup Chrome options
        chrome_options = Options()
        if headless:
            chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        
        try:
            self.driver = webdriver.Chrome(options=chrome_options)
            self.driver.maximize_window()
            self.wait = WebDriverWait(self.driver, 30)
        except Exception as e:
            logger.error(f"Failed to initialize WebDriver: {e}")
            raise
    
    def load_test_config(self, test_id):
        """Load test configuration from JSON file"""
        config_path = os.path.join(self.test_dir, test_id, "test_config.json")
        try:
            with open(config_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            logger.error(f"Test configuration file not found: {config_path}")
            return None
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in test configuration: {e}")
            return None
    
    def wait_for_server_ready(self):
        """Wait for the Flask server to be ready"""
        max_attempts = 30
        for attempt in range(max_attempts):
            try:
                response = requests.get(self.base_url, timeout=5)
                if response.status_code == 200:
                    logger.info("Server is ready")
                    return True
            except requests.RequestException:
                logger.info(f"Waiting for server... attempt {attempt + 1}/{max_attempts}")
                time.sleep(2)
        
        logger.error("Server not ready after maximum attempts")
        return False
    
    def upload_file(self, file_input_id, file_path):
        """Upload a file using the file input element"""
        try:
            file_input = self.wait.until(
                EC.presence_of_element_located((By.ID, file_input_id))
            )
            file_input.send_keys(file_path)
            logger.info(f"Uploaded file: {file_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to upload file {file_path}: {e}")
            return False
    
    def select_dropdown_option(self, dropdown_id, value):
        """Select an option from a dropdown"""
        try:
            dropdown = self.wait.until(
                EC.element_to_be_clickable((By.ID, dropdown_id))
            )
            select = Select(dropdown)
            select.select_by_value(value)
            logger.info(f"Selected {value} in dropdown {dropdown_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to select {value} in dropdown {dropdown_id}: {e}")
            return False
    
    def fill_input_field(self, field_id, value):
        """Fill an input field with a value"""
        try:
            field = self.wait.until(
                EC.element_to_be_clickable((By.ID, field_id))
            )
            field.clear()
            field.send_keys(str(value))
            logger.info(f"Filled {field_id} with: {value}")
            return True
        except Exception as e:
            logger.error(f"Failed to fill {field_id}: {e}")
            return False
    
    def wait_for_cluster_options(self):
        """Wait for cluster options to be loaded dynamically"""
        try:
            # Wait for cluster dropdown to have options (not just the default)
            WebDriverWait(self.driver, 30).until(
                lambda driver: len(driver.find_elements(By.CSS_SELECTOR, "#cluster-guiado option")) > 1
            )
            logger.info("Cluster options loaded")
            return True
        except TimeoutException:
            logger.warning("Cluster options not loaded within timeout, proceeding anyway")
            return False
    
    def submit_form(self):
        """Submit the job form"""
        try:
            submit_button = self.wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "button[type='submit']"))
            )
            submit_button.click()
            logger.info("Form submitted")
            return True
        except Exception as e:
            logger.error(f"Failed to submit form: {e}")
            return False
    
    def wait_for_job_submission_response(self):
        """Wait for job submission response and extract job ID"""
        try:
            # Wait for either success redirect or error message
            time.sleep(3)  # Give time for AJAX response
            
            # Check if we got redirected to results page
            current_url = self.driver.current_url
            if "/results/" in current_url:
                job_id = current_url.split("/results/")[-1]
                logger.info(f"Job submitted successfully, job ID: {job_id}")
                return job_id
            else:
                logger.error("Job submission did not redirect to results page")
                return None
        except Exception as e:
            logger.error(f"Error waiting for job submission response: {e}")
            return None
    
    def validate_results_page(self, job_id, expected_files):
        """Validate that the results page shows expected output files"""
        try:
            # Wait for results to be displayed
            self.wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".results-grid"))
            )
            
            # Count output files displayed
            output_elements = self.driver.find_elements(By.CSS_SELECTOR, ".file-card")
            actual_files = len(output_elements)
            
            logger.info(f"Found {actual_files} output files, expected {expected_files}")
            
            # Wait a bit more for jobs to potentially complete
            time.sleep(40)
            
            # Refresh and check again
            self.driver.refresh()
            time.sleep(5)
            
            output_elements = self.driver.find_elements(By.CSS_SELECTOR, ".file-card")
            actual_files = len(output_elements)
            
            logger.info(f"After refresh: Found {actual_files} output files")
            
            return actual_files >= expected_files
        except Exception as e:
            logger.error(f"Error validating results page: {e}")
            return False
    
    def check_job_status(self, job_id):
        """Check job status via API"""
        try:
            response = requests.get(f"{self.base_url}/job_status/{job_id}")
            if response.status_code == 200:
                status_data = response.json()
                logger.info(f"Job {job_id} status: {status_data}")
                return status_data
            else:
                logger.error(f"Failed to get job status: {response.status_code}")
                return None
        except Exception as e:
            logger.error(f"Error checking job status: {e}")
            return None
    
    def execute_test_esc01(self):
        """Execute ESC-01: Grid execution with equal parameter repetitions"""
        logger.info("=== Starting ESC-01 Test ===")
        test_config = self.load_test_config("ESC-01")
        if not test_config:
            return False
        
        test_result = {
            "test_id": "ESC-01",
            "start_time": datetime.now().isoformat(),
            "status": "RUNNING",
            "steps_completed": [],
            "errors": []
        }
        
        try:
            # Step 1: Navigate to application
            self.driver.get(self.base_url)
            test_result["steps_completed"].append("Page loaded")
            
            # Wait for cluster options to load
            self.wait_for_cluster_options()
            
            # Step 2: Upload binary file
            binary_path = os.path.join(self.test_dir, "ESC-01", "montecarlo_pi.sh")
            if self.upload_file("binary-file", binary_path):
                test_result["steps_completed"].append("Binary uploaded")
            
            # Step 3: Fill additional arguments
            if self.fill_input_field("additional-args", "10"):
                test_result["steps_completed"].append("Arguments filled")
            
            # Step 4: Select job type (vanilla)
            if self.select_dropdown_option("job-type", "vanilla"):
                test_result["steps_completed"].append("Job type selected")
            
            # Step 5: Select vanilla mode (equal repetitions)
            if self.select_dropdown_option("vanilla-mode", "equal"):
                test_result["steps_completed"].append("Vanilla mode selected")
            
            # Step 6: Set repetitions
            if self.fill_input_field("equal-repetitions", "5"):
                test_result["steps_completed"].append("Repetitions set")
            
            # Step 7: Select cluster (if available)
            cluster_options = self.driver.find_elements(By.CSS_SELECTOR, "#cluster-guiado option")
            if len(cluster_options) > 1:
                # Select first available cluster (not the default option)
                select = Select(self.driver.find_element(By.ID, "cluster-guiado"))
                select.select_by_index(1)
                test_result["steps_completed"].append("Cluster selected")
            
            # Step 8: Submit form
            if self.submit_form():
                test_result["steps_completed"].append("Form submitted")
                
                # Step 9: Wait for job submission and get job ID
                job_id = self.wait_for_job_submission_response()
                if job_id:
                    test_result["job_id"] = job_id
                    test_result["steps_completed"].append("Job ID received")
                    
                    # Check job status
                    job_status = self.check_job_status(job_id)
                    if job_status:
                        test_result["job_status"] = job_status
                    
                    # Validate results page
                    if self.validate_results_page(job_id, 5):
                        test_result["steps_completed"].append("Results validated")
                        test_result["status"] = "PASSED"
                    else:
                        test_result["errors"].append("Results validation failed")
                        test_result["status"] = "FAILED"
                else:
                    test_result["errors"].append("Job ID not received")
                    test_result["status"] = "FAILED"
            
        except Exception as e:
            test_result["errors"].append(str(e))
            test_result["status"] = "ERROR"
            logger.error(f"ESC-01 test error: {e}")
        
        test_result["end_time"] = datetime.now().isoformat()
        self.results.append(test_result)
        logger.info(f"ESC-01 completed with status: {test_result['status']}")
        return test_result["status"] == "PASSED"
    
    def execute_test_esc02(self):
        """Execute ESC-02: Grid execution with parametrizable variables"""
        logger.info("=== Starting ESC-02 Test ===")
        test_config = self.load_test_config("ESC-02")
        if not test_config:
            return False
        
        test_result = {
            "test_id": "ESC-02",
            "start_time": datetime.now().isoformat(),
            "status": "RUNNING",
            "steps_completed": [],
            "errors": []
        }
        
        try:
            # Navigate to application
            self.driver.get(self.base_url)
            test_result["steps_completed"].append("Page loaded")
            
            # Wait for cluster options
            self.wait_for_cluster_options()
            
            # Upload binary file
            binary_path = os.path.join(self.test_dir, "ESC-02", "test_binary")
            if self.upload_file("binary-file", binary_path):
                test_result["steps_completed"].append("Binary uploaded")
            
            # Fill additional arguments with variable
            if self.fill_input_field("additional-args", "arg1 VAR1 arg2"):
                test_result["steps_completed"].append("Arguments with variable filled")
            
            # Select job type (vanilla)
            if self.select_dropdown_option("job-type", "vanilla"):
                test_result["steps_completed"].append("Job type selected")
            
            # Select vanilla mode (range)
            if self.select_dropdown_option("vanilla-mode", "range"):
                test_result["steps_completed"].append("Range mode selected")
                
                # Wait for parameter variable dropdown to be populated
                time.sleep(2)
                
                # Select parameter variable (VAR1 should be detected)
                param_options = self.driver.find_elements(By.CSS_SELECTOR, "#param-variable option")
                if len(param_options) > 1:
                    select = Select(self.driver.find_element(By.ID, "param-variable"))
                    # Look for VAR1 or select first available
                    for option in param_options[1:]:  # Skip first default option
                        if "VAR1" in option.text or option.get_attribute("value"):
                            select.select_by_value(option.get_attribute("value"))
                            test_result["steps_completed"].append("Parameter variable selected")
                            break
                    
                    # Fill range values
                    time.sleep(1)  # Wait for sub-options to appear
                    
                    if self.fill_input_field("start-value", "1"):
                        test_result["steps_completed"].append("Start value set")
                    
                    if self.fill_input_field("end-value", "10"):
                        test_result["steps_completed"].append("End value set")
                    
                    if self.fill_input_field("increment", "2"):
                        test_result["steps_completed"].append("Increment set")
            
            # Select cluster
            cluster_options = self.driver.find_elements(By.CSS_SELECTOR, "#cluster-guiado option")
            if len(cluster_options) > 1:
                select = Select(self.driver.find_element(By.ID, "cluster-guiado"))
                select.select_by_index(1)
                test_result["steps_completed"].append("Cluster selected")
            
            # Submit form
            if self.submit_form():
                test_result["steps_completed"].append("Form submitted")
                
                job_id = self.wait_for_job_submission_response()
                if job_id:
                    test_result["job_id"] = job_id
                    test_result["steps_completed"].append("Job ID received")
                    
                    # Check job status
                    job_status = self.check_job_status(job_id)
                    if job_status:
                        test_result["job_status"] = job_status
                    
                    # Validate results (should have 5 jobs: 1,3,5,7,9)
                    if self.validate_results_page(job_id, 5):
                        test_result["steps_completed"].append("Results validated")
                        test_result["status"] = "PASSED"
                    else:
                        test_result["errors"].append("Results validation failed")
                        test_result["status"] = "FAILED"
                else:
                    test_result["errors"].append("Job ID not received")
                    test_result["status"] = "FAILED"
        
        except Exception as e:
            test_result["errors"].append(str(e))
            test_result["status"] = "ERROR"
            logger.error(f"ESC-02 test error: {e}")
        
        test_result["end_time"] = datetime.now().isoformat()
        self.results.append(test_result)
        logger.info(f"ESC-02 completed with status: {test_result['status']}")
        return test_result["status"] == "PASSED"
    
    def execute_test_esc03(self):
        """Execute ESC-03: Parallel execution"""
        logger.info("=== Starting ESC-03 Test ===")
        test_config = self.load_test_config("ESC-03")
        if not test_config:
            return False
        
        test_result = {
            "test_id": "ESC-03",
            "start_time": datetime.now().isoformat(),
            "status": "RUNNING",
            "steps_completed": [],
            "errors": []
        }
        
        try:
            # Navigate to application
            self.driver.get(self.base_url)
            test_result["steps_completed"].append("Page loaded")
            
            # Wait for cluster options
            self.wait_for_cluster_options()
            
            # Upload binary file
            binary_path = os.path.join(self.test_dir, "ESC-03", "test_binary")
            if self.upload_file("binary-file", binary_path):
                test_result["steps_completed"].append("Binary uploaded")
            
            # Fill additional arguments
            if self.fill_input_field("additional-args", "arg1 arg2"):
                test_result["steps_completed"].append("Arguments filled")
            
            # Select job type (parallel)
            if self.select_dropdown_option("job-type", "parallel"):
                test_result["steps_completed"].append("Parallel job type selected")
                
                # Wait for parallel options to appear
                time.sleep(2)
                
                # Upload input file
                input_path = os.path.join(self.test_dir, "ESC-03", "test_input.dat")
                if self.upload_file("input-file", input_path):
                    test_result["steps_completed"].append("Input file uploaded")
                
                # Set machines count
                if self.fill_input_field("machines-count", "2"):
                    test_result["steps_completed"].append("Machines count set")
                
                # Set cores per machine
                if self.fill_input_field("cores-per-machine", "4"):
                    test_result["steps_completed"].append("Cores per machine set")
            
            # Select cluster
            cluster_options = self.driver.find_elements(By.CSS_SELECTOR, "#cluster-guiado option")
            if len(cluster_options) > 1:
                select = Select(self.driver.find_element(By.ID, "cluster-guiado"))
                select.select_by_index(1)
                test_result["steps_completed"].append("Cluster selected")
            
            # Submit form
            if self.submit_form():
                test_result["steps_completed"].append("Form submitted")
                
                job_id = self.wait_for_job_submission_response()
                if job_id:
                    test_result["job_id"] = job_id
                    test_result["steps_completed"].append("Job ID received")
                    
                    # Check job status
                    job_status = self.check_job_status(job_id)
                    if job_status:
                        test_result["job_status"] = job_status
                    
                    # Validate results (should have 1 main output file)
                    if self.validate_results_page(job_id, 1):
                        test_result["steps_completed"].append("Results validated")
                        test_result["status"] = "PASSED"
                    else:
                        test_result["errors"].append("Results validation failed")
                        test_result["status"] = "FAILED"
                else:
                    test_result["errors"].append("Job ID not received")
                    test_result["status"] = "FAILED"
        
        except Exception as e:
            test_result["errors"].append(str(e))
            test_result["status"] = "ERROR"
            logger.error(f"ESC-03 test error: {e}")
        
        test_result["end_time"] = datetime.now().isoformat()
        self.results.append(test_result)
        logger.info(f"ESC-03 completed with status: {test_result['status']}")
        return test_result["status"] == "PASSED"
    
    def generate_report(self):
        """Generate a comprehensive test report"""
        report_path = os.path.join(self.test_dir, "test_report.json")
        
        report = {
            "test_suite": "HTCondor Web UI Automated Tests",
            "execution_date": datetime.now().isoformat(),
            "total_tests": len(self.results),
            "passed_tests": len([r for r in self.results if r["status"] == "PASSED"]),
            "failed_tests": len([r for r in self.results if r["status"] == "FAILED"]),
            "error_tests": len([r for r in self.results if r["status"] == "ERROR"]),
            "test_results": self.results
        }
        
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)
        
        # Print summary
        logger.info("=== TEST SUITE SUMMARY ===")
        logger.info(f"Total tests: {report['total_tests']}")
        logger.info(f"Passed: {report['passed_tests']}")
        logger.info(f"Failed: {report['failed_tests']}")
        logger.info(f"Errors: {report['error_tests']}")
        logger.info(f"Success rate: {(report['passed_tests']/report['total_tests']*100):.1f}%")
        logger.info(f"Detailed report saved to: {report_path}")
        
        return report
    
    def run_all_tests(self):
        """Execute all test scenarios"""
        logger.info("Starting HTCondor Web UI Test Suite")
        
        # Wait for server to be ready
        if not self.wait_for_server_ready():
            logger.error("Cannot proceed - server not ready")
            return False
        
        # Execute all tests
        tests = [
            self.execute_test_esc01,
            self.execute_test_esc02,
            self.execute_test_esc03
        ]
        
        all_passed = True
        for test_func in tests:
            try:
                result = test_func()
                all_passed = all_passed and result
            except Exception as e:
                logger.error(f"Test execution failed: {e}")
                all_passed = False
            
            # Wait between tests
            time.sleep(5)
        
        # Generate report
        report = self.generate_report()
        
        return all_passed
    
    def cleanup(self):
        """Clean up resources"""
        if hasattr(self, 'driver'):
            self.driver.quit()
            logger.info("WebDriver closed")

def main():
    """Main function to run the test suite"""
    import argparse
    
    parser = argparse.ArgumentParser(description="HTCondor Web UI Test Suite")
    parser.add_argument("--url", default="http://172.30.27.11:5000", help="Base URL of the application")
    parser.add_argument("--headless", action="store_true", help="Run in headless mode")
    parser.add_argument("--test", choices=["ESC-01", "ESC-02", "ESC-03"], help="Run specific test")
    
    args = parser.parse_args()
    
    test_suite = None
    try:
        test_suite = HTCondorWebUITestSuite(base_url=args.url, headless=args.headless)
        
        if args.test:
            # Run specific test
            if args.test == "ESC-01":
                success = test_suite.execute_test_esc01()
            elif args.test == "ESC-02":
                success = test_suite.execute_test_esc02()
            elif args.test == "ESC-03":
                success = test_suite.execute_test_esc03()
            
            test_suite.generate_report()
        else:
            # Run all tests
            success = test_suite.run_all_tests()
        
        exit_code = 0 if success else 1
        sys.exit(exit_code)
        
    except Exception as e:
        logger.error(f"Test suite failed: {e}")
        sys.exit(1)
    finally:
        if test_suite:
            test_suite.cleanup()

if __name__ == "__main__":
    main()
