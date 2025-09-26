# Scraping engine for LeadSprinter
# Uses Selenium to scrape LinkedIn profiles

import time
import random
import pandas as pd
from selenium import webdriver
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
        
        # Performance optimizations
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--disable-extensions')
        chrome_options.add_argument('--disable-images')  # Faster loading
        chrome_options.add_argument('--disable-javascript')  # For basic scraping
        
        # User agent to appear more legitimate
        chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36')
        
        # Window size
        chrome_options.add_argument('--window-size=1920,1080')
        
        # Optional: Run headless (uncomment for background operation)
        # chrome_options.add_argument('--headless')
        
        try:
            self.driver = webdriver.Chrome(options=chrome_options)
            self.wait = WebDriverWait(self.driver, 10)
            return True
        except Exception as e:
            raise Exception(f"Failed to setup Chrome driver: {str(e)}")
    
    def random_delay(self, min_seconds=1, max_seconds=3):
        """Add random delay to avoid detection"""
        if not self.stop_requested:
            time.sleep(random.uniform(min_seconds, max_seconds))
    
    def extract_email_from_text(self, text):
        """Extract email from text using regex"""
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        emails = re.findall(email_pattern, text)
        return emails[0] if emails else None
    
    def scrape_google_search_results(self, search_query, num_results, progress_callback=None):
        """Scrape LinkedIn profiles from Google search results"""
        try:
            # Format Google search query for LinkedIn profiles
            google_query = f'site:linkedin.com/in/ "{search_query}"'
            search_url = f'https://www.google.com/search?q={quote(google_query)}&num={min(num_results, 100)}'
            
            if progress_callback:
                progress_callback(0, num_results, f"Starting Google search for: {search_query}")
            
            self.driver.get(search_url)
            self.random_delay(2, 4)
            
            # Find LinkedIn profile links
            profile_links = []
            try:
                # Look for LinkedIn profile links in search results
                links = self.driver.find_elements(By.XPATH, "//a[contains(@href, 'linkedin.com/in/')]")
                
                for link in links[:num_results]:
                    href = link.get_attribute('href')
                    if href and 'linkedin.com/in/' in href and href not in profile_links:
                        profile_links.append(href)
                
            except Exception as e:
                print(f"Error finding profile links: {str(e)}")
            
            return profile_links
            
        except Exception as e:
            raise Exception(f"Error in Google search: {str(e)}")
    
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
                        
                    search_query = f"{job_title} {location}"
                    
                    if progress_callback:
                        progress_callback(current_count, total_requested, 
                                        f"Searching for: {search_query}")
                    
                    # Get profile URLs from Google search
                    try:
                        profile_urls = self.scrape_google_search_results(
                            search_query, 
                            min(20, total_requested - current_count)
                        )
                        
                        # Process each profile URL
                        for url in profile_urls:
                            if self.stop_requested or current_count >= total_requested:
                                break
                            
                            if progress_callback:
                                progress_callback(current_count, total_requested, 
                                                f"Processing profile {current_count + 1}/{total_requested}")
                            
                            profile_data = self.scrape_profile_info(url)
                            if profile_data:
                                all_results.append(profile_data)
                                current_count += 1
                            
                            self.random_delay(2, 5)  # Longer delay between profiles
                            
                    except Exception as e:
                        print(f"Error processing search query '{search_query}': {str(e)}")
                        continue
                    
                    if current_count >= total_requested:
                        break
                
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
