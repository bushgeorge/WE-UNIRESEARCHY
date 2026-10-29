"""
CRUD (Create, Read, Update, Delete) operations for the research repository
"""

from sqlalchemy.orm import Session
from sqlalchemy import or_, and_, func
from typing import List, Optional, Dict, Any
import os

from models import (
    Publication, Researcher, University, AdminUser, 
    ResearchType, PublicationStatus
)
from schemas import (
    PublicationCreate, PublicationUpdate, ResearcherCreate,
    UniversityCreate, AdminUserCreate
)
from auth import hash_password

def create_university(db: Session, university: UniversityCreate) -> University:
    """Create a new university"""
    db_university = University(
        name=university.name,
        abbreviation=university.abbreviation,
        location=university.location,
        website=university.website
    )
    db.add(db_university)
    db.commit()
    db.refresh(db_university)
    return db_university

def get_universities(db: Session, skip: int = 0, limit: int = 100) -> List[University]:
    """Get all universities with pagination"""
    return db.query(University).offset(skip).limit(limit).all()

def get_university(db: Session, university_id: int) -> Optional[University]:
    """Get a university by ID"""
    return db.query(University).filter(University.id == university_id).first()

def create_researcher(db: Session, researcher: ResearcherCreate) -> Researcher:
    """Create a new researcher or return existing one by email"""
    # Check if researcher already exists by email
    db_researcher = db.query(Researcher).filter(
        Researcher.email == researcher.email
    ).first()
    
    if db_researcher:
        return db_researcher
    
    # Create new researcher
    db_researcher = Researcher(
        full_name=researcher.full_name,
        email=researcher.email,
        university_id=researcher.university_id,
        department=researcher.department,
        position=researcher.position,
        orcid_id=researcher.orcid_id,
        bio=researcher.bio
    )
    db.add(db_researcher)
    db.commit()
    db.refresh(db_researcher)
    return db_researcher

def get_researcher(db: Session, researcher_id: int) -> Optional[Researcher]:
    """Get a researcher by ID"""
    return db.query(Researcher).filter(Researcher.id == researcher_id).first()

def get_researchers(db: Session, skip: int = 0, limit: int = 100) -> List[Researcher]:
    """Get all researchers with pagination"""
    return db.query(Researcher).offset(skip).limit(limit).all()

def get_researcher_by_email(db: Session, email: str) -> Optional[Researcher]:
    """Get a researcher by email"""
    return db.query(Researcher).filter(Researcher.email == email).first()

def create_publication(db: Session, publication: PublicationCreate, filename: str = None, file_size: int = None) -> Publication:
    """Create a new publication with researchers"""
    # Create publication
    db_publication = Publication(
        title=publication.title,
        abstract=publication.abstract,
        keywords=publication.keywords,
        year=publication.year,
        research_type=publication.research_type,
        subject_area=publication.subject_area,
        university_id=publication.university_id,
        department=publication.department,
        supervisor=publication.supervisor,
        doi=publication.doi,
        filename=filename,
        file_size=file_size,
        status=PublicationStatus.PENDING
    )
    
    # Add researchers
    researchers = []
    for name, email in zip(publication.researcher_names, publication.researcher_emails):
        # Check if researcher exists
        researcher = get_researcher_by_email(db, email)
        if not researcher:
            # Create new researcher with minimal info
            researcher = Researcher(
                full_name=name,
                email=email,
                university_id=publication.university_id,
                department=publication.department
            )
            db.add(researcher)
            db.commit()
            db.refresh(researcher)
        researchers.append(researcher)
    
    db_publication.researchers = researchers
    db.add(db_publication)
    db.commit()
    db.refresh(db_publication)
    return db_publication

def get_publications(
    db: Session, 
    skip: int = 0, 
    limit: int = 100,
    status: Optional[str] = None
) -> List[Publication]:
    """Get all publications with optional status filter"""
    query = db.query(Publication)
    
    if status:
        query = query.filter(Publication.status == status)
    
    return query.order_by(Publication.created_at.desc()).offset(skip).limit(limit).all()

def get_publication(db: Session, publication_id: int) -> Optional[Publication]:
    """Get a publication by ID"""
    return db.query(Publication).filter(Publication.id == publication_id).first()

def update_publication_status(
    db: Session, 
    publication_id: int, 
    status: str,
    rejection_reason: str = None
) -> Optional[Publication]:
    """Update publication status"""
    publication = get_publication(db, publication_id)
    if not publication:
        return None
    
    publication.status = status
    if status == "rejected" and rejection_reason:
        publication.rejection_reason = rejection_reason
    
    db.commit()
    db.refresh(publication)
    return publication

