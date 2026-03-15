"""FastAPI backend for LinkedIn Job Scraper with AI Agent features."""

from fastapi import FastAPI, Query, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, FileResponse
from pydantic import BaseModel, Field
from typing import Optional, List
import sys
import os
import json
import tempfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from linkedin_scraper.scraper import LinkedInScraper, Job
from linkedin_scraper.indeed_scraper import IndeedScraper
from linkedin_scraper.greenhouse_scraper import GreenhouseScraper, GREENHOUSE_COMPANIES
from linkedin_scraper.multi_scraper import MultiSourceScraper
from linkedin_scraper.agent.profile import UserProfile, parse_resume_text, parse_pdf_resume
from linkedin_scraper.agent.ranker import JobRanker, RankedJob
from linkedin_scraper.agent.resume_tailor import ResumeTailor
from linkedin_scraper.agent.cover_letter import CoverLetterGenerator
from linkedin_scraper.agent.agent import JobSearchAgent
from linkedin_scraper.agent.evaluation import AgentEvaluator
from linkedin_scraper.agent.llm_tool_agent import run_llm_tool_agent
from assignment_agent import get_two_modified_bullets

app = FastAPI(
    title="LinkedIn Job Search Agent API",
    description="AI-powered job search, ranking, and application generation",
    version="2.0.0",
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


class RankedJobResponse(BaseModel):
    """Ranked job response with match details."""
    job: JobResponse
    score: float
    skill_match: float
    title_match: float
    location_match: float
    experience_match: float
    matched_skills: list[str]
    missing_skills: list[str]
    match_reasons: list[str]


class JobResponseWithSource(JobResponse):
    """Job listing response with source information."""
    source: Optional[str] = "linkedin"


class SearchResponse(BaseModel):
    """Search results response model."""
    jobs: list[JobResponse]
    count: int
    keyword: str
    location: str


class MultiSourceSearchResponse(BaseModel):
    """Multi-source search results response model."""
    jobs: list[JobResponseWithSource]
    count: int
    keyword: str
    location: str
    sources: list[str]
    jobs_by_source: dict[str, int]


class RankedSearchResponse(BaseModel):
    """Ranked search results response."""
    jobs: list[RankedJobResponse]
    count: int
    keyword: str
    location: str
    profile_name: str
    reasoning: Optional[str] = None


class ProfileModel(BaseModel):
    """User profile model for API."""
    name: str = ""
    email: str = ""
    phone: str = ""
    location: str = ""
    linkedin_url: str = ""
    github_url: str = ""
    portfolio_url: str = ""
    title: str = ""
    summary: str = ""
    years_experience: int = 0
    skills: list[str] = []
    programming_languages: list[str] = []
    frameworks: list[str] = []
    tools: list[str] = []
    experience: list[dict] = []
    education: list[dict] = []
    certifications: list[str] = []
    projects: list[dict] = []
    target_roles: list[str] = []
    target_companies: list[str] = []
    preferred_locations: list[str] = []
    remote_preference: str = "flexible"
    min_salary: int = 0


class TailoredResumeResponse(BaseModel):
    """Tailored resume response (assignment-style: summary + exactly 2 modified bullets + aligned skills app-wide)."""
    summary: str
    highlighted_skills: list[str]
    keywords_added: list[str]
    resume_text: str
    resume_html: str
    ats_score: float
    suggestions: list[str]
    modified_bullets: Optional[List[str]] = None  # Exactly 2 experience bullets modified for the job (app-wide)


class CoverLetterResponse(BaseModel):
    """Cover letter response."""
    content: str
    html_content: str
    word_count: int
    key_points: list[str]
    personalization_score: float


class ApplicationResponse(BaseModel):
    """Complete application response."""
    job: JobResponse
    match_score: float
    matched_skills: list[str]
    missing_skills: list[str]
    resume: TailoredResumeResponse
    cover_letter: CoverLetterResponse


class EvaluationResponse(BaseModel):
    """Evaluation metrics response."""
    total_applications: int
    avg_match_score: float
    avg_ats_score: float
    avg_personalization_score: float
    interview_rate: float
    maybe_rate: float
    rejection_rate: float
    skill_coverage: float
    recruiter_feedback: list[dict]


class JobTextModel(BaseModel):
    """Minimal job information when user pastes description manually."""
    position: str
    company: str
    description: str
    location: str = ""
    salary: str = ""
    job_url: str = ""


class CsvJobModel(BaseModel):
    """Job row from the offline CSV dataset."""
    title: str
    company: str
    location: str
    required_skills: str
    years_experience: str
    description: str
    url: str


class OfflineAgentResponse(BaseModel):
    """Response model for offline CSV-based agent."""
    reasoning: Optional[str] = None
    ranked_jobs: list[RankedJobResponse]
    chosen_index: int
    tailored_resume: TailoredResumeResponse


profile_store: dict[str, UserProfile] = {}


def job_to_response(job: Job) -> JobResponse:
    """Convert Job to JobResponse."""
    return JobResponse(
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


def ranked_job_to_response(ranked: RankedJob) -> RankedJobResponse:
    """Convert RankedJob to RankedJobResponse."""
    return RankedJobResponse(
        job=job_to_response(ranked.job),
        score=ranked.score,
        skill_match=ranked.skill_match,
        title_match=ranked.title_match,
        location_match=ranked.location_match,
        experience_match=ranked.experience_match,
        matched_skills=ranked.matched_skills,
        missing_skills=ranked.missing_skills,
        match_reasons=ranked.match_reasons,
    )


@app.get("/")
async def root():
    """API health check."""
    return {
        "status": "ok",
        "message": "LinkedIn Job Search Agent API",
        "version": "2.0.0",
        "features": [
            "Job Search",
            "AI Ranking",
            "Resume Tailoring",
            "Cover Letter Generation",
            "Hiring Simulation",
        ]
    }


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
    """Search for jobs on LinkedIn with optional filtering."""
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

    return SearchResponse(
        jobs=[job_to_response(job) for job in jobs],
        count=len(jobs),
        keyword=keyword,
        location=location,
    )


@app.get("/api/search/multi", response_model=MultiSourceSearchResponse)
async def search_jobs_multi_source(
    keyword: str = Query(..., description="Job title or keywords to search"),
    location: str = Query("", description="City or region"),
    sources: str = Query("linkedin,indeed,greenhouse", description="Comma-separated sources: linkedin, indeed, greenhouse"),
    job_type: Optional[str] = Query(None, description="full-time, part-time, contract, etc."),
    remote: Optional[str] = Query(None, description="on-site, remote, hybrid"),
    experience: Optional[str] = Query(None, description="entry-level, senior, etc."),
    date_posted: Optional[str] = Query(None, description="24hr, past-week, past-month"),
    salary: Optional[str] = Query(None, description="Minimum salary"),
    sort_by: str = Query("relevant", description="recent or relevant"),
    easy_apply: bool = Query(False, description="Filter to Easy Apply only (LinkedIn)"),
    limit: int = Query(25, ge=1, le=100, description="Max results per source (1-100)"),
    details: bool = Query(False, description="Fetch full job descriptions"),
):
    """Search for jobs across multiple sources (LinkedIn, Indeed, Greenhouse)."""
    source_list = [s.strip().lower() for s in sources.split(",") if s.strip()]
    valid_sources = [s for s in source_list if s in ["linkedin", "indeed", "greenhouse"]]
    
    if not valid_sources:
        valid_sources = ["linkedin", "indeed", "greenhouse"]

    scraper = MultiSourceScraper(sources=valid_sources)

    date_posted_val = date_posted.replace("-", " ") if date_posted else ""
    job_type_val = job_type.replace("-", " ") if job_type else ""
    remote_val = remote.replace("-", " ") if remote else ""
    experience_val = experience.replace("-", " ") if experience else ""

    results = scraper.search(
        keyword=keyword,
        location=location,
        date_posted=date_posted_val,
        job_type=job_type_val,
        remote=remote_val,
        experience=experience_val,
        salary=salary or "",
        sort_by=sort_by,
        easy_apply=easy_apply,
        per_source_limit=limit,
    )

    all_jobs = []
    jobs_by_source = {}
    
    for source, jobs in results.items():
        jobs_by_source[source] = len(jobs)
        
        for job in jobs:
            if details:
                scraper.fetch_job_details(job)
            
            job_response = job_to_response(job)
            job_with_source = JobResponseWithSource(
                **job_response.model_dump(),
                source=source
            )
            all_jobs.append(job_with_source)

    return MultiSourceSearchResponse(
        jobs=all_jobs,
        count=len(all_jobs),
        keyword=keyword,
        location=location,
        sources=valid_sources,
        jobs_by_source=jobs_by_source,
    )


@app.get("/api/sources")
async def get_available_sources():
    """Get list of available job sources."""
    return {
        "sources": [
            {
                "id": "linkedin",
                "name": "LinkedIn",
                "description": "Professional job listings from LinkedIn",
                "features": ["easy_apply", "applicant_count", "company_size"]
            },
            {
                "id": "indeed",
                "name": "Indeed",
                "description": "General job listings from Indeed",
                "features": ["salary_info", "company_reviews"]
            },
            {
                "id": "greenhouse",
                "name": "Greenhouse",
                "description": "Direct job boards from tech companies",
                "features": ["direct_apply", "startup_jobs"],
                "companies": list(GREENHOUSE_COMPANIES.keys())[:20]
            }
        ]
    }


@app.get("/api/sources/greenhouse/companies")
async def get_greenhouse_companies():
    """Get list of companies with Greenhouse job boards."""
    return {
        "companies": list(GREENHOUSE_COMPANIES.keys()),
        "count": len(GREENHOUSE_COMPANIES)
    }


@app.post("/api/profile")
async def create_profile(profile: ProfileModel):
    """Create or update user profile."""
    user_profile = UserProfile(
        name=profile.name,
        email=profile.email,
        phone=profile.phone,
        location=profile.location,
        linkedin_url=profile.linkedin_url,
        github_url=profile.github_url,
        portfolio_url=profile.portfolio_url,
        title=profile.title,
        summary=profile.summary,
        years_experience=profile.years_experience,
        skills=profile.skills,
        programming_languages=profile.programming_languages,
        frameworks=profile.frameworks,
        tools=profile.tools,
        experience=profile.experience,
        education=profile.education,
        certifications=profile.certifications,
        projects=profile.projects,
        target_roles=profile.target_roles,
        target_companies=profile.target_companies,
        preferred_locations=profile.preferred_locations,
        remote_preference=profile.remote_preference,
        min_salary=profile.min_salary,
    )
    
    profile_id = profile.email or profile.name or "default"
    profile_store[profile_id] = user_profile
    
    return {"status": "success", "profile_id": profile_id, "profile": user_profile.to_dict()}


@app.post("/api/profile/parse")
async def parse_resume(resume_text: str = Form(...)):
    """Parse resume text into a profile."""
    profile = parse_resume_text(resume_text)
    
    profile_id = profile.email or profile.name or "parsed"
    profile_store[profile_id] = profile
    
    return {"status": "success", "profile_id": profile_id, "profile": profile.to_dict()}


@app.post("/api/profile/upload-pdf")
async def upload_pdf_resume(file: UploadFile = File(...)):
    """Upload and parse a PDF resume."""
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(status_code=400, detail="File must be a PDF")
    
    try:
        contents = await file.read()
        profile = parse_pdf_resume(contents)
        
        profile_id = profile.email or profile.name or "uploaded"
        profile_store[profile_id] = profile
        
        return {"status": "success", "profile_id": profile_id, "profile": profile.to_dict()}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to parse PDF: {str(e)}")


@app.get("/api/profile/{profile_id}")
async def get_profile(profile_id: str):
    """Get a stored profile."""
    if profile_id not in profile_store:
        raise HTTPException(status_code=404, detail="Profile not found")
    
    return profile_store[profile_id].to_dict()


@app.post("/api/search/ranked", response_model=RankedSearchResponse)
async def search_and_rank_jobs(
    keyword: str = Query(..., description="Job title or keywords"),
    location: str = Query("", description="Location"),
    profile_id: str = Query(..., description="Profile ID to rank against"),
    limit: int = Query(25, ge=1, le=100),
    top_n: int = Query(10, ge=1, le=50, description="Number of top matches to return"),
):
    """Search for jobs and rank them against user profile."""
    if profile_id not in profile_store:
        raise HTTPException(status_code=404, detail="Profile not found. Create profile first.")
    
    profile = profile_store[profile_id]
    reasoning = _llm_reasoning_trace_generic(profile, job_count=0, source="live")
    scraper = LinkedInScraper()
    
    jobs = scraper.search(keyword=keyword, location=location, limit=limit)
    
    jobs = _filter_live_jobs(jobs, profile)  # Assignment-style: company exclusion + location preference

    ranker = JobRanker(profile)
    ranked_jobs = ranker.rank_jobs(jobs, top_n=top_n)
    
    return RankedSearchResponse(
        jobs=[ranked_job_to_response(r) for r in ranked_jobs],
        count=len(ranked_jobs),
        keyword=keyword,
        location=location,
        profile_name=profile.name,
        reasoning=reasoning,
    )


@app.post("/api/tailor/resume", response_model=TailoredResumeResponse)
async def tailor_resume(
    profile_id: str = Query(..., description="Profile ID"),
    job_url: str = Query(..., description="Job URL to tailor for"),
    use_openai: bool = Query(False, description="Use OpenAI for generation"),
):
    """Generate a tailored resume for a specific job."""
    if profile_id not in profile_store:
        raise HTTPException(status_code=404, detail="Profile not found")
    
    profile = profile_store[profile_id]
    scraper = LinkedInScraper()
    
    job = Job(
        position="",
        company="",
        company_logo=None,
        location="",
        date="",
        ago_time="",
        salary="",
        job_url=job_url,
    )
    scraper.fetch_job_details(job)
    
    if not job.position:
        raise HTTPException(status_code=400, detail="Could not fetch job details")
    
    tailor = ResumeTailor(use_openai=use_openai)
    result = tailor.tailor_resume(profile, job)
    modified_bullets = get_two_modified_bullets(profile, job, result.highlighted_skills)

    return TailoredResumeResponse(
        summary=result.summary,
        highlighted_skills=result.highlighted_skills,
        keywords_added=result.keywords_added,
        resume_text=result.resume_text,
        resume_html=result.resume_html,
        ats_score=result.ats_score,
        suggestions=result.suggestions,
        modified_bullets=modified_bullets,
    )


@app.post("/api/tailor/resume-from-text", response_model=TailoredResumeResponse)
async def tailor_resume_from_text(
    profile_id: str = Query(..., description="Profile ID"),
    use_openai: bool = Query(False, description="Use OpenAI for generation"),
    job: JobTextModel = None,
):
    """
    Generate a tailored resume using manually provided job description instead of scraping.
    """
    if profile_id not in profile_store:
        raise HTTPException(status_code=404, detail="Profile not found")

    if job is None:
        raise HTTPException(status_code=400, detail="Job details are required")

    profile = profile_store[profile_id]

    job_obj = Job(
        position=job.position,
        company=job.company,
        company_logo=None,
        location=job.location,
        date="",
        ago_time="",
        salary=job.salary,
        job_url=job.job_url,
        description=job.description,
    )

    tailor = ResumeTailor(use_openai=use_openai)
    result = tailor.tailor_resume(profile, job_obj)
    modified_bullets = get_two_modified_bullets(profile, job_obj, result.highlighted_skills)

    return TailoredResumeResponse(
        summary=result.summary,
        highlighted_skills=result.highlighted_skills,
        keywords_added=result.keywords_added,
        resume_text=result.resume_text,
        resume_html=result.resume_html,
        ats_score=result.ats_score,
        suggestions=result.suggestions,
        modified_bullets=modified_bullets,
    )


@app.post("/api/generate/cover-letter", response_model=CoverLetterResponse)
async def generate_cover_letter(
    profile_id: str = Query(..., description="Profile ID"),
    job_url: str = Query(..., description="Job URL"),
    use_openai: bool = Query(False, description="Use OpenAI for generation"),
):
    """Generate a cover letter for a specific job."""
    if profile_id not in profile_store:
        raise HTTPException(status_code=404, detail="Profile not found")
    
    profile = profile_store[profile_id]
    scraper = LinkedInScraper()
    
    job = Job(
        position="",
        company="",
        company_logo=None,
        location="",
        date="",
        ago_time="",
        salary="",
        job_url=job_url,
    )
    scraper.fetch_job_details(job)
    
    if not job.position:
        raise HTTPException(status_code=400, detail="Could not fetch job details")
    
    generator = CoverLetterGenerator(use_openai=use_openai)
    result = generator.generate(profile, job)
    
    return CoverLetterResponse(
        content=result.content,
        html_content=result.html_content,
        word_count=result.word_count,
        key_points=result.key_points,
        personalization_score=result.personalization_score,
    )


@app.post("/api/generate/cover-letter-from-text", response_model=CoverLetterResponse)
async def generate_cover_letter_from_text(
    profile_id: str = Query(..., description="Profile ID"),
    use_openai: bool = Query(False, description="Use OpenAI for generation"),
    job: JobTextModel = None,
):
    """
    Generate a cover letter using manually provided job description instead of scraping.
    """
    if profile_id not in profile_store:
        raise HTTPException(status_code=404, detail="Profile not found")

    if job is None:
        raise HTTPException(status_code=400, detail="Job details are required")

    profile = profile_store[profile_id]

    job_obj = Job(
        position=job.position,
        company=job.company,
        company_logo=None,
        location=job.location,
        date="",
        ago_time="",
        salary=job.salary,
        job_url=job.job_url,
        description=job.description,
    )

    generator = CoverLetterGenerator(use_openai=use_openai)
    result = generator.generate(profile, job_obj)

    return CoverLetterResponse(
        content=result.content,
        html_content=result.html_content,
        word_count=result.word_count,
        key_points=result.key_points,
        personalization_score=result.personalization_score,
    )


@app.post("/api/agent/run")
async def run_agent_pipeline(
    profile_id: str = Query(..., description="Profile ID"),
    keyword: str = Query("AI Engineer", description="Search keyword"),
    location: str = Query("", description="Location"),
    limit: int = Query(50, description="Search limit"),
    top_n: int = Query(5, description="Number of applications to generate"),
    use_openai: bool = Query(False, description="Use OpenAI"),
):
    """Run the full job search agent pipeline."""
    if profile_id not in profile_store:
        raise HTTPException(status_code=404, detail="Profile not found")
    
    profile = profile_store[profile_id]
    reasoning = _llm_reasoning_trace_generic(profile, job_count=0, source="live")
    agent = JobSearchAgent(profile, use_openai=use_openai)
    
    report = agent.run_full_pipeline(
        keyword=keyword,
        location=location,
        limit=limit,
        top_n_applications=top_n,
    )
    
    applications = agent.get_applications()
    
    return {
        "reasoning": reasoning,
        "report": report.to_dict(),
        "applications": [
            {
                "job": job_to_response(app.job).__dict__,
                "match_score": app.ranked_job.score,
                "matched_skills": app.ranked_job.matched_skills,
                "ats_score": app.tailored_resume.ats_score,
                "personalization_score": app.cover_letter.personalization_score,
            }
            for app in applications
        ],
    }


@app.post("/api/agent/middle-america")
async def run_middle_america_pipeline(
    profile_id: str = Query(..., description="Profile ID"),
    keyword: str = Query("AI Engineer", description="Search keyword"),
    location: str = Query("Iowa", description="Search location"),
    exclude_faang: bool = Query(True, description="Exclude FAANG+ companies"),
    exclude_startups: bool = Query(True, description="Exclude startups (<50 employees)"),
    location_filter: Optional[str] = Query(None, description="Additional location filter (e.g., 'Texas')"),
    limit: int = Query(50, description="Search limit"),
    top_n: int = Query(10, description="Number of top jobs to rank"),
    top_n_applications: int = Query(3, description="Number of applications to generate"),
    use_openai: bool = Query(False, description="Use OpenAI"),
):
    """
    Run the Middle America job search pipeline.
    
    Pipeline: Search → Filter FAANG → Filter Startups → Filter Location → Rank Top 10 → Tailor Top 3
    
    This pipeline is specifically designed for finding AI Engineer jobs at mid-sized
    "Middle America" companies, excluding big tech (FAANG+) and startups.
    """
    if profile_id not in profile_store:
        raise HTTPException(status_code=404, detail="Profile not found")
    
    profile = profile_store[profile_id]
    reasoning = _llm_reasoning_trace_generic(profile, job_count=0, source="live")
    agent = JobSearchAgent(profile, use_openai=use_openai, enable_logging=True)
    
    results = agent.run_middle_america_pipeline(
        keyword=keyword,
        location=location,
        exclude_faang=exclude_faang,
        exclude_startups=exclude_startups,
        location_filter=location_filter,
        limit=limit,
        top_n=top_n,
        top_n_applications=top_n_applications,
    )
    
    results["reasoning"] = reasoning
    applications = agent.get_applications()
    
    results["applications_detail"] = [
        {
            "job": job_to_response(app.job).__dict__,
            "match_score": app.ranked_job.score,
            "matched_skills": app.ranked_job.matched_skills,
            "missing_skills": app.ranked_job.missing_skills,
            "match_reasons": app.ranked_job.match_reasons,
            "ats_score": app.tailored_resume.ats_score,
            "resume_suggestions": app.tailored_resume.suggestions,
            "cover_letter_preview": app.cover_letter.content[:500] + "..." if len(app.cover_letter.content) > 500 else app.cover_letter.content,
            "personalization_score": app.cover_letter.personalization_score,
        }
        for app in applications
    ]
    
    return results


@app.get("/api/benchmark")
async def get_benchmark_dataset():
    """Get the 20-job benchmark dataset for evaluation."""
    import os
    benchmark_path = os.path.join(
        os.path.dirname(os.path.dirname(__file__)),
        "data",
        "benchmark_jobs.json"
    )
    
    if not os.path.exists(benchmark_path):
        raise HTTPException(status_code=404, detail="Benchmark dataset not found")
    
    with open(benchmark_path, 'r') as f:
        return json.load(f)


@app.get("/api/sample-resume")
async def get_sample_resume():
    """Get the sample AI Engineer resume for evaluation."""
    import os
    resume_path = os.path.join(
        os.path.dirname(os.path.dirname(__file__)),
        "data",
        "sample_resume.json"
    )
    
    if not os.path.exists(resume_path):
        raise HTTPException(status_code=404, detail="Sample resume not found")
    
    with open(resume_path, 'r') as f:
        return json.load(f)


@app.post("/api/agent/load-sample-profile")
async def load_sample_profile():
    """Load the sample AI Engineer profile for testing."""
    import os
    resume_path = os.path.join(
        os.path.dirname(os.path.dirname(__file__)),
        "data",
        "sample_resume.json"
    )
    
    if not os.path.exists(resume_path):
        raise HTTPException(status_code=404, detail="Sample resume not found")
    
    with open(resume_path, 'r') as f:
        data = json.load(f)
    
    profile = UserProfile(
        name=data.get("name", ""),
        email=data.get("email", ""),
        phone=data.get("phone", ""),
        location=data.get("location", ""),
        linkedin_url=data.get("linkedin_url", ""),
        github_url=data.get("github_url", ""),
        portfolio_url=data.get("portfolio_url", ""),
        title=data.get("title", ""),
        summary=data.get("summary", ""),
        years_experience=data.get("years_experience", 0),
        skills=data.get("skills", []),
        programming_languages=data.get("programming_languages", []),
        frameworks=data.get("frameworks", []),
        tools=data.get("tools", []),
        experience=data.get("experience", []),
        education=data.get("education", []),
        certifications=data.get("certifications", []),
        projects=data.get("projects", []),
        target_roles=data.get("target_roles", []),
        target_companies=data.get("target_companies", []),
        preferred_locations=data.get("preferred_locations", []),
        remote_preference=data.get("remote_preference", "flexible"),
        min_salary=data.get("min_salary", 0),
    )
    
    profile_id = "sample_ai_engineer"
    profile_store[profile_id] = profile
    
    return {
        "status": "success",
        "profile_id": profile_id,
        "profile": profile.to_dict(),
        "message": "Sample AI Engineer profile loaded. Use profile_id='sample_ai_engineer' in API calls."
    }


def _benchmark_job_to_job(bj: dict) -> Job:
    """Convert benchmark job dict to Job object."""
    return Job(
        position=bj.get("position", ""),
        company=bj.get("company", ""),
        company_logo=None,
        location=bj.get("location", ""),
        date="",
        ago_time="1 week ago",
        salary=bj.get("salary", ""),
        job_url=bj.get("job_url", ""),
        description=bj.get("description", ""),
        skills=bj.get("skills"),
    )


def _load_csv_jobs() -> list[CsvJobModel]:
    """Load jobs from the offline CSV dataset."""
    import csv
    from pathlib import Path

    csv_path = Path(os.path.dirname(os.path.dirname(__file__))) / "data" / "jobs_dataset.csv"
    if not csv_path.exists():
        raise HTTPException(status_code=500, detail="jobs_dataset.csv not found in data/")

    jobs: list[CsvJobModel] = []
    with csv_path.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            jobs.append(
                CsvJobModel(
                    title=(row.get("Job Title") or "").strip(),
                    company=(row.get("Company") or "").strip(),
                    location=(row.get("Location") or "").strip(),
                    required_skills=(row.get("Required Skills") or "").strip(),
                    years_experience=(row.get("Years of Experience Required") or "").strip(),
                    description=(row.get("Shortened Job Description (5–8 lines)") or "").strip(),
                    url=(row.get("URL") or "").strip(),
                )
            )
    return jobs


# Company exclusion for filtering (e.g. FAANG) – used for both live and CSV
_EXCLUDED_COMPANIES = {"meta", "facebook", "amazon", "apple", "netflix", "google", "alphabet"}

def _apply_offline_search_filters(
    jobs: list[CsvJobModel],
    keyword: str = "",
    location: str = "",
) -> list[CsvJobModel]:
    """Filter CSV jobs by search keyword and location (before profile-based filtering)."""
    if not jobs:
        return jobs
    result = jobs
    keyword = (keyword or "").strip().lower()
    location = (location or "").strip().lower()

    if keyword:
        out = []
        for j in result:
            text = f"{j.title} {j.company} {j.location} {j.required_skills} {j.description}".lower()
            if keyword in text:
                out.append(j)
        result = out if out else result
    if location:
        out = [j for j in result if location in (j.location or "").lower()]
        result = out if out else result
    return result


def _filter_live_jobs(jobs: list, profile: UserProfile) -> list:
    """Apply assignment-style filtering to live scraped jobs: company exclusion, location preference."""
    if not jobs:
        return jobs
    preferred = {loc.lower() for loc in (profile.preferred_locations or [])}
    filtered = []
    for job in jobs:
        company = (getattr(job, "company", None) or "").lower()
        if any(ex in company for ex in _EXCLUDED_COMPANIES):
            continue
        location = (getattr(job, "location", None) or "").lower()
        if preferred and location and not any(p in location for p in preferred):
            continue
        filtered.append(job)
    return filtered


def _filter_csv_jobs(
    jobs: list[CsvJobModel],
    profile: UserProfile,
    remote_only: bool = False,
) -> list[CsvJobModel]:
    """Filtering Tool for CSV jobs. Rules: location preference, experience limit, company exclusion, optional remote-only."""
    preferred_locations = {loc.lower() for loc in profile.preferred_locations}
    profile_skills = {s.lower() for s in profile.get_all_skills()}
    apply_remote_only = remote_only or (profile.remote_preference or "").lower() == "remote"

    filtered: list[CsvJobModel] = []
    for job in jobs:
        if any(ex in (job.company or "").lower() for ex in _EXCLUDED_COMPANIES):
            continue
        if apply_remote_only and "remote" not in (job.location or "").lower():
            continue
        if preferred_locations and not any(pref in (job.location or "").lower() for pref in preferred_locations):
            continue
        if job.years_experience.isdigit() and profile.years_experience < int(job.years_experience):
            continue
        job_skills = {s.strip().lower() for s in (job.required_skills or "").split(";") if s.strip()}
        if profile_skills and job_skills and not (profile_skills & job_skills):
            continue
        filtered.append(job)
    return filtered


def _rank_csv_jobs(jobs: list[CsvJobModel], profile: UserProfile, top_n: int = 10) -> list[RankedJob]:
    """Ranking Tool for CSV jobs, reusing JobRanker."""
    converted: list[Job] = []
    for j in jobs:
        converted.append(
            Job(
                position=j.title,
                company=j.company,
                company_logo=None,
                location=j.location,
                date="",
                ago_time="",
                salary="",
                job_url=j.url,
                description=j.description,
                skills=[s.strip() for s in j.required_skills.split(";") if s.strip()] or None,
            )
        )

    ranker = JobRanker(profile)
    return ranker.rank_jobs(converted, top_n=top_n)


def _tailor_resume_offline(profile: UserProfile, ranked_job: RankedJob, use_openai: bool = False) -> TailoredResumeResponse:
    """Resume Tailoring Tool for offline CSV jobs (same assignment-style: summary + 2 bullets + aligned skills)."""
    tailor = ResumeTailor(use_openai=use_openai)
    result = tailor.tailor_resume(profile, ranked_job.job)
    modified_bullets = get_two_modified_bullets(profile, ranked_job.job, list(ranked_job.matched_skills))

    return TailoredResumeResponse(
        summary=result.summary,
        highlighted_skills=result.highlighted_skills,
        keywords_added=result.keywords_added,
        resume_text=result.resume_text,
        resume_html=result.resume_html,
        ats_score=result.ats_score,
        suggestions=result.suggestions,
        modified_bullets=modified_bullets,
    )


def _llm_reasoning_trace_generic(profile: UserProfile, job_count: int = 0, source: str = "live") -> Optional[str]:
    """Shared LLM reasoning trace for live and CSV workflows (OpenAI, Claude, or Ollama)."""
    provider = os.environ.get("LLM_PROVIDER", "").lower()
    openai_key = os.environ.get("OPENAI_API_KEY")
    anthropic_key = os.environ.get("ANTHROPIC_API_KEY")
    if not provider:
        if openai_key:
            provider = "openai"
        elif anthropic_key:
            provider = "anthropic"
        else:
            provider = "ollama"
    system_msg = (
        "You are an AI job search agent that must decide which tools to call and in what order. "
        "Available tools:\n"
        "1) filtering_tool: filters jobs by location, skills, experience years, and company exclusion.\n"
        "2) ranking_tool: scores jobs by skill match, title, location, and experience alignment.\n"
        "3) resume_tailoring_tool: rewrites the professional summary and two experience bullets for the chosen job.\n"
        "You should reason step by step and output a short explanation of which tools you will call and why."
    )
    if source == "csv":
        user_msg = (
            f"Candidate profile:\n"
            f"- Title: {profile.title}\n"
            f"- Years of experience: {profile.years_experience}\n"
            f"- Skills: {', '.join(profile.get_all_skills())}\n"
            f"- Preferred locations: {', '.join(profile.preferred_locations) or 'not specified'}\n"
            f"There are {job_count} jobs in the CSV dataset. "
            "Explain which tools you will use, in what order, and what each contributes. Keep it under 8 sentences."
        )
    else:
        user_msg = (
            f"Candidate profile:\n"
            f"- Title: {profile.title}\n"
            f"- Years of experience: {profile.years_experience}\n"
            f"- Skills: {', '.join(profile.get_all_skills())}\n"
            f"- Preferred locations: {', '.join(profile.preferred_locations) or 'not specified'}\n"
            "The agent will search LinkedIn (and optionally other sources) for jobs, then apply filtering "
            "(location, experience), then rank jobs by skill and experience match, then select "
            "the best job and tailor the resume (summary + 2 bullets). Explain which tools are used and in what order, and why."
        )
    reasoning: Optional[str] = None
    try:
        if provider == "openai" and openai_key:
            try:
                from openai import OpenAI
            except Exception:
                pass
            else:
                client = OpenAI(api_key=openai_key)
                resp = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": system_msg},
                        {"role": "user", "content": user_msg},
                    ],
                    temperature=0.2,
                )
                reasoning = resp.choices[0].message.content
        elif provider == "anthropic" and anthropic_key:
            try:
                import anthropic
            except Exception:
                pass
            else:
                client = anthropic.Anthropic(api_key=anthropic_key)
                resp = client.messages.create(
                    model="claude-3-5-sonnet-20240620",
                    max_tokens=400,
                    temperature=0.2,
                    system=system_msg,
                    messages=[{"role": "user", "content": user_msg}],
                )
                parts: List[str] = []
                for block in resp.content:
                    if getattr(block, "type", "") == "text":
                        parts.append(block.text)
                reasoning = "\n".join(parts)
        elif provider == "ollama":
            try:
                import json
                import requests
            except Exception:
                pass
            else:
                payload = {
                    "model": os.environ.get("OLLAMA_MODEL", "llama3.2"),
                    "messages": [
                        {"role": "system", "content": system_msg},
                        {"role": "user", "content": user_msg},
                    ],
                    "stream": False,
                }
                resp = requests.post(
                    "http://localhost:11434/api/chat",
                    data=json.dumps(payload),
                    timeout=60,
                )
                if resp.ok:
                    data = resp.json()
                    reasoning = data.get("message", {}).get("content", "")
    except Exception:
        reasoning = None
    return reasoning


