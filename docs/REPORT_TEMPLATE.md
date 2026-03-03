# Report: Middle America Job and Application Agent

**AI for Engineers - Group Assignment**  
**Target Length: 8-10 pages**

---

## 1. Introduction and Requirements (1-1.5 pages)

### 1.1 Project Overview
- Brief description of the agent and its purpose
- Target user: AI Engineer job seekers at mid-sized "Middle America" companies
- Key differentiator: Excludes FAANG+ and startups, focuses on skill/location/recency match

### 1.2 Requirements Summary
- **Functional**: Search → Filter → Rank → Tailor pipeline
- **Constraints**: FAANG blacklist, startup exclusion (<50 employees heuristic)
- **Sample Resume**: Alex Johnson, 4 years experience, Python/TensorFlow/MLflow, Des Moines

### 1.3 Learning Objectives Addressed
- Web interaction and scraping
- LLM personalization and prompt engineering
- Constraint-based filtering and ranking
- Hiring-focused evaluation and benchmarking
- Ethical AI and bias analysis

---

## 2. Design and Implementation Details (2-2.5 pages)

### 2.1 Architecture Overview
- Reference pipeline diagram from `docs/DESIGN_DOCUMENT.md`
- Explain separation of concerns: Scraper, Ranker, Tailor, Evaluator

### 2.2 Pipeline Stages
1. **Search**: Sources (LinkedIn, Indeed, Greenhouse), data extracted
2. **Filter**: FAANG blacklist, startup heuristics, location toggle
3. **Rank**: Weighted scoring (skills 35%, title 20%, location 15%, recency 10%, etc.)
4. **Tailor**: Resume keyword optimization, cover letter generation

### 2.3 Filter Heuristics
- FAANG+ companies excluded (40+)
- Startup indicators: seed, series a, YC, etc.
- Location filter: Iowa, Texas, Remote options

### 2.4 Logging and Traceability
- Decision log structure
- Pipeline trace export for appendix

---

## 3. Evaluation Results (2-2.5 pages)

### 3.1 Hiring Simulation (Priority)
- **20-job benchmark**: 10 interview-worthy, 10 rejects
- **Precision@10**: [Fill: (interview-worthy in top 10) / 10]
- **Interview Yield**: [Fill: Human "yes" ratings / total ratings]
- Human rating process: 3 raters, Yes/No per job

### 3.2 Tailoring Quality
- Human scores (1-5 scale) for top 3 tailored resumes
- Criteria: keyword incorporation, relevance, professional tone, specificity, ATS optimization
- Comparison to manual baseline (if available)

### 3.3 Filter Toggle Experiment
- **Iowa-only mode**: [Fill: Results, top matches]
- **Texas mode**: [Fill: Results, how results adapted]
- Demonstrate adaptation to location filter change

### 3.4 Metrics Summary Table
| Metric | Value |
|--------|-------|
| Precision@10 | |
| Interview Yield | |
| Avg ATS Score | |
| Avg Match Score | |

---

## 4. Bias and Ethics Analysis (1.5-2 pages)

### 4.1 Tailoring Fairness
- How does the agent avoid misrepresentation?
- Truthfulness of AI-generated content

### 4.2 Potential Biases
- Location bias (geographic distribution)
- Company size bias
- Salary range bias
- Experience level bias

### 4.3 Responsible Usage
- Personal job searching only
- Review AI-generated content before submission
- Respect rate limits and ToS

### 4.4 Recommendations
- Mitigation strategies from `docs/ETHICS.md`

---

## 5. Conclusion (0.5 page)

- Summary of achievements
- Limitations
- Future improvements

---

## Appendix A: Agent Trace

*(Paste or reference full pipeline trace from `pipeline_trace.json`)*

- Search query and results count
- Filter decisions (included/excluded per job)
- Ranking score breakdowns
- Tailoring changes made

---

## Appendix B: Sample Outputs

- Top 10 ranked jobs with match reasons
- Sample tailored resume (before/after)
- Sample cover letter excerpt

---

*Fill in bracketed sections with actual evaluation data from your runs.*
