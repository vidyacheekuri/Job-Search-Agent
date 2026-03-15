"""Main Job Search Agent that orchestrates the entire pipeline."""

import json
import os
from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Optional
from pathlib import Path

from ..scraper import LinkedInScraper, Job
from .profile import UserProfile
from .ranker import JobRanker, RankedJob
from .resume_tailor import ResumeTailor, TailoredResume
from .cover_letter import CoverLetterGenerator, CoverLetter
from .evaluation import PipelineLogger, HiringSimulator, TailoringEvaluator


@dataclass
class ApplicationPackage:
    """Complete application materials for a job."""
    job: Job
    ranked_job: RankedJob
    tailored_resume: TailoredResume
    cover_letter: CoverLetter
    created_at: str
    
    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "job": self.job.to_dict(),
            "match_score": self.ranked_job.score,
            "matched_skills": self.ranked_job.matched_skills,
            "missing_skills": self.ranked_job.missing_skills,
            "match_reasons": self.ranked_job.match_reasons,
            "ats_score": self.tailored_resume.ats_score,
            "resume_suggestions": self.tailored_resume.suggestions,
            "cover_letter_word_count": self.cover_letter.word_count,
            "personalization_score": self.cover_letter.personalization_score,
            "created_at": self.created_at,
        }
    
    def save(self, output_dir: str) -> dict:
        """
        Save application materials to directory.
        
        Args:
            output_dir: Directory to save files to.
            
        Returns:
            Dictionary with file paths.
        """
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        
        company_slug = self.job.company.lower().replace(" ", "_")[:20]
        position_slug = self.job.position.lower().replace(" ", "_")[:20]
        prefix = f"{company_slug}_{position_slug}"
        
        resume_txt_path = os.path.join(output_dir, f"{prefix}_resume.txt")
        with open(resume_txt_path, "w") as f:
            f.write(self.tailored_resume.resume_text)
        
        resume_html_path = os.path.join(output_dir, f"{prefix}_resume.html")
        with open(resume_html_path, "w") as f:
            f.write(self.tailored_resume.resume_html)
        
        cover_txt_path = os.path.join(output_dir, f"{prefix}_cover_letter.txt")
        with open(cover_txt_path, "w") as f:
            f.write(self.cover_letter.content)
        
        cover_html_path = os.path.join(output_dir, f"{prefix}_cover_letter.html")
        with open(cover_html_path, "w") as f:
            f.write(self.cover_letter.html_content)
        
        summary_path = os.path.join(output_dir, f"{prefix}_summary.json")
        with open(summary_path, "w") as f:
            json.dump(self.to_dict(), f, indent=2)
        
        return {
            "resume_txt": resume_txt_path,
            "resume_html": resume_html_path,
            "cover_letter_txt": cover_txt_path,
            "cover_letter_html": cover_html_path,
            "summary": summary_path,
        }


@dataclass
class AgentReport:
    """Summary report of agent's job search run."""
    profile_name: str
    search_keyword: str
    search_location: str
    total_jobs_found: int
    jobs_after_filter: int
    top_matches: list[dict]
    applications_generated: int
    average_match_score: float
    average_ats_score: float
    run_timestamp: str
    run_duration_seconds: float
    
    def to_dict(self) -> dict:
        return asdict(self)
    
    def save(self, path: str) -> None:
        """Save report to JSON file."""
        with open(path, "w") as f:
            json.dump(self.to_dict(), f, indent=2)


