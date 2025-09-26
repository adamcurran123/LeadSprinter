# Entry point for LeadSprinter Pro
# Professional LinkedIn Lead Generation Tool
import sys
import os
import traceback
import logging
from datetime import datetime

# Setup logging
def setup_logging():
    """Setup logging configuration"""
    log_dir = "logs"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    log_filename = os.path.join(log_dir, f"leadsprinter_{datetime.now().strftime('%Y%m%d')}.log")
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_filename),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger(__name__)

def check_dependencies():
    """Check if all required dependencies are installed"""
    required_modules = [
        'PySimpleGUI',
        'selenium', 
        'pandas',
        'openpyxl',
        'requests'
    ]
    
    missing_modules = []
    
    for module in required_modules:
        try:
            __import__(module)
        except ImportError:
            missing_modules.append(module)
    
    if missing_modules:
        error_msg = f"""
        Missing required dependencies: {', '.join(missing_modules)}
        
        Please install them using:
        pip install {' '.join(missing_modules)}
        
        Or install all requirements:
        pip install -r requirements.txt
        """
        print(error_msg)
        input("Press Enter to exit...")
        sys.exit(1)

def check_webdriver():
    """Check if Chrome WebDriver is available"""
    try:
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
        from webdriver_manager.chrome import ChromeDriverManager
        from selenium.webdriver.chrome.service import Service
        import tempfile
        
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        
        # Use unique user data directory
        user_data_dir = tempfile.mkdtemp()
        chrome_options.add_argument(f'--user-data-dir={user_data_dir}')
        
        # Try webdriver-manager first
        try:
            service = Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=chrome_options)
            driver.quit()
            return True
        except Exception as e1:
            # Fallback to system driver
            try:
                driver = webdriver.Chrome(options=chrome_options)
                driver.quit()
                return True
            except Exception as e2:
                print(f"WebDriver check failed: {str(e1)}")
                return False
        
    except Exception as e:
        print(f"WebDriver check failed: {str(e)}")
        return False

def create_directories():
    """Create necessary directories"""
    directories = ['logs', 'exports', 'temp']
    
    for directory in directories:
        if not os.path.exists(directory):
            os.makedirs(directory)

def is_headless_environment():
    """Check if we're in a headless environment (like Codespaces)"""
    # Only consider truly headless environments - be more restrictive
    headless_indicators = [
        os.environ.get('CODESPACES') == 'true',  # GitHub Codespaces specifically
        os.environ.get('CI') == 'true',  # CI environments
        os.environ.get('GITHUB_ACTIONS') == 'true',  # GitHub Actions
    ]
    
    # Always try GUI first on normal systems, even without perfect DISPLAY detection
    return any(headless_indicators)

def main():
    """Main entry point"""
    logger = setup_logging()
    
    try:
        logger.info("Starting LeadSprinter Pro application")
        print("=== LeadSprinter Pro ===")
        print("Professional LinkedIn Lead Generation Tool")
        
        # Check if we're in a headless environment
        is_headless = is_headless_environment()
        if is_headless:
            print("Detected headless environment - using command line interface")
            print("(Perfect for Codespaces, SSH, or server environments)")
        
        print("Initializing application...")
        
        # Create necessary directories
        create_directories()
        logger.info("Created application directories")
        
        # Check dependencies
        print("Checking dependencies...")
        check_dependencies()
        logger.info("All dependencies satisfied")
        
        # Check WebDriver (warning only, not fatal)
        print("Checking Chrome WebDriver...")
        webdriver_ok = check_webdriver()
        if not webdriver_ok:
            logger.warning("WebDriver check failed, but continuing...")
            print("Warning: WebDriver issues detected. This may be normal in headless environments.")
            if not is_headless:
                response = input("Continue anyway? (y/N): ").lower().strip()
                if response != 'y':
                    sys.exit(1)
        
        # Choose interface - ALWAYS try GUI first unless explicitly CLI
        if '--cli' in sys.argv or '--command-line' in sys.argv:
            print("Command line mode requested...")
            try:
                from cli import run_cli
                run_cli()
            except Exception as e:
                logger.error(f"CLI failed: {e}")
                print(f"CLI interface failed: {e}")
                sys.exit(1)
        else:
            # Always try GUI first, fall back to CLI if GUI fails
            print("Starting GUI interface...")
            try:
                from gui import run_gui
                logger.info("GUI module imported successfully")
                run_gui()
            except Exception as gui_error:
                logger.warning(f"GUI failed: {gui_error}")
                print(f"GUI failed ({gui_error}), falling back to CLI...")
                try:
                    from cli import run_cli
                    run_cli()
                except Exception as cli_error:
                    logger.error(f"Both GUI and CLI failed. GUI: {gui_error}, CLI: {cli_error}")
                    print(f"Both interfaces failed. Please check the logs.")
                    sys.exit(1)
            
    except KeyboardInterrupt:
        logger.info("Application interrupted by user")
        print("\nApplication interrupted by user.")
        
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        
        print(f"\nAn unexpected error occurred: {str(e)}")
        print("Please check the log file for more details.")
        print(f"Log location: logs/leadsprinter_{datetime.now().strftime('%Y%m%d')}.log")
        
        if not is_headless_environment():
            input("Press Enter to exit...")
        sys.exit(1)
    
    finally:
        logger.info("LeadSprinter Pro application ended")

if __name__ == "__main__":
    main()
