from fastapi import FastAPI, BackgroundTasks, HTTPException
from typing import List, Optional
from pydantic import BaseModel
from sqlalchemy.orm import Session

from scraper.detail_scraper import scrape_projects  # your existing scraper, updated to accept pages param
from db.database import SessionLocal
from db.models import Project as ProjectModel


app = FastAPI()


# Pydantic model for serialization
class Project(BaseModel):
    project_name: str
    rera_no: str
    promoter_address: Optional[str] = None
    promoter_name: Optional[str] = None
    promoter_company_name: Optional[str] = None
    promoter_registration_no: Optional[str] = None
    promoter_correspondence_office_address: Optional[str] = None
    promoter_registered_office_address: Optional[str] = None
    promoter_entity: Optional[str] = None
    promoter_email: Optional[str] = None
    promoter_mobile: Optional[str] = None
    promoter_telephone: Optional[str] = None
    promoter_gst_no: Optional[str] = None


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.post("/scrape-projects/")
async def scrape_projects_endpoint(background_tasks: BackgroundTasks, pages: int = 5):
    """
    Trigger scraping of `pages` number of pages, runs in background.
    """
    background_tasks.add_task(scrape_projects, pages)
    return {"message": f"Started scraping {pages} pages of projects."}


@app.get("/projects/", response_model=List[Project])
def get_all_projects():
    """
    Fetch all projects stored in DB.
    """
    db = SessionLocal()
    projects = db.query(ProjectModel).all()
    db.close()
    return projects
