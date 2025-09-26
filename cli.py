# Command-line interface for LeadSprinter Pro
# Useful for testing in environments without GUI support (like Codespaces)

import sys
import os
from datetime import datetime
from scraper import LinkedInScraper
from data_handler import DataHandler
import logging

class LeadSprinterCLI:
    def __init__(self):
        self.scraper = None
        self.data_handler = DataHandler()
        self.setup_logging()
    
    def setup_logging(self):
        """Setup logging for CLI"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
    
    def get_user_input(self):
        """Get search parameters from user input"""
        print("\n=== LeadSprinter Pro - Command Line Interface ===")
        print("Professional LinkedIn Lead Generation Tool")
        print("-" * 50)
        
        # Get job titles
        job_titles_input = input("Enter job titles (comma-separated): ").strip()
        if not job_titles_input:
            print("Error: Job titles are required")
            return None
        
        # Get locations
        locations_input = input("Enter locations (comma-separated): ").strip()
        if not locations_input:
            print("Error: Locations are required")
            return None
        
        # Get number of results
        try:
            num_results = int(input("Enter number of results (default 20): ") or "20")
            num_results = max(1, min(200, num_results))  # Limit for testing
        except ValueError:
            num_results = 20
        
        # Get industry filter
        print("\nAvailable industries:")
        industries = ['All', 'Technology', 'Healthcare', 'Finance', 'Marketing', 'Sales', 'Education']
        for i, industry in enumerate(industries, 1):
            print(f"{i}. {industry}")
        
        try:
            industry_choice = int(input("Select industry (1-7, default 1): ") or "1")
            industry = industries[industry_choice - 1] if 1 <= industry_choice <= len(industries) else 'All'
        except ValueError:
            industry = 'All'
        
        return {
            'job_titles': [title.strip() for title in job_titles_input.split(',')],
            'locations': [loc.strip() for loc in locations_input.split(',')],
            'num_results': num_results,
            'industry': industry if industry != 'All' else None,
            'company_size': None
        }
    
    def progress_callback(self, current, total, status):
        """Progress callback for CLI"""
        if total > 0:
            percentage = (current / total) * 100
            print(f"\rProgress: {current}/{total} ({percentage:.1f}%) - {status}", end='', flush=True)
        else:
            print(f"\r{status}", end='', flush=True)
    
    def run_scraping(self, search_params):
        """Run the scraping process"""
        print(f"\nStarting scrape with parameters:")
        print(f"  Job Titles: {', '.join(search_params['job_titles'])}")
        print(f"  Locations: {', '.join(search_params['locations'])}")
        print(f"  Results: {search_params['num_results']}")
        print(f"  Industry: {search_params['industry'] or 'All'}")
        print("-" * 50)
        
        try:
            self.scraper = LinkedInScraper()
            results_df = self.scraper.scrape_profiles(
                search_params, 
                progress_callback=self.progress_callback
            )
            
            print(f"\n\nScraping completed!")
            
            if not results_df.empty:
                print(f"Found {len(results_df)} profiles")
                
                # Store results
                self.data_handler.store_results(results_df)
                
                # Show preview
                print("\nFirst 5 results:")
                print("-" * 80)
                for idx, row in results_df.head(5).iterrows():
                    print(f"Name: {row.get('name', 'N/A')}")
                    print(f"Title: {row.get('title', 'N/A')}")
                    print(f"Company: {row.get('company', 'N/A')}")
                    print(f"Location: {row.get('location', 'N/A')}")
                    print(f"LinkedIn: {row.get('linkedin_url', 'N/A')}")
                    if row.get('email'):
                        print(f"Email: {row.get('email', 'N/A')}")
                    print("-" * 40)
                
                # Export results
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                job_title_clean = search_params['job_titles'][0].replace(' ', '_')
                filename = f"LeadSprinter_Results_{job_title_clean}_{timestamp}.xlsx"
                
                try:
                    filepath = self.data_handler.export_to_excel(filename, search_params)
                    print(f"\nResults exported to: {filepath}")
                    
                    # Show file info
                    file_size = os.path.getsize(filepath) / (1024 * 1024)  # MB
                    print(f"File size: {file_size:.2f} MB")
                    
                except Exception as e:
                    print(f"Export failed: {str(e)}")
                
            else:
                print("No results found. Try different search parameters.")
                
        except Exception as e:
            print(f"\nError during scraping: {str(e)}")
            self.logger.error(f"Scraping error: {str(e)}")
        
        finally:
            if self.scraper:
                self.scraper.cleanup()
    
    def run(self):
        """Main CLI loop"""
        try:
            search_params = self.get_user_input()
            if search_params:
                confirm = input(f"\nProceed with scraping? (y/N): ").lower().strip()
                if confirm == 'y':
                    self.run_scraping(search_params)
                else:
                    print("Operation cancelled.")
            
        except KeyboardInterrupt:
            print("\nOperation interrupted by user.")
        except Exception as e:
            print(f"Unexpected error: {str(e)}")
            self.logger.error(f"CLI error: {str(e)}")

def run_cli():
    """Entry point for CLI"""
    cli = LeadSprinterCLI()
    cli.run()

if __name__ == "__main__":
    run_cli()