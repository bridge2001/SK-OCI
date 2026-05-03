"""Unit tests for OCI Client module"""

import unittest
from unittest import mock
import oci
from src.oci_client import OCIClient


class TestOCIClient(unittest.TestCase):
    """Tests for OCIClient class"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.config = {
            "user": "ocid1.user.oc1..example",
            "fingerprint": "00:11:22:33:44:55:66:77:88:99:aa:bb:cc:dd:ee:ff",
            "key_file": "/path/to/key.pem",
            "tenancy": "ocid1.tenancy.oc1..example",
            "region": "us-phoenix-1",
        }
        self.client = OCIClient(self.config)
    
    @mock.patch("src.oci_client.IdentityClient")
    @mock.patch("src.oci_client.oci.config.validate_config")
    def test_authenticate_success(self, mock_validate, mock_client_class):
        """Test successful authentication"""
        mock_validate.return_value = self.config
        mock_client_instance = mock.Mock()
        mock_client_class.return_value = mock_client_instance
        
        result = self.client.authenticate()
        
        self.assertTrue(result)
        self.assertIsNotNone(self.client.identity_client)
    
    @mock.patch("src.oci_client.IdentityClient")
    @mock.patch("src.oci_client.oci.config.validate_config")
    def test_authenticate_failure(self, mock_validate, mock_client_class):
        """Test authentication failure"""
        mock_validate.side_effect = ValueError("Invalid config")
        
        with self.assertRaises(ValueError):
            self.client.authenticate()
    
    def test_is_authenticated_false(self):
        """Test is_authenticated when not authenticated"""
        self.assertFalse(self.client.is_authenticated())
    
    @mock.patch("src.oci_client.IdentityClient")
    @mock.patch("src.oci_client.oci.config.validate_config")
    def test_is_authenticated_true(self, mock_validate, mock_client_class):
        """Test is_authenticated when authenticated"""
        mock_validate.return_value = self.config
        mock_client_instance = mock.Mock()
        mock_client_class.return_value = mock_client_instance
        
        self.client.authenticate()
        self.assertTrue(self.client.is_authenticated())
    
    def test_retry_logic_success(self):
        """Test retry logic with eventual success"""
        call_count = 0
        
        def side_effect(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            if call_count < 2:
                error = oci.exceptions.ServiceError(
                    status=500,
                    code="InternalServerError",
                    message="Temporary error"
                )
                raise error
            return "success"
        
        result = self.client._retry_api_call(side_effect)
        self.assertEqual(result, "success")
        self.assertEqual(call_count, 2)
    
    def test_retry_logic_permanent_failure(self):
        """Test retry logic with permanent failure"""
        def side_effect(*args, **kwargs):
            error = oci.exceptions.ServiceError(
                status=401,
                code="Unauthorized",
                message="Invalid credentials"
            )
            raise error
        
        with self.assertRaises(oci.exceptions.ServiceError):
            self.client._retry_api_call(side_effect)


class TestRetryBackoff(unittest.TestCase):
    """Tests for retry backoff functionality"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.config = {
            "user": "ocid1.user.oc1..example",
            "fingerprint": "00:11:22:33:44:55:66:77:88:99:aa:bb:cc:dd:ee:ff",
            "key_file": "/path/to/key.pem",
            "tenancy": "ocid1.tenancy.oc1..example",
            "region": "us-phoenix-1",
        }
        self.client = OCIClient(self.config)
    
    def test_backoff_calculation(self):
        """Test exponential backoff calculation"""
        # First retry: 2^0 = 1 second
        # Second retry: 2^1 = 2 seconds
        expected_backoffs = [1, 2]
        
        for attempt, expected in enumerate(expected_backoffs):
            calculated = self.client.RETRY_BACKOFF ** attempt
            self.assertEqual(calculated, expected)


if __name__ == "__main__":
    unittest.main()
