# Job Search Agent — AI Assignment Submission

An LLM-based AI agent that autonomously filters, ranks, and tailors resumes for AI/ML job postings. Built for the *AI for Engineers* assignment.

---

## Quick Start — Assignment Grading (3 Steps)

> **No API keys required.** The agent runs fully with local heuristics. Add an optional API key for LLM-driven tool calling (see below).

**Step 1 — Clone & install dependencies**

```bash
git clone <repo-url>
cd Job-Search-Agent
pip install -r requirements.txt
```

**Step 2 — Run the assignment agent**

```bash
python assignment_agent.py
```

**Step 3 — Read the output**

The terminal will print:
- LLM reasoning trace (which tools to call and why)
- Filtered job list
- Ranked job list with scores (0–100)
- Top 3 jobs
- Tailored resume: rewritten summary + exactly 2 modified bullet points

That's it. No server needed. No browser needed.

---

## Optional: Enable LLM-Driven Tool Calling

Without a key the agent falls back to rule-based heuristics. To unlock LLM decision-making:

```bash
# OpenAI
export OPENAI_API_KEY=sk-...

# or Anthropic Claude
export ANTHROPIC_API_KEY=sk-ant-...

# or local Ollama (install Ollama first, then pull a model)
ollama pull llama3
export LLM_PROVIDER=ollama
```

Then re-run `python assignment_agent.py`. The agent will use function/tool calling so the LLM decides which tools to invoke and in what order.

---

## Agent Pipeline

```
Candidate Profile
      │
      ▼
 [1] Filtering Tool
     • Exclude FAANG companies (Meta, Amazon, Apple, Netflix, Google…)
     • Location preference match
     • Experience years limit
     • Skills overlap check
     • Optional remote-only filter
     (No company-size filter; all company sizes are included.)
      │
      ▼
 [2] Ranking Tool
     • Skill match       35%
     • Title match       20%
     • Location match    15%
     • Recency           10%
     • Experience        10%
     • Company match      5%
     • Salary match       5%
     → Outputs ranked list with 0–100 scores
      │
      ▼
 [3] Resume Tailoring Tool  (top-ranked job only)
     • Rewrite Professional Summary
     • Modify exactly 2 experience bullet points
     • Highlight aligned skills
     • Rest of resume untouched
```

---

## Dataset

`data/jobs_dataset.csv` — 29 manually collected real AI/ML job postings.

| Column | Description |
|--------|-------------|
| Job Title | Role name |
| Company | Employer |
| Location | City / Remote |
| Required Skills | Semicolon-separated skill list |
| Years of Experience Required | Numeric |
| Shortened Job Description (5–8 lines) | Role summary |
| URL | Original job posting link |

---

## Project Structure

```
Job-Search-Agent/
├── assignment_agent.py          # ← MAIN ENTRY POINT for assignment
├── data/
│   ├── jobs_dataset.csv         # 29 AI/ML job postings
│   ├── benchmark_jobs.json      # 20-job evaluation set
│   └── sample_resume.json       # Sample AI Engineer profile
├── linkedin_scraper/
│   └── agent/
│       ├── llm_tool_agent.py    # LLM tool-calling (OpenAI / Claude / Ollama)
│       ├── ranker.py            # Ranking logic + filtering rules
│       ├── resume_tailor.py     # Resume tailoring
│       ├── profile.py           # Candidate profile model
│       ├── cover_letter.py      # Cover letter generation
│       └── evaluation.py        # Hiring simulation / evaluation metrics
├── api/
│   └── main.py                  # FastAPI backend (optional web UI)
├── frontend/                    # React web interface (optional)
├── docs/                        # Design docs, filtering rules, ranking spec
└── requirements.txt
```

---

## Full Web App (Optional)

The project also includes a full web interface ("Career Match") with live job search across LinkedIn, Indeed, and Greenhouse. This is **not required for assignment grading** — it's a bonus.

**Backend**
```bash
python api/main.py
# Runs at http://localhost:8000
```

**Frontend** (separate terminal)
```bash
cd frontend
npm install
npm run dev
# Runs at http://localhost:5173
```

---

## Requirements

- Python 3.10+
- Node.js 18+ (only for the optional web UI)

Install Python dependencies:
```bash
pip install -r requirements.txt
```

---

## Common Issues

| Problem | Fix |
|---------|-----|
| `ModuleNotFoundError` | Run `pip install -r requirements.txt` |
| `FileNotFoundError: jobs_dataset.csv` | Make sure you're running from the `Job-Search-Agent/` root folder |
| LLM reasoning says "Ollama unavailable" | Either set `OPENAI_API_KEY` or `ANTHROPIC_API_KEY`, or install Ollama and run `ollama pull llama3` |
| Port 8000 or 5173 already in use | Only relevant for the optional web UI, not the assignment script |

---

## Use Responsibly

This project is for personal academic use. AI-generated resume content should always be reviewed before submission to real employers.
