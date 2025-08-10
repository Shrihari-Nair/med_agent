#!/usr/bin/env python3
"""
Development Server Starter
Runs both frontend and backend in development mode.
"""

import subprocess
import sys
import os
import signal
import time
from pathlib import Path
import threading

class ServerManager:
    def __init__(self):
        self.processes = []
        
    def start_backend(self):
        """Start the FastAPI backend server."""
        print("🔄 Starting backend server...")
        try:
            # Kill any existing processes on port 8000
            try:
                subprocess.run(["pkill", "-f", "uvicorn.*backend_api"], check=False)
                time.sleep(1)
            except:
                pass
                
            process = subprocess.Popen([
                "python3", "-m", "uvicorn", "backend_api:app", 
                "--host", "0.0.0.0", "--port", "8001", "--reload"
            ])
            self.processes.append(process)
            print("✅ Backend server started on http://localhost:8001")
            return process
        except Exception as e:
            print(f"❌ Failed to start backend: {e}")
            return None
    
    def start_frontend(self):
        """Start the Vite frontend server."""
        frontend_dir = Path("generic-saver-bot")
        if not frontend_dir.exists():
            print("⚠️ Frontend directory not found")
            return None
            
        print("🔄 Starting frontend server...")
        try:
            # First install dependencies
            subprocess.run(["npm", "install"], cwd=str(frontend_dir), check=True)
            
            # Then start dev server
            process = subprocess.Popen(["npm", "run", "dev"], cwd=str(frontend_dir))
            self.processes.append(process)
            print("✅ Frontend server started on http://localhost:8080")
            return process
        except Exception as e:
            print(f"❌ Failed to start frontend: {e}")
            return None
    
    def cleanup(self):
        """Clean up all processes."""
        print("\n🛑 Stopping servers...")
        for process in self.processes:
            try:
                process.terminate()
                process.wait(timeout=5)
            except:
                try:
                    process.kill()
                except:
                    pass
        print("👋 All servers stopped")

def main():
    """Main function to start development servers."""
    print("🚀 Starting Medicine Alternative System (Development Mode)")
    print("=" * 60)
    
    # Check if we're in the right directory
    if not os.path.exists("backend_api.py"):
        print("❌ Please run this script from the med_agent directory")
        sys.exit(1)
    
    # Check environment variables
    if not os.getenv("GOOGLE_API_KEY"):
        print("⚠️ Warning: GOOGLE_API_KEY environment variable not set")
        print("   Set it with: export GOOGLE_API_KEY='your_api_key'")
        print()
    
    # Check if database exists
    if not os.path.exists("medicines.db"):
        print("🗄️ Creating medicine database...")
        try:
            subprocess.run(["python3", "create_medicine_db.py"], check=True)
            print("✅ Database created successfully")
        except Exception as e:
            print(f"❌ Failed to create database: {e}")
            print("   Please run 'python3 create_medicine_db.py' manually")
            sys.exit(1)
    
    manager = ServerManager()
    
    try:
        # Start backend
        backend_process = manager.start_backend()
        if not backend_process:
            sys.exit(1)
        
        # Wait a moment for backend to start
        time.sleep(2)
        
        # Start frontend
        frontend_process = manager.start_frontend()
        
        print("\n🌟 Development servers are running!")
        print("📊 Frontend: http://localhost:8080")
        print("🔗 Backend API: http://localhost:8001")
        print("📚 API Docs: http://localhost:8001/docs")
        print("\n🛑 Press Ctrl+C to stop all servers")
        print("-" * 60)
        
        # Wait for processes
        try:
            if frontend_process:
                frontend_process.wait()
            elif backend_process:
                backend_process.wait()
        except KeyboardInterrupt:
            pass
            
    except KeyboardInterrupt:
        pass
    finally:
        manager.cleanup()

if __name__ == "__main__":
    main() 