# LinkedIn Job Scraper

A Python CLI tool and web application for scraping job listings from LinkedIn's public job search pages.

## Features

- **CLI Tool**: Search jobs from the command line
- **Web UI**: Modern React dashboard with filters
- **API**: FastAPI backend for programmatic access
- **Export**: Save results to CSV or JSON
- **Filters**: Job type, remote, experience, salary, Easy Apply, and more

## Installation

```bash
# Clone the repository
git clone https://github.com/AdithyaReddyGeeda/Linkedin-job-scraper.git
cd Linkedin-job-scraper

# Install Python dependencies
pip install -r requirements.txt
pip install -e .
```

## Usage

### Option 1: Command Line

```bash
# Basic search
linkedin-jobs search "software engineer" --location "San Francisco"

# With filters
linkedin-jobs search "python developer" \
  --location "Remote" \
  --job-type full-time \
  --experience entry-level \
  --limit 50 \
  --output jobs.csv

# Easy Apply jobs with full descriptions
linkedin-jobs search "frontend developer" --easy-apply --details
```

### Option 2: Web UI

**Terminal 1 - Start the API server:**
```bash
cd api
pip install fastapi uvicorn
python main.py
```

**Terminal 2 - Start the frontend:**
```bash
cd frontend
npm install
npm run dev
```

Open http://localhost:5173 in your browser.

## CLI Options

| Option | Short | Description |
|--------|-------|-------------|
| `--location` | `-l` | City or region |
| `--job-type` | `-t` | full-time, part-time, contract, temporary, volunteer, internship |
| `--remote` | `-r` | on-site, remote, hybrid |
| `--experience` | `-e` | internship, entry-level, associate, senior, director, executive |
| `--date-posted` | `-d` | 24hr, past-week, past-month |
| `--salary` | `-s` | Minimum salary: 40000, 60000, 80000, 100000, 120000 |
| `--sort-by` | | recent, relevant |
| `--limit` | `-n` | Maximum number of jobs (default: 25) |
| `--output` | `-o` | Output file path (CSV or JSON) |
| `--details` | `-D` | Fetch full job descriptions (slower) |
| `--easy-apply` | | Filter to Easy Apply jobs only |
| `--under-10-applicants` | | Filter to jobs with <10 applicants |

## API Endpoints

- `GET /` - Health check
- `GET /api/search` - Search for jobs

Example:
```bash
curl "http://localhost:8000/api/search?keyword=python&location=remote&limit=10"
```

## Project Structure

```
linkedin-job-scraper/
├── linkedin_scraper/     # Core scraper module
│   ├── cli.py           # CLI commands
│   ├── scraper.py       # LinkedIn scraping logic
│   └── exporter.py      # CSV/JSON export
├── api/                  # FastAPI backend
│   └── main.py
├── frontend/             # React web UI
│   ├── src/
│   └── package.json
├── requirements.txt
├── setup.py
└── README.md
```

## Disclaimer

This tool scrapes publicly available job listings from LinkedIn. Use responsibly and respect LinkedIn's Terms of Service. Consider implementing appropriate rate limiting for production use.

## License

MIT
