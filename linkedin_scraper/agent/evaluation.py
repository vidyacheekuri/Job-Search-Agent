"""Evaluation framework for the Job Search Agent with hiring simulation metrics."""

import json
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
from pathlib import Path


@dataclass
class PipelineLog:
    """Structured log entry for pipeline decisions."""
    timestamp: str
    stage: str
    action: str
    details: dict
    
    def to_dict(self) -> dict:
        return {
            "timestamp": self.timestamp,
            "stage": self.stage,
            "action": self.action,
            "details": self.details,
        }


@dataclass
class EvaluationResult:
    """Results from evaluation metrics."""
    precision_at_k: float
    interview_yield: float
    total_jobs_searched: int
    jobs_after_faang_filter: int
    jobs_after_startup_filter: int
    jobs_after_location_filter: int
    top_k_jobs: list
    human_ratings: list = field(default_factory=list)
    tailoring_scores: list = field(default_factory=list)
    
    def to_dict(self) -> dict:
        return {
            "precision_at_k": self.precision_at_k,
            "interview_yield": self.interview_yield,
            "total_jobs_searched": self.total_jobs_searched,
            "jobs_after_faang_filter": self.jobs_after_faang_filter,
            "jobs_after_startup_filter": self.jobs_after_startup_filter,
            "jobs_after_location_filter": self.jobs_after_location_filter,
            "top_k_jobs": self.top_k_jobs,
            "human_ratings": self.human_ratings,
            "tailoring_scores": self.tailoring_scores,
        }


class PipelineLogger:
    """
    Logger for tracking all pipeline decisions and rationales.
    Required for the assignment's decision logging requirement.
    """
    
    def __init__(self):
        self.logs: list[PipelineLog] = []
        self.stage_counts = {
            "search": 0,
            "filter_faang": 0,
            "filter_startup": 0,
            "filter_location": 0,
            "rank": 0,
            "tailor": 0,
        }
    
    def log(self, stage: str, action: str, details: dict) -> None:
        """
        Log a pipeline decision.
        
        Args:
            stage: Pipeline stage (search, filter_faang, filter_startup, rank, tailor)
            action: Action taken (included, excluded, ranked, tailored)
            details: Additional details about the decision
        """
        entry = PipelineLog(
            timestamp=datetime.now().isoformat(),
            stage=stage,
            action=action,
            details=details,
        )
        self.logs.append(entry)
        
        if stage in self.stage_counts:
            self.stage_counts[stage] += 1
    
    def log_search(self, query: str, source: str, num_results: int) -> None:
        """Log a search operation."""
        self.log("search", "SEARCH", {
            "query": query,
            "source": source,
            "results_found": num_results,
        })
    
    def log_filter(self, stage: str, job_title: str, company: str, 
                   included: bool, reason: str) -> None:
        """Log a filter decision."""
        self.log(stage, "INCLUDED" if included else "EXCLUDED", {
            "job": job_title,
            "company": company,
            "reason": reason,
        })
    
    def log_rank(self, job_title: str, company: str, score: float, 
                 rank: int, reasons: list[str]) -> None:
        """Log a ranking decision."""
        self.log("rank", "RANKED", {
            "job": job_title,
            "company": company,
            "score": score,
            "rank": rank,
            "match_reasons": reasons,
        })
    
    def log_tailor(self, job_title: str, company: str, 
                   document_type: str, changes_made: list[str]) -> None:
        """Log a tailoring operation."""
        self.log("tailor", "TAILORED", {
            "job": job_title,
            "company": company,
            "document_type": document_type,
            "changes_made": changes_made,
        })
    
    def get_summary(self) -> dict:
        """Get a summary of all pipeline operations."""
        return {
            "total_logs": len(self.logs),
            "stage_counts": self.stage_counts,
            "stages_executed": [s for s, c in self.stage_counts.items() if c > 0],
        }
    
    def export_trace(self, filepath: str) -> None:
        """Export full pipeline trace for the report appendix."""
        trace = {
            "summary": self.get_summary(),
            "logs": [log.to_dict() for log in self.logs],
        }
        
        with open(filepath, 'w') as f:
            json.dump(trace, f, indent=2)
    
    def get_logs_by_stage(self, stage: str) -> list[PipelineLog]:
        """Get all logs for a specific stage."""
        return [log for log in self.logs if log.stage == stage]


