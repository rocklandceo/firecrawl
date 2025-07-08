"""
File Management System for Firecrawl-Streamlit Web Scraper
Advanced file organization with domain-based folders, metadata management, and export capabilities
Designed for efficient storage and retrieval of scraped content
"""

import os
import json
import zipfile
import hashlib
import logging
from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path
from datetime import datetime
from urllib.parse import urlparse
import yaml
import pandas as pd
from dataclasses import dataclass, asdict
import shutil

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@dataclass
class FileMetadata:
    """Metadata structure for managed files."""
    file_id: str
    original_url: str
    domain: str
    file_path: str
    content_type: str
    content_hash: str
    file_size: int
    created_at: str
    last_modified: str
    processing_info: Dict[str, Any]
    quality_score: float
    tags: List[str]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'FileMetadata':
        """Create from dictionary loaded from JSON."""
        return cls(**data)

class FileManager:
    """
    Advanced file management system for organizing and managing scraped content.
    
    Provides domain-based organization, duplicate detection, metadata management,
    and efficient export capabilities.
    """
    
    def __init__(self, base_directory: Optional[str] = None, config_file: Optional[str] = None):
        """
        Initialize the file manager with configuration.
        
        Args:
            base_directory: Base directory for file storage
            config_file: Path to YAML configuration file
        """
        self.config = self._load_configuration(config_file)
        self.base_directory = Path(base_directory) if base_directory else self._get_default_base_directory()
        self.metadata_file = self.base_directory / 'metadata' / 'file_index.json'
        self.metadata_cache: Dict[str, FileMetadata] = {}
        
        # Initialize directory structure
        self._initialize_directory_structure()
        
        # Load existing metadata
        self._load_metadata_cache()
        
        logger.info(f"FileManager initialized with base directory: {self.base_directory}")
    
    def _load_configuration(self, config_file: Optional[str] = None) -> Dict[str, Any]:
        """Load configuration from YAML file."""
        if not config_file:
            # Default config file path
            project_root = Path(__file__).parent.parent
            config_file = project_root / 'config' / 'app_settings.yaml'
        
        try:
            with open(config_file, 'r') as f:
                config = yaml.safe_load(f)
                storage_config = config.get('storage', {})
                logger.info(f"Storage configuration loaded from {config_file}")
                return storage_config
        except FileNotFoundError:
            logger.warning(f"Configuration file not found: {config_file}")
            return self._get_default_config()
        except yaml.YAMLError as e:
            logger.error(f"Error parsing configuration file: {e}")
            return self._get_default_config()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Return default storage configuration."""
        return {
            'organization': {
                'domain_based_folders': True,
                'timestamp_naming': True,
                'max_filename_length': 100,
                'sanitize_filenames': True
            },
            'storage': {
                'compression_enabled': True,
                'backup_enabled': True,
                'max_file_size_mb': 50,
                'duplicate_handling': 'skip'
            },
            'export': {
                'include_metadata': True,
                'default_format': 'zip',
                'preserve_structure': True
            }
        }
    
    def _get_default_base_directory(self) -> Path:
        """Get the default base directory for file storage."""
        project_root = Path(__file__).parent.parent
        return project_root / 'data'
    
    def _initialize_directory_structure(self):
        """Create the required directory structure."""
        directories = [
            self.base_directory,
            self.base_directory / 'scraped_content',
            self.base_directory / 'processed_content', 
            self.base_directory / 'metadata',
            self.base_directory / 'exports',
            self.base_directory / 'backups',
            self.base_directory / 'temp'
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
        
        logger.debug("Directory structure initialized")
    
    def _load_metadata_cache(self):
        """Load metadata cache from file."""
        if self.metadata_file.exists():
            try:
                with open(self.metadata_file, 'r') as f:
                    metadata_data = json.load(f)
                    
                self.metadata_cache = {
                    file_id: FileMetadata.from_dict(data)
                    for file_id, data in metadata_data.items()
                }
                
                logger.info(f"Loaded {len(self.metadata_cache)} file metadata records")
                
            except (json.JSONDecodeError, KeyError) as e:
                logger.error(f"Error loading metadata cache: {e}")
                self.metadata_cache = {}
        else:
            logger.info("No existing metadata cache found, starting fresh")
    
    def _save_metadata_cache(self):
        """Save metadata cache to file."""
        try:
            # Create backup if file exists
            if self.metadata_file.exists():
                backup_path = self.base_directory / 'backups' / f"file_index_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                shutil.copy2(self.metadata_file, backup_path)
            
            # Save current cache
            metadata_data = {
                file_id: metadata.to_dict()
                for file_id, metadata in self.metadata_cache.items()
            }
            
            with open(self.metadata_file, 'w') as f:
                json.dump(metadata_data, f, indent=2, default=str)
            
            logger.debug("Metadata cache saved successfully")
            
        except Exception as e:
            logger.error(f"Error saving metadata cache: {e}")
            raise
    
    def _generate_file_id(self, url: str, content_hash: str) -> str:
        """Generate a unique file ID."""
        combined = f"{url}_{content_hash}_{datetime.now().isoformat()}"
        return hashlib.md5(combined.encode()).hexdigest()[:12]
    
    def _sanitize_filename(self, filename: str, max_length: Optional[int] = None) -> str:
        """Sanitize filename for safe storage."""
        if max_length is None:
            max_length = self.config.get('organization', {}).get('max_filename_length', 100)
        
        # Remove or replace problematic characters
        sanitized = "".join(c for c in filename if c.isalnum() or c in (' ', '-', '_', '.'))
        sanitized = sanitized.replace(' ', '_')
        
        # Truncate if too long
        if len(sanitized) > max_length:
            name, ext = os.path.splitext(sanitized)
            available_length = max_length - len(ext)
            sanitized = name[:available_length] + ext
        
        return sanitized
    
    def _get_domain_directory(self, url: str) -> Path:
        """Get or create domain-based directory."""
        domain = urlparse(url).netloc
        domain_safe = self._sanitize_filename(domain)
        
        domain_dir = self.base_directory / 'scraped_content' / domain_safe
        domain_dir.mkdir(parents=True, exist_ok=True)
        
        return domain_dir
    
    def _generate_filename(self, url: str, content_type: str, timestamp: Optional[datetime] = None) -> str:
        """Generate timestamped filename."""
        if timestamp is None:
            timestamp = datetime.now()
        
        # Extract meaningful part from URL
        parsed_url = urlparse(url)
        path_parts = [part for part in parsed_url.path.split('/') if part]
        
        if path_parts:
            base_name = path_parts[-1]
            # Remove existing extension if present
            base_name = os.path.splitext(base_name)[0]
        else:
            base_name = "page"
        
        # Determine file extension
        extension_map = {
            'markdown': '.md',
            'processed_markdown': '.md',
            'html': '.html',
            'json': '.json',
            'text': '.txt'
        }
        
        extension = extension_map.get(content_type, '.txt')
        
        # Create timestamped filename
        timestamp_str = timestamp.strftime('%Y%m%d_%H%M%S')
        filename = f"{base_name}_{timestamp_str}{extension}"
        
        return self._sanitize_filename(filename)
    
    def store_content(self, 
                     url: str,
                     content: str,
                     content_type: str = 'markdown',
                     metadata: Optional[Dict[str, Any]] = None,
                     tags: Optional[List[str]] = None) -> str:
        """
        Store content with automatic organization and metadata management.
        
        Args:
            url: Source URL of the content
            content: Content to store
            content_type: Type of content (markdown, html, json, etc.)
            metadata: Additional metadata to store
            tags: Tags for categorization
            
        Returns:
            File ID of the stored content
        """
        try:
            # Generate content hash for duplicate detection
            content_hash = hashlib.sha256(content.encode()).hexdigest()
            
            # Check for duplicates
            if self._is_duplicate(content_hash):
                duplicate_id = self._get_duplicate_file_id(content_hash)
                logger.info(f"Duplicate content detected, returning existing file ID: {duplicate_id}")
                return duplicate_id
            
            # Generate file ID and paths
            file_id = self._generate_file_id(url, content_hash)
            domain_dir = self._get_domain_directory(url)
            filename = self._generate_filename(url, content_type)
            file_path = domain_dir / filename
            
            # Write content to file
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            # Create metadata record
            file_metadata = FileMetadata(
                file_id=file_id,
                original_url=url,
                domain=urlparse(url).netloc,
                file_path=str(file_path.relative_to(self.base_directory)),
                content_type=content_type,
                content_hash=content_hash,
                file_size=len(content.encode('utf-8')),
                created_at=datetime.now().isoformat(),
                last_modified=datetime.now().isoformat(),
                processing_info=metadata or {},
                quality_score=metadata.get('content_quality_score', 0.0) if metadata else 0.0,
                tags=tags or []
            )
            
            # Store metadata
            self.metadata_cache[file_id] = file_metadata
            self._save_metadata_cache()
            
            logger.info(f"Content stored successfully: {file_id} ({file_path})")
            return file_id
            
        except Exception as e:
            logger.error(f"Error storing content for {url}: {e}")
            raise
    
    def store_processed_content(self,
                              processed_result: Dict[str, Any],
                              tags: Optional[List[str]] = None) -> str:
        """
        Store processed content from ContentProcessor.
        
        Args:
            processed_result: Result from ContentProcessor.process_content()
            tags: Additional tags for categorization
            
        Returns:
            File ID of the stored content
        """
        try:
            url = processed_result['source_url']
            optimized_content = processed_result.get('optimized_content', {})
            
            # Store the optimized markdown content
            markdown_content = optimized_content.get('markdown', '')
            if not markdown_content:
                raise ValueError("No markdown content found in processed result")
            
            # Prepare metadata
            metadata = {
                'processing_info': processed_result.get('processing_info', {}),
                'content_stats': processed_result.get('metadata', {}).get('content_stats', {}),
                'content_quality_score': processed_result.get('metadata', {}).get('content_quality_score', 0.0),
                'processing_steps': processed_result.get('processing_steps', []),
                'code_blocks': processed_result.get('optimized_content', {}).get('code_blocks', [])
            }
            
            # Add processing-specific tags
            processing_tags = (tags or []) + ['processed', 'ai_optimized']
            if metadata.get('code_blocks'):
                processing_tags.append('contains_code')
            
            return self.store_content(
                url=url,
                content=markdown_content,
                content_type='processed_markdown',
                metadata=metadata,
                tags=processing_tags
            )
            
        except Exception as e:
            logger.error(f"Error storing processed content: {e}")
            raise
    
    def _is_duplicate(self, content_hash: str) -> bool:
        """Check if content hash already exists."""
        return any(
            metadata.content_hash == content_hash 
            for metadata in self.metadata_cache.values()
        )
    
    def _get_duplicate_file_id(self, content_hash: str) -> Optional[str]:
        """Get file ID of duplicate content."""
        for file_id, metadata in self.metadata_cache.items():
            if metadata.content_hash == content_hash:
                return file_id
        return None
    
    def get_file_metadata(self, file_id: str) -> Optional[FileMetadata]:
        """Get metadata for a specific file."""
        return self.metadata_cache.get(file_id)
    
    def get_content(self, file_id: str) -> Optional[str]:
        """Retrieve content by file ID."""
        metadata = self.get_file_metadata(file_id)
        if not metadata:
            return None
        
        try:
            file_path = self.base_directory / metadata.file_path
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except FileNotFoundError:
            logger.error(f"File not found: {file_path}")
            return None
        except Exception as e:
            logger.error(f"Error reading file {file_id}: {e}")
            return None
    
    def list_files(self, 
                   domain: Optional[str] = None,
                   content_type: Optional[str] = None,
                   tags: Optional[List[str]] = None,
                   min_quality_score: Optional[float] = None) -> List[FileMetadata]:
        """
        List files with optional filtering.
        
        Args:
            domain: Filter by domain
            content_type: Filter by content type
            tags: Filter by tags (must contain all specified tags)
            min_quality_score: Minimum quality score
            
        Returns:
            List of matching file metadata
        """
        results = []
        
        for metadata in self.metadata_cache.values():
            # Domain filter
            if domain and metadata.domain != domain:
                continue
            
            # Content type filter
            if content_type and metadata.content_type != content_type:
                continue
            
            # Tags filter
            if tags and not all(tag in metadata.tags for tag in tags):
                continue
            
            # Quality score filter
            if min_quality_score and metadata.quality_score < min_quality_score:
                continue
            
            results.append(metadata)
        
        # Sort by creation date (newest first)
        results.sort(key=lambda x: x.created_at, reverse=True)
        return results
    
    def delete_file(self, file_id: str) -> bool:
        """
        Delete a file and its metadata.
        
        Args:
            file_id: File ID to delete
            
        Returns:
            True if successful, False otherwise
        """
        try:
            metadata = self.get_file_metadata(file_id)
            if not metadata:
                logger.warning(f"File metadata not found: {file_id}")
                return False
            
            # Delete physical file
            file_path = self.base_directory / metadata.file_path
            if file_path.exists():
                file_path.unlink()
                logger.info(f"Physical file deleted: {file_path}")
            
            # Remove from metadata cache
            del self.metadata_cache[file_id]
            self._save_metadata_cache()
            
            logger.info(f"File deleted successfully: {file_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting file {file_id}: {e}")
            return False
    
    def export_files(self,
                    file_ids: Optional[List[str]] = None,
                    domain: Optional[str] = None,
                    export_format: str = 'zip',
                    include_metadata: bool = True) -> Path:
        """
        Export files to a compressed archive.
        
        Args:
            file_ids: Specific file IDs to export (None for all)
            domain: Export files from specific domain
            export_format: Export format ('zip' currently supported)
            include_metadata: Include metadata files in export
            
        Returns:
            Path to the exported archive
        """
        try:
            # Determine files to export
            if file_ids:
                files_to_export = [
                    self.get_file_metadata(file_id) 
                    for file_id in file_ids
                    if self.get_file_metadata(file_id)
                ]
            else:
                files_to_export = self.list_files(domain=domain)
            
            if not files_to_export:
                raise ValueError("No files found to export")
            
            # Create export filename
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            if domain:
                export_name = f"export_{domain}_{timestamp}"
            else:
                export_name = f"export_all_{timestamp}"
            
            export_path = self.base_directory / 'exports' / f"{export_name}.zip"
            export_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Create ZIP archive
            with zipfile.ZipFile(export_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for metadata in files_to_export:
                    # Add content file
                    file_path = self.base_directory / metadata.file_path
                    if file_path.exists():
                        # Preserve directory structure in ZIP
                        archive_path = metadata.file_path
                        zipf.write(file_path, archive_path)
                
                # Add metadata if requested
                if include_metadata:
                    metadata_content = json.dumps(
                        [metadata.to_dict() for metadata in files_to_export],
                        indent=2,
                        default=str
                    )
                    zipf.writestr("export_metadata.json", metadata_content)
            
            logger.info(f"Export completed: {export_path} ({len(files_to_export)} files)")
            return export_path
            
        except Exception as e:
            logger.error(f"Error during export: {e}")
            raise
    
    def get_storage_statistics(self) -> Dict[str, Any]:
        """Get comprehensive storage statistics."""
        try:
            total_files = len(self.metadata_cache)
            total_size = sum(metadata.file_size for metadata in self.metadata_cache.values())
            
            # Domain statistics
            domain_stats = {}
            for metadata in self.metadata_cache.values():
                domain = metadata.domain
                if domain not in domain_stats:
                    domain_stats[domain] = {'count': 0, 'size': 0}
                domain_stats[domain]['count'] += 1
                domain_stats[domain]['size'] += metadata.file_size
            
            # Content type statistics
            content_type_stats = {}
            for metadata in self.metadata_cache.values():
                content_type = metadata.content_type
                if content_type not in content_type_stats:
                    content_type_stats[content_type] = {'count': 0, 'size': 0}
                content_type_stats[content_type]['count'] += 1
                content_type_stats[content_type]['size'] += metadata.file_size
            
            # Quality statistics
            quality_scores = [metadata.quality_score for metadata in self.metadata_cache.values()]
            avg_quality = sum(quality_scores) / len(quality_scores) if quality_scores else 0
            
            return {
                'total_files': total_files,
                'total_size_bytes': total_size,
                'total_size_mb': total_size / (1024 * 1024),
                'average_quality_score': avg_quality,
                'domains': dict(sorted(domain_stats.items(), key=lambda x: x[1]['count'], reverse=True)),
                'content_types': dict(sorted(content_type_stats.items(), key=lambda x: x[1]['count'], reverse=True)),
                'storage_path': str(self.base_directory)
            }
            
        except Exception as e:
            logger.error(f"Error generating storage statistics: {e}")
            return {'error': str(e)}
    
    def cleanup_orphaned_files(self) -> int:
        """Remove files that exist on disk but not in metadata."""
        try:
            orphaned_count = 0
            content_dir = self.base_directory / 'scraped_content'
            
            if not content_dir.exists():
                return 0
            
            # Get all files referenced in metadata
            referenced_paths = {
                Path(metadata.file_path).resolve()
                for metadata in self.metadata_cache.values()
            }
            
            # Find all actual files
            for file_path in content_dir.rglob('*'):
                if file_path.is_file():
                    relative_path = file_path.relative_to(self.base_directory)
                    full_path = file_path.resolve()
                    
                    if full_path not in referenced_paths:
                        # This is an orphaned file
                        try:
                            file_path.unlink()
                            orphaned_count += 1
                            logger.debug(f"Removed orphaned file: {relative_path}")
                        except Exception as e:
                            logger.error(f"Error removing orphaned file {relative_path}: {e}")
            
            logger.info(f"Cleanup completed: {orphaned_count} orphaned files removed")
            return orphaned_count
            
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")
            return 0
    
    def get_manager_info(self) -> Dict[str, Any]:
        """Get information about the file manager configuration and status."""
        return {
            'manager_version': '1.0.0',
            'base_directory': str(self.base_directory),
            'configuration': self.config,
            'metadata_cache_size': len(self.metadata_cache),
            'metadata_file_path': str(self.metadata_file),
            'supported_features': [
                'domain_based_organization',
                'duplicate_detection',
                'timestamped_naming',
                'metadata_management',
                'bulk_export',
                'content_filtering',
                'storage_statistics',
                'orphaned_file_cleanup'
            ]
        }
    
    def __repr__(self) -> str:
        return f"FileManager(base_dir={self.base_directory}, files={len(self.metadata_cache)})"
