#!/usr/bin/env python3
"""
Simple setup runner - just run this file to set up everything!
"""

import subprocess
import sys
import os
from pathlib import Path

def main():
    print("🌍 CarbonTrace - One-Click Setup")
    print("=" * 40)
    
    # Check if setup file exists
    setup_file = Path("setup_complete_system.py")
    
    if not setup_file.exists():
        print("❌ Setup file not found!")
        print("Please ensure you're in the correct directory.")
        return
    
    try:
        # Run the complete setup
        print("🚀 Running automated setup...")
        subprocess.run([sys.executable, str(setup_file)], check=True)
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Setup failed with error: {e}")
        print("Please check the error messages above.")
    except KeyboardInterrupt:
        print("\n⚠️ Setup interrupted by user.")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

if __name__ == "__main__":
    main()
