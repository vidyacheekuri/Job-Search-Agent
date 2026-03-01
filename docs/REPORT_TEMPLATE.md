# Middle America Job Search Agent
## AI for Engineers - Group Assignment Report

**Team Members:**
1. [Name] - Product Lead
2. [Name] - Agent Architect
3. [Name] - Web Engineer
4. [Name] - LLM Engineer
5. [Name] - Eval Lead

**Date:** February 2026

---

## Table of Contents
1. [Introduction](#1-introduction)
2. [Requirements and Constraints](#2-requirements-and-constraints)
3. [Design and Implementation](#3-design-and-implementation)
4. [Evaluation Results](#4-evaluation-results)
5. [Bias and Ethics Analysis](#5-bias-and-ethics-analysis)
6. [Appendix: Agent Trace](#appendix-agent-trace)

---

## 1. Introduction

### 1.1 Problem Statement

[Describe the problem: Finding AI Engineer jobs at mid-sized "Middle America" companies while avoiding big tech and startups. Explain why this is a meaningful task for job seekers.]

### 1.2 Solution Overview

[Provide a high-level overview of your agent: an AI-powered job search system that searches, filters, ranks, and tailors applications autonomously.]

### 1.3 Key Contributions

- **Multi-source job aggregation:** LinkedIn, Indeed, Greenhouse
- **FAANG+ blacklist filtering:** Excludes 40+ big tech companies
- **Startup detection heuristics:** Filters companies with <50 employees
- **AI-powered ranking:** Weighted scoring across 6 dimensions
- **Application tailoring:** Personalized resumes and cover letters

---

## 2. Requirements and Constraints

### 2.1 Functional Requirements

| Requirement | Description | Status |
|-------------|-------------|--------|
| Job Search | Search multiple job boards for AI Engineer roles | ✅ |
| Data Extraction | Extract title, company, location, skills, salary, URL | ✅ |
| FAANG Filter | Exclude big tech companies | ✅ |
| Startup Filter | Exclude startups (<50 employees) | ✅ |
| Job Ranking | Rank top 10 by relevance | ✅ |
| Resume Tailoring | Generate customized resumes | ✅ |
| Cover Letter | Generate personalized cover letters | ✅ |

### 2.2 Filter Constraints

**FAANG+ Blacklist (40+ companies):**
- FAANG: Facebook/Meta, Amazon, Apple, Netflix, Google
- Big Tech: Microsoft, Tesla, Nvidia, OpenAI, Anthropic
- [List additional categories...]

**Startup Exclusion Heuristics:**
- Funding indicators: "seed", "series a", "early stage"
- Team size indicators: "employee #", "first hire", "small team"
- Accelerator mentions: "Y Combinator", "TechStars"

### 2.3 Sample Resume Definition

[Include details of the sample AI Engineer profile used:]
- **Experience:** 4 years
- **Skills:** Python, TensorFlow, PyTorch, MLflow, AWS
- **Location Preference:** Iowa, Illinois, Minnesota (Midwest)
- **Minimum Salary:** $120,000

---

## 3. Design and Implementation

### 3.1 Pipeline Architecture

[Include the pipeline diagram from DESIGN_DOCUMENT.md]

```
Search → Filter FAANG → Filter Startups → Filter Location → Rank → Tailor
```

### 3.2 Implementation Details

#### Search Module
- **Sources:** LinkedIn, Indeed, Greenhouse
- **Query:** "AI Engineer" + location
- **Parallelization:** ThreadPoolExecutor for concurrent searches

#### Filter Module
- **FAANG Filter:** String matching against blacklist
- **Startup Filter:** Keyword detection in job descriptions
- **Location Filter:** Toggle-able by state (Iowa, Texas, etc.)

#### Ranking Module
- **Algorithm:** Weighted sum scoring
- **Weights:** Skills (35%), Title (25%), Location (15%), Experience (10%), Company (5%), Salary (10%)

#### Tailoring Module
- **Resume:** Keyword injection, experience reordering
- **Cover Letter:** Template-based generation with company personalization
- **ATS Score:** Heuristic compatibility assessment

### 3.3 Code Structure

[Include file tree and key modules]

### 3.4 Decision Logging

All pipeline decisions are logged with:
- Timestamp
- Stage (search, filter, rank, tailor)
- Action (included/excluded)
- Reason

---

## 4. Evaluation Results

### 4.1 Benchmark Dataset

| Category | Count | Description |
|----------|-------|-------------|
| Interview-worthy | 10 | Jobs matching profile criteria |
| Rejects | 10 | FAANG, startups, mismatched roles |
| **Total** | **20** | Complete benchmark set |

### 4.2 Precision@10 Results

[Run the agent on the benchmark and report results]

| Metric | Value |
|--------|-------|
| Precision@10 | [X.X] |
| Interview Yield | [X.X%] |

**Top 10 Shortlist:**

| Rank | Company | Position | Score | Interview? |
|------|---------|----------|-------|------------|
| 1 | [Company] | [Position] | XX% | Yes/No |
| 2 | [Company] | [Position] | XX% | Yes/No |
| ... | ... | ... | ... | ... |

### 4.3 Human Ratings

**Raters:** [Name 1], [Name 2], [Name 3]

| Job | Rater 1 | Rater 2 | Rater 3 | Consensus |
|-----|---------|---------|---------|-----------|
| Job 1 | Yes | Yes | Yes | Yes |
| Job 2 | Yes | No | Yes | Yes |
| ... | ... | ... | ... | ... |

**Interview Yield:** [X/10] = [XX%]

### 4.4 Tailoring Quality Scores

| Document | Keyword | Relevance | Tone | Specificity | ATS | Overall |
|----------|---------|-----------|------|-------------|-----|---------|
| Resume 1 | 4 | 4 | 5 | 4 | 4 | 4.2 |
| Resume 2 | 4 | 5 | 4 | 4 | 5 | 4.4 |
| Resume 3 | 5 | 4 | 4 | 5 | 4 | 4.4 |
| Cover 1 | 4 | 5 | 5 | 4 | 4 | 4.4 |
| Cover 2 | 4 | 4 | 5 | 4 | 4 | 4.2 |
| Cover 3 | 5 | 5 | 4 | 4 | 5 | 4.6 |

### 4.5 Filter Toggle Experiment

**Experiment:** Change location filter from "Iowa" to "Texas"

| Filter Setting | Jobs Before | Jobs After | Top Match |
|----------------|-------------|------------|-----------|
| Iowa-only | 50 | 12 | Midwest Mfg Co |
| Texas-only | 50 | 15 | Austin Analytics |
| Remote-only | 50 | 20 | Remote Tech Inc |

[Discuss adaptation behavior and results]

---

## 5. Bias and Ethics Analysis

### 5.1 Potential Biases Identified

| Bias Type | Description | Mitigation |
|-----------|-------------|------------|
| Geographic | Preference for certain states | Include remote options |
| Company Size | May miss good small companies | Adjustable thresholds |
| Keyword | Over-reliance on exact matches | Semantic similarity |
| Experience | May filter valid candidates | Flexible year ranges |

### 5.2 Fairness in Tailoring

[Discuss how the tailoring process maintains fairness:]
- No demographic information used
- Focus on skills and experience only
- Transparent optimization criteria

### 5.3 Hiring Equity Impact

[Discuss broader implications:]
- **Positive:** Helps candidates from non-coastal areas find opportunities
- **Concern:** May reinforce existing hiring patterns
- **Recommendation:** Regular audits of filter criteria

### 5.4 Transparency and Explainability

[Discuss how the agent explains its decisions:]
- Match score breakdown provided
- Filter reasons logged
- Tailoring changes documented

---

## Appendix: Agent Trace

### A.1 Sample Pipeline Execution

```json
{
  "timestamp": "2026-02-28T10:00:00",
  "stage": "search",
  "action": "SEARCH",
  "details": {
    "query": "AI Engineer Iowa",
    "source": "linkedin",
    "results_found": 45
  }
}
```

[Include 5-10 representative log entries showing the pipeline flow]

### A.2 Filter Statistics

| Stage | Input | Output | Filtered |
|-------|-------|--------|----------|
| Search | - | 150 | - |
| FAANG Filter | 150 | 120 | 30 |
| Startup Filter | 120 | 95 | 25 |
| Location Filter | 95 | 45 | 50 |
| Ranking | 45 | 10 | 35 |

### A.3 Top 3 Tailored Documents

[Include excerpts from tailored resumes and cover letters]

---

## References

1. [Any external resources, APIs, or libraries used]
2. LinkedIn Jobs API
3. Indeed Job Search
4. Greenhouse Job Boards

---

**Word Count:** [Approximately 2500-3000 words for 8-10 pages]

**Submission Checklist:**
- [ ] Report (8-10 pages)
- [ ] Code repository with README
- [ ] Demo video (8-10 minutes)
- [ ] Individual reflections (5)
- [ ] Peer assessments (5)
