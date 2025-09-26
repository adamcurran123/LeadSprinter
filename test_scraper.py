#!/usr/bin/env python3
"""
Test script to verify core scraping functionality works in headless mode
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from scraper import LinkedInScraper
import logging

# Setup basic logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def test_scraper():
    """Test the scraper with a simple search"""
    print("Testing LeadSprinter scraping functionality...")
    
    # Test configuration
    config = {
        'search_query': 'CEO software company site:linkedin.com',
        'max_profiles': 3,  # Small number for testing
        'output_format': 'csv',
        'output_filename': 'test_results.csv'
    }
    
    try:
        scraper = LinkedInScraper()
        profiles = scraper.scrape_profiles(config)
        
        print(f"\nScraping completed successfully!")
        print(f"Found {len(profiles)} profiles")
        
        if profiles:
            print("\nSample profile data:")
            for i, profile in enumerate(profiles[:2], 1):
                print(f"\nProfile {i}:")
                for key, value in profile.items():
                    print(f"  {key}: {value}")
        else:
            print("No profiles found - this might be due to anti-bot measures or search limitations")
        
        return True
        
    except Exception as e:
        print(f"Error during scraping: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_scraper()
    sys.exit(0 if success else 1)