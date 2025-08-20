# Breaders WhatsApp Bot Testing Framework

This document provides comprehensive guidelines for the testing framework used in the Breaders WhatsApp Bot project.

## Table of Contents

1. [Overview](#overview)
2. [Test Structure](#test-structure)
3. [Running Tests](#running-tests)
4. [Creating New Tests](#creating-new-tests)
5. [Logging and Output](#logging-and-output)
6. [CI/CD Integration](#cicd-integration)
7. [Best Practices](#best-practices)

## Overview

The Breaders WhatsApp Bot testing framework is built on Python's unittest framework and Django's TestCase class. It features:

- A modular test structure with separate test files for each major component
- A main test runner that orchestrates all test cases
- Enhanced logging with clear, formatted messages for each test step
- Comprehensive test coverage for critical functionalities

## Test Structure

The testing structure follows a hierarchical approach:

```
whatsapp_bot/tests/
├── README.md               # This documentation
├── run_tests.py            # Main test runner
├── test_base.py            # Base test case with common utilities
├── test_whatsapp_flow.py   # Tests for WhatsApp message flow
├── test_twilio_ai_handler_new.py # Tests for Twilio AI integration
├── test_ngrok_integration.py # Tests for ngrok tunnel integration
└── ... other component-specific test files
```

### Key Components

- **`run_tests.py`**: Orchestrates the execution of all test suites
- **`test_base.py`**: Provides the `BreadersBotBaseTestCase` class with enhanced logging and common utilities
- **Component-specific test files**: Each major component has its own dedicated test file

## Running Tests

### Running All Tests

To run all tests with the enhanced test runner:

```bash
python whatsapp_bot/tests/run_tests.py
```

This will:
- Discover all test files in the `tests` directory
- Run each test suite in sequence
- Display a comprehensive summary of results
- Create a log file with detailed test information

### Running Individual Test Suites

To run a specific test suite:

```bash
python -m unittest whatsapp_bot.tests.test_whatsapp_flow
```

### Running Specific Test Cases

To run a specific test case:

```bash
python -m unittest whatsapp_bot.tests.test_whatsapp_flow.WhatsAppFlowTest.test_greeting_flow
```

## Creating New Tests

### Step 1: Create a New Test File

Create a new Python file in the `whatsapp_bot/tests` directory with a name following the convention `test_component_name.py`.

### Step 2: Import Base Test Case

```python
from whatsapp_bot.tests.test_base import BreadersBotBaseTestCase
```

### Step 3: Create Test Class

```python
class YourComponentTest(BreadersBotBaseTestCase):
    """
    Tests for YourComponent.
    
    Detailed description of what these tests verify.
    """
    
    def setUp(self):
        """Set up test environment."""
        super().setUp()
        self.log_step("Setting up test environment for YourComponent")
        # Component-specific setup
    
    def tearDown(self):
        """Clean up after tests."""
        self.log_step("Cleaning up test environment")
        # Component-specific cleanup
        super().tearDown()
    
    def test_your_functionality(self):
        """Test description."""
        self.log_step("Testing your functionality")
        
        # Perform test steps
        self.log_check("Checking expected behavior")
        result = self.perform_action()
        
        # Assert with logging
        self.assert_equal_with_log(
            result,
            expected_value,
            "Checking if result matches expected value"
        )
```

## Logging and Output

The testing framework provides enhanced logging through the `BreadersBotBaseTestCase` class:

- **`self.log_step(message)`**: Log a test step
- **`self.log_check(message)`**: Log an assertion or check
- **`self.log_result(message, success=True)`**: Log a test result
- **`self.assert_with_log(condition, message, success_message=None)`**: Assert with detailed logging
- **`self.assert_equal_with_log(first, second, message, success_message=None)`**: Assert equality with logging
- **`self.assert_in_with_log(member, container, message, success_message=None)`**: Assert membership with logging

Example:

```python
# Instead of:
self.assertEqual(result, expected_value)

# Use:
self.assert_equal_with_log(
    result, 
    expected_value,
    "Checking if result matches expected value",
    "Result matches expected value!"
)
```

## CI/CD Integration

The test framework is designed to work seamlessly with CI/CD pipelines:

1. The test runner returns appropriate exit codes (0 for success, non-zero for failure)
2. Logs are written to files that can be captured as artifacts
3. Test output is formatted for easy parsing

## Best Practices

1. **Test Isolation**: Each test should be independent of other tests
2. **Clear Documentation**: Document the purpose of each test case and test method
3. **Use Mocks**: Mock external services and dependencies
4. **Descriptive Logging**: Use descriptive messages in logging calls
5. **Test Edge Cases**: Include tests for error conditions and edge cases
6. **Keep Tests Focused**: Each test method should test a single functionality
7. **Follow AAA Pattern**: Arrange, Act, Assert

### Example Test Structure

```python
def test_user_login(self):
    """Test user login functionality."""
    # Arrange - set up the test
    self.log_step("Setting up test user")
    test_user = self.create_test_user()
    
    # Act - perform the action to test
    self.log_step("Attempting to log in")
    result = self.client.login(username='testuser', password='testpass')
    
    # Assert - verify the results
    self.assert_with_log(
        result,
        "Checking if login was successful",
        "Login successful as expected"
    )
```

## Maintainability Tips

1. **Keep the Base Test Case Updated**: As you discover common patterns, add them to `test_base.py`
2. **Review Test Coverage**: Regularly review and update tests to maintain coverage
3. **Refactor Tests**: When the application code changes significantly, refactor tests accordingly
4. **Document Assumptions**: Document any assumptions made in the tests
5. **Test the Tests**: Occasionally verify that tests fail when they should
