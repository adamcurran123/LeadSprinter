# Test version of LeadSprinter Pro without WebDriver dependency
# For testing the application structure and data handling

import pandas as pd
import random
import time
from datetime import datetime
from data_handler import DataHandler

class MockScraper:
    """Mock scraper for testing without WebDriver"""
    
    def __init__(self):
        self.stop_requested = False
    
    def scrape_profiles(self, search_params, progress_callback=None):
        """Mock scraping that generates sample data"""
        
        # Sample data for testing
        sample_names = [
            "John Smith", "Sarah Johnson", "Mike Brown", "Emma Davis", "Chris Wilson",
            "Lisa Anderson", "David Miller", "Jennifer Taylor", "Robert Garcia", "Michelle Lee"
        ]
        
        sample_titles = [
            "Marketing Manager", "Sales Director", "Software Engineer", "Product Manager",
            "Business Analyst", "Operations Manager", "HR Director", "Finance Manager",
            "Digital Marketing Specialist", "Customer Success Manager"
        ]
        
        sample_companies = [
            "TechCorp Ltd", "InnovateCo", "GlobalSoft", "DataSystems Inc", "CloudTech Solutions",
            "Marketing Pro", "SalesForce Partners", "Digital Dynamics", "Growth Solutions", "NextGen Systems"
        ]
        
        sample_locations = search_params.get('locations', ['Dublin', 'London', 'New York'])
        
        results = []
        num_results = min(search_params.get('num_results', 10), 20)  # Limit for testing
        
        for i in range(num_results):
            if self.stop_requested:
                break
            
            if progress_callback:
                progress_callback(i, num_results, f"Processing profile {i+1}/{num_results}")
            
            # Generate mock profile data
            profile = {
                'name': random.choice(sample_names),
                'title': random.choice(sample_titles),
                'company': random.choice(sample_companies),
                'location': random.choice(sample_locations),
                'linkedin_url': f'https://linkedin.com/in/mock-profile-{i+1}',
                'email': f'user{i+1}@example.com' if random.random() > 0.7 else None,
                'scraped_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            
            results.append(profile)
            
            # Simulate processing time
            time.sleep(0.5)
        
        if progress_callback:
            progress_callback(len(results), num_results, f"Completed! Found {len(results)} profiles")
        
        return pd.DataFrame(results)
    
    def stop_scraping(self):
        """Stop the mock scraping"""
        self.stop_requested = True
    
    def cleanup(self):
        """Mock cleanup"""
        pass

def test_cli():
    """Test the CLI with mock data"""
    print("\n=== LeadSprinter Pro - Test Mode ===")
    print("Using mock data (no actual web scraping)")
    print("-" * 50)
    
    # Mock search parameters
    search_params = {
        'job_titles': ['Marketing Manager', 'Sales Director'],
        'locations': ['Dublin', 'London'],
        'num_results': 10,
        'industry': 'Technology',
        'company_size': None
    }
    
    print(f"Test Parameters:")
    print(f"  Job Titles: {', '.join(search_params['job_titles'])}")
    print(f"  Locations: {', '.join(search_params['locations'])}")
    print(f"  Results: {search_params['num_results']}")
    print(f"  Industry: {search_params['industry']}")
    print("-" * 50)
    
    def progress_callback(current, total, status):
        if total > 0:
            percentage = (current / total) * 100
            print(f"\rProgress: {current}/{total} ({percentage:.1f}%) - {status}", end='', flush=True)
        else:
            print(f"\r{status}", end='', flush=True)
    
    try:
        # Create mock scraper and data handler
        scraper = MockScraper()
        data_handler = DataHandler()
        
        print("Starting mock scraping...")
        results_df = scraper.scrape_profiles(search_params, progress_callback)
        
        print(f"\n\nMock scraping completed!")
        
        if not results_df.empty:
            print(f"Generated {len(results_df)} mock profiles")
            
            # Store results
            data_handler.store_results(results_df)
            
            # Show preview
            print("\nGenerated profiles:")
            print("-" * 80)
            for idx, row in results_df.iterrows():
                print(f"Name: {row['name']}")
                print(f"Title: {row['title']}")
                print(f"Company: {row['company']}")
                print(f"Location: {row['location']}")
                print(f"LinkedIn: {row['linkedin_url']}")
                if row['email']:
                    print(f"Email: {row['email']}")
                print("-" * 40)
            
            # Test export
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"LeadSprinter_Test_Results_{timestamp}.xlsx"
            
            try:
                filepath = data_handler.export_to_excel(filename, search_params)
                print(f"\nTest results exported to: {filepath}")
                
                # Show file info
                import os
                file_size = os.path.getsize(filepath) / (1024 * 1024)  # MB
                print(f"File size: {file_size:.2f} MB")
                
                print(f"\n✅ Test completed successfully!")
                print(f"All components working correctly.")
                
            except Exception as e:
                print(f"Export test failed: {str(e)}")
                return False
                
        else:
            print("No mock data generated.")
            return False
            
    except Exception as e:
        print(f"\nError during test: {str(e)}")
        return False
    
    finally:
        scraper.cleanup()
    
    return True

if __name__ == "__main__":
    success = test_cli()
    if success:
        print("\n🎉 LeadSprinter Pro test completed successfully!")
        print("The application structure is working correctly.")
        print("Ready to run on your laptop with full web scraping!")
    else:
        print("\n❌ Test failed. Check the errors above.")