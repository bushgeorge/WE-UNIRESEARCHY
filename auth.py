"""
Authentication and authorization utilities
"""

from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from sqlalchemy.orm import Session
import os

from database import get_db
from crud import get_admin_by_username
from config import settings

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Basic authentication for admin routes
security = HTTPBasic()

def hash_password(password: str) -> str:
    """Hash a password using bcrypt"""
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    return pwd_context.verify(plain_password, hashed_password)

def authenticate_admin(username: str, password: str, db: Session) -> bool:
    """Authenticate admin user"""
    admin = get_admin_by_username(db, username)
    if not admin:
        return False
    if not admin.is_active:
        return False
    if not verify_password(password, admin.password_hash):
        return False
    return True

def get_current_admin(
    credentials: HTTPBasicCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """Dependency to get current authenticated admin"""
    # For simplicity, we're using basic auth
    # In a production app, use JWT tokens
    
    # Check if credentials match configured admin
    if (credentials.username == settings.ADMIN_USERNAME and 
        verify_password(credentials.password, settings.ADMIN_PASSWORD_HASH)):
        return True
    
    # Also check database
    if authenticate_admin(credentials.username, credentials.password, db):
        return True
    
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid authentication credentials",
        headers={"WWW-Authenticate": "Basic"},
    )

def create_admin_user(username: str, password: str, full_name: str = None, db: Session = None):
    """Create a new admin user"""
    from crud import create_admin_user as crud_create_admin
    from schemas import AdminUserCreate
    
    admin_data = AdminUserCreate(
        username=username,
        password=password,
        full_name=full_name or username
    )
    
    if db:
        return crud_create_admin(db, admin_data)
    
    # If no db session provided, create one
    from database import SessionLocal
    db = SessionLocal()
    try:
        admin = crud_create_admin(db, admin_data)
        db.commit()
        return admin
    finally:
        db.close()

def init_admin():
    """Initialize admin user if not exists"""
    from database import SessionLocal
    from crud import get_admin_by_username
    
    db = SessionLocal()
    try:
        # Check if admin exists
        admin = get_admin_by_username(db, "admin")
        if not admin:
            # Create default admin (password: admin123)
            create_admin_user("admin", "admin123", "System Administrator", db)
            print("Default admin user created: username=admin, password=admin123")
        else:
            print("Admin user already exists")
    finally:
        db.close()