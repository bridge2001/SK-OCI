"""Configuration management for OCI credentials and application settings"""

import os
from configparser import ConfigParser
from typing import Dict, Optional
from src.logger import setup_logger

logger = setup_logger(__name__)


class ConfigManager:
    """Manages OCI configuration from multiple sources"""
    
    def __init__(self, config_file: Optional[str] = None, profile: str = "DEFAULT"):
        """
        Initialize configuration manager.
        
        Args:
            config_file: Path to OCI config file (defaults to ~/.oci/config)
            profile: OCI profile name to use
        """
        self.config_file = config_file or os.path.expanduser("~/.oci/config")
        self.profile = profile
        self.config = {}
        logger.info(f"Initializing ConfigManager with profile: {profile}")
    
    def load_config_file(self) -> Dict[str, str]:
        """
        Load configuration from OCI config file.
        
        Returns:
            Dictionary of configuration values
            
        Raises:
            FileNotFoundError: If config file doesn't exist
            ValueError: If profile not found in config
        """
        if not os.path.exists(self.config_file):
            logger.error(f"Config file not found: {self.config_file}")
            raise FileNotFoundError(f"OCI config file not found: {self.config_file}")
        
        logger.info(f"Loading configuration from: {self.config_file}")
        
        parser = ConfigParser()
        parser.read(self.config_file)
        
        if self.profile not in parser.sections():
            logger.error(f"Profile '{self.profile}' not found in config file")
            raise ValueError(f"Profile '{self.profile}' not found in {self.config_file}")
        
        self.config = dict(parser.items(self.profile))
        logger.info(f"Successfully loaded configuration for profile: {self.profile}")
        logger.debug(f"Config keys: {list(self.config.keys())}")
        
        return self.config
    
    def load_from_environment(self) -> Dict[str, str]:
        """
        Load configuration from environment variables.
        
        Expected environment variables:
        - OCI_CONFIG_FILE: Path to config file
        - OCI_PROFILE: Profile name
        - OCI_USER_OCID: User OCID
        - OCI_TENANCY_OCID: Tenancy OCID
        - OCI_FINGERPRINT: Key fingerprint
        - OCI_KEY_FILE: Private key file path
        - OCI_REGION: Region
        
        Returns:
            Dictionary of configuration values
        """
        logger.info("Loading configuration from environment variables")
        
        env_config = {}
        env_keys = {
            "OCI_USER_OCID": "user",
            "OCI_TENANCY_OCID": "tenancy",
            "OCI_FINGERPRINT": "fingerprint",
            "OCI_KEY_FILE": "key_file",
            "OCI_REGION": "region",
        }
        
        for env_var, config_key in env_keys.items():
            if env_var in os.environ:
                env_config[config_key] = os.environ[env_var]
                logger.debug(f"Set {config_key} from {env_var}")
        
        self.config.update(env_config)
        logger.info(f"Loaded {len(env_config)} values from environment")
        
        return self.config
    
    def validate_config(self) -> bool:
        """
        Validate that required configuration values are present.
        
        Returns:
            True if configuration is valid
            
        Raises:
            ValueError: If required configuration is missing
        """
        required_keys = {"user", "tenancy", "fingerprint", "key_file", "region"}
        missing_keys = required_keys - set(self.config.keys())
        
        if missing_keys:
            logger.error(f"Missing required configuration: {missing_keys}")
            raise ValueError(f"Missing required configuration: {missing_keys}")
        
        # Validate key file exists
        key_file = self.config.get("key_file")
        if not os.path.exists(key_file):
            logger.error(f"Private key file not found: {key_file}")
            raise FileNotFoundError(f"Private key file not found: {key_file}")
        
        logger.info("Configuration validation passed")
        return True
    
    def get_config(self) -> Dict[str, str]:
        """
        Get the current configuration dictionary.
        
        Returns:
            Configuration dictionary
        """
        return self.config.copy()
    
    def get(self, key: str, default: Optional[str] = None) -> Optional[str]:
        """
        Get a configuration value.
        
        Args:
            key: Configuration key
            default: Default value if key not found
            
        Returns:
            Configuration value or default
        """
        return self.config.get(key, default)
    
    def load(self, use_env: bool = True) -> Dict[str, str]:
        """
        Load configuration from file and optionally from environment.
        
        Args:
            use_env: Whether to also load from environment variables
            
        Returns:
            Complete configuration dictionary
            
        Raises:
            FileNotFoundError: If config file doesn't exist
            ValueError: If configuration is invalid
        """
        logger.info("Starting configuration load sequence")
        
        # Load from config file
        self.load_config_file()
        
        # Load from environment variables (overwrites file config)
        if use_env:
            self.load_from_environment()
        
        # Validate configuration
        self.validate_config()
        
        return self.get_config()
