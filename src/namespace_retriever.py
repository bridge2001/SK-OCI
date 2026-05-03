"""Retrieve and process OCI tenancy namespace information"""

from typing import Dict, Any
from datetime import datetime
import time
from src.logger import setup_logger
from src.oci_client import OCIClient

logger = setup_logger(__name__)


class NamespaceRetriever:
    """Retrieves tenancy namespace and related information from OCI"""
    
    def __init__(self, oci_client: OCIClient):
        """
        Initialize namespace retriever.
        
        Args:
            oci_client: Authenticated OCIClient instance
        """
        self.oci_client = oci_client
        self.tenancy_data = None
        self.start_time = None
        logger.info("Initializing NamespaceRetriever")
    
    def retrieve_namespace(self, tenancy_id: str) -> Dict[str, Any]:
        """
        Retrieve tenancy namespace and related metadata.
        
        Args:
            tenancy_id: Tenancy OCID
            
        Returns:
            Dictionary containing namespace and metadata
            
        Raises:
            Exception: If retrieval fails
        """
        logger.info("Starting namespace retrieval")
        self.start_time = time.time()
        
        try:
            # Get tenancy information
            print("Fetching OCI tenancy information...")
            logger.info(f"Fetching tenancy information for ID: {tenancy_id[:30]}...")
            
            tenancy_data = self.oci_client.get_tenancy(tenancy_id)
            namespace = tenancy_data.get("namespace")
            
            print(f"✓ Tenancy retrieved: {tenancy_data['name']}")
            print(f"✓ Namespace: {namespace}")
            logger.info(f"Namespace retrieved: {namespace}")
            
            # Get availability domains
            print("\nFetching availability domains...")
            logger.info("Retrieving availability domains")
            
            availability_domains = self.oci_client.list_availability_domains(
                tenancy_data["compartment_id"]
            )
            print(f"✓ Found {len(availability_domains)} availability domain(s)")
            logger.info(f"Retrieved {len(availability_domains)} availability domains")
            
            # Get regions
            print("\nFetching region information...")
            logger.info("Retrieving regions")
            
            regions = self.oci_client.list_regions()
            print(f"✓ Found {len(regions)} region(s)")
            logger.info(f"Retrieved {len(regions)} regions")
            
            # Calculate execution time
            execution_time = time.time() - self.start_time
            
            # Compile results
            result = {
                "metadata": {
                    "version": "1.0",
                    "generated_at": datetime.utcnow().isoformat() + "Z",
                    "execution_time_seconds": round(execution_time, 2),
                },
                "tenancy": {
                    "namespace": namespace,
                    "ocid": tenancy_data["id"],
                    "home_region": tenancy_data["home_region"],
                    "name": tenancy_data["name"],
                    "compartment_id": tenancy_data["compartment_id"],
                },
                "availability_domains": availability_domains,
                "regions": regions,
            }
            
            self.tenancy_data = result
            
            print(f"\n✓ Data retrieval completed in {execution_time:.2f} seconds")
            logger.info(f"Namespace retrieval completed in {execution_time:.2f} seconds")
            
            return result
            
        except Exception as e:
            logger.error(f"Namespace retrieval failed: {str(e)}")
            print(f"✗ Error retrieving namespace: {str(e)}")
            raise
    
    def get_namespace(self) -> str:
        """
        Get the retrieved namespace string.
        
        Returns:
            Namespace string
            
        Raises:
            ValueError: If namespace not retrieved yet
        """
        if not self.tenancy_data:
            raise ValueError("Namespace not retrieved yet. Call retrieve_namespace() first.")
        
        namespace = self.tenancy_data["tenancy"]["namespace"]
        logger.debug(f"Returning namespace: {namespace}")
        return namespace
    
    def get_data(self) -> Dict[str, Any]:
        """
        Get all retrieved data.
        
        Returns:
            Complete data dictionary
            
        Raises:
            ValueError: If namespace not retrieved yet
        """
        if not self.tenancy_data:
            raise ValueError("Data not retrieved yet. Call retrieve_namespace() first.")
        
        return self.tenancy_data.copy()
