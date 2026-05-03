"""Main entry point for SK-OCI application"""

import sys
import argparse
from typing import Optional
from src.logger import setup_logger
from src.config_manager import ConfigManager
from src.oci_client import OCIClient
from src.namespace_retriever import NamespaceRetriever

logger = setup_logger(__name__)


def parse_arguments() -> argparse.Namespace:
    """
    Parse command-line arguments.
    
    Returns:
        Parsed arguments
    """
    parser = argparse.ArgumentParser(
        description="SK-OCI Tenancy Namespace Report Generator",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python -m src.main
  python -m src.main --config ~/.oci/config
  python -m src.main --profile DEFAULT --log-level DEBUG
        """,
    )
    
    parser.add_argument(
        "--config",
        type=str,
        default=None,
        help="Path to OCI config file (default: ~/.oci/config)",
    )
    
    parser.add_argument(
        "--profile",
        type=str,
        default="DEFAULT",
        help="OCI profile name to use (default: DEFAULT)",
    )
    
    parser.add_argument(
        "--log-level",
        type=str,
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        default="INFO",
        help="Logging level (default: INFO)",
    )
    
    parser.add_argument(
        "--version",
        action="version",
        version="SK-OCI v1.0.0",
    )
    
    return parser.parse_args()


def main(config_file: Optional[str] = None, profile: str = "DEFAULT", 
         log_level: str = "INFO") -> int:
    """
    Main application function.
    
    Args:
        config_file: Path to OCI config file
        profile: OCI profile name
        log_level: Logging level
        
    Returns:
        Exit code (0 for success, 1 for failure)
    """
    # Setup logger
    logger = setup_logger(__name__, log_level=log_level)
    
    try:
        print("\n" + "=" * 60)
        print("SK-OCI Tenancy Namespace Report Generator")
        print("=" * 60 + "\n")
        
        # Load configuration
        print("Loading configuration...")
        logger.info(f"Loading configuration from profile: {profile}")
        
        config_manager = ConfigManager(config_file=config_file, profile=profile)
        config = config_manager.load(use_env=True)
        
        print("✓ Configuration loaded successfully")
        logger.info("Configuration loaded successfully")
        
        # Authenticate with OCI
        print("\nAuthenticating with OCI...")
        logger.info("Starting OCI authentication")
        
        oci_client = OCIClient(config)
        oci_client.authenticate()
        
        print("✓ OCI authentication successful")
        logger.info("OCI authentication successful")
        
        # Retrieve namespace
        print("\n" + "-" * 60)
        print("Retrieving Tenancy Information")
        print("-" * 60 + "\n")
        
        retriever = NamespaceRetriever(oci_client)
        data = retriever.retrieve_namespace(config["tenancy"])
        
        # Display results
        print("\n" + "-" * 60)
        print("Results")
        print("-" * 60 + "\n")
        
        namespace = retriever.get_namespace()
        print(f"Tenancy Namespace: {namespace}")
        print(f"Tenancy Name: {data['tenancy']['name']}")
        print(f"Tenancy OCID: {data['tenancy']['ocid']}")
        print(f"Home Region: {data['tenancy']['home_region']}")
        print(f"\nAvailability Domains:")
        for ad in data["availability_domains"]:
            print(f"  - {ad['name']}")
        print(f"\nRegions:")
        for region in data["regions"]:
            home_indicator = " (Home)" if region["is_home_region"] else ""
            print(f"  - {region['name']}{home_indicator}")
        
        print(f"\nExecution Time: {data['metadata']['execution_time_seconds']} seconds")
        print("\n" + "=" * 60)
        print("✓ Operation completed successfully")
        print("=" * 60 + "\n")
        
        logger.info("Application completed successfully")
        return 0
        
    except FileNotFoundError as e:
        logger.error(f"Configuration file error: {str(e)}")
        print(f"\n✗ Error: {str(e)}")
        print("\nPlease ensure OCI config file exists at ~/.oci/config")
        return 1
        
    except ValueError as e:
        logger.error(f"Configuration error: {str(e)}")
        print(f"\n✗ Configuration error: {str(e)}")
        print("\nPlease check your OCI configuration and credentials")
        return 1
        
    except Exception as e:
        logger.error(f"Application error: {str(e)}", exc_info=True)
        print(f"\n✗ Error: {str(e)}")
        print("\nCheck the logs for more details")
        return 1


if __name__ == "__main__":
    args = parse_arguments()
    sys.exit(main(
        config_file=args.config,
        profile=args.profile,
        log_level=args.log_level,
    ))
