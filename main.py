"""
WE UNIRESEARCHITY - Research Repository for Kenyan Universities
Main FastAPI application entry point
"""

import os
from fastapi import FastAPI, Request, Depends, HTTPException, status
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List, Optional

# Import database and models
from database import engine, Base, get_db
from models import Researcher, Publication, University
from schemas import PublicationCreate, PublicationUpdate, ResearcherCreate
from crud import (
    create_publication, get_publications, get_publication, update_publication_status,
    create_researcher, get_researcher, get_researchers, get_universities,
    get_publication_stats, search_publications
)
from auth import get_current_admin, create_admin_user, verify_password
from config import settings

# Create database tables
Base.metadata.create_all(bind=engine)

# Create FastAPI app
app = FastAPI(
    title="WE UNIRESEARCHITY",
    description="Research Repository for Kenyan Universities",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Setup templates
templates = Jinja2Templates(directory="templates")

# Create uploads directory if it doesn't exist
os.makedirs("uploads", exist_ok=True)

@app.get("/", response_class=HTMLResponse)
async def home(request: Request, db: Session = Depends(get_db)):
    """Home page with stats and search"""
    stats = get_publication_stats(db)
    universities = get_universities(db)
    recent_publications = get_publications(db, skip=0, limit=10, status="approved")
    
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "stats": stats,
            "universities": universities,
            "recent_publications": recent_publications
        }
    )

@app.get("/search", response_class=HTMLResponse)
async def search_page(
    request: Request,
    q: Optional[str] = None,
    university_id: Optional[int] = None,
    year: Optional[int] = None,
    research_type: Optional[str] = None,
    subject_area: Optional[str] = None,
    page: int = 1,
    db: Session = Depends(get_db)
):
    """Search results page"""
    limit = 20
    skip = (page - 1) * limit
    
    publications = search_publications(
        db,
        query=q,
        university_id=university_id,
        year=year,
        research_type=research_type,
        subject_area=subject_area,
        status="approved",
        skip=skip,
        limit=limit
    )
    
    total_count = len(publications)  # Simplified - in real app would get total count
    total_pages = (total_count + limit - 1) // limit
    
    universities = get_universities(db)
    
    return templates.TemplateResponse(
        "search.html",
        {
            "request": request,
            "publications": publications,
            "query": q,
            "universities": universities,
            "selected_university": university_id,
            "selected_year": year,
            "selected_type": research_type,
            "selected_subject": subject_area,
            "page": page,
            "total_pages": total_pages,
            "total_count": total_count
        }
    )

@app.get("/publication/{publication_id}", response_class=HTMLResponse)
async def publication_detail(request: Request, publication_id: int, db: Session = Depends(get_db)):
    """Publication detail page"""
    publication = get_publication(db, publication_id)
    if not publication or publication.status != "approved":
        raise HTTPException(status_code=404, detail="Publication not found")
    
    # Generate APA citation
    apa_citation = generate_apa_citation(publication)
    
    return templates.TemplateResponse(
        "publication.html",
        {
            "request": request,
            "publication": publication,
            "apa_citation": apa_citation
        }
    )

@app.get("/researcher/{researcher_id}", response_class=HTMLResponse)
async def researcher_detail(request: Request, researcher_id: int, db: Session = Depends(get_db)):
    """Researcher profile page"""
    researcher = get_researcher(db, researcher_id)
    if not researcher:
        raise HTTPException(status_code=404, detail="Researcher not found")
    
    # Get researcher's publications
    publications = [pub for pub in researcher.publications if pub.status == "approved"]
    
    return templates.TemplateResponse(
        "researcher.html",
        {
            "request": request,
            "researcher": researcher,
            "publications": publications
        }
    )

@app.get("/submit", response_class=HTMLResponse)
async def submit_page(request: Request, db: Session = Depends(get_db)):
    """Submit research form page"""
    universities = get_universities(db)
    return templates.TemplateResponse(
        "submit.html",
        {
            "request": request,
            "universities": universities
        }
    )

@app.get("/admin", response_class=HTMLResponse)
async def admin_login_page(request: Request):
    """Admin login page"""
    return templates.TemplateResponse("admin_login.html", {"request": request})

@app.get("/admin/dashboard", response_class=HTMLResponse)
async def admin_dashboard(request: Request, db: Session = Depends(get_db), admin: bool = Depends(get_current_admin)):
    """Admin dashboard for managing submissions"""
    pending_publications = get_publications(db, status="pending")
    return templates.TemplateResponse(
        "admin_dashboard.html",
        {
            "request": request,
            "pending_publications": pending_publications
        }
    )

def generate_apa_citation(publication):
    """Generate APA citation for a publication"""
    authors = ", ".join([researcher.full_name for researcher in publication.researchers])
    year = publication.year
    title = publication.title
    
    if publication.research_type == "thesis":
        return f"{authors} ({year}). {title} [Master's thesis, {publication.university.name}]. WE UNIRESEARCHITY."
    elif publication.research_type == "journal_article":
        return f"{authors} ({year}). {title}. Journal Name, Volume(Issue), pages. https://doi.org/xxxx"
    else:
        return f"{authors} ({year}). {title}. WE UNIRESEARCHITY. Retrieved from https://uniresearchity.example.com/publication/{publication.id}"

# API endpoints for form submissions
@app.post("/api/submit")
async def submit_research(publication_data: PublicationCreate, db: Session = Depends(get_db)):
    """API endpoint to submit new research"""
    try:
        publication = create_publication(db, publication_data)
        return {
            "success": True,
            "message": "Research submitted successfully. It will be reviewed by an admin.",
            "publication_id": publication.id
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/api/admin/login")
async def admin_login(username: str, password: str, db: Session = Depends(get_db)):
    """API endpoint for admin login"""
    # In a real app, this would use JWT tokens
    if username == settings.ADMIN_USERNAME and verify_password(password, settings.ADMIN_PASSWORD_HASH):
        return {"success": True, "message": "Login successful"}
    else:
        raise HTTPException(status_code=401, detail="Invalid credentials")

@app.post("/api/admin/approve/{publication_id}")
async def approve_publication(
    publication_id: int,
    db: Session = Depends(get_db),
    admin: bool = Depends(get_current_admin)
):
    """API endpoint to approve a publication"""
    publication = update_publication_status(db, publication_id, "approved")
    return {
        "success": True,
        "message": "Publication approved successfully",
        "publication_id": publication.id
    }

@app.post("/api/admin/reject/{publication_id}")
async def reject_publication(
    publication_id: int,
    reason: str,
    db: Session = Depends(get_db),
    admin: bool = Depends(get_current_admin)
):
    """API endpoint to reject a publication"""
    publication = update_publication_status(db, publication_id, "rejected")
    return {
        "success": True,
        "message": f"Publication rejected. Reason: {reason}",
        "publication_id": publication.id
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    )