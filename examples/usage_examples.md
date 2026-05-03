# Usage Examples - SK-OCI Tenancy Namespace Report Generator

## Basic Usage

### Run with default configuration
```bash
python -m src.main
```

This will use the default OCI configuration file located at `~/.oci/config` with the `DEFAULT` profile.

### Run with specific profile
```bash
python -m src.main --profile production
```

### Run with custom config file
```bash
python -m src.main --config /path/to/custom/oci/config
```

## Logging and Debugging

### Run with DEBUG logging
```bash
python -m src.main --log-level DEBUG
```

This will output detailed debug information to both console and log file.

### Check log files
Log files are created in the `logs/` directory:
```bash
cat logs/sk-oci_20260503.log
```

### Run with different log levels
```bash
python -m src.main --log-level INFO     # Default information
python -m src.main --log-level WARNING  # Only warnings and errors
python -m src.main --log-level ERROR    # Only errors
```

## Advanced Usage

### Using environment variables
Set your OCI configuration via environment variables:
```bash
export OCI_USER_OCID=ocid1.user.oc1..xxxxx
export OCI_TENANCY_OCID=ocid1.tenancy.oc1..xxxxx
export OCI_FINGERPRINT=xx:xx:xx:xx:xx:xx
export OCI_KEY_FILE=~/.oci/oci_api_key.pem
export OCI_REGION=us-phoenix-1

python -m src.main
```

### Batch execution with logging
```bash
python -m src.main --profile DEFAULT --log-level INFO > /tmp/oci_output.txt 2>&1
echo "Exit code: $?"
```

### Using in scripts
```bash
#!/bin/bash
if python -m src.main --log-level ERROR; then
    echo "Success"
else
    echo "Failed with exit code: $?"
fi
```

## Troubleshooting

### Authentication fails
1. Check your OCI config file exists: `ls -la ~/.oci/config`
2. Check your private key file exists: `ls -la ~/.oci/oci_api_key.pem`
3. Verify fingerprint matches in OCI Console
4. Run with DEBUG logging: `python -m src.main --log-level DEBUG`

### Permission denied errors
1. Ensure your OCI user has appropriate IAM policies
2. Check tenancy permissions for Identity service access
3. Review logs for specific permission errors

### Configuration not found
```bash
# Copy example config to ~/.oci/config
cp examples/config_example.txt ~/.oci/config
# Edit with your credentials
nano ~/.oci/config
```

## Integration Examples

### Cron Job
```bash
# Add to crontab (every day at 2 AM)
0 2 * * * /usr/bin/python3 /path/to/sk-oci/src/main.py --log-level INFO >> /var/log/sk-oci.log 2>&1
```

### Docker
```bash
# Build image
docker build -t sk-oci:1.0 .

# Run container
docker run --rm \
  -v ~/.oci:/root/.oci \
  -v /tmp/reports:/app/reports \
  sk-oci:1.0 \
  python -m src.main --log-level INFO
```

### Python Script Integration
```python
from src.config_manager import ConfigManager
from src.oci_client import OCIClient
from src.namespace_retriever import NamespaceRetriever

# Load configuration
config_manager = ConfigManager()
config = config_manager.load()

# Create client and retrieve namespace
oci_client = OCIClient(config)
oci_client.authenticate()

retriever = NamespaceRetriever(oci_client)
data = retriever.retrieve_namespace(config["tenancy"])

# Use the data
namespace = retriever.get_namespace()
print(f"Namespace: {namespace}")
```

## Performance Optimization

### For large tenancies
- Use DEBUG logging only when needed (impacts performance)
- Run during off-peak hours
- Consider caching results

### Parallel execution
Multiple profiles can be run in parallel:
```bash
python -m src.main --profile prod1 &
python -m src.main --profile prod2 &
python -m src.main --profile prod3 &
wait
```
