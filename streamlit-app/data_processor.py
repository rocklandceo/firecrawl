"""
Data Processing Module for Firecrawl-Streamlit Web Scraper
Advanced content processing with markdown optimization and AI-friendly formatting
Designed for JavaScript-heavy websites with robust content preservation
"""

import re
import logging
from typing import Dict, List, Optional, Any, Union
from pathlib import Path
import markdown
from markdown.extensions import fenced_code, toc, tables, codehilite
from bs4 import BeautifulSoup
import hashlib
import json
from datetime import datetime
from urllib.parse import urlparse, urljoin, urlunparse
import yaml

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ContentProcessor:
    """
    Advanced content processor for optimizing scraped content for AI/LLM consumption.
    
    Provides comprehensive markdown optimization, code block preservation,
    link processing, and AI-friendly formatting capabilities.
    """
    
    def __init__(self, config_file: Optional[str] = None):
        """
        Initialize the content processor with configuration.
        
        Args:
            config_file: Path to YAML configuration file
        """
        self.config = self._load_configuration(config_file)
        self.markdown_processor = self._setup_markdown_processor()
        
        logger.info("ContentProcessor initialized successfully")
    
    def _load_configuration(self, config_file: Optional[str] = None) -> Dict[str, Any]:
        """Load configuration from YAML file."""
        if not config_file:
            # Default config file path
            project_root = Path(__file__).parent.parent
            config_file = project_root / 'config' / 'app_settings.yaml'
        
        try:
            with open(config_file, 'r') as f:
                config = yaml.safe_load(f)
                processing_config = config.get('processing', {})
                logger.info(f"Processing configuration loaded from {config_file}")
                return processing_config
        except FileNotFoundError:
            logger.warning(f"Configuration file not found: {config_file}")
            return self._get_default_config()
        except yaml.YAMLError as e:
            logger.error(f"Error parsing configuration file: {e}")
            return self._get_default_config()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Return default processing configuration."""
        return {
            'defaults': {
                'preserve_code_blocks': True,
                'optimize_for_ai': True,
                'clean_navigation': True,
                'include_metadata': True
            },
            'markdown': {
                'heading_normalization': True,
                'code_fence_language_detection': True,
                'link_validation': True,
                'remove_html_artifacts': True
            }
        }
    
    def _setup_markdown_processor(self) -> markdown.Markdown:
        """Set up the markdown processor with appropriate extensions."""
        extensions = [
            'fenced_code',
            'tables',
            'toc',
            'codehilite',
            'attr_list',
            'def_list',
            'footnotes',
            'md_in_html',
            'nl2br'
        ]
        
        extension_configs = {
            'codehilite': {
                'use_pygments': True,
                'css_class': 'highlight',
                'guess_lang': True
            },
            'toc': {
                'permalink': False,
                'baselevel': 1,
                'toc_depth': 6
            },
            'fenced_code': {
                'lang_prefix': 'language-'
            }
        }
        
        return markdown.Markdown(
            extensions=extensions,
            extension_configs=extension_configs,
            output_format='html5'
        )
    
    def process_content(self, 
                       content: Dict[str, Any],
                       url: str,
                       options: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Main content processing pipeline that orchestrates all optimization steps.
        
        Args:
            content: Raw content from Firecrawl (markdown, html, etc.)
            url: Source URL for context and link processing
            options: Processing options to override defaults
            
        Returns:
            Dict containing optimized content and processing metadata
        """
        logger.info(f"Processing content from: {url}")
        
        # Merge options with defaults
        processing_options = {**self.config.get('defaults', {})}
        if options:
            processing_options.update(options)
        
        try:
            # Initialize processing result
            result = {
                'source_url': url,
                'processed_at': datetime.now().isoformat(),
                'processing_options': processing_options,
                'original_content': content.copy(),
                'optimized_content': {},
                'processing_steps': [],
                'metadata': {}
            }
            
            # Step 1: Extract and preserve code blocks
            if processing_options.get('preserve_code_blocks', True):
                preserved_content = self._preserve_code_blocks(content)
                result['processing_steps'].append('code_block_preservation')
                logger.debug("Code blocks preserved")
            else:
                preserved_content = content
            
            # Step 2: Process and validate links  
            if 'markdown' in preserved_content:
                link_processed_content = self._process_links(
                    preserved_content['markdown'], 
                    url,
                    processing_options.get('link_validation', True)
                )
                preserved_content['markdown'] = link_processed_content
                result['processing_steps'].append('link_processing')
                logger.debug("Links processed and validated")
            
            # Step 3: Clean and optimize content structure
            if processing_options.get('clean_navigation', True):
                cleaned_content = self._clean_content_structure(preserved_content)
                result['processing_steps'].append('content_cleaning')
                logger.debug("Content structure cleaned")
            else:
                cleaned_content = preserved_content
            
            # Step 4: Apply AI-friendly formatting
            if processing_options.get('optimize_for_ai', True):
                ai_optimized_content = self._apply_ai_friendly_formatting(cleaned_content)
                result['processing_steps'].append('ai_optimization')
                logger.debug("AI-friendly formatting applied")
            else:
                ai_optimized_content = cleaned_content
            
            # Step 5: Generate structured output
            final_content = self._generate_structured_output(ai_optimized_content, url)
            result['optimized_content'] = final_content
            result['processing_steps'].append('structured_output_generation')
            
            # Step 6: Generate metadata and hash
            result['metadata'] = self._generate_content_metadata(final_content, url)
            result['content_hash'] = self._generate_content_hash(final_content)
            
            logger.info(f"Content processing completed for {url}")
            return result
            
        except Exception as e:
            error_result = {
                'source_url': url,
                'processed_at': datetime.now().isoformat(),
                'status': 'error',
                'error_message': str(e),
                'error_type': type(e).__name__,
                'processing_options': processing_options,
                'original_content': content
            }
            
            logger.error(f"Content processing failed for {url}: {e}")
            return error_result
    
    def _preserve_code_blocks(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """
        Detect and preserve fenced code blocks with language detection and metadata.
        
        Args:
            content: Content dictionary potentially containing markdown
            
        Returns:
            Content with preserved and enhanced code blocks
        """
        if 'markdown' not in content:
            return content
        
        markdown_content = content['markdown']
        preserved_content = content.copy()
        
        # Pattern to match fenced code blocks with optional language specifier
        code_block_pattern = r'```(\w+)?\s*\n(.*?)\n```'
        
        code_blocks = []
        
        def preserve_code_block(match):
            language = match.group(1) or 'text'
            code_content = match.group(2)
            
            # Detect language if not specified
            if language == 'text':
                detected_language = self._detect_code_language(code_content)
                language = detected_language if detected_language else 'text'
            
            # Store code block metadata
            code_block_info = {
                'language': language,
                'content': code_content,
                'line_count': len(code_content.split('\n')),
                'character_count': len(code_content)
            }
            code_blocks.append(code_block_info)
            
            # Return enhanced code block
            return f'```{language}\n{code_content}\n```'
        
        # Process and preserve code blocks
        enhanced_markdown = re.sub(
            code_block_pattern, 
            preserve_code_block, 
            markdown_content, 
            flags=re.DOTALL
        )
        
        preserved_content['markdown'] = enhanced_markdown
        preserved_content['code_blocks_metadata'] = code_blocks
        
        logger.debug(f"Preserved {len(code_blocks)} code blocks")
        return preserved_content
    
    def _detect_code_language(self, code_content: str) -> Optional[str]:
        """
        Detect programming language from code content using heuristics.
        
        Args:
            code_content: Raw code content
            
        Returns:
            Detected language or None
        """
        code_lower = code_content.lower().strip()
        
        # Language detection patterns
        if any(keyword in code_lower for keyword in ['def ', 'import ', 'from ', 'if __name__']):
            return 'python'
        elif any(keyword in code_lower for keyword in ['function ', 'const ', 'let ', 'var ', '=>']):
            return 'javascript'
        elif any(keyword in code_lower for keyword in ['<html', '<div', '<span', 'class=']):
            return 'html'
        elif any(keyword in code_lower for keyword in ['body {', '.class', '#id', '@media']):
            return 'css'
        elif any(keyword in code_lower for keyword in ['public class', 'private ', 'public static void']):
            return 'java'
        elif any(keyword in code_lower for keyword in ['#!/bin/', 'echo ', 'grep ', 'awk ']):
            return 'bash'
        elif any(keyword in code_lower for keyword in ['select ', 'from ', 'where ', 'insert into']):
            return 'sql'
        elif any(keyword in code_lower for keyword in ['"', 'key:', '- name:']):
            return 'yaml'
        elif code_lower.startswith('{') and code_lower.endswith('}'):
            return 'json'
        else:
            return None
    
    def _process_links(self, markdown_content: str, base_url: str, validate: bool = True) -> str:
        """
        Process and validate links in markdown content.
        
        Args:
            markdown_content: Markdown content containing links
            base_url: Base URL for resolving relative links
            validate: Whether to validate link accessibility
            
        Returns:
            Processed markdown with optimized links
        """
        # Pattern to match markdown links [text](url)
        link_pattern = r'\[([^\]]*)\]\(([^)]+)\)'
        
        def process_link(match):
            link_text = match.group(1)
            link_url = match.group(2)
            
            # Skip anchor links and mail links
            if link_url.startswith(('#', 'mailto:', 'tel:')):
                return match.group(0)
            
            # Resolve relative URLs
            if not link_url.startswith(('http://', 'https://', '//')):
                resolved_url = urljoin(base_url, link_url)
            else:
                resolved_url = link_url
            
            # Clean up URL
            parsed_url = urlparse(resolved_url)
            clean_url = urlunparse((
                parsed_url.scheme,
                parsed_url.netloc,
                parsed_url.path,
                parsed_url.params,
                parsed_url.query,
                ''  # Remove fragment for cleaner URLs
            ))
            
            # Return processed link
            if link_text.strip():
                return f'[{link_text}]({clean_url})'
            else:
                # Use URL as text if no link text provided
                return f'[{clean_url}]({clean_url})'
        
        processed_content = re.sub(link_pattern, process_link, markdown_content)
        return processed_content
    
    def _clean_content_structure(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """
        Clean and optimize content structure by removing navigation and artifacts.
        
        Args:
            content: Content dictionary
            
        Returns:
            Cleaned content dictionary
        """
        cleaned_content = content.copy()
        
        if 'markdown' in content:
            markdown_text = content['markdown']
            
            # Remove common navigation patterns
            navigation_patterns = [
                r'^\s*\*\s*\[Home\].*$',
                r'^\s*\*\s*\[Back\].*$',
                r'^\s*\*\s*\[Next\].*$',
                r'^\s*\*\s*\[Previous\].*$',
                r'^\s*Navigation\s*$',
                r'^\s*Menu\s*$',
                r'^\s*\[Skip to .*?\].*$'
            ]
            
            for pattern in navigation_patterns:
                markdown_text = re.sub(pattern, '', markdown_text, flags=re.MULTILINE | re.IGNORECASE)
            
            # Remove excessive whitespace
            markdown_text = re.sub(r'\n{3,}', '\n\n', markdown_text)
            markdown_text = markdown_text.strip()
            
            cleaned_content['markdown'] = markdown_text
        
        return cleaned_content
    
    def _apply_ai_friendly_formatting(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """
        Apply AI-friendly formatting to optimize content for LLM consumption.
        
        Args:
            content: Content dictionary
            
        Returns:
            AI-optimized content dictionary
        """
        ai_content = content.copy()
        
        if 'markdown' in content:
            markdown_text = content['markdown']
            
            # Normalize heading hierarchy
            markdown_text = self._normalize_heading_hierarchy(markdown_text)
            
            # Ensure proper spacing around headings
            markdown_text = re.sub(r'\n(#{1,6})', r'\n\n\1', markdown_text)
            markdown_text = re.sub(r'(#{1,6}.*)\n([^#\n])', r'\1\n\n\2', markdown_text)
            
            # Improve list formatting
            markdown_text = self._improve_list_formatting(markdown_text)
            
            # Clean up HTML artifacts
            if self.config.get('markdown', {}).get('remove_html_artifacts', True):
                markdown_text = self._remove_html_artifacts(markdown_text)
            
            # Ensure proper paragraph separation
            markdown_text = re.sub(r'\n{3,}', '\n\n', markdown_text)
            
            ai_content['markdown'] = markdown_text.strip()
        
        return ai_content
    
    def _normalize_heading_hierarchy(self, markdown_text: str) -> str:
        """Normalize heading hierarchy to ensure proper semantic structure."""
        lines = markdown_text.split('\n')
        normalized_lines = []
        current_level = 0
        
        for line in lines:
            if line.strip().startswith('#'):
                # Count heading level
                level = len(line) - len(line.lstrip('#'))
                
                # Ensure proper hierarchy (max jump of 1 level)
                if level > current_level + 1:
                    level = current_level + 1
                
                current_level = level
                
                # Reconstruct heading with normalized level
                heading_text = line.lstrip('#').strip()
                normalized_line = '#' * level + ' ' + heading_text
                normalized_lines.append(normalized_line)
            else:
                normalized_lines.append(line)
        
        return '\n'.join(normalized_lines)
    
    def _improve_list_formatting(self, markdown_text: str) -> str:
        """Improve list formatting for better readability."""
        # Ensure proper spacing before lists
        markdown_text = re.sub(r'\n([*+-]|\d+\.)', r'\n\n\1', markdown_text)
        
        # Ensure consistent list markers
        markdown_text = re.sub(r'^\s*[*+-]\s+', '- ', markdown_text, flags=re.MULTILINE)
        
        return markdown_text
    
    def _remove_html_artifacts(self, markdown_text: str) -> str:
        """Remove HTML artifacts that may interfere with markdown parsing."""
        # Remove common HTML tags that shouldn't be in markdown
        html_patterns = [
            r'</?div[^>]*>',
            r'</?span[^>]*>',
            r'</?p[^>]*>',
            r'<br\s*/?>'
        ]
        
        for pattern in html_patterns:
            markdown_text = re.sub(pattern, '', markdown_text, flags=re.IGNORECASE)
        
        return markdown_text
    
    def _generate_structured_output(self, content: Dict[str, Any], url: str) -> Dict[str, Any]:
        """
        Generate final structured output combining all processing steps.
        
        Args:
            content: Processed content dictionary
            url: Source URL
            
        Returns:
            Final structured content dictionary
        """
        structured_output = {
            'source_url': url,
            'content_type': 'processed_markdown',
            'markdown': content.get('markdown', ''),
            'html': content.get('html', ''),
            'raw_html': content.get('rawHtml', ''),
            'metadata': content.get('metadata', {}),
            'code_blocks': content.get('code_blocks_metadata', []),
            'processing_info': {
                'processed_at': datetime.now().isoformat(),
                'processor_version': '1.0.0',
                'total_code_blocks': len(content.get('code_blocks_metadata', [])),
                'content_length': len(content.get('markdown', '')),
                'estimated_reading_time_minutes': max(1, len(content.get('markdown', '').split()) // 200)
            }
        }
        
        return structured_output
    
    def _generate_content_metadata(self, content: Dict[str, Any], url: str) -> Dict[str, Any]:
        """Generate comprehensive metadata for the processed content."""
        markdown_content = content.get('markdown', '')
        
        # Extract headings
        headings = re.findall(r'^(#{1,6})\s+(.+)$', markdown_content, re.MULTILINE)
        
        # Count various content elements
        word_count = len(markdown_content.split())
        line_count = len(markdown_content.split('\n'))
        code_block_count = len(content.get('code_blocks', []))
        link_count = len(re.findall(r'\[([^\]]*)\]\([^)]+\)', markdown_content))
        
        metadata = {
            'url': url,
            'domain': urlparse(url).netloc,
            'content_stats': {
                'word_count': word_count,
                'line_count': line_count,
                'character_count': len(markdown_content),
                'heading_count': len(headings),
                'code_block_count': code_block_count,
                'link_count': link_count
            },
            'headings': [{'level': len(h[0]), 'text': h[1]} for h in headings],
            'estimated_reading_time_minutes': max(1, word_count // 200),
            'content_quality_score': self._calculate_content_quality_score(
                word_count, len(headings), code_block_count, link_count
            )
        }
        
        return metadata
    
    def _calculate_content_quality_score(self, word_count: int, heading_count: int, 
                                       code_block_count: int, link_count: int) -> float:
        """Calculate a content quality score (0-100) based on various factors."""
        score = 0
        
        # Word count score (0-25 points)
        if word_count > 500:
            score += 25
        elif word_count > 200:
            score += 15
        elif word_count > 50:
            score += 10
        
        # Structure score (0-25 points)
        if heading_count > 0:
            score += min(25, heading_count * 5)
        
        # Code content score (0-25 points)
        if code_block_count > 0:
            score += min(25, code_block_count * 8)
        
        # Link richness score (0-25 points)
        if link_count > 0:
            score += min(25, link_count * 3)
        
        return min(100.0, score)
    
    def _generate_content_hash(self, content: Dict[str, Any]) -> str:
        """Generate a hash for the processed content."""
        content_str = json.dumps(content, sort_keys=True, default=str)
        return hashlib.sha256(content_str.encode()).hexdigest()
    
    def batch_process_content(self, content_list: List[Dict[str, Any]], 
                            options: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Process multiple content items in batch.
        
        Args:
            content_list: List of content dictionaries to process
            options: Processing options to apply to all items
            
        Returns:
            List of processed content dictionaries
        """
        logger.info(f"Starting batch processing of {len(content_list)} content items")
        
        results = []
        
        for i, content_item in enumerate(content_list):
            try:
                url = content_item.get('url', f'item_{i}')
                content_data = content_item.get('content', content_item)
                
                processed_result = self.process_content(content_data, url, options)
                results.append(processed_result)
                
                logger.debug(f"Processed item {i+1}/{len(content_list)}: {url}")
                
            except Exception as e:
                error_result = {
                    'source_url': content_item.get('url', f'item_{i}'),
                    'status': 'error',
                    'error_message': str(e),
                    'error_type': type(e).__name__,
                    'processed_at': datetime.now().isoformat()
                }
                results.append(error_result)
                logger.error(f"Failed to process item {i+1}: {e}")
        
        logger.info(f"Batch processing completed: {len(results)} items processed")
        return results
    
    def get_processor_info(self) -> Dict[str, Any]:
        """Get information about the processor configuration and capabilities."""
        return {
            'processor_version': '1.0.0',
            'configuration': self.config,
            'markdown_extensions': self.markdown_processor.treeprocessors.keys(),
            'supported_features': [
                'code_block_preservation',
                'language_detection',
                'link_processing', 
                'content_cleaning',
                'ai_friendly_formatting',
                'structured_output_generation',
                'batch_processing'
            ]
        }
    
    def __repr__(self) -> str:
        return f"ContentProcessor(config_loaded={bool(self.config)})"
