# Job Search Agent

A simple app that helps you find AI/ML jobs, see how well they match your profile, and get a tailored resume for the best match. No API keys needed to run it.

---

## What You Need First

- **Python 3.10 or newer** — [Download](https://www.python.org/downloads/)
- **Node.js 18 or newer** — [Download](https://nodejs.org/)
- A terminal (Terminal on Mac, Command Prompt or PowerShell on Windows)

---

## How to Run the App (Step by Step)

### 1. Open the project folder

```bash
cd Job-Search-Agent
```

*(If you just cloned the repo, you're already in the right place.)*

### 2. Install Python packages

```bash
pip install -r requirements.txt
```

If that fails, try:

```bash
pip3 install -r requirements.txt
```

### 3. Install frontend packages

```bash
cd frontend
npm install
cd ..
```

### 4. Start the backend (keep this window open)

Open a terminal and run:

```bash
python api/main.py
```

You should see something like: `Uvicorn running on http://0.0.0.0:8000`. Leave this terminal open.

### 5. Start the frontend (use a second terminal)

Open a **new** terminal, go to the project folder, then run:

```bash
cd frontend
npm run dev
```

You should see a local URL, usually: `http://localhost:5173`

### 6. Open the app in your browser

In your browser, go to: **http://localhost:5173**

You should see the Job Search Agent page. Create a profile, then search and rank jobs.

---

## What This App Does

- **Search jobs** — From the web (LinkedIn, etc.) or from a built-in list of 20–30 AI/ML jobs in a CSV file.
- **Filter jobs** — By location, experience, and company (e.g. skip big tech if you want).
- **Rank jobs** — Shows a score for each job based on how well it fits your profile.
- **Tailor your resume** — Rewrites your summary and two bullet points for the top job and highlights matching skills.
- **Cover letters** — Can generate a cover letter for a job.

---

## Running Only the Assignment Script (No Web UI)

If you just want to run the assignment pipeline (CSV jobs → filter → rank → tailor) from the command line:

```bash
python assignment_agent.py
```

Make sure you're in the `Job-Search-Agent` folder. The script reads jobs from `data/jobs_dataset.csv` and prints the ranked list and tailored resume.

**Optional:** For the AI to *choose* which step to do next (instead of a fixed order), set one of these before running:

- `OPENAI_API_KEY=your-key-here`
- or `ANTHROPIC_API_KEY=your-key-here`

You can put them in a `.env` file in the project root, or type them in the terminal (e.g. `export OPENAI_API_KEY=sk-...` on Mac/Linux).

---

## Common Problems

| Problem | What to do |
|--------|------------|
| **"Could not connect to the server"** | Start the backend first: `python api/main.py` in the project folder. Keep that terminal open. |
| **"Module not found"** | Run `pip install -r requirements.txt` (or `pip3 install -r requirements.txt`) in the project folder. |
| **"npm: command not found"** | Install Node.js from https://nodejs.org/ and try again. |
| **"Port already in use"** | Something else is using port 8000 or 5173. Close that app or use a different port. |
| **Jobs don't load** | If using live search, the job site may be slow or limiting requests. Try again later or use "Offline CSV Dataset" in the app. |

---

## Project Folders (Quick Reference)

| Folder / File | What it is |
|---------------|------------|
| `api/main.py` | Backend server — run this first. |
| `frontend/` | Web interface — run `npm run dev` from here. |
| `data/jobs_dataset.csv` | List of 20–30 AI/ML jobs used by the offline/assignment flow. |
| `assignment_agent.py` | Script to run filter → rank → tailor from the command line. |
| `docs/` | Extra docs (filtering rules, ranking, report template). |

---

## Optional: API Keys for Smarter AI

The app works **without** any API keys. If you want better resume and reasoning quality:

- **OpenAI:** Create a key at [platform.openai.com](https://platform.openai.com/), then set `OPENAI_API_KEY` in a `.env` file or in your terminal.
- **Claude:** Set `ANTHROPIC_API_KEY` the same way.
- **Ollama (local):** Install [Ollama](https://ollama.ai), run a model (e.g. `llama3`), and set `LLM_PROVIDER=ollama` if you want to use it.

---

## Report and Assignment Docs

- **Report template (3–4 pages):** `docs/ASSIGNMENT_REPORT.md` — fill in Top 3 jobs, resume snippet, and ethics reflection.
- **Filtering rules:** `docs/FILTERING_RULES.md`
- **Ranking system:** `docs/RANKING_SYSTEM.md`
- **Resume tailoring:** `docs/RESUME_TAILORING_REQUIREMENTS.md`
- **Checklist:** `docs/ASSIGNMENT_CHECKLIST.md`

---

## Use Responsibly

Use for personal job searching only. Don’t overload job sites with requests. Always review AI-generated resumes and cover letters before sending.
