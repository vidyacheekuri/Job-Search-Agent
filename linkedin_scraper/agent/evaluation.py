"""Evaluation framework for hiring simulation and agent performance metrics."""

import json
import random
from dataclasses import dataclass, asdict, field
from datetime import datetime
from typing import Optional
from pathlib import Path

from ..scraper import Job
from .profile import UserProfile
from .ranker import RankedJob
from .agent import ApplicationPackage, JobSearchAgent


@dataclass
class MockRecruiterFeedback:
    """Simulated recruiter feedback on an application."""
    application_id: str
    resume_score: float  # 0-100
    cover_letter_score: float  # 0-100
    overall_impression: str  # "strong", "good", "average", "weak"
    interview_decision: str  # "advance", "maybe", "reject"
    strengths: list[str]
    weaknesses: list[str]
    feedback: str


@dataclass
class EvaluationMetrics:
    """Metrics for evaluating agent performance."""
    total_applications: int
    
    avg_match_score: float
    avg_ats_score: float
    avg_personalization_score: float
    
    interview_rate: float  # % of "advance" decisions
    maybe_rate: float  # % of "maybe" decisions
    rejection_rate: float  # % of "reject" decisions
    
    skill_coverage: float  # % of job skills matched
    keyword_coverage: float  # % of job keywords in resume
    
    diversity_score: float  # variety in companies/roles
    relevance_score: float  # how relevant jobs are to profile
    
    recruiter_feedback: list[MockRecruiterFeedback]
    
    def to_dict(self) -> dict:
        return {
            **asdict(self),
            "recruiter_feedback": [asdict(f) for f in self.recruiter_feedback],
        }


@dataclass
class BiasAnalysis:
    """Analysis of potential biases in the job search agent."""
    
    location_bias: dict  # distribution of job locations
    company_size_bias: dict  # distribution of company sizes
    salary_range_bias: dict  # distribution of salary ranges
    experience_level_bias: dict  # distribution of experience levels
    
    keyword_frequency: dict  # most common keywords in selected jobs
    excluded_keywords: list[str]  # keywords that might exclude diverse candidates
    
    recommendations: list[str]  # suggestions to reduce bias
    
    def to_dict(self) -> dict:
        return asdict(self)


