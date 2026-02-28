"""FastAPI backend for LinkedIn Job Scraper."""

from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from linkedin_scraper.scraper import LinkedInScraper, Job

app = FastAPI(
    title="LinkedIn Job Scraper API",
    description="Search LinkedIn jobs programmatically",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class JobResponse(BaseModel):
    """Job listing response model."""
    position: str
    company: str
    company_logo: Optional[str] = None
    location: str
    date: str
    ago_time: str
    salary: str
    job_url: str
    description: Optional[str] = None
    skills: Optional[list[str]] = None
    apply_method: Optional[str] = None
    applicant_count: Optional[str] = None


class SearchResponse(BaseModel):
    """Search results response model."""
    jobs: list[JobResponse]
    count: int
    keyword: str
    location: str


@app.get("/")
async def root():
    """API health check."""
    return {"status": "ok", "message": "LinkedIn Job Scraper API"}


@app.get("/api/search", response_model=SearchResponse)
async def search_jobs(
    keyword: str = Query(..., description="Job title or keywords to search"),
    location: str = Query("", description="City or region"),
    job_type: Optional[str] = Query(None, description="full-time, part-time, contract, etc."),
    remote: Optional[str] = Query(None, description="on-site, remote, hybrid"),
    experience: Optional[str] = Query(None, description="entry-level, senior, etc."),
    date_posted: Optional[str] = Query(None, description="24hr, past-week, past-month"),
    salary: Optional[str] = Query(None, description="Minimum salary: 40000, 60000, etc."),
    sort_by: str = Query("relevant", description="recent or relevant"),
    easy_apply: bool = Query(False, description="Filter to Easy Apply only"),
    under_10_applicants: bool = Query(False, description="Filter to jobs with <10 applicants"),
    limit: int = Query(25, ge=1, le=100, description="Max results (1-100)"),
    details: bool = Query(False, description="Fetch full job descriptions"),
):
    """Search for jobs on LinkedIn."""
    scraper = LinkedInScraper()

    date_posted_val = date_posted.replace("-", " ") if date_posted else ""
    job_type_val = job_type.replace("-", " ") if job_type else ""
    remote_val = remote.replace("-", " ") if remote else ""
    experience_val = experience.replace("-", " ") if experience else ""

    jobs = scraper.search(
        keyword=keyword,
        location=location,
        date_posted=date_posted_val,
        job_type=job_type_val,
        remote=remote_val,
        experience=experience_val,
        salary=salary or "",
        sort_by=sort_by,
        easy_apply=easy_apply,
        under_10_applicants=under_10_applicants,
        limit=limit,
    )

    if details:
        for job in jobs:
            scraper.fetch_job_details(job)

    job_responses = [
        JobResponse(
            position=job.position,
            company=job.company,
            company_logo=job.company_logo,
            location=job.location,
            date=job.date,
            ago_time=job.ago_time,
            salary=job.salary,
            job_url=job.job_url,
            description=job.description,
            skills=job.skills,
            apply_method=job.apply_method,
            applicant_count=job.applicant_count,
        )
        for job in jobs
    ]

    return SearchResponse(
        jobs=job_responses,
        count=len(job_responses),
        keyword=keyword,
        location=location,
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