class HiringSimulator:
    """
    Simulates hiring decisions for evaluation.
    Computes Precision@K and Interview Yield metrics.
    """
    
    def __init__(self, benchmark_path: Optional[str] = None):
        """
        Initialize with optional benchmark dataset.
        
        Args:
            benchmark_path: Path to benchmark_jobs.json
        """
        self.benchmark = None
        self.interview_worthy_ids = set()
        self.reject_ids = set()
        
        if benchmark_path:
            self.load_benchmark(benchmark_path)
    
    def load_benchmark(self, filepath: str) -> None:
        """Load the benchmark dataset."""
        with open(filepath, 'r') as f:
            self.benchmark = json.load(f)
        
        self.interview_worthy_ids = {
            job["id"] for job in self.benchmark.get("interview_worthy", [])
        }
        self.reject_ids = {
            job["id"] for job in self.benchmark.get("reject", [])
        }
    
    def compute_precision_at_k(self, shortlist: list[dict], k: int = 10) -> float:
        """
        Compute Precision@K: how many of the top K are interview-worthy.
        
        Args:
            shortlist: List of ranked jobs (should have 'id' field)
            k: Number of top jobs to consider
            
        Returns:
            Precision@K score (0.0 to 1.0)
        """
        top_k = shortlist[:k]
        
        relevant_count = sum(
            1 for job in top_k 
            if job.get("id") in self.interview_worthy_ids
        )
        
        return relevant_count / k if k > 0 else 0.0
    
    def compute_interview_yield(self, human_ratings: list[dict]) -> float:
        """
        Compute Interview Yield from human ratings.
        
        Args:
            human_ratings: List of {job_id, rater, interview_decision (yes/no)}
            
        Returns:
            Interview yield (proportion of 'yes' decisions)
        """
        if not human_ratings:
            return 0.0
        
        yes_count = sum(
            1 for rating in human_ratings 
            if rating.get("interview_decision", "").lower() == "yes"
        )
        
        return yes_count / len(human_ratings)
    
    def simulate_human_rating(self, job: dict) -> dict:
        """
        Simulate a human rating decision based on benchmark labels.
        Used for automated testing; real evaluation uses actual human ratings.
        
        Args:
            job: Job dictionary with id field
            
        Returns:
            Simulated rating decision
        """
        job_id = job.get("id", "")
        
        if job_id in self.interview_worthy_ids:
            decision = "yes"
            confidence = 0.9
        elif job_id in self.reject_ids:
            decision = "no"
            confidence = 0.85
        else:
            decision = "maybe"
            confidence = 0.5
        
        return {
            "job_id": job_id,
            "job_title": job.get("position", job.get("title", "")),
            "company": job.get("company", ""),
            "interview_decision": decision,
            "confidence": confidence,
            "simulated": True,
        }
    
    def evaluate_shortlist(self, shortlist: list[dict], k: int = 10) -> dict:
        """
        Full evaluation of a job shortlist.
        
        Args:
            shortlist: Ranked list of jobs
            k: Number of top jobs for Precision@K
            
        Returns:
            Complete evaluation metrics
        """
        precision = self.compute_precision_at_k(shortlist, k)
        
        simulated_ratings = [
            self.simulate_human_rating(job) for job in shortlist[:k]
        ]
        interview_yield = self.compute_interview_yield(simulated_ratings)
        
        return {
            "precision_at_k": precision,
            "k": k,
            "interview_yield": interview_yield,
            "top_k_breakdown": {
                "interview_worthy": sum(
                    1 for job in shortlist[:k] 
                    if job.get("id") in self.interview_worthy_ids
                ),
                "rejects": sum(
                    1 for job in shortlist[:k] 
                    if job.get("id") in self.reject_ids
                ),
                "unknown": sum(
                    1 for job in shortlist[:k] 
                    if job.get("id") not in self.interview_worthy_ids 
                    and job.get("id") not in self.reject_ids
                ),
            },
            "simulated_ratings": simulated_ratings,
        }


