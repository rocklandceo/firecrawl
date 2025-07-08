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

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

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
            
            # Use direct keyword arguments per current Firecrawl SDK specification
            scrape_kwargs = {
                'url': url,
                'formats': formats,
                'wait_after_load': wait_for_js * 1000,  # Convert to milliseconds
                'timeout': self.config.get('api', {}).get('timeout', 30) * 1000
            }
            
            # Add metadata extraction if requested
            if include_metadata:
                scrape_kwargs['extract'] = {
                    'schema': {
                        'type': 'object',
                        'properties': {
                            'title': {'type': 'string'},
                            'description': {'type': 'string'},
                            'keywords': {'type': 'array', 'items': {'type': 'string'}},
                            'author': {'type': 'string'},
                            'published_date': {'type': 'string'}
                        }
                    }
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
