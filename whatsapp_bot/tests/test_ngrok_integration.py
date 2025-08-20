"""
Test suite for ngrok integration

This module provides comprehensive tests for the ngrok integration functionality,
testing the retrieval of ngrok tunnel URLs and updating Django configuration.
"""
import os
import json
import unittest
from unittest.mock import patch, MagicMock, mock_open
import subprocess
import sys

# Add project root to path for importing run_dev
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
import run_dev
from whatsapp_bot.tests.test_base import BreadersBotBaseTestCase


class NgrokIntegrationTest(BreadersBotBaseTestCase):
    """
    Tests for the ngrok integration functionality.
    
    These tests focus on the functionality in run_dev.py for:
    1. Starting ngrok
    2. Retrieving the ngrok tunnel URL
    3. Updating Django configuration with the ngrok URL
    """
    
    def setUp(self):
        """Set up test environment."""
        super().setUp()
        self.log_step("Setting up ngrok integration test environment")
        
        # Patch subprocess.run to prevent actual commands from running
        self.run_patcher = patch('subprocess.run')
        self.mock_run = self.run_patcher.start()
        
        # Patch subprocess.Popen to prevent actual processes from starting
        self.popen_patcher = patch('subprocess.Popen')
        self.mock_popen = self.popen_patcher.start()
        
        # Mock process object with expected behavior
        self.mock_process = MagicMock()
        self.mock_popen.return_value = self.mock_process
        
        # Path for settings
        self.settings_patcher = patch('run_dev.setup_django')
        self.mock_settings_func = self.settings_patcher.start()
        self.mock_settings = MagicMock()
        self.mock_settings.ALLOWED_HOSTS = []
        self.mock_settings_func.return_value = self.mock_settings
        
        # Patch os.environ to prevent actual environment changes
        self.env_patcher = patch.dict('os.environ', {})
        self.env_patcher.start()
        
        # Patch time.sleep to speed up tests
        self.sleep_patcher = patch('time.sleep')
        self.mock_sleep = self.sleep_patcher.start()
        
    def tearDown(self):
        """Clean up after tests."""
        self.log_step("Cleaning up test environment")
        self.run_patcher.stop()
        self.popen_patcher.stop()
        self.settings_patcher.stop()
        self.env_patcher.stop()
        self.sleep_patcher.stop()
        super().tearDown()
    
    def test_ngrok_not_installed(self):
        """Test behavior when ngrok is not installed."""
        self.log_step("Testing behavior when ngrok is not installed")
        
        # Configure mock to simulate ngrok not being found
        self.mock_run.side_effect = subprocess.CalledProcessError(1, 'which ngrok')
        
        # Set the event to avoid blocking
        run_dev.ngrok_ready_event.clear()
        
        # Run the function
        run_dev.run_ngrok()
        
        # Check if the event was set
        self.assert_with_log(
            run_dev.ngrok_ready_event.is_set(),
            "Checking if ngrok_ready_event was set when ngrok is not installed"
        )
    
    def test_ngrok_already_running(self):
        """Test behavior when ngrok is already running."""
        self.log_step("Testing behavior when ngrok is already running")
        
        # Set up ngrok_ready_event for this test
        run_dev.ngrok_ready_event.clear()
        
        # Configure mock to simulate ngrok already running - carefully set up the sequence
        pgrep_response = MagicMock()
        pgrep_response.stdout = "12345\n"
        pgrep_response.returncode = 0
        
        pkill_response = MagicMock()
        pkill_response.returncode = 0
        
        which_response = MagicMock()
        which_response.returncode = 0
        
        # Mock JSON response from ngrok API
        tunnels_json = json.dumps({
            "tunnels": [
                {
                    "name": "command_line",
                    "uri": "/api/tunnels/command_line",
                    "public_url": "https://abcd1234.ngrok.io",
                    "proto": "https",
                    "config": {"addr": "http://localhost:8000", "inspect": True},
                    "metrics": {
                        "conns": {"count": 0, "gauge": 0, "rate1": 0, "rate5": 0, "rate15": 0, "p50": 0, "p90": 0, "p95": 0, "p99": 0},
                        "http": {"count": 0, "rate1": 0, "rate5": 0, "rate15": 0, "p50": 0, "p90": 0, "p95": 0, "p99": 0}
                    }
                }
            ]
        })
        curl_response = MagicMock()
        curl_response.stdout = tunnels_json
        curl_response.returncode = 0
        
        # Set up the sequence of responses
        self.mock_run.side_effect = [pgrep_response, pkill_response, which_response, curl_response]
        
        # Mock update_twilio_webhook to avoid actual API calls
        update_webhook_patcher = patch('run_dev.update_twilio_webhook')
        mock_update_webhook = update_webhook_patcher.start()
        
        try:
            # Patch open function to prevent file writes
            with patch('builtins.open', mock_open()) as mock_file:
                # Run the function
                run_dev.run_ngrok()
                
                # Verify update_twilio_webhook was called with expected URL
                mock_update_webhook.assert_called_once_with("https://abcd1234.ngrok.io")
                
                # Verify ngrok_ready_event was set
                self.assert_with_log(
                    run_dev.ngrok_ready_event.is_set(),
                    "Checking if ngrok_ready_event was set"
                )
                
                # Verify file writes
                self.assert_with_log(
                    mock_file.call_count >= 2,
                    "Checking if files were written when ngrok is started"
                )
        finally:
            update_webhook_patcher.stop()
    
    def test_ngrok_api_empty_response(self):
        """Test behavior when ngrok API returns empty response."""
        self.log_step("Testing behavior when ngrok API returns empty response")
        
        # Configure mock to simulate successful ngrok start but empty API response
        self.mock_run.side_effect = [
            MagicMock(stdout="", returncode=0),  # pgrep returns empty (not running)
            MagicMock(returncode=0),  # which ngrok succeeds
            MagicMock(stdout="", returncode=0),  # First curl attempt returns empty
            MagicMock(stdout="", returncode=0),  # Second curl attempt returns empty
            MagicMock(stdout="", returncode=0),  # Third curl attempt returns empty
            MagicMock(stdout="", returncode=0),  # Fourth curl attempt returns empty
            MagicMock(stdout="", returncode=0)   # Fifth curl attempt returns empty
        ]
        
        # Set the event to avoid blocking
        run_dev.ngrok_ready_event.clear()
        
        # Run the function
        run_dev.run_ngrok()
        
        # Verify that retries occurred
        self.assert_with_log(
            self.mock_run.call_count >= 6,  # 1 for pgrep, 1 for which, and at least 4 for curl
            "Checking if multiple API call attempts were made"
        )
    
    def test_ngrok_successful_retrieval(self):
        """Test successful retrieval of ngrok tunnel URL."""
        self.log_step("Testing successful retrieval of ngrok tunnel URL")
        
        # Configure mock for initial checks
        self.mock_run.side_effect = [
            MagicMock(stdout="", returncode=0),  # pgrep returns empty (not running)
            MagicMock(returncode=0),  # which ngrok succeeds
        ]
        
        # Mock JSON response from ngrok API with a valid tunnel
        tunnels_json = json.dumps({
            "tunnels": [
                {
                    "name": "command_line",
                    "uri": "/api/tunnels/command_line",
                    "public_url": "https://abcd1234.ngrok.io",
                    "proto": "https",
                    "config": {"addr": "http://localhost:8000", "inspect": True},
                    "metrics": {
                        "conns": {"count": 0, "gauge": 0, "rate1": 0, "rate5": 0, "rate15": 0, "p50": 0, "p90": 0, "p95": 0, "p99": 0},
                        "http": {"count": 0, "rate1": 0, "rate5": 0, "rate15": 0, "p50": 0, "p90": 0, "p95": 0, "p99": 0}
                    }
                }
            ]
        })
        # Set the side effect for the third call
        self.mock_run.side_effect = list(self.mock_run.side_effect) + [MagicMock(stdout=tunnels_json, returncode=0)]
        
        # Mock update_twilio_webhook
        update_webhook_patcher = patch('run_dev.update_twilio_webhook')
        mock_update_webhook = update_webhook_patcher.start()
        
        # Patch open function to prevent file writes
        with patch('builtins.open', mock_open()) as mock_file:
            # Run the function
            run_dev.run_ngrok()
            
            # Verify that update_twilio_webhook was called with the correct URL
            mock_update_webhook.assert_called_once_with("https://abcd1234.ngrok.io")
            
            # Verify ALLOWED_HOSTS was updated
            self.assert_in_with_log(
                "abcd1234.ngrok.io",
                self.mock_settings.ALLOWED_HOSTS,
                "Checking if ALLOWED_HOSTS was updated with ngrok hostname"
            )
            
            # Verify environment variables were set
            self.assert_equal_with_log(
                os.environ.get('NGROK_HOST'),
                "abcd1234.ngrok.io",
                "Checking if NGROK_HOST environment variable was set"
            )
            
            self.assert_equal_with_log(
                os.environ.get('NGROK_URL'),
                "https://abcd1234.ngrok.io",
                "Checking if NGROK_URL environment variable was set"
            )
        
        # Clean up
        update_webhook_patcher.stop()
    
    def test_ngrok_no_https_tunnel(self):
        """Test behavior when no HTTPS tunnel is available."""
        self.log_step("Testing behavior when no HTTPS tunnel is available")
        
        # Configure mock for initial checks
        self.mock_run.side_effect = [
            MagicMock(stdout="", returncode=0),  # pgrep returns empty (not running)
            MagicMock(returncode=0),  # which ngrok succeeds
        ]
        
        # Mock JSON response with only HTTP tunnel (no HTTPS)
        tunnels_json = json.dumps({
            "tunnels": [
                {
                    "name": "command_line",
                    "uri": "/api/tunnels/command_line",
                    "public_url": "http://abcd1234.ngrok.io",
                    "proto": "http",
                    "config": {"addr": "http://localhost:8000", "inspect": True},
                    "metrics": {
                        "conns": {"count": 0, "gauge": 0, "rate1": 0, "rate5": 0, "rate15": 0, "p50": 0, "p90": 0, "p95": 0, "p99": 0},
                        "http": {"count": 0, "rate1": 0, "rate5": 0, "rate15": 0, "p50": 0, "p90": 0, "p95": 0, "p99": 0}
                    }
                }
            ]
        })
        # Set the side effect for the third call
        self.mock_run.side_effect = list(self.mock_run.side_effect) + [MagicMock(stdout=tunnels_json, returncode=0)]
        
        # Patch open function to prevent file writes
        with patch('builtins.open', mock_open()) as mock_file:
            # Run the function
            run_dev.run_ngrok()
            
            # Verify no files were written (since no HTTPS tunnel found)
            self.assert_with_log(
                mock_file.call_count == 0,
                "Checking that no files were written when only HTTP tunnel is available"
            )
            
            # Verify ALLOWED_HOSTS was not updated
            self.assert_with_log(
                len(self.mock_settings.ALLOWED_HOSTS) == 0,
                "Checking that ALLOWED_HOSTS was not updated"
            )


if __name__ == '__main__':
    unittest.main()
