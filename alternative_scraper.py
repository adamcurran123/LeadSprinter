#!/usr/bin/env python3
"""
Alternative LinkedIn scraper using multiple approaches to bypass anti-bot measures
"""

import requests
import time
import random
from urllib.parse import quote_plus
import re
from bs4 import BeautifulSoup

class AlternativeLinkedInScraper:
    def __init__(self):
        self.session = requests.Session()
        # Rotate user agents
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.7339.207 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.7339.207 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/119.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:109.0) Gecko/20100101 Firefox/119.0'
        ]
        self.setup_session()
    
    def setup_session(self):
        """Setup requests session with headers"""
        headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Cache-Control': 'max-age=0'
        }
        self.session.headers.update(headers)
    
    def random_delay(self, min_seconds=1, max_seconds=3):
        """Random delay to appear more human"""
        time.sleep(random.uniform(min_seconds, max_seconds))
    
    def get_user_agent(self):
        """Get random user agent"""
        return random.choice(self.user_agents)
    
    def search_bing_for_linkedin(self, query, max_results=20):
        """Search Bing for LinkedIn profiles (less aggressive anti-bot)"""
        try:
            profiles = []
            
            # Bing is less aggressive with blocking
            search_url = "https://www.bing.com/search"
            
            searches = [
                f'site:linkedin.com/in "{query}"',
                f'site:linkedin.com/in {query}',
                f'linkedin.com "{query}" profile',
                f'{query} linkedin profile site:linkedin.com'
            ]
            
            for search_query in searches:
                if len(profiles) >= max_results:
                    break
                    
                print(f"🔍 Bing search: {search_query}")
                
                params = {
                    'q': search_query,
                    'count': '20',
                    'mkt': 'en-IE',  # Ireland market
                    'setlang': 'en'
                }
                
                headers = {
                    'User-Agent': self.get_user_agent(),
                    'Referer': 'https://www.bing.com'
                }
                
                try:
                    response = self.session.get(search_url, params=params, headers=headers, timeout=10)
                    
                    if response.status_code == 200:
                        # Extract LinkedIn URLs from response
                        linkedin_urls = self.extract_linkedin_urls_from_html(response.text)
                        
                        for url in linkedin_urls:
                            if url not in profiles and len(profiles) < max_results:
                                profiles.append(url)
                        
                        print(f"✅ Found {len(linkedin_urls)} profiles with this search")
                        self.random_delay(2, 4)
                    else:
                        print(f"❌ Bing returned status code: {response.status_code}")
                        
                except Exception as e:
                    print(f"❌ Bing search failed: {str(e)}")
                    continue
            
            return profiles
            
        except Exception as e:
            print(f"❌ Bing search error: {str(e)}")
            return []
    
    def search_duckduckgo_for_linkedin(self, query, max_results=20):
        """Search DuckDuckGo for LinkedIn profiles"""
        try:
            profiles = []
            
            # DuckDuckGo HTML search endpoint
            search_url = "https://html.duckduckgo.com/html/"
            
            searches = [
                f'site:linkedin.com/in "{query}"',
                f'{query} linkedin profile',
                f'"{query}" linkedin.com/in',
                f'site:linkedin.com {query}'
            ]
            
            for search_query in searches:
                if len(profiles) >= max_results:
                    break
                    
                print(f"🦆 DuckDuckGo search: {search_query}")
                
                data = {
                    'q': search_query,
                    'kl': 'ie-en',  # Ireland English
                    's': '0',  # Start position
                    'df': '',  # Date filter
                    'vqd': ''  # Required by DDG
                }
                
                headers = {
                    'User-Agent': self.get_user_agent(),
                    'Referer': 'https://duckduckgo.com/',
                    'Content-Type': 'application/x-www-form-urlencoded'
                }
                
                try:
                    response = self.session.post(search_url, data=data, headers=headers, timeout=10)
                    
                    if response.status_code == 200:
                        # Extract LinkedIn URLs from response
                        linkedin_urls = self.extract_linkedin_urls_from_html(response.text)
                        
                        for url in linkedin_urls:
                            if url not in profiles and len(profiles) < max_results:
                                profiles.append(url)
                        
                        print(f"✅ Found {len(linkedin_urls)} profiles with this search")
                        self.random_delay(2, 4)
                    else:
                        print(f"❌ DuckDuckGo returned status code: {response.status_code}")
                        
                except Exception as e:
                    print(f"❌ DuckDuckGo search failed: {str(e)}")
                    continue
            
            return profiles
            
        except Exception as e:
            print(f"❌ DuckDuckGo search error: {str(e)}")
            return []
    
    def extract_linkedin_urls_from_html(self, html):
        """Extract LinkedIn profile URLs from HTML content"""
        try:
            linkedin_urls = []
            
            # Use regex to find LinkedIn URLs
            patterns = [
                r'https?://(?:www\.)?linkedin\.com/in/[a-zA-Z0-9\-_%]+',
                r'linkedin\.com/in/[a-zA-Z0-9\-_%]+',
                r'/in/[a-zA-Z0-9\-_%]+'
            ]
            
            for pattern in patterns:
                matches = re.findall(pattern, html, re.IGNORECASE)
                for match in matches:
                    # Clean and normalize the URL
                    if match.startswith('/in/'):
                        clean_url = f"https://www.linkedin.com{match}"
                    elif match.startswith('linkedin.com'):
                        clean_url = f"https://www.{match}"
                    else:
                        clean_url = match
                    
                    # Remove query parameters
                    clean_url = clean_url.split('?')[0].split('#')[0]
                    
                    if clean_url not in linkedin_urls and '/in/' in clean_url:
                        linkedin_urls.append(clean_url)
            
            return list(set(linkedin_urls))  # Remove duplicates
            
        except Exception as e:
            print(f"Error extracting URLs: {str(e)}")
            return []
    
    def scrape_linkedin_profiles(self, query, max_results=20):
        """Main method to scrape LinkedIn profiles using multiple search engines"""
        print(f"🔍 Searching for LinkedIn profiles: {query}")
        all_profiles = []
        
        # Try Bing first (usually less restrictive)
        print("🟦 Trying Bing search...")
        bing_profiles = self.search_bing_for_linkedin(query, max_results)
        all_profiles.extend(bing_profiles)
        
        # Try DuckDuckGo if we need more results
        if len(all_profiles) < max_results:
            print("🦆 Trying DuckDuckGo search...")
            remaining_needed = max_results - len(all_profiles)
            ddg_profiles = self.search_duckduckgo_for_linkedin(query, remaining_needed)
            all_profiles.extend(ddg_profiles)
        
        # Remove duplicates
        unique_profiles = list(dict.fromkeys(all_profiles))  # Preserves order
        
        print(f"🎯 Total unique LinkedIn profiles found: {len(unique_profiles)}")
        
        return unique_profiles[:max_results]

def test_alternative_scraper():
    """Test the alternative scraper"""
    scraper = AlternativeLinkedInScraper()
    
    test_queries = [
        "software developer galway",
        "software developer ireland", 
        "developer galway"
    ]
    
    for query in test_queries:
        print(f"\n{'='*50}")
        print(f"Testing query: {query}")
        print('='*50)
        
        profiles = scraper.scrape_linkedin_profiles(query, 10)
        
        if profiles:
            print(f"\n✅ SUCCESS: Found {len(profiles)} profiles")
            for i, profile in enumerate(profiles, 1):
                print(f"  {i}. {profile}")
        else:
            print("❌ No profiles found")
        
        print("\nWaiting before next query...")
        time.sleep(3)

if __name__ == "__main__":
    test_alternative_scraper()