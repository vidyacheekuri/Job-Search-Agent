# Assignment Rubric Checklist – Triple-Checked

Use this to confirm every requirement is met before submission. Items are marked ✅ (done), ⚠️ (partial / note), or ❌ (gap).

---

## Grading Criteria

| Criterion | Weight | Status | Evidence |
|----------|--------|--------|----------|
| **Agent Architecture Design** | 25% | ✅ | Pipeline: Profile → Analyze dataset → Filter → Rank → Select best → Tailor. Three callable tools (filter, rank, tailor). `llm_tool_agent.py` + `assignment_agent.py` + API `/api/agent/offline`. |
| **Tool Implementation (Filtering + Ranking)** | 20% | ✅ | Filtering: `filtering_tool` / `_filter_csv_jobs` (location, experience, company exclusion, remote-only). Ranking: `ranking_tool` / `_rank_csv_jobs` + `JobRanker` (skill, title, location, experience). |
| **LLM Reasoning & Autonomy** | 20% | ✅* | With **OpenAI** or **Anthropic**: LLM decides which tool to call via function/tool calling; reasoning trace returned. *With **Ollama only**: single reasoning message shown but execution is fixed pipeline (no tool-calling). For full marks use an API key. |
| **Prompt Engineering Quality** | 15% | ✅ | System/user prompts in `llm_tool_agent.py` describe tools and order; tool descriptions state purpose and when to call. |
| **Resume Tailoring Quality** | 10% | ✅ | Summary rewritten; exactly 2 modified bullets; aligned skills highlighted; no full-resume regeneration. `resume_tailoring_tool`, `get_two_modified_bullets`, `ResumeTailor`. |
| **Code Quality & Documentation** | 5% | ✅ | README, `docs/FILTERING_RULES.md`, `docs/RANKING_SYSTEM.md`, `docs/RESUME_TAILORING_REQUIREMENTS.md`, docstrings on tools. |
| **Report Clarity & Organization** | 5% | ⚠️ | `docs/REPORT_TEMPLATE.md` exists. **You** must write the actual report (intro, design, filtering/ranking/tailoring explanation, results, conclusions) and optionally remove/adapt the “Bias and Ethics” section if your assignment no longer requires it. |

---

## Required Pipeline

**Your agent must follow:**  
**Input Candidate Profile → Analyze Dataset → Decide Filtering → Rank Jobs → Select Best Job → Tailor Resume**

| Step | Status | Where |
|------|--------|--------|
| Input candidate profile | ✅ | Profile from form/API; passed into offline agent and tools. |
| Analyze dataset | ✅ | Dataset (CSV) loaded; job count and profile shape inform LLM/tools. |
| Decide filtering | ✅ | LLM calls `filtering_tool` first (or fixed pipeline runs `_filter_csv_jobs`). |
| Rank jobs | ✅ | LLM calls `ranking_tool` on filtered jobs (or `_rank_csv_jobs`). |
| Select best job | ✅ | Best = rank 1 (`job_rank=1` or `ranked[0]`). |
| Tailor resume | ✅ | LLM calls `resume_tailoring_tool(job_rank=1)` (or fixed pipeline tailors for `ranked[0]`). |

---

## Dataset Requirement

| Requirement | Status | Evidence |
|-------------|--------|----------|
| Manually collect 20–30 real AI/ML job postings | ✅ | `data/jobs_dataset.csv` has 29 job rows (30 lines − 1 header). |
| Store in CSV | ✅ | `data/jobs_dataset.csv`. |
| No web scraping required | ✅ | CSV is static; scraping is only for building/refreshing the dataset if you choose. |
| Job Title | ✅ | Column "Job Title". |
| Company | ✅ | Column "Company". |
| Location | ✅ | Column "Location". |
| Required Skills | ✅ | Column "Required Skills". |
| Years of Experience Required | ✅ | Column "Years of Experience Required". |
| Shortened Job Description (5–8 lines) | ✅ | Column "Shortened Job Description (5–8 lines)". |
| URL | ✅ | Column "URL". |

---

## Agent Requirements (Critical)

