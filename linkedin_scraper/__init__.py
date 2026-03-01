"""LinkedIn Job Scraper - A CLI tool for scraping LinkedIn job listings."""

__version__ = "0.2.0"

from .scraper import Job, LinkedInScraper
from .indeed_scraper import IndeedScraper
from .greenhouse_scraper import GreenhouseScraper, GREENHOUSE_COMPANIES
from .multi_scraper import MultiSourceScraper

__all__ = [
    "Job",
    "LinkedInScraper",
    "IndeedScraper",
    "GreenhouseScraper",
    "GREENHOUSE_COMPANIES",
    "MultiSourceScraper",
]
