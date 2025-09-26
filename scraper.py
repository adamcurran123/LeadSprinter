# Scraping engine for LeadSprinter
# Uses Selenium to scrape LinkedIn profiles

import time
import random
import pandas as pd
from selenium import webdriver
from alternative_scraper import AlternativeLinkedInScraper
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException
import re
import os
from urllib.parse import quote

class LinkedInScraper:
    def __init__(self):
        self.driver = None
        self.wait = None
        self.stop_requested = False
        self.results_df = pd.DataFrame(columns=['name', 'title', 'company', 'location', 'linkedin_url', 'email'])
        
    def setup_driver(self):
        """Setup Chrome driver with optimal settings"""
        chrome_options = Options()
        
        # ALWAYS run headless to avoid opening browser windows
        chrome_options.add_argument('--headless=new')  # Use new headless mode
        
        # Performance optimizations
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--disable-extensions')
        chrome_options.add_argument('--disable-images')  # Faster loading
        chrome_options.add_argument('--disable-notifications')
        chrome_options.add_argument('--disable-popup-blocking')
        
        # Anti-detection measures
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        # Fix for dev container/codespace issues
        chrome_options.add_argument('--disable-web-security')
        chrome_options.add_argument('--allow-running-insecure-content')
        chrome_options.add_argument('--disable-features=VizDisplayCompositor')
        
        # User agent to appear more human
        chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
        
        # Use unique user data directory to avoid conflicts
        import tempfile
        user_data_dir = tempfile.mkdtemp()
        chrome_options.add_argument(f'--user-data-dir={user_data_dir}')
        
        # User agent to appear more legitimate
        chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36')
        
        # Window size
        chrome_options.add_argument('--window-size=1920,1080')
        
        # Optional: Run headless (uncomment for background operation)
        # chrome_options.add_argument('--headless')
        
        try:
            # Try using webdriver-manager for automatic driver management
            from webdriver_manager.chrome import ChromeDriverManager
            from selenium.webdriver.chrome.service import Service
            
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            self.wait = WebDriverWait(self.driver, 10)
            return True
            
        except Exception as e1:
            try:
                # Fallback: try with system ChromeDriver
                self.driver = webdriver.Chrome(options=chrome_options)
                self.wait = WebDriverWait(self.driver, 10)
                return True
            except Exception as e2:
                raise Exception(f"Failed to setup Chrome driver: {str(e1)}. Fallback also failed: {str(e2)}")
        
        return False
    
    def random_delay(self, min_seconds=1, max_seconds=3):
        """Add random delay to avoid detection"""
        if not self.stop_requested:
            time.sleep(random.uniform(min_seconds, max_seconds))
    
    def extract_email_from_text(self, text):
        """Extract email from text using regex"""
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        emails = re.findall(email_pattern, text)
        return emails[0] if emails else None
    
    def extract_linkedin_urls(self):
        """Extract LinkedIn profile URLs from current Google search results page"""
        profile_links = []
        
        try:
            print("🔍 Extracting LinkedIn URLs from search results...")
            
            # Multiple selectors to find LinkedIn profile links
            selectors = [
                'div.g h3 a[href*="linkedin.com/in/"]',  # Standard search results
                'a[href*="linkedin.com/in/"]',  # Any LinkedIn profile links
                'div[data-ved] a[href*="linkedin.com/in/"]',  # Results with data-ved
                '.g a[href*="linkedin.com/in/"]',  # General result container links
                '[data-ved] a[href*="linkedin.com/in/"]'  # Any element with data-ved
            ]
            
            for i, selector in enumerate(selectors):
                try:
                    links = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    print(f"  Selector {i+1} '{selector}': found {len(links)} links")
                    
                    for link in links:
                        href = link.get_attribute('href')
                        if href and 'linkedin.com/in/' in href:
                            # Clean Google tracking URLs
                            clean_url = self.clean_google_url(href)
                            if clean_url and clean_url not in profile_links:
                                profile_links.append(clean_url)
                                print(f"    ✅ Added: {clean_url}")
                except Exception as e:
                    print(f"  ❌ Selector {i+1} failed: {str(e)}")
                    continue
            
            # Try finding URLs in page source as backup
            if not profile_links:
                print("🔍 No URLs found with selectors, trying regex on page source...")
                try:
                    page_source = self.driver.page_source
                    import re
                    # Look for LinkedIn URLs in the raw HTML
                    linkedin_pattern = r'https://[^"\'>\s]*linkedin\.com/in/[^"\'>\s/]+'
                    matches = re.findall(linkedin_pattern, page_source)
                    print(f"  Regex found {len(matches)} potential URLs")
                    
                    for match in matches:
                        clean_url = self.clean_google_url(match)
                        if clean_url and clean_url not in profile_links:
                            profile_links.append(clean_url)
                            print(f"    ✅ Added from regex: {clean_url}")
                except Exception as e:
                    print(f"  ❌ Regex extraction failed: {str(e)}")
            
            # Debug: show part of page source if no results
            if not profile_links:
                print("⚠️ No LinkedIn URLs found. Checking page content...")
                try:
                    page_text = self.driver.page_source.lower()[:2000]
                    if 'linkedin' in page_text:
                        print("  ✅ Page contains 'linkedin' text")
                    else:
                        print("  ❌ Page does not contain 'linkedin' text")
                    
                    if 'search' in page_text:
                        print("  ✅ Page appears to be a search page")
                    else:
                        print("  ❌ Page may not be a search results page")
                        
                    if any(word in page_text for word in ['captcha', 'unusual', 'blocked', 'verify']):
                        print("  ⚠️ Page may contain anti-bot measures")
                        
                except:
                    pass
                    
        except Exception as e:
            print(f"❌ Error extracting URLs: {str(e)}")
        
        print(f"🎯 Total LinkedIn URLs extracted: {len(profile_links)}")
        return list(set(profile_links))  # Remove duplicates
    
    def clean_google_url(self, url):
        """Clean Google tracking from URLs"""
        try:
            if not url or 'linkedin.com/in/' not in url:
                return None
                
            # Handle Google redirect URLs
            if 'google.com/url?q=' in url:
                # Extract the actual URL from Google's redirect
                import urllib.parse
                parsed = urllib.parse.parse_qs(urllib.parse.urlparse(url).query)
                if 'q' in parsed:
                    actual_url = parsed['q'][0]
                    if 'linkedin.com/in/' in actual_url:
                        return actual_url.split('&')[0]  # Remove tracking parameters
            
            # Clean direct LinkedIn URLs
            if url.startswith('https://linkedin.com') or url.startswith('https://www.linkedin.com'):
                return url.split('?')[0]  # Remove query parameters
                
            return None
        except:
            return None

    def detect_captcha_or_blocking(self):
        """Enhanced detection of anti-bot measures"""
        try:
            page_source = self.driver.page_source.lower()
            current_url = self.driver.current_url.lower()
            
            # Check for various blocking indicators
            blocking_indicators = [
                'captcha', 'unusual traffic', 'detected unusual', 
                'verify you are human', 'suspicious requests',
                'automated queries', 'robot', 'unusual requests',
                'please confirm', 'verify that you', 'prove you\'re human'
            ]
            
            url_indicators = [
                'captcha', 'blocked', 'denied', 'robot'
            ]
            
            # Check page content
            if any(indicator in page_source for indicator in blocking_indicators):
                return True
                
            # Check URL
            if any(indicator in current_url for indicator in url_indicators):
                return True
                
            # Check for absence of search results (might indicate blocking)
            if 'did not match any documents' in page_source:
                return False  # This is a legitimate "no results" message
            
            # Check if we're on an error page
            if '403' in page_source or '429' in page_source:
                return True
                
            return False
            
        except Exception as e:
            print(f"Error detecting blocking: {str(e)}")
            return False

    def scrape_duckduckgo_search_results(self, search_query, max_results=20):
        """Alternative search using DuckDuckGo with requests (bypasses Selenium blocking)"""
        try:
            print(f"🦆 Using DuckDuckGo alternative scraper for: {search_query}")
            
            # Use the alternative scraper for DuckDuckGo
            alt_scraper = AlternativeLinkedInScraper()
            profiles = alt_scraper.search_duckduckgo_for_linkedin(search_query, max_results)
            
            if profiles:
                print(f"✅ DuckDuckGo alternative found {len(profiles)} profiles")
            else:
                print("❌ DuckDuckGo alternative found no profiles")
                
            return profiles
            
        except Exception as e:
            print(f"❌ DuckDuckGo alternative search failed: {str(e)}")
            return []

    def clean_search_url(self, url):
        """Clean URLs from search engines"""
        try:
            if not url or 'linkedin.com/in/' not in url:
                return None
                
            # Handle various redirect patterns
            if 'duckduckgo.com' in url and 'uddg=' in url:
                # DuckDuckGo redirect
                import urllib.parse
                parsed = urllib.parse.parse_qs(urllib.parse.urlparse(url).query)
                if 'uddg' in parsed:
                    return parsed['uddg'][0]
            
            if 'google.com/url?q=' in url:
                # Google redirect
                import urllib.parse
                parsed = urllib.parse.parse_qs(urllib.parse.urlparse(url).query)
                if 'q' in parsed:
                    actual_url = parsed['q'][0]
                    if 'linkedin.com/in/' in actual_url:
                        return actual_url.split('&')[0]
            
            # Direct LinkedIn URL
            if url.startswith('https://linkedin.com') or url.startswith('https://www.linkedin.com'):
                return url.split('?')[0]
                
            return None
        except:
            return None

    def scrape_google_search_results(self, search_query, max_results):
        """Enhanced Google search for LinkedIn profiles with multiple strategies"""
        try:
            profile_links = []
            
            # Multiple search strategies for better results
            search_strategies = [
                f'site:linkedin.com/in/ "{search_query}" Ireland',  # Specific to Ireland for Galway
                f'site:linkedin.com/in/ {search_query} Galway',
                f'site:linkedin.com/in/ "{search_query}"',
                f'linkedin.com/in {search_query}',
                f'intitle:"{search_query}" site:linkedin.com',
                f'"{search_query}" linkedin profile'
            ]
            
            for i, search_terms in enumerate(search_strategies):
                if len(profile_links) >= max_results:
                    break
                    
                print(f"🔍 Strategy {i+1}: {search_terms}")
                
                try:
                    # Build search URL with Irish locale
                    base_url = "https://www.google.com/search"
                    params = {
                        'q': search_terms,
                        'num': '20',
                        'hl': 'en',
                        'gl': 'ie',  # Ireland
                        'start': '0'
                    }
                    
                    # Manual URL building to avoid encoding issues
                    query_parts = []
                    for key, value in params.items():
                        encoded_value = str(value).replace(' ', '+').replace('"', '%22')
                        query_parts.append(f"{key}={encoded_value}")
                    
                    url = f"{base_url}?{'&'.join(query_parts)}"
                    
                    self.driver.get(url)
                    self.random_delay(2, 4)
                    
                    print(f"📍 Current URL: {self.driver.current_url}")
                    print(f"📄 Page title: {self.driver.title}")
                    
                    # Handle consent/cookie pages
                    if 'consent.google' in self.driver.current_url:
                        print("📝 Handling consent page...")
                        try:
                            # Try different consent button selectors
                            consent_buttons = [
                                'button[aria-label*="Accept"]',
                                'button[aria-label*="I agree"]', 
                                'form[action*="consent"] button',
                                '#L2AGLb',  # Common Google consent button ID
                                'button:contains("I agree")'
                            ]
                            
                            for selector in consent_buttons:
                                try:
                                    buttons = self.driver.find_elements(By.CSS_SELECTOR, selector)
                                    if buttons:
                                        buttons[0].click()
                                        self.random_delay(2, 3)
                                        break
                                except:
                                    continue
                        except:
                            pass
                    
                    # Check for blocking
                    if self.detect_captcha_or_blocking():
                        print("⚠️ Anti-bot measures detected, trying next strategy...")
                        self.random_delay(5, 8)
                        continue
                    
                    # Extract URLs from current page
                    batch_urls = self.extract_linkedin_urls()
                    
                    # Add unique URLs
                    for url in batch_urls:
                        if url not in profile_links and len(profile_links) < max_results:
                            profile_links.append(url)
                    
                    print(f"✅ Found {len(batch_urls)} profiles (total: {len(profile_links)})")
                    
                    if batch_urls:
                        self.random_delay(2, 4)  # Success - moderate delay
                    else:
                        self.random_delay(3, 6)  # No results - longer delay
                        
                except Exception as e:
                    print(f"❌ Strategy {i+1} failed: {str(e)}")
                    self.random_delay(2, 4)
                    continue
            
            if profile_links:
                print(f"🎯 SUCCESS: Found {len(profile_links)} LinkedIn profiles!")
            else:
                print("⚠️ No LinkedIn profiles found with any search strategy")
                print("This could be due to:")
                print("  - No matching profiles exist")
                print("  - Google is blocking automated searches")  
                print("  - Search terms too specific")
                
                # Try alternative scraper as fallback
                print("\n🔄 Trying alternative scraping methods...")
                try:
                    alt_scraper = AlternativeLinkedInScraper()
                    alt_profiles = alt_scraper.scrape_linkedin_profiles(search_query, max_results)
                    
                    if alt_profiles:
                        print(f"✅ Alternative scraper found {len(alt_profiles)} profiles!")
                        profile_links.extend(alt_profiles)
                    else:
                        print("❌ Alternative scraper also found no results")
                        
                except Exception as e:
                    print(f"❌ Alternative scraper failed: {str(e)}")

            return profile_links[:max_results]
            
        except Exception as e:
            print(f"❌ Google search failed: {str(e)}")
            return []
    
    def scrape_profile_info(self, profile_url):
        """Extract information from a LinkedIn profile URL"""
        try:
            self.driver.get(profile_url)
            self.random_delay(2, 4)
            
            profile_data = {
                'name': 'N/A',
                'title': 'N/A',
                'company': 'N/A',
                'location': 'N/A',
                'linkedin_url': profile_url,
                'email': None
            }
            
            # Try to extract name
            try:
                name_selectors = [
                    'h1.text-heading-xlarge',
                    '.pv-text-details__left-panel h1',
                    '.profile-photo-edit__preview'
                ]
                
                for selector in name_selectors:
                    try:
                        name_element = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, selector)))
                        if name_element and name_element.text.strip():
                            profile_data['name'] = name_element.text.strip()
                            break
                    except:
                        continue
                        
            except Exception as e:
                print(f"Could not extract name: {str(e)}")
            
            # Try to extract title
            try:
                title_selectors = [
                    '.text-body-medium.break-words',
                    '.pv-text-details__left-panel .text-body-medium',
                    '.profile-photo-edit__preview + div'
                ]
                
                for selector in title_selectors:
                    try:
                        title_element = self.driver.find_element(By.CSS_SELECTOR, selector)
                        if title_element and title_element.text.strip():
                            profile_data['title'] = title_element.text.strip()
                            break
                    except:
                        continue
                        
            except Exception as e:
                print(f"Could not extract title: {str(e)}")
            
            # Try to extract location
            try:
                location_selectors = [
                    '.text-body-small.inline.t-black--light.break-words',
                    '.pv-text-details__left-panel .text-body-small',
                    '[data-field="location"]'
                ]
                
                for selector in location_selectors:
                    try:
                        location_element = self.driver.find_element(By.CSS_SELECTOR, selector)
                        if location_element and location_element.text.strip():
                            profile_data['location'] = location_element.text.strip()
                            break
                    except:
                        continue
                        
            except Exception as e:
                print(f"Could not extract location: {str(e)}")
            
            # Try to extract company from experience section
            try:
                company_selectors = [
                    '.pv-entity__secondary-title',
                    '.experience-item__subtitle',
                    '[data-field="experience"] .pv-entity__secondary-title'
                ]
                
                for selector in company_selectors:
                    try:
                        company_element = self.driver.find_element(By.CSS_SELECTOR, selector)
                        if company_element and company_element.text.strip():
                            profile_data['company'] = company_element.text.strip()
                            break
                    except:
                        continue
                        
            except Exception as e:
                print(f"Could not extract company: {str(e)}")
            
            # Try to find email in contact info or about section
            try:
                page_text = self.driver.page_source
                email = self.extract_email_from_text(page_text)
                if email:
                    profile_data['email'] = email
            except Exception as e:
                print(f"Could not extract email: {str(e)}")
            
            return profile_data
            
        except Exception as e:
            print(f"Error scraping profile {profile_url}: {str(e)}")
            return None
    
    def scrape_profiles(self, search_params, progress_callback=None):
        """Main scraping function"""
        try:
            if not self.setup_driver():
                raise Exception("Failed to setup web driver")
            
            all_results = []
            total_requested = search_params['num_results']
            current_count = 0
            
            # Process each job title and location combination
            for job_title in search_params['job_titles']:
                for location in search_params['locations']:
                    if self.stop_requested:
                        break
                    
                    # Create more effective search queries
                    search_variants = [
                        f"{job_title} {location}",
                        f"{job_title} in {location}", 
                        f"{job_title} {location} Ireland" if 'galway' in location.lower() else f"{job_title} {location}"
                    ]
                    
                    for search_query in search_variants:
                        if current_count >= total_requested or self.stop_requested:
                            break
                            
                        if progress_callback:
                            progress_callback(current_count, total_requested, 
                                            f"Searching: {search_query}")
                        
                        # Get profile URLs from Google search
                        try:
                            remaining_needed = total_requested - current_count
                            profile_urls = self.scrape_google_search_results(
                                search_query, 
                                min(20, remaining_needed)
                            )
                            
                            # If Google returns no results, try DuckDuckGo as fallback
                            if not profile_urls:
                                print(f"🔄 Google found nothing for '{search_query}', trying DuckDuckGo...")
                                profile_urls = self.scrape_duckduckgo_search_results(
                                    search_query,
                                    min(15, remaining_needed)
                                )
                            
                            if not profile_urls:
                                print(f"❌ No profiles found for '{search_query}' with any search engine")
                                continue
                            
                            print(f"🔍 Processing {len(profile_urls)} profiles from '{search_query}'")
                            
                            # Process each profile URL
                            for i, profile_url in enumerate(profile_urls):
                                if current_count >= total_requested or self.stop_requested:
                                    break
                                
                                if progress_callback:
                                    progress_callback(current_count, total_requested, 
                                                    f"Extracting profile {i+1}/{len(profile_urls)}")
                                
                                # Skip if we already have this profile
                                if any(result.get('linkedin_url') == profile_url for result in all_results):
                                    continue
                                
                                try:
                                    profile_data = self.scrape_profile_info(profile_url)
                                    if profile_data:
                                        # Add search context
                                        profile_data['search_query'] = search_query
                                        profile_data['job_title_searched'] = job_title
                                        profile_data['location_searched'] = location
                                        
                                        all_results.append(profile_data)
                                        current_count += 1
                                        
                                        print(f"✅ Profile {current_count}: {profile_data.get('name', 'Unknown')} - {profile_data.get('title', 'No title')}")
                                    else:
                                        print(f"⚠️  Could not extract data from {profile_url}")
                                        
                                except Exception as e:
                                    print(f"❌ Error processing {profile_url}: {str(e)}")
                                    continue
                                
                                # Small delay between profile scraping
                                if not self.stop_requested:
                                    self.random_delay(1, 3)
                            
                            # If we found profiles with this variant, don't try other variants for this job/location combo
                            if profile_urls:
                                break
                                
                        except Exception as e:
                            print(f"❌ Search failed for '{search_query}': {str(e)}")
                            continue
                    
                    # Break out of location loop if we have enough results
                    if current_count >= total_requested:
                        break
                
                # Break out of job title loop if we have enough results  
                if current_count >= total_requested:
                    break
            
            # Convert results to DataFrame
            if all_results:
                self.results_df = pd.DataFrame(all_results)
                
                # Remove duplicates based on LinkedIn URL
                self.results_df = self.results_df.drop_duplicates(subset=['linkedin_url'], keep='first')
                
                if progress_callback:
                    progress_callback(len(self.results_df), total_requested, 
                                    f"Completed! Found {len(self.results_df)} unique profiles")
            else:
                if progress_callback:
                    progress_callback(0, total_requested, "No profiles found")
            
            return self.results_df
            
        except Exception as e:
            if progress_callback:
                progress_callback(0, 0, f"Error: {str(e)}")
            raise Exception(f"Scraping failed: {str(e)}")
        
        finally:
            self.cleanup()
    
    def stop_scraping(self):
        """Stop the scraping process"""
        self.stop_requested = True
    
    def cleanup(self):
        """Clean up resources"""
        if self.driver:
            try:
                self.driver.quit()
            except:
                pass
            self.driver = None

def scrape_profiles(params):
    """Legacy function for backward compatibility"""
    scraper = LinkedInScraper()
    try:
        return scraper.scrape_profiles(params)
    finally:
        scraper.cleanup()
