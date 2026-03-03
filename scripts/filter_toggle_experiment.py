#!/usr/bin/env python3
"""
Filter Toggle Experiment - Assignment requirement.
Run the pipeline with Iowa-only, then Texas-only, and compare results.
Usage: python scripts/filter_toggle_experiment.py
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from linkedin_scraper.agent.profile import UserProfile
from linkedin_scraper.agent.agent import JobSearchAgent
from pathlib import Path


def load_sample_profile():
    """Load sample AI Engineer profile from data/sample_resume.json"""
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    resume_path = project_root / "data" / "sample_resume.json"
    with open(resume_path, "r") as f:
        data = json.load(f)
    return UserProfile.from_dict(data)


def run_experiment():
    """Run filter toggle: Iowa vs Texas"""
    profile = load_sample_profile()
    agent = JobSearchAgent(profile, enable_logging=True)
    
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    output_dir = project_root / "output" / "filter_toggle_experiment"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    results = {}
    
    for location in ["Iowa", "Texas"]:
        print(f"\n{'='*60}")
        print(f"Running pipeline with location_filter={location}")
        print(f"{'='*60}")
        
        run_results = agent.run_middle_america_pipeline(
            keyword="AI Engineer",
            location=location,
            exclude_faang=True,
            exclude_startups=True,
            location_filter=location,
            limit=25,
            top_n=10,
            top_n_applications=3,
            output_dir=str(output_dir / location.lower()),
        )
        
        results[location] = {
            "total_found": run_results["search"]["total_found"],
            "after_filter": run_results["filters"]["jobs_after_filter"],
            "top_jobs": run_results["ranking"]["top_jobs"][:5],
            "avg_match": run_results["metrics"]["average_match_score"],
        }
    
    # Save comparison
    with open(output_dir / "comparison.json", "w") as f:
        json.dump(results, f, indent=2)
    
    print("\n" + "="*60)
    print("Filter Toggle Experiment Complete")
    print("="*60)
    print(f"Iowa: {results['Iowa']['after_filter']} jobs after filter, avg match {results['Iowa']['avg_match']}%")
    print(f"Texas: {results['Texas']['after_filter']} jobs after filter, avg match {results['Texas']['avg_match']}%")
    print(f"\nResults saved to {output_dir}")
    
    return results


if __name__ == "__main__":
    run_experiment()
