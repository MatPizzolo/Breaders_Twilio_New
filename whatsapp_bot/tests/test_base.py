"""
Base Test Case for Breaders WhatsApp Bot

This module provides a base test case class with standardized logging and common utilities
for all test cases in the Breaders WhatsApp Bot project.
"""
import os
import logging
import unittest
from django.test import TestCase
from termcolor import colored

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

class BreadersBotBaseTestCase(TestCase):
    """
    Base test case for Breaders WhatsApp Bot tests.
    
    Provides standardized logging and common utilities for all test cases.
    All other test classes should inherit from this class.
    """
    
    @classmethod
    def setUpClass(cls):
        """Class-level setup executed before any test methods."""
        super().setUpClass()
        cls.logger = logging.getLogger(cls.__name__)
        cls.log_header(f"Setting up {cls.__name__}")
    
    @classmethod
    def tearDownClass(cls):
        """Class-level teardown executed after all test methods have been run."""
        cls.log_header(f"Tearing down {cls.__name__}")
        super().tearDownClass()
    
    def setUp(self):
        """Set up the test case before each test method runs."""
        super().setUp()
        self.log_test_start(self._testMethodName)
    
    def tearDown(self):
        """Clean up after each test method finishes."""
        self.log_test_end(self._testMethodName)
        super().tearDown()
    
    @classmethod
    def log_header(cls, message):
        """
        Log a header message.
        
        Args:
            message (str): The message to log
        """
        cls.logger.info(f"{'='*20} {message} {'='*20}")
        print(colored(f"\n{'='*20} {message} {'='*20}", 'cyan'))
    
    def log_test_start(self, test_name):
        """
        Log the start of a test method.
        
        Args:
            test_name (str): Name of the test method
        """
        self.logger.info(f"STARTING TEST: {test_name}")
        print(colored(f"\nSTARTING TEST: {test_name}", 'green'))
    
    def log_test_end(self, test_name):
        """
        Log the end of a test method.
        
        Args:
            test_name (str): Name of the test method
        """
        self.logger.info(f"COMPLETED TEST: {test_name}")
        print(colored(f"COMPLETED TEST: {test_name}", 'green'))
    
    def log_step(self, step_message):
        """
        Log a test step with consistent formatting.
        
        Args:
            step_message (str): Description of the test step
        """
        self.logger.info(f"STEP: {step_message}")
        print(colored(f"  STEP: {step_message}", 'blue'))
    
    def log_check(self, check_message):
        """
        Log a test assertion or check with consistent formatting.
        
        Args:
            check_message (str): Description of what is being checked
        """
        self.logger.info(f"CHECK: {check_message}")
        print(colored(f"    CHECK: {check_message}", 'magenta'))
    
    def log_result(self, result_message, success=True):
        """
        Log a test result with colored output based on success.
        
        Args:
            result_message (str): Result message
            success (bool): Whether the result indicates success
        """
        self.logger.info(f"RESULT: {result_message}")
        color = 'green' if success else 'red'
        print(colored(f"      RESULT: {result_message}", color))
    
    def assert_with_log(self, condition, message, success_message=None):
        """
        Assert a condition with detailed logging.
        
        Args:
            condition: The condition to assert
            message (str): Message for assertion failure
            success_message (str, optional): Message for assertion success
        """
        self.log_check(message)
        try:
            self.assertTrue(condition, message)
            if success_message:
                self.log_result(success_message)
            else:
                self.log_result("Assertion passed")
            return True
        except AssertionError as e:
            self.log_result(f"Assertion failed: {str(e)}", success=False)
            raise
    
    def assert_equal_with_log(self, first, second, message, success_message=None):
        """
        Assert equality with detailed logging.
        
        Args:
            first: First object to compare
            second: Second object to compare
            message (str): Message for assertion failure
            success_message (str, optional): Message for assertion success
        """
        self.log_check(message)
        try:
            self.assertEqual(first, second, message)
            if success_message:
                self.log_result(success_message)
            else:
                self.log_result(f"Equality assertion passed: {first} == {second}")
            return True
        except AssertionError as e:
            self.log_result(f"Equality assertion failed: {first} != {second}", success=False)
            raise
    
    def assert_in_with_log(self, member, container, message, success_message=None):
        """
        Assert membership with detailed logging.
        
        Args:
            member: The object to check for membership
            container: The container object
            message (str): Message for assertion failure
            success_message (str, optional): Message for assertion success
        """
        self.log_check(message)
        try:
            self.assertIn(member, container, message)
            if success_message:
                self.log_result(success_message)
            else:
                self.log_result(f"Membership assertion passed: {member} is in the container")
            return True
        except AssertionError as e:
            self.log_result(f"Membership assertion failed: {member} is not in the container", success=False)
            raise
    
    def mock_with_log(self, target, attribute, new_callable=None):
        """
        Create and log a mock object.
        
        Args:
            target: The object to patch
            attribute (str): The attribute of the target to patch
            new_callable (callable, optional): The callable to create the mock object
            
        Returns:
            unittest.mock.Mock: The mock object
        """
        from unittest.mock import patch
        
        self.log_step(f"Mocking {target}.{attribute}")
        patcher = patch.object(target, attribute, new_callable=new_callable)
        mock_obj = patcher.start()
        self.addCleanup(patcher.stop)
        return mock_obj
