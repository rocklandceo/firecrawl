"""
Firecrawl Client Integration
Professional API wrapper for Firecrawl scraping and crawling functionality
Supports both cloud and self-hosted Firecrawl instances
"""

import os
import yaml
import logging
from typing import Dict, List, Optional, Union, Any
from pathlib import Path
from firecrawl import FirecrawlApp
from datetime import datetime
import hashlib
import json
import sys
from logging.handlers import RotatingFileHandler

# Ensure logs directory exists
logs_dir = Path(__file__).parent.parent / 'logs'
logs_dir.mkdir(exist_ok=True)

# Configure logging with both console and file output
log_file = logs_dir / f'firecrawl_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'

# Create custom formatter with more detail
class ContextualFormatter(logging.Formatter):
    """Custom formatter that adds contextual information to log records"""
    def __init__(self):
        super().__init__(
            fmt='%(asctime)s - %(name)s - %(levelname)s - [%(session_id)s] - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
    
    def format(self, record):
        # Add session/request ID if not present
        if not hasattr(record, 'session_id'):
            record.session_id = '-'
        
        # Add URL context if not present
        if not hasattr(record, 'url'):
            record.url = '-'
            
        # Use the parent's format method to handle asctime correctly
        return super().format(record)

# Set up handlers
console_handler = logging.StreamHandler(sys.stdout)
file_handler = RotatingFileHandler(log_file, maxBytes=10*1024*1024, backupCount=5)

# Apply formatter
formatter = ContextualFormatter()
console_handler.setFormatter(formatter)
file_handler.setFormatter(formatter)

# Configure the logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Remove any existing handlers and add our configured ones
for handler in logger.handlers:
    logger.removeHandler(handler)
logger.addHandler(console_handler)
logger.addHandler(file_handler)

# Add log file location to startup message
logger.info(f"Firecrawl logging initialized. Log file: {log_file}")

class FirecrawlClient:
    """
    Professional Firecrawl API client with comprehensive error handling and configuration management.
    
    Supports both scraping single URLs and crawling entire websites.
    Designed for JavaScript-heavy websites with robust retry logic.
    """
    
    def __init__(self, 
                 api_key: Optional[str] = None,
                 api_url: Optional[str] = None,
                 config_file: Optional[str] = None):
        """
        Initialize the Firecrawl client with API credentials and configuration.
        
        Args:
            api_key: Firecrawl API key (if None, loads from environment)
            api_url: API URL for self-hosted instances (if None, uses cloud)
            config_file: Path to YAML configuration file
        """
        self.config = self._load_configuration(config_file)
        self.api_key = api_key or self._get_api_key()
        self.api_url = api_url or self.config.get('api', {}).get('url', 'https://api.firecrawl.dev')
        
        # Initialize Firecrawl app
        self.app = None
        self._initialize_client()
        
        # Connection status
        self._connection_verified = False
        self._last_connection_check = None
        
        logger.info(f"FirecrawlClient initialized with API URL: {self.api_url}")
    
    def _load_configuration(self, config_file: Optional[str] = None) -> Dict[str, Any]:
        """Load configuration from YAML file."""
        if not config_file:
            # Default config file path
            project_root = Path(__file__).parent.parent
            config_file = project_root / 'config' / 'firecrawl.yaml'
        
        try:
            with open(config_file, 'r') as f:
                config = yaml.safe_load(f)
                logger.info(f"Configuration loaded from {config_file}")
                return config
        except FileNotFoundError:
            logger.warning(f"Configuration file not found: {config_file}")
            return self._get_default_config()
        except yaml.YAMLError as e:
            logger.error(f"Error parsing configuration file: {e}")
            return self._get_default_config()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Return default configuration if config file is not available."""
        return {
            'api': {
                'url': 'https://api.firecrawl.dev',
                'timeout': 30
            },
            'scraping': {
                'formats': ['markdown', 'html'],
                'javascript': {
                    'enabled': True,
                    'timeout': 10,
                    'wait_for': 'networkidle'
                },
                'extraction': {
                    'preserve_code_blocks': True,
                    'clean_navigation': True,
                    'optimize_for_ai': True,
                    'include_metadata': True
                }
            },
            'crawling': {
                'max_pages': 100,
                'max_depth': 3
            }
        }
    
    def _get_api_key(self) -> str:
        """Get API key from environment variables."""
        api_key = os.getenv('FIRECRAWL_API_KEY')
        if not api_key:
            raise ValueError(
                "FIRECRAWL_API_KEY not found in environment variables. "
                "Please set your API key in the .env file."
            )
        return api_key
    
    def _initialize_client(self):
        """Initialize the Firecrawl client with proper error handling."""
        try:
            if self.api_url == 'https://api.firecrawl.dev':
                # Cloud instance
                self.app = FirecrawlApp(api_key=self.api_key)
            else:
                # Self-hosted instance
                self.app = FirecrawlApp(api_key=self.api_key, api_url=self.api_url)
            
            logger.info("Firecrawl client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Firecrawl client: {e}")
            raise
    
    def test_connection(self) -> Dict[str, Any]:
        """
        Test the connection to Firecrawl API.
        
        Returns:
            Dict containing connection status, response time, and any errors
        """
        start_time = datetime.now()
        
        try:
            # Test with a simple, fast URL
            test_url = "https://httpbin.org/html"
            
            logger.info(f"Testing connection with URL: {test_url}")
            
            # Perform a lightweight scrape test
            result = self.app.scrape_url(
                url=test_url,
                formats=['markdown'],
                timeout=10000  # Convert to milliseconds
            )
            
            end_time = datetime.now()
            response_time = (end_time - start_time).total_seconds()
            
            if result and hasattr(result, 'markdown') and result.markdown:
                self._connection_verified = True
                self._last_connection_check = datetime.now()
                
                connection_result = {
                    'status': 'success',
                    'message': 'Connection to Firecrawl API verified successfully',
                    'response_time_seconds': response_time,
                    'api_url': self.api_url,
                    'test_url': test_url,
                    'timestamp': datetime.now().isoformat()
                }
                
                logger.info(f"Connection test successful (Response time: {response_time:.2f}s)")
                return connection_result
            else:
                raise Exception(f"No markdown content returned from test scrape. Result type: {type(result)}, Result: {result}")
                
        except Exception as e:
            end_time = datetime.now()
            response_time = (end_time - start_time).total_seconds()
            
            error_result = {
                'status': 'error',
                'message': f'Connection test failed: {str(e)}',
                'response_time_seconds': response_time,
                'api_url': self.api_url,
                'error_type': type(e).__name__,
                'timestamp': datetime.now().isoformat()
            }
            
            logger.error(f"Connection test failed: {e}")
            return error_result
    
    def scrape_url(self, 
                   url: str, 
                   formats: Optional[List[str]] = None,
                   wait_for_js: int = 10,
                   include_metadata: bool = True) -> Dict[str, Any]:
        """
        Scrape a single URL with comprehensive options and error handling.
        
        Args:
            url: URL to scrape
            formats: Output formats ['markdown', 'html', 'rawHtml']
            wait_for_js: Time to wait for JavaScript content (seconds)
            include_metadata: Whether to include page metadata
            
        Returns:
            Dict containing scraped content, metadata, and status information
        """
        if not formats:
            formats = self.config.get('scraping', {}).get('formats', ['markdown'])
        
        logger.info(f"Scraping URL: {url}")
        
        try:
            # Perform the scrape using current Firecrawl SDK format
            start_time = datetime.now()
            
            # Use current Firecrawl SDK specification (v1 API)
            scrape_kwargs = {
                'url': url,
                'formats': formats,
                'timeout': self.config.get('api', {}).get('timeout', 30) * 1000
            }
            
            # Add wait time using correct parameter name for current API
            if wait_for_js > 0:
                scrape_kwargs['wait'] = wait_for_js * 1000  # Convert to milliseconds
            
            # Add metadata extraction if requested (simplified for compatibility)
            if include_metadata:
                scrape_kwargs['includeTags'] = ['title', 'meta', 'links']
                
            # Add required options for extract format if needed
            if 'extract' in formats:
                scrape_kwargs['extractOptions'] = {
                    'selectors': ['main', 'article', '.codelab-step', '#codelab-steps']
                }
                
            # Add required options for json format if needed
            if 'json' in formats:
                scrape_kwargs['jsonOptions'] = {
                    'selector': 'body'
                }
            
            result = self.app.scrape_url(**scrape_kwargs)
            end_time = datetime.now()
            
            # Convert ScrapeResponse object to dict format for compatibility
            if hasattr(result, 'markdown'):
                content_dict = {
                    'markdown': result.markdown,
                    'html': getattr(result, 'html', None),
                    'rawHtml': getattr(result, 'rawHtml', None),
                    'links': getattr(result, 'links', None),
                    'metadata': getattr(result, 'metadata', {}),
                    'extract': getattr(result, 'extract', None)
                }
            else:
                # Fallback for dict format (if still supported)
                content_dict = result if isinstance(result, dict) else {'raw': str(result)}
            
            # Process and enrich the result
            processed_result = {
                'url': url,
                'status': 'success',
                'scraped_at': start_time.isoformat(),
                'processing_time_seconds': (end_time - start_time).total_seconds(),
                'content': content_dict,
                'content_hash': self._generate_content_hash(content_dict),
                'formats_requested': formats,
                'parameters_used': scrape_kwargs
            }
            
            logger.info(f"Successfully scraped {url} in {processed_result['processing_time_seconds']:.2f}s")
            return processed_result
            
        except Exception as e:
            error_result = {
                'url': url,
                'status': 'error',
                'error_message': str(e),
                'error_type': type(e).__name__,
                'scraped_at': datetime.now().isoformat(),
                'formats_requested': formats
            }
            
            logger.error(f"Failed to scrape {url}: {e}")
            return error_result
    
    def crawl_website(self, 
                     url: str,
                     max_pages: int = 100,
                     max_depth: int = 3,
                     include_patterns: Optional[List[str]] = None,
                     exclude_patterns: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Crawl an entire website with comprehensive options.
        
        Args:
            url: Base URL to start crawling
            max_pages: Maximum number of pages to crawl
            max_depth: Maximum crawl depth
            include_patterns: URL patterns to include
            exclude_patterns: URL patterns to exclude
            
        Returns:
            Dict containing crawl results and status information
        """
        logger.info(f"Starting website crawl: {url}")
        
        try:
            # Build crawling parameters using current Firecrawl SDK format
            crawl_kwargs = {
                'url': url,
                'limit': max_pages,
                'maxDepth': max_depth,
                'formats': self.config.get('scraping', {}).get('formats', ['markdown'])
            }
            
            # Add URL filtering if specified
            if include_patterns or exclude_patterns:
                crawl_kwargs['includePaths'] = include_patterns or []
                crawl_kwargs['excludePaths'] = exclude_patterns or []
            
            # Start the crawl
            start_time = datetime.now()
            crawl_result = self.app.crawl_url(**crawl_kwargs)
            end_time = datetime.now()
            
            # Process crawl results
            processed_result = {
                'base_url': url,
                'status': 'success',
                'crawl_started_at': start_time.isoformat(),
                'crawl_completed_at': end_time.isoformat(),
                'total_processing_time_seconds': (end_time - start_time).total_seconds(),
                'crawl_id': crawl_result.get('id') if crawl_result else None,
                'results': crawl_result,
                'parameters_used': params,
                'pages_found': len(crawl_result.get('data', [])) if crawl_result else 0
            }
            
            logger.info(f"Crawl completed for {url}: {processed_result['pages_found']} pages found")
            return processed_result
            
        except Exception as e:
            error_result = {
                'base_url': url,
                'status': 'error',
                'error_message': str(e),
                'error_type': type(e).__name__,
                'crawl_started_at': datetime.now().isoformat(),
                'parameters_used': locals()
            }
            
            logger.error(f"Failed to crawl {url}: {e}")
        return error_result
    
    def scrape_codelabs_tutorial(self, 
                                base_url: str, 
                                max_pages: int = 20,
                                formats: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Scrape a complete Google Codelabs tutorial with hash-based pagination.
        
        Google Codelabs use hash-based navigation (e.g., #0, #1, #2, etc.)
        This function automatically discovers and scrapes all pages in the tutorial.
        
        Args:
            base_url: Base Codelabs URL (e.g., 'https://codelabs.developers.google.com/tutorial-name/instructions')
            max_pages: Maximum number of pages to attempt (default: 20)
            formats: Output formats ['markdown', 'html', 'rawHtml']
            
        Returns:
            Dict containing all scraped pages and comprehensive metadata
        """
        if not formats:
            formats = self.config.get('scraping', {}).get('formats', ['markdown'])
        
        # Remove any existing hash from the base URL
        clean_base_url = base_url.split('#')[0]
        
        logger.info(f"Starting Google Codelabs tutorial scrape: {clean_base_url}")
        logger.info(f"Will attempt to scrape up to {max_pages} pages with hash-based pagination")
        
        start_time = datetime.now()
        results = {
            'base_url': clean_base_url,
            'status': 'in_progress',
            'scrape_started_at': start_time.isoformat(),
            'pages_scraped': [],
            'pages_failed': [],
            'total_pages_found': 0,
            'formats_requested': formats,
            'errors': []
        }
        
        # Start with page 0 (sometimes Codelabs start with #0, sometimes with no hash)
        page_urls_to_try = [clean_base_url]  # First try without hash
        for i in range(max_pages):
            page_urls_to_try.append(f"{clean_base_url}#{i}")
        
        successful_scrapes = 0
        consecutive_failures = 0
        max_consecutive_failures = 3  # Stop after 3 consecutive failures
        
        for page_num, page_url in enumerate(page_urls_to_try):
            logger.info(f"Scraping Codelabs page {page_num}: {page_url}")
            
            try:
                # For Google Codelabs SPA, we need to use actions to navigate
                # Try the enhanced approach first, then fall back to direct URL
                page_result = self._scrape_codelabs_page_with_actions(
                    base_url=clean_base_url,
                    page_number=page_num if page_num > 0 else None,
                    formats=formats
                )
                
                if page_result.get('status') == 'success':
                    # Check if we got meaningful content (not just navigation)
                    content = page_result.get('content', {})
                    markdown_content = content.get('markdown', '')
                    
                    # Skip if content is too short (likely just navigation)
                    if len(markdown_content.strip()) < 100:
                        logger.warning(f"Page {page_num} has minimal content ({len(markdown_content)} chars), skipping")
                        consecutive_failures += 1
                    else:
                        logger.info(f"Successfully scraped page {page_num}: {len(markdown_content)} characters")
                        
                        # Add page metadata
                        page_result['page_number'] = page_num
                        page_result['page_url'] = page_url
                        page_result['content_length'] = len(markdown_content)
                        
                        results['pages_scraped'].append(page_result)
                        successful_scrapes += 1
                        consecutive_failures = 0
                        
                else:
                    logger.warning(f"Failed to scrape page {page_num}: {page_result.get('error_message', 'Unknown error')}")
                    results['pages_failed'].append({
                        'page_number': page_num,
                        'page_url': page_url,
                        'error': page_result.get('error_message', 'Unknown error')
                    })
                    consecutive_failures += 1
                    
            except Exception as e:
                logger.error(f"Exception scraping page {page_num} ({page_url}): {str(e)}")
                results['pages_failed'].append({
                    'page_number': page_num,
                    'page_url': page_url,
                    'error': str(e)
                })
                consecutive_failures += 1
            
            # Stop if we've had too many consecutive failures
            if consecutive_failures >= max_consecutive_failures:
                logger.info(f"Stopping after {consecutive_failures} consecutive failures")
                break
        
        # Finalize results
        end_time = datetime.now()
        results.update({
            'status': 'completed',
            'scrape_completed_at': end_time.isoformat(),
            'total_processing_time_seconds': (end_time - start_time).total_seconds(),
            'total_pages_found': successful_scrapes,
            'pages_attempted': len([url for url in page_urls_to_try if consecutive_failures < max_consecutive_failures]),
            'success_rate': (successful_scrapes / len(results['pages_scraped'] + results['pages_failed'])) * 100 if (results['pages_scraped'] or results['pages_failed']) else 0
        })
        
        logger.info(f"Google Codelabs scraping completed: {successful_scrapes} pages scraped successfully")
        logger.info(f"Total processing time: {results['total_processing_time_seconds']:.2f} seconds")
        
        return results
    
    def _scrape_codelabs_page_with_actions(self, 
                                           base_url: str, 
                                           page_number: Optional[int] = None,
                                           formats: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Scrape a Google Codelabs page using actions to handle SPA navigation.
        
        Args:
            base_url: Clean base URL without hash
            page_number: Page number to navigate to (None for first page)
            formats: Output formats to request
            
        Returns:
            Dict containing scrape results
        """
        if not formats:
            formats = ['markdown']
        
        # Construct the target URL
        target_url = f"{base_url}#{page_number}" if page_number is not None else base_url
        
        try:
            # First, try with actions to simulate navigation
            scrape_kwargs = {
                'url': base_url,  # Start from base URL
                'formats': formats,
                'wait': 3000,  # Wait for initial load
                'includeTags': ['title', 'meta', 'h1', 'h2', 'h3'],  # Updated metadata approach
            }
            
            # Add required options for extract format if needed
            if 'extract' in formats:
                scrape_kwargs['extractOptions'] = {
                    'selectors': ['main', 'article', '.codelab-step', '#codelab-steps']
                }
                
            # Add required options for json format if needed
            if 'json' in formats:
                scrape_kwargs['jsonOptions'] = {
                    'selector': 'body'
                }
            
            # Add navigation action if we need to go to a specific page
            if page_number is not None:
                # Use actions to navigate to the specific page - fixed format
                scrape_kwargs['actions'] = [
                    {'type': 'wait', 'milliseconds': 2000},  # Wait for page to load
                    {'type': 'click', 'selector': f'[href="#{page_number}"], [data-step="{page_number}"], .step-{page_number}, button:contains("Next")'},  # Try common selectors
                    {'type': 'wait', 'milliseconds': 3000},  # Wait for navigation
                ]
            
            logger.info(f"Attempting SPA-aware scraping for page {page_number or 'main'} of {base_url}")
            
            # Execute the scrape with actions
            start_time = datetime.now()
            result = self.app.scrape_url(**scrape_kwargs)
            end_time = datetime.now()
            
            # Handle different response formats safely
            content = {}
            
            # Try to extract content, handling different response structures
            try:
                # Check if result is a dict with 'data' key
                if isinstance(result, dict) and 'data' in result:
                    content_data = result['data']
                    
                    # Extract content in the requested formats
                    for format_type in formats:
                        if format_type in content_data:
                            content[format_type] = content_data[format_type]
                
                # Alternative format: direct attributes
                elif hasattr(result, 'data'):
                    content_data = result.data
                    
                    # Try to extract content from attributes
                    for format_type in formats:
                        if hasattr(content_data, format_type):
                            content[format_type] = getattr(content_data, format_type)
            
                # Log the successful extraction
                if any(content.values()):
                    logger.info(f"Successfully extracted content using SPA actions: {sum(len(str(c)) for c in content.values())} total chars")
            except Exception as extract_err:
                logger.warning(f"Error extracting content from response: {extract_err}")
                
                processed_result = {
                    'url': target_url,
                    'status': 'success',
                    'scraped_at': start_time.isoformat(),
                    'processing_time_seconds': (end_time - start_time).total_seconds(),
                    'content': content,
                    'metadata': content_data.get('metadata', {}),
                    'method': 'spa_actions'
                }
                
                return processed_result
            else:
                # Fallback to direct URL scraping if actions don't work
                logger.warning(f"SPA actions failed for page {page_number}, falling back to direct URL scraping")
                return self._scrape_codelabs_fallback(target_url, formats)
                
        except Exception as e:
            logger.warning(f"SPA navigation failed for page {page_number}: {str(e)}, trying fallback")
            # Fallback to direct URL scraping
            return self._scrape_codelabs_fallback(target_url, formats)
            
        # Execute the scrape
        result = self.app.scrape_url(**scrape_kwargs)
            
        # Handle different response formats safely
        content = {}
        extracted_html = None
            
        try:
            # Format 1: Dictionary with data key
            if isinstance(result, dict):
                if 'data' in result:
                    content_data = result['data']
                        
                    # Extract content in the requested formats
                    for format_type in formats:
                        if format_type in content_data:
                            content[format_type] = content_data[format_type]
                        
                    # Try to get extraction data if available
                    if 'extract' in content_data:
                        extracted_content = content_data['extract']
                        if isinstance(extracted_content, list) and len(extracted_content) > 0:
                            first_extract = extracted_content[0]
                            if isinstance(first_extract, dict) and 'html' in first_extract:
                                html_content = first_extract['html']
                                if len(html_content) > 100:
                                    # Use extracted content if substantial
                                    logger.info(f"Using extracted content ({len(html_content)} chars)")
                                    extracted_html = html_content
                
            # Format 2: Object with attributes
            elif hasattr(result, 'data'):
                data = result.data
                    
                # Get formats from attributes
                for format_type in formats:
                    if hasattr(data, format_type):
                        content[format_type] = getattr(data, format_type)
                    
                # Try to get extract data if available
                if hasattr(data, 'extract'):
                    extracted_content = data.extract
                    if isinstance(extracted_content, list) and len(extracted_content) > 0:
                        first_extract = extracted_content[0]
                        if hasattr(first_extract, 'html'):
                            html_content = first_extract.html
                            if len(html_content) > 100:
                                logger.info(f"Using extracted content from attributes ({len(html_content)} chars)")
                                extracted_html = html_content
                
            # Convert HTML to markdown if we have extracted HTML content
            if extracted_html and 'markdown' in formats:
                try:
                    from bs4 import BeautifulSoup
                    from markdownify import markdownify
                        
                    soup = BeautifulSoup(extracted_html, 'html.parser')
                    markdown_content = markdownify(str(soup))
                    content['html'] = extracted_html
                    content['markdown'] = markdown_content
                    logger.info(f"Generated markdown from extracted HTML: {len(markdown_content)} chars")
                except Exception as e:
                    logger.warning(f"Failed to convert HTML to Markdown: {e}")
                
            # Log success
            if any(content.values()):
                logger.info(f"Successfully extracted content: {sum(len(str(c)) for c in content.values())} total chars")
                    
        except Exception as e:
            logger.warning(f"Error processing scrape result: {e}")
            
        # Return the result with whatever content we managed to extract
        end_time = datetime.now()
        return {
            'url': target_url,
            'status': 'success' if any(content.values()) else 'error',
            'scraped_at': start_time.isoformat(),
            'processing_time_seconds': (end_time - start_time).total_seconds(),
            'content': content,
            'content_length': len(content.get('markdown', '')),
            'method': 'spa_actions'
        }
    
    def _scrape_codelabs_fallback(self, url: str, formats: List[str]) -> Dict[str, Any]:
        """
        Fallback method for Codelabs scraping using direct URL approach.
        """
        start_time = datetime.now()
        logger.info(f"Using fallback direct scraping for {url}")
        
        # Special case for Google Codelabs - use direct HTML extraction
        if 'codelabs.developers.google.com' in url:
            try:
                logger.info(f"Using direct HTML extraction for Google Codelabs: {url}")
                import requests
                from bs4 import BeautifulSoup
                from markdownify import markdownify
                
                # Fetch the HTML content directly
                response = requests.get(url, timeout=15)
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, 'html.parser')
                    
                    # Extract title
                    title = soup.title.string if soup.title else ''
                    
                    # Try to find the main content container
                    content_selectors = [
                        '#codelab-steps', '.codelab-step', '.instructions', 
                        'main', 'article', '.step-content'
                    ]
                    content_html = ''
                    
                    for selector in content_selectors:
                        elements = soup.select(selector)
                        if elements:
                            logger.info(f"Found {len(elements)} content elements with selector '{selector}'")
                            # Use the first significant content element found
                            element_html = str(elements[0])
                            if len(element_html) > 500:  # Must be substantial content
                                content_html = element_html
                                logger.info(f"Using content from selector '{selector}': {len(content_html)} chars")
                                break
                    
                    # If we found content, convert to markdown and HTML
                    content = {}
                    if content_html:
                        content['html'] = content_html
                        if 'markdown' in formats:
                            markdown_content = markdownify(content_html)
                            content['markdown'] = markdown_content
                            logger.info(f"Generated markdown: {len(markdown_content)} chars")
                    
                    end_time = datetime.now()
                    return {
                        'url': url,
                        'status': 'success' if content else 'error',
                        'scraped_at': start_time.isoformat(),
                        'processing_time_seconds': (end_time - start_time).total_seconds(),
                        'content': content,
                        'content_length': len(content.get('markdown', '')),
                        'title': title,
                        'method': 'direct_html_extraction'
                    }
                else:
                    logger.warning(f"Failed to fetch URL, status code: {response.status_code}")
            except Exception as e:
                logger.warning(f"Error during direct HTML extraction: {str(e)}")
                # Continue to try the API-based approach as fallback
        
        # Regular fallback using Firecrawl API
        try:
            # Use compatible API parameters
            scrape_kwargs = {
                'url': url,
                'formats': formats,
                'wait': 8000,  # 8 seconds in milliseconds
                'includeTags': ['title', 'meta', 'h1', 'h2', 'h3']
            }
            
            # Add required options for extract format if needed
            if 'extract' in formats:
                scrape_kwargs['extractOptions'] = {
                    'selectors': ['main', 'article', '.codelab-step', '#codelab-steps']
                }
                
            # Add required options for json format if needed
            if 'json' in formats:
                scrape_kwargs['jsonOptions'] = {
                    'selector': 'body'
                }
            
            # Execute the scrape
            api_start_time = datetime.now()
            result = self.app.scrape_url(**scrape_kwargs)
            api_end_time = datetime.now()
            
            # Handle different response formats safely
            content = {}
            extracted_html = None
            
            try:
                # Format 1: Dictionary with data key
                if isinstance(result, dict):
                    if 'data' in result:
                        content_data = result['data']
                        
                        # Extract content in the requested formats
                        for format_type in formats:
                            if format_type in content_data:
                                content[format_type] = content_data[format_type]
                
                # Format 2: Object with attributes
                elif hasattr(result, 'data'):
                    data = result.data
                    
                    # Get formats from attributes
                    for format_type in formats:
                        if hasattr(data, format_type):
                            content[format_type] = getattr(data, format_type)
                
                # Log success
                if any(content.values()):
                    logger.info(f"Successfully extracted content via API: {sum(len(str(c)) for c in content.values())} total chars")
                    
            except Exception as e:
                logger.warning(f"Error processing API scrape result: {e}")
            
            # Return the result with whatever content we managed to extract
            end_time = datetime.now()
            return {
                'url': url,
                'status': 'success' if any(content.values()) else 'error',
                'scraped_at': start_time.isoformat(),
                'processing_time_seconds': (end_time - start_time).total_seconds(),
                'content': content,
                'content_length': len(content.get('markdown', '')),
                'method': 'firecrawl_api'
            }
            
        except Exception as e:
            end_time = datetime.now()
            return {
                'url': url,
                'status': 'error',
                'error': str(e),
                'scraped_at': start_time.isoformat(),
                'processing_time_seconds': (end_time - start_time).total_seconds(),
                'method': 'fallback_failed'
            }
    
    def _generate_content_hash(self, content: Any) -> str:
        """Generate a hash for content to detect duplicates."""
        content_str = json.dumps(content, sort_keys=True, default=str)
        return hashlib.sha256(content_str.encode()).hexdigest()
    
    def get_client_info(self) -> Dict[str, Any]:
        """Get information about the client configuration and status."""
        return {
            'api_url': self.api_url,
            'connection_verified': self._connection_verified,
            'last_connection_check': self._last_connection_check.isoformat() if self._last_connection_check else None,
            'configuration': self.config,
            'client_initialized': self.app is not None
        }
    
    def __repr__(self) -> str:
        return f"FirecrawlClient(api_url='{self.api_url}', connected={self._connection_verified})"