def search_publications(
    db: Session,
    query: Optional[str] = None,
    university_id: Optional[int] = None,
    year: Optional[int] = None,
    research_type: Optional[str] = None,
    subject_area: Optional[str] = None,
    status: str = "approved",
    skip: int = 0,
    limit: int = 20
) -> List[Publication]:
    """Search publications with multiple filters"""
    search_query = db.query(Publication).filter(Publication.status == status)
    
    # Text search across title, abstract, keywords
    if query:
        search_terms = f"%{query}%"
        search_query = search_query.filter(
            or_(
                Publication.title.ilike(search_terms),
                Publication.abstract.ilike(search_terms),
                Publication.keywords.ilike(search_terms),
                Publication.supervisor.ilike(search_terms),
                Publication.department.ilike(search_terms)
            )
        )
    
    # Filter by university
    if university_id:
        search_query = search_query.filter(Publication.university_id == university_id)
    
    # Filter by year
    if year:
        search_query = search_query.filter(Publication.year == year)
    
    # Filter by research type
    if research_type:
        search_query = search_query.filter(Publication.research_type == research_type)
    
    # Filter by subject area
    if subject_area:
        search_query = search_query.filter(Publication.subject_area.ilike(f"%{subject_area}%"))
    
    return search_query.order_by(Publication.year.desc(), Publication.created_at.desc()).offset(skip).limit(limit).all()

def get_publication_stats(db: Session) -> Dict[str, Any]:
    """Get statistics for the home page"""
    # Total publications
    total_publications = db.query(func.count(Publication.id)).filter(
        Publication.status == "approved"
    ).scalar() or 0
    
    # Total researchers
    total_researchers = db.query(func.count(Researcher.id)).scalar() or 0
    
    # Publications by university
    publications_by_university = {}
    universities = db.query(University).all()
    for university in universities:
        count = db.query(func.count(Publication.id)).filter(
            Publication.university_id == university.id,
            Publication.status == "approved"
        ).scalar() or 0
        if count > 0:
            publications_by_university[university.name] = count
    
    # Publications by type
    publications_by_type = {}
    for research_type in ResearchType:
        count = db.query(func.count(Publication.id)).filter(
            Publication.research_type == research_type,
            Publication.status == "approved"
        ).scalar() or 0
        if count > 0:
            publications_by_type[research_type.value] = count
    
    # Publications by year (last 5 years)
    publications_by_year = {}
    from datetime import datetime
    current_year = datetime.now().year
    for year in range(current_year - 4, current_year + 1):
        count = db.query(func.count(Publication.id)).filter(
            Publication.year == year,
            Publication.status == "approved"
        ).scalar() or 0
        if count > 0:
            publications_by_year[str(year)] = count
    
    return {
        "total_publications": total_publications,
        "total_researchers": total_researchers,
        "publications_by_university": publications_by_university,
        "publications_by_type": publications_by_type,
        "publications_by_year": publications_by_year
    }

def create_admin_user(db: Session, admin: AdminUserCreate) -> AdminUser:
    """Create a new admin user"""
    db_admin = AdminUser(
        username=admin.username,
        password_hash=hash_password(admin.password),
        full_name=admin.full_name,
        is_active=True
    )
    db.add(db_admin)
    db.commit()
    db.refresh(db_admin)
    return db_admin

def get_admin_by_username(db: Session, username: str) -> Optional[AdminUser]:
    """Get admin user by username"""
    return db.query(AdminUser).filter(AdminUser.username == username).first()

