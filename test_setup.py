#!/usr/bin/env python3
"""
Test script to verify WE UNIRESEARCHITY setup
"""

import os
import sys
import importlib

def test_imports():
    """Test if all required modules can be imported"""
    modules = [
        "fastapi",
        "uvicorn",
        "sqlalchemy",
        "pydantic",
        "passlib"
    ]
    
    print("Testing imports...")
    for module in modules:
        try:
            importlib.import_module(module)
            print(f"✓ {module}")
        except ImportError:
            print(f"✗ {module} - not installed")
            return False
    return True

def test_files():
    """Test if all required files exist"""
    required_files = [
        "main.py",
        "requirements.txt",
        "database.py",
        "models.py",
        "schemas.py",
        "crud.py",
        "auth.py",
        "config.py",
        "templates/base.html",
        "static/style.css",
        "uploads/.gitkeep",
        "database/",
    ]
    
    print("\nChecking files...")
    all_exist = True
    for file in required_files:
        if os.path.exists(file):
            print(f"✓ {file}")
        else:
            print(f"✗ {file} - missing")
            all_exist = False
    
    return all_exist

def test_database():
    """Test database initialization"""
    print("\nTesting database...")
    try:
        from database import init_db, SessionLocal
        from models import Base
        
        # Check if we can create engine
        from sqlalchemy import create_engine
        engine = create_engine("sqlite:///./database/test.db")
        
        # Create test table
        Base.metadata.create_all(bind=engine)
        
        # Test session
        from sqlalchemy.orm import sessionmaker
        TestSession = sessionmaker(bind=engine)
        session = TestSession()
        session.close()
        
        # Clean up
        os.remove("./database/test.db")
        
        print("✓ Database connection test passed")
        return True
    except Exception as e:
        print(f"✗ Database test failed: {e}")
        return False

def test_app_structure():
    """Test application structure"""
    print("\nTesting application structure...")
    try:
        # Try to import main app components
        from main import app
        from database import get_db
        from models import Publication, Researcher, University
        
        print("✓ Application structure test passed")
        return True
    except Exception as e:
        print(f"✗ Application structure test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("WE UNIRESEARCHITY Setup Test")
    print("=" * 50)
    
    tests = [
        ("File structure", test_files),
        ("Import dependencies", test_imports),
        ("Database", test_database),
        ("Application structure", test_app_structure),
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n{test_name}:")
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"✗ Test error: {e}")
            results.append((test_name, False))
    
    print("\n" + "=" * 50)
    print("Test Results:")
    print("=" * 50)
    
    all_passed = True
    for test_name, result in results:
        status = "PASS" if result else "FAIL"
        print(f"{test_name:30} {status}")
        if not result:
            all_passed = False
    
    print("\n" + "=" * 50)
    if all_passed:
        print("✓ All tests passed! The application is ready to run.")
        print("\nTo start the application:")
        print("  python start.py")
        print("  or")
        print("  python main.py")
    else:
        print("✗ Some tests failed. Please check the errors above.")
        print("\nTry running: pip install -r requirements.txt")
    
    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main())