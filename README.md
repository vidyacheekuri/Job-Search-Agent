# AI Job Search Agent

An autonomous AI agent for searching AI Engineer jobs at mid-sized companies, with intelligent ranking, resume tailoring, cover letter generation, and hiring simulation evaluation.

![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)
![React](https://img.shields.io/badge/React-18-61DAFB.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.109+-009688.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)

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
- [Features](#features)
- [Architecture](#architecture)
- [Installation](#installation)
- [Usage](#usage)
  - [Web Interface](#web-interface)
  - [Command Line](#command-line)
  - [API Endpoints](#api-endpoints)
- [Agent Pipeline](#agent-pipeline)
- [Evaluation Framework](#evaluation-framework)
- [Ethics & Bias Analysis](#ethics--bias-analysis)
- [Project Structure](#project-structure)
- [Tech Stack](#tech-stack)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)

---

## Features

### Core Features
| Feature | Description |
|---------|-------------|
| **Job Search** | Search LinkedIn for AI/ML engineering jobs |
| **Company Size Filter** | Filter for small, mid-sized, or large companies |
| **AI-Powered Ranking** | Rank jobs by profile match (skills, title, location, experience) |
| **Resume Tailoring** | Generate customized resumes for each job |
| **Cover Letter Generation** | AI-generated personalized cover letters |
| **ATS Optimization** | Score resumes for Applicant Tracking Systems |

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

### Agent Pipeline

```
1. SEARCH → 2. FILTER → 3. RANK → 4. TAILOR
    │            │          │         │
    ▼            ▼          ▼         ▼
 LinkedIn    Company     Profile   Resume +
   Jobs       Size       Match    Cover Letter
```

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
| GET | `/api/search` | Search jobs with filters |
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

### Hiring Simulation
The evaluator simulates recruiter review:

```python
from linkedin_scraper.agent import JobSearchAgent, AgentEvaluator

# Create agent with profile
agent = JobSearchAgent(profile)
evaluator = AgentEvaluator(recruiter_strictness=0.5)

# Run evaluation
agent.run_full_pipeline(keyword="AI Engineer", top_n_applications=10)
metrics = evaluator.evaluate_applications(agent.get_applications())

print(f"Interview Rate: {metrics.interview_rate}%")
print(f"Average Match Score: {metrics.avg_match_score}")
print(f"ATS Score: {metrics.avg_ats_score}")
```

### Metrics Tracked
- Interview rate (% advancing)
- Resume scores
- Cover letter scores
- Skill coverage
- ATS optimization
- Recruiter feedback

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
│   ├── exporter.py            # CSV/JSON export
│   └── agent/                 # AI Agent module
│       ├── __init__.py
│       ├── profile.py         # User profile management
│       ├── ranker.py          # Job ranking algorithm
│       ├── resume_tailor.py   # Resume generation
│       ├── cover_letter.py    # Cover letter generation
│       ├── agent.py           # Main agent orchestrator
│       └── evaluation.py      # Hiring simulation
│
├── api/                       # FastAPI backend
│   └── main.py                # API endpoints
│
├── frontend/                  # React web application
│   ├── src/
│   │   ├── components/        # React components
│   │   ├── hooks/             # Custom hooks
│   │   ├── services/          # API client
│   │   └── types/             # TypeScript types
│   └── package.json
│
├── docs/
│   └── ETHICS.md              # Ethics documentation
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

## Contributing

Contributions are welcome! Areas of interest:

- [ ] Additional job sources (Indeed, Glassdoor)
- [ ] Improved skill matching (embeddings)
- [x] PDF resume parsing
- [ ] Interview preparation module
- [ ] Salary negotiation assistant

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

## License

MIT License - see [LICENSE](LICENSE) for details.
