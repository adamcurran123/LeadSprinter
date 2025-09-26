#!/usr/bin/env python3
"""
Test PySimpleGUI installation and basic functionality
"""

import sys

def test_pysimplegui():
    """Test if PySimpleGUI can create a basic window"""
    try:
        import PySimpleGUI as sg
        print("✅ PySimpleGUI imported successfully")
        
        # Check PySimpleGUI version and attributes
        try:
            version = sg.version if hasattr(sg, 'version') else 'Unknown'
            print(f"PySimpleGUI version: {version}")
        except:
            print("Could not determine PySimpleGUI version")
        
        # Check for Text attribute
        if not hasattr(sg, 'Text'):
            print("❌ PySimpleGUI is missing Text attribute - installation is incomplete")
            print("This usually means PySimpleGUI needs to be properly installed from the new server")
            return False
        
        # Try to set a theme
        try:
            sg.theme('DarkBlue3')
            print("✅ Theme set successfully")
        except:
            print("⚠️  Theme setting failed, but continuing...")
        
        # Create a simple test window
        layout = [
            [sg.Text('PySimpleGUI Test Window')],
            [sg.Text('If you can see this, PySimpleGUI is working!')],
            [sg.Button('OK'), sg.Button('Cancel')]
        ]
        
        print("Creating test window...")
        window = sg.Window('PySimpleGUI Test', layout, finalize=True)
        print("✅ Test window created successfully!")
        print("✅ PySimpleGUI is working properly on your system!")
        
        # Show the window briefly
        event, values = window.read(timeout=100)
        window.close()
        
        return True
        
    except ImportError as e:
        print(f"❌ PySimpleGUI not found: {e}")
        print("Run: pip install --upgrade PySimpleGUI")
        return False
        
    except Exception as e:
        print(f"❌ PySimpleGUI test failed: {e}")
        print("This might indicate a display, GUI issue, or incomplete PySimpleGUI installation")
        
        # Try to get more specific error info
        import traceback
        print("\nDetailed error:")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("=== PySimpleGUI Test ===")
    success = test_pysimplegui()
    
    if success:
        print("\n🎉 All tests passed! LeadSprinter GUI should work.")
    else:
        print("\n❌ Tests failed. Please install PySimpleGUI properly:")
        print("\n1. Uninstall current version:")
        print("   python -m pip uninstall PySimpleGUI")
        print("   python -m pip cache purge")
        print("\n2. Install from the new server:")
        print("   python -m pip install --upgrade --extra-index-url https://PySimpleGUI.net/install PySimpleGUI")
        print("\n3. Or force reinstall:")
        print("   python -m pip install --force-reinstall --extra-index-url https://PySimpleGUI.net/install PySimpleGUI")
        print("\n4. Then run this test again:")
        print("   python test_gui.py")
        
    sys.exit(0 if success else 1)