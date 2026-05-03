"""OCI SDK wrapper for authentication and API interactions"""

import time
from typing import Dict, Any, Optional
import oci
from oci.config import from_file
from oci.identity import IdentityClient
from src.logger import setup_logger

logger = setup_logger(__name__)


class OCIClient:
    """Wrapper around OCI SDK for consistent authentication and API calls"""
    
    MAX_RETRIES = 3
    RETRY_BACKOFF = 2  # Exponential backoff multiplier
    
    def __init__(self, config_dict: Dict[str, str]):
        """
        Initialize OCI client.
        
        Args:
            config_dict: Configuration dictionary with OCI credentials
            
        Raises:
            ValueError: If configuration is invalid
        """
        self.config_dict = config_dict
        self.identity_client = None
        logger.info("Initializing OCI Client")
    
    def authenticate(self) -> bool:
        """
        Authenticate with OCI using provided configuration.
        
        Returns:
            True if authentication successful
            
        Raises:
            Exception: If authentication fails
        """
        try:
            logger.info("Attempting OCI authentication")
            
            # Create OCI config from dictionary
            oci_config = oci.config.validate_config(self.config_dict)
            
            # Initialize Identity Client
            self.identity_client = IdentityClient(oci_config)
            
            logger.info("OCI authentication successful")
            return True
            
        except Exception as e:
            logger.error(f"OCI authentication failed: {str(e)}")
            raise
    
    def _retry_api_call(self, api_call_func, *args, **kwargs) -> Any:
        """
        Execute API call with retry logic and exponential backoff.
        
        Args:
            api_call_func: Function to call
            *args: Positional arguments for the function
            **kwargs: Keyword arguments for the function
            
        Returns:
            Result of the API call
            
        Raises:
            Exception: If all retries fail
        """
        last_exception = None
        
        for attempt in range(self.MAX_RETRIES):
            try:
                logger.debug(f"API call attempt {attempt + 1}/{self.MAX_RETRIES}")
                result = api_call_func(*args, **kwargs)
                logger.debug("API call successful")
                return result
                
            except oci.exceptions.ServiceError as e:
                last_exception = e
                
                # Don't retry for 401/403 (auth errors)
                if e.status in [401, 403]:
                    logger.error(f"Authentication error (status {e.status}): {e.message}")
                    raise
                
                # Don't retry for 404 (not found)
                if e.status == 404:
                    logger.error(f"Resource not found (status {e.status}): {e.message}")
                    raise
                
                if attempt < self.MAX_RETRIES - 1:
                    wait_time = self.RETRY_BACKOFF ** attempt
                    logger.warning(
                        f"API call failed (attempt {attempt + 1}): {e.message}. "
                        f"Retrying in {wait_time}s..."
                    )
                    time.sleep(wait_time)
                else:
                    logger.error(f"API call failed after {self.MAX_RETRIES} attempts")
                    
            except Exception as e:
                logger.error(f"Unexpected error during API call: {str(e)}")
                raise
        
        if last_exception:
            raise last_exception
    
    def get_tenancy(self, tenancy_id: str) -> Dict[str, Any]:
        """
        Retrieve tenancy information.
        
        Args:
            tenancy_id: Tenancy OCID
            
        Returns:
            Tenancy information dictionary
            
        Raises:
            Exception: If API call fails
        """
        logger.info(f"Fetching tenancy information for: {tenancy_id[:20]}...")
        
        try:
            response = self._retry_api_call(
                self.identity_client.get_tenancy,
                tenancy_id=tenancy_id
            )
            
            tenancy_data = {
                "id": response.data.id,
                "name": response.data.name,
                "namespace": response.data.namespace,
                "compartment_id": response.data.compartment_id,
                "home_region": response.data.home_region_key,
                "freeform_tags": response.data.freeform_tags or {},
                "defined_tags": response.data.defined_tags or {},
            }
            
            logger.info(f"Successfully retrieved tenancy: {tenancy_data['name']}")
            logger.debug(f"Tenancy namespace: {tenancy_data['namespace']}")
            
            return tenancy_data
            
        except Exception as e:
            logger.error(f"Failed to retrieve tenancy: {str(e)}")
            raise
    
    def list_availability_domains(self, compartment_id: str) -> list:
        """
        List availability domains in a compartment.
        
        Args:
            compartment_id: Compartment OCID
            
        Returns:
            List of availability domain dictionaries
            
        Raises:
            Exception: If API call fails
        """
        logger.info("Fetching availability domains")
        
        try:
            response = self._retry_api_call(
                self.identity_client.list_availability_domains,
                compartment_id=compartment_id
            )
            
            domains = [
                {
                    "name": ad.name,
                    "compartment_id": ad.compartment_id,
                }
                for ad in response.data
            ]
            
            logger.info(f"Retrieved {len(domains)} availability domains")
            return domains
            
        except Exception as e:
            logger.error(f"Failed to list availability domains: {str(e)}")
            raise
    
    def list_regions(self) -> list:
        """
        List all regions.
        
        Returns:
            List of region dictionaries
            
        Raises:
            Exception: If API call fails
        """
        logger.info("Fetching regions")
        
        try:
            response = self._retry_api_call(
                self.identity_client.list_region_subscriptions,
                tenancy_id=self.config_dict["tenancy"]
            )
            
            regions = [
                {
                    "key": region.region_key,
                    "name": region.region_name,
                    "status": region.status,
                    "is_home_region": region.is_home_region,
                }
                for region in response.data
            ]
            
            logger.info(f"Retrieved {len(regions)} regions")
            return regions
            
        except Exception as e:
            logger.error(f"Failed to list regions: {str(e)}")
            raise
    
    def is_authenticated(self) -> bool:
        """
        Check if client is authenticated.
        
        Returns:
            True if authenticated, False otherwise
        """
        return self.identity_client is not None
