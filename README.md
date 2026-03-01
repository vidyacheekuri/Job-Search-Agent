# LinkedIn Job Scraper

Search and discover job opportunities from LinkedIn with a modern web interface or command line.

![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)
![React](https://img.shields.io/badge/React-18-61DAFB.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.109+-009688.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)

## Features

| Feature | Description |
|---------|-------------|
| **Web Dashboard** | Clean React UI with search and filters |
| **Dark Mode** | Toggle between light and dark themes |
| **Search History** | Quick access to recent searches |
| **Save Jobs** | Bookmark jobs with personal notes |
| **Application Tracker** | Track applied jobs with status updates |
| **Company Info** | Quick links to LinkedIn, Glassdoor, Google |
| **Salary Insights** | Estimated salary when not provided |
| **Pagination** | Navigate through large result sets |
| **Mobile Responsive** | Works on all devices |
| **CLI Tool** | Search directly from your terminal |
| **REST API** | Integrate with your own applications |
| **Advanced Filters** | Job type, location, experience, salary, remote |
| **Easy Apply** | Filter for LinkedIn Easy Apply jobs |
| **Export** | Save results to CSV or JSON |
| **Full Descriptions** | Fetch complete job details |

## Screenshots

### Web Interface
Search for jobs with an intuitive interface featuring real-time results, dark mode, and job tracking.

### Terminal Output
Beautiful formatted tables with job listings directly in your terminal.

---

## Installation

### Prerequisites
- Python 3.10 or higher
- Node.js 18+ (for web UI only)

### Setup

```bash
# Clone the repository
git clone https://github.com/AdithyaReddyGeeda/Linkedin-job-scraper.git
cd Linkedin-job-scraper

# Install Python dependencies
pip install -r requirements.txt

# Install CLI tool
pip install -e .
```

---

## Usage

### Web Interface

The easiest way to use the scraper. Requires two terminal windows.

**Terminal 1 - Start the API server:**
```bash
python api/main.py
```

**Terminal 2 - Start the web app:**
```bash
cd frontend
npm install
npm run dev
```

Open **http://localhost:5173** in your browser.

#### Web UI Features

| Feature | How to Use |
|---------|------------|
| **Dark Mode** | Click the moon/sun icon in the header |
| **Search History** | Click on recent search chips below the search bar |
| **Save Jobs** | Click the bookmark icon on any job card |
| **Track Applications** | Click "Mark Applied" on a job card |
| **Company Info** | Click on a company name to view links |
| **Pagination** | Use page numbers at the bottom of results |

---

### Command Line

For quick searches and automation.

```bash
# Basic search
linkedin-jobs search "software engineer" --location "San Francisco"

# Remote jobs with filters
linkedin-jobs search "python developer" \
  --location "Remote" \
  --job-type full-time \
  --experience entry-level \
  --limit 50

# Easy Apply jobs only
linkedin-jobs search "data scientist" --easy-apply

# Export to file
linkedin-jobs search "frontend developer" -o jobs.csv

# Get full job descriptions
linkedin-jobs search "backend engineer" --details -o detailed_jobs.json
```

---

### REST API

For integrating with other applications.

```bash
# Start the server
python api/main.py
```

**Endpoints:**

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Health check |
| GET | `/api/search` | Search for jobs |

**Example Request:**
```bash
curl "http://localhost:8000/api/search?keyword=python&location=remote&limit=10"
```

**Query Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `keyword` | string | Job title or search terms (required) |
| `location` | string | City, state, or "Remote" |
| `job_type` | string | full-time, part-time, contract, internship |
| `remote` | string | remote, hybrid, on-site |
| `experience` | string | entry-level, associate, senior, director, executive |
| `date_posted` | string | 24hr, past-week, past-month |
| `salary` | string | 40000, 60000, 80000, 100000, 120000 |
| `easy_apply` | boolean | Filter for Easy Apply jobs |
| `under_10_applicants` | boolean | Jobs with fewer applicants |
| `limit` | integer | Max results (1-100) |
| `details` | boolean | Fetch full job descriptions |

---

## CLI Reference

```
linkedin-jobs search [OPTIONS] KEYWORD
```

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
| `--output` | `-o` | Export file path (.csv or .json) |
| `--format` | `-f` | csv, json, auto |
| `--details` | `-D` | Fetch full job descriptions (slower) |
| `--easy-apply` | | Filter to Easy Apply jobs only |
| `--under-10-applicants` | | Filter to jobs with <10 applicants |

---

## Project Structure

```
linkedin-job-scraper/
│
├── linkedin_scraper/          # Core Python package
│   ├── __init__.py
│   ├── cli.py                 # Command line interface
│   ├── scraper.py             # LinkedIn scraping logic
│   └── exporter.py            # CSV/JSON export
│
├── api/                       # FastAPI backend
│   ├── __init__.py
│   └── main.py                # API endpoints
│
├── frontend/                  # React web application
│   ├── src/
│   │   ├── components/        # React components
│   │   │   ├── App.tsx        # Main app with tabs
│   │   │   ├── SearchForm.tsx # Search with filters
│   │   │   ├── JobCard.tsx    # Job listing card
│   │   │   ├── JobList.tsx    # Job results list
│   │   │   ├── SearchHistory.tsx    # Recent searches
│   │   │   ├── SavedJobs.tsx        # Bookmarked jobs
│   │   │   ├── ApplicationTracker.tsx # Track applied jobs
│   │   │   ├── CompanyInfoModal.tsx   # Company links
│   │   │   ├── ThemeToggle.tsx        # Dark mode toggle
│   │   │   ├── Pagination.tsx         # Page navigation
│   │   │   ├── SkeletonCard.tsx       # Loading skeleton
│   │   │   └── ErrorMessage.tsx       # Error display
│   │   ├── hooks/             # Custom React hooks
│   │   │   ├── useTheme.ts    # Theme management
│   │   │   └── useLocalStorage.ts # Persistent storage
│   │   ├── services/          # API client
│   │   └── types/             # TypeScript types
│   ├── package.json
│   └── tailwind.config.js
│
├── requirements.txt           # Python dependencies
├── setup.py                   # Package configuration
└── README.md
```

---

## How It Works

This tool scrapes LinkedIn's **public job search pages** - the same pages you see when browsing jobs without logging in. No API key or authentication required.

1. Constructs search URL with your filters
2. Fetches the public job listings page
3. Parses HTML to extract job data
4. Returns structured results

**Note:** LinkedIn may rate-limit requests. The scraper includes delays between requests to be respectful.

---

## Tech Stack

| Layer | Technology |
|-------|------------|
| Scraping | Python, BeautifulSoup, Requests |
| CLI | Click, Rich |
| Backend | FastAPI, Uvicorn, Pydantic |
| Frontend | React, TypeScript, Vite, Tailwind CSS |
| Storage | localStorage (browser) |

---

## Contributing

Contributions are welcome! Feel free to:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

---

## Disclaimer

This tool scrapes publicly available job listings from LinkedIn. Please use responsibly:

- Respect LinkedIn's Terms of Service
- Don't make excessive requests
- Use for personal job searching only
- Consider rate limiting in production

---

## Author

**Adithya Reddy Geeda**

- GitHub: [@AdithyaReddyGeeda](https://github.com/AdithyaReddyGeeda)
