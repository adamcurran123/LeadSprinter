# Utility functions for LeadSprinter Pro

import re
import os
import sys
import time
import random
from datetime import datetime
from urllib.parse import urlparse
import logging

def setup_logger(name, log_file=None, level=logging.INFO):
    """Set up a logger with file and console handlers"""
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # File handler
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger

def validate_email(email):
    """Validate email format"""
    if not email or not isinstance(email, str):
        return False
    
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def extract_emails_from_text(text):
    """Extract all valid emails from text"""
    if not text:
        return []
    
    pattern = r'\b[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}\b'
    emails = re.findall(pattern, text)
    return [email for email in emails if validate_email(email)]

def clean_text(text):
    """Clean and normalize text"""
    if not text or not isinstance(text, str):
        return 'N/A'
    
    # Remove extra whitespace
    text = ' '.join(text.split())
    
    # Remove special characters that might cause issues
    text = re.sub(r'[^\w\s\-\.,@]', '', text)
    
    return text.strip() or 'N/A'

def validate_linkedin_url(url):
    """Validate LinkedIn profile URL"""
    if not url or not isinstance(url, str):
        return False
    
    try:
        parsed = urlparse(url)
        return (
            parsed.netloc.endswith('linkedin.com') and
            '/in/' in parsed.path
        )
    except:
        return False

def format_filename(text, max_length=50):
    """Format text to be safe for filenames"""
    if not text:
        return "untitled"
    
    # Remove/replace unsafe characters
    safe_text = re.sub(r'[<>:"/\\|?*]', '_', text)
    safe_text = re.sub(r'\s+', '_', safe_text)
    safe_text = safe_text.strip('_')
    
    # Limit length
    if len(safe_text) > max_length:
        safe_text = safe_text[:max_length].rstrip('_')
    
    return safe_text or "untitled"

def random_delay(min_seconds=1, max_seconds=3):
    """Add random delay between operations"""
    delay = random.uniform(min_seconds, max_seconds)
    time.sleep(delay)
    return delay

def get_chrome_driver_path():
    """Try to find Chrome driver in common locations"""
    possible_paths = [
        'chromedriver.exe',  # Current directory
        'chromedriver',      # Unix
        '/usr/local/bin/chromedriver',
        '/usr/bin/chromedriver',
        'C:\\chromedriver\\chromedriver.exe',
        os.path.join(os.path.dirname(sys.executable), 'chromedriver.exe'),
    ]
    
    for path in possible_paths:
        if os.path.exists(path) and os.access(path, os.X_OK):
            return path
    
    return None

def format_number(num):
    """Format numbers for display"""
    if num >= 1000000:
        return f"{num/1000000:.1f}M"
    elif num >= 1000:
        return f"{num/1000:.1f}K"
    else:
        return str(num)

def get_file_size_mb(filepath):
    """Get file size in MB"""
    try:
        size_bytes = os.path.getsize(filepath)
        return round(size_bytes / (1024 * 1024), 2)
    except:
        return 0

def create_backup_filename(filepath):
    """Create a backup filename"""
    directory = os.path.dirname(filepath)
    filename = os.path.basename(filepath)
    name, ext = os.path.splitext(filename)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return os.path.join(directory, f"{name}_backup_{timestamp}{ext}")

def sanitize_search_params(params):
    """Sanitize search parameters"""
    sanitized = {}
    
    # Job titles
    if 'job_titles' in params:
        job_titles = params['job_titles']
        if isinstance(job_titles, str):
            job_titles = [title.strip() for title in job_titles.split(',')]
        sanitized['job_titles'] = [clean_text(title) for title in job_titles if title.strip()]
    
    # Locations
    if 'locations' in params:
        locations = params['locations']
        if isinstance(locations, str):
            locations = [loc.strip() for loc in locations.split(',')]
        sanitized['locations'] = [clean_text(loc) for loc in locations if loc.strip()]
    
    # Number of results
    sanitized['num_results'] = max(1, min(1000, params.get('num_results', 50)))
    
    # Industry and company size
    sanitized['industry'] = params.get('industry')
    sanitized['company_size'] = params.get('company_size')
    
    return sanitized

def estimate_scraping_time(num_results, delay_per_profile=3.5):
    """Estimate scraping time in minutes"""
    estimated_seconds = num_results * delay_per_profile
    estimated_minutes = estimated_seconds / 60
    return max(1, round(estimated_minutes))

def check_disk_space(directory, required_mb=100):
    """Check if there's enough disk space"""
    try:
        import shutil
        total, used, free = shutil.disk_usage(directory)
        free_mb = free // (1024 * 1024)
        return free_mb >= required_mb
    except:
        return True  # Assume OK if we can't check

def get_system_info():
    """Get basic system information"""
    import platform
    
    return {
        'system': platform.system(),
        'version': platform.version(),
        'architecture': platform.architecture()[0],
        'python_version': platform.python_version(),
        'machine': platform.machine()
    }

class ProgressTracker:
    """Simple progress tracking utility"""
    
    def __init__(self, total, description="Processing"):
        self.total = total
        self.current = 0
        self.description = description
        self.start_time = datetime.now()
    
    def update(self, increment=1):
        """Update progress"""
        self.current += increment
        self.current = min(self.current, self.total)
    
    def get_percentage(self):
        """Get completion percentage"""
        return (self.current / self.total * 100) if self.total > 0 else 0
    
    def get_eta(self):
        """Estimate time remaining"""
        if self.current == 0:
            return "Unknown"
        
        elapsed = (datetime.now() - self.start_time).total_seconds()
        rate = self.current / elapsed
        remaining = (self.total - self.current) / rate
        
        if remaining < 60:
            return f"{int(remaining)}s"
        elif remaining < 3600:
            return f"{int(remaining/60)}m"
        else:
            return f"{int(remaining/3600)}h {int((remaining%3600)/60)}m"
    
    def get_status(self):
        """Get formatted status string"""
        percentage = self.get_percentage()
        eta = self.get_eta()
        return f"{self.description}: {self.current}/{self.total} ({percentage:.1f}%) - ETA: {eta}"