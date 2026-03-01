"""Greenhouse job board scraper module."""

import time
import random
import re
from dataclasses import dataclass, asdict
from typing import Optional
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

from .scraper import Job


# Popular tech companies using Greenhouse
GREENHOUSE_COMPANIES = {
    "airbnb": "https://boards.greenhouse.io/airbnb",
    "stripe": "https://boards.greenhouse.io/stripe",
    "discord": "https://boards.greenhouse.io/discord",
    "figma": "https://boards.greenhouse.io/figma",
    "notion": "https://boards.greenhouse.io/notion",
    "airtable": "https://boards.greenhouse.io/airtable",
    "vercel": "https://boards.greenhouse.io/vercel",
    "netlify": "https://boards.greenhouse.io/netlify",
    "linear": "https://boards.greenhouse.io/linear",
    "plaid": "https://boards.greenhouse.io/plaid",
    "ramp": "https://boards.greenhouse.io/ramp",
    "brex": "https://boards.greenhouse.io/brex",
    "flexport": "https://boards.greenhouse.io/flexport",
    "gusto": "https://boards.greenhouse.io/gusto",
    "lattice": "https://boards.greenhouse.io/lattice",
    "nerdwallet": "https://boards.greenhouse.io/nerdwallet",
    "coinbase": "https://boards.greenhouse.io/coinbase",
    "opensea": "https://boards.greenhouse.io/opensea",
    "reddit": "https://boards.greenhouse.io/reddit",
    "duolingo": "https://boards.greenhouse.io/duolingo",
    "calm": "https://boards.greenhouse.io/calm",
    "databricks": "https://boards.greenhouse.io/databricks",
    "hashicorp": "https://boards.greenhouse.io/hashicorp",
    "gitlab": "https://boards.greenhouse.io/gitlab",
    "mongodb": "https://boards.greenhouse.io/mongodb",
    "elastic": "https://boards.greenhouse.io/elastic",
    "cockroachlabs": "https://boards.greenhouse.io/cockroachlabs",
    "snowflake": "https://boards.greenhouse.io/snowflake",
    "dbt": "https://boards.greenhouse.io/daboratory",
    "amplitude": "https://boards.greenhouse.io/amplitude",
    "mixpanel": "https://boards.greenhouse.io/mixpanel",
    "segment": "https://boards.greenhouse.io/segment",
    "twilio": "https://boards.greenhouse.io/twilio",
    "sendgrid": "https://boards.greenhouse.io/sendgrid",
    "zapier": "https://boards.greenhouse.io/zapier",
    "zoom": "https://boards.greenhouse.io/zoom",
    "hubspot": "https://boards.greenhouse.io/hubspot",
    "intercom": "https://boards.greenhouse.io/intercom",
    "drift": "https://boards.greenhouse.io/drift",
    "pagerduty": "https://boards.greenhouse.io/pagerduty",
    "splunk": "https://boards.greenhouse.io/splunk",
    "datadog": "https://boards.greenhouse.io/datadog",
    "newrelic": "https://boards.greenhouse.io/newrelic",
    "sumo": "https://boards.greenhouse.io/sumologic",
    "okta": "https://boards.greenhouse.io/okta",
    "auth0": "https://boards.greenhouse.io/auth0",
    "crowdstrike": "https://boards.greenhouse.io/crowdstrike",
    "anthropic": "https://boards.greenhouse.io/anthropic",
    "openai": "https://boards.greenhouse.io/openai",
    "cohere": "https://boards.greenhouse.io/cohere",
    "huggingface": "https://boards.greenhouse.io/huggingface",
    "stability": "https://boards.greenhouse.io/stability",
    "midjourney": "https://boards.greenhouse.io/midjourney",
    "anyscale": "https://boards.greenhouse.io/anyscale",
    "wandb": "https://boards.greenhouse.io/wandb",
    "scale": "https://boards.greenhouse.io/scaleai",
    "labelbox": "https://boards.greenhouse.io/labelbox",
}


