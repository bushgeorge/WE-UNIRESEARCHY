"""
Pydantic schemas for data validation and serialization
"""

from pydantic import BaseModel, EmailStr, validator, field_validator
from typing import List, Optional
from datetime import datetime
from enum import Enum

# Enums for validation
class ResearchTypeEnum(str, Enum):
    thesis = "thesis"
    journal_article = "journal_article"
    conference_paper = "conference_paper"
    dataset = "dataset"
    other = "other"

class PublicationStatusEnum(str, Enum):
    pending = "pending"
    approved = "approved"
    rejected = "rejected"

# Base schemas
class UniversityBase(BaseModel):
    name: str
    abbreviation: Optional[str] = None
    location: Optional[str] = None
    website: Optional[str] = None

class UniversityCreate(UniversityBase):
    pass

class University(UniversityBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

class ResearcherBase(BaseModel):
    full_name: str
    email: EmailStr
    university_id: int
    department: Optional[str] = None
    position: Optional[str] = None
    orcid_id: Optional[str] = None
    bio: Optional[str] = None

class ResearcherCreate(ResearcherBase):
    @field_validator('orcid_id')
    def validate_orcid(cls, v):
        if v and not v.startswith('0000-000'):
            raise ValueError('Invalid ORCID format. Should be like 0000-0000-0000-0000')
        return v

class Researcher(ResearcherBase):
    id: int
    created_at: datetime
    university: Optional[University] = None
    
    class Config:
        from_attributes = True

class PublicationBase(BaseModel):
    title: str
    abstract: str
    keywords: str  # Comma-separated
    year: int
    research_type: ResearchTypeEnum
    subject_area: str
    university_id: int
    department: Optional[str] = None
    supervisor: Optional[str] = None
    doi: Optional[str] = None
    
    @field_validator('year')
    def validate_year(cls, v):
        if v < 1900 or v > 2100:
            raise ValueError('Year must be between 1900 and 2100')
        return v
    
    @field_validator('keywords')
    def validate_keywords(cls, v):
        # Limit to 10 keywords
        keywords = [k.strip() for k in v.split(',') if k.strip()]
        if len(keywords) > 10:
            raise ValueError('Maximum 10 keywords allowed')
        return v

class PublicationCreate(PublicationBase):
    researcher_names: List[str]  # List of researcher full names
    researcher_emails: List[EmailStr]  # List of researcher emails
    
    @field_validator('researcher_names')
    def validate_researchers(cls, v):
        if not v:
            raise ValueError('At least one researcher is required')
        if len(v) > 10:
            raise ValueError('Maximum 10 researchers allowed')
        return v
    
    @field_validator('researcher_emails')
    def validate_emails_match_names(cls, v, info):
        names = info.data.get('researcher_names', [])
        if len(v) != len(names):
            raise ValueError('Number of emails must match number of researchers')
        return v

class PublicationUpdate(BaseModel):
    status: Optional[PublicationStatusEnum] = None
    rejection_reason: Optional[str] = None

class Publication(PublicationBase):
    id: int
    status: PublicationStatusEnum
    filename: Optional[str] = None
    file_size: Optional[int] = None
    rejection_reason: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    university: Optional[University] = None
    researchers: List[Researcher] = []
    
    class Config:
        from_attributes = True

class PublicationSearch(BaseModel):
    query: Optional[str] = None
    university_id: Optional[int] = None
    year: Optional[int] = None
    research_type: Optional[ResearchTypeEnum] = None
    subject_area: Optional[str] = None
    page: int = 1
    limit: int = 20

class AdminUserBase(BaseModel):
    username: str
    full_name: Optional[str] = None

class AdminUserCreate(AdminUserBase):
    password: str
    
    @field_validator('password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        return v

class AdminUser(AdminUserBase):
    id: int
    is_active: bool
    created_at: datetime
    last_login: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class StatsResponse(BaseModel):
    total_publications: int
    total_researchers: int
    publications_by_university: dict
    publications_by_type: dict
    publications_by_year: dict

class SearchResponse(BaseModel):
    publications: List[Publication]
    total_count: int
    page: int
    total_pages: int
    query: Optional[str] = None