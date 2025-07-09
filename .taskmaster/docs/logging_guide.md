# Firecrawl Logging Guide

## Overview
Firecrawl provides comprehensive logging for all scraping and crawling operations. This guide explains how to find, interpret, and use these logs to monitor scraping activities and troubleshoot issues.

## Log Locations

### Docker Environment
When running Firecrawl in Docker (the default setup), logs are available through multiple channels:

1. **Docker Logs** (Real-time streaming):
   ```bash
   docker-compose logs -f firecrawl-streamlit-dev
   ```
   This shows real-time logs from the Streamlit app container, including all scraping operations, API requests, and errors.

2. **Container Log Files**:
   Logs are now stored in rotating log files within the container at:
   ```
   /app/logs/firecrawl_YYYYMMDD_HHMMSS.log
   ```
   These files contain detailed logs with timestamps, log levels, and contextual information.

3. **Accessing Log Files from Host**:
   To copy log files from the container to your host machine:
   ```bash
   docker cp firecrawl-streamlit-dev:/app/logs ./local_logs
   ```
   This will copy all log files to a `local_logs` directory in your current location.

### Local Environment
If running outside Docker:

1. **Console Output**:
   All logs are printed to the console/terminal.

2. **Python Logging**:
   The application uses Python's standard logging module with the following configuration:
   ```python
   logging.basicConfig(
       level=logging.INFO,
       format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
   )
   ```

## Log Categories & Levels

### Logging Levels
Firecrawl uses the following logging levels:

- **INFO** (Default): General operational information
  - Successful API connections
  - Scraping progress
  - Content extraction statistics
  - Method selection decisions

- **WARNING**: Potential issues that don't stop execution
  - Fallback to alternative methods
  - API response format mismatches
  - Content extraction challenges
  - Non-fatal API errors

- **ERROR**: Critical issues preventing successful operation
  - API connection failures
  - Authentication errors
  - Fatal scraping errors

### Important Log Messages

#### Scraping Initiation
```
INFO - Starting Google Codelabs tutorial scrape: [URL]
INFO - Will attempt to scrape up to [N] pages with hash-based pagination
```

#### Method Selection
```
INFO - Attempting SPA-aware scraping for page [N] of [URL]
WARNING - SPA navigation failed for page [N]: [Error], trying fallback
INFO - Using fallback direct scraping for [URL]
INFO - Using direct HTML extraction for Google Codelabs: [URL]
```

#### Content Extraction
```
INFO - Found [N] content elements with selector '[SELECTOR]'
INFO - Using content from selector '[SELECTOR]': [N] chars
INFO - Generated markdown: [N] chars
INFO - Successfully scraped page [N]: [N] characters
```

#### API Issues
```
WARNING - API error: [ERROR_MESSAGE]
WARNING - Failed to parse Firecrawl error response as JSON. Status code: [CODE]
```

#### Completion
```
INFO - Google Codelabs scraping completed: [N] pages scraped successfully
INFO - Total processing time: [N] seconds
```

## Monitoring Scraping Activity in Real-Time

For real-time monitoring of Firecrawl scraping operations:

1. Open a terminal window
2. Run:
   ```bash
   docker-compose logs -f firecrawl-streamlit-dev
   ```
3. Keep this window open while performing scraping operations through the Streamlit UI

## Troubleshooting Common Issues

### API Authentication Issues
Look for:
```
ERROR - Failed to initialize Firecrawl client: Authentication failed
ERROR - API key not valid or missing
```
**Solution**: Check that your `FIRECRAWL_API_KEY` is correctly set in the `.env` file.

### SPA Navigation Failures
Look for:
```
WARNING - SPA navigation failed for page [N]: [Error], trying fallback
```
**Solution**: The application will automatically fall back to direct HTML extraction for Google Codelabs sites, which has proven to be more reliable.

### Content Extraction Issues
Look for:
```
WARNING - No substantial content found
WARNING - Content too short or minimal
```
**Solution**: 
- Try adjusting selectors in the `_scrape_codelabs_fallback` method
- For non-Codelabs sites, try using different selectors or approaches

### Docker Permission Issues
Look for:
```
ERROR - Permission denied: '/home/appuser'
```
**Solution**: Ensure the Docker environment has the correct environment variables set:
```
STREAMLIT_BROWSER_GATHER_USAGE_STATS=false
```

## Customizing Logging

### Changing Log Level
To change the log level, modify `firecrawl_client.py`:

```python
# Configure logging
logging.basicConfig(
    level=logging.DEBUG,  # Change to DEBUG for more details
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
```

### Adding File-Based Logging
To save logs to files, add a file handler to the logging configuration:

```python
# Add to firecrawl_client.py
import logging
import os
from datetime import datetime

# Create logs directory if it doesn't exist
os.makedirs('/app/logs', exist_ok=True)

# Configure logging
log_file = f'/app/logs/firecrawl_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)
logger.info(f"Logging to: {log_file}")
```

## Best Practices

1. **Always Monitor Logs During Initial Testing**:
   - Keep the Docker logs open in a separate terminal window
   - Look for warnings and errors to catch issues early

2. **Log Rotation**:
   - For high-volume scraping, consider implementing log rotation:
   ```python
   from logging.handlers import RotatingFileHandler
   handler = RotatingFileHandler('/app/logs/firecrawl.log', maxBytes=10485760, backupCount=5)
   ```

3. **Correlate With Streamlit Output**:
   - The Streamlit UI shows basic progress, but logs provide more detail
   - Look at both together for comprehensive troubleshooting

4. **Check Container Health**:
   - Use `docker-compose ps` to check container status if logging stops
   - Use `docker stats` to monitor resource usage during scraping
