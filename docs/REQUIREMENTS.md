# Requirements Document

**Product Lead Deliverable**  
**AI for Engineers - Group Assignment**

---

## 1. Project Scope

**Middle America Job and Application Agent**: An AI agent that autonomously browses job boards to find AI Engineer positions at mid-sized "Middle America" companies (excluding big tech and startups), then tailors resumes and cover letters for the top matches.

---

## 2. Constraints (TA Verification Points)

### 2.1 FAANG+ Blacklist
- **Requirement**: Exclude big tech companies
- **Definition**: 40+ companies including Google, Meta, Amazon, Apple, Netflix, Microsoft, OpenAI, Anthropic, Nvidia, Uber, Airbnb, Stripe, etc.
- **Implementation**: `JobRanker.FAANG_BLACKLIST` in `linkedin_scraper/agent/ranker.py`
- **Enforcement**: Applied in Stage 2 of pipeline via `filter_faang_blacklist()`

### 2.2 Startup Exclusion (≥50 Employees Heuristic)
- **Requirement**: Exclude startups (companies with <50 employees)
- **Heuristic**: Detect startup indicators in job/company text: "seed", "series a", "early stage", "Y Combinator", "first hire", "employee #", etc.
- **Implementation**: `JobRanker.STARTUP_INDICATORS` in `linkedin_scraper/agent/ranker.py`
- **Enforcement**: Applied in Stage 3 via `filter_startups()`

### 2.3 Company Size
- **Target**: Mid-sized companies (50-1000 employees)
- **Indicators**: "growth stage", "series b/c", "regional", "mid-size"

---

## 3. Sample Resume Profile

**Name**: Alex Johnson  
**Experience**: 4 years (3-5 year target per assignment)  
**Skills**: Python, TensorFlow, MLflow, PyTorch, NLP, Computer Vision  
**Location**: Des Moines, Iowa (Midwest preference)  
**Target Roles**: AI Engineer, ML Engineer, Senior AI Engineer  

**Full profile**: `data/sample_resume.json`

---

## 4. Pipeline Requirements

1. **Search**: Extract title, company, location, skills, salary, URL
2. **Filter**: FAANG blacklist + startup exclusion
3. **Rank**: Top 10 by skill match, location preference, recency
4. **Tailor**: Resume + cover letter for top 3 jobs

---

## 5. Deliverables Checklist

| Item | Location |
|------|----------|
| Requirements doc | `docs/REQUIREMENTS.md` (this file) |
| Sample resume | `data/sample_resume.json` |
| Constraint definitions | Section 2 above |
