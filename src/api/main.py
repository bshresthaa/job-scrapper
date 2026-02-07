# src/api/main.py
from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from src.models.database import db

app = FastAPI(
    title="Job Scraper API",
    description="API for querying scraped job listings",
    version="1.0.0"
)

# Pydantic models
class Job(BaseModel):
    id: int
    title: str
    company: str
    location: Optional[str] = None
    job_type: Optional[str] = None
    salary_min: Optional[float] = None
    salary_max: Optional[float] = None
    url: str
    posted_date: Optional[str] = None

class Application(BaseModel):
    id: int
    job_id: int
    status: str
    applied_at: str
    notes: Optional[str] = None
    title: str
    company: str
    url: str

# Endpoints
@app.get("/")
def root():
    """Health check"""
    return {
        "status": "healthy",
        "version": "1.0.0",
        "endpoints": ["/jobs", "/jobs/{id}", "/applications"]
    }

@app.get("/jobs", response_model=List[Job])
def list_jobs(
    keyword: Optional[str] = None,
    location: Optional[str] = None,
    limit: int = Query(default=50, le=100)
):
    """List jobs with optional filters"""
    jobs = db.query_jobs(keyword=keyword, location=location, limit=limit)
    return jobs

@app.get("/jobs/{job_id}", response_model=Job)
def get_job(job_id: int):
    """Get specific job by ID"""
    job = db.get_job(job_id)
    
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    return job

@app.post("/applications", status_code=201)
def create_application(job_id: int, notes: Optional[str] = None):
    """Track job application"""
    # Verify job exists
    job = db.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    app_id = db.track_application(job_id, notes)
    return {"id": app_id, "job_id": job_id, "status": "applied"}

@app.get("/applications", response_model=List[Application])
def list_applications(status: Optional[str] = None):
    """List job applications"""
    apps = db.get_applications(status=status)
    return apps

@app.get("/stats")
def get_stats():
    """Get scraper statistics"""
    total_jobs = len(db.query_jobs(limit=100000))
    total_apps = len(db.get_applications())
    
    return {
        "total_jobs": total_jobs,
        "total_applications": total_apps,
        "application_rate": f"{(total_apps/total_jobs*100):.1f}%" if total_jobs > 0 else "0%"
    }