# LinkedIn Job Scraper

A Python CLI tool for scraping job listings from LinkedIn's public job search pages.

## Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/linkedin-job-scraper.git
cd linkedin-job-scraper

# Install in development mode
pip install -e .
```

Or install dependencies directly:

```bash
pip install -r requirements.txt
```

## Usage

### Basic Search

```bash
linkedin-jobs search "software engineer" --location "San Francisco"
```

### With Filters

```bash
linkedin-jobs search "python developer" \
  --location "Remote" \
  --job-type full-time \
  --experience entry-level \
  --limit 50 \
  --output jobs.csv
```

### Export to JSON

```bash
linkedin-jobs search "data scientist" --output results.json
```

## Options

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
| `--format` | `-f` | csv, json, auto (default: auto-detect) |

## Output

Results are displayed in a formatted table in the terminal. Use `--output` to save to a file.

### CSV Output Fields

- position
- company
- location
- date
- ago_time
- salary
- job_url
- company_logo

## Disclaimer

This tool scrapes publicly available job listings from LinkedIn. Use responsibly and respect LinkedIn's Terms of Service. Consider implementing appropriate rate limiting for production use.


