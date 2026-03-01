"""FastAPI backend for LinkedIn Job Scraper with AI Agent features."""

from fastapi import FastAPI, Query, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, FileResponse
from pydantic import BaseModel, Field
from typing import Optional
import sys
import os
import json
import tempfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from linkedin_scraper.scraper import LinkedInScraper, Job
from linkedin_scraper.agent.profile import UserProfile, parse_resume_text, parse_pdf_resume
from linkedin_scraper.agent.ranker import JobRanker, RankedJob
from linkedin_scraper.agent.resume_tailor import ResumeTailor
from linkedin_scraper.agent.cover_letter import CoverLetterGenerator
from linkedin_scraper.agent.agent import JobSearchAgent
from linkedin_scraper.agent.evaluation import AgentEvaluator, BiasAnalyzer

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


class SearchResponse(BaseModel):
    """Search results response model."""
    jobs: list[JobResponse]
    count: int
    keyword: str
    location: str


class RankedSearchResponse(BaseModel):
    """Ranked search results response."""
    jobs: list[RankedJobResponse]
    count: int
    keyword: str
    location: str
    profile_name: str


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
    """Tailored resume response."""
    summary: str
    highlighted_skills: list[str]
    keywords_added: list[str]
    resume_text: str
    resume_html: str
    ats_score: float
    suggestions: list[str]


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


class BiasAnalysisResponse(BaseModel):
    """Bias analysis response."""
    location_bias: dict
    company_size_bias: dict
    salary_range_bias: dict
    experience_level_bias: dict
    keyword_frequency: dict
    excluded_keywords: list[str]
    recommendations: list[str]


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
            "Bias Analysis",
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
    company_size: Optional[str] = Query(None, description="small, mid, or large"),
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

    if company_size:
        jobs = JobRanker.filter_by_company_size(jobs, company_size)

    if details:
        for job in jobs:
            scraper.fetch_job_details(job)

    return SearchResponse(
        jobs=[job_to_response(job) for job in jobs],
        count=len(jobs),
        keyword=keyword,
        location=location,
    )


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
    company_size: str = Query("mid", description="Company size filter"),
    limit: int = Query(25, ge=1, le=100),
    top_n: int = Query(10, ge=1, le=50, description="Number of top matches to return"),
):
    """Search for jobs and rank them against user profile."""
    if profile_id not in profile_store:
        raise HTTPException(status_code=404, detail="Profile not found. Create profile first.")
    
    profile = profile_store[profile_id]
    scraper = LinkedInScraper()
    
    jobs = scraper.search(keyword=keyword, location=location, limit=limit)
    
    jobs = JobRanker.filter_by_company_size(jobs, company_size)
    
    ranker = JobRanker(profile)
    ranked_jobs = ranker.rank_jobs(jobs, top_n=top_n)
    
    return RankedSearchResponse(
        jobs=[ranked_job_to_response(r) for r in ranked_jobs],
        count=len(ranked_jobs),
        keyword=keyword,
        location=location,
        profile_name=profile.name,
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
    
    return TailoredResumeResponse(
        summary=result.summary,
        highlighted_skills=result.highlighted_skills,
        keywords_added=result.keywords_added,
        resume_text=result.resume_text,
        resume_html=result.resume_html,
        ats_score=result.ats_score,
        suggestions=result.suggestions,
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


@app.post("/api/agent/run")
async def run_agent_pipeline(
    profile_id: str = Query(..., description="Profile ID"),
    keyword: str = Query("AI Engineer", description="Search keyword"),
    location: str = Query("", description="Location"),
    company_size: str = Query("mid", description="Company size"),
    limit: int = Query(50, description="Search limit"),
    top_n: int = Query(5, description="Number of applications to generate"),
    use_openai: bool = Query(False, description="Use OpenAI"),
):
    """Run the full job search agent pipeline."""
    if profile_id not in profile_store:
        raise HTTPException(status_code=404, detail="Profile not found")
    
    profile = profile_store[profile_id]
    agent = JobSearchAgent(profile, use_openai=use_openai)
    
    report = agent.run_full_pipeline(
        keyword=keyword,
        location=location,
        company_size=company_size,
        limit=limit,
        top_n_applications=top_n,
    )
    
    applications = agent.get_applications()
    
    return {
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


@app.post("/api/evaluate", response_model=EvaluationResponse)
async def evaluate_applications(
    profile_id: str = Query(..., description="Profile ID"),
    keyword: str = Query("AI Engineer"),
    num_applications: int = Query(5, ge=1, le=20),
):
    """Run hiring simulation evaluation."""
    if profile_id not in profile_store:
        raise HTTPException(status_code=404, detail="Profile not found")
    
    profile = profile_store[profile_id]
    agent = JobSearchAgent(profile, use_openai=False)
    
    agent.search(keyword=keyword, limit=30)
    agent.filter_jobs(company_size="mid")
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


@app.post("/api/analyze/bias", response_model=BiasAnalysisResponse)
async def analyze_bias(
    profile_id: str = Query(..., description="Profile ID"),
    keyword: str = Query("AI Engineer"),
    limit: int = Query(30),
):
    """Analyze potential biases in job search results."""
    if profile_id not in profile_store:
        raise HTTPException(status_code=404, detail="Profile not found")
    
    profile = profile_store[profile_id]
    scraper = LinkedInScraper()
    ranker = JobRanker(profile)
    
    jobs = scraper.search(keyword=keyword, limit=limit)
    ranked = ranker.rank_jobs(jobs)
    
    analyzer = BiasAnalyzer()
    analysis = analyzer.analyze(jobs, ranked, profile)
    
    return BiasAnalysisResponse(
        location_bias=analysis.location_bias,
        company_size_bias=analysis.company_size_bias,
        salary_range_bias=analysis.salary_range_bias,
        experience_level_bias=analysis.experience_level_bias,
        keyword_frequency=analysis.keyword_frequency,
        excluded_keywords=analysis.excluded_keywords,
        recommendations=analysis.recommendations,
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
