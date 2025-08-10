#!/usr/bin/env python3
"""
Server Runner for Medicine Alternative System
Builds frontend and starts the FastAPI server.
"""

import subprocess
import sys
import os
from pathlib import Path

def run_command(command, cwd=None, description=""):
    """Run a command and handle errors."""
    print(f"🔄 {description}")
    try:
        result = subprocess.run(command, shell=True, cwd=cwd, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed:")
        print(f"Error: {e.stderr}")
        return False

def main():
    """Main function to build and start the application."""
    print("🚀 Starting Medicine Alternative System...")
    
    # Check if we're in the right directory
    if not os.path.exists("backend_api.py"):
        print("❌ Please run this script from the med_agent directory")
        sys.exit(1)
    
    # Check if database exists
    if not os.path.exists("medicines.db"):
        print("🗄️ Creating medicine database...")
        if not run_command("python3 create_medicine_db.py", description="Creating medicine database"):
            print("❌ Failed to create database. Please run 'python3 create_medicine_db.py' manually.")
            sys.exit(1)
    
    # Build frontend
    frontend_dir = Path("generic-saver-bot")
    if frontend_dir.exists():
        print("🔨 Building frontend...")
        if not run_command("npm install", cwd=str(frontend_dir), description="Installing frontend dependencies"):
            print("❌ Failed to install frontend dependencies")
            sys.exit(1)
        
        if not run_command("npm run build", cwd=str(frontend_dir), description="Building frontend"):
            print("❌ Failed to build frontend")
            sys.exit(1)
    else:
        print("⚠️ Frontend directory not found, serving API only")
    
    # Check environment variables
    if not os.getenv("GOOGLE_API_KEY"):
        print("⚠️ Warning: GOOGLE_API_KEY environment variable not set")
        print("   The system may not work properly without a Gemini API key")
        print("   Set it with: export GOOGLE_API_KEY='your_api_key'")
    
    # Start the server
    print("\n🌟 Starting the application...")
    print("📊 Frontend will be available at: http://localhost:8000")
    print("🔗 API documentation at: http://localhost:8000/docs")
    print("🛑 Press Ctrl+C to stop the server")
    print("-" * 50)
    
    try:
        subprocess.run(["python3", "backend_api.py"], check=True)
    except KeyboardInterrupt:
        print("\n👋 Server stopped by user")
    except Exception as e:
        print(f"\n❌ Server error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 