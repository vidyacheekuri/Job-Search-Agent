"""Indeed job scraper module."""

import time
import random
import re
from dataclasses import dataclass, asdict
from typing import Optional
from urllib.parse import urlencode, quote_plus

import requests
from bs4 import BeautifulSoup

from .scraper import Job


class IndeedScraper:
    """Scraper for Indeed job listings."""

    BASE_URL = "https://www.indeed.com/jobs"

    DATE_POSTED_MAP = {
        "24hr": "1",
        "past week": "7",
        "past month": "30",
    }

    JOB_TYPE_MAP = {
        "full time": "fulltime",
        "full-time": "fulltime",
        "part time": "parttime",
        "part-time": "parttime",
        "contract": "contract",
        "temporary": "temporary",
        "internship": "internship",
    }

    EXPERIENCE_MAP = {
        "entry level": "entry_level",
        "entry-level": "entry_level",
        "mid level": "mid_level",
        "mid-level": "mid_level",
        "senior": "senior_level",
    }

    HEADERS = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
    }

    def __init__(self, delay: float = 1.5):
        """
        Initialize the scraper.
        
        Args:
            delay: Minimum delay between requests in seconds.
        """
        self.delay = delay
        self.session = requests.Session()
        self.session.headers.update(self.HEADERS)

    def _build_url(
        self,
        keyword: str,
        location: str = "",
        date_posted: str = "",
        job_type: str = "",
        remote: str = "",
        experience: str = "",
        salary: str = "",
        sort_by: str = "",
        start: int = 0,
    ) -> str:
        """Build the Indeed jobs search URL with query parameters."""
        params = {
            "q": keyword,
            "start": start,
        }

        if location:
            params["l"] = location

        if date_posted:
            date_key = date_posted.lower()
            if date_key in self.DATE_POSTED_MAP:
                params["fromage"] = self.DATE_POSTED_MAP[date_key]

        if job_type:
            job_key = job_type.lower()
            if job_key in self.JOB_TYPE_MAP:
                params["jt"] = self.JOB_TYPE_MAP[job_key]

        if remote and remote.lower() == "remote":
            params["remotejob"] = "1"

        if experience:
            exp_key = experience.lower()
            if exp_key in self.EXPERIENCE_MAP:
                params["explvl"] = self.EXPERIENCE_MAP[exp_key]

        if sort_by and sort_by.lower() == "recent":
            params["sort"] = "date"

        return f"{self.BASE_URL}?{urlencode(params)}"

    def _parse_job_card(self, card: BeautifulSoup) -> Optional[Job]:
        """Parse a single job card element into a Job object."""
        try:
            title_elem = card.find("h2", class_="jobTitle")
            if not title_elem:
                title_elem = card.find("a", {"data-jk": True})
            position = ""
            if title_elem:
                span = title_elem.find("span")
                position = span.get_text(strip=True) if span else title_elem.get_text(strip=True)

            company_elem = card.find("span", {"data-testid": "company-name"})
            if not company_elem:
                company_elem = card.find("span", class_="companyName")
            company = company_elem.get_text(strip=True) if company_elem else ""

            location_elem = card.find("div", {"data-testid": "text-location"})
            if not location_elem:
                location_elem = card.find("div", class_="companyLocation")
            location = location_elem.get_text(strip=True) if location_elem else ""

            date_elem = card.find("span", class_="date")
            if not date_elem:
                date_elem = card.find("span", {"data-testid": "myJobsStateDate"})
            ago_time = date_elem.get_text(strip=True) if date_elem else ""
            ago_time = ago_time.replace("Posted", "").replace("Employer", "").strip()

            salary_elem = card.find("div", class_="salary-snippet-container")
            if not salary_elem:
                salary_elem = card.find("div", {"data-testid": "attribute_snippet_testid"})
            salary = ""
            if salary_elem:
                salary_text = salary_elem.get_text(strip=True)
                if "$" in salary_text or "year" in salary_text.lower() or "hour" in salary_text.lower():
                    salary = salary_text

            job_id = card.get("data-jk", "")
            if not job_id:
                link = card.find("a", {"data-jk": True})
                job_id = link.get("data-jk", "") if link else ""
            
            job_url = f"https://www.indeed.com/viewjob?jk={job_id}" if job_id else ""

            if not position or not company:
                return None

            return Job(
                position=position,
                company=company,
                company_logo=None,
                location=location,
                date="",
                ago_time=ago_time,
                salary=salary,
                job_url=job_url,
            )
        except Exception:
            return None

    def fetch_job_details(self, job: Job) -> Job:
        """
        Fetch full job details from the job page.
        """
        if not job.job_url:
            return job

        try:
            response = self.session.get(job.job_url, timeout=10)
            response.raise_for_status()
        except requests.RequestException:
            return job

        soup = BeautifulSoup(response.text, "lxml")

        description_elem = soup.find("div", id="jobDescriptionText")
        if description_elem:
            job.description = description_elem.get_text(separator="\n", strip=True)

        time.sleep(self.delay + random.uniform(0, 0.3))
        return job

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
    ) -> list[Job]:
        """
        Search for jobs on Indeed.
        
        Args:
            keyword: Job title or keywords to search.
            location: City or region.
            date_posted: "24hr", "past week", or "past month".
            job_type: "full time", "part time", "contract", etc.
            remote: "remote" to filter remote jobs.
            experience: "entry level", "mid level", "senior".
            salary: Minimum salary filter (not fully supported).
            sort_by: "recent" or "relevant".
            easy_apply: Not supported on Indeed (ignored).
            under_10_applicants: Not supported on Indeed (ignored).
            limit: Maximum number of jobs to return.
            
        Returns:
            List of Job objects.
        """
        jobs: list[Job] = []
        start = 0
        page_size = 15

        while len(jobs) < limit:
            url = self._build_url(
                keyword=keyword,
                location=location,
                date_posted=date_posted,
                job_type=job_type,
                remote=remote,
                experience=experience,
                salary=salary,
                sort_by=sort_by,
                start=start,
            )

            try:
                response = self.session.get(url, timeout=10)
                response.raise_for_status()
            except requests.RequestException:
                break

            soup = BeautifulSoup(response.text, "lxml")
            
            cards = soup.find_all("div", class_="job_seen_beacon")
            if not cards:
                cards = soup.find_all("div", class_="jobsearch-SerpJobCard")
            if not cards:
                cards = soup.find_all("div", {"data-jk": True})

            if not cards:
                break

            for card in cards:
                if len(jobs) >= limit:
                    break
                job = self._parse_job_card(card)
                if job:
                    jobs.append(job)

            start += page_size
            time.sleep(self.delay + random.uniform(0, 0.5))

        return jobs