class TailoringEvaluator:
    """Evaluator for resume and cover letter tailoring quality."""
    
    CRITERIA = [
        "keyword_incorporation",
        "relevance_to_job",
        "professional_tone",
        "specificity",
        "ats_optimization",
    ]
    
    def score_tailored_document(
        self, 
        original: str, 
        tailored: str, 
        job_description: str
    ) -> dict:
        """
        Score a tailored document (heuristic-based).
        
        Args:
            original: Original resume/cover letter text
            tailored: Tailored version
            job_description: Target job description
            
        Returns:
            Scoring breakdown (1-5 scale)
        """
        job_keywords = self._extract_keywords(job_description)
        
        original_kw_count = sum(1 for kw in job_keywords if kw in original.lower())
        tailored_kw_count = sum(1 for kw in job_keywords if kw in tailored.lower())
        keyword_improvement = tailored_kw_count - original_kw_count
        
        keyword_score = min(5, 2 + keyword_improvement)
        
        tailored_lower = tailored.lower()
        relevance_signals = [
            "experience" in tailored_lower,
            "skills" in tailored_lower,
            any(kw in tailored_lower for kw in job_keywords[:5]),
            len(tailored) > len(original) * 0.8,
        ]
        relevance_score = 1 + sum(relevance_signals)
        
        professional_signals = [
            not any(word in tailored_lower for word in ["awesome", "amazing", "super"]),
            "sincerely" in tailored_lower or "regards" in tailored_lower or "experience" in tailored_lower,
            tailored[0].isupper() if tailored else False,
            tailored.count("!") < 3,
        ]
        professional_score = 1 + sum(professional_signals)
        
        specificity_signals = [
            any(char.isdigit() for char in tailored),
            "%" in tailored,
            "$" in tailored,
            len(tailored.split()) > 100,
        ]
        specificity_score = 1 + sum(specificity_signals)
        
        ats_signals = [
            tailored_kw_count >= 3,
            len(tailored) > 500,
            tailored.count("\n\n") >= 2,
            not any(c in tailored for c in ["★", "●", "►"]),
        ]
        ats_score = 1 + sum(ats_signals)
        
        scores = {
            "keyword_incorporation": keyword_score,
            "relevance_to_job": relevance_score,
            "professional_tone": professional_score,
            "specificity": specificity_score,
            "ats_optimization": ats_score,
        }
        
        scores["overall"] = round(sum(scores.values()) / len(scores), 1)
        scores["keywords_added"] = keyword_improvement
        
        return scores
    
    def _extract_keywords(self, text: str) -> list[str]:
        """Extract important keywords from job description."""
        common_words = {
            "the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for",
            "of", "with", "by", "from", "as", "is", "was", "are", "were", "been",
            "be", "have", "has", "had", "do", "does", "did", "will", "would",
            "could", "should", "may", "might", "must", "shall", "can", "need",
            "our", "we", "you", "your", "their", "this", "that", "these", "those",
        }
        
        words = text.lower().split()
        keywords = [
            word.strip(".,;:!?()[]{}\"'") 
            for word in words 
            if len(word) > 3 and word.lower() not in common_words
        ]
        
        return list(dict.fromkeys(keywords))[:20]


