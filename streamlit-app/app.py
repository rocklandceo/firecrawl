"""
Firecrawl-Streamlit Web Scraper
Professional web application for scraping JavaScript-heavy websites using Firecrawl
Optimized for Google CodeLabs and similar dynamic content sites
"""

import streamlit as st
import os
import json
from pathlib import Path
from datetime import datetime
from urllib.parse import urlparse
from firecrawl_client import FirecrawlClient
from data_processor import ContentProcessor
from file_manager import FileManager

# Page Configuration
st.set_page_config(
    page_title="Firecrawl Web Scraper",
    page_icon="🔥",
    layout="wide",
    initial_sidebar_state="expanded"
)

def main():
    """Main application entry point"""
    
    # Application Header
    st.title("🔥 Firecrawl Web Scraper")
    st.markdown("**Professional web scraping for JavaScript-heavy websites**")
    st.markdown("Optimized for Google CodeLabs, dynamic tutorials, and AI-ready content extraction")
    
    # Sidebar Configuration
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        # Connection Status
        st.subheader("🔗 Connection Status")
        connection_status = check_firecrawl_connection()
        if connection_status:
            st.success("✅ Firecrawl API Connected")
        else:
            st.error("❌ Firecrawl API Disconnected")
            st.info("💡 Check your FIRECRAWL_API_KEY in .env file")
        
        # Output Format Selection
        output_format = st.selectbox(
            "Output Format",
            ["Markdown (Primary)", "JSON with Metadata", "Both Formats"],
            help="Choose the primary output format for scraped content"
        )
        
        # JavaScript Execution Settings
        js_timeout = st.slider(
            "JavaScript Timeout (seconds)",
            min_value=3,
            max_value=30,
            value=10,
            help="Time to wait for JavaScript content to load"
        )
        
        # Content Processing Options
        st.subheader("Content Processing")
        preserve_code_blocks = st.checkbox("Preserve Code Blocks", value=True)
        optimize_for_ai = st.checkbox("AI-Friendly Formatting", value=True)
        clean_navigation = st.checkbox("Remove Navigation Elements", value=True)
    
    # Main Content Area
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.header("🌐 URL Input")
        
        # Single URL Input
        with st.form("single_url_form"):
            single_url = st.text_input(
                "Enter URL to scrape:",
                placeholder="https://codelabs.developers.google.com/your-codelab-here",
                help="Paste the URL of the webpage you want to scrape"
            )
            
            single_submit = st.form_submit_button("🚀 Scrape Single URL", type="primary")
        
        # Batch URL Input
        st.subheader("📋 Batch Processing")
        with st.form("batch_urls_form"):
            batch_urls = st.text_area(
                "Enter multiple URLs (one per line):",
                placeholder="https://example1.com\nhttps://example2.com\nhttps://example3.com",
                height=100,
                help="Enter multiple URLs separated by line breaks for batch processing"
            )
            
            batch_submit = st.form_submit_button("⚡ Batch Scrape", type="secondary")
    
    with col2:
        st.header("📊 Status")
        
        # Status Placeholder
        status_placeholder = st.empty()
        
        # Quick Stats
        with st.container():
            st.metric("Total Scraped", "0", "0")
            st.metric("Success Rate", "0%", "0%")
            st.metric("Processing Time", "0s", "0s")
    
    # Processing Logic
    if single_submit and single_url:
        process_single_url(single_url, output_format, js_timeout, {
            'preserve_code_blocks': preserve_code_blocks,
            'optimize_for_ai': optimize_for_ai,
            'clean_navigation': clean_navigation
        })
    
    if batch_submit and batch_urls:
        urls = [url.strip() for url in batch_urls.split('\n') if url.strip()]
        if urls:
            process_batch_urls(urls, output_format, js_timeout, {
                'preserve_code_blocks': preserve_code_blocks,
                'optimize_for_ai': optimize_for_ai,
                'clean_navigation': clean_navigation
            })
    
    # Test URLs Section
    with st.expander("🧪 Test with Sample URLs"):
        st.markdown("**Google CodeLabs Test URLs:**")
        test_urls = [
            "https://codelabs.developers.google.com/deploy-manage-observe-adk-cloud-run#",
            "https://codelabs.developers.google.com/instavibe-adk-multi-agents/instructions?hl=en#"
        ]
        
        for i, url in enumerate(test_urls, 1):
            col_url, col_button = st.columns([3, 1])
            with col_url:
                st.code(url)
            with col_button:
                if st.button(f"Test {i}", key=f"test_url_{i}"):
                    process_single_url(url, output_format, js_timeout, {
                        'preserve_code_blocks': preserve_code_blocks,
                        'optimize_for_ai': optimize_for_ai,
                        'clean_navigation': clean_navigation
                    })