class GreenhouseScraper:
    """Scraper for Greenhouse job boards."""

    HEADERS = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
    }

    def __init__(self, delay: float = 0.5):
        """
        Initialize the scraper.
        
        Args:
            delay: Minimum delay between requests in seconds.
        """
        self.delay = delay
        self.session = requests.Session()
        self.session.headers.update(self.HEADERS)

    def _scrape_company_board(
        self, 
        company_name: str, 
        board_url: str, 
        keyword: str = "",
        location: str = "",
    ) -> list[Job]:
        """Scrape jobs from a single company's Greenhouse board."""
        jobs = []
        
        try:
            response = self.session.get(board_url, timeout=10)
            response.raise_for_status()
        except requests.RequestException:
            return jobs

        soup = BeautifulSoup(response.text, "lxml")

        job_sections = soup.find_all("section", class_="level-0")
        if not job_sections:
            job_sections = soup.find_all("div", class_="opening")

        for section in job_sections:
            openings = section.find_all("div", class_="opening")
            if not openings:
                openings = [section] if section.find("a") else []
            
            for opening in openings:
                try:
                    link = opening.find("a")
                    if not link:
                        continue
                    
                    position = link.get_text(strip=True)
                    job_url = link.get("href", "")
                    if job_url and not job_url.startswith("http"):
                        job_url = urljoin(board_url, job_url)

                    location_elem = opening.find("span", class_="location")
                    job_location = location_elem.get_text(strip=True) if location_elem else ""

                    if keyword:
                        keyword_lower = keyword.lower()
                        if keyword_lower not in position.lower() and keyword_lower not in job_location.lower():
                            continue

                    if location:
                        location_lower = location.lower()
                        if location_lower not in job_location.lower() and "remote" not in job_location.lower():
                            continue

                    job = Job(
                        position=position,
                        company=company_name.title(),
                        company_logo=None,
                        location=job_location,
                        date="",
                        ago_time="",
                        salary="",
                        job_url=job_url,
                    )
                    jobs.append(job)
                except Exception:
                    continue

        return jobs

    def _scrape_greenhouse_api(
        self,
        company_slug: str,
        keyword: str = "",
        location: str = "",
    ) -> list[Job]:
        """Try to scrape using Greenhouse's JSON API."""
        jobs = []
        api_url = f"https://boards-api.greenhouse.io/v1/boards/{company_slug}/jobs"
        
        try:
            response = self.session.get(api_url, timeout=10)
            if response.status_code != 200:
                return jobs
            
            data = response.json()
            job_list = data.get("jobs", [])
            
            for job_data in job_list:
                position = job_data.get("title", "")
                job_location = job_data.get("location", {}).get("name", "")
                job_id = job_data.get("id", "")
                job_url = f"https://boards.greenhouse.io/{company_slug}/jobs/{job_id}"

                if keyword:
                    keyword_lower = keyword.lower()
                    if keyword_lower not in position.lower():
                        continue

                if location:
                    location_lower = location.lower()
                    if location_lower not in job_location.lower() and "remote" not in job_location.lower():
                        continue

                job = Job(
                    position=position,
                    company=company_slug.title(),
                    company_logo=None,
                    location=job_location,
                    date="",
                    ago_time="",
                    salary="",
                    job_url=job_url,
                )
                jobs.append(job)
        except Exception:
            pass

        return jobs

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

        description_elem = soup.find("div", id="content")
        if not description_elem:
            description_elem = soup.find("div", class_="content")
        if description_elem:
            job.description = description_elem.get_text(separator="\n", strip=True)

        time.sleep(self.delay + random.uniform(0, 0.2))
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
        companies: list[str] = None,
    ) -> list[Job]:
        """
        Search for jobs on Greenhouse job boards.
        
        Args:
            keyword: Job title or keywords to search.
            location: City or region.
            date_posted: Not supported (ignored).
            job_type: Not supported (ignored).
            remote: Filter for remote if "remote".
            experience: Not supported (ignored).
            salary: Not supported (ignored).
            sort_by: Not supported (ignored).
            easy_apply: Not supported (ignored).
            under_10_applicants: Not supported (ignored).
            limit: Maximum number of jobs to return.
            companies: List of company slugs to search. If None, searches all known companies.
            
        Returns:
            List of Job objects.
        """
        all_jobs: list[Job] = []
        
        target_companies = companies if companies else list(GREENHOUSE_COMPANIES.keys())
        
        ai_ml_keywords = ["ai", "ml", "machine learning", "deep learning", "llm", 
                          "data scientist", "artificial intelligence", "nlp", "computer vision"]
        
        is_ai_search = any(kw in keyword.lower() for kw in ai_ml_keywords)
        if is_ai_search:
            priority_companies = ["anthropic", "openai", "cohere", "huggingface", "stability",
                                  "anyscale", "wandb", "scale", "labelbox", "databricks"]
            other_companies = [c for c in target_companies if c not in priority_companies]
            target_companies = [c for c in priority_companies if c in target_companies] + other_companies

        for company_slug in target_companies:
            if len(all_jobs) >= limit:
                break

            jobs = self._scrape_greenhouse_api(company_slug, keyword, location)
            
            if not jobs and company_slug in GREENHOUSE_COMPANIES:
                jobs = self._scrape_company_board(
                    company_slug,
                    GREENHOUSE_COMPANIES[company_slug],
                    keyword,
                    location
                )

            if remote and remote.lower() == "remote":
                jobs = [j for j in jobs if "remote" in j.location.lower()]

            all_jobs.extend(jobs)
            time.sleep(self.delay + random.uniform(0, 0.3))

        return all_jobs[:limit]

    def get_available_companies(self) -> list[str]:
        """Return list of available company slugs."""
        return list(GREENHOUSE_COMPANIES.keys())

    def add_company(self, slug: str, board_url: str = None) -> None:
        """Add a company to the scraping list."""
        if board_url is None:
            board_url = f"https://boards.greenhouse.io/{slug}"
        GREENHOUSE_COMPANIES[slug] = board_url
