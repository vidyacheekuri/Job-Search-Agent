"""AI-powered job ranking based on user profile matching."""

import re
from dataclasses import dataclass
from typing import Optional

from ..scraper import Job
from .profile import UserProfile


@dataclass
class RankedJob:
    """A job with ranking score and match details."""
    job: Job
    score: float
    skill_match: float
    title_match: float
    location_match: float
    experience_match: float
    company_match: float
    salary_match: float
    matched_skills: list[str]
    missing_skills: list[str]
    match_reasons: list[str]
    
    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "job": self.job.to_dict(),
            "score": self.score,
            "skill_match": self.skill_match,
            "title_match": self.title_match,
            "location_match": self.location_match,
            "experience_match": self.experience_match,
            "company_match": self.company_match,
            "salary_match": self.salary_match,
            "matched_skills": self.matched_skills,
            "missing_skills": self.missing_skills,
            "match_reasons": self.match_reasons,
        }


class JobRanker:
    """
    Ranks jobs based on how well they match a user's profile.
    Uses a weighted scoring system across multiple dimensions.
    """
    
    WEIGHTS = {
        "skills": 0.35,
        "title": 0.25,
        "location": 0.15,
        "experience": 0.10,
        "company": 0.05,
        "salary": 0.10,
    }
    
    EXPERIENCE_LEVEL_YEARS = {
        "internship": (0, 1),
        "entry": (0, 2),
        "junior": (0, 2),
        "associate": (2, 4),
        "mid": (3, 6),
        "senior": (5, 10),
        "staff": (7, 12),
        "principal": (10, 15),
        "lead": (5, 12),
        "manager": (5, 15),
        "director": (10, 20),
        "vp": (12, 25),
        "executive": (15, 30),
    }
    
    COMPANY_SIZE_KEYWORDS = {
        "small": ["startup", "small", "seed", "series a", "early stage", "emerging"],
        "mid": ["mid-size", "midsize", "mid size", "series b", "series c", "growth stage", "scale-up", "scaleup"],
        "large": ["enterprise", "fortune 500", "large", "multinational", "global", "corporation"],
    }
    
    # FAANG+ Big Tech blacklist for "Middle America" jobs assignment
    FAANG_BLACKLIST = [
        # FAANG
        "facebook", "meta", "amazon", "apple", "netflix", "google", "alphabet",
        # Extended Big Tech
        "microsoft", "tesla", "nvidia", "openai", "anthropic", "deepmind",
        "uber", "lyft", "airbnb", "stripe", "palantir", "snowflake",
        "salesforce", "oracle", "ibm", "intel", "amd", "qualcomm",
        "twitter", "x corp", "linkedin", "spotify", "pinterest", "snap",
        "bytedance", "tiktok", "alibaba", "tencent", "baidu",
        "adobe", "vmware", "servicenow", "workday", "splunk", "datadog",
        "coinbase", "robinhood", "block", "square", "paypal",
        "doordash", "instacart", "grubhub", "postmates",
        "zoom", "slack", "dropbox", "box", "twilio", "cloudflare",
    ]
    
    # Keywords indicating startup (<50 employees heuristic)
    STARTUP_INDICATORS = [
        "seed", "pre-seed", "series a", "early stage", "early-stage",
        "founding", "co-founder", "first hire", "employee #",
        "stealth", "pre-launch", "mvp", "bootstrap", "bootstrapped",
        "10 employees", "20 employees", "small team", "tight-knit team",
        "garage", "incubator", "accelerator", "y combinator", "yc",
        "techstars", "500 startups",
    ]
    
    def __init__(self, profile: UserProfile):
        """
        Initialize ranker with user profile.
        
        Args:
            profile: User profile to match jobs against.
        """
        self.profile = profile
        self._profile_skills_lower = set(s.lower() for s in profile.get_all_skills())
        self._target_roles_lower = set(r.lower() for r in profile.target_roles)
        self._preferred_locations_lower = set(l.lower() for l in profile.preferred_locations)
        self._target_companies_lower = set(c.lower() for c in profile.target_companies)
    
    def _calculate_skill_match(self, job: Job) -> tuple[float, list[str], list[str]]:
        """Calculate skill match score between 0 and 1."""
        job_text = f"{job.position} {job.description or ''}".lower()
        
        if job.skills:
            job_skills = set(s.lower() for s in job.skills)
        else:
            job_skills = set()
            for skill in self._profile_skills_lower:
                if skill in job_text:
                    job_skills.add(skill)
        
        if not job_skills and not self._profile_skills_lower:
            return 0.5, [], []
        
        matched = self._profile_skills_lower.intersection(job_skills)
        
        job_skills_in_text = set()
        for skill in self._profile_skills_lower:
            if skill in job_text:
                job_skills_in_text.add(skill)
        matched.update(job_skills_in_text)
        
        if not self._profile_skills_lower:
            return 0.5, list(matched), []
        
        score = len(matched) / len(self._profile_skills_lower)
        
        all_job_skills = job_skills.union(job_skills_in_text)
        missing = all_job_skills - matched
        
        return min(score, 1.0), list(matched), list(missing)[:5]
    
    def _calculate_title_match(self, job: Job) -> float:
        """Calculate job title match score between 0 and 1."""
        job_title_lower = job.position.lower()
        
        if not self._target_roles_lower and not self.profile.title:
            return 0.5
        
        for target in self._target_roles_lower:
            if target in job_title_lower or job_title_lower in target:
                return 1.0
        
        if self.profile.title:
            profile_title_lower = self.profile.title.lower()
            title_words = set(re.findall(r'\b\w+\b', profile_title_lower))
            job_words = set(re.findall(r'\b\w+\b', job_title_lower))
            
            stop_words = {"the", "a", "an", "and", "or", "at", "in", "for", "to", "of"}
            title_words -= stop_words
            job_words -= stop_words
            
            if title_words:
                overlap = len(title_words.intersection(job_words)) / len(title_words)
                return overlap
        
        ai_keywords = ["ai", "machine learning", "ml", "deep learning", "data scientist", 
                       "nlp", "computer vision", "artificial intelligence"]
        for kw in ai_keywords:
            if kw in job_title_lower:
                return 0.7
        
        return 0.3
    
    def _calculate_location_match(self, job: Job) -> float:
        """Calculate location match score between 0 and 1."""
        job_location_lower = job.location.lower()
        
        if "remote" in job_location_lower:
            if self.profile.remote_preference in ["remote", "flexible"]:
                return 1.0
            return 0.7
        
        if not self._preferred_locations_lower:
            return 0.5
        
        for loc in self._preferred_locations_lower:
            if loc in job_location_lower or job_location_lower in loc:
                return 1.0
        
        for loc in self._preferred_locations_lower:
            loc_parts = loc.split(',')
            for part in loc_parts:
                if part.strip() in job_location_lower:
                    return 0.8
        
        return 0.2
    
    def _calculate_experience_match(self, job: Job) -> float:
        """Calculate experience level match score between 0 and 1."""
        job_text = f"{job.position} {job.description or ''}".lower()
        user_years = self.profile.years_experience
        
        detected_level = None
        for level, (min_yrs, max_yrs) in self.EXPERIENCE_LEVEL_YEARS.items():
            if level in job_text:
                detected_level = (min_yrs, max_yrs)
                break
        
        years_pattern = r'(\d+)\+?\s*(?:years?|yrs?)'
        years_matches = re.findall(years_pattern, job_text)
        if years_matches:
            required_years = int(years_matches[0])
            if user_years >= required_years:
                return 1.0
            elif user_years >= required_years - 2:
                return 0.7
            else:
                return 0.3
        
        if detected_level:
            min_yrs, max_yrs = detected_level
            if min_yrs <= user_years <= max_yrs:
                return 1.0
            elif user_years >= min_yrs - 1:
                return 0.7
            else:
                return 0.4
        
        return 0.5
    
    def _calculate_company_match(self, job: Job) -> float:
        """Calculate company match score between 0 and 1."""
        company_lower = job.company.lower()
        
        for target in self._target_companies_lower:
            if target in company_lower or company_lower in target:
                return 1.0
        
        return 0.5
    
    def _calculate_salary_match(self, job: Job) -> float:
        """Calculate salary match score between 0 and 1."""
        if not job.salary or not self.profile.min_salary:
            return 0.5
        
        salary_text = job.salary.replace(",", "").replace("$", "").lower()
        numbers = re.findall(r'\d+', salary_text)
        
        if not numbers:
            return 0.5
        
        if "k" in salary_text or len(numbers[0]) <= 3:
            salary_value = int(numbers[0]) * 1000
        else:
            salary_value = int(numbers[0])
        
        if "/hr" in salary_text or "hourly" in salary_text:
            salary_value = salary_value * 2080
        
        if salary_value >= self.profile.min_salary:
            return 1.0
        elif salary_value >= self.profile.min_salary * 0.9:
            return 0.8
        elif salary_value >= self.profile.min_salary * 0.8:
            return 0.6
        else:
            return 0.3
    
    def _generate_match_reasons(self, ranked_job: RankedJob) -> list[str]:
        """Generate human-readable match reasons."""
        reasons = []
        
        if ranked_job.skill_match >= 0.8:
            reasons.append(f"Strong skill match ({len(ranked_job.matched_skills)} skills)")
        elif ranked_job.skill_match >= 0.5:
            reasons.append(f"Good skill match ({len(ranked_job.matched_skills)} skills)")
        
        if ranked_job.title_match >= 0.8:
            reasons.append("Excellent title match")
        elif ranked_job.title_match >= 0.6:
            reasons.append("Good title match")
        
        if ranked_job.location_match >= 0.9:
            reasons.append("Perfect location match")
        elif "remote" in ranked_job.job.location.lower():
            reasons.append("Remote opportunity")
        
        if ranked_job.salary_match >= 0.9 and ranked_job.job.salary:
            reasons.append(f"Meets salary expectations ({ranked_job.job.salary})")
        
        if ranked_job.company_match >= 0.9:
            reasons.append("Target company")
        
        if ranked_job.missing_skills:
            reasons.append(f"Consider learning: {', '.join(ranked_job.missing_skills[:3])}")
        
        return reasons
    
    def rank_job(self, job: Job) -> RankedJob:
        """
        Rank a single job against the user profile.
        
        Args:
            job: Job to rank.
            
        Returns:
            RankedJob with score and match details.
        """
        skill_match, matched_skills, missing_skills = self._calculate_skill_match(job)
        title_match = self._calculate_title_match(job)
        location_match = self._calculate_location_match(job)
        experience_match = self._calculate_experience_match(job)
        company_match = self._calculate_company_match(job)
        salary_match = self._calculate_salary_match(job)
        
        score = (
            skill_match * self.WEIGHTS["skills"] +
            title_match * self.WEIGHTS["title"] +
            location_match * self.WEIGHTS["location"] +
            experience_match * self.WEIGHTS["experience"] +
            company_match * self.WEIGHTS["company"] +
            salary_match * self.WEIGHTS["salary"]
        )
        
        ranked_job = RankedJob(
            job=job,
            score=round(score * 100, 1),
            skill_match=round(skill_match * 100, 1),
            title_match=round(title_match * 100, 1),
            location_match=round(location_match * 100, 1),
            experience_match=round(experience_match * 100, 1),
            company_match=round(company_match * 100, 1),
            salary_match=round(salary_match * 100, 1),
            matched_skills=matched_skills,
            missing_skills=missing_skills,
            match_reasons=[],
        )
        
        ranked_job.match_reasons = self._generate_match_reasons(ranked_job)
        
        return ranked_job
    
    def rank_jobs(self, jobs: list[Job], top_n: Optional[int] = None) -> list[RankedJob]:
        """
        Rank multiple jobs and return sorted by score.
        
        Args:
            jobs: List of jobs to rank.
            top_n: Optional limit on number of results.
            
        Returns:
            List of RankedJob sorted by score descending.
        """
        ranked = [self.rank_job(job) for job in jobs]
        ranked.sort(key=lambda x: x.score, reverse=True)
        
        if top_n:
            ranked = ranked[:top_n]
        
        return ranked
    
    @staticmethod
    def filter_by_company_size(jobs: list[Job], size: str = "mid") -> list[Job]:
        """
        Filter jobs by estimated company size.
        
        Args:
            jobs: List of jobs to filter.
            size: "small", "mid", or "large".
            
        Returns:
            Filtered list of jobs.
        """
        keywords = JobRanker.COMPANY_SIZE_KEYWORDS.get(size, [])
        if not keywords:
            return jobs
        
        filtered = []
        for job in jobs:
            job_text = f"{job.company} {job.description or ''}".lower()
            
            if size == "mid":
                is_small = any(kw in job_text for kw in JobRanker.COMPANY_SIZE_KEYWORDS["small"])
                is_large = any(kw in job_text for kw in JobRanker.COMPANY_SIZE_KEYWORDS["large"])
                
                if not is_small and not is_large:
                    filtered.append(job)
                elif any(kw in job_text for kw in keywords):
                    filtered.append(job)
            else:
                if any(kw in job_text for kw in keywords):
                    filtered.append(job)
        
        return filtered if filtered else jobs
    
    @staticmethod
    def filter_faang_blacklist(jobs: list[Job], log_decisions: bool = False) -> tuple[list[Job], list[dict]]:
        """
        Filter out FAANG+ big tech companies.
        
        Args:
            jobs: List of jobs to filter.
            log_decisions: Whether to log filter decisions.
            
        Returns:
            Tuple of (filtered jobs, decision log).
        """
        filtered = []
        decision_log = []
        
        for job in jobs:
            company_lower = job.company.lower()
            
            is_faang = any(faang in company_lower for faang in JobRanker.FAANG_BLACKLIST)
            
            if is_faang:
                if log_decisions:
                    decision_log.append({
                        "job": job.position,
                        "company": job.company,
                        "action": "EXCLUDED",
                        "reason": "FAANG+ blacklist",
                    })
            else:
                filtered.append(job)
                if log_decisions:
                    decision_log.append({
                        "job": job.position,
                        "company": job.company,
                        "action": "INCLUDED",
                        "reason": "Not in FAANG+ blacklist",
                    })
        
        return filtered, decision_log
    
    @staticmethod
    def filter_startups(jobs: list[Job], log_decisions: bool = False) -> tuple[list[Job], list[dict]]:
        """
        Filter out startups (<50 employees heuristic).
        
        Args:
            jobs: List of jobs to filter.
            log_decisions: Whether to log filter decisions.
            
        Returns:
            Tuple of (filtered jobs, decision log).
        """
        filtered = []
        decision_log = []
        
        for job in jobs:
            job_text = f"{job.company} {job.description or ''}".lower()
            
            is_startup = any(indicator in job_text for indicator in JobRanker.STARTUP_INDICATORS)
            
            if is_startup:
                if log_decisions:
                    decision_log.append({
                        "job": job.position,
                        "company": job.company,
                        "action": "EXCLUDED",
                        "reason": "Startup indicator detected (<50 employees heuristic)",
                    })
            else:
                filtered.append(job)
                if log_decisions:
                    decision_log.append({
                        "job": job.position,
                        "company": job.company,
                        "action": "INCLUDED",
                        "reason": "No startup indicators",
                    })
        
        return filtered, decision_log
    
    @staticmethod
    def filter_middle_america(
        jobs: list[Job], 
        exclude_faang: bool = True,
        exclude_startups: bool = True,
        log_decisions: bool = False
    ) -> tuple[list[Job], list[dict]]:
        """
        Filter for "Middle America" jobs - mid-sized companies, not big tech or startups.
        
        Args:
            jobs: List of jobs to filter.
            exclude_faang: Whether to exclude FAANG+ companies.
            exclude_startups: Whether to exclude startups.
            log_decisions: Whether to log all decisions.
            
        Returns:
            Tuple of (filtered jobs, complete decision log).
        """
        all_logs = []
        current_jobs = jobs
        
        if exclude_faang:
            current_jobs, faang_logs = JobRanker.filter_faang_blacklist(current_jobs, log_decisions)
            all_logs.extend(faang_logs)
        
        if exclude_startups:
            current_jobs, startup_logs = JobRanker.filter_startups(current_jobs, log_decisions)
            all_logs.extend(startup_logs)
        
        current_jobs = JobRanker.filter_by_company_size(current_jobs, "mid")
        
        return current_jobs, all_logs
    
    @staticmethod
    def filter_by_location(jobs: list[Job], location_filter: str, log_decisions: bool = False) -> tuple[list[Job], list[dict]]:
        """
        Filter jobs by location (e.g., 'Iowa', 'Texas', 'Remote').
        
        Args:
            jobs: List of jobs to filter.
            location_filter: Location string to match.
            log_decisions: Whether to log decisions.
            
        Returns:
            Tuple of (filtered jobs, decision log).
        """
        filtered = []
        decision_log = []
        location_lower = location_filter.lower()
        
        for job in jobs:
            job_location_lower = job.location.lower()
            
            matches = location_lower in job_location_lower or "remote" in job_location_lower
            
            if matches:
                filtered.append(job)
                if log_decisions:
                    decision_log.append({
                        "job": job.position,
                        "company": job.company,
                        "location": job.location,
                        "action": "INCLUDED",
                        "reason": f"Matches location filter: {location_filter}",
                    })
            else:
                if log_decisions:
                    decision_log.append({
                        "job": job.position,
                        "company": job.company,
                        "location": job.location,
                        "action": "EXCLUDED",
                        "reason": f"Does not match location filter: {location_filter}",
                    })
        
        return filtered, decision_log