def create_human_rating_form(
    shortlist: list[dict],
    output_path: str,
    num_raters: int = 3,
) -> None:
    """
    Create a human rating form for the benchmark evaluation.
    Assignment: "Have 3 humans score the agent shortlist: Interview? (Yes/No)"
    
    Args:
        shortlist: List of jobs to rate
        output_path: Path to save the form
        num_raters: Number of human raters (default: 3 per assignment)
    """
    form = {
        "instructions": """
Human Rating Form for Job Search Agent Evaluation
(Assignment: 3 human raters per shortlist)

Instructions for Each Rater:
1. Review each job in the shortlist below
2. For each job, decide: "Would you interview this candidate for this role?"
3. Mark 'yes' or 'no' for each job (required)
4. Optionally add comments explaining your decision

Rating Scale:
- yes: This is a good match, candidate should be interviewed
- no: This is not a good match, candidate should not be interviewed

After all 3 raters complete their forms, aggregate for Interview Yield:
Interview Yield = (Total 'yes' ratings) / (Total ratings)
""",
        "num_raters_required": num_raters,
        "date_created": datetime.now().strftime("%Y-%m-%d"),
        "jobs_to_rate": [],
        "rater_responses": {
            f"rater_{i+1}": {
                "rater_name": "[RATER NAME]",
                "date_completed": "",
                "ratings": [],
            }
            for i in range(num_raters)
        },
    }
    
    for i, job in enumerate(shortlist, 1):
        job_entry = {
            "rank": i,
            "position": job.get("position", job.get("title", "")),
            "company": job.get("company", ""),
            "location": job.get("location", ""),
            "salary": job.get("salary", "Not specified"),
            "match_score": job.get("score", "N/A"),
            "job_id": job.get("id", ""),
        }
        form["jobs_to_rate"].append(job_entry)
        for rater_key in form["rater_responses"]:
            form["rater_responses"][rater_key]["ratings"].append({
                "rank": i,
                "job_id": job.get("id", ""),
                "interview_decision": "",
                "comments": "",
            })
    
    with open(output_path, 'w') as f:
        json.dump(form, f, indent=2)


def load_benchmark_as_jobs(benchmark_path: str) -> list[dict]:
    """
    Load benchmark jobs as a combined list for testing.
    
    Args:
        benchmark_path: Path to benchmark_jobs.json
        
    Returns:
        Combined list of all benchmark jobs
    """
    with open(benchmark_path, 'r') as f:
        benchmark = json.load(f)
    
    all_jobs = []
    all_jobs.extend(benchmark.get("interview_worthy", []))
    all_jobs.extend(benchmark.get("reject", []))
    
    return all_jobs


@dataclass
class RecruiterFeedback:
    """Simulated recruiter feedback on an application."""
    application_id: str
    resume_score: float
    cover_letter_score: float
    interview_decision: str
    overall_impression: str
    strengths: list[str]
    weaknesses: list[str]


@dataclass 
class EvaluationMetrics:
    """Metrics from agent evaluation."""
    total_applications: int
    avg_match_score: float
    avg_ats_score: float
    avg_personalization_score: float
    interview_rate: float
    maybe_rate: float
    rejection_rate: float
    skill_coverage: float
    recruiter_feedback: list[RecruiterFeedback]


