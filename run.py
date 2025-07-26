#!/usr/bin/env python
"""
Mathly - AI Math Assistant
Run script to easily start the Mathly chatbot application
"""
import os
import webbrowser
import time
import subprocess
import sys
import argparse
from pathlib import Path

def check_dependencies():
    """Check if required dependencies are installed"""
    try:
        import flask
        import flask_cors
        import numpy
        import requests
        print("✅ All required dependencies are installed")
        return True
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("Installing required dependencies...")
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("Please restart the application after installing dependencies.")
        return False

def main():
    """Main function to run the Mathly chatbot application"""
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Run Mathly AI Math Assistant")
    parser.add_argument("--port", type=int, default=5000, help="Port to run the server on")
    parser.add_argument("--no-browser", action="store_true", help="Don't open the browser automatically")
    parser.add_argument("--formula-file", type=str, default="expanded_formulas.json", 
                      help="Formula file to use (math_formulas.json or expanded_formulas.json)")
    args = parser.parse_args()
    
    print("Starting Mathly - AI Math Assistant...")
    print("=" * 50)
    
    # Get the root directory of the project
    root_dir = Path(__file__).parent
    backend_dir = root_dir / 'backend'
    
    # Check dependencies
    if not check_dependencies():
        return
    
    # Start the Flask server
    print("\nStarting the backend server...")
    server_process = subprocess.Popen(
        ["python", os.path.join(backend_dir, "app.py")],
        cwd=backend_dir
    )
    
    # Wait a bit for the server to start
    time.sleep(2)
    
    # Open the web browser
    print("Opening Mathly in your web browser...")
    webbrowser.open("http://localhost:5001")
    
    print("\n" + "=" * 50)
    print("Mathly is now running!")
    print("Access the chatbot at: http://localhost:5001")
    print("Press Ctrl+C to stop the server")
    
    try:
        # Keep the script running
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        # Stop the server when Ctrl+C is pressed
        server_process.terminate()
        print("\nShutting down Mathly...")
        print("Thank you for using Mathly!")

if __name__ == "__main__":
    main()
