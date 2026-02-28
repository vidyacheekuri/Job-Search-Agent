"""Export job listings to CSV and JSON formats."""

import csv
import json
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .scraper import Job


def export_to_csv(jobs: list["Job"], filepath: str | Path) -> None:
    """
    Export jobs to a CSV file.
    
    Args:
        jobs: List of Job objects to export.
        filepath: Path to the output CSV file.
    """
    if not jobs:
        return

    filepath = Path(filepath)
    fieldnames = [
        "position",
        "company",
        "location",
        "date",
        "ago_time",
        "salary",
        "job_url",
        "company_logo",
        "description",
        "skills",
        "apply_method",
        "applicant_count",
    ]

    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        for job in jobs:
            row = job.to_dict()
            if row.get("skills"):
                row["skills"] = "; ".join(row["skills"])
            if row.get("description"):
                row["description"] = row["description"][:500] + "..." if len(row["description"]) > 500 else row["description"]
            writer.writerow(row)


def export_to_json(jobs: list["Job"], filepath: str | Path, indent: int = 2) -> None:
    """
    Export jobs to a JSON file.
    
    Args:
        jobs: List of Job objects to export.
        filepath: Path to the output JSON file.
        indent: JSON indentation level.
    """
    filepath = Path(filepath)
    data = [job.to_dict() for job in jobs]

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=indent, ensure_ascii=False)


def export_jobs(jobs: list["Job"], filepath: str | Path, format: str = "auto") -> None:
    """
    Export jobs to a file, auto-detecting format from extension.
    
    Args:
        jobs: List of Job objects to export.
        filepath: Path to the output file.
        format: "csv", "json", or "auto" (detect from extension).
    """
    filepath = Path(filepath)

    if format == "auto":
        ext = filepath.suffix.lower()
        if ext == ".json":
            format = "json"
        else:
            format = "csv"

    if format == "json":
        export_to_json(jobs, filepath)
    else:
        export_to_csv(jobs, filepath)
