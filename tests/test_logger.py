"""Unit tests for Logger module"""

import unittest
import tempfile
import os
import logging
from src.logger import setup_logger, redact_credentials


class TestLogger(unittest.TestCase):
    """Tests for logger setup"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        """Clean up test fixtures"""
        # Remove log files
        if os.path.exists(self.temp_dir):
            for file in os.listdir(self.temp_dir):
                os.remove(os.path.join(self.temp_dir, file))
            os.rmdir(self.temp_dir)
    
    def test_setup_logger_creates_logger(self):
        """Test that setup_logger creates a logger"""
        logger = setup_logger("test_logger", log_dir=self.temp_dir)
        
        self.assertIsNotNone(logger)
        self.assertIsInstance(logger, logging.Logger)
    
    def test_setup_logger_default_level(self):
        """Test logger with default INFO level"""
        logger = setup_logger("test", log_dir=self.temp_dir)
        
        self.assertEqual(logger.level, logging.INFO)
    
    def test_setup_logger_debug_level(self):
        """Test logger with DEBUG level"""
        logger = setup_logger("test", log_level="DEBUG", log_dir=self.temp_dir)
        
        self.assertEqual(logger.level, logging.DEBUG)
    
    def test_setup_logger_invalid_level(self):
        """Test logger with invalid level"""
        with self.assertRaises(ValueError):
            setup_logger("test", log_level="INVALID", log_dir=self.temp_dir)
    
    def test_logger_creates_directory(self):
        """Test that logger creates log directory"""
        log_dir = os.path.join(self.temp_dir, "logs")
        logger = setup_logger("test", log_dir=log_dir)
        
        self.assertTrue(os.path.exists(log_dir))


class TestCredentialRedaction(unittest.TestCase):
    """Tests for credential redaction"""
    
    def test_redact_ocid(self):
        """Test redaction of OCID"""
        message = "Using OCID ocid1.tenancy.oc1..example"
        redacted = redact_credentials(message)
        
        self.assertIn("***REDACTED***", redacted)
        self.assertNotIn("ocid1.", redacted)
    
    def test_redact_multiple(self):
        """Test redaction of multiple patterns"""
        message = "User: ocid1.user.oc1..xyz, Fingerprint: aa:bb:cc:dd"
        redacted = redact_credentials(message)
        
        self.assertIn("***REDACTED***", redacted)
    
    def test_no_redaction_needed(self):
        """Test message with nothing to redact"""
        message = "This is a normal message"
        redacted = redact_credentials(message)
        
        self.assertEqual(message, redacted)


if __name__ == "__main__":
    unittest.main()
