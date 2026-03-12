"""Assignment Agent: LLM-based job filtering, ranking, and resume tailoring.

This script is focused on the AI for Engineers assignment requirements and uses
the CSV dataset at data/jobs_dataset.csv instead of live scraping.

It implements:
  - Filtering Tool
  - Ranking Tool
  - Resume Tailoring Tool
and a simple agent loop that can be driven by an LLM (OpenAI) when an
OPENAI_API_KEY is available, or fall back to heuristic behavior otherwise.
"""

from __future__ import annotations

import csv
import os
from dataclasses import dataclass
from pathlib import Path
from typing import List

from linkedin_scraper.agent.profile import UserProfile
from linkedin_scraper.agent.ranker import JobRanker, RankedJob
from linkedin_scraper.agent.resume_tailor import ResumeTailor


DATA_PATH = Path(__file__).resolve().parent / "data" / "jobs_dataset.csv"


@dataclass
class CsvJob:
    """Job row loaded from the assignment CSV dataset."""

    title: str
    company: str
    location: str
    required_skills: str
    years_experience: str
    description: str
    url: str


def load_jobs_from_csv(path: Path = DATA_PATH) -> List[CsvJob]:
    """Load jobs from the assignment CSV into CsvJob objects."""
    jobs: List[CsvJob] = []
    with path.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            jobs.append(
                CsvJob(
                    title=row.get("Job Title", "").strip(),
                    company=row.get("Company", "").strip(),
                    location=row.get("Location", "").strip(),
                    required_skills=row.get("Required Skills", "").strip(),
                    years_experience=row.get("Years of Experience Required", "").strip(),
                    description=row.get("Shortened Job Description (5–8 lines)", "").strip(),
                    url=row.get("URL", "").strip(),
                )
            )
    return jobs


# --------------------------- Tools for the assignment --------------------------- #

EXCLUDED_COMPANIES = {
    # Example company exclusion list for assignment (could be FAANG or others)
    "meta", "facebook", "amazon", "apple", "netflix", "google", "alphabet",
}


def filtering_tool(jobs: List[CsvJob], profile: UserProfile) -> List[CsvJob]:
    """Filtering Tool – rule-based filtering over the CSV dataset.

    Simple rules:
      - Keep jobs whose location roughly matches one of profile.preferred_locations
        (or keep all if none specified).
      - Keep jobs where required years <= profile.years_experience (if filled).
      - Keep jobs where there is at least one overlapping skill.
      - Exclude companies in EXCLUDED_COMPANIES.
    """
    preferred_locations = {loc.lower() for loc in profile.preferred_locations}
    profile_skills = {s.lower() for s in profile.get_all_skills()}

    filtered: List[CsvJob] = []
    for job in jobs:
        company_lower = job.company.lower()
        if any(ex in company_lower for ex in EXCLUDED_COMPANIES):
            continue
        # Location filter
        if preferred_locations:
            loc_lower = job.location.lower()
            if not any(pref in loc_lower for pref in preferred_locations):
                continue

        # Experience filter
        if job.years_experience.isdigit():
            required_years = int(job.years_experience)
            if profile.years_experience < required_years:
                continue

        # Skills overlap
        job_skills = {s.strip().lower() for s in job.required_skills.split(";") if s.strip()}
        if profile_skills and job_skills and not (profile_skills & job_skills):
            continue

        filtered.append(job)

    return filtered


