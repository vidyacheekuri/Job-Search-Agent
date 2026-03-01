# Job Search Agent

An autonomous AI agent for searching **AI Engineer jobs at mid-sized "Middle America" companies** (not big tech or startups). The agent filters out FAANG+, excludes startups, ranks jobs by profile match, and generates tailored application materials.

**AI for Engineers - Group Assignment**

![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)
![React](https://img.shields.io/badge/React-18-61DAFB.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.109+-009688.svg)
## Quick Start (TL;DR)

```bash
# 1. Clone and install
git clone https://github.com/AdithyaReddyGeeda/Linkedin-job-scraper.git
cd Linkedin-job-scraper
pip install -r requirements.txt

# 2. Install frontend
cd frontend && npm install && cd ..

# 3. Start backend (Terminal 1)
python api/main.py

# 4. Start frontend (Terminal 2)
cd frontend && npm run dev

# 5. Open http://localhost:5173 in your browser
```

**No API keys required!** The app works fully offline with heuristic-based AI. Optionally set `OPENAI_API_KEY` for enhanced generation.

---

## Table of Contents
- [Quick Start](#quick-start-tldr)
- [Assignment Overview](#assignment-overview)
- [Features](#features)
- [Architecture](#architecture)
- [Installation](#installation)
- [Usage](#usage)
  - [Web Interface](#web-interface)
  - [Middle America Pipeline](#middle-america-pipeline)
  - [API Endpoints](#api-endpoints)
- [Agent Pipeline](#agent-pipeline)
- [Evaluation Framework](#evaluation-framework)
- [Ethics & Bias Analysis](#ethics--bias-analysis)
- [Project Structure](#project-structure)
- [Tech Stack](#tech-stack)
- [Troubleshooting](#troubleshooting)
- [Demo Recording Guide](#demo-recording-guide)
- [Submission Checklist](#submission-checklist)

---

## Assignment Overview

This project implements an AI agent for the **"Middle America Job and Application Agent"** assignment.

### Pipeline Steps
1. **Search** job boards; extract title, company, location, skills, salary, URL
2. **Filter**: Blacklist FAANG+; exclude startups (<50 employees heuristic)
3. **Rank** top 10 by skill match, location preference, and recency
4. **Tailor**: Generate customized resumes + cover letters for top 3 jobs

### Sample Resume Profile
- **Name**: Alex Johnson (Generic AI Engineer)
- **Experience**: 4 years (Python, TensorFlow, MLflow)
- **Location**: Des Moines, Iowa (Midwest preference)
- **Target**: AI Engineer roles at mid-sized companies

### Key Deliverables
| Deliverable | Status | Location |
|-------------|--------|----------|
| Design Document | ✅ | `docs/DESIGN_DOCUMENT.md` |
| Implementation | ✅ | `linkedin_scraper/agent/` |
| 20-Job Benchmark | ✅ | `data/benchmark_jobs.json` |
| Sample Resume | ✅ | `data/sample_resume.json` |
| Evaluation Metrics | ✅ | Precision@10, Interview Yield |
| Ethics/Bias Analysis | ✅ | `docs/ETHICS.md` |
| Reflections Template | ✅ | `docs/REFLECTIONS_TEMPLATE.md` |

---

## Features

### Core Features
| Feature | Description |
|---------|-------------|
| **Multi-Source Search** | Search across LinkedIn, Indeed, and Greenhouse simultaneously |
| **FAANG+ Blacklist** | Automatically exclude 40+ big tech companies (Google, Meta, Amazon, etc.) |
| **Startup Filter** | Exclude startups (<50 employees) using heuristic detection |
| **Location Filter** | Toggle-able state filter (Iowa-only, Texas-only, etc.) |
| **AI-Powered Ranking** | Rank jobs by profile match (skills, title, location, experience) |
| **Resume Tailoring** | Generate customized resumes for each job |
| **Cover Letter Generation** | AI-generated personalized cover letters |
| **ATS Optimization** | Score resumes for Applicant Tracking Systems |
| **Decision Logging** | Full pipeline trace for every filter and rank decision |

### Supported Job Sources
| Source | Description |
|--------|-------------|
| **LinkedIn** | Professional job listings with Easy Apply support |
| **Indeed** | General job listings with salary information |
| **Greenhouse** | Direct job boards from 50+ tech companies (Anthropic, OpenAI, Stripe, etc.) |

### Web Dashboard Features
| Feature | Description |
|---------|-------------|
| **Dark Mode** | Toggle between light and dark themes |
| **Search History** | Quick access to recent searches |
| **Save Jobs** | Bookmark jobs with personal notes |
| **Application Tracker** | Track jobs with status (Applied → Offered) |
| **Company Info** | Quick links to LinkedIn, Glassdoor, Google |
| **Salary Insights** | Estimated salary when not provided |
| **Mobile Responsive** | Works on all devices |
| **Pagination** | Navigate through large result sets |

### AI Agent Features
| Feature | Description |
|---------|-------------|
| **Profile Management** | Create profile manually, upload PDF resume, or paste resume text |
| **Job Matching** | Score jobs 0-100% based on profile fit |
| **Skill Gap Analysis** | Identify missing skills to learn |
| **Hiring Simulation** | Mock recruiter evaluation of applications |
| **Bias Analysis** | Detect biases in search results |

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        Web Interface (React)                     │
├─────────────────────────────────────────────────────────────────┤
│  Search Tab  │  AI Agent Tab  │  Saved Jobs  │  Applications    │
└──────────────┴────────────────┴──────────────┴──────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      FastAPI Backend                             │
├─────────────────────────────────────────────────────────────────┤
│  /api/search      │  /api/profile     │  /api/agent/run         │
│  /api/search/ranked│ /api/tailor/resume│ /api/evaluate          │
│  /api/generate/   │                   │  /api/analyze/bias      │
│     cover-letter  │                   │                         │
└──────────────┬────┴────────────────┬──┴─────────────────────────┘
               │                     │
               ▼                     ▼
┌──────────────────────┐   ┌──────────────────────────────────────┐
│   LinkedIn Scraper   │   │           AI Agent Module            │
├──────────────────────┤   ├──────────────────────────────────────┤
│ • Job Search         │   │ • UserProfile (profile.py)           │
│ • Job Details        │   │ • JobRanker (ranker.py)              │
│ • Pagination         │   │ • ResumeTailor (resume_tailor.py)    │
│ • Rate Limiting      │   │ • CoverLetterGenerator (cover_letter)│
└──────────────────────┘   │ • JobSearchAgent (agent.py)          │
                           │ • Evaluation (evaluation.py)         │
                           └──────────────────────────────────────┘
```

### Agent Pipeline (Middle America)

```
1. SEARCH → 2. FILTER FAANG → 3. FILTER STARTUPS → 4. FILTER LOCATION → 5. RANK TOP 10 → 6. TAILOR TOP 3
     │             │                  │                    │                  │                │
     ▼             ▼                  ▼                    ▼                  ▼                ▼
  LinkedIn     Blacklist           <50 emp             Iowa/TX/          Profile          Resume +
  Indeed       40+ cos             heuristic           Remote            Match           Cover Letter
  Greenhouse
```

### FAANG+ Blacklist (40+ companies)
Google, Meta, Amazon, Apple, Netflix, Microsoft, OpenAI, Anthropic, Nvidia, Uber, Airbnb, Stripe, etc.

### Startup Indicators
"seed", "series a", "founding team", "Y Combinator", "employee #5", etc.

---

## Installation

### Prerequisites
- **Python 3.10+** - [Download Python](https://www.python.org/downloads/)
- **Node.js 18+** - [Download Node.js](https://nodejs.org/)
- **pip** - Comes with Python
- **npm** - Comes with Node.js

### Step-by-Step Installation

#### Step 1: Clone the Repository
```bash
git clone https://github.com/AdithyaReddyGeeda/Linkedin-job-scraper.git
cd Linkedin-job-scraper
```

#### Step 2: Install Python Dependencies
```bash
pip install -r requirements.txt
```

This installs:
- `fastapi` - Backend API framework
- `uvicorn` - ASGI server
- `beautifulsoup4` - Web scraping
- `PyPDF2` - PDF resume parsing
- `openai` - Optional AI enhancement

#### Step 3: Install Frontend Dependencies
```bash
cd frontend
npm install
cd ..
```

#### Step 4 (Optional): Install CLI Tool
```bash
pip install -e .
```

### API Keys (Optional)

**The app works WITHOUT any API keys!** All features use local heuristic algorithms by default.

For enhanced AI-powered resume/cover letter generation with OpenAI:
```bash
# macOS/Linux
export OPENAI_API_KEY="your-api-key"

# Windows (Command Prompt)
set OPENAI_API_KEY=your-api-key

# Windows (PowerShell)
$env:OPENAI_API_KEY="your-api-key"
```

---

## Usage

### Web Interface (Recommended)

The easiest way to use the agent. **You need TWO terminal windows running simultaneously.**

#### Terminal 1 - Start the Backend API Server
```bash
# From the project root directory
python api/main.py
```
You should see:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete.
```

#### Terminal 2 - Start the Frontend Dev Server
```bash
# From the project root directory
cd frontend
npm run dev
```
You should see:
```
VITE v5.x.x  ready in xxx ms
➜  Local:   http://localhost:5173/
```

#### Open the App
Open **http://localhost:5173** in your browser.

> **Important**: Keep BOTH terminals running while using the app. The frontend (Terminal 2) talks to the backend API (Terminal 1).

---

### Using the AI Agent Tab (Step-by-Step)

#### 1. Create Your Profile
You have 3 options:
- **Fill Form**: Manually enter your details
- **Upload PDF**: Upload your resume as a PDF file (drag & drop supported)
- **Paste Text**: Copy/paste your resume text

#### 2. Search for Jobs
- Enter job keywords (default: "AI Engineer")
- Enter location (optional, e.g., "San Francisco" or "Remote")
- Select company size filter (Startups / Mid-sized / Enterprise)
- Click "Search & Rank Jobs"

#### 3. Review Ranked Results
- Jobs are scored 0-100% based on how well they match your profile
- See which skills you have and which you're missing
- Click on any job to see more details

#### 4. Generate Application Materials
For any job, click:
- **"Generate Resume"** - Creates a tailored resume optimized for that job
- **"Generate Cover Letter"** - Creates a personalized cover letter

#### 5. Run Hiring Simulation
- Click "Run Evaluation" to simulate how recruiters would review your applications
- See interview rates, ATS scores, and feedback

#### 6. Analyze Bias
- Click "Analyze Bias" to detect potential biases in search results
- See distribution by location, company size, salary, and experience level

---

### Command Line

```bash
# Basic AI Engineer job search
linkedin-jobs search "AI Engineer" --location "San Francisco"

# Search for mid-sized companies with filters
linkedin-jobs search "Machine Learning Engineer" \
  --location "Remote" \
  --job-type full-time \
  --experience senior \
  --easy-apply \
  --limit 50

# Export to file with full descriptions
linkedin-jobs search "Deep Learning Engineer" \
  --details \
  -o ai_jobs.json
```

---

### API Endpoints

Start the API server:
```bash
python api/main.py
```

#### Core Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Health check |
| GET | `/api/search` | Search LinkedIn jobs with filters |
| GET | `/api/search/multi` | Search multiple sources (LinkedIn, Indeed, Greenhouse) |
| GET | `/api/sources` | Get available job sources |
| GET | `/api/sources/greenhouse/companies` | List Greenhouse companies |
| POST | `/api/profile` | Create user profile |
| POST | `/api/profile/parse` | Parse resume text |
| POST | `/api/profile/upload-pdf` | Upload and parse PDF resume |
| POST | `/api/search/ranked` | Search and rank by profile |
| POST | `/api/tailor/resume` | Generate tailored resume |
| POST | `/api/generate/cover-letter` | Generate cover letter |
| POST | `/api/agent/run` | Run full agent pipeline |
| POST | `/api/evaluate` | Run hiring simulation |
| POST | `/api/analyze/bias` | Analyze result biases |

#### Example: Full Pipeline

```bash
# 1. Create profile
curl -X POST "http://localhost:8000/api/profile" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "John Doe",
    "email": "john@example.com",
    "title": "AI Engineer",
    "years_experience": 5,
    "skills": ["Python", "TensorFlow", "PyTorch", "NLP"],
    "target_roles": ["AI Engineer", "ML Engineer"]
  }'

# 2. Search and rank jobs
curl -X POST "http://localhost:8000/api/search/ranked?\
keyword=AI%20Engineer&\
location=Remote&\
profile_id=john@example.com&\
company_size=mid&\
top_n=10"

# 3. Generate resume for a job
curl -X POST "http://localhost:8000/api/tailor/resume?\
profile_id=john@example.com&\
job_url=https://linkedin.com/jobs/view/123456"

# 4. Run evaluation
curl -X POST "http://localhost:8000/api/evaluate?\
profile_id=john@example.com&\
keyword=AI%20Engineer&\
num_applications=5"
```

---

## Agent Pipeline

The agent follows a 4-step pipeline:

### 1. Search
- Query LinkedIn for job listings
- Support for multiple AI-related keywords
- Rate-limited to respect LinkedIn

### 2. Filter
- **Company Size**: small (startups), mid (growth stage), large (enterprise)
- **Requirements**: salary, easy apply, applicant count
- **Exclusions**: specific companies

### 3. Rank
Jobs are scored 0-100% based on:

| Dimension | Weight | Description |
|-----------|--------|-------------|
| Skills | 35% | Matching technical skills |
| Title | 25% | Job title relevance |
| Location | 15% | Geographic match |
| Experience | 10% | Years alignment |
| Salary | 10% | Meets expectations |
| Company | 5% | Target company match |

### 4. Tailor
For each top job:
- **Resume**: Reorder skills, optimize keywords, improve ATS score
- **Cover Letter**: Personalize for company and role

---

## Evaluation Framework

### Benchmark Dataset
A 20-job ground-truth benchmark for evaluation (`data/benchmark_jobs.json`):
- **10 Interview-Worthy**: Jobs matching the sample profile (mid-sized, Midwest, skills align)
- **10 Rejects**: FAANG companies, startups, experience mismatches

### Core Metrics

| Metric | Formula | Description |
|--------|---------|-------------|
| **Precision@10** | Interview-worthy in top 10 / 10 | How many top-ranked jobs are actually good matches |
| **Interview Yield** | Human "Yes" ratings / Total rated | Human evaluation of shortlist quality |

### Hiring Simulation
The evaluator simulates recruiter review:

```python
from linkedin_scraper.agent import JobSearchAgent, HiringSimulator

# Load benchmark
simulator = HiringSimulator("data/benchmark_jobs.json")

# Run agent pipeline
agent = JobSearchAgent(profile)
results = agent.run_middle_america_pipeline(
    keyword="AI Engineer",
    location="Iowa",
    exclude_faang=True,
    exclude_startups=True,
)

# Evaluate shortlist
eval_results = simulator.evaluate_shortlist(results["ranking"]["top_jobs"], k=10)
print(f"Precision@10: {eval_results['precision_at_k']}")
print(f"Interview Yield: {eval_results['interview_yield']}")
```

### Human Rating Form
Generate a form for 3 human raters:
```python
from linkedin_scraper.agent import create_human_rating_form

create_human_rating_form(
    shortlist=top_10_jobs,
    output_path="human_rating_form.json"
)
```

### Metrics Tracked
- **Precision@10**: Core metric for ranking quality
- **Interview Yield**: Human rater consensus
- **ATS Score**: Resume compatibility (0-100)
- **Personalization Score**: Cover letter quality (0-100)
- **Skill Coverage**: % of required skills matched

---

## Ethics & Bias Analysis

See [docs/ETHICS.md](docs/ETHICS.md) for full documentation.

### Bias Detection
The agent analyzes:
- **Location bias**: Geographic distribution
- **Company size bias**: Startup vs enterprise skew
- **Salary range bias**: Compensation patterns
- **Experience level bias**: Junior vs senior roles
- **Language bias**: Problematic terms in job postings

### Responsible Usage
- Use for personal job searching only
- Review all AI-generated content before submitting
- Don't misrepresent experience or skills
- Respect LinkedIn's rate limits

---

## Project Structure

```
linkedin-job-scraper/
├── linkedin_scraper/          # Core Python package
│   ├── __init__.py
│   ├── cli.py                 # Command line interface
│   ├── scraper.py             # LinkedIn scraping logic
│   ├── indeed_scraper.py      # Indeed scraping
│   ├── greenhouse_scraper.py  # Greenhouse scraping
│   ├── multi_scraper.py       # Multi-source orchestrator
│   ├── exporter.py            # CSV/JSON export
│   └── agent/                 # AI Agent module
│       ├── __init__.py
│       ├── profile.py         # User profile + PDF parsing
│       ├── ranker.py          # Ranking + FAANG blacklist + startup filter
│       ├── resume_tailor.py   # Resume generation
│       ├── cover_letter.py    # Cover letter generation
│       ├── agent.py           # Main agent + Middle America pipeline
│       └── evaluation.py      # Precision@10, HiringSimulator, BiasAnalyzer
│
├── api/                       # FastAPI backend
│   └── main.py                # API endpoints (30+ routes)
│
├── frontend/                  # React web application
│   ├── src/
│   │   ├── components/        # React components
│   │   ├── hooks/             # Custom hooks
│   │   ├── services/          # API client
│   │   └── types/             # TypeScript types
│   └── package.json
│
├── data/                      # Assignment data files
│   ├── sample_resume.json     # Sample AI Engineer profile (3-5 yrs)
│   └── benchmark_jobs.json    # 20-job benchmark (10 good, 10 reject)
│
├── docs/                      # Documentation
│   ├── DESIGN_DOCUMENT.md     # Pipeline diagram + filter heuristics
│   ├── REPORT_TEMPLATE.md     # 8-10 page report template
│   ├── REFLECTIONS_TEMPLATE.md# Individual reflection template
│   └── ETHICS.md              # Ethics + bias analysis
│
├── requirements.txt           # Python dependencies
├── setup.py                   # Package configuration
└── README.md
```

---

## Tech Stack

| Layer | Technology |
|-------|------------|
| Scraping | Python, BeautifulSoup, Requests |
| AI/ML | Heuristic matching, OpenAI (optional) |
| CLI | Click, Rich |
| Backend | FastAPI, Uvicorn, Pydantic |
| Frontend | React, TypeScript, Vite, Tailwind CSS |
| PDF Parsing | PyPDF2 |
| Storage | localStorage (browser) |

---

## Troubleshooting

### Common Issues

#### "Could not connect to the server"
**Problem**: Frontend can't reach the backend API.

**Solution**:
1. Make sure Terminal 1 is running `python api/main.py`
2. Check that port 8000 is not in use by another app
3. Try restarting the API server

```bash
# Check if port 8000 is in use
lsof -i :8000  # macOS/Linux
netstat -ano | findstr :8000  # Windows

# Kill the process using that port (if needed)
kill -9 <PID>  # macOS/Linux
```

#### "Module not found" errors
**Problem**: Python dependencies not installed.

**Solution**:
```bash
pip install -r requirements.txt
```

#### "npm: command not found"
**Problem**: Node.js is not installed.

**Solution**: Download and install Node.js from https://nodejs.org/

#### Frontend shows blank page
**Problem**: Frontend dependencies not installed or build failed.

**Solution**:
```bash
cd frontend
rm -rf node_modules
npm install
npm run dev
```

#### PDF upload not working
**Problem**: PyPDF2 not installed.

**Solution**:
```bash
pip install PyPDF2
```

#### Jobs not loading / "Search failed"
**Problem**: LinkedIn may be rate-limiting or blocking requests.

**Solution**:
- Wait a few minutes and try again
- Reduce the number of results (limit)
- Try different search keywords

### Getting Help

If you're still having issues:
1. Check that all prerequisites are installed (`python --version`, `node --version`)
2. Make sure both terminals are running
3. Try a fresh install (delete `node_modules` and reinstall)
4. Open an issue on GitHub with error details

---

## Demo Recording Guide

Record an **8-10 minute demo video** covering these required segments:

### Demo Script (with timestamps)

| Segment | Duration | Content |
|---------|----------|---------|
| **0:00 - Introduction** | 30 sec | Project overview, team members |
| **0:30 - Setup** | 1 min | Start backend + frontend, show both terminals |
| **1:30 - Profile** | 1 min | Load sample resume OR upload PDF |
| **2:30 - Fresh Query** | 2 min | Search "AI Engineer Iowa", show filters working |
| **4:30 - Filter Toggle** | 1 min | Change from Iowa → Texas, show adaptation |
| **5:30 - Top Job** | 1 min | Explain top match: "85% match, Texas, <30 days" |
| **6:30 - Tailoring** | 2 min | Generate resume + cover letter for top 3, narrate changes |
| **8:30 - Failure Case** | 1 min | Show one bug/issue + how team fixed it |
| **9:30 - Conclusion** | 30 sec | Summarize, mention ethics |

### Required Demonstrations

1. **Fresh Query Run**
   ```bash
   # Run the Middle America pipeline
   curl -X POST "http://localhost:8000/api/agent/middle-america?\
   profile_id=sample_ai_engineer&\
   keyword=AI%20Engineer&\
   location=Iowa&\
   exclude_faang=true&\
   exclude_startups=true"
   ```

2. **Filter Toggle Test**
   - First search: `location=Iowa`
   - Second search: `location=Texas` (same query, different filter)
   - Show how results adapt to new location

3. **Top Job Explanation**
   - Point to match score (e.g., "85%")
   - Explain: location match, skill overlap, recency
   - Show FAANG jobs were excluded

4. **Tailoring Narration**
   - Show original resume
   - Show tailored resume side-by-side
   - Point out: keywords added, experience reordered, ATS score

5. **Failure Case**
   - Examples: Rate limiting, parsing error, wrong filter
   - Show git commit where you fixed it
   - Explain the solution

### Recording Requirements
- **Unlisted YouTube/Vimeo video** (share link only)
- **Timestamped segments** in video description
- Screen share with voiceover
- All 5 team members should appear in narration

### Recording Tips
- Use OBS Studio, QuickTime, or Loom
- 1080p resolution recommended
- Test audio levels before recording
- Keep under 10 minutes

---

## Individual Reflections

Each team member must submit an individual reflection. Use the template at:
- [`docs/REFLECTIONS_TEMPLATE.md`](docs/REFLECTIONS_TEMPLATE.md)

Save your completed reflection as `REFLECTION_[YourName].md` in the `docs/` folder.

---

## Contributing

Contributions are welcome! Areas of interest:

- [x] Additional job sources (Indeed, Greenhouse) ✅
- [ ] Improved skill matching (embeddings)
- [x] PDF resume parsing ✅
- [ ] Interview preparation module
- [ ] Salary negotiation assistant

---

## Submission Checklist

For the group assignment, ensure you have:

### Code Repository
- [x] Complete source code on GitHub
- [x] Clear README with installation instructions  
- [x] `requirements.txt` with all dependencies
- [x] TAs can run code from scratch using only README

### Design Document (2-3 pages)
- [x] Pipeline diagram (visual flow) → `docs/DESIGN_DOCUMENT.md`
- [x] Filter heuristics explained (FAANG blacklist, startup indicators)
- [x] Tailoring workflow description

### Implementation
- [x] **Search**: Multi-source job scraping (LinkedIn, Indeed, Greenhouse)
- [x] **Filter FAANG**: Blacklist 40+ big tech companies
- [x] **Filter Startups**: Exclude <50 employees using heuristics
- [x] **Filter Location**: Toggle-able state filter (Iowa/Texas/Remote)
- [x] **Rank Top 10**: Weighted scoring (skills, title, location, experience)
- [x] **Tailor Top 3**: Resume + cover letter generation
- [x] **Decision Logging**: Full trace of all pipeline decisions

### Evaluation (Core)
- [x] 20-job benchmark dataset → `data/benchmark_jobs.json`
  - [x] 10 interview-worthy jobs
  - [x] 10 reject jobs (FAANG, startups, mismatches)
- [x] Precision@10 metric computation
- [x] Interview Yield metric
- [x] Human rating form generation
- [x] Tailoring quality scores (1-5 scale)
- [x] Filter toggle experiment support (Iowa → Texas)

### Report (8-10 pages)
- [ ] Write report with sections: Intro, Design, Eval Results, Bias/Ethics, Appendix

### Demo Video (8-10 minutes)
- [ ] Fresh query run with screen share + voiceover
- [ ] Filter toggle demonstration (e.g., Texas → Iowa)
- [ ] Top job explanation ("85% match, Texas, <30 days")
- [ ] Tailor sample resume for top 3 jobs with narration
- [ ] One failure case + how team fixed it
- [ ] Unlisted video URL with timestamped segments

### Individual Reflections (1 page each)
- [ ] Each member completes `docs/REFLECTIONS_TEMPLATE.md`
- [ ] Save as `REFLECTION_[YourName].md`
- [ ] Personal role and contributions
- [ ] Reflection on hiring equity impact

### Peer Assessment
- [ ] Each member submits scores and comments for teammates
- [ ] Categories: contribution, communication, quality

### Development Setup

```bash
# Install dev dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Run linting
flake8 linkedin_scraper
```

---

## Disclaimer

This tool scrapes publicly available job listings from LinkedIn. Please use responsibly:

- Respect LinkedIn's Terms of Service
- Don't make excessive requests
- Use for personal job searching only
- Consider rate limiting in production
- Review all AI-generated content before use

---

## Author

**Adithya Reddy Geeda**

- GitHub: [@AdithyaReddyGeeda](https://github.com/AdithyaReddyGeeda)

---
