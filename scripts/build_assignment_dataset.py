"""Build assignment CSV dataset using LinkedInScraper.

This script uses the existing LinkedInScraper to fetch ~30 AI/ML jobs
and writes them into data/jobs_dataset.csv in the exact format required
by the AI Agent assignment PDF.

Columns:
- Job Title
- Company
- Location
- Required Skills
- Years of Experience Required
- Shortened Job Description (5–8 lines)
- URL
"""

from __future__ import annotations

import csv
import re
from pathlib import Path

from linkedin_scraper.scraper import LinkedInScraper, Job
from linkedin_scraper.agent.ranker import JobRanker


OUTPUT_PATH = Path(__file__).resolve().parents[1] / "data" / "jobs_dataset.csv"

# Multiple AI/ML-related keywords to broaden the dataset
AI_ML_KEYWORDS = [
    "AI Engineer",
    "Machine Learning Engineer",
    "ML Engineer",
    "Data Scientist",
    "Deep Learning Engineer",
    "Applied Scientist",
]


def shorten_description(text: str, max_chars: int = 800) -> str:
    """Shorten description to roughly 5–8 lines / reasonable length."""
    if not text:
        return ""
    text = text.replace("\r", " ").replace("\n", " ")
    text = " ".join(text.split())
    if len(text) <= max_chars:
        return text
    return text[: max_chars].rsplit(" ", 1)[0] + "..."


COMMON_SKILLS = [
    # Languages
    "python", "java", "c++", "c#", "scala", "r", "go", "rust", "sql",
    # ML / AI
    "machine learning", "deep learning", "nlp", "natural language processing",
    "computer vision", "reinforcement learning", "mlops",
    # Frameworks & libs
    "pytorch", "tensorflow", "keras", "scikit-learn", "sklearn",
    "xgboost", "lightgbm", "spark", "pandas", "numpy",
    # Tools / platforms
    "aws", "azure", "gcp", "docker", "kubernetes",
    "airflow", "mlflow", "databricks", "snowflake",
]


def extract_required_skills(job: Job) -> str:
    """Best-effort extraction of required skills from job.skills or description."""
    if job.skills:
        return "; ".join(sorted(set(job.skills)))

    text = f"{job.position} {job.description or ''}".lower()
    found = []
    for skill in COMMON_SKILLS:
        if skill in text:
            found.append(skill)

    # Deduplicate and keep a reasonable number
    found = sorted(set(found))
    return "; ".join(found[:15])


def extract_years_experience(job: Job) -> str:
    """
    Extract years of experience requirement from description/title.
    Returns a string like '3+' or '5' or '' if not found.
    """
    text = f"{job.position} {job.description or ''}".lower()
    # Examples: 3+ years, 5 years, 2 yrs, 7+ yrs
    match = re.search(r'(\d+)\s*\+?\s*(?:years?|yrs?)', text)
    if match:
        return match.group(1)

    # Heuristic mapping from seniority words to years
    if any(kw in text for kw in ["intern", "internship"]):
        return "0"
    if any(kw in text for kw in ["junior", "entry level", "entry-level", "associate"]):
        return "1"
    if any(kw in text for kw in ["mid-level", "mid level", "midlevel"]):
        return "3"
    if any(kw in text for kw in ["senior", "sr.", "sr "]):
        return "5"
    if any(kw in text for kw in ["staff", "lead", "principal"]):
        return "7"
    if any(kw in text for kw in ["director", "vp", "vice president", "head of"]):
        return "10"

    return ""


def main() -> None:
    scraper = LinkedInScraper(delay=1.0)

    # Prefer US jobs, but don't over-filter in code – we'll just fetch more
    location = "United States"
    target_count = 40  # fetch a bit more so that after filters we still have ~30

    print(f"Searching LinkedIn for ~{target_count} AI/ML-related jobs...")

    jobs_by_url: dict[str, Job] = {}

    for keyword in AI_ML_KEYWORDS:
        if len(jobs_by_url) >= target_count:
            break

        remaining = target_count - len(jobs_by_url)
        per_keyword_limit = max(5, remaining)

        print(f"  -> Searching '{keyword}' (limit {per_keyword_limit})")
        found_jobs: list[Job] = scraper.search(
            keyword=keyword,
            location=location,
            limit=per_keyword_limit,
        )

        for job in found_jobs:
            if job.job_url and job.job_url not in jobs_by_url:
                scraper.fetch_job_details(job)
                jobs_by_url[job.job_url] = job

        print(f"     Total unique jobs so far: {len(jobs_by_url)}")

        if len(jobs_by_url) >= target_count:
            break

    all_jobs: list[Job] = list(jobs_by_url.values())
    print(f"Collected {len(all_jobs)} unique AI/ML jobs before filters.")

    # Only exclude FAANG+; keep others so we end up with ~30 rows.
    enriched_jobs, _ = JobRanker.filter_faang_blacklist(all_jobs, log_decisions=False)
    print(f"After FAANG filter: {len(enriched_jobs)} jobs. Writing CSV...")

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    fieldnames = [
        "Job Title",
        "Company",
        "Location",
        "Required Skills",
        "Years of Experience Required",
        "Shortened Job Description (5–8 lines)",
        "URL",
    ]

    with OUTPUT_PATH.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

        for job in enriched_jobs:
            row = {
                "Job Title": job.position,
                "Company": job.company,
                "Location": job.location,
                "Required Skills": extract_required_skills(job),
                "Years of Experience Required": extract_years_experience(job),
                "Shortened Job Description (5–8 lines)": shorten_description(job.description or ""),
                "URL": job.job_url,
            }
            writer.writerow(row)

    print(f"Wrote {len(enriched_jobs)} jobs to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()

