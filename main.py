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
        
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        
        # Try to create a driver instance
        driver = webdriver.Chrome(options=chrome_options)
        driver.quit()
        
        return True
        
    except Exception as e:
        error_msg = f"""
        Chrome WebDriver not found or not working properly.
        
        Error: {str(e)}
        
        Please ensure:
        1. Google Chrome browser is installed
        2. ChromeDriver is installed and in your PATH
        
        You can install ChromeDriver using:
        - Download from: https://chromedriver.chromium.org/
        - Or use: pip install webdriver-manager
        
        For automatic driver management, we'll try to handle this in the application.
        """
        print(error_msg)
        return False

def create_directories():
    """Create necessary directories"""
    directories = ['logs', 'exports', 'temp']
    
    for directory in directories:
        if not os.path.exists(directory):
            os.makedirs(directory)

def main():
    """Main entry point"""
    logger = setup_logging()
    
    try:
        logger.info("Starting LeadSprinter Pro application")
        print("=== LeadSprinter Pro ===")
        print("Professional LinkedIn Lead Generation Tool")
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
            print("Warning: WebDriver issues detected. The application may not work properly.")
            response = input("Continue anyway? (y/N): ").lower().strip()
            if response != 'y':
                sys.exit(1)
        
        # Import and run GUI
        print("Loading application interface...")
        try:
            from gui import run_gui
            logger.info("GUI module imported successfully")
            
            print("Starting LeadSprinter Pro...")
            run_gui()
            
        except ImportError as e:
            logger.error(f"Failed to import GUI module: {str(e)}")
            print(f"Error: Failed to load application interface: {str(e)}")
            print("Please ensure all files are present and try again.")
            input("Press Enter to exit...")
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
        
        input("Press Enter to exit...")
        sys.exit(1)
    
    finally:
        logger.info("LeadSprinter Pro application ended")

if __name__ == "__main__":
    main()
