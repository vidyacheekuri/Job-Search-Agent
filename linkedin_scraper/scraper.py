"""LinkedIn job scraper module."""

import time
import random
from dataclasses import dataclass, asdict
from typing import Optional
from urllib.parse import urlencode

import requests
from bs4 import BeautifulSoup


@dataclass
class Job:
    """Represents a LinkedIn job listing."""
    position: str
    company: str
    company_logo: Optional[str]
    location: str
    date: str
    ago_time: str
    salary: str
    job_url: str

    def to_dict(self) -> dict:
        return asdict(self)


class LinkedInScraper:
    """Scraper for LinkedIn public job listings."""

    BASE_URL = "https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search"

    DATE_POSTED_MAP = {
        "24hr": "r86400",
        "past week": "r604800",
        "past month": "r2592000",
    }

    JOB_TYPE_MAP = {
        "full time": "F",
        "full-time": "F",
        "part time": "P",
        "part-time": "P",
        "contract": "C",
        "temporary": "T",
        "volunteer": "V",
        "internship": "I",
    }

    REMOTE_MAP = {
        "on site": "1",
        "on-site": "1",
        "remote": "2",
        "hybrid": "3",
    }

    EXPERIENCE_MAP = {
        "internship": "1",
        "entry level": "2",
        "entry-level": "2",
        "associate": "3",
        "senior": "4",
        "director": "5",
        "executive": "6",
    }

    HEADERS = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
    }

    def __init__(self, delay: float = 1.0):
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
        """Build the LinkedIn jobs search URL with query parameters."""
        params = {
            "keywords": keyword,
            "location": location,
            "start": start,
        }

        if date_posted:
            date_key = date_posted.lower()
            if date_key in self.DATE_POSTED_MAP:
                params["f_TPR"] = self.DATE_POSTED_MAP[date_key]

        if job_type:
            job_key = job_type.lower()
            if job_key in self.JOB_TYPE_MAP:
                params["f_JT"] = self.JOB_TYPE_MAP[job_key]

        if remote:
            remote_key = remote.lower()
            if remote_key in self.REMOTE_MAP:
                params["f_WT"] = self.REMOTE_MAP[remote_key]

        if experience:
            exp_key = experience.lower()
            if exp_key in self.EXPERIENCE_MAP:
                params["f_E"] = self.EXPERIENCE_MAP[exp_key]

        if salary:
            params["f_SB2"] = salary

        if sort_by:
            params["sortBy"] = "DD" if sort_by.lower() == "recent" else "R"

        return f"{self.BASE_URL}?{urlencode(params)}"

    def _parse_job_card(self, card: BeautifulSoup) -> Optional[Job]:
        """Parse a single job card element into a Job object."""
        try:
            position_elem = card.find("h3", class_="base-search-card__title")
            position = position_elem.get_text(strip=True) if position_elem else ""

            company_elem = card.find("h4", class_="base-search-card__subtitle")
            company = company_elem.get_text(strip=True) if company_elem else ""

            logo_elem = card.find("img", class_="artdeco-entity-image")
            company_logo = logo_elem.get("src") if logo_elem else None

            location_elem = card.find("span", class_="job-search-card__location")
            location = location_elem.get_text(strip=True) if location_elem else ""

            time_elem = card.find("time", class_="job-search-card__listdate")
            if not time_elem:
                time_elem = card.find("time", class_="job-search-card__listdate--new")
            
            date = time_elem.get("datetime", "") if time_elem else ""
            ago_time = time_elem.get_text(strip=True) if time_elem else ""

            salary_elem = card.find("span", class_="job-search-card__salary-info")
            salary = salary_elem.get_text(strip=True) if salary_elem else ""

            link_elem = card.find("a", class_="base-card__full-link")
            job_url = link_elem.get("href", "") if link_elem else ""

            if not position or not company:
                return None

            return Job(
                position=position,
                company=company,
                company_logo=company_logo,
                location=location,
                date=date,
                ago_time=ago_time,
                salary=salary,
                job_url=job_url,
            )
        except Exception:
            return None

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
        limit: int = 25,
    ) -> list[Job]:
        """
        Search for jobs on LinkedIn.
        
        Args:
            keyword: Job title or keywords to search.
            location: City or region.
            date_posted: "24hr", "past week", or "past month".
            job_type: "full time", "part time", "contract", etc.
            remote: "on site", "remote", or "hybrid".
            experience: "entry level", "senior", etc.
            salary: Minimum salary filter.
            sort_by: "recent" or "relevant".
            limit: Maximum number of jobs to return.
            
        Returns:
            List of Job objects.
        """
        jobs: list[Job] = []
        start = 0
        page_size = 25

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
            except requests.RequestException as e:
                break

            soup = BeautifulSoup(response.text, "lxml")
            cards = soup.find_all("div", class_="base-card")

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
