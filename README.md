# LinkedIn Job Scraper

A Python CLI tool and web application for searching job listings from LinkedIn.

## Features

- **CLI Tool** - Search jobs from the command line
- **Web UI** - Modern React dashboard with filters
- **API** - FastAPI backend for programmatic access
- **Export** - Save results to CSV or JSON
- **Filters** - Job type, remote, experience, salary, Easy Apply, and more

## Quick Start

### Option 1: Web UI

**Terminal 1 - Start API:**
```bash
cd linkedin-job-scraper
pip install -r requirements.txt
python api/main.py
```

**Terminal 2 - Start Frontend:**
```bash
cd linkedin-job-scraper/frontend
npm install
npm run dev
```

Open **http://localhost:5173** in your browser.

### Option 2: Command Line

```bash
pip install -e .
linkedin-jobs search "software engineer" --location "San Francisco"
```

## CLI Usage

```bash
# Basic search
linkedin-jobs search "software engineer" --location "Remote"

# With filters
linkedin-jobs search "python developer" \
  --job-type full-time \
  --experience entry-level \
  --limit 50 \
  --output jobs.csv

# Easy Apply jobs with full descriptions
linkedin-jobs search "data scientist" --easy-apply --details -o results.json
```

## CLI Options

| Option | Short | Description |
|--------|-------|-------------|
| `--location` | `-l` | City or region |
| `--job-type` | `-t` | full-time, part-time, contract, internship |
| `--remote` | `-r` | on-site, remote, hybrid |
| `--experience` | `-e` | entry-level, associate, senior, director, executive |
| `--date-posted` | `-d` | 24hr, past-week, past-month |
| `--salary` | `-s` | Minimum: 40000, 60000, 80000, 100000, 120000 |
| `--limit` | `-n` | Max results (default: 25) |
| `--output` | `-o` | Export to CSV or JSON |
| `--details` | `-D` | Fetch full job descriptions |
| `--easy-apply` | | Easy Apply jobs only |
| `--under-10-applicants` | | Jobs with <10 applicants |

## API

The API runs on `http://localhost:8000`.

```bash
# Search endpoint
curl "http://localhost:8000/api/search?keyword=python&location=remote&limit=10"
```

## Project Structure

```
linkedin-job-scraper/
├── linkedin_scraper/     # Core scraper
│   ├── cli.py           # CLI interface
│   ├── scraper.py       # LinkedIn scraping
│   └── exporter.py      # CSV/JSON export
├── api/                  # FastAPI backend
│   └── main.py
├── frontend/             # React web UI
│   └── src/
├── requirements.txt
└── setup.py
```

## Requirements

- Python 3.10+
- Node.js 18+ (for web UI)

## Disclaimer

This tool scrapes publicly available job listings from LinkedIn. Use responsibly and respect LinkedIn's Terms of Service.

## License

MIT