class JobSearchAgent:
    """
    Autonomous AI agent for job searching.
    
    Pipeline:
    1. Search - Find jobs matching criteria
    2. Filter - Filter by company size, requirements
    3. Rank - Score and rank jobs by profile match
    4. Tailor - Generate customized resumes and cover letters
    """
    
    DEFAULT_AI_KEYWORDS = [
        "AI Engineer",
        "Machine Learning Engineer", 
        "ML Engineer",
        "Deep Learning Engineer",
        "NLP Engineer",
        "Computer Vision Engineer",
        "AI/ML Engineer",
        "Applied Scientist",
        "Research Engineer",
    ]
    
    def __init__(
        self,
        profile: UserProfile,
        use_openai: bool = False,
        openai_api_key: Optional[str] = None,
        scraper_delay: float = 1.0,
        enable_logging: bool = True,
    ):
        """
        Initialize the job search agent.
        
        Args:
            profile: User profile for matching and tailoring.
            use_openai: Whether to use OpenAI for generation.
            openai_api_key: OpenAI API key.
            scraper_delay: Delay between scraper requests.
            enable_logging: Enable pipeline decision logging.
        """
        self.profile = profile
        self.scraper = LinkedInScraper(delay=scraper_delay)
        self.ranker = JobRanker(profile)
        self.resume_tailor = ResumeTailor(use_openai=use_openai, api_key=openai_api_key)
        self.cover_letter_gen = CoverLetterGenerator(use_openai=use_openai, api_key=openai_api_key)
        
        self._search_results: list[Job] = []
        self._filtered_results: list[Job] = []
        self._ranked_results: list[RankedJob] = []
        self._applications: list[ApplicationPackage] = []
        
        self.enable_logging = enable_logging
        self.logger = PipelineLogger() if enable_logging else None
        self.evaluator = TailoringEvaluator()
    
    def search(
        self,
        keyword: str = "AI Engineer",
        location: str = "",
        job_type: str = "full time",
        remote: str = "",
        experience: str = "",
        date_posted: str = "",
        easy_apply: bool = False,
        limit: int = 50,
    ) -> list[Job]:
        """
        Search for jobs on LinkedIn.
        
        Args:
            keyword: Job title or keywords.
            location: Location to search in.
            job_type: Type of job (full time, contract, etc).
            remote: Remote preference.
            experience: Experience level.
            date_posted: How recent jobs should be.
            easy_apply: Filter for Easy Apply only.
            limit: Maximum number of results.
            
        Returns:
            List of found jobs.
        """
        jobs = self.scraper.search(
            keyword=keyword,
            location=location,
            job_type=job_type,
            remote=remote,
            experience=experience,
            date_posted=date_posted,
            easy_apply=easy_apply,
            limit=limit,
        )
        
        self._search_results = jobs
        return jobs
    
    def search_ai_engineer_roles(
        self,
        location: str = "",
        experience: str = "",
        limit_per_keyword: int = 20,
    ) -> list[Job]:
        """
        Search specifically for AI Engineer roles using multiple keywords.
        
        Args:
            location: Location to search in.
            experience: Experience level filter.
            limit_per_keyword: Max results per keyword search.
            
        Returns:
            Deduplicated list of AI engineer jobs.
        """
        all_jobs = []
        seen_urls = set()
        
        for keyword in self.DEFAULT_AI_KEYWORDS:
            jobs = self.scraper.search(
                keyword=keyword,
                location=location,
                experience=experience,
                job_type="full time",
                limit=limit_per_keyword,
            )
            
            for job in jobs:
                if job.job_url not in seen_urls:
                    seen_urls.add(job.job_url)
                    all_jobs.append(job)
        
        self._search_results = all_jobs
        return all_jobs
    
    def filter_jobs(
        self,
        jobs: Optional[list[Job]] = None,
        require_salary: bool = False,
        exclude_companies: Optional[list[str]] = None,
    ) -> list[Job]:
        """
        Filter jobs by criteria.
        
        Args:
            jobs: Jobs to filter (uses search results if not provided).
            require_salary: Only include jobs with salary info.
            exclude_companies: Companies to exclude.
            
        Returns:
            Filtered list of jobs.
        """
        jobs = jobs or self._search_results
        filtered = list(jobs)
        
        if require_salary:
            filtered = [j for j in filtered if j.salary]
        
        if exclude_companies:
            exclude_lower = set(c.lower() for c in exclude_companies)
            filtered = [j for j in filtered if j.company.lower() not in exclude_lower]
        
        self._filtered_results = filtered
        return filtered
    
    def filter_middle_america(
        self,
        jobs: Optional[list[Job]] = None,
        exclude_faang: bool = True,
        exclude_startups: bool = True,
        location_filter: Optional[str] = None,
    ) -> tuple[list[Job], list[dict]]:
        """
        Apply Middle America filters (FAANG blacklist + startup exclusion).
        
        Args:
            jobs: Jobs to filter (uses search results if not provided).
            exclude_faang: Exclude FAANG+ big tech companies.
            exclude_startups: Exclude startups (<50 employees).
            location_filter: Optional location filter (e.g., "Iowa", "Texas").
            
        Returns:
            Tuple of (filtered jobs, decision log).
        """
        jobs = jobs or self._search_results
        all_logs = []
        
        if exclude_faang:
            jobs, faang_logs = JobRanker.filter_faang_blacklist(jobs, log_decisions=self.enable_logging)
            all_logs.extend(faang_logs)
            if self.logger:
                for log in faang_logs:
                    self.logger.log_filter(
                        "filter_faang",
                        log.get("job", ""),
                        log.get("company", ""),
                        log.get("action") == "INCLUDED",
                        log.get("reason", ""),
                    )
        
        if exclude_startups:
            jobs, startup_logs = JobRanker.filter_startups(jobs, log_decisions=self.enable_logging)
            all_logs.extend(startup_logs)
            if self.logger:
                for log in startup_logs:
                    self.logger.log_filter(
                        "filter_startup",
                        log.get("job", ""),
                        log.get("company", ""),
                        log.get("action") == "INCLUDED",
                        log.get("reason", ""),
                    )
        
        if location_filter:
            jobs, location_logs = JobRanker.filter_by_location(jobs, location_filter, log_decisions=self.enable_logging)
            all_logs.extend(location_logs)
            if self.logger:
                for log in location_logs:
                    self.logger.log_filter(
                        "filter_location",
                        log.get("job", ""),
                        log.get("company", ""),
                        log.get("action") == "INCLUDED",
                        log.get("reason", ""),
                    )
        
        self._filtered_results = jobs
        return jobs, all_logs
    
    def rank_jobs(
        self,
        jobs: Optional[list[Job]] = None,
        top_n: Optional[int] = None,
        min_score: float = 0,
        fetch_details: bool = True,
    ) -> list[RankedJob]:
        """
        Rank jobs by profile match.
        
        Args:
            jobs: Jobs to rank (uses filtered results if not provided).
            top_n: Limit to top N results.
            min_score: Minimum match score (0-100).
            fetch_details: Fetch full job descriptions before ranking.
            
        Returns:
            List of ranked jobs sorted by score.
        """
        jobs = jobs or self._filtered_results or self._search_results
        
        if fetch_details:
            for job in jobs:
                if not job.description:
                    self.scraper.fetch_job_details(job)
        
        ranked = self.ranker.rank_jobs(jobs, top_n=top_n)
        
        if min_score > 0:
            ranked = [r for r in ranked if r.score >= min_score]
        
        self._ranked_results = ranked
        return ranked
    
    def generate_application(
        self,
        ranked_job: RankedJob,
    ) -> ApplicationPackage:
        """
        Generate complete application materials for a job.
        
        Args:
            ranked_job: Ranked job to generate application for.
            
        Returns:
            ApplicationPackage with resume and cover letter.
        """
        tailored_resume = self.resume_tailor.tailor_resume(self.profile, ranked_job.job)
        
        cover_letter = self.cover_letter_gen.generate(self.profile, ranked_job.job)
        
        package = ApplicationPackage(
            job=ranked_job.job,
            ranked_job=ranked_job,
            tailored_resume=tailored_resume,
            cover_letter=cover_letter,
            created_at=datetime.now().isoformat(),
        )
        
        self._applications.append(package)
        return package
    
    def generate_applications(
        self,
        ranked_jobs: Optional[list[RankedJob]] = None,
        top_n: int = 5,
    ) -> list[ApplicationPackage]:
        """
        Generate applications for top ranked jobs.
        
        Args:
            ranked_jobs: Ranked jobs (uses ranking results if not provided).
            top_n: Number of applications to generate.
            
        Returns:
            List of application packages.
        """
        ranked_jobs = ranked_jobs or self._ranked_results
        
        applications = []
        for ranked_job in ranked_jobs[:top_n]:
            package = self.generate_application(ranked_job)
            applications.append(package)
        
        return applications
    
    def run_full_pipeline(
        self,
        keyword: str = "AI Engineer",
        location: str = "",
        limit: int = 50,
        top_n_applications: int = 5,
        output_dir: Optional[str] = None,
    ) -> AgentReport:
        """
        Run the complete job search and application pipeline.
        
        Args:
            keyword: Search keyword.
            location: Search location.
            limit: Max search results.
            top_n_applications: Number of applications to generate.
            output_dir: Directory to save outputs.
            
        Returns:
            AgentReport summarizing the run.
        """
        import time
        start_time = time.time()
        
        print(f"🔍 Searching for '{keyword}' jobs...")
        jobs = self.search(keyword=keyword, location=location, limit=limit)
        print(f"   Found {len(jobs)} jobs")
        
        filtered = self.filter_jobs()
        print(f"   {len(filtered)} jobs after filtering")
        
        print("📊 Ranking jobs by profile match...")
        ranked = self.rank_jobs(top_n=top_n_applications * 2)
        print(f"   Top match: {ranked[0].score}% - {ranked[0].job.position} at {ranked[0].job.company}" if ranked else "   No matches")
        
        print(f"📝 Generating {top_n_applications} application packages...")
        applications = self.generate_applications(top_n=top_n_applications)
        print(f"   Generated {len(applications)} applications")
        
        if output_dir:
            print(f"💾 Saving to {output_dir}...")
            for app in applications:
                app.save(output_dir)
        
        elapsed = time.time() - start_time
        
        avg_match = sum(r.score for r in ranked) / len(ranked) if ranked else 0
        avg_ats = sum(a.tailored_resume.ats_score for a in applications) / len(applications) if applications else 0
        
        report = AgentReport(
            profile_name=self.profile.name,
            search_keyword=keyword,
            search_location=location,
            total_jobs_found=len(jobs),
            jobs_after_filter=len(filtered),
            top_matches=[
                {
                    "position": r.job.position,
                    "company": r.job.company,
                    "score": r.score,
                    "location": r.job.location,
                }
                for r in ranked[:10]
            ],
            applications_generated=len(applications),
            average_match_score=round(avg_match, 1),
            average_ats_score=round(avg_ats, 1),
            run_timestamp=datetime.now().isoformat(),
            run_duration_seconds=round(elapsed, 2),
        )
        
        if output_dir:
            report.save(os.path.join(output_dir, "agent_report.json"))
        
        print(f"✅ Pipeline complete in {elapsed:.1f}s")
        
        return report
    
    def get_search_results(self) -> list[Job]:
        """Get the last search results."""
        return self._search_results
    
    def get_filtered_results(self) -> list[Job]:
        """Get the last filtered results."""
        return self._filtered_results
    
    def get_ranked_results(self) -> list[RankedJob]:
        """Get the last ranked results."""
        return self._ranked_results
    
    def get_applications(self) -> list[ApplicationPackage]:
        """Get all generated applications."""
        return self._applications
    
    def get_pipeline_log(self) -> dict:
        """Get the pipeline decision log."""
        if self.logger:
            return {
                "summary": self.logger.get_summary(),
                "logs": [log.to_dict() for log in self.logger.logs],
            }
        return {"summary": {}, "logs": []}
    
    def export_pipeline_trace(self, filepath: str) -> None:
        """Export pipeline trace for report appendix."""
        if self.logger:
            self.logger.export_trace(filepath)
    
    def run_middle_america_pipeline(
        self,
        keyword: str = "AI Engineer",
        location: str = "Iowa",
        exclude_faang: bool = True,
        exclude_startups: bool = True,
        location_filter: Optional[str] = None,
        limit: int = 50,
        top_n: int = 10,
        top_n_applications: int = 3,
        output_dir: Optional[str] = None,
    ) -> dict:
        """
        Run the complete Middle America job search pipeline.
        
        Pipeline: Search → Filter FAANG → Filter Startups → Filter Location → Rank → Tailor
        
        Args:
            keyword: Search keyword (default: "AI Engineer").
            location: Search location.
            exclude_faang: Exclude FAANG+ companies.
            exclude_startups: Exclude startups.
            location_filter: Additional location filter (e.g., "Iowa-only").
            limit: Max search results.
            top_n: Number of top jobs to rank.
            top_n_applications: Number of applications to generate (top 3).
            output_dir: Directory to save outputs.
            
        Returns:
            Complete pipeline results with logs and metrics.
        """
        import time
        start_time = time.time()
        
        print(f"🔍 Stage 1: Searching for '{keyword}' jobs in {location}...")
        jobs = self.search(keyword=keyword, location=location, limit=limit)
        print(f"   Found {len(jobs)} jobs")
        if self.logger:
            self.logger.log_search(keyword, "linkedin", len(jobs))
        
        print(f"🚫 Stage 2: Filtering FAANG+ and startups...")
        filtered, filter_logs = self.filter_middle_america(
            jobs,
            exclude_faang=exclude_faang,
            exclude_startups=exclude_startups,
            location_filter=location_filter,
        )
        print(f"   {len(filtered)} jobs after filtering")
        
        print(f"📊 Stage 3: Ranking top {top_n} jobs by profile match...")
        ranked = self.rank_jobs(top_n=top_n)
        if self.logger:
            for i, r in enumerate(ranked, 1):
                self.logger.log_rank(
                    r.job.position,
                    r.job.company,
                    r.score,
                    i,
                    r.match_reasons,
                )
        print(f"   Top match: {ranked[0].score}% - {ranked[0].job.position} at {ranked[0].job.company}" if ranked else "   No matches")
        
        print(f"📝 Stage 4: Generating {top_n_applications} application packages...")
        applications = self.generate_applications(top_n=top_n_applications)
        if self.logger:
            for app in applications:
                self.logger.log_tailor(
                    app.job.position,
                    app.job.company,
                    "resume+cover_letter",
                    app.tailored_resume.suggestions[:3] if app.tailored_resume.suggestions else [],
                )
        print(f"   Generated {len(applications)} applications")
        
        if output_dir:
            print(f"💾 Saving outputs to {output_dir}...")
            Path(output_dir).mkdir(parents=True, exist_ok=True)
            for app in applications:
                app.save(output_dir)
            self.export_pipeline_trace(os.path.join(output_dir, "pipeline_trace.json"))
        
        elapsed = time.time() - start_time
        
        results = {
            "pipeline": "Middle America Job Search Agent",
            "profile": self.profile.name,
            "search": {
                "keyword": keyword,
                "location": location,
                "total_found": len(jobs),
            },
            "filters": {
                "exclude_faang": exclude_faang,
                "exclude_startups": exclude_startups,
                "location_filter": location_filter,
                "jobs_after_filter": len(filtered),
            },
            "ranking": {
                "top_n": top_n,
                "top_jobs": [
                    {
                        "rank": i + 1,
                        "position": r.job.position,
                        "company": r.job.company,
                        "location": r.job.location,
                        "score": r.score,
                        "match_reasons": r.match_reasons,
                    }
                    for i, r in enumerate(ranked[:top_n])
                ],
            },
            "applications": {
                "generated": len(applications),
                "jobs": [
                    {
                        "position": app.job.position,
                        "company": app.job.company,
                        "ats_score": app.tailored_resume.ats_score,
                    }
                    for app in applications
                ],
            },
            "metrics": {
                "average_match_score": round(sum(r.score for r in ranked) / len(ranked), 1) if ranked else 0,
                "average_ats_score": round(sum(a.tailored_resume.ats_score for a in applications) / len(applications), 1) if applications else 0,
            },
            "timing": {
                "duration_seconds": round(elapsed, 2),
                "timestamp": datetime.now().isoformat(),
            },
            "pipeline_log": self.get_pipeline_log() if self.enable_logging else None,
        }
        
        if output_dir:
            with open(os.path.join(output_dir, "pipeline_results.json"), "w") as f:
                json.dump(results, f, indent=2)
        
        print(f"✅ Pipeline complete in {elapsed:.1f}s")
        
        return results
