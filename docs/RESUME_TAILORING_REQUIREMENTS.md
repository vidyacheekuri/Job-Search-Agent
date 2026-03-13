# Resume Tailoring Requirements (for Report)

The agent **tailors the resume for only the top-ranked job**. These rules are implemented **app-wide** (live search, agent run, middle-America, and offline CSV). The following can be used in your report.

---

## 1. Tailor for only the top-ranked job

- The Resume Tailoring Tool is called **once**, for the **top-ranked job** (rank 1) after the Ranking Tool runs.
- In the LLM-driven flow, the agent calls `resume_tailoring_tool(job_rank=1)`. In the fixed pipeline, the best job is `ranked[0]`.
- No tailoring is performed for other jobs; only the single best match gets a tailored resume.

---

## 2. Rewrite the Professional Summary

- The **Professional Summary** is **rewritten** for the target job.
- The system generates a new 2–3 sentence summary that incorporates the job title, required skills, and the candidate’s experience.
- Generation uses the LLM (OpenAI/Claude/Ollama) when configured, or a heuristic template otherwise.
- The rest of the resume is **not** regenerated; only the summary block is replaced.

---

## 3. Modify exactly 2 experience bullet points

- **Exactly two** experience bullet points are **modified** for the job.
- Those two bullets are derived from the candidate’s **existing** experience (from their profile). They are reworded or reordered to better align with the job (e.g. action verbs, job-related keywords, aligned skills).
- No additional experience bullets are created; the rest of the experience section is unchanged.
- Output is clearly labeled as **“Modified Experience Bullet Points (exactly 2)”**.

---

## 4. Highlight aligned skills

- **Aligned skills** (skills that match the job) are **highlighted** in the tailoring output.
- The Ranking Tool’s `matched_skills` (and the tailor’s keyword overlap) are used to list which profile skills align with the job.
- The tailored output includes a **“Highlight Aligned Skills”** section listing these skills, and the two modified bullets are written to emphasize them where relevant.

---

## 5. Do NOT regenerate the entire resume

- The system **does not** regenerate the entire resume.
- Only the following are produced or changed:
  - **Rewritten Professional Summary**
  - **Exactly 2 modified experience bullet points**
  - **Highlighted aligned skills** (called out explicitly)
- All other sections (contact, other experience, education, etc.) are **unchanged** from the candidate’s profile. The deliverable states that only the summary and these two bullets were modified.

---

*Implementation: `assignment_agent.py` (`resume_tailoring_tool`, `_get_two_modified_bullets`), `linkedin_scraper/agent/resume_tailor.py` (`ResumeTailor`).*
