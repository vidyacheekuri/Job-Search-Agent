# Filtering Tool – Rules (for Report)

The **Filtering Tool** applies the following rules to the job dataset. You can use this section in your assignment report to clearly explain the filtering logic.

---

## 1. Location preference

- **Rule:** Keep only jobs whose **location** matches at least one of the candidate’s **preferred locations** (e.g. `"United States"`, `"Remote"`, `"New York"`).
- **Implementation:** The job’s location string is compared (case-insensitive) to each preferred location; if any preferred term appears in the job location, the job is kept.
- **Default:** If the profile has no preferred locations, this rule is not applied (all locations pass).

---

## 2. Experience limit

- **Rule:** Keep only jobs where the **required years of experience** are less than or equal to the candidate’s **years of experience**.
- **Implementation:** If the job lists a numeric requirement (e.g. in “Years of Experience Required”), that value is parsed. The candidate must have `profile.years_experience >= required_years`; otherwise the job is excluded.
- **Default:** If the job does not specify a numeric requirement, this rule does not exclude the job.

---

## 3. Company exclusion

- **Rule:** Exclude jobs from a fixed **company exclusion list** (e.g. FAANG and similar large tech companies).
- **Implementation:** The job’s company name is compared (case-insensitive) against a set of excluded names (e.g. `meta`, `facebook`, `amazon`, `apple`, `netflix`, `google`, `alphabet`). If the company name contains any of these, the job is excluded.

---

## 4. Remote-only filter (optional)

- **Rule:** When **remote-only** is enabled, keep only jobs whose location indicates **remote** work.
- **Implementation:** Either the profile’s `remote_preference` is set to `"remote"`, or an explicit `remote_only=True` is passed. The job’s location string must contain the word `"remote"` (case-insensitive); otherwise the job is excluded.
- **Default:** If remote-only is not enabled, this rule is not applied.

---

## Order of application

In code, the order applied is: **company exclusion** → **remote-only (if enabled)** → **location preference** → **experience limit** → **skills overlap** (at least one skill in common). Jobs that pass all applicable rules are kept.

---

*Implementation: `assignment_agent.py` (`filtering_tool`) and `api/main.py` (`_filter_csv_jobs`).*
