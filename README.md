# CPVS Monitoring API Runner

A Python script to monitor CPVS Services APIs by calling all monitoring endpoints in parallel and generating comprehensive response reports.

## Features

- ✅ **Parallel Execution**: Calls all APIs simultaneously using ThreadPoolExecutor
- ✅ **Comprehensive Reporting**: Generates detailed JSON reports with status, response times, and results
- ✅ **Error Handling**: Robust error handling with timeout and retry support
- ✅ **Configurable**: Easy-to-modify JSON configuration for all API endpoints
- ✅ **Console Summary**: Beautiful console output with success/failure indicators
- ✅ **Performance Metrics**: Tracks response times, success rates, and other metrics

## Monitored APIs

This script monitors the following CPVS Services APIs:

1. **Fund-Value-Exp** - Fund Value Export API
2. **Fund-Value-Reload** - Fund Value Reload API
3. **LTC_COSTS** - LTC Costs API
4. **LTC-Costs-Load** - LTC Costs Load API (POST)
5. **Producer-Search-P1.0** - Producer Search API Version 1.0
6. **Producer-Search-withEmail-P1.0** - Producer Search with Email API Version 1.0
7. **Producer-Search-P2.0** - Producer Search API Version 2.0
8. **Producer-Search-withEmail-P2.0** - Producer Search with Email API Version 2.0
9. **Producer-With-Mock** - Producer Mock API

## Installation

### Prerequisites

- Python 3.7 or higher
- pip (Python package installer)

### Setup

1. Clone the repository:
```bash
git clone https://github.com/T93UNKL/cpvs-monitoring-api-runner.git
cd cpvs-monitoring-api-runner
```

2. Install required dependencies:
```bash
pip install -r requirements.txt
```

## Configuration

The `config.json` file contains all API endpoint configurations:

```json
{
  "base_url": "https://{{cpvs.services.domain}}",
  "monitoring_apis": [
    {
      "name": "Fund-Value-Exp",
      "method": "GET",
      "endpoint": "/fundvalue-nyl-exp/api/fundUnitValues",
      "params": { "productUnitValueCd": "C18" }
    }
  ],
  "timeout": 30,
  "retry_attempts": 3
}
```

### Configuration Parameters

- `base_url`: Base URL template with domain placeholder
- `monitoring_apis`: Array of API configurations
- `timeout`: Request timeout in seconds (default: 30)
- `retry_attempts`: Number of retry attempts for failed requests

## Usage

### Basic Usage

```bash
python monitor_apis.py --domain <your-domain>
```

### Advanced Usage

```bash
# Specify custom output file
python monitor_apis.py --domain example.com --output my_report.json

# Adjust number of parallel workers
python monitor_apis.py --domain example.com --workers 5

# Use custom configuration file
python monitor_apis.py --domain example.com --config custom_config.json
```

### Command-Line Arguments

| Argument | Required | Default | Description |
|----------|----------|---------|-------------|
| `--domain` | Yes | - | Domain for CPVS services (e.g., example.com) |
| `--output` | No | monitoring_report.json | Output file for JSON report |
| `--workers` | No | 10 | Number of parallel workers |
| `--config` | No | config.json | Configuration file path |

## Output

### Console Output

The script prints a beautiful summary to the console:

```
================================================================================
 CPVS MONITORING API REPORT
================================================================================

Base URL: https://example.com
Execution Time: 2025-12-02T11:30:00

Total APIs: 9
Successful: 8
Failed: 1
Success Rate: 88.89%
Average Response Time: 234.56 ms

--------------------------------------------------------------------------------
 INDIVIDUAL API RESULTS
--------------------------------------------------------------------------------

✓ Fund-Value-Exp
   Method: GET
   Endpoint: /fundvalue-nyl-exp/api/fundUnitValues
   Status: SUCCESS
   HTTP Status: 200
   Response Time: 150.23 ms

✗ Producer-Search-P1.0
   Method: GET
   Endpoint: /producer-nyl-exp/api/1.0/producerProfile
   Status: TIMEOUT
   Error: Request timed out
```

### JSON Report

The script generates a detailed JSON report:

```json
{
  "summary": {
    "total_apis": 9,
    "successful": 8,
    "failed": 1,
    "success_rate": "88.89%",
    "average_response_time_ms": 234.56,
    "execution_timestamp": "2025-12-02T11:30:00",
    "base_url": "https://example.com"
  },
  "detailed_results": [
    {
      "name": "Fund-Value-Exp",
      "endpoint": "/fundvalue-nyl-exp/api/fundUnitValues",
      "method": "GET",
      "url": "https://example.com/fundvalue-nyl-exp/api/fundUnitValues",
      "description": "Fund Value Export API",
      "timestamp": "2025-12-02T11:30:00",
      "status": "SUCCESS",
      "status_code": 200,
      "response_time_ms": 150.23,
      "response_size_bytes": 1024,
      "content_type": "application/json",
      "response_data": { ... }
    }
  ]
}
```

## Exit Codes

- `0`: All APIs succeeded
- `1`: One or more APIs failed

## Error Handling

The script handles various error scenarios:

- **Timeout**: Request exceeds configured timeout
- **Connection Error**: Unable to connect to the API
- **HTTP Errors**: Non-200 status codes are captured
- **JSON Parse Errors**: Invalid JSON responses are handled gracefully

## Logging

The script uses Python's logging module to provide real-time feedback:

```
2025-12-02 11:30:00 - INFO - Base URL set to: https://example.com
2025-12-02 11:30:00 - INFO - Starting monitoring of 9 APIs with 10 parallel workers
2025-12-02 11:30:00 - INFO - Calling Fund-Value-Exp (GET https://example.com/fundvalue-nyl-exp/api/fundUnitValues)
2025-12-02 11:30:01 - INFO - Fund-Value-Exp: SUCCESS (Status: 200, Time: 150.23ms)
```

## Customization

### Adding New APIs

To add a new API to monitor, edit `config.json`:

```json
{
  "name": "New-API",
  "method": "GET",
  "endpoint": "/new-api/endpoint",
  "params": {
    "param1": "value1"
  },
  "description": "Description of the new API"
}
```

### Modifying Parameters

Update the `params` object in the API configuration to change query parameters.

## Use Cases

- **Health Monitoring**: Regular health checks of all CPVS services
- **Performance Testing**: Track response times and identify slow endpoints
- **Integration Testing**: Verify all APIs are functioning after deployments
- **Dashboard Reporting**: Generate data for monitoring dashboards
- **Alerting**: Exit codes can trigger alerts in CI/CD pipelines

## Troubleshooting

### Common Issues

1. **ImportError: No module named 'requests'**
   - Solution: Run `pip install -r requirements.txt`

2. **FileNotFoundError: config.json not found**
   - Solution: Ensure `config.json` exists in the same directory

3. **Connection timeout errors**
   - Solution: Check network connectivity and increase timeout in config.json

4. **Permission denied when writing report**
   - Solution: Check file permissions or specify a different output path

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is open source and available for use.

## Author

Created for CPVS Services monitoring

## Support

For issues or questions, please create an issue in the GitHub repository.
