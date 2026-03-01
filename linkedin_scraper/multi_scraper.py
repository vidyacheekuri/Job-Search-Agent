"""Multi-source job scraper that combines LinkedIn, Indeed, and Greenhouse."""

from dataclasses import dataclass
from typing import Optional
from concurrent.futures import ThreadPoolExecutor, as_completed

from .scraper import Job, LinkedInScraper
from .indeed_scraper import IndeedScraper
from .greenhouse_scraper import GreenhouseScraper, GREENHOUSE_COMPANIES


@dataclass
class JobSource:
    """Represents a job source with metadata."""
    name: str
    enabled: bool = True


class MultiSourceScraper:
    """
    Unified scraper that searches across multiple job platforms.
    
    Supported sources:
    - LinkedIn: General job listings
    - Indeed: General job listings  
    - Greenhouse: Direct company job boards (great for startups/tech companies)
    """

    SOURCES = {
        "linkedin": JobSource("LinkedIn", True),
        "indeed": JobSource("Indeed", True),
        "greenhouse": JobSource("Greenhouse", True),
    }

    def __init__(
        self,
        sources: list[str] = None,
        delay: float = 1.0,
        parallel: bool = True,
    ):
        """
        Initialize the multi-source scraper.
        
        Args:
            sources: List of source names to use. Default: all sources.
            delay: Delay between requests in seconds.
            parallel: Whether to search sources in parallel.
        """
        self.parallel = parallel
        self.scrapers = {}
        
        active_sources = sources if sources else list(self.SOURCES.keys())
        
        if "linkedin" in active_sources:
            self.scrapers["linkedin"] = LinkedInScraper(delay=delay)
        if "indeed" in active_sources:
            self.scrapers["indeed"] = IndeedScraper(delay=delay * 1.5)
        if "greenhouse" in active_sources:
            self.scrapers["greenhouse"] = GreenhouseScraper(delay=delay * 0.5)

    def _add_source_tag(self, job: Job, source: str) -> Job:
        """Add source information to job."""
        if not hasattr(job, 'source'):
            job.__dict__['source'] = source
        return job

    def _search_source(
        self,
        source_name: str,
        keyword: str,
        location: str,
        limit: int,
        **kwargs
    ) -> tuple[str, list[Job]]:
        """Search a single source and return results with source name."""
        scraper = self.scrapers.get(source_name)
        if not scraper:
            return source_name, []
        
        try:
            jobs = scraper.search(
                keyword=keyword,
                location=location,
                limit=limit,
                **kwargs
            )
            jobs = [self._add_source_tag(job, source_name) for job in jobs]
            return source_name, jobs
        except Exception as e:
            print(f"Error searching {source_name}: {e}")
            return source_name, []

    def search(
        self,
        keyword: str,
        location: str = "",
        date_posted: str = "",
        job_type: str = "",
        remote: str = "",
        experience: str = "",
        salary: str = "",
        sort_by: str = "",
        easy_apply: bool = False,
        under_10_applicants: bool = False,
        limit: int = 25,
        per_source_limit: int = None,
    ) -> dict[str, list[Job]]:
        """
        Search for jobs across all enabled sources.
        
        Args:
            keyword: Job title or keywords to search.
            location: City or region.
            date_posted: "24hr", "past week", or "past month".
            job_type: "full time", "part time", "contract", etc.
            remote: "on site", "remote", or "hybrid".
            experience: "entry level", "senior", etc.
            salary: Minimum salary filter.
            sort_by: "recent" or "relevant".
            easy_apply: Filter to Easy Apply jobs (LinkedIn only).
            under_10_applicants: Filter to jobs with under 10 applicants (LinkedIn only).
            limit: Total maximum number of jobs to return.
            per_source_limit: Max jobs per source. Default: limit / num_sources.
            
        Returns:
            Dictionary mapping source name to list of jobs.
        """
        if per_source_limit is None:
            per_source_limit = max(10, limit // len(self.scrapers))

        results = {}
        search_kwargs = {
            "date_posted": date_posted,
            "job_type": job_type,
            "remote": remote,
            "experience": experience,
            "salary": salary,
            "sort_by": sort_by,
            "easy_apply": easy_apply,
            "under_10_applicants": under_10_applicants,
        }

        if self.parallel and len(self.scrapers) > 1:
            with ThreadPoolExecutor(max_workers=len(self.scrapers)) as executor:
                futures = {
                    executor.submit(
                        self._search_source,
                        source_name,
                        keyword,
                        location,
                        per_source_limit,
                        **search_kwargs
                    ): source_name
                    for source_name in self.scrapers
                }
                
                for future in as_completed(futures):
                    source_name, jobs = future.result()
                    results[source_name] = jobs
        else:
            for source_name in self.scrapers:
                _, jobs = self._search_source(
                    source_name,
                    keyword,
                    location,
                    per_source_limit,
                    **search_kwargs
                )
                results[source_name] = jobs

        return results

    def search_combined(
        self,
        keyword: str,
        location: str = "",
        limit: int = 25,
        **kwargs
    ) -> list[Job]:
        """
        Search all sources and return a combined, deduplicated list.
        
        Jobs are interleaved from different sources for variety.
        
        Returns:
            Combined list of jobs from all sources.
        """
        results = self.search(keyword, location, limit=limit, **kwargs)
        
        combined = []
        seen_jobs = set()
        
        source_iterators = {
            source: iter(jobs) for source, jobs in results.items()
        }
        
        while len(combined) < limit and source_iterators:
            exhausted_sources = []
            
            for source, iterator in source_iterators.items():
                if len(combined) >= limit:
                    break
                    
                try:
                    job = next(iterator)
                    job_key = (
                        job.position.lower().strip(),
                        job.company.lower().strip(),
                    )
                    
                    if job_key not in seen_jobs:
                        seen_jobs.add(job_key)
                        combined.append(job)
                except StopIteration:
                    exhausted_sources.append(source)
            
            for source in exhausted_sources:
                del source_iterators[source]

        return combined

    def fetch_job_details(self, job: Job) -> Job:
        """
        Fetch full details for a job using the appropriate scraper.
        """
        source = getattr(job, 'source', None) or job.__dict__.get('source')
        
        if not source:
            if "linkedin.com" in job.job_url:
                source = "linkedin"
            elif "indeed.com" in job.job_url:
                source = "indeed"
            elif "greenhouse.io" in job.job_url:
                source = "greenhouse"

        if source and source in self.scrapers:
            return self.scrapers[source].fetch_job_details(job)
        
        return job

    def get_active_sources(self) -> list[str]:
        """Return list of currently active source names."""
        return list(self.scrapers.keys())

    def get_greenhouse_companies(self) -> list[str]:
        """Return list of available Greenhouse company slugs."""
        if "greenhouse" in self.scrapers:
            return self.scrapers["greenhouse"].get_available_companies()
        return []
