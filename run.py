#!/usr/bin/env python
"""
Mathly - AI Math Assistant
Run script to easily start the Mathly chatbot application
"""
import os
import webbrowser
import time
import subprocess
from pathlib import Path

def main():
    """Main function to run the Mathly chatbot application"""
    print("Starting Mathly - AI Math Assistant...")
    print("=" * 50)
    
    # Get the root directory of the project
    root_dir = Path(__file__).parent
    backend_dir = root_dir / 'backend'
    
    # Skip dependency check since we've already installed them
    print("✅ Using pre-installed dependencies")
    
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
