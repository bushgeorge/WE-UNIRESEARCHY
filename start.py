#!/usr/bin/env python3
"""
Startup script for WE UNIRESEARCHITY
"""

import os
import sys
import subprocess
import webbrowser
import time

def check_dependencies():
    """Check if required dependencies are installed"""
    try:
        import fastapi
        import uvicorn
        import sqlalchemy
        print("✓ Dependencies found")
        return True
    except ImportError as e:
        print(f"✗ Missing dependency: {e}")
        print("Installing dependencies...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
            print("✓ Dependencies installed successfully")
            return True
        except subprocess.CalledProcessError:
            print("✗ Failed to install dependencies")
            return False

def initialize_database():
    """Initialize database and seed sample data"""
    try:
        from database import init_db
        from crud import seed_initial_data
        from database import SessionLocal
        
        print("Initializing database...")
        init_db()
        
        # Seed initial data
        db = SessionLocal()
        try:
            seed_initial_data(db)
            print("✓ Database initialized with sample data")
        except Exception as e:
            print(f"Note: {e}")
            print("Database already contains data")
        finally:
            db.close()
            
        return True
    except Exception as e:
        print(f"✗ Database initialization failed: {e}")
        return False

def start_server():
    """Start the FastAPI development server"""
    print("Starting WE UNIRESEARCHITY server...")
    print("=" * 50)
    print("Application: WE UNIRESEARCHITY")
    print("URL: http://localhost:8000")
    print("Admin: http://localhost:8000/admin")
    print("Admin credentials: admin / admin123")
    print("=" * 50)
    print("\nPress Ctrl+C to stop the server\n")
    
    # Open browser after a short delay
    def open_browser():
        time.sleep(2)
        webbrowser.open("http://localhost:8000")
    
    import threading
    threading.Thread(target=open_browser, daemon=True).start()
    
    # Start the server
    try:
        import uvicorn
        uvicorn.run(
            "main:app",
            host="0.0.0.0",
            port=8000,
            reload=True,
            log_level="info"
        )
    except KeyboardInterrupt:
        print("\nServer stopped by user")
    except Exception as e:
        print(f"✗ Server error: {e}")

def main():
    """Main entry point"""
    print("WE UNIRESEARCHITY - Research Repository for Kenyan Universities")
    print("=" * 60)
    
    # Check if we're in the right directory
    if not os.path.exists("requirements.txt"):
        print("Error: Please run this script from the project root directory")
        return 1
    
    # Check dependencies
    if not check_dependencies():
        return 1
    
    # Initialize database
    if not initialize_database():
        return 1
    
    # Start server
    start_server()
    return 0

if __name__ == "__main__":
    sys.exit(main())