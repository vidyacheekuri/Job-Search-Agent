# Job Search Agent — Career Match

An AI-powered job search app: create a profile, search and rank AI/ML jobs (live or from a CSV dataset), and get tailored resumes and cover letters. Uses Ollama for LLM reasoning and resume generation.

---

## What you need

- **Python 3.10+**
- **Node.js 18+**
- **Ollama** (for LLM reasoning and resume text) — [Install](https://ollama.ai), then run: `ollama pull llama3.2`
- A terminal

---

## Run the app (after cloning)

**1. Clone and go into the project**

```bash
git clone <repo-url>
cd Job-Search-Agent
```

**2. Install Python dependencies**

```bash
pip install -r requirements.txt
```

**3. Install frontend dependencies**

```bash
cd frontend
npm install
cd ..
```

**4. Start the backend with Ollama** (leave this terminal open)

```bash
LLM_PROVIDER=ollama python api/main.py
```

You should see something like: `Uvicorn running on http://0.0.0.0:8000`

**5. Start the frontend** (open a **new** terminal)

```bash
cd Job-Search-Agent/frontend
npm run dev
```

You should see a local URL, usually: `http://localhost:5173`

**6. Open the app**

In your browser go to: **http://localhost:5173**

Create a profile, then use **AI Agent** to search and rank jobs (live or from the CSV dataset), generate resumes, and run evaluation. The app uses Ollama for the “LLM Reasoning & Trace” and for resume summary generation.

---

## Agent pipeline

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

## Project structure

```
Job-Search-Agent/
├── api/
│   └── main.py                  # FastAPI backend
├── frontend/                    # React web UI (Career Match)
├── linkedin_scraper/
│   └── agent/
│       ├── llm_tool_agent.py    # LLM tool-calling (OpenAI / Claude / Ollama)
│       ├── ranker.py            # Ranking + filtering rules
│       ├── resume_tailor.py     # Resume tailoring
│       ├── profile.py           # Candidate profile model
│       ├── cover_letter.py      # Cover letter generation
│       └── evaluation.py        # Hiring simulation / evaluation
├── data/
│   ├── jobs_dataset.csv         # AI/ML job postings (offline mode)
│   ├── benchmark_jobs.json      # Evaluation set
│   └── sample_resume.json       # Sample profile
├── docs/                        # Filtering rules, ranking spec, report templates
└── requirements.txt
```

---

## If something goes wrong

| Problem | What to do |
|--------|------------|
| “Could not connect to the server” | Start the backend first (`LLM_PROVIDER=ollama python api/main.py`) and leave it running. |
| “Module not found” | Run `pip install -r requirements.txt` from the project root. |
| “npm: command not found” | Install Node.js from [nodejs.org](https://nodejs.org). |
| Port 8000 or 5173 already in use | Stop the other app using that port. |
| “Ollama unavailable” | Install [Ollama](https://ollama.ai), then run `ollama pull llama3.2`. Make sure Ollama is running (open the app or run `ollama serve`). |

---

## Use responsibly

For personal use only. Always review AI-generated resumes and cover letters before sending to employers.
