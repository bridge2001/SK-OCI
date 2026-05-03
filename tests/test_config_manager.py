"""Unit tests for Configuration Manager module"""

import unittest
import tempfile
import os
from src.config_manager import ConfigManager


class TestConfigManager(unittest.TestCase):
    """Tests for ConfigManager class"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.config_content = """[DEFAULT]
user=ocid1.user.oc1..example
fingerprint=00:11:22:33:44:55:66:77:88:99:aa:bb:cc:dd:ee:ff
key_file=~/.oci/oci_api_key.pem
tenancy=ocid1.tenancy.oc1..example
region=us-phoenix-1
"""
        
        # Create temporary config file
        self.temp_config = tempfile.NamedTemporaryFile(
            mode="w",
            delete=False,
            suffix=".config"
        )
        self.temp_config.write(self.config_content)
        self.temp_config.close()
    
    def tearDown(self):
        """Clean up test fixtures"""
        if os.path.exists(self.temp_config.name):
            os.remove(self.temp_config.name)
    
    def test_load_config_file_success(self):
        """Test successful config file loading"""
        manager = ConfigManager(config_file=self.temp_config.name)
        config = manager.load_config_file()
        
        self.assertEqual(config["user"], "ocid1.user.oc1..example")
        self.assertEqual(config["region"], "us-phoenix-1")
    
    def test_load_config_file_not_found(self):
        """Test config file not found error"""
        manager = ConfigManager(config_file="/nonexistent/config")
        
        with self.assertRaises(FileNotFoundError):
            manager.load_config_file()
    
    def test_load_from_environment(self):
        """Test loading config from environment variables"""
        manager = ConfigManager(config_file=self.temp_config.name)
        manager.load_config_file()  # Load base config first
        
        # Set environment variables
        os.environ["OCI_USER_OCID"] = "ocid1.user.oc1..env_example"
        
        try:
            manager.load_from_environment()
            self.assertEqual(manager.config["user"], "ocid1.user.oc1..env_example")
        finally:
            del os.environ["OCI_USER_OCID"]
    
    def test_get_config(self):
        """Test getting configuration"""
        manager = ConfigManager(config_file=self.temp_config.name)
        manager.load_config_file()
        config = manager.get_config()
        
        self.assertIsInstance(config, dict)
        self.assertIn("user", config)
    
    def test_get_single_value(self):
        """Test getting single config value"""
        manager = ConfigManager(config_file=self.temp_config.name)
        manager.load_config_file()
        
        user = manager.get("user")
        self.assertEqual(user, "ocid1.user.oc1..example")
    
    def test_get_with_default(self):
        """Test getting config value with default"""
        manager = ConfigManager(config_file=self.temp_config.name)
        manager.load_config_file()
        
        value = manager.get("nonexistent", "default_value")
        self.assertEqual(value, "default_value")


class TestConfigValidation(unittest.TestCase):
    """Tests for configuration validation"""
    
    def test_validate_missing_keys(self):
        """Test validation with missing required keys"""
        manager = ConfigManager()
        manager.config = {
            "user": "ocid1.user.oc1..example",
            # Missing other required keys
        }
        
        with self.assertRaises(ValueError):
            manager.validate_config()


if __name__ == "__main__":
    unittest.main()
