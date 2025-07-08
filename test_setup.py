#!/usr/bin/env python3
"""
Smoke Test Script for Firecrawl-Streamlit Web Scraper
Validates basic setup, dependencies, and initial configuration
"""

import sys
import os
import importlib
from pathlib import Path
import yaml
from datetime import datetime

def print_header(title):
    """Print a formatted header"""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")

def print_success(message):
    """Print success message"""
    print(f"✅ {message}")

def print_error(message):
    """Print error message"""
    print(f"❌ {message}")

def print_warning(message):
    """Print warning message"""
    print(f"⚠️  {message}")

def check_python_version():
    """Check Python version compatibility"""
    print_header("Python Version Check")
    
    version = sys.version_info
    print(f"Python version: {version.major}.{version.minor}.{version.micro}")
    
    if version.major >= 3 and version.minor >= 11:
        print_success("Python version is compatible (3.11+ required)")
        return True
    else:
        print_error(f"Python 3.11+ required, found {version.major}.{version.minor}")
        return False

def check_dependencies():
    """Check if required dependencies are available"""
    print_header("Dependency Check")
    
    required_packages = [
        'streamlit',
        'requests',
        'pandas',
        'pathlib',
        'dotenv',
        'pydantic',
        'yaml',
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            if package == 'yaml':
                importlib.import_module('yaml')
            elif package == 'dotenv':
                importlib.import_module('dotenv')
            else:
                importlib.import_module(package)
            print_success(f"{package} is available")
        except ImportError:
            print_error(f"{package} is missing")
            missing_packages.append(package)
    
    if missing_packages:
        print_warning(f"Install missing packages: pip install {' '.join(missing_packages)}")
        return False
    
    print_success("All core dependencies are available")
    return True

def check_firecrawl_dependency():
    """Check Firecrawl-specific dependency"""
    print_header("Firecrawl Dependency Check")
    
    try:
        import firecrawl
        print_success("firecrawl-py is available")
        return True
    except ImportError:
        print_error("firecrawl-py is missing")
        print_warning("Install with: pip install firecrawl-py")
        return False

def check_directory_structure():
    """Verify project directory structure"""
    print_header("Directory Structure Check")
    
    project_root = Path(__file__).parent
    
    required_dirs = [
        'streamlit-app',
        'data',
        'data/scraped',
        'data/scraped/markdown',
        'data/scraped/json',
        'data/scraped/metadata',
        'data/exports',
        'config',
        'logs'
    ]
    
    all_exist = True
    
    for dir_path in required_dirs:
        full_path = project_root / dir_path
        if full_path.exists():
            print_success(f"{dir_path}/ exists")
        else:
            print_error(f"{dir_path}/ is missing")
            all_exist = False
    
    return all_exist

def check_config_files():
    """Check configuration files"""
    print_header("Configuration Files Check")
    
    project_root = Path(__file__).parent
    
    config_files = [
        'config/firecrawl.yaml',
        'config/app_settings.yaml',
        '.env.example'
    ]
    
    all_exist = True
    
    for config_file in config_files:
        file_path = project_root / config_file
        if file_path.exists():
            print_success(f"{config_file} exists")
            
            # Try to load YAML files
            if config_file.endswith('.yaml'):
                try:
                    with open(file_path, 'r') as f:
                        yaml.safe_load(f)
                    print_success(f"{config_file} is valid YAML")
                except yaml.YAMLError as e:
                    print_error(f"{config_file} has invalid YAML: {e}")
                    all_exist = False
        else:
            print_error(f"{config_file} is missing")
            all_exist = False
    
    return all_exist

def check_streamlit_app():
    """Check Streamlit app file"""
    print_header("Streamlit App Check")
    
    app_file = Path(__file__).parent / 'streamlit-app' / 'app.py'
    
    if app_file.exists():
        print_success("streamlit-app/app.py exists")
        
        # Check if it's a valid Python file
        try:
            with open(app_file, 'r') as f:
                content = f.read()
            
            if 'streamlit' in content and 'def main():' in content:
                print_success("app.py appears to be a valid Streamlit application")
                return True
            else:
                print_warning("app.py may not be a complete Streamlit application")
                return False
        except Exception as e:
            print_error(f"Error reading app.py: {e}")
            return False
    else:
        print_error("streamlit-app/app.py is missing")
        return False

def check_environment():
    """Check environment configuration"""
    print_header("Environment Check")
    
    env_file = Path(__file__).parent / '.env'
    
    if env_file.exists():
        print_success(".env file exists")
        print_warning("Verify that FIRECRAWL_API_KEY is set in .env")
    else:
        print_warning(".env file not found (copy from .env.example)")
    
    return True

def main():
    """Run all smoke tests"""
    print_header("Firecrawl-Streamlit Web Scraper - Setup Validation")
    print(f"Test run at: {datetime.now()}")
    
    tests = [
        ("Python Version", check_python_version),
        ("Core Dependencies", check_dependencies),
        ("Firecrawl Dependency", check_firecrawl_dependency),
        ("Directory Structure", check_directory_structure),
        ("Configuration Files", check_config_files),
        ("Streamlit App", check_streamlit_app),
        ("Environment", check_environment),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print_error(f"Test '{test_name}' failed with error: {e}")
            results.append((test_name, False))
    
    # Summary
    print_header("Test Summary")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    print(f"Tests passed: {passed}/{total}")
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")
    
    if passed == total:
        print_success("All tests passed! Setup is complete.")
        print("\nNext steps:")
        print("1. Copy .env.example to .env and add your FIRECRAWL_API_KEY")
        print("2. Install dependencies: pip install -r requirements.txt")
        print("3. Run the app: streamlit run streamlit-app/app.py")
        return True
    else:
        print_error(f"{total - passed} tests failed. Please fix the issues above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
