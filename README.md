# Job Search Agent — Career Match

An AI-powered job search app: create a profile, search and rank AI/ML jobs (live or from a CSV dataset), and get tailored resumes and cover letters. No API keys required to run.

---

## What you need

- **Python 3.10+**
- **Node.js 18+**
- A terminal

---

## Run the app (after cloning)

**1. Clone and go into the project**

```bash
git clone <repo-url>
cd Job-Search-Agent
```

**2. Install Python dependencies**

```bash
pip install -r requirements.txt
```

**3. Install frontend dependencies**

```bash
cd frontend
npm install
cd ..
```

**4. Start the backend** (leave this terminal open)

```bash
python api/main.py
```

You should see something like: `Uvicorn running on http://0.0.0.0:8000`

**5. Start the frontend** (open a **new** terminal)

```bash
cd Job-Search-Agent/frontend
npm run dev
```

You should see a local URL, usually: `http://localhost:5173`

**6. Open the app**

In your browser go to: **http://localhost:5173**

Create a profile, then use **AI Agent** to search and rank jobs (live or from the CSV dataset), generate resumes, and run evaluation.

---

## Optional: LLM reasoning

The app can show an “LLM Reasoning & Trace” and use an LLM for resume text. To enable:

- **Ollama (local):** Install [Ollama](https://ollama.ai), run `ollama pull llama3.2`, then start the backend with:
  ```bash
  LLM_PROVIDER=ollama python api/main.py
  ```
- **OpenAI or Claude:** Set `OPENAI_API_KEY` or `ANTHROPIC_API_KEY` in your environment (or in a `.env` file in the project root). The app will use it for reasoning and resume generation when available.

---

## If something goes wrong

| Problem | What to do |
|--------|------------|
| “Could not connect to the server” | Start the backend first (`python api/main.py`) and leave it running. |
| “Module not found” | Run `pip install -r requirements.txt` from the project root. |
| “npm: command not found” | Install Node.js from [nodejs.org](https://nodejs.org). |
| Port 8000 or 5173 already in use | Stop the other app using that port, or use a different port. |
| “Ollama unavailable” | Install Ollama and run `ollama pull llama3.2`, or set an OpenAI/Claude API key. |

---

## Use responsibly

For personal use only. Always review AI-generated resumes and cover letters before sending to employers.
