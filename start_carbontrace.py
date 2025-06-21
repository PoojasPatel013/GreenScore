#!/usr/bin/env python3
"""
CarbonTrace Quick Start Script
Run this to start the application with sample data
"""

import subprocess
import sys
import os
from pathlib import Path

def main():
    print("CarbonTrace - Starting Application...")
    
    # Check if we're in the right directory
    if not Path("app.py").exists():
        print("ERROR: app.py not found. Please run from the project root directory.")
        return
    
    # Set environment variables for demo
    os.environ["DEMO_MODE"] = "True"
    os.environ["USE_SAMPLE_DATA"] = "True"
    
    try:
        # Start Streamlit app
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", "app.py",
            "--server.port", "8501",
            "--server.address", "localhost"
        ])
    except KeyboardInterrupt:
        print("\nCarbonTrace stopped.")
    except Exception as e:
        print(f"ERROR: Error starting CarbonTrace: {e}")

if __name__ == "__main__":
    main()