class MockRecruiter:
    """
    Simulates recruiter evaluation of applications.
    Uses heuristics to provide realistic feedback.
    """
    
    STRONG_INDICATORS = [
        "quantifiable results",
        "relevant experience",
        "matching skills",
        "clear progression",
        "specific achievements",
        "industry knowledge",
        "leadership experience",
    ]
    
    WEAK_INDICATORS = [
        "generic language",
        "missing keywords",
        "no metrics",
        "unclear experience",
        "skill gaps",
        "format issues",
        "too short/long",
    ]
    
    def __init__(self, strictness: float = 0.5):
        """
        Initialize mock recruiter.
        
        Args:
            strictness: How strict the recruiter is (0-1).
                        Higher = more rejections.
        """
        self.strictness = strictness
    
    def evaluate_resume(self, application: ApplicationPackage) -> tuple[float, list[str], list[str]]:
        """Evaluate resume quality."""
        score = 50.0
        strengths = []
        weaknesses = []
        
        ats_score = application.tailored_resume.ats_score
        score += (ats_score - 50) * 0.3
        
        if ats_score >= 70:
            strengths.append("Strong keyword optimization")
        elif ats_score < 40:
            weaknesses.append("Missing important keywords")
        
        matched_skills = len(application.ranked_job.matched_skills)
        if matched_skills >= 5:
            score += 15
            strengths.append(f"Excellent skill match ({matched_skills} skills)")
        elif matched_skills >= 3:
            score += 8
            strengths.append("Good skill alignment")
        else:
            score -= 10
            weaknesses.append("Limited skill match")
        
        missing_skills = application.ranked_job.missing_skills
        if missing_skills:
            score -= len(missing_skills) * 2
            if len(missing_skills) >= 3:
                weaknesses.append(f"Missing key skills: {', '.join(missing_skills[:3])}")
        
        experience = application.tailored_resume.experience_bullets
        if experience:
            has_metrics = any(
                any(c.isdigit() for c in str(exp.get("highlights", [])))
                for exp in experience
            )
            if has_metrics:
                score += 10
                strengths.append("Includes quantifiable achievements")
            else:
                weaknesses.append("Could add more metrics")
        
        score += (application.ranked_job.score - 50) * 0.2
        
        score = max(0, min(100, score))
        
        score -= self.strictness * 10
        
        return score, strengths, weaknesses
    
    def evaluate_cover_letter(self, application: ApplicationPackage) -> tuple[float, list[str], list[str]]:
        """Evaluate cover letter quality."""
        score = 50.0
        strengths = []
        weaknesses = []
        
        personalization = application.cover_letter.personalization_score
        score += (personalization - 50) * 0.4
        
        if personalization >= 70:
            strengths.append("Well personalized to company")
        elif personalization < 40:
            weaknesses.append("Could be more personalized")
        
        word_count = application.cover_letter.word_count
        if 250 <= word_count <= 400:
            score += 10
            strengths.append("Appropriate length")
        elif word_count < 150:
            score -= 15
            weaknesses.append("Too brief")
        elif word_count > 500:
            score -= 10
            weaknesses.append("Could be more concise")
        
        content = application.cover_letter.content.lower()
        if application.job.company.lower() in content:
            score += 8
        else:
            weaknesses.append("Should mention company more")
        
        action_words = ["achieved", "delivered", "built", "led", "developed", "improved"]
        action_count = sum(1 for w in action_words if w in content)
        if action_count >= 2:
            score += 8
            strengths.append("Strong action-oriented language")
        
        score = max(0, min(100, score))
        score -= self.strictness * 8
        
        return score, strengths, weaknesses
    
    def make_decision(self, resume_score: float, cover_letter_score: float) -> str:
        """Make interview decision based on scores."""
        combined_score = resume_score * 0.6 + cover_letter_score * 0.4
        
        combined_score += random.uniform(-5, 5)
        
        threshold_advance = 65 - (self.strictness * 10)
        threshold_maybe = 50 - (self.strictness * 5)
        
        if combined_score >= threshold_advance:
            return "advance"
        elif combined_score >= threshold_maybe:
            return "maybe"
        else:
            return "reject"
    
    def evaluate(self, application: ApplicationPackage) -> MockRecruiterFeedback:
        """
        Evaluate a complete application.
        
        Args:
            application: Application package to evaluate.
            
        Returns:
            MockRecruiterFeedback with scores and decision.
        """
        resume_score, resume_strengths, resume_weaknesses = self.evaluate_resume(application)
        cl_score, cl_strengths, cl_weaknesses = self.evaluate_cover_letter(application)
        
        decision = self.make_decision(resume_score, cl_score)
        
        combined = (resume_score + cl_score) / 2
        if combined >= 70:
            impression = "strong"
        elif combined >= 55:
            impression = "good"
        elif combined >= 40:
            impression = "average"
        else:
            impression = "weak"
        
        strengths = resume_strengths + cl_strengths
        weaknesses = resume_weaknesses + cl_weaknesses
        
        feedback_templates = {
            "advance": f"Strong candidate for {application.job.position}. Recommend moving forward with interview.",
            "maybe": f"Potential fit for {application.job.position}. Consider for second review or different role.",
            "reject": f"Does not meet requirements for {application.job.position} at this time.",
        }
        
        return MockRecruiterFeedback(
            application_id=f"{application.job.company}_{application.job.position}"[:50],
            resume_score=round(resume_score, 1),
            cover_letter_score=round(cl_score, 1),
            overall_impression=impression,
            interview_decision=decision,
            strengths=strengths[:5],
            weaknesses=weaknesses[:5],
            feedback=feedback_templates[decision],
        )


