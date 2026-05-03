"""SK-OCI Tenancy Report Generator - OCI Namespace and Report Generation Tool"""

__version__ = "1.0.0"
__author__ = "SK-OCI Development Team"

from src.logger import setup_logger
from src.config_manager import ConfigManager
from src.oci_client import OCIClient
from src.namespace_retriever import NamespaceRetriever

__all__ = [
    "setup_logger",
    "ConfigManager",
    "OCIClient",
    "NamespaceRetriever",
]
