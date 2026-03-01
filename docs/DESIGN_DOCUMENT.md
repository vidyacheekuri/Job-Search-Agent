# Design Document: Middle America Job Search Agent

## AI for Engineers - Group Assignment
**Version:** 1.0  
**Date:** February 2026

---

## 1. Overview

This document describes the design and architecture of an AI agent that autonomously searches for AI Engineer jobs at mid-sized "Middle America" companies. The agent filters out big tech (FAANG+) and startups, ranks jobs by relevance, and generates tailored application materials.

---

## 2. Pipeline Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        JOB SEARCH AGENT PIPELINE                         │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│  STAGE 1: SEARCH                                                         │
│  ─────────────────                                                       │
│  • Query: "AI Engineer" + location preferences                           │
│  • Sources: LinkedIn, Indeed, Greenhouse                                 │
│  • Extract: title, company, location, skills, salary, URL                │
│  • Logging: Search query, source, results count                          │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│  STAGE 2: FILTER - FAANG+ BLACKLIST                                      │
│  ──────────────────────────────────                                      │
│  • Exclude: Google, Meta, Amazon, Apple, Netflix, Microsoft, etc.        │
│  • Exclude: OpenAI, Anthropic, Nvidia, Uber, Airbnb, etc.               │
│  • Logging: Company name, INCLUDED/EXCLUDED, reason                      │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│  STAGE 3: FILTER - STARTUP EXCLUSION (<50 employees)                    │
│  ───────────────────────────────────────────────────                     │
│  • Detect: "seed", "series a", "founding team", "YC", etc.              │
│  • Detect: "employee #", "first hire", "early stage"                     │
│  • Logging: Company name, indicators found, INCLUDED/EXCLUDED            │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│  STAGE 4: FILTER - LOCATION (Optional Toggle)                            │
│  ─────────────────────────────────────────────                           │
│  • Filter by state: Iowa, Texas, etc.                                    │
│  • Include remote positions                                              │
│  • Logging: Location match, filter criteria                              │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│  STAGE 5: RANK - Top 10 Selection                                        │
│  ────────────────────────────────                                        │
│  • Skill Match (35%): Python, TensorFlow, MLflow alignment              │
│  • Title Match (25%): AI Engineer, ML Engineer similarity               │
│  • Location Match (15%): Preferred region proximity                      │
│  • Experience Match (10%): 3-5 years requirement                         │
│  • Company Match (5%): Target company preferences                        │
│  • Salary Match (10%): Meets minimum salary threshold                    │
│  • Logging: Score breakdown, rank position, match reasons                │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│  STAGE 6: TAILOR - Application Materials (Top 3)                         │
│  ───────────────────────────────────────────────                         │
│  • Resume: Keyword optimization, experience highlighting                 │
│  • Cover Letter: Company-specific, role-aligned messaging                │
│  • ATS Score: Compatibility assessment                                   │
│  • Logging: Changes made, keywords added, optimization steps             │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│  OUTPUT                                                                  │
│  ──────                                                                  │
│  • Ranked job list with match explanations                               │
│  • Tailored resumes for top 3 jobs                                       │
│  • Personalized cover letters                                            │
│  • Complete pipeline trace log                                           │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 3. Filter Heuristics

### 3.1 FAANG+ Blacklist

**Justification:** The assignment requires focusing on "Middle America" companies, excluding big tech.

| Category | Companies |
|----------|-----------|
| FAANG | Facebook/Meta, Amazon, Apple, Netflix, Google/Alphabet |
| Extended Big Tech | Microsoft, Tesla, Nvidia, OpenAI, Anthropic, DeepMind |
| Ride-sharing/Delivery | Uber, Lyft, DoorDash, Instacart |
| Fintech Giants | Stripe, PayPal, Coinbase, Robinhood |
| Social/Media | Twitter/X, LinkedIn, Spotify, Pinterest, Snap, TikTok |
| Enterprise | Salesforce, Oracle, IBM, Adobe, VMware |
| Cloud/Infra | Cloudflare, Twilio, Datadog, Snowflake |

**Implementation:**
```python
FAANG_BLACKLIST = [
    "facebook", "meta", "amazon", "apple", "netflix", "google",
    "microsoft", "openai", "anthropic", "nvidia", ...
]

def filter_faang_blacklist(jobs):
    return [job for job in jobs 
            if not any(faang in job.company.lower() 
                      for faang in FAANG_BLACKLIST)]
```

### 3.2 Startup Exclusion (<50 Employees)

**Justification:** Mid-sized companies provide stability while avoiding big tech culture.

| Indicator Type | Keywords |
|----------------|----------|
| Funding Stage | "seed", "pre-seed", "series a", "early stage" |
| Team Size | "employee #", "first hire", "small team", "10 employees" |
| Accelerators | "Y Combinator", "YC", "TechStars", "500 Startups" |
| Growth Stage | "stealth", "pre-launch", "MVP", "bootstrap" |

**Implementation:**
```python
STARTUP_INDICATORS = [
    "seed", "series a", "founding", "first hire",
    "stealth", "y combinator", "incubator", ...
]

def filter_startups(jobs):
    return [job for job in jobs
            if not any(indicator in job.description.lower()
                      for indicator in STARTUP_INDICATORS)]
```

### 3.3 Company Size Classification

| Size | Employee Count | Indicators |
|------|---------------|------------|
| Small (Startup) | <50 | Series A, seed, founding team |
| Mid-sized | 50-1000 | Series B/C, growth stage, regional |
| Large (Enterprise) | >1000 | Fortune 500, multinational, global |

---

## 4. Ranking Algorithm

### 4.1 Weighted Scoring Model

