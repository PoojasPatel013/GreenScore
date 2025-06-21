#!/usr/bin/env python3
"""
Fixed setup runner for Windows - handles encoding issues
"""

import subprocess
import sys
import os
from pathlib import Path

def main():
    print("CarbonTrace - One-Click Setup (Windows Compatible)")
    print("=" * 50)
    
    # Set UTF-8 encoding for Windows
    if os.name == 'nt':  # Windows
        os.environ['PYTHONIOENCODING'] = 'utf-8'
    
    # Check if setup file exists
    setup_file = Path("setup_complete_system.py")
    
    if not setup_file.exists():
        print("ERROR: Setup file not found!")
        print("Please ensure you're in the correct directory.")
        return
    
    try:
        # Run the complete setup with proper encoding
        print("Running automated setup...")
        
        # Use UTF-8 encoding for subprocess
        env = os.environ.copy()
        env['PYTHONIOENCODING'] = 'utf-8'
        
        subprocess.run([
            sys.executable, str(setup_file)
        ], check=True, env=env)
        
    except subprocess.CalledProcessError as e:
        print(f"Setup failed with error: {e}")
        print("Please check the error messages above.")
    except KeyboardInterrupt:
        print("\nSetup interrupted by user.")
    except Exception as e:
        print(f"Unexpected error: {e}")

if __name__ == "__main__":
    main()