def process_single_url(url: str, format_type: str, timeout: int, options: dict):
    """Process a single URL for scraping"""
    st.info(f"🔄 Processing: {url}")
    
    try:
        # Initialize Firecrawl client
        client = get_firecrawl_client()
        if not client:
            st.error("❌ Firecrawl client not available. Please check your API key configuration.")
            return
        
        # Determine output formats based on selection
        formats = []
        if "Markdown" in format_type:
            formats.append("markdown")
        if "JSON" in format_type:
            formats.append("html")
        if not formats:
            formats = ["markdown"]
        
        with st.spinner("Scraping content..."):
            # Perform the scrape
            result = client.scrape_url(
                url=url,
                formats=formats,
                wait_for_js=timeout,
                include_metadata=True
            )
        
        if result['status'] == 'success':
            st.success(f"Successfully scraped: {url}")
            
            # Process content with ContentProcessor
            content_processor = get_content_processor()
            file_manager = get_file_manager()
            
            if content_processor:
                with st.spinner("Optimizing content for AI consumption..."):
                    processed_result = content_processor.process_content(
                        content=result['content'],
                        url=url,
                        options={
                            'preserve_code_blocks': True,
                            'optimize_for_ai': True,
                            'clean_navigation': True,
                            'include_metadata': True
                        }
                    )
                    
                    # Save processed content to file management system
                    if file_manager and processed_result:
                        try:
                            file_id = file_manager.store_processed_content(
                                processed_result,
                                tags=['single_url', 'web_scrape']
                            )
                            st.success(f"💾 Content saved to file system (ID: {file_id})")
                        except Exception as e:
                            st.warning(f"⚠️ Content processed but not saved: {e}")
                
                # Create tabs for different views
                tab1, tab2, tab3, tab4 = st.tabs(["📄 Processed Content", "🔍 Analysis", "💾 Raw Data", "⚙️ Processing Info"])
                
                with tab1:
                    if 'optimized_content' in processed_result and processed_result['optimized_content']:
                        opt_content = processed_result['optimized_content']
                        
                        # Display optimized markdown
                        if 'markdown' in opt_content and opt_content['markdown']:
                            st.subheader("🎯 AI-Optimized Markdown")
                            st.text_area(
                                "Optimized Content", 
                                opt_content['markdown'], 
                                height=400,
                                help="Content optimized for AI/LLM consumption with preserved code blocks and enhanced formatting"
                            )
                            
                            # Download button for processed content
                            st.download_button(
                                label="📥 Download Processed Markdown",
                                data=opt_content['markdown'],
                                file_name=f"processed_{urlparse(url).netloc}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md",
                                mime="text/markdown"
                            )
                
                with tab2:
                    st.subheader("📊 Content Analysis")
                    
                    if 'metadata' in processed_result:
                        metadata = processed_result['metadata']
                        
                        # Content statistics
                        col1, col2, col3, col4 = st.columns(4)
                        
                        with col1:
                            st.metric(
                                "Word Count", 
                                metadata.get('content_stats', {}).get('word_count', 0)
                            )
                        
                        with col2:
                            st.metric(
                                "Code Blocks", 
                                metadata.get('content_stats', {}).get('code_block_count', 0)
                            )
                        
                        with col3:
                            st.metric(
                                "Headings", 
                                metadata.get('content_stats', {}).get('heading_count', 0)
                            )
                        
                        with col4:
                            st.metric(
                                "Quality Score", 
                                f"{metadata.get('content_quality_score', 0):.0f}/100"
                            )
                        
                        # Reading time and structure info
                        st.info(f"📖 Estimated reading time: {metadata.get('estimated_reading_time_minutes', 1)} minutes")
                        
                        # Headings structure
                        if metadata.get('headings'):
                            st.subheader("🗂️ Content Structure")
                            for heading in metadata['headings']:
                                indent = "  " * (heading['level'] - 1)
                                st.write(f"{indent}{'#' * heading['level']} {heading['text']}")
                        
                        # Code blocks summary
                        if processed_result.get('optimized_content', {}).get('code_blocks'):
                            st.subheader("💻 Code Blocks Detected")
                            code_blocks = processed_result['optimized_content']['code_blocks']
                            for i, block in enumerate(code_blocks):
                                with st.expander(f"Code Block {i+1}: {block.get('language', 'unknown')} ({block.get('line_count', 0)} lines)"):
                                    st.code(block.get('content', ''), language=block.get('language', 'text'))
                
                with tab3:
                    st.subheader("📦 Raw Scraped Data")
                    
                    content = result['content']
                    if 'markdown' in content:
                        st.markdown("**Original Markdown:**")
                        st.text_area("Raw Markdown", content['markdown'], height=300)
                    
                    if 'html' in content:
                        st.markdown("**HTML Content:**")
                        with st.expander("View Raw HTML"):
                            st.code(content['html'], language='html')
                    
                    # Original scraping metadata
                    st.subheader("🔍 Scraping Metadata")
                    st.json({
                        'processing_time': f"{result['processing_time_seconds']:.2f}s",
                        'content_hash': result['content_hash'][:16] + '...',
                        'formats': result['formats_requested'],
                        'scraped_at': result['scraped_at']
                    })
                
                with tab4:
                    st.subheader("⚙️ Processing Information")
                    
                    if 'processing_steps' in processed_result:
                        st.write("**Processing Steps Completed:**")
                        for step in processed_result['processing_steps']:
                            st.write(f"✅ {step.replace('_', ' ').title()}")
                    
                    if 'processing_options' in processed_result:
                        st.write("**Processing Options:**")
                        st.json(processed_result['processing_options'])
                    
                    # Processor info
                    processor_info = processor.get_processor_info()
                    st.write("**Processor Configuration:**")
                    st.json(processor_info)
            
            else:
                # Fallback to basic display if processor unavailable
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    st.subheader("📄 Scraped Content")
                    
                    content = result['content']
                    if 'markdown' in content:
                        st.markdown("**Markdown Content:**")
                        st.text_area("Markdown", content['markdown'], height=300)
                    
                    if 'html' in content:
                        st.markdown("**HTML Content:**")
                        with st.expander("View HTML"):
                            st.code(content['html'], language='html')
                
                with col2:
                    st.subheader("📊 Metadata")
                    st.json({
                        'processing_time': f"{result['processing_time_seconds']:.2f}s",
                        'content_hash': result['content_hash'][:16] + '...',
                        'formats': result['formats_requested'],
                        'scraped_at': result['scraped_at']
                    })
        else:
            st.error(f"❌ Failed to scrape: {result['error_message']}")
            st.json(result)
            
    except Exception as e:
        st.error(f"❌ Error during scraping: {str(e)}")
        st.exception(e)

