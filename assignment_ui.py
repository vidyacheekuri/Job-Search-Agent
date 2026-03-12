"""
Streamlit UI for the Job-Search-Agent assignment pipeline.

This UI wraps the CSV-based assignment agent in `assignment_agent.py` and
exposes:
- Dataset inspection
- Candidate profile + filtering + ranking
- Resume tailoring for a selected job
- Optional LLM reasoning about the tool sequence
"""

from __future__ import annotations

from dataclasses import asdict
from pathlib import Path
from typing import List

import streamlit as st

from assignment_agent import (
    CsvJob,
    DATA_PATH,
    build_sample_profile,
    filtering_tool,
    load_jobs_from_csv,
    ranking_tool,
    resume_tailoring_tool,
)
from linkedin_scraper.agent.profile import UserProfile
from linkedin_scraper.agent.ranker import RankedJob


def _jobs_to_dataframe(jobs: List[CsvJob]):
    """Convert CsvJob list to a pandas DataFrame-like structure for Streamlit."""
    import pandas as pd

    return pd.DataFrame(
        [
            {
                "Job Title": j.title,
                "Company": j.company,
                "Location": j.location,
                "Required Skills": j.required_skills,
                "Years Experience": j.years_experience,
                "URL": j.url,
            }
            for j in jobs
        ]
    )


def _build_profile_from_form(sample: UserProfile) -> UserProfile:
    """Create a UserProfile from Streamlit form inputs, based on a sample profile."""
    title = st.text_input("Target Title", value=sample.title)
    years_experience = st.number_input(
        "Years of experience", min_value=0, max_value=50, value=sample.years_experience
    )
    skills_text = st.text_input(
        "Core skills (comma-separated)", value=", ".join(sample.skills)
    )
    preferred_locations_text = st.text_input(
        "Preferred locations (comma-separated)",
        value=", ".join(sample.preferred_locations),
    )
    summary = st.text_area("Short summary", value=sample.summary, height=80)

    skills = [s.strip() for s in skills_text.split(",") if s.strip()]
    preferred_locations = [
        s.strip() for s in preferred_locations_text.split(",") if s.strip()
    ]

    profile_dict = asdict(sample)
    profile_dict.update(
        {
            "title": title,
            "years_experience": int(years_experience),
            "skills": skills,
            "preferred_locations": preferred_locations,
            "summary": summary,
        }
    )
    return UserProfile(**profile_dict)


def _render_dataset_page() -> None:
    st.header("Step 1 – Jobs Dataset (CSV)")
    path = DATA_PATH

    try:
        jobs = load_jobs_from_csv(path)
    except Exception as exc:  # noqa: BLE001
        st.error(
            f"Failed to load jobs from {path}.\n\n"
            f"Error: {exc}\n\n"
            "Make sure the CSV exists and matches the expected schema."
        )
        return

    st.success(f"Loaded {len(jobs)} jobs from `{path}`.")
    df = _jobs_to_dataframe(jobs)
    st.dataframe(df.head(15), use_container_width=True)


def _render_filter_rank_page() -> None:
    st.header("Step 2 – Candidate Profile + Filtering & Ranking")

    try:
        jobs = load_jobs_from_csv()
    except Exception as exc:  # noqa: BLE001
        st.error(
            f"Failed to load jobs from {DATA_PATH}.\n\n"
            f"Error: {exc}"
        )
        return

    sample = build_sample_profile()

    with st.form("profile_filter_rank_form"):
        st.subheader("Candidate Profile")
        profile = _build_profile_from_form(sample)
        top_n = st.slider(
            "Top N jobs to show",
            min_value=1,
            max_value=20,
            value=10,
            step=1,
        )
        submitted = st.form_submit_button("Run Filtering + Ranking")

    if not submitted:
        return

    with st.spinner("Running Filtering Tool..."):
        filtered = filtering_tool(jobs, profile)

    st.info(f"Jobs after filtering: {len(filtered)}")
    if not filtered:
        st.warning(
            "No jobs matched the rule-based filters. Try broadening locations or skills."
        )
        return

    with st.spinner("Running Ranking Tool..."):
        ranked: List[RankedJob] = ranking_tool(filtered, profile, top_n=top_n)

    if not ranked:
        st.warning("No jobs remained after ranking.")
        return

    st.subheader("Top Ranked Jobs")
    rows = []
    for rj in ranked:
        rows.append(
            {
                "Job Title": rj.job.position,
                "Company": rj.job.company,
                "Location": rj.job.location,
                "Score (%)": rj.score,
                "URL": rj.job.job_url,
            }
        )

    import pandas as pd

    st.dataframe(pd.DataFrame(rows), use_container_width=True)


def _render_resume_tailor_page() -> None:
    st.header("Step 3 – Resume Tailoring Tool")

    try:
        jobs = load_jobs_from_csv()
    except Exception as exc:  # noqa: BLE001
        st.error(
            f"Failed to load jobs from {DATA_PATH}.\n\n"
            f"Error: {exc}"
        )
        return

    sample = build_sample_profile()

    with st.form("resume_tailor_form"):
        st.subheader("Candidate Profile (used for tailoring)")
        profile = _build_profile_from_form(sample)

        st.subheader("Job Selection")
        job_options = [
            f"{j.title} – {j.company} ({j.location})" for j in jobs
        ]
        job_idx = st.selectbox(
            "Select a job from the CSV",
            options=list(range(len(job_options))),
            format_func=lambda i: job_options[i],
        )

        submitted = st.form_submit_button("Generate Tailored Resume Snippet")

    if not submitted:
        return

    selected_job = jobs[job_idx]

    # Convert CsvJob to RankedJob-like wrapper around scraper.Job
    from linkedin_scraper.scraper import Job as ScrapedJob
    from linkedin_scraper.agent.ranker import RankedJob

    scraped_job = ScrapedJob(
        position=selected_job.title,
        company=selected_job.company,
        company_logo=None,
        location=selected_job.location,
        date="",
        ago_time="",
        salary="",
        job_url=selected_job.url,
        description=selected_job.description,
        skills=[s.strip() for s in selected_job.required_skills.split(";") if s.strip()]
        or None,
    )
    ranked_wrapper = RankedJob(job=scraped_job, score=0.0, reasons=[])

    with st.spinner("Calling Resume Tailoring Tool..."):
        try:
            tailored_text = resume_tailoring_tool(
                profile, ranked_wrapper, use_openai=bool(st.secrets.get("OPENAI_API_KEY", "") or False)
            )
        except Exception as exc:  # noqa: BLE001
            st.error(
                "Resume tailoring failed.\n\n"
                f"Error: {exc}\n\n"
                "Check your OpenAI / Anthropic / Ollama configuration."
            )
            return

    st.subheader("Tailored Resume Output")
    st.code(tailored_text)


def main() -> None:
    st.set_page_config(
        page_title="Job-Search-Agent – Assignment UI",
        layout="wide",
    )
    st.title("Job-Search-Agent – Assignment UI")

    with st.sidebar:
        st.header("Navigation")
        page = st.radio(
            "Go to",
            options=[
                "Step 1 – Dataset",
                "Step 2 – Filter & Rank",
                "Step 3 – Resume Tailoring",
            ],
        )

    if page == "Step 1 – Dataset":
        _render_dataset_page()
    elif page == "Step 2 – Filter & Rank":
        _render_filter_rank_page()
    elif page == "Step 3 – Resume Tailoring":
        _render_resume_tailor_page()


if __name__ == "__main__":
    main()

