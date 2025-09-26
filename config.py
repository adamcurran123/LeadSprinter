# Configuration settings for LeadSprinter Pro

import os
from datetime import datetime

class Config:
    """Application configuration settings"""
    
    # Application Information
    APP_NAME = "LeadSprinter Pro"
    APP_VERSION = "1.0.0"
    APP_AUTHOR = "LeadSprinter Development Team"
    APP_DESCRIPTION = "Professional LinkedIn Lead Generation Tool"
    
    # GUI Settings
    WINDOW_SIZE = (800, 700)
    THEME = 'DarkBlue3'
    
    # Scraping Settings
    DEFAULT_DELAY_MIN = 1
    DEFAULT_DELAY_MAX = 3
    PROFILE_DELAY_MIN = 2
    PROFILE_DELAY_MAX = 5
    MAX_RESULTS_PER_SEARCH = 100
    TIMEOUT_SECONDS = 10
    
    # File Paths
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    LOGS_DIR = os.path.join(BASE_DIR, 'logs')
    EXPORTS_DIR = os.path.join(BASE_DIR, 'exports')
    TEMP_DIR = os.path.join(BASE_DIR, 'temp')
    
    # Chrome Options
    CHROME_OPTIONS = [
        '--no-sandbox',
        '--disable-dev-shm-usage',
        '--disable-gpu',
        '--disable-extensions',
        '--disable-images',
        '--window-size=1920,1080',
        '--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    ]
    
    # Search Settings
    INDUSTRIES = [
        'All Industries',
        'Technology',
        'Healthcare', 
        'Finance',
        'Marketing',
        'Sales',
        'Education',
        'Manufacturing',
        'Consulting',
        'Real Estate',
        'Retail',
        'Government',
        'Non-profit'
    ]
    
    COMPANY_SIZES = [
        'All Sizes',
        '1-10',
        '11-50', 
        '51-200',
        '201-500',
        '501-1000',
        '1000+'
    ]
    
    # Export Settings
    EXPORT_COLUMNS = [
        'name',
        'title', 
        'company',
        'location',
        'linkedin_url',
        'email',
        'scraped_date'
    ]
    
    EXPORT_COLUMN_NAMES = {
        'name': 'Full Name',
        'title': 'Job Title',
        'company': 'Company',
        'location': 'Location', 
        'linkedin_url': 'LinkedIn Profile',
        'email': 'Email Address',
        'scraped_date': 'Date Scraped'
    }
    
    @classmethod
    def get_export_filename(cls, job_titles, extension='xlsx'):
        """Generate export filename"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        job_title_clean = job_titles.replace(',', '_').replace(' ', '_')[:30]
        return f"LeadSprinter_Results_{job_title_clean}_{timestamp}.{extension}"
    
    @classmethod
    def ensure_directories(cls):
        """Ensure all necessary directories exist"""
        directories = [cls.LOGS_DIR, cls.EXPORTS_DIR, cls.TEMP_DIR]
        for directory in directories:
            if not os.path.exists(directory):
                os.makedirs(directory)