#!/usr/bin/env python3
"""
Debug script to test Google search functionality and see what's happening
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from scraper import LinkedInScraper
import time

def debug_google_search():
    """Debug Google search to see what's happening"""
    print("=== LeadSprinter Debug - Google Search Test ===")
    
    scraper = LinkedInScraper()
    
    try:
        print("Setting up Chrome driver...")
        if not scraper.setup_driver():
            print("❌ Failed to setup Chrome driver")
            return
        
        print("✅ Chrome driver setup successful")
        print(f"Chrome version: {scraper.driver.capabilities.get('browserVersion', 'Unknown')}")
        
        # Test basic Google access
        print("\n1. Testing basic Google access...")
        scraper.driver.get("https://www.google.com")
        time.sleep(2)
        
        current_url = scraper.driver.current_url
        page_title = scraper.driver.title
        print(f"Current URL: {current_url}")
        print(f"Page title: {page_title}")
        
        # Check if we can see Google
        if 'google' in current_url.lower():
            print("✅ Successfully reached Google")
        else:
            print("❌ Did not reach Google - might be blocked")
            
        # Test search functionality
        print("\n2. Testing search functionality...")
        test_query = "software developer galway"
        print(f"Searching for: {test_query}")
        
        results = scraper.scrape_google_search_results(test_query, 5)
        
        if results:
            print(f"✅ Found {len(results)} results:")
            for i, url in enumerate(results, 1):
                print(f"  {i}. {url}")
        else:
            print("❌ No results found")
            
        # Check current page content for debugging
        print("\n3. Checking page content...")
        page_source = scraper.driver.page_source[:1000].lower()  # First 1000 chars
        
        if 'captcha' in page_source:
            print("⚠️ CAPTCHA detected in page")
        if 'unusual traffic' in page_source:
            print("⚠️ 'Unusual traffic' message detected")
        if 'blocked' in page_source:
            print("⚠️ 'Blocked' message detected")
        if 'linkedin' in page_source:
            print("✅ LinkedIn mentioned in page content")
        if 'search' in page_source:
            print("✅ Search functionality present")
            
        # Save page source for inspection
        try:
            with open('debug_page_source.html', 'w', encoding='utf-8') as f:
                f.write(scraper.driver.page_source)
            print("💾 Page source saved to 'debug_page_source.html'")
        except:
            print("⚠️ Could not save page source")
            
    except Exception as e:
        print(f"❌ Error during debug: {str(e)}")
        import traceback
        traceback.print_exc()
        
    finally:
        if scraper.driver:
            scraper.driver.quit()
            print("🔄 Browser closed")

if __name__ == "__main__":
    debug_google_search()