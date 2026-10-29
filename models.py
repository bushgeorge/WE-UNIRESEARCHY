"""
SQLAlchemy models for the research repository
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Table, Enum, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from database import Base

# Association table for many-to-many relationship between researchers and publications
publication_researchers = Table(
    'publication_researchers',
    Base.metadata,
    Column('publication_id', Integer, ForeignKey('publications.id'), primary_key=True),
    Column('researcher_id', Integer, ForeignKey('researchers.id'), primary_key=True)
)

class ResearchType(str, enum.Enum):
    """Enum for research types"""
    THESIS = "thesis"
    JOURNAL_ARTICLE = "journal_article"
    CONFERENCE_PAPER = "conference_paper"
    DATASET = "dataset"
    OTHER = "other"

class PublicationStatus(str, enum.Enum):
    """Enum for publication status"""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"

class University(Base):
    """University model"""
    __tablename__ = "universities"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False, unique=True, index=True)
    abbreviation = Column(String(20))
    location = Column(String(100))
    website = Column(String(200))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    publications = relationship("Publication", back_populates="university")
    researchers = relationship("Researcher", back_populates="university")

class Researcher(Base):
    """Researcher/Author model"""
    __tablename__ = "researchers"
    
    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String(200), nullable=False, index=True)
    email = Column(String(100), unique=True, index=True)
    university_id = Column(Integer, ForeignKey("universities.id"))
    department = Column(String(100))
    position = Column(String(100))  # e.g., Student, Lecturer, Professor
    orcid_id = Column(String(50), unique=True)  # Optional ORCID identifier
    bio = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    university = relationship("University", back_populates="researchers")
    publications = relationship(
        "Publication",
        secondary=publication_researchers,
        back_populates="researchers"
    )

class Publication(Base):
    """Research publication model"""
    __tablename__ = "publications"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(300), nullable=False, index=True)
    abstract = Column(Text, nullable=False)
    keywords = Column(String(500))  # Comma-separated keywords
    year = Column(Integer, nullable=False, index=True)
    research_type = Column(Enum(ResearchType), nullable=False, index=True)
    subject_area = Column(String(100), index=True)
    university_id = Column(Integer, ForeignKey("universities.id"), nullable=False)
    department = Column(String(100))
    supervisor = Column(String(200))  # For theses
    doi = Column(String(100))  # Digital Object Identifier
    filename = Column(String(255))  # Uploaded PDF filename
    file_size = Column(Integer)  # File size in bytes
    status = Column(Enum(PublicationStatus), default=PublicationStatus.PENDING, index=True)
    rejection_reason = Column(Text)  # If rejected, store reason
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    university = relationship("University", back_populates="publications")
    researchers = relationship(
        "Researcher",
        secondary=publication_researchers,
        back_populates="publications"
    )

class AdminUser(Base):
    """Admin user model for authentication"""
    __tablename__ = "admin_users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(100))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    last_login = Column(DateTime(timezone=True))