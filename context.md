# Firecrawl-Streamlit Web Scraper Project Context

## **Project Overview**
Create a professional Streamlit web application that uses Firecrawl to scrape JavaScript-heavy websites, specifically optimized for Google CodeLabs pages and similar dynamic content sites. The application should output clean markdown files suitable for AI agents like ChatGPT while remaining human-readable.

## **Target Requirements**

**Primary Scraping Targets:**
- Google CodeLabs pages (JavaScript-rendered content)
- Dynamic websites with progressive content loading
- Multi-step tutorials with interactive elements
- Sites requiring JavaScript execution for full content display

**Output Requirements:**
- **Primary format**: Clean markdown optimized for LLM consumption
- **Secondary format**: Structured JSON with metadata
- **File organization**: Organized directory structure with timestamps
- **AI-ready formatting**: Proper headers, code blocks, and content segmentation

## **Technical Stack**
- **Frontend**: Streamlit for web interface
- **Scraping Engine**: Firecrawl (self-hosted local instance)
- **Language**: Python 3.11+
- **Data Processing**: Pandas for analytics
- **File Management**: Pathlib for cross-platform compatibility

## **Project Structure**
```
firecrawl-local/
├── streamlit-app/
│   ├── app.py                    # Main Streamlit interface
│   ├── firecrawl_client.py      # Firecrawl API wrapper
│   ├── data_processor.py        # Content processing & formatting
│   ├── file_manager.py          # File operations & organization
│   └── requirements.txt         # Dependencies
├── data/
│   ├── scraped/                 # Raw scraped content
│   │   ├── markdown/           # Markdown files by domain
│   │   ├── json/              # Structured data exports
│   │   └── metadata/          # Scraping metadata & logs
│   └── exports/                # Processed exports for AI
├── config/
│   ├── scraping_profiles.json  # Pre-configured site profiles
│   └── firecrawl_config.yaml  # Firecrawl settings
└── firecrawl/                  # Self-hosted Firecrawl repository
```

## **Core Application Features**

### **1. Streamlit Interface Design**
Create a clean, professional interface with:

**Header Section:**
- App title: "🔥 Advanced Web Content Extractor"
- Connection status indicator for local Firecrawl instance
- Real-time scraping progress bar

**Input Section:**
- **URL Input**: Text area for multiple URLs (one per line)
- **Scraping Mode Selection**: Radio buttons for "Single Page" vs "Deep Crawl"
- **Content Type**: Dropdown for "Tutorial/CodeLab", "Documentation", "General Web Content"
- **Advanced Options**: Expandable section with wait times, depth limits, custom selectors

**Output Controls:**
- **Format Selection**: Checkboxes for Markdown, JSON, HTML
- **AI Optimization**: Toggle for "Optimize for LLM Training" 
- **File Naming**: Options for timestamp, domain-based, or custom naming
- **Export Location**: Directory picker for output destination

### **2. Firecrawl Integration (firecrawl_client.py)**
```python
class FirecrawlLocalClient:
    def __init__(self, base_url="http://localhost:3002"):
        # Initialize connection to self-hosted Firecrawl
        
    def scrape_codelab_optimized(self, url, options=None):
        # Specialized method for Google CodeLabs
        # Include JavaScript wait times, scroll handling
        # Extract step-by-step content, code blocks, images
        
    def batch_scrape_urls(self, urls, callback=None):
        # Process multiple URLs with progress callbacks
        
    def health_check(self):
        # Verify Firecrawl service availability
```

**Scraping Configuration for CodeLabs:**
- **JavaScript Execution**: Enable with 3-5 second wait times
- **Content Extraction**: Focus on main tutorial content, exclude navigation
- **Code Block Preservation**: Maintain formatting for technical content
- **Image Handling**: Download and reference locally or extract alt text
- **Step Navigation**: Handle multi-step tutorials with pagination

### **3. Content Processing (data_processor.py)**
**AI-Optimized Markdown Generation:**
```python
class ContentProcessor:
    def optimize_for_llm(self, raw_content):
        # Clean and structure content for AI consumption
        # Remove redundant navigation, ads, footers
        # Enhance code block formatting
        # Add clear section headers
        # Preserve technical accuracy
        
    def extract_metadata(self, scraping_result):
        # Extract title, description, author, publication date
        # Identify content type (tutorial, documentation, etc.)
        # Generate content summary
        
    def create_ai_friendly_structure(self, content):
        # Add clear markdown headers (H1, H2, H3)
        # Separate code blocks with proper language tagging
        # Create table of contents for long content
        # Add context markers for multi-step processes
```

### **4. File Management (file_manager.py)**
**Organized Storage System:**
- **Domain-based folders**: Separate folders for each website
- **Timestamp organization**: YYYY-MM-DD_HH-MM format
- **Content categorization**: Separate directories for different content types
- **Duplicate detection**: Check for existing content to avoid re-scraping
- **Export packaging**: Create ZIP archives for easy AI training data distribution

### **5. Advanced Features**

**Pre-configured Profiles:**
Create scraping profiles for common sites:
```json
{
  "google_codelabs": {
    "wait_for_js": 5000,
    "scroll_pause": 2000,
    "exclude_selectors": [".navigation", ".footer", ".sidebar"],
    "include_code_blocks": true,
    "follow_next_links": true
  }
}
```

**Real-time Monitoring:**
- **Progress Indicators**: Show current URL being processed
- **Success/Error Tracking**: Visual indicators for completed/failed scrapes
- **Content Preview**: Display first 500 characters of scraped content
- **Statistics Dashboard**: Pages scraped, data volume, processing time

**Error Handling & Retry Logic:**
- Automatic retry for failed requests (up to 3 attempts)
- Detailed error logging with specific failure reasons
- Graceful degradation for JavaScript-heavy sites
- User-friendly error messages with suggested solutions

### **6. Output Specifications**

**AI-Optimized Markdown Format:**
```markdown
# [Page Title]

**Source URL:** [Original URL]
**Scraped Date:** [Timestamp]
**Content Type:** [Tutorial/Documentation/etc.]

## Overview
[Extracted meta description or auto-generated summary]

## Content
[Main content with preserved formatting]

### Code Examples
```
[Preserved code blocks with proper syntax highlighting]
```

## Metadata
- **Word Count:** [Number]
- **Code Blocks:** [Count]
- **Images:** [Count with descriptions]
- **External Links:** [Count]
```

**JSON Metadata Export:**
```json
{
  "url": "source_url",
  "title": "extracted_title",
  "scraped_timestamp": "ISO_timestamp",
  "content_type": "detected_type",
  "word_count": 0,
  "code_blocks": [],
  "images": [],
  "external_links": [],
  "ai_optimization_applied": true
}
```

## **User Interface Requirements**

**Main Dashboard:**
- **Left Sidebar**: Configuration options, scraping profiles, history
- **Center Panel**: URL input, progress display, content preview
- **Right Panel**: Export options, file management, statistics

**Progress Visualization:**
- **Real-time progress bar** for batch operations
- **Live log display** showing current scraping status
- **Success/failure indicators** for each URL
- **ETA calculation** for large batch operations

**Results Management:**
- **Tabbed interface** for different output formats
- **Quick preview** of scraped content
- **Download buttons** for individual files or batch exports
- **Search and filter** through scraped content history

## **Technical Implementation Notes**

**Firecrawl Configuration:**
- Connect to local Firecrawl instance on `localhost:3002`
- Configure for optimal JavaScript rendering
- Set appropriate timeouts for dynamic content loading
- Enable markdown output format as primary choice

**Error Handling:**
- Implement comprehensive try-catch blocks
- Provide user-friendly error messages
- Log detailed errors for debugging
- Offer retry mechanisms for failed scrapes

**Performance Optimization:**
- Implement async processing for multiple URLs
- Add progress callbacks for user feedback
- Cache successful scrapes to avoid duplicates
- Optimize memory usage for large content processing

**File Organization:**
- Create clear directory structures automatically
- Implement file naming conventions for easy sorting
- Add metadata files for each scraping session
- Provide export options in multiple formats

## **Testing Requirements**

**Primary Test URLs:**
1. `https://codelabs.developers.google.com/deploy-manage-observe-adk-cloud-run#`
2. `https://codelabs.developers.google.com/instavibe-adk-multi-agents/instructions?hl=en#`

**Success Criteria:**
- Successfully extract all tutorial steps and content
- Preserve code blocks with proper formatting
- Generate clean, readable markdown suitable for AI training
- Handle JavaScript-rendered content without missing information
- Create organized file structure with proper metadata

**Additional Testing:**
- Test with other dynamic websites
- Verify markdown output quality for LLM consumption
- Test batch processing with multiple URLs
- Validate error handling with invalid URLs

## **Dependencies (requirements.txt)**
```txt
streamlit>=1.28.0
firecrawl-py>=1.0.0
requests>=2.31.0
pandas>=2.0.0
pathlib>=1.0.0
python-dotenv>=1.0.0
pydantic>=2.0.0
```

**Implementation Priority:**
1. Basic Streamlit interface with URL input
2. Firecrawl client integration and testing
3. Content processing and markdown optimization
4. File management and organization
5. Advanced features and error handling
6. UI polish and user experience improvements

**Please ensure the application is production-ready, well-documented, and includes comprehensive error handling for robust scraping of JavaScript-heavy websites like Google CodeLabs.**