| Requirement | Status | Evidence |
|-------------|--------|----------|
| Use an LLM for reasoning | ✅ | `_llm_reasoning_trace_generic`, `run_llm_tool_agent` (OpenAI/Anthropic/Ollama). |
| At least two callable tools: **Filtering** (mandatory) | ✅ | `filtering_tool`, `_filter_csv_jobs`; exposed to LLM in `OPENAI_TOOLS` / `ANTHROPIC_TOOLS`. |
| **Ranking** (mandatory) | ✅ | `ranking_tool`, `_rank_csv_jobs`; exposed to LLM. |
| **Resume Tailoring** (required for final output) | ✅ | `resume_tailoring_tool`, `_tailor_resume_offline`; exposed to LLM. |
| Show reasoning trace or explanation of decisions | ✅ | `reasoning` in `OfflineAgentResponse`; "LLM Reasoning & Trace" in UI; printed in `assignment_agent.py`. |
| **Not** hard-coded fixed steps without LLM decision-making | ✅* | With **OpenAI/Anthropic**: LLM chooses which tool to call and in what order (tool/function calling). With **Ollama only**: fallback is fixed pipeline; reasoning text is still shown. |

---

## Filtering Logic

| Rule | Status | Report-ready doc |
|------|--------|-------------------|
| Location preference | ✅ | `docs/FILTERING_RULES.md` §1. |
| Experience limit | ✅ | `docs/FILTERING_RULES.md` §2. |
| Company exclusion | ✅ | `docs/FILTERING_RULES.md` §3. |
| Remote-only filter (optional) | ✅ | `docs/FILTERING_RULES.md` §4. |
| Rules clearly explained for report | ✅ | `docs/FILTERING_RULES.md` – copy/adapt into your report. |

---

## Ranking System

| Requirement | Status | Evidence / Doc |
|-------------|--------|-----------------|
| Assign scores based on skill matching | ✅ | `JobRanker` WEIGHTS["skills"]=0.35; `_calculate_skill_match`. `docs/RANKING_SYSTEM.md`. |
| Consider experience alignment | ✅ | `WEIGHTS["experience"]=0.10`; experience match in `rank_job`. |
| Optionally consider location match | ✅ | `WEIGHTS["location"]=0.15`; location match in `rank_job`. |
| Output a ranked list with clear scores | ✅ | Each `RankedJob` has `.score` (0–100); list sorted by score. |
| Clearly display: **Ranked job list with scores** | ✅ | UI: "Ranked job list with scores"; each card shows score. |
| Clearly display: **Top 3 jobs** | ✅ | UI: "Top 3 jobs" section; script: "Top 3 jobs by score" in `assignment_agent.py`. |

---

## Resume Tailoring Requirements

| Requirement | Status | Evidence |
|-------------|--------|----------|
| Tailor for **only** the top-ranked job | ✅ | `resume_tailoring_tool` called with `job_rank=1` or `ranked[0]`. |
| Rewrite the Professional Summary | ✅ | `ResumeTailor._generate_tailored_summary`; output "Rewritten Professional Summary". |
| Modify **exactly 2** experience bullet points | ✅ | `get_two_modified_bullets` / `_get_two_modified_bullets`; "Modified Experience Bullet Points (exactly 2)". |
| Highlight aligned skills | ✅ | "Highlight Aligned Skills" section; `matched_skills` / `highlighted_skills`. |
| Do NOT regenerate the entire resume | ✅ | Only summary + 2 bullets changed; "(Rest of resume unchanged...)" in output; `docs/RESUME_TAILORING_REQUIREMENTS.md`. |

---

## Quick Verification Commands

```bash
# CSV row count (expect 29 data rows)
wc -l data/jobs_dataset.csv

# Run assignment agent (requires OPENAI_API_KEY or ANTHROPIC_API_KEY for LLM tool-calling)
python assignment_agent.py
```

---

## Summary

- **Fully met:** Pipeline, dataset, three tools (filter, rank, tailor), filtering rules, ranking (scores + Top 3), resume (summary + 2 bullets + aligned skills, no full regenerate), reasoning trace, docs for report.
- **Note:** For **LLM autonomy** (tool-calling), use **OpenAI** or **Anthropic**; with Ollama only, execution falls back to a fixed sequence (reasoning text still shown).
- **Your task:** Write the **report** using `docs/REPORT_TEMPLATE.md` and the three docs (`FILTERING_RULES.md`, `RANKING_SYSTEM.md`, `RESUME_TAILORING_REQUIREMENTS.md`), and adjust or drop the bias/ethics section if the assignment no longer requires it.
