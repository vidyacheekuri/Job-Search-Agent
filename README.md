# Job Search Agent

An autonomous AI agent for searching **AI Engineer jobs at mid-sized "Middle America" companies** (not big tech or startups). The agent filters out FAANG+, excludes startups, ranks jobs by profile match, and generates tailored application materials.

![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)
![React](https://img.shields.io/badge/React-18-61DAFB.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.109+-009688.svg)

## Quick Start

```bash
# 1. Clone and install
git clone https://github.com/vidyacheekuri/Job-Search-Agent.git
cd Job-Search-Agent
pip install -r requirements.txt

# 2. Install frontend
cd frontend && npm install && cd ..

# 3. Start backend (Terminal 1)
python api/main.py

# 4. Start frontend (Terminal 2)
cd frontend && npm run dev

# 5. Open http://localhost:5173 in your browser
```

**No API keys required!** The app works offline with heuristic-based AI. Optionally set `OPENAI_API_KEY` for enhanced generation.

---

## Features

| Feature | Description |
|---------|-------------|
| **Multi-Source Search** | LinkedIn, Indeed, and Greenhouse |
| **FAANG+ Blacklist** | Exclude 40+ big tech companies |
| **Startup Filter** | Exclude startups (<50 employees heuristic) |
| **Location Filter** | Iowa, Texas, Remote, etc. |
| **AI-Powered Ranking** | Score jobs by skill, title, location, recency |
| **Resume Tailoring** | Customized resumes per job |
| **Cover Letter Generation** | AI-generated cover letters |
| **ATS Optimization** | Resume compatibility scoring |
| **Hiring Simulation** | Mock recruiter evaluation |
| **LLM Reasoning & Trace** | Optional LLM explains filtering → ranking → tailoring |
| **Offline CSV Agent** | Static CSV dataset + same workflow for assignment use |

---

## Pipeline

```
Search → Filter FAANG → Filter Startups → Filter Location → Rank Top 10 → Tailor Top 3
```

1. **Search** job boards; extract title, company, location, skills, salary, URL  
2. **Filter** FAANG+ blacklist; exclude startups  
3. **Rank** top 10 by skill match, location preference, recency  
4. **Tailor** customized resumes + cover letters for top 3 jobs  

---

## Installation

### Prerequisites
- Python 3.10+
- Node.js 18+
- pip, npm

### Setup

```bash
# Python dependencies
pip install -r requirements.txt

# Or with Conda
conda env create -f environment.yml
conda activate job-search-agent

# Frontend
cd frontend && npm install
```

### Optional: CLI
```bash
pip install -e .
```

---

## Usage

### Web Interface

**Terminal 1:**
```bash
python api/main.py
```

**Terminal 2:**
```bash
cd frontend && npm run dev
```

Open **http://localhost:5173**

### AI Agent Tab
1. Create profile (form, PDF upload, or paste text)
2. Search & rank jobs (Live Web or Offline CSV dataset)
3. Generate tailored resumes and cover letters
4. Run evaluation (benchmark-based, ~5 sec)

### API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/search` | Search LinkedIn jobs |
| GET | `/api/search/multi` | Multi-source search |
| POST | `/api/profile` | Create profile |
| POST | `/api/profile/upload-pdf` | Upload PDF resume |
| POST | `/api/search/ranked` | Search and rank by profile |
| POST | `/api/tailor/resume` | Generate tailored resume |
| POST | `/api/generate/cover-letter` | Generate cover letter |
| POST | `/api/evaluate` | Hiring simulation |
| POST | `/api/agent/offline` | Offline CSV agent (filter → rank → tailor) |

---

## Project Structure

```
Job-Search-Agent/
├── linkedin_scraper/       # Core package
│   ├── scraper.py          # LinkedIn scraping
│   ├── indeed_scraper.py
│   ├── greenhouse_scraper.py
│   └── agent/              # AI agent
│       ├── profile.py
│       ├── ranker.py
│       ├── resume_tailor.py
│       ├── cover_letter.py
│       ├── agent.py
│       └── evaluation.py
├── api/main.py             # FastAPI backend
├── frontend/               # React app
├── data/
│   ├── sample_resume.json
│   └── benchmark_jobs.json
├── docs/
└── scripts/
```

---

## Tech Stack

| Layer | Technology |
|-------|------------|
| Scraping | Python, BeautifulSoup, Requests |
| AI | Heuristic + optional LLMs (OpenAI / Claude / Ollama) for reasoning & resume summary |
| Backend | FastAPI, Uvicorn, Pydantic |
| Frontend | React, TypeScript, Vite, Tailwind CSS |
| PDF | PyPDF2 |

---

## Troubleshooting

**"Could not connect to the server"**  
- Ensure `python api/main.py` is running  
- Check port 8000 is free  

**"Module not found"**  
```bash
pip install -r requirements.txt
```

**"npm: command not found"**  
- Install Node.js from https://nodejs.org/

**Jobs not loading**  
- LinkedIn may rate-limit; wait and retry  
- Reduce result limit  

---

## Assignment / Offline CSV Agent

- **Dataset**: `data/jobs_dataset.csv` (Job Title, Company, Location, Required Skills, Years of Experience, Shortened Description, URL).
- **Script**: `assignment_agent.py` — load CSV, run filtering_tool → ranking_tool → resume_tailoring_tool, print ranked list and tailored resume for top job.
- **API**: `POST /api/agent/offline` — same workflow; used when you choose **Data Source: Offline CSV Dataset** in the AI Agent tab.

### LLM Reasoning & Trace

The agent can use an LLM to explain its workflow (which tools, in what order). This reasoning is returned by `/api/agent/offline`, `/api/search/ranked`, `/api/agent/run`, and `/api/agent/middle-america`, and shown in the UI as **“LLM Reasoning & Trace”**.

### LLM Providers

Set `LLM_PROVIDER` to `openai`, `anthropic`, or `ollama`. If unset, the app uses OpenAI if `OPENAI_API_KEY` is set, else Anthropic if `ANTHROPIC_API_KEY` is set, else Ollama. Optional: `OLLAMA_MODEL` (default `llama3`). The same provider is used for reasoning traces and for resume summary generation in the tailor.

---

## Disclaimer

Use responsibly. Respect LinkedIn's Terms of Service. Don't make excessive requests. Use for personal job searching only. Review all AI-generated content before submitting.
