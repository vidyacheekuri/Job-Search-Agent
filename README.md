# AI Job Search Agent

An autonomous AI agent for searching AI Engineer jobs at mid-sized companies, with intelligent ranking, resume tailoring, cover letter generation, and hiring simulation evaluation.

![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)
![React](https://img.shields.io/badge/React-18-61DAFB.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.109+-009688.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)

## Table of Contents
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
| **Profile Management** | Create profile or parse from resume text |
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
- Python 3.10 or higher
- Node.js 18+ (for web UI)

### Quick Start

```bash
# Clone the repository
git clone https://github.com/AdithyaReddyGeeda/Linkedin-job-scraper.git
cd Linkedin-job-scraper

# Install Python dependencies
pip install -r requirements.txt

# Install CLI tool
pip install -e .

# Install frontend dependencies
cd frontend
npm install
cd ..
```

### Optional: OpenAI API Key
For enhanced resume and cover letter generation:
```bash
export OPENAI_API_KEY="your-api-key"
```

---

## Usage

### Web Interface

The easiest way to use the agent. Start both servers:

**Terminal 1 - API Server:**
```bash
python api/main.py
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
```

Open **http://localhost:5173** in your browser.

#### Using the AI Agent Tab

1. **Create Profile**: Fill in your details or paste your resume
2. **Search**: Enter job keywords and location
3. **Review Ranked Jobs**: See match scores and skill gaps
4. **Generate Materials**: Create tailored resumes and cover letters
5. **Evaluate**: Run hiring simulation to test your applications
6. **Analyze Bias**: Check for biases in search results

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
| Storage | localStorage (browser) |

---

## Contributing

Contributions are welcome! Areas of interest:

- [ ] Additional job sources (Indeed, Glassdoor)
- [ ] Improved skill matching (embeddings)
- [ ] PDF resume parsing
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
