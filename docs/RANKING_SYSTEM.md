# Ranking Tool – System (for Report)

The **Ranking Tool** produces a **ranked list with clear scores** and is designed so you can **clearly display** the **ranked job list with scores** and the **Top 3 jobs**. You can use this section in your assignment report to explain the ranking system.

---

## Requirements met

1. **Assign scores based on skill matching**  
   Each job gets a **skill match score** (0–100) from overlap between the job’s required skills and the candidate’s profile skills (including synonyms and fuzzy matching). This is a main input to the overall score.

2. **Consider experience alignment**  
   An **experience match score** (0–100) is computed by comparing the job’s required experience level (or years) with the candidate’s years of experience. This is included in the weighted overall score.

3. **Optionally consider location match**  
   A **location match score** (0–100) is computed from the job’s location and the candidate’s preferred locations (including “Remote”). It is included in the weighted overall score.

4. **Output a ranked list with clear scores**  
   Jobs are sorted by **overall score** (0–100). Each job in the list has a single **score** and optional breakdown (skill, title, location, experience). The list is returned and displayed in order, highest score first.

5. **Clearly display: Ranked job list with scores**  
   The UI and the assignment script both show the full ranked list; each row/card shows the job and its **score** (e.g. `72%`).

6. **Clearly display: Top 3 jobs**  
   The **Top 3 jobs** are explicitly labeled and shown first (e.g. “Top 3 jobs” section in the UI and “Top 3 jobs by score” in the script output).

---

## How the overall score is computed

The overall score is a **weighted sum** of (each factor is 0–1, then scaled to 0–100):

- **Skill matching** (weight 0.35) – overlap between profile skills and job skills/description  
- **Title match** (weight 0.20) – fit between profile title and job title  
- **Location match** (weight 0.15) – fit between preferred locations and job location  
- **Recency** (weight 0.10) – how recent the posting is  
- **Experience alignment** (weight 0.10) – match on required vs candidate experience  
- **Company** (weight 0.05) – target company or neutral  
- **Salary** (weight 0.05) – salary fit if data available  

So the Ranking Tool **assigns scores based on skill matching**, **considers experience alignment** and **optionally location match**, and **outputs a ranked list with clear scores**, with **ranked job list with scores** and **Top 3 jobs** clearly displayed.

---

*Implementation: `linkedin_scraper/agent/ranker.py` (`JobRanker`), `assignment_agent.py` (`ranking_tool`), and API `_rank_csv_jobs`.*