def process_batch_urls(urls: list, format_type: str, timeout: int, options: dict):
    """Process multiple URLs for batch scraping"""
    st.info(f"🔄 Batch processing {len(urls)} URLs")
    
    try:
        # Initialize Firecrawl client
        client = get_firecrawl_client()
        if not client:
            st.error("❌ Firecrawl client not available. Please check your API key configuration.")
            return
        
        # Progress tracking
        progress_bar = st.progress(0)
        status_text = st.empty()
        results_container = st.container()
        
        successful_scrapes = 0
        failed_scrapes = 0
        results = []
        
        # Determine output formats
        formats = []
        if "Markdown" in format_type:
            formats.append("markdown")
        if "JSON" in format_type:
            formats.append("html")
        if not formats:
            formats = ["markdown"]
        
        for i, url in enumerate(urls):
            status_text.text(f"Processing {i+1}/{len(urls)}: {url}")
            progress_bar.progress((i + 1) / len(urls))
            
            try:
                result = client.scrape_url(
                    url=url,
                    formats=formats,
                    wait_for_js=timeout,
                    include_metadata=True
                )
                
                results.append(result)
                
                if result['status'] == 'success':
                    successful_scrapes += 1
                    with results_container:
                        st.success(f"✅ {i+1}. {url}")
                else:
                    failed_scrapes += 1
                    with results_container:
                        st.error(f"❌ {i+1}. {url}: {result.get('error_message', 'Unknown error')}")
                        
            except Exception as e:
                failed_scrapes += 1
                results.append({
                    'url': url,
                    'status': 'error',
                    'error_message': str(e)
                })
                with results_container:
                    st.error(f"❌ {i+1}. {url}: {str(e)}")
        
        # Final summary
        st.success(f"🎉 Batch processing complete!")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total URLs", len(urls))
        with col2:
            st.metric("Successful", successful_scrapes)
        with col3:
            st.metric("Failed", failed_scrapes)
        
        # Process successful results with ContentProcessor if available
        processor = get_content_processor()
        file_manager = get_file_manager()
        processed_results = []
        saved_file_ids = []
        
        if processor and successful_scrapes > 0:
            st.info("🔧 Processing scraped content for AI optimization...")
            
            processing_progress = st.progress(0)
            processed_count = 0
            
            for result in results:
                if result.get('status') == 'success':
                    try:
                        processed_result = processor.process_content(
                            content=result['content'],
                            url=result['url'],
                            options={
                                'preserve_code_blocks': True,
                                'optimize_for_ai': True,
                                'clean_navigation': True,
                                'include_metadata': True
                            }
                        )
                        processed_results.append(processed_result)
                        
                        # Save processed content to file management system
                        if file_manager:
                            try:
                                file_id = file_manager.store_processed_content(
                                    processed_result,
                                    tags=['batch_processing', 'web_scrape']
                                )
                                saved_file_ids.append(file_id)
                            except Exception as e:
                                logger.error(f"Failed to save content for {result['url']}: {e}")
                        
                        processed_count += 1
                        processing_progress.progress(processed_count / successful_scrapes)
                    except Exception as e:
                        logger.error(f"Failed to process content for {result['url']}: {e}")
                        processed_results.append({
                            'source_url': result['url'],
                            'status': 'processing_error',
                            'error_message': str(e)
                        })
            
            st.success(f"✅ Content processing completed for {processed_count} URLs!")
        
        # Display batch analysis and download options
        if processed_results:
            st.subheader("📊 Batch Analysis Summary")
            
            # Aggregate statistics
            total_words = sum(
                r.get('metadata', {}).get('content_stats', {}).get('word_count', 0) 
                for r in processed_results if r.get('status') != 'processing_error'
            )
            total_code_blocks = sum(
                r.get('metadata', {}).get('content_stats', {}).get('code_block_count', 0) 
                for r in processed_results if r.get('status') != 'processing_error'
            )
            avg_quality_score = sum(
                r.get('metadata', {}).get('content_quality_score', 0) 
                for r in processed_results if r.get('status') != 'processing_error'
            ) / max(1, len([r for r in processed_results if r.get('status') != 'processing_error']))
            
            # Display aggregate metrics
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Total Words", f"{total_words:,}")
            with col2:
                st.metric("Total Code Blocks", total_code_blocks)
            with col3:
                st.metric("Avg Quality Score", f"{avg_quality_score:.1f}/100")
            with col4:
                st.metric("Processing Success Rate", f"{(processed_count/successful_scrapes*100):.0f}%" if successful_scrapes > 0 else "0%")
            
            # Download options for processed content
            st.subheader("📥 Download Options")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                # Download all processed markdown as a single file
                if st.button("📄 Download All Processed Markdown"):
                    combined_markdown = "\n\n---\n\n".join([
                        f"# {urlparse(r['source_url']).netloc}\n\nSource: {r['source_url']}\n\n{r.get('optimized_content', {}).get('markdown', '')}"
                        for r in processed_results 
                        if r.get('status') != 'processing_error' and r.get('optimized_content', {}).get('markdown')
                    ])
                    
                    st.download_button(
                        label="📥 Download Combined Markdown",
                        data=combined_markdown,
                        file_name=f"batch_processed_content_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md",
                        mime="text/markdown"
                    )
            
            with col2:
                # Download processed results as JSON
                if st.button("📊 Download Analysis JSON"):
                    st.download_button(
                        label="📥 Download Analysis Data",
                        data=json.dumps(processed_results, indent=2, default=str),
                        file_name=f"batch_analysis_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                        mime="application/json"
                    )
            
            with col3:
                # Download raw scraping results
                if st.button("📦 Download Raw Scraping Data"):
                    st.download_button(
                        label="📥 Download Raw Results",
                        data=json.dumps(results, indent=2, default=str),
                        file_name=f"batch_scrape_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                        mime="application/json"
                    )
            
            # Individual result preview
            st.subheader("🔍 Individual Results Preview")
            
            if processed_results:
                for i, result in enumerate(processed_results[:5]):  # Show first 5 results
                    if result.get('status') != 'processing_error':
                        with st.expander(f"{i+1}. {urlparse(result['source_url']).netloc} - Quality: {result.get('metadata', {}).get('content_quality_score', 0):.0f}/100"):
                            
                            # Quick stats
                            metadata = result.get('metadata', {})
                            stats = metadata.get('content_stats', {})
                            
                            col1, col2, col3 = st.columns(3)
                            with col1:
                                st.write(f"**Words:** {stats.get('word_count', 0)}")
                            with col2:
                                st.write(f"**Code Blocks:** {stats.get('code_block_count', 0)}")
                            with col3:
                                st.write(f"**Reading Time:** {metadata.get('estimated_reading_time_minutes', 1)} min")
                            
                            # Content preview
                            content = result.get('optimized_content', {}).get('markdown', '')
                            if content:
                                preview = content[:500] + "..." if len(content) > 500 else content
                                st.text_area(f"Preview ({len(content)} chars)", preview, height=100)
                    else:
                        with st.expander(f"{i+1}. {result['source_url']} - ❌ Processing Error"):
                            st.error(f"Error: {result.get('error_message', 'Unknown error')}")
                
                if len(processed_results) > 5:
                    st.info(f"📄 Showing first 5 results. Total processed: {len(processed_results)}")
        
        else:
            # Fallback download for raw results only
            if results and st.button("📥 Download Raw Results as JSON"):
                st.download_button(
                    label="Download Batch Results",
                    data=json.dumps(results, indent=2, default=str),
                    file_name=f"batch_scrape_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                    mime="application/json"
                )
            
    except Exception as e:
        st.error(f"❌ Error during batch processing: {str(e)}")
        st.exception(e)

    # File Management Interface
    st.markdown("---")
    st.header("📁 File Management")
    st.markdown("**Manage your saved scraped content with advanced organization and export features**")
    
    file_manager = get_file_manager()
    if file_manager:
        # Get storage statistics
        try:
            storage_stats = file_manager.get_storage_statistics()
            
            # Display storage overview
            st.subheader("📊 Storage Overview")
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Total Files", storage_stats.get('total_files', 0))
            with col2:
                st.metric("Storage Used", f"{storage_stats.get('total_size_mb', 0):.1f} MB")
            with col3:
                avg_quality = storage_stats.get('average_quality_score', 0)
                st.metric("Avg Quality", f"{avg_quality:.0f}/100")
            with col4:
                domains_count = len(storage_stats.get('domains', {}))
                st.metric("Domains", domains_count)
            
            # File filtering and search
            st.subheader("🔍 Browse & Filter Files")
            
            col1, col2 = st.columns([1, 1])
            
            with col1:
                # Domain filter
                domains = list(storage_stats.get('domains', {}).keys())
                domain_filter = st.selectbox(
                    "Filter by Domain",
                    ["All Domains"] + domains,
                    help="Filter files by source domain"
                )
                
                # Quality filter
                min_quality = st.slider(
                    "Minimum Quality Score",
                    min_value=0,
                    max_value=100,
                    value=0,
                    help="Show only files with quality score above this threshold"
                )
            
            with col2:
                # Tag filter
                all_tags = set()
                if hasattr(file_manager, 'metadata_cache'):
                    for metadata in file_manager.metadata_cache.values():
                        if hasattr(metadata, 'tags') and metadata.tags:
                            all_tags.update(metadata.tags)
                
                tag_filter = st.multiselect(
                    "Filter by Tags",
                    sorted(list(all_tags)),
                    help="Show only files with selected tags"
                )
                
                # Date range filter
                st.write("**Filter by Date:**")
                date_range = st.date_input(
                    "Date Range",
                    value=[],
                    help="Filter files by creation date range"
                )
            
            # Apply filters and get file list
            filter_domain = None if domain_filter == "All Domains" else domain_filter
            filter_min_quality = min_quality if min_quality > 0 else None
            filter_tags = tag_filter if tag_filter else None
            
            try:
                filtered_files = file_manager.list_files(
                    domain=filter_domain,
                    min_quality_score=filter_min_quality,
                    tags=filter_tags
                )
                
                st.subheader(f"📄 Files ({len(filtered_files)} found)")
                
                if filtered_files:
                    # Bulk actions
                    st.markdown("**Bulk Actions:**")
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        if st.button("📦 Export All Filtered Files"):
                            try:
                                with st.spinner("Creating export..."):
                                    file_ids = [f.file_id for f in filtered_files]
                                    export_path = file_manager.export_files(
                                        file_ids=file_ids,
                                        export_format='zip',
                                        include_metadata=True
                                    )
                                
                                st.success(f"✅ Export created: {export_path.name}")
                                
                                # Provide download link
                                with open(export_path, 'rb') as f:
                                    st.download_button(
                                        label="⬇️ Download Export",
                                        data=f.read(),
                                        file_name=export_path.name,
                                        mime="application/zip"
                                    )
                            except Exception as e:
                                st.error(f"Export failed: {e}")
                    
                    with col2:
                        if st.button("🧹 Cleanup Orphaned Files"):
                            try:
                                with st.spinner("Cleaning up..."):
                                    orphaned_count = file_manager.cleanup_orphaned_files()
                                st.success(f"✅ Removed {orphaned_count} orphaned files")
                                st.rerun()
                            except Exception as e:
                                st.error(f"Cleanup failed: {e}")
                    
                    with col3:
                        if st.button("📊 Refresh Statistics"):
                            st.rerun()
                    
                    st.markdown("---")
                    
                    # Display files with pagination
                    files_per_page = 10
                    total_pages = (len(filtered_files) + files_per_page - 1) // files_per_page
                    
                    if total_pages > 1:
                        page = st.number_input(
                            "Page",
                            min_value=1,
                            max_value=total_pages,
                            value=1,
                            help=f"Showing {files_per_page} files per page"
                        )
                        start_idx = (page - 1) * files_per_page
                        end_idx = start_idx + files_per_page
                        display_files = filtered_files[start_idx:end_idx]
                    else:
                        display_files = filtered_files
                    
                    # Display file cards
                    for i, file_metadata in enumerate(display_files):
                        with st.expander(f"📄 {file_metadata.domain} | Quality: {file_metadata.quality_score:.0f}/100 | {file_metadata.created_at[:10]}"):
                            col1, col2 = st.columns([2, 1])
                            
                            with col1:
                                st.write(f"**URL:** {file_metadata.original_url}")
                                st.write(f"**File ID:** `{file_metadata.file_id}`")
                                st.write(f"**Content Type:** {file_metadata.content_type}")
                                st.write(f"**File Size:** {file_metadata.file_size:,} bytes")
                                if hasattr(file_metadata, 'tags') and file_metadata.tags:
                                    st.write(f"**Tags:** {', '.join(file_metadata.tags)}")
                                else:
                                    st.write("**Tags:** None")
                                
                                # Processing info
                                if hasattr(file_metadata, 'processing_info') and file_metadata.processing_info:
                                    processing_info = file_metadata.processing_info
                                    if 'content_stats' in processing_info:
                                        stats = processing_info['content_stats']
                                        st.write(f"**Stats:** {stats.get('word_count', 0)} words, {stats.get('code_block_count', 0)} code blocks")
                            
                            with col2:
                                st.write(f"**Created:** {file_metadata.created_at[:19]}")
                                st.write(f"**Modified:** {file_metadata.last_modified[:19]}")
                                
                                # Action buttons
                                col2_1, col2_2 = st.columns(2)
                                
                                with col2_1:
                                    if st.button(f"👁️ View", key=f"view_{file_metadata.file_id}"):
                                        content = file_manager.get_content(file_metadata.file_id)
                                        if content:
                                            st.text_area(
                                                f"Content Preview ({len(content)} chars)",
                                                content[:1000] + "..." if len(content) > 1000 else content,
                                                height=200,
                                                key=f"preview_{file_metadata.file_id}"
                                            )
                                        else:
                                            st.error("Content not found")
                                
                                with col2_2:
                                    if st.button(f"🗑️ Delete", key=f"delete_{file_metadata.file_id}"):
                                        if file_manager.delete_file(file_metadata.file_id):
                                            st.success("File deleted")
                                            st.rerun()
                                        else:
                                            st.error("Delete failed")
                                
                                # Download button
                                content = file_manager.get_content(file_metadata.file_id)
                                if content:
                                    file_extension = ".md" if file_metadata.content_type in ['markdown', 'processed_markdown'] else ".txt"
                                    filename = f"{file_metadata.file_id}{file_extension}"
                                    
                                    st.download_button(
                                        label="⬇️ Download",
                                        data=content,
                                        file_name=filename,
                                        mime="text/plain",
                                        key=f"download_{file_metadata.file_id}"
                                    )
                else:
                    st.info("📑 No files found matching the current filters.")
                    
                    if storage_stats.get('total_files', 0) > 0:
                        st.markdown("💡 **Tip:** Try adjusting your filters to see more files.")
                    else:
                        st.markdown("💡 **Tip:** Start by scraping some URLs to see saved content here.")
                        
            except Exception as e:
                st.error(f"Failed to list files: {e}")
                
        except Exception as e:
            st.error(f"Failed to get storage statistics: {e}")
    
    else:
        st.error("❌ File Manager not available")

@st.cache_resource
def get_firecrawl_client():
    """Get or create a cached Firecrawl client instance"""
    try:
        client = FirecrawlClient()
        return client
    except Exception as e:
        st.error(f"Failed to initialize Firecrawl client: {e}")
        return None

@st.cache_resource
def get_content_processor():
    """Get cached ContentProcessor instance."""
    return ContentProcessor()

@st.cache_resource
def get_file_manager():
    """Get cached FileManager instance."""
    return FileManager()

def check_firecrawl_connection():
    """Check if Firecrawl client is available and configured"""
    client = get_firecrawl_client()
    if not client:
        return False
    
    connection_result = client.test_connection()
    return connection_result['status'] == 'success'

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666;'>
    <p>🔥 Firecrawl Web Scraper | Optimized for JavaScript-heavy websites | AI-ready content extraction</p>
</div>
""", unsafe_allow_html=True)

if __name__ == "__main__":
    main()