def ranking_tool(jobs: List[CsvJob], profile: UserProfile, top_n: int = 10) -> List[RankedJob]:
    """Ranking Tool – score and rank CSV jobs using existing JobRanker logic.

    We convert CsvJob rows into linkedin_scraper.scraper.Job objects so we can
    reuse the ranking implementation for skills, location, experience, etc.
    """
    from linkedin_scraper.scraper import Job as ScrapedJob  # local import to avoid cycles

    job_ranker = JobRanker(profile)
    converted = []
    for j in jobs:
        converted.append(
            ScrapedJob(
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

    ranked = job_ranker.rank_jobs(converted, top_n=top_n)
    return ranked


def resume_tailoring_tool(profile: UserProfile, ranked_job: RankedJob, use_openai: bool = False) -> str:
    """Resume Tailoring Tool – generate a tailored resume summary + 2 bullets.

    For the assignment we can reuse ResumeTailor and then post-process its output
    to extract a short summary and highlight two experience bullet points.
    """
    tailor = ResumeTailor(use_openai=use_openai)
    result = tailor.tailor_resume(profile, ranked_job.job)

    # For the assignment deliverable: rewritten summary + exactly two bullets
    summary = result.summary.strip()

    # Use matched skills from RankedJob to ground the bullets
    key_skills = [s for s in ranked_job.matched_skills][:3]
    skill_phrase = ", ".join(key_skills) if key_skills else "core AI/ML skills"

    bullet_1 = f"Led end-to-end delivery of AI/ML features using {skill_phrase}, aligned with the target role."
    bullet_2 = "Improved model and data pipeline performance in environments similar to the selected job."

    formatted = [
        "=== Rewritten Professional Summary ===",
        summary,
        "",
        "=== Modified Experience Bullet Points (2) ===",
        f"- {bullet_1}",
        f"- {bullet_2}",
    ]
    return "\n".join(formatted)


# ------------------------------ Agent Orchestration ----------------------------- #

def print_llm_reasoning_trace(profile: UserProfile, jobs: List[CsvJob]) -> None:
    """Call an LLM (OpenAI, Claude, or Ollama) to explain which tools to use and why.

    Provider is chosen via the LLM_PROVIDER env var:
      - "openai"   (default if OPENAI_API_KEY is set)
      - "anthropic" (Claude, via ANTHROPIC_API_KEY)
      - "ollama"   (local model via Ollama HTTP API)
    """
    provider = os.environ.get("LLM_PROVIDER", "").lower()

    openai_key = os.environ.get("OPENAI_API_KEY")
    anthropic_key = os.environ.get("ANTHROPIC_API_KEY")

    # Auto-detect provider if not explicitly set
    if not provider:
        if openai_key:
            provider = "openai"
        elif anthropic_key:
            provider = "anthropic"
        else:
            provider = "ollama"  # assume local Ollama if nothing else

    system_msg = (
        "You are an AI job search agent that must decide which tools to call and in what order. "
        "Available tools:\n"
        "1) filtering_tool: filters jobs by location, skills, and experience years.\n"
        "2) ranking_tool: scores filtered jobs using skill, title, location, and recency.\n"
        "3) resume_tailoring_tool: generates a tailored resume summary and improves two bullets.\n"
        "You should reason step by step and output a short explanation of which tools you will call and why."
    )

    user_msg = (
        f"Candidate profile:\n"
        f"- Title: {profile.title}\n"
        f"- Years of experience: {profile.years_experience}\n"
        f"- Skills: {', '.join(profile.get_all_skills())}\n"
        f"- Preferred locations: {', '.join(profile.preferred_locations) or 'not specified'}\n"
        f"There are {len(jobs)} jobs in the CSV dataset. "
        "Explain which tools you will use, in what order, and what each contributes. "
        "Keep it under 8 sentences."
    )

    reasoning: str | None = None

    try:
        if provider == "openai" and openai_key:
            try:
                from openai import OpenAI
            except Exception:
                reasoning = None
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
                reasoning = None
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
                reasoning = None
            else:
                payload = {
                    "model": os.environ.get("OLLAMA_MODEL", "llama3"),
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

    if reasoning:
        print("\n=== LLM Reasoning Trace ===")
        print(reasoning.strip())
        print("=== End of LLM Reasoning Trace ===\n")


def run_agent(profile: UserProfile, use_openai: bool = False) -> None:
    """Run the full assignment pipeline end-to-end."""
    print("Loading CSV jobs from data/jobs_dataset.csv ...")
    jobs = load_jobs_from_csv()
    print(f"Loaded {len(jobs)} jobs from CSV.")

    # Step 0: ask LLM (if available) to explain which tools it will use.
    print_llm_reasoning_trace(profile, jobs)

    print("\n[1] Filtering Tool: applying rule-based filters...")
    filtered = filtering_tool(jobs, profile)
    print(f"Remaining after filtering: {len(filtered)} jobs.")

    print("\n[2] Ranking Tool: scoring jobs by profile match...")
    ranked = ranking_tool(filtered, profile, top_n=10)
    if not ranked:
        print("No jobs remained after ranking.")
        return

    print("Top matches (ranked list):")
    for i, rj in enumerate(ranked, start=1):
        print(f"{i}. {rj.job.position} at {rj.job.company} [{rj.score}%] – {rj.job.location}")

    # Explicitly highlight Top 3 jobs for the assignment
    print("\nTop 3 jobs by score:")
    for i, rj in enumerate(ranked[:3], start=1):
        print(f"#{i}: {rj.job.position} at {rj.job.company} [{rj.score}%] – {rj.job.location}")

    # Simple autonomy: pick the best job automatically
    best = ranked[0]
    print("\n[3] Agent decision: selecting best job automatically:")
    print(f"Chosen: {best.job.position} at {best.job.company} ({best.score}% match)")
    print(f"URL: {best.job.job_url}")

    print("\n[4] Resume Tailoring Tool: generating tailored summary + bullets...\n")
    tailored_text = resume_tailoring_tool(profile, best, use_openai=use_openai)
    print(tailored_text)


def build_sample_profile() -> UserProfile:
    """Quick helper to build a sample UserProfile for testing the agent."""
    return UserProfile(
        name="Sample Candidate",
        email="sample@example.com",
        phone="",
        location="USA",
        linkedin_url="",
        github_url="",
        portfolio_url="",
        title="AI / ML Engineer",
        summary="AI/ML engineer with experience in Python, deep learning, and MLOps.",
        years_experience=3,
        skills=["Python", "Machine Learning", "Deep Learning", "NLP", "AWS"],
        programming_languages=["Python"],
        frameworks=["PyTorch", "TensorFlow", "scikit-learn"],
        tools=["Docker", "Git"],
        experience=[],
        education=[],
        certifications=[],
        projects=[],
        target_roles=["AI Engineer", "Machine Learning Engineer"],
        target_companies=[],
        preferred_locations=["United States", "Remote"],
        remote_preference="flexible",
        min_salary=0,
    )


if __name__ == "__main__":
    use_openai_flag = bool(os.environ.get("OPENAI_API_KEY"))
    profile = build_sample_profile()
    run_agent(profile, use_openai=use_openai_flag)