def _llm_reasoning_trace_offline(profile: UserProfile, jobs: list[CsvJobModel]) -> Optional[str]:
    """LLM reasoning trace for offline CSV agent; delegates to generic helper."""
    return _llm_reasoning_trace_generic(profile, job_count=len(jobs), source="csv")


@app.post("/api/evaluate", response_model=EvaluationResponse)
async def evaluate_applications(
    profile_id: str = Query(..., description="Profile ID"),
    keyword: str = Query("AI Engineer"),
    num_applications: int = Query(5, ge=1, le=20),
    use_benchmark: bool = Query(True, description="Use benchmark (fast, ~5 sec) vs live LinkedIn (slow, 2-5 min)"),
):
    """Run hiring simulation evaluation. Default: benchmark mode (fast). Set use_benchmark=false for live search."""
    if profile_id not in profile_store:
        raise HTTPException(status_code=404, detail="Profile not found")
    
    profile = profile_store[profile_id]
    
    if use_benchmark:
        # Fast path: use 20-job benchmark, no LinkedIn scraping
        benchmark_path = os.path.join(os.path.dirname(__file__), "..", "data", "benchmark_jobs.json")
        if not os.path.exists(benchmark_path):
            raise HTTPException(status_code=500, detail="Benchmark file not found")
        with open(benchmark_path) as f:
            benchmark = json.load(f)
        jobs_data = benchmark.get("interview_worthy", [])[:num_applications]
        jobs = [_benchmark_job_to_job(bj) for bj in jobs_data]
        ranker = JobRanker(profile)
        resume_tailor = ResumeTailor(use_openai=False)
        cover_letter_gen = CoverLetterGenerator(use_openai=False)
        from linkedin_scraper.agent.agent import ApplicationPackage
        from datetime import datetime
        ranked = ranker.rank_jobs(jobs, top_n=num_applications)
        applications = []
        for rj in ranked:
            tailored = resume_tailor.tailor_resume(profile, rj.job)
            cover = cover_letter_gen.generate(profile, rj.job)
            applications.append(ApplicationPackage(
                job=rj.job, ranked_job=rj, tailored_resume=tailored,
                cover_letter=cover, created_at=datetime.now().isoformat(),
            ))
    else:
        # Full pipeline: live LinkedIn search (slow - 2-5 min)
        agent = JobSearchAgent(profile, use_openai=False)
        agent.search(keyword=keyword, limit=30)
        agent.filter_jobs()
        agent.rank_jobs(fetch_details=False)
        applications = agent.generate_applications(top_n=num_applications)
    
    evaluator = AgentEvaluator(recruiter_strictness=0.5)
    metrics = evaluator.evaluate_applications(applications)
    
    return EvaluationResponse(
        total_applications=metrics.total_applications,
        avg_match_score=metrics.avg_match_score,
        avg_ats_score=metrics.avg_ats_score,
        avg_personalization_score=metrics.avg_personalization_score,
        interview_rate=metrics.interview_rate,
        maybe_rate=metrics.maybe_rate,
        rejection_rate=metrics.rejection_rate,
        skill_coverage=metrics.skill_coverage,
        recruiter_feedback=[
            {
                "application_id": f.application_id,
                "resume_score": f.resume_score,
                "cover_letter_score": f.cover_letter_score,
                "decision": f.interview_decision,
                "impression": f.overall_impression,
                "strengths": f.strengths,
                "weaknesses": f.weaknesses,
            }
            for f in metrics.recruiter_feedback
        ],
    )