class AgentEvaluator:
    """
    Evaluates the job search agent's performance
    using mock hiring simulations.
    """
    
    def __init__(self, recruiter_strictness: float = 0.5):
        """
        Initialize evaluator.
        
        Args:
            recruiter_strictness: How strict mock recruiters should be.
        """
        self.recruiter = MockRecruiter(strictness=recruiter_strictness)
    
    def evaluate_applications(
        self,
        applications: list[ApplicationPackage],
    ) -> EvaluationMetrics:
        """
        Evaluate a set of applications.
        
        Args:
            applications: List of application packages to evaluate.
            
        Returns:
            EvaluationMetrics with comprehensive analysis.
        """
        if not applications:
            raise ValueError("No applications to evaluate")
        
        feedback_list = []
        for app in applications:
            feedback = self.recruiter.evaluate(app)
            feedback_list.append(feedback)
        
        avg_match = sum(a.ranked_job.score for a in applications) / len(applications)
        avg_ats = sum(a.tailored_resume.ats_score for a in applications) / len(applications)
        avg_personalization = sum(a.cover_letter.personalization_score for a in applications) / len(applications)
        
        decisions = [f.interview_decision for f in feedback_list]
        interview_rate = decisions.count("advance") / len(decisions) * 100
        maybe_rate = decisions.count("maybe") / len(decisions) * 100
        rejection_rate = decisions.count("reject") / len(decisions) * 100
        
        total_matched = sum(len(a.ranked_job.matched_skills) for a in applications)
        total_possible = sum(
            len(a.ranked_job.matched_skills) + len(a.ranked_job.missing_skills)
            for a in applications
        )
        skill_coverage = (total_matched / total_possible * 100) if total_possible else 0
        
        keyword_coverage = avg_ats
        
        companies = set(a.job.company for a in applications)
        positions = set(a.job.position for a in applications)
        diversity_score = (len(companies) + len(positions)) / (len(applications) * 2) * 100
        
        relevance_score = avg_match
        
        return EvaluationMetrics(
            total_applications=len(applications),
            avg_match_score=round(avg_match, 1),
            avg_ats_score=round(avg_ats, 1),
            avg_personalization_score=round(avg_personalization, 1),
            interview_rate=round(interview_rate, 1),
            maybe_rate=round(maybe_rate, 1),
            rejection_rate=round(rejection_rate, 1),
            skill_coverage=round(skill_coverage, 1),
            keyword_coverage=round(keyword_coverage, 1),
            diversity_score=round(diversity_score, 1),
            relevance_score=round(relevance_score, 1),
            recruiter_feedback=feedback_list,
        )
    
    def run_hiring_simulation(
        self,
        agent: JobSearchAgent,
        keyword: str = "AI Engineer",
        location: str = "",
        num_applications: int = 10,
        num_simulations: int = 3,
    ) -> dict:
        """
        Run multiple hiring simulations to evaluate agent.
        
        Args:
            agent: JobSearchAgent to evaluate.
            keyword: Search keyword.
            location: Search location.
            num_applications: Applications per simulation.
            num_simulations: Number of simulation runs.
            
        Returns:
            Aggregated results across all simulations.
        """
        all_results = []
        
        for i in range(num_simulations):
            print(f"\n📊 Running simulation {i+1}/{num_simulations}...")
            
            agent.search(keyword=keyword, location=location, limit=50)
            agent.filter_jobs(company_size="mid")
            agent.rank_jobs(fetch_details=False)
            applications = agent.generate_applications(top_n=num_applications)
            
            metrics = self.evaluate_applications(applications)
            all_results.append(metrics)
            
            print(f"   Interview rate: {metrics.interview_rate}%")
            print(f"   Avg match score: {metrics.avg_match_score}")
        
        avg_interview_rate = sum(r.interview_rate for r in all_results) / len(all_results)
        avg_match = sum(r.avg_match_score for r in all_results) / len(all_results)
        avg_ats = sum(r.avg_ats_score for r in all_results) / len(all_results)
        
        return {
            "num_simulations": num_simulations,
            "applications_per_sim": num_applications,
            "total_applications": num_simulations * num_applications,
            "avg_interview_rate": round(avg_interview_rate, 1),
            "avg_match_score": round(avg_match, 1),
            "avg_ats_score": round(avg_ats, 1),
            "simulation_results": [r.to_dict() for r in all_results],
        }


