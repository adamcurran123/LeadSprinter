# PySimpleGUI interface for LeadSprinter
import PySimpleGUI as sg
import threading
import time
from datetime import datetime
from scraper import LinkedInScraper
from data_handler import DataHandler

class LeadSprinterGUI:
    def __init__(self):
        # Set professional theme - handle different PySimpleGUI versions
        try:
            sg.theme('DarkBlue3')
        except AttributeError:
            try:
                sg.theme_global('DarkBlue3')
            except AttributeError:
                try:
                    sg.change_look_and_feel('DarkBlue3')
                except AttributeError:
                    # Fallback for older versions or if theme doesn't exist
                    pass
        
        self.scraper = None
        self.data_handler = DataHandler()
        self.scraping_active = False
        
    def create_layout(self):
        """Create the main GUI layout"""
        
        # Header section
        header = [
            [sg.Text('LeadSprinter Pro', font=('Arial', 24, 'bold'), 
                    text_color='white', justification='center', expand_x=True)],
            [sg.Text('Professional LinkedIn Lead Generation Tool', 
                    font=('Arial', 12), text_color='lightblue', 
                    justification='center', expand_x=True)],
            [sg.HSeparator(color='lightblue')]
        ]
        
        # Input section
        input_section = [
            [sg.Text('Search Parameters', font=('Arial', 14, 'bold'), 
                    text_color='white', pad=(0, (10, 5)))],
            
            [sg.Text('Job Titles/Keywords:', size=(18, 1)), 
             sg.Input(key='-JOB_TITLES-', size=(40, 1), 
                     tooltip='Enter job titles separated by commas (e.g., Marketing Manager, Sales Director)')],
            
            [sg.Text('Locations:', size=(18, 1)), 
             sg.Input(key='-LOCATIONS-', size=(40, 1),
                     tooltip='Enter locations separated by commas (e.g., Dublin, London, New York)')],
            
            [sg.Text('Number of Results:', size=(18, 1)), 
             sg.Spin([i for i in range(10, 501, 10)], initial_value=50, 
                    key='-NUM_RESULTS-', size=(10, 1))],
            
            [sg.Text('Industry Filter:', size=(18, 1)), 
             sg.Combo(['All Industries', 'Technology', 'Healthcare', 'Finance', 
                      'Marketing', 'Sales', 'Education', 'Manufacturing'], 
                     default_value='All Industries', key='-INDUSTRY-', size=(25, 1))],
            
            [sg.Text('Company Size:', size=(18, 1)), 
             sg.Combo(['All Sizes', '1-10', '11-50', '51-200', '201-500', 
                      '501-1000', '1000+'], default_value='All Sizes', 
                     key='-COMPANY_SIZE-', size=(25, 1))]
        ]
        
        # Control buttons section
        control_section = [
            [sg.HSeparator(pad=(0, (10, 10)))],
            [sg.Button('Start Scraping', key='-START-', size=(15, 2), 
                      button_color=('white', '#28a745'), font=('Arial', 10, 'bold')),
             sg.Button('Stop Scraping', key='-STOP-', size=(15, 2), 
                      button_color=('white', '#dc3545'), font=('Arial', 10, 'bold'), 
                      disabled=True),
             sg.Button('Export Results', key='-EXPORT-', size=(15, 2), 
                      button_color=('white', '#007bff'), font=('Arial', 10, 'bold'), 
                      disabled=True)]
        ]
        
        # Progress section
        progress_section = [
            [sg.HSeparator(pad=(0, (10, 10)))],
            [sg.Text('Progress', font=('Arial', 14, 'bold'), text_color='white')],
            [sg.ProgressBar(100, orientation='h', size=(50, 20), key='-PROGRESS-')],
            [sg.Text('Ready to start...', key='-STATUS-', size=(60, 1), 
                    text_color='lightgreen')],
            [sg.Text('Profiles Found: 0', key='-COUNTER-', font=('Arial', 10, 'bold'), 
                    text_color='yellow')]
        ]
        
        # Results preview section
        results_section = [
            [sg.HSeparator(pad=(0, (10, 10)))],
            [sg.Text('Recent Results Preview', font=('Arial', 14, 'bold'), 
                    text_color='white')],
            [sg.Table(values=[], headings=['Name', 'Title', 'Company', 'Location'],
                     key='-RESULTS_TABLE-', size=(70, 10), justification='left',
                     alternating_row_color='lightblue', row_height=25)]
        ]
        
        # Footer
        footer = [
            [sg.HSeparator(pad=(0, (10, 5)))],
            [sg.Text('© 2025 LeadSprinter Pro - Professional Lead Generation', 
                    font=('Arial', 8), text_color='gray', justification='center', 
                    expand_x=True)]
        ]
        
        # Combine all sections
        layout = header + input_section + control_section + progress_section + results_section + footer
        
        return layout
    
    def validate_inputs(self, values):
        """Validate user inputs"""
        errors = []
        
        if not values['-JOB_TITLES-'].strip():
            errors.append("Job titles/keywords are required")
        
        if not values['-LOCATIONS-'].strip():
            errors.append("Locations are required")
            
        if values['-NUM_RESULTS-'] < 1:
            errors.append("Number of results must be at least 1")
        
        return errors
    
    def update_progress(self, window, current, total, status_text=""):
        """Update progress bar and status"""
        progress = int((current / total) * 100) if total > 0 else 0
        window['-PROGRESS-'].update(progress)
        window['-STATUS-'].update(status_text)
        window['-COUNTER-'].update(f'Profiles Found: {current}')
        
    def update_results_preview(self, window, results_df):
        """Update the results preview table"""
        if results_df.empty:
            return
            
        # Show last 10 results
        preview_data = results_df.tail(10)[['name', 'title', 'company', 'location']].values.tolist()
        window['-RESULTS_TABLE-'].update(values=preview_data)
    
    def scraping_thread(self, window, search_params):
        """Run scraping in separate thread"""
        self.scraping_active = True
        
        try:
            self.scraper = LinkedInScraper()
            results_df = self.scraper.scrape_profiles(
                search_params, 
                progress_callback=lambda current, total, status: 
                    self.update_progress(window, current, total, status)
            )
            
            if not results_df.empty:
                self.data_handler.store_results(results_df)
                self.update_results_preview(window, results_df)
                window['-EXPORT-'].update(disabled=False)
                window['-STATUS-'].update("Scraping completed successfully!")
            else:
                window['-STATUS-'].update("No results found. Try different search parameters.")
                
        except Exception as e:
            window['-STATUS-'].update(f"Error: {str(e)}")
        finally:
            self.scraping_active = False
            window['-START-'].update(disabled=False)
            window['-STOP-'].update(disabled=True)
    
    def run(self):
        """Main GUI loop"""
        layout = self.create_layout()
        
        window = sg.Window('LeadSprinter Pro - Professional Lead Generation', 
                          layout, 
                          size=(800, 700),
                          finalize=True,
                          icon=None,  # Add icon later
                          resizable=True)
        
        while True:
            event, values = window.read(timeout=1000)
            
            if event == sg.WIN_CLOSED:
                break
                
            elif event == '-START-':
                # Validate inputs
                errors = self.validate_inputs(values)
                if errors:
                    sg.popup_error('Input Errors:\n' + '\n'.join(errors), 
                                  title='Validation Error')
                    continue
                
                # Prepare search parameters
                search_params = {
                    'job_titles': [title.strip() for title in values['-JOB_TITLES-'].split(',')],
                    'locations': [loc.strip() for loc in values['-LOCATIONS-'].split(',')],
                    'num_results': values['-NUM_RESULTS-'],
                    'industry': values['-INDUSTRY-'] if values['-INDUSTRY-'] != 'All Industries' else None,
                    'company_size': values['-COMPANY_SIZE-'] if values['-COMPANY_SIZE-'] != 'All Sizes' else None
                }
                
                # Start scraping in background thread
                window['-START-'].update(disabled=True)
                window['-STOP-'].update(disabled=False)
                window['-STATUS-'].update('Starting scraper...')
                
                threading.Thread(target=self.scraping_thread, 
                               args=(window, search_params), daemon=True).start()
            
            elif event == '-STOP-':
                if self.scraper:
                    self.scraper.stop_scraping()
                self.scraping_active = False
                window['-START-'].update(disabled=False)
                window['-STOP-'].update(disabled=True)
                window['-STATUS-'].update('Scraping stopped by user')
            
            elif event == '-EXPORT-':
                if self.data_handler.has_data():
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    job_title = values['-JOB_TITLES-'].replace(',', '_').replace(' ', '_')
                    filename = f"LeadSprinter_Results_{job_title}_{timestamp}.xlsx"
                    
                    try:
                        filepath = self.data_handler.export_to_excel(filename, search_params=values)
                        sg.popup_ok(f'Results exported successfully!\n\nFile saved as:\n{filepath}',
                                   title='Export Complete')
                    except Exception as e:
                        sg.popup_error(f'Export failed:\n{str(e)}', title='Export Error')
                else:
                    sg.popup_error('No data to export. Please run a search first.', 
                                  title='Export Error')
        
        window.close()
        
        # Cleanup
        if self.scraper:
            self.scraper.cleanup()

def run_gui():
    """Entry point for GUI"""
    try:
        # Check if we can actually run GUI in this environment
        import os
        if not os.environ.get('DISPLAY') and not os.environ.get('WAYLAND_DISPLAY'):
            raise Exception("No display available - GUI cannot run in headless environment")
        
        app = LeadSprinterGUI()
        app.run()
    except Exception as e:
        print(f"GUI cannot run: {str(e)}")
        print("This is normal in headless environments like Codespaces")
        raise
