"""CLI interface for LinkedIn Job Scraper."""

import click
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn

from .scraper import LinkedInScraper
from .exporter import export_jobs


console = Console()


@click.group()
@click.version_option(package_name="linkedin-job-scraper")
def main():
    """LinkedIn Job Scraper - Search and export job listings from LinkedIn."""
    pass


@main.command()
@click.argument("keyword")
@click.option(
    "--location", "-l",
    default="",
    help="City or region (e.g., 'San Francisco', 'Remote')"
)
@click.option(
    "--job-type", "-t",
    type=click.Choice(
        ["full-time", "part-time", "contract", "temporary", "volunteer", "internship"],
        case_sensitive=False
    ),
    default=None,
    help="Type of employment"
)
@click.option(
    "--remote", "-r",
    type=click.Choice(["on-site", "remote", "hybrid"], case_sensitive=False),
    default=None,
    help="Work location type"
)
@click.option(
    "--experience", "-e",
    type=click.Choice(
        ["internship", "entry-level", "associate", "senior", "director", "executive"],
        case_sensitive=False
    ),
    default=None,
    help="Experience level"
)
@click.option(
    "--date-posted", "-d",
    type=click.Choice(["24hr", "past-week", "past-month"], case_sensitive=False),
    default=None,
    help="Filter by posting date"
)
@click.option(
    "--salary", "-s",
    type=click.Choice(["40000", "60000", "80000", "100000", "120000"]),
    default=None,
    help="Minimum salary filter"
)
@click.option(
    "--sort-by",
    type=click.Choice(["recent", "relevant"], case_sensitive=False),
    default="relevant",
    help="Sort order for results"
)
@click.option(
    "--limit", "-n",
    default=25,
    type=int,
    help="Maximum number of jobs to return (default: 25)"
)
@click.option(
    "--output", "-o",
    type=click.Path(),
    default=None,
    help="Output file path (CSV or JSON based on extension)"
)
@click.option(
    "--format", "-f",
    type=click.Choice(["csv", "json", "auto"], case_sensitive=False),
    default="auto",
    help="Output format (default: auto-detect from file extension)"
)
def search(
    keyword: str,
    location: str,
    job_type: str | None,
    remote: str | None,
    experience: str | None,
    date_posted: str | None,
    salary: str | None,
    sort_by: str,
    limit: int,
    output: str | None,
    format: str,
):
    """
    Search for jobs on LinkedIn.
    
    KEYWORD is the job title or search term (e.g., "software engineer").
    
    Examples:
    
        linkedin-jobs search "software engineer" --location "San Francisco"
        
        linkedin-jobs search "python developer" -l Remote -t full-time -n 50
        
        linkedin-jobs search "data scientist" -o jobs.csv
    """
    scraper = LinkedInScraper()

    date_posted_val = date_posted.replace("-", " ") if date_posted else ""
    job_type_val = job_type.replace("-", " ") if job_type else ""
    remote_val = remote.replace("-", " ") if remote else ""
    experience_val = experience.replace("-", " ") if experience else ""

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
        transient=True,
    ) as progress:
        progress.add_task(f"Searching for '{keyword}' jobs...", total=None)
        
        jobs = scraper.search(
            keyword=keyword,
            location=location,
            date_posted=date_posted_val,
            job_type=job_type_val,
            remote=remote_val,
            experience=experience_val,
            salary=salary or "",
            sort_by=sort_by,
            limit=limit,
        )

    if not jobs:
        console.print("[yellow]No jobs found matching your criteria.[/yellow]")
        return

    console.print(f"\n[green]Found {len(jobs)} job(s)[/green]\n")

    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("#", style="dim", width=4)
    table.add_column("Position", style="cyan", max_width=35)
    table.add_column("Company", style="green", max_width=25)
    table.add_column("Location", max_width=20)
    table.add_column("Posted", style="dim", max_width=15)
    table.add_column("Salary", style="yellow", max_width=15)

    for i, job in enumerate(jobs, 1):
        table.add_row(
            str(i),
            job.position[:35] + "..." if len(job.position) > 35 else job.position,
            job.company[:25] + "..." if len(job.company) > 25 else job.company,
            job.location[:20] + "..." if len(job.location) > 20 else job.location,
            job.ago_time or job.date,
            job.salary or "-",
        )

    console.print(table)

    if output:
        export_jobs(jobs, output, format)
        console.print(f"\n[green]Results exported to: {output}[/green]")


if __name__ == "__main__":
    main()
