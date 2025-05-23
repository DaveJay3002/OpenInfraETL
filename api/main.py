from fastapi import FastAPI, BackgroundTasks, HTTPException
from typing import List
from pydantic import BaseModel
from sqlalchemy.orm import Session

from scraper.detail_scraper import scrape_projects  # your existing scraper, updated to accept pages param
from db.database import SessionLocal
from db.models import Project as ProjectModel


app = FastAPI()


# Pydantic model for serialization
class Project(BaseModel):
    id: int
    project_name: str
    rera_no: str
    promoter_name: str
    promoter_address: str

    model_config = {
        "from_attributes": True,
    }


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
