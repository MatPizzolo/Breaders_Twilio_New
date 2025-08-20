#!/usr/bin/env python
"""
Main Test Runner for Breaders WhatsApp Bot

This script orchestrates the execution of all test suites in the project.
Each test suite is dedicated to a specific component or functionality.
Results are displayed with clear logging and simple messages for each test case.
"""
import os
import sys

# Fix Python path for imports
# Add the project root directory to the Python path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

# Now we can properly import Django settings to set up the environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'breaders_twilio_bot.settings')

# Try to set up Django
try:
    import django
    django.setup()
    print("Django setup successful")
except Exception as e:
    print(f"Warning: Django setup failed: {e}")
    print("Some tests requiring Django might fail.")

import unittest
import logging
import datetime
import importlib
import traceback
from termcolor import colored

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger('test_runner')

# File handler to save logs to a file
log_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'logs')
os.makedirs(log_dir, exist_ok=True)
timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
log_file = os.path.join(log_dir, f'test_run_{timestamp}.log')
file_handler = logging.FileHandler(log_file)
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
logger.addHandler(file_handler)

class TestRunner:
    """
    Main test runner class that orchestrates the execution of all test suites.
    
    Attributes:
        test_files (list): List of test files to run
        results (dict): Dictionary to store test results
    """
    
    def __init__(self):
        """Initialize the test runner."""
        self.test_files = []
        self.results = {
            'total': 0,
            'passed': 0,
            'failed': 0,
            'errors': 0,
            'skipped': 0,
            'details': {}
        }
    
    def discover_test_files(self):
        """
        Discover all test files in the tests directory.
        
        Returns:
            list: List of discovered test files
        """
        logger.info("Discovering test files...")
        test_dir = os.path.dirname(os.path.abspath(__file__))
        
        for filename in os.listdir(test_dir):
            if (filename.startswith('test_') and filename.endswith('.py') and 
                filename != os.path.basename(__file__)):
                self.test_files.append(filename[:-3])  # Remove .py extension
                logger.debug(f"Discovered test file: {filename}")
        
        return self.test_files
    
    def run_test_file(self, test_module_name):
        """
        Run a specific test file.
        
        Args:
            test_module_name (str): Name of the test module to run
            
        Returns:
            tuple: (success, result_detail)
        """
        full_module_name = f"whatsapp_bot.tests.{test_module_name}"
        
        try:
            logger.info(f"Running test module: {test_module_name}")
            print(colored(f"\n{'='*60}", 'cyan'))
            print(colored(f" TEST MODULE: {test_module_name}", 'cyan', attrs=['bold']))
            print(colored(f"{'='*60}", 'cyan'))
            
            # Import the test module dynamically
            test_module = importlib.import_module(full_module_name)
            
            # Discover and create a test suite from the module
            loader = unittest.TestLoader()
            suite = loader.loadTestsFromModule(test_module)
            
            # Create a test result collector
            result = unittest.TextTestRunner(verbosity=2).run(suite)
            
            # Collect test results
            test_results = {
                'total': result.testsRun,
                'passed': result.testsRun - len(result.errors) - len(result.failures) - len(result.skipped),
                'failed': len(result.failures),
                'errors': len(result.errors),
                'skipped': len(result.skipped),
                'failures_detail': [str(failure[0]) for failure in result.failures],
                'errors_detail': [str(error[0]) for error in result.errors]
            }
            
            # Update global results
            self.results['total'] += test_results['total']
            self.results['passed'] += test_results['passed']
            self.results['failed'] += test_results['failed']
            self.results['errors'] += test_results['errors']
            self.results['skipped'] += test_results['skipped']
            self.results['details'][test_module_name] = test_results
            
            # Log results for this test file
            logger.info(f"Test results for {test_module_name}: "
                        f"Total={test_results['total']}, "
                        f"Passed={test_results['passed']}, "
                        f"Failed={test_results['failed']}, "
                        f"Errors={test_results['errors']}, "
                        f"Skipped={test_results['skipped']}")
            
            return result.wasSuccessful(), test_results
        
        except Exception as e:
            error_msg = f"Error running test module {test_module_name}: {str(e)}"
            logger.error(error_msg)
            logger.error(traceback.format_exc())
            
            # Update error count
            self.results['errors'] += 1
            self.results['details'][test_module_name] = {
                'total': 0,
                'passed': 0,
                'failed': 0,
                'errors': 1,
                'skipped': 0,
                'errors_detail': [error_msg]
            }
            
            return False, None
    
    def run_all_tests(self):
        """
        Run all discovered test files.
        
        Returns:
            bool: True if all tests pass, False otherwise
        """
        logger.info("Starting test run")
        print(colored("\n==== BREADERS WHATSAPP BOT TEST SUITE ====", 'yellow', attrs=['bold']))
        
        if not self.test_files:
            self.discover_test_files()
            
        if not self.test_files:
            logger.warning("No test files found!")
            print(colored("No test files found!", 'red'))
            return False
        
        logger.info(f"Found {len(self.test_files)} test files: {', '.join(self.test_files)}")
        all_success = True
        
        for test_file in self.test_files:
            success, _ = self.run_test_file(test_file)
            all_success = all_success and success
        
        self.print_summary()
        return all_success
    
    def print_summary(self):
        """Print a summary of all test results."""
        print(colored("\n\n===== TEST SUMMARY =====", 'green', attrs=['bold']))
        print(f"Total Tests Run: {self.results['total']}")
        print(colored(f"Passed: {self.results['passed']}", 'green'))
        
        if self.results['failed'] > 0:
            print(colored(f"Failed: {self.results['failed']}", 'red'))
        else:
            print(f"Failed: {self.results['failed']}")
        
        if self.results['errors'] > 0:
            print(colored(f"Errors: {self.results['errors']}", 'red'))
        else:
            print(f"Errors: {self.results['errors']}")
        
        if self.results['skipped'] > 0:
            print(colored(f"Skipped: {self.results['skipped']}", 'yellow'))
        else:
            print(f"Skipped: {self.results['skipped']}")
        
        success_rate = 100 * self.results['passed'] / self.results['total'] if self.results['total'] > 0 else 0
        print(f"Success Rate: {success_rate:.2f}%")
        
        # Print details for modules with failures or errors
        has_issues = False
        for module_name, results in self.results['details'].items():
            if results['failed'] > 0 or results['errors'] > 0:
                has_issues = True
                print(colored(f"\nIssues in {module_name}:", 'red'))
                
                if results['failed'] > 0:
                    print(colored("Failures:", 'red'))
                    for failure in results.get('failures_detail', []):
                        print(f"  - {failure}")
                
                if results['errors'] > 0:
                    print(colored("Errors:", 'red'))
                    for error in results.get('errors_detail', []):
                        print(f"  - {error}")
        
        if not has_issues and self.results['total'] > 0:
            print(colored("\nAll tests passed successfully!", 'green', attrs=['bold']))
        
        print(colored(f"\nFull test log available at: {log_file}", 'blue'))

def main():
    """Main function to run all tests."""
    runner = TestRunner()
    success = runner.run_all_tests()
    
    # Return appropriate exit code
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())