def seed_initial_data(db: Session):
    """Seed database with initial sample data"""
    # Create Kenyan universities
    universities_data = [
        {"name": "University of Nairobi", "abbreviation": "UoN", "location": "Nairobi"},
        {"name": "Kenyatta University", "abbreviation": "KU", "location": "Nairobi"},
        {"name": "Moi University", "abbreviation": "MU", "location": "Eldoret"},
        {"name": "Jomo Kenyatta University of Agriculture and Technology", "abbreviation": "JKUAT", "location": "Juja"},
    ]
    
    universities = []
    for uni_data in universities_data:
        university = University(
            name=uni_data["name"],
            abbreviation=uni_data["abbreviation"],
            location=uni_data["location"]
        )
        db.add(university)
        universities.append(university)
    
    db.commit()
    
    # Refresh to get IDs
    for uni in universities:
        db.refresh(uni)
    
    # Create sample researchers
    researchers_data = [
        {
            "full_name": "Dr. Jane Wanjiku",
            "email": "jane.wanjiku@uon.ac.ke",
            "university_id": universities[0].id,
            "department": "Computer Science",
            "position": "Senior Lecturer",
            "orcid_id": "0000-0002-1825-0097"
        },
        {
            "full_name": "Dr. Michael Otieno",
            "email": "michael.otieno@ku.ac.ke",
            "university_id": universities[1].id,
            "department": "Environmental Science",
            "position": "Associate Professor"
        },
        {
            "full_name": "Sarah Akinyi",
            "email": "sarah.akinyi@students.mu.ac.ke",
            "university_id": universities[2].id,
            "department": "Public Health",
            "position": "MSc Student"
        },
        {
            "full_name": "Peter Kamau",
            "email": "peter.kamau@jkuat.ac.ke",
            "university_id": universities[3].id,
            "department": "Engineering",
            "position": "PhD Candidate"
        },
    ]
    
    researchers = []
    for res_data in researchers_data:
        researcher = Researcher(**res_data)
        db.add(researcher)
        researchers.append(researcher)
    
    db.commit()
    
    # Create sample publications
    publications_data = [
        {
            "title": "Machine Learning for Crop Disease Detection in Smallholder Farms",
            "abstract": "This research develops a machine learning model to detect crop diseases using smartphone images, specifically targeting smallholder farmers in Kenya.",
            "keywords": "machine learning, agriculture, crop disease, computer vision, Kenya",
            "year": 2023,
            "research_type": ResearchType.JOURNAL_ARTICLE,
            "subject_area": "Computer Science",
            "university_id": universities[0].id,
            "department": "Computer Science",
            "supervisor": "Prof. David Mwangi",
            "status": PublicationStatus.APPROVED,
            "filename": "sample1.pdf"
        },
        {
            "title": "Impact of Climate Change on Water Resources in Arid Regions of Kenya",
            "abstract": "A comprehensive study on the effects of climate change on water availability and quality in Kenya's arid and semi-arid lands.",
            "keywords": "climate change, water resources, arid lands, Kenya, sustainability",
            "year": 2022,
            "research_type": ResearchType.THESIS,
            "subject_area": "Environmental Science",
            "university_id": universities[1].id,
            "department": "Environmental Science",
            "supervisor": "Dr. Elizabeth Njoroge",
            "status": PublicationStatus.APPROVED,
            "filename": "sample2.pdf"
        },
        {
            "title": "Community-Based Approaches to Malaria Prevention in Rural Western Kenya",
            "abstract": "Evaluating the effectiveness of community-led interventions in reducing malaria incidence in rural communities.",
            "keywords": "malaria, public health, community health, Kenya, prevention",
            "year": 2024,
            "research_type": ResearchType.CONFERENCE_PAPER,
            "subject_area": "Public Health",
            "university_id": universities[2].id,
            "department": "Public Health",
            "status": PublicationStatus.APPROVED,
            "filename": "sample3.pdf"
        },
        {
            "title": "Renewable Energy Potential Assessment for Off-Grid Communities",
            "abstract": "Assessing solar and wind energy potential for electrifying off-grid communities in Northern Kenya.",
            "keywords": "renewable energy, solar, wind, off-grid, Kenya, sustainability",
            "year": 2023,
            "research_type": ResearchType.DATASET,
            "subject_area": "Engineering",
            "university_id": universities[3].id,
            "department": "Engineering",
            "supervisor": "Dr. Robert Kiptoo",
            "status": PublicationStatus.APPROVED,
            "filename": "sample4.pdf"
        },
        {
            "title": "Digital Financial Inclusion for Women Entrepreneurs in Nairobi",
            "abstract": "Exploring barriers and opportunities for women entrepreneurs in accessing digital financial services in urban Kenya.",
            "keywords": "financial inclusion, women entrepreneurs, digital finance, Kenya, gender",
            "year": 2024,
            "research_type": ResearchType.JOURNAL_ARTICLE,
            "subject_area": "Business",
            "university_id": universities[0].id,
            "department": "Business Administration",
            "status": PublicationStatus.PENDING,
            "filename": "sample5.pdf"
        },
    ]
    
    for pub_data in publications_data:
        publication = Publication(**pub_data)
        
        # Assign researchers (simplified - in real app would match properly)
        if pub_data["university_id"] == universities[0].id:
            publication.researchers = [researchers[0]]
        elif pub_data["university_id"] == universities[1].id:
            publication.researchers = [researchers[1]]
        elif pub_data["university_id"] == universities[2].id:
            publication.researchers = [researchers[2]]
        elif pub_data["university_id"] == universities[3].id:
            publication.researchers = [researchers[3]]
        
        db.add(publication)
    
    db.commit()
    
    # Create default admin user (password: admin123)
    admin_user = AdminUser(
        username="admin",
        password_hash="$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",  # bcrypt hash for "admin123"
        full_name="System Administrator",
        is_active=True
    )
    db.add(admin_user)
    db.commit()
    
    print("Initial data seeded successfully")