class AgentEvaluator:
    """Evaluates agent performance through hiring simulation."""
    
    def __init__(self, recruiter_strictness: float = 0.5):
        """
        Initialize evaluator.
        
        Args:
            recruiter_strictness: How strict the simulated recruiter is (0-1).
        """
        self.strictness = recruiter_strictness
    
    def evaluate_applications(self, applications: list) -> EvaluationMetrics:
        """
        Evaluate a list of application packages.
        
        Args:
            applications: List of ApplicationPackage objects.
            
        Returns:
            EvaluationMetrics with scores and feedback.
        """
        if not applications:
            return EvaluationMetrics(
                total_applications=0,
                avg_match_score=0,
                avg_ats_score=0,
                avg_personalization_score=0,
                interview_rate=0,
                maybe_rate=0,
                rejection_rate=0,
                skill_coverage=0,
                recruiter_feedback=[],
            )
        
        feedback_list = []
        interview_count = 0
        maybe_count = 0
        reject_count = 0
        
        for i, app in enumerate(applications):
            feedback = self._simulate_recruiter_review(app, i)
            feedback_list.append(feedback)
            
            if feedback.interview_decision == "interview":
                interview_count += 1
            elif feedback.interview_decision == "maybe":
                maybe_count += 1
            else:
                reject_count += 1
        
        total = len(applications)
        
        return EvaluationMetrics(
            total_applications=total,
            avg_match_score=sum(a.ranked_job.score for a in applications) / total,
            avg_ats_score=sum(a.tailored_resume.ats_score for a in applications) / total,
            avg_personalization_score=sum(a.cover_letter.personalization_score for a in applications) / total,
            interview_rate=interview_count / total,
            maybe_rate=maybe_count / total,
            rejection_rate=reject_count / total,
            skill_coverage=sum(len(a.ranked_job.matched_skills) for a in applications) / (total * 5),
            recruiter_feedback=feedback_list,
        )
    
    def _simulate_recruiter_review(self, app, index: int) -> RecruiterFeedback:
        """Simulate a recruiter reviewing an application."""
        match_score = app.ranked_job.score
        ats_score = app.tailored_resume.ats_score
        personalization = app.cover_letter.personalization_score  # 0-100 scale
        personalization_norm = min(personalization / 100.0, 1.0)
        
        combined_score = (match_score * 0.4 + ats_score * 0.3 + personalization_norm * 30) / 100
        
        threshold_interview = 0.7 - (self.strictness * 0.2)
        threshold_maybe = 0.5 - (self.strictness * 0.1)
        
        if combined_score >= threshold_interview:
            decision = "interview"
            impression = "Strong candidate with relevant experience"
        elif combined_score >= threshold_maybe:
            decision = "maybe"
            impression = "Potential fit, needs more review"
        else:
            decision = "reject"
            impression = "Does not meet current requirements"
        
        strengths = []
        if match_score >= 70:
            strengths.append("Strong skill alignment")
        if ats_score >= 75:
            strengths.append("Well-formatted resume")
        if personalization >= 60:
            strengths.append("Personalized cover letter")
        if app.ranked_job.matched_skills:
            strengths.append(f"Matched skills: {', '.join(app.ranked_job.matched_skills[:3])}")
        
        weaknesses = []
        if match_score < 60:
            weaknesses.append("Limited skill match")
        if app.ranked_job.missing_skills:
            weaknesses.append(f"Missing: {', '.join(app.ranked_job.missing_skills[:2])}")
        if personalization < 40:
            weaknesses.append("Generic cover letter")
        
        job = app.ranked_job.job
        position = getattr(job, "position", "") or ""
        company = getattr(job, "company", "") or ""
        if position or company:
            application_id = f"{position} · {company}".strip(" · ") if (position and company) else (position or company)
        else:
            application_id = f"Application {index + 1}"
        return RecruiterFeedback(
            application_id=application_id,
            resume_score=ats_score,
            cover_letter_score=round(personalization, 1),
            interview_decision=decision,
            overall_impression=impression,
            strengths=strengths or ["Meets basic requirements"],
            weaknesses=weaknesses or ["No significant concerns"],
        )


@dataclass
class BiasAnalysisResult:
    """Results from bias analysis."""
    location_bias: dict
    company_size_bias: dict
    salary_range_bias: dict
    experience_level_bias: dict
    keyword_frequency: dict
    excluded_keywords: list[str]
    recommendations: list[str]