class BiasAnalyzer:
    """Analyzes potential biases in the job search agent."""
    
    POTENTIALLY_BIASED_TERMS = [
        "rockstar", "ninja", "guru", "young", "energetic",
        "native speaker", "culture fit", "prestigious",
    ]
    
    def analyze(
        self,
        jobs: list[Job],
        ranked_jobs: list[RankedJob],
        profile: UserProfile,
    ) -> BiasAnalysis:
        """
        Analyze potential biases in job selection.
        
        Args:
            jobs: All jobs found.
            ranked_jobs: Jobs after ranking.
            profile: User profile used for matching.
            
        Returns:
            BiasAnalysis with findings and recommendations.
        """
        location_dist = {}
        for job in ranked_jobs:
            loc = job.job.location.split(",")[0].strip() if job.job.location else "Unknown"
            location_dist[loc] = location_dist.get(loc, 0) + 1
        
        company_sizes = {"small": 0, "mid": 0, "large": 0, "unknown": 0}
        for job in ranked_jobs:
            text = f"{job.job.company} {job.job.description or ''}".lower()
            if any(kw in text for kw in ["startup", "seed", "series a"]):
                company_sizes["small"] += 1
            elif any(kw in text for kw in ["fortune", "enterprise", "global"]):
                company_sizes["large"] += 1
            elif any(kw in text for kw in ["series b", "series c", "growth"]):
                company_sizes["mid"] += 1
            else:
                company_sizes["unknown"] += 1
        
        salary_ranges = {"<80k": 0, "80-120k": 0, "120-160k": 0, ">160k": 0, "unknown": 0}
        for job in ranked_jobs:
            if not job.job.salary:
                salary_ranges["unknown"] += 1
                continue
            
            import re
            numbers = re.findall(r'\d+', job.job.salary.replace(",", ""))
            if numbers:
                salary = int(numbers[0])
                if salary < 80:
                    salary *= 1000
                
                if salary < 80000:
                    salary_ranges["<80k"] += 1
                elif salary < 120000:
                    salary_ranges["80-120k"] += 1
                elif salary < 160000:
                    salary_ranges["120-160k"] += 1
                else:
                    salary_ranges[">160k"] += 1
            else:
                salary_ranges["unknown"] += 1
        
        exp_levels = {"entry": 0, "mid": 0, "senior": 0, "unknown": 0}
        for job in ranked_jobs:
            title = job.job.position.lower()
            if any(kw in title for kw in ["senior", "sr.", "lead", "principal", "staff"]):
                exp_levels["senior"] += 1
            elif any(kw in title for kw in ["junior", "jr.", "entry", "associate"]):
                exp_levels["entry"] += 1
            else:
                exp_levels["mid"] += 1
        
        keyword_freq = {}
        for job in ranked_jobs:
            text = f"{job.job.position} {job.job.description or ''}".lower()
            words = set(text.split())
            for word in words:
                if len(word) > 4:
                    keyword_freq[word] = keyword_freq.get(word, 0) + 1
        
        top_keywords = sorted(keyword_freq.items(), key=lambda x: x[1], reverse=True)[:20]
        
        found_biased_terms = []
        for job in ranked_jobs:
            text = f"{job.job.position} {job.job.description or ''}".lower()
            for term in self.POTENTIALLY_BIASED_TERMS:
                if term in text:
                    found_biased_terms.append(term)
        
        recommendations = []
        
        if len(location_dist) < 3 and len(ranked_jobs) > 5:
            recommendations.append("Consider expanding location search to increase diversity of opportunities")
        
        if company_sizes["unknown"] > len(ranked_jobs) * 0.5:
            recommendations.append("Many companies have unknown sizes - consider researching companies before applying")
        
        if salary_ranges["unknown"] > len(ranked_jobs) * 0.6:
            recommendations.append("Most jobs don't list salaries - research market rates independently")
        
        if exp_levels["senior"] > len(ranked_jobs) * 0.7:
            recommendations.append("Results skew heavily toward senior roles - ensure this matches your experience")
        
        if found_biased_terms:
            recommendations.append(f"Some job postings contain potentially biased language: {', '.join(set(found_biased_terms))}")
        
        profile_skills = set(s.lower() for s in profile.get_all_skills())
        matched_any = sum(1 for j in ranked_jobs if any(s in j.matched_skills for s in profile_skills))
        if matched_any < len(ranked_jobs) * 0.3:
            recommendations.append("Low skill match rate - consider updating profile with more relevant skills")
        
        return BiasAnalysis(
            location_bias=location_dist,
            company_size_bias=company_sizes,
            salary_range_bias=salary_ranges,
            experience_level_bias=exp_levels,
            keyword_frequency=dict(top_keywords),
            excluded_keywords=list(set(found_biased_terms)),
            recommendations=recommendations,
        )