```
Total Score = Σ (Weight_i × Match_i)

Where:
- Skills:     35% weight, matches Python/TensorFlow/MLflow etc.
- Title:      25% weight, matches "AI Engineer", "ML Engineer"
- Location:   15% weight, matches preferred regions/remote
- Experience: 10% weight, matches 3-5 years requirement
- Company:    5%  weight, matches target company list
- Salary:     10% weight, meets minimum threshold
```

### 4.2 Skill Matching

**Process:**
1. Extract skills from user profile
2. Parse job description for skill mentions
3. Calculate intersection / profile skills
4. Bonus for exact skill matches

**Example:**
```
Profile Skills: [Python, TensorFlow, MLflow, AWS, Docker]
Job Skills:     [Python, PyTorch, MLflow, Kubernetes]
Matched:        [Python, MLflow] = 2/5 = 40% base match
Text Detection: "TensorFlow" found in description = +1
Final:          3/5 = 60% skill match
```

### 4.3 Top 10 Selection

Jobs are ranked by total score, top 10 selected for shortlist:

| Rank | Score | Company | Position | Key Match Reasons |
|------|-------|---------|----------|-------------------|
| 1 | 85% | Midwest Mfg Co | AI Engineer | 5 skills, Iowa, 4 yrs |
| 2 | 82% | AgriTech Solutions | ML Engineer | 4 skills, Remote |
| ... | ... | ... | ... | ... |
| 10 | 68% | Regional Health | Data Scientist | 3 skills, IL |

---

## 5. Tailoring Workflow

### 5.1 Resume Tailoring Process

```
┌──────────────────┐     ┌──────────────────┐     ┌──────────────────┐
│  Original Resume │────▶│  Keyword Engine  │────▶│  Tailored Resume │
└──────────────────┘     └──────────────────┘     └──────────────────┘
                                  │
                                  ▼
                         ┌──────────────────┐
                         │  Job Description │
                         │  - Required skills│
                         │  - Keywords       │
                         │  - Company values │
                         └──────────────────┘
```

**Steps:**
1. Parse job description for required skills and keywords
2. Identify matching experience from profile
3. Reorder/emphasize relevant accomplishments
4. Add missing keywords naturally
5. Calculate ATS compatibility score

### 5.2 Cover Letter Generation

**Template Structure:**
```
Opening:     Hook + specific company mention
Body 1:      Relevant experience alignment
Body 2:      Skill match demonstration
Body 3:      Cultural fit / company interest
Closing:     Call to action + availability
```

**Personalization Points:**
- Company name and mission
- Specific job title
- Key requirements addressed
- Relevant project examples
- Location/remote preference

### 5.3 ATS Optimization

| Factor | Weight | Optimization |
|--------|--------|--------------|
| Keywords | 40% | Include all required skills verbatim |
| Format | 20% | Simple formatting, no tables/graphics |
| Length | 15% | 1-2 pages for resume |
| Sections | 15% | Standard headings (Experience, Skills) |
| Contact | 10% | Clear contact information at top |

---

## 6. Logging and Traceability

### 6.1 Decision Log Structure

Every pipeline decision is logged with:
```json
{
  "timestamp": "2026-02-28T10:30:00",
  "stage": "filter_faang",
  "action": "EXCLUDED",
  "details": {
    "job": "AI Engineer",
    "company": "Google",
    "reason": "FAANG+ blacklist"
  }
}
```

### 6.2 Pipeline Trace Export

Full trace exported for report appendix:
- Total jobs searched
- Jobs filtered at each stage
- Ranking decisions with score breakdowns
- Tailoring changes made

---

## 7. Evaluation Metrics

### 7.1 Precision@10

```
Precision@10 = (Interview-worthy jobs in top 10) / 10
```

Using 20-job benchmark: 10 interview-worthy + 10 rejects.

### 7.2 Interview Yield

```
Interview Yield = (Human "Yes" ratings) / (Total ratings)
```

3 human raters score each shortlisted job.

### 7.3 Tailoring Quality

Human scoring (1-5 scale):
- Keyword incorporation
- Job relevance
- Professional tone
- Specificity
- ATS optimization

---

## 8. File Structure

```
linkedin-job-scraper/
├── linkedin_scraper/
│   ├── agent/
│   │   ├── __init__.py
│   │   ├── profile.py      # User profile parsing
│   │   ├── ranker.py       # Ranking + filters
│   │   ├── resume_tailor.py
│   │   ├── cover_letter.py
│   │   ├── evaluation.py   # Metrics + logging
│   │   └── agent.py        # Main orchestrator
│   ├── scraper.py          # LinkedIn scraper
│   ├── indeed_scraper.py
│   ├── greenhouse_scraper.py
│   └── multi_scraper.py
├── api/
│   └── main.py             # FastAPI backend
├── frontend/               # React UI
├── data/
│   ├── sample_resume.json  # Sample AI Engineer profile
│   └── benchmark_jobs.json # 20-job evaluation set
├── docs/
│   ├── DESIGN_DOCUMENT.md  # This document
│   ├── ETHICS.md           # Bias/ethics analysis
│   └── REFLECTIONS_TEMPLATE.md
└── README.md
```

---

## 9. Role Responsibilities

| Role | Primary Deliverables |
|------|---------------------|
| Product Lead | Requirements, sample resume, constraints |
| Agent Architect | Pipeline design, this document |
| Web Engineer | Scrapers, API integration |
| LLM Engineer | Ranking logic, tailoring prompts |
| Eval Lead | Benchmark, metrics, bias analysis |

---

## 10. Revision History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | Feb 2026 | Initial design document |