class BiasAnalyzer:
    """Analyzes potential biases in job search and ranking."""
    
    def analyze(self, jobs: list, ranked_jobs: list, profile) -> BiasAnalysisResult:
        """
        Analyze biases in job search results.
        
        Args:
            jobs: All jobs found.
            ranked_jobs: Ranked jobs.
            profile: User profile.
            
        Returns:
            BiasAnalysisResult with findings.
        """
        location_dist = {}
        for job in jobs:
            loc = job.location if hasattr(job, 'location') else job.get('location', 'Unknown')
            state = self._extract_state(loc)
            location_dist[state] = location_dist.get(state, 0) + 1
        
        ranked_locations = {}
        for rj in ranked_jobs[:10]:
            job = rj.job if hasattr(rj, 'job') else rj
            loc = job.location if hasattr(job, 'location') else job.get('location', 'Unknown')
            state = self._extract_state(loc)
            ranked_locations[state] = ranked_locations.get(state, 0) + 1
        
        company_size_dist = {
            "small": 0,
            "mid": 0,
            "large": 0,
            "unknown": 0,
        }
        
        salary_dist = {
            "<80k": 0,
            "80k-120k": 0,
            "120k-160k": 0,
            "160k+": 0,
            "not_specified": 0,
        }
        
        experience_dist = {
            "entry": 0,
            "mid": 0,
            "senior": 0,
            "unknown": 0,
        }
        
        for job in jobs:
            desc = job.description if hasattr(job, 'description') else job.get('description', '')
            desc = desc or ''
            desc_lower = desc.lower()
            
            if any(kw in desc_lower for kw in ["startup", "seed", "series a"]):
                company_size_dist["small"] += 1
            elif any(kw in desc_lower for kw in ["fortune 500", "enterprise", "multinational"]):
                company_size_dist["large"] += 1
            else:
                company_size_dist["mid"] += 1
            
            if "senior" in desc_lower or "lead" in desc_lower:
                experience_dist["senior"] += 1
            elif "entry" in desc_lower or "junior" in desc_lower:
                experience_dist["entry"] += 1
            else:
                experience_dist["mid"] += 1
        
        keywords = {}
        for job in jobs:
            desc = job.description if hasattr(job, 'description') else job.get('description', '')
            desc = desc or ''
            for word in desc.lower().split():
                if len(word) > 4:
                    keywords[word] = keywords.get(word, 0) + 1
        
        top_keywords = dict(sorted(keywords.items(), key=lambda x: x[1], reverse=True)[:20])
        
        recommendations = [
            "Consider expanding location preferences to increase job pool",
            "Review FAANG blacklist to ensure it aligns with career goals",
            "Monitor for potential bias in salary range filtering",
            "Ensure experience level filters don't exclude valid opportunities",
            "Regularly audit ranking weights for fairness",
        ]
        
        return BiasAnalysisResult(
            location_bias={"all_jobs": location_dist, "top_ranked": ranked_locations},
            company_size_bias=company_size_dist,
            salary_range_bias=salary_dist,
            experience_level_bias=experience_dist,
            keyword_frequency=top_keywords,
            excluded_keywords=["faang", "startup", "seed"],
            recommendations=recommendations,
        )
    
    def _extract_state(self, location: str) -> str:
        """Extract state from location string."""
        if not location:
            return "Unknown"
        
        states = {
            "CA": "California", "TX": "Texas", "NY": "New York",
            "WA": "Washington", "MA": "Massachusetts", "CO": "Colorado",
            "IL": "Illinois", "GA": "Georgia", "NC": "North Carolina",
            "VA": "Virginia", "IA": "Iowa", "MN": "Minnesota",
            "WI": "Wisconsin", "NE": "Nebraska", "IN": "Indiana",
            "MI": "Michigan", "OH": "Ohio", "PA": "Pennsylvania",
        }
        
        location_upper = location.upper()
        for abbr, name in states.items():
            if abbr in location_upper or name.upper() in location_upper:
                return name
        
        if "remote" in location.lower():
            return "Remote"
        
        return "Other"