@app.post("/api/agent/offline", response_model=OfflineAgentResponse)
async def run_offline_agent(
    profile_id: str = Query(..., description="Profile ID"),
    top_n: int = Query(10, ge=1, le=50, description="Number of top matches to return"),
    use_openai: bool = Query(False, description="Use OpenAI/LLM for resume tailoring"),
    keyword: str = Query("", description="Search keyword (job title, company, description, skills)"),
    location: str = Query("", description="Location filter (e.g. Remote, California)"),
):
    """
    Run the offline CSV-based assignment agent.

    Optional search filters: keyword, location (applied to CSV before profile filtering).
    Then: Filtering Tool → Ranking Tool → Resume Tailoring Tool for the best job.
    """
    if profile_id not in profile_store:
        raise HTTPException(status_code=404, detail="Profile not found")

    profile = profile_store[profile_id]
    all_jobs = _load_csv_jobs()
    jobs = _apply_offline_search_filters(all_jobs, keyword=keyword, location=location)
    if not jobs:
        jobs = all_jobs

    profile_summary = (
        f"Title: {profile.title}, Years: {profile.years_experience}, "
        f"Skills: {', '.join(profile.get_all_skills()[:12])}, "
        f"Locations: {', '.join(profile.preferred_locations) or 'Any'}."
    )
    state: dict = {"filtered": None, "ranked": None, "tailored": None}

    def execute_tool(tool_name: str, arguments: dict) -> str:
        if tool_name == "filtering_tool":
            state["filtered"] = _filter_csv_jobs(jobs, profile)
            return f"Filtered to {len(state['filtered'])} jobs."
        if tool_name == "ranking_tool":
            if not state.get("filtered"):
                return "Error: call filtering_tool first."
            top_n = min(int(arguments.get("top_n", 3)), 3)
            state["ranked"] = _rank_csv_jobs(state["filtered"], profile, top_n=top_n)
            top3 = state["ranked"][:3]
            return f"Ranked {len(state['ranked'])} jobs. Top 3: " + "; ".join(f"{rj.job.position} at {rj.job.company} ({rj.score}%)" for rj in top3)
        if tool_name == "resume_tailoring_tool":
            if not state.get("ranked"):
                return "Error: call ranking_tool first."
            idx = max(0, int(arguments.get("job_rank", 1)) - 1)
            best = state["ranked"][idx]
            state["tailored"] = _tailor_resume_offline(profile, best, use_openai=use_openai)
            return f"Tailored resume generated for {best.job.position} at {best.job.company}."
        return "Unknown tool."

    reasoning, success = run_llm_tool_agent(
        profile_summary=profile_summary,
        job_count=len(jobs),
        execute_tool=execute_tool,
    )

    if success and state.get("ranked") and state.get("tailored") is not None:
        ranked = state["ranked"]
        tailored_resume = state["tailored"]
    else:
        filtered = _filter_csv_jobs(jobs, profile)
        if not filtered:
            filtered = jobs
        ranked = _rank_csv_jobs(filtered, profile, top_n=3)
        if not ranked:
            ranked = _rank_csv_jobs(jobs, profile, top_n=3)
        if not ranked:
            raise HTTPException(status_code=400, detail="No jobs in the dataset")
        best_ranked = ranked[0]
        tailored_resume = _tailor_resume_offline(profile, best_ranked, use_openai=use_openai)

    ranked = ranked[:3]
    ranked_responses = [ranked_job_to_response(rj) for rj in ranked]
    best_index = 0

    return OfflineAgentResponse(
        reasoning=reasoning,
        ranked_jobs=ranked_responses,
        chosen_index=best_index,
        tailored_resume=tailored_resume,
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
