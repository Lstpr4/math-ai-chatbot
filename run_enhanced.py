#!/usr/bin/env python
"""
Mathly - AI Math Assistant
Enhanced run script with additional options
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
        subprocess.check_call([sys.executable, "-m", "pip", "show", "flask"], 
                            stdout=subprocess.DEVNULL, 
                            stderr=subprocess.DEVNULL)
        print("✅ Dependencies appear to be installed")
        return True
    except subprocess.CalledProcessError:
        print("❌ Missing dependencies")
        print("Installing required dependencies...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
            print("✅ Dependencies installed successfully")
            return True
        except subprocess.CalledProcessError:
            print("❌ Failed to install dependencies")
            print("Please manually install the dependencies with:")
            print("pip install -r requirements.txt")
            return False

def main():
    """Main function to run the Mathly chatbot application"""
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Run Mathly AI Math Assistant")
    parser.add_argument("--port", type=int, default=5000, help="Port to run the server on")
    parser.add_argument("--no-browser", action="store_true", help="Don't open the browser automatically")
    parser.add_argument("--formula-file", type=str, choices=["math_formulas.json", "expanded_formulas.json"], 
                      default="expanded_formulas.json", 
                      help="Formula file to use")
    args = parser.parse_args()
    
    print("Starting Mathly - AI Math Assistant...")
    print("=" * 50)
    
    # Get the root directory of the project
    root_dir = Path(__file__).parent
    backend_dir = root_dir / 'backend'
    data_dir = root_dir / 'data'
    
    # Check dependencies
    if not check_dependencies():
        return
    
    # Validate formula file exists
    formula_path = data_dir / args.formula_file
    if not formula_path.exists():
        print(f"❌ Error: Formula file '{args.formula_file}' not found in data directory")
        return
        
    print(f"Using formula file: {args.formula_file}")
    
    # Set environment variable for the Flask app to use the selected formula file
    os.environ["MATHLY_FORMULA_FILE"] = str(formula_path)
    
    # Start the Flask server with the specified port
    print(f"\nStarting the backend server on port {args.port}...")
    server_cmd = [sys.executable, os.path.join(backend_dir, "app.py")]
    if args.port != 5000:
        server_cmd.append(f"--port={args.port}")
        
    server_process = subprocess.Popen(
        server_cmd,
        cwd=backend_dir,
        env=dict(os.environ)
    )
    
    # Wait for the server to start
    time.sleep(2)
    
    # Open the browser if not disabled
    if not args.no_browser:
        print("Opening Mathly in your default web browser...")
        webbrowser.open(f"http://localhost:{args.port}")
    
    print("\n" + "=" * 50)
    print("Mathly is now running!")
    print(f"Access it at http://localhost:{args.port}")
    print("Press Ctrl+C to shut down the server when you're done.")
    print("=" * 50)
    
    try:
        # Keep the script running until interrupted
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nShutting down Mathly...")
        server_process.terminate()
        print("Goodbye!")

if __name__ == "__main__":
    main()
