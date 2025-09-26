#!/usr/bin/env python3
"""
LeadSprinter Pro - GUI Only Launcher
Forces GUI mode without any environment detection or CLI fallback
"""

import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def main():
    """Launch GUI directly"""
    print("=== LeadSprinter Pro - GUI Mode ===")
    print("Professional LinkedIn Lead Generation Tool")
    print("Starting GUI interface...")
    
    try:
        from gui import run_gui
        run_gui()
    except Exception as e:
        print(f"\nError launching GUI: {e}")
        print("\nPossible solutions:")
        print("1. Install/upgrade PySimpleGUI: pip install --upgrade PySimpleGUI")
        print("2. Check if you have a display available")
        print("3. Try running from a desktop environment")
        
        import traceback
        print(f"\nFull error details:")
        traceback.print_exc()
        
        input("Press Enter to exit...")
        sys.exit(1)

if __name__ == "__main__":
    main()