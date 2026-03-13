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
from linkedin_scraper.agent.llm_tool_agent import run_llm_tool_agent


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


def filtering_tool(
    jobs: List[CsvJob],
    profile: UserProfile,
    remote_only: bool = False,
) -> List[CsvJob]:
    """Filtering Tool – rule-based filtering over the CSV dataset.

    Implements the following rules (for report / assignment):

    1. Location preference: Keep jobs whose location matches one of profile.preferred_locations
       (e.g. "United States", "Remote"). If none specified, all locations pass.

    2. Experience limit: Keep only jobs where required years <= profile.years_experience.
       If the job lists a numeric requirement (e.g. "3" years), the candidate must meet it.

    3. Company exclusion: Exclude companies in EXCLUDED_COMPANIES (e.g. FAANG: Meta, Facebook,
       Amazon, Apple, Netflix, Google, Alphabet).

    4. Remote-only filter (optional): If remote_only=True or profile.remote_preference == "remote",
       keep only jobs whose location string contains "remote".
    """
    preferred_locations = {loc.lower() for loc in profile.preferred_locations}
    profile_skills = {s.lower() for s in profile.get_all_skills()}
    apply_remote_only = remote_only or (profile.remote_preference or "").lower() == "remote"

    filtered: List[CsvJob] = []
    for job in jobs:
        # Rule: Company exclusion
        company_lower = job.company.lower()
        if any(ex in company_lower for ex in EXCLUDED_COMPANIES):
            continue

        # Rule: Remote-only (optional)
        if apply_remote_only:
            if "remote" not in (job.location or "").lower():
                continue

        # Rule: Location preference
        if preferred_locations:
            loc_lower = (job.location or "").lower()
            if not any(pref in loc_lower for pref in preferred_locations):
                continue

        # Rule: Experience limit
        if job.years_experience.isdigit():
            required_years = int(job.years_experience)
            if profile.years_experience < required_years:
                continue

        # Skills overlap (ensures at least one skill match)
        job_skills = {s.strip().lower() for s in job.required_skills.split(";") if s.strip()}
        if profile_skills and job_skills and not (profile_skills & job_skills):
            continue

        filtered.append(job)

    return filtered


def ranking_tool(jobs: List[CsvJob], profile: UserProfile, top_n: int = 10) -> List[RankedJob]:
    """Ranking Tool – score and rank jobs. Outputs a ranked list with clear scores.

    Assignment requirements:
    - Assigns scores based on skill matching (profile vs job skills).
    - Considers experience alignment (profile years vs job requirement).
    - Optionally considers location match (preferred locations vs job location).
    - Returns a ranked list with clear scores (0–100 per job).
    Display: show ranked job list with scores and clearly show Top 3 jobs.
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
    """Resume Tailoring Tool – for the top-ranked job only.

    Assignment requirements:
    - Tailor for only the top-ranked job (caller passes that job).
    - Rewrite the Professional Summary.
    - Modify exactly 2 experience bullet points (from profile, tailored to the job).
    - Highlight aligned skills.
    - Do NOT regenerate the entire resume; only summary + 2 bullets are modified.
    """
    tailor = ResumeTailor(use_openai=use_openai)
    result = tailor.tailor_resume(profile, ranked_job.job)

    summary = result.summary.strip()
    aligned_skills = list(ranked_job.matched_skills)[:10]
    key_skills = aligned_skills[:3]
    skill_phrase = ", ".join(key_skills) if key_skills else "core AI/ML skills"

    # Exactly 2 modified experience bullets: base on profile experience, tailor to job
    two_bullets = _get_two_modified_bullets(profile, ranked_job, skill_phrase)

    formatted = [
        "=== Rewritten Professional Summary ===",
        summary,
        "",
        "=== Highlight Aligned Skills ===",
        ", ".join(aligned_skills) if aligned_skills else "—",
        "",
        "=== Modified Experience Bullet Points (exactly 2) ===",
        f"- {two_bullets[0]}",
        f"- {two_bullets[1]}",
        "",
        "(Rest of resume unchanged; only summary and these 2 bullets were modified.)",
    ]
    return "\n".join(formatted)


def get_two_modified_bullets(
    profile: UserProfile,
    job: "Job",
    matched_skills: List[str],
) -> List[str]:
    """Produce exactly 2 experience bullet points modified for the job (from profile experience).

    Used by both assignment_agent and the main API so resume tailoring is consistent app-wide.
    """
    job_position = getattr(job, "position", None) or ""
    keywords = set(s.lower() for s in matched_skills)
    skill_phrase = ", ".join(matched_skills[:3]) if matched_skills else "core AI/ML skills"
    scored: List[tuple[int, str]] = []
    for exp in profile.experience:
        for h in exp.get("highlights", []):
            if not h.strip():
                continue
            h_lower = h.lower()
            relevance = sum(1 for kw in keywords if kw in h_lower)
            scored.append((relevance, h.strip()))
    scored.sort(key=lambda x: (-x[0], x[1]))
    bullets_from_profile = [h for _, h in scored]
    if len(bullets_from_profile) >= 2:
        b1, b2 = bullets_from_profile[0], bullets_from_profile[1]
        if not any(b1.lower().startswith(v.lower()) for v in ("Led", "Developed", "Implemented", "Built", "Designed")):
            b1 = "Led " + b1[0].lower() + b1[1:] if len(b1) > 1 else "Led " + b1
        if not any(b2.lower().startswith(v.lower()) for v in ("Improved", "Delivered", "Scaled", "Reduced", "Increased")):
            b2 = "Improved " + b2[0].lower() + b2[1:] if len(b2) > 1 else "Improved " + b2
        return [b1, b2]
    if len(bullets_from_profile) == 1:
        b1 = bullets_from_profile[0]
        if not any(b1.lower().startswith(v.lower()) for v in ("Led", "Developed", "Implemented")):
            b1 = "Led " + b1[0].lower() + b1[1:] if len(b1) > 1 else "Led " + b1
        return [b1, f"Applied {skill_phrase} to deliver outcomes aligned with {job_position or 'target role'}."]
    return [
        f"Led delivery of AI/ML solutions using {skill_phrase}, aligned with the target role.",
        f"Improved model and pipeline performance; experience relevant to {job_position or 'this position'}.",
    ]


def _get_two_modified_bullets(profile: UserProfile, ranked_job: RankedJob, skill_phrase: str) -> List[str]:
    """Produce exactly 2 experience bullet points modified for the job (from profile experience)."""
    return get_two_modified_bullets(profile, ranked_job.job, list(ranked_job.matched_skills))


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


def run_agent_llm_driven(profile: UserProfile, jobs: List[CsvJob], use_openai: bool = False) -> bool:
    """
    Run the agent with LLM decision-making: the model decides which tool to call and in what order
    (assignment: avoid hard-coded scripts without LLM decision-making).
    Returns True if the LLM completed the workflow via tool calls; False to fall back to fixed pipeline.
    """
    profile_summary = (
        f"Title: {profile.title}, Years: {profile.years_experience}, "
        f"Skills: {', '.join(profile.get_all_skills()[:12])}, "
        f"Locations: {', '.join(profile.preferred_locations) or 'Any'}."
    )
    state: dict = {"filtered": None, "ranked": None, "tailored": None}

    def execute_tool(tool_name: str, arguments: dict) -> str:
        if tool_name == "filtering_tool":
            state["filtered"] = filtering_tool(jobs, profile)
            return f"Filtered to {len(state['filtered'])} jobs."
        if tool_name == "ranking_tool":
            if not state.get("filtered"):
                return "Error: call filtering_tool first."
            top_n = arguments.get("top_n", 10)
            state["ranked"] = ranking_tool(state["filtered"], profile, top_n=top_n)
            top3 = state["ranked"][:3]
            return f"Ranked {len(state['ranked'])} jobs. Top 3: " + "; ".join(
                f"{rj.job.position} at {rj.job.company} ({rj.score}%)" for rj in top3
            )
        if tool_name == "resume_tailoring_tool":
            if not state.get("ranked"):
                return "Error: call ranking_tool first."
            idx = max(0, int(arguments.get("job_rank", 1)) - 1)
            best = state["ranked"][idx]
            state["tailored"] = resume_tailoring_tool(profile, best, use_openai=use_openai)
            return f"Tailored resume generated for {best.job.position} at {best.job.company}."
        return "Unknown tool."

    reasoning, success = run_llm_tool_agent(
        profile_summary=profile_summary,
        job_count=len(jobs),
        execute_tool=execute_tool,
    )
    print("\n=== LLM Reasoning Trace (tool decisions) ===")
    print(reasoning.strip())
    print("=== End of LLM Reasoning Trace ===\n")
    if success and state.get("ranked") and state.get("tailored") is not None:
        ranked = state["ranked"]
        print("Top matches (ranked list):")
        for i, rj in enumerate(ranked, start=1):
            print(f"{i}. {rj.job.position} at {rj.job.company} [{rj.score}%] – {rj.job.location}")
        print("\nTop 3 jobs by score:")
        for i, rj in enumerate(ranked[:3], start=1):
            print(f"#{i}: {rj.job.position} at {rj.job.company} [{rj.score}%] – {rj.job.location}")
        print("\n[Resume Tailoring Tool output]\n")
        print(state["tailored"])
        return True
    return False


def run_agent(profile: UserProfile, use_openai: bool = False) -> None:
    """Run the full assignment pipeline. Uses LLM-driven tool calling when OpenAI is available."""
    print("Loading CSV jobs from data/jobs_dataset.csv ...")
    jobs = load_jobs_from_csv()
    print(f"Loaded {len(jobs)} jobs from CSV.")

    if os.environ.get("OPENAI_API_KEY") or os.environ.get("ANTHROPIC_API_KEY"):
        if run_agent_llm_driven(profile, jobs, use_openai=use_openai):
            return
        print("(Falling back to fixed pipeline after LLM agent did not complete.)\n")

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

    print("\nTop 3 jobs by score:")
    for i, rj in enumerate(ranked[:3], start=1):
        print(f"#{i}: {rj.job.position} at {rj.job.company} [{rj.score}%] – {rj.job.location}")

    best = ranked[0]
    print("\n[3] Agent decision: selecting best job:")
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

