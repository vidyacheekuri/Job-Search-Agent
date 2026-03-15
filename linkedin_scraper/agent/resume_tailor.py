"""AI-powered resume tailoring for specific job applications."""

import os
import json
import re
from typing import Optional
from dataclasses import dataclass

from ..scraper import Job
from .profile import UserProfile


@dataclass
class TailoredResume:
    """A resume tailored for a specific job."""
    job: Job
    profile: UserProfile
    summary: str
    highlighted_skills: list[str]
    experience_bullets: list[dict]
    keywords_added: list[str]
    resume_text: str
    resume_html: str
    ats_score: float
    suggestions: list[str]


class ResumeTailor:
    """
    Tailors resumes for specific job applications.
    Can use either local heuristics or OpenAI API.
    """
    
    ATS_KEYWORDS = {
        "ai_engineer": [
            "machine learning", "deep learning", "neural networks", "tensorflow", "pytorch",
            "nlp", "computer vision", "model training", "feature engineering", "mlops",
            "data pipeline", "model deployment", "ai/ml", "large language models", "llm",
            "transformers", "bert", "gpt", "fine-tuning", "inference optimization"
        ],
        "data_scientist": [
            "statistical analysis", "predictive modeling", "data visualization", "python",
            "r programming", "sql", "machine learning", "a/b testing", "hypothesis testing",
            "pandas", "numpy", "scikit-learn", "jupyter", "data mining"
        ],
        "software_engineer": [
            "software development", "agile", "ci/cd", "version control", "git",
            "code review", "unit testing", "system design", "api development",
            "microservices", "cloud computing", "docker", "kubernetes"
        ],
        "ml_engineer": [
            "model deployment", "mlops", "model monitoring", "feature store",
            "training pipeline", "inference optimization", "model serving",
            "kubernetes", "docker", "aws sagemaker", "vertex ai", "mlflow"
        ]
    }
    
    ACTION_VERBS = [
        "Developed", "Implemented", "Designed", "Built", "Created", "Led", "Managed",
        "Optimized", "Improved", "Reduced", "Increased", "Automated", "Architected",
        "Deployed", "Integrated", "Scaled", "Mentored", "Collaborated", "Delivered",
        "Engineered", "Established", "Launched", "Streamlined", "Transformed"
    ]
    
    def __init__(self, use_openai: bool = False, api_key: Optional[str] = None):
        """
        Initialize resume tailor.
        use_openai=True uses LLM for summary (OpenAI, Claude, or Ollama per LLM_PROVIDER).
        """
        self.use_openai = use_openai
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self._openai_client = None
        provider = (os.getenv("LLM_PROVIDER") or "").lower()
        if not provider:
            if os.getenv("OPENAI_API_KEY") or self.api_key:
                provider = "openai"
            elif os.getenv("ANTHROPIC_API_KEY"):
                provider = "anthropic"
            else:
                provider = "ollama"
        self.provider = provider
        if self.use_openai and provider == "openai" and (self.api_key or os.getenv("OPENAI_API_KEY")):
            try:
                from openai import OpenAI
                self._openai_client = OpenAI(api_key=self.api_key or os.getenv("OPENAI_API_KEY"))
            except ImportError:
                pass
    
    def _extract_job_keywords(self, job: Job) -> list[str]:
        """Extract important keywords from job posting."""
        text = f"{job.position} {job.description or ''}".lower()
        
        keywords = []
        
        for category, kw_list in self.ATS_KEYWORDS.items():
            for kw in kw_list:
                if kw.lower() in text:
                    keywords.append(kw)
        
        tech_pattern = r'\b(python|java|javascript|typescript|c\+\+|go|rust|ruby|scala|kotlin)\b'
        tech_matches = re.findall(tech_pattern, text, re.IGNORECASE)
        keywords.extend([t.capitalize() for t in tech_matches])
        
        framework_pattern = r'\b(react|vue|angular|django|flask|fastapi|spring|node\.?js|express)\b'
        framework_matches = re.findall(framework_pattern, text, re.IGNORECASE)
        keywords.extend(framework_matches)
        
        cloud_pattern = r'\b(aws|azure|gcp|google cloud|amazon web services)\b'
        cloud_matches = re.findall(cloud_pattern, text, re.IGNORECASE)
        keywords.extend(cloud_matches)
        
        return list(set(keywords))
    
    def _determine_job_category(self, job: Job) -> str:
        """Determine the job category for keyword matching."""
        title_lower = job.position.lower()
        
        if any(kw in title_lower for kw in ["ai engineer", "artificial intelligence"]):
            return "ai_engineer"
        elif any(kw in title_lower for kw in ["ml engineer", "machine learning engineer"]):
            return "ml_engineer"
        elif any(kw in title_lower for kw in ["data scientist", "data science"]):
            return "data_scientist"
        else:
            return "software_engineer"
    
    def _generate_tailored_summary(self, profile: UserProfile, job: Job, keywords: list[str]) -> str:
        """Generate a summary tailored to the job."""
        if self.use_openai:
            out = self._generate_summary_llm(profile, job, keywords)
            if out:
                return out
        return self._generate_summary_local(profile, job, keywords)
    
    def _generate_summary_local(self, profile: UserProfile, job: Job, keywords: list[str]) -> str:
        """Generate summary using local heuristics."""
        years = profile.years_experience
        title = profile.title or "professional"
        
        key_skills = []
        profile_skills = profile.get_all_skills()
        for skill in profile_skills[:6]:
            if skill.lower() in [k.lower() for k in keywords]:
                key_skills.insert(0, skill)
            else:
                key_skills.append(skill)
        key_skills = key_skills[:4]
        
        job_category = self._determine_job_category(job)
        
        templates = {
            "ai_engineer": f"Results-driven {title} with {years}+ years of experience in artificial intelligence and machine learning. Proven expertise in {', '.join(key_skills[:3])}. Passionate about developing innovative AI solutions that drive business impact.",
            "ml_engineer": f"Experienced {title} with {years}+ years specializing in machine learning systems and MLOps. Strong background in {', '.join(key_skills[:3])}. Committed to building scalable, production-ready ML pipelines.",
            "data_scientist": f"Analytical {title} with {years}+ years of experience in data science and statistical modeling. Expert in {', '.join(key_skills[:3])}. Skilled at transforming complex data into actionable insights.",
            "software_engineer": f"Skilled {title} with {years}+ years of experience building robust software systems. Proficient in {', '.join(key_skills[:3])}. Dedicated to writing clean, maintainable code and delivering high-quality solutions.",
        }
        
        return templates.get(job_category, templates["software_engineer"])
    
    def _build_summary_prompt(self, profile: UserProfile, job: Job, keywords: list[str]) -> str:
        """Build prompt for LLM resume summary."""
        return f"""Write a professional resume summary (2-3 sentences) for this candidate applying to this job.

Candidate:
- Name: {profile.name}
- Current Title: {profile.title}
- Years of Experience: {profile.years_experience}
- Key Skills: {', '.join(profile.get_all_skills()[:10])}
- Summary: {profile.summary}

Job:
- Title: {job.position}
- Company: {job.company}
- Description: {(job.description or '')[:500]}

Important keywords to include: {', '.join(keywords[:10])}

Write a compelling, ATS-friendly summary that highlights relevant experience and skills for this specific role."""

    def _generate_summary_llm(self, profile: UserProfile, job: Job, keywords: list[str]) -> Optional[str]:
        """Generate summary using OpenAI, Claude, or Ollama."""
        prompt = self._build_summary_prompt(profile, job, keywords)
        try:
            if self.provider == "openai" and (self._openai_client or os.getenv("OPENAI_API_KEY")):
                client = self._openai_client
                if not client:
                    from openai import OpenAI
                    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
                resp = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=200,
                    temperature=0.7,
                )
                return (resp.choices[0].message.content or "").strip()
            if self.provider == "anthropic" and os.getenv("ANTHROPIC_API_KEY"):
                import anthropic
                client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
                resp = client.messages.create(
                    model="claude-3-5-sonnet-20240620",
                    max_tokens=200,
                    temperature=0.7,
                    messages=[{"role": "user", "content": prompt}],
                )
                parts = [b.text for b in resp.content if getattr(b, "type", "") == "text"]
                return ("\n".join(parts)).strip() if parts else None
            if self.provider == "ollama":
                import json
                import requests
                payload = {
                    "model": os.getenv("OLLAMA_MODEL", "llama3.2"),
                    "messages": [{"role": "user", "content": prompt}],
                    "stream": False,
                }
                r = requests.post("http://localhost:11434/api/chat", data=json.dumps(payload), timeout=60)
                if r.ok:
                    text = (r.json().get("message") or {}).get("content", "")
                    return text.strip() if text else None
        except Exception:
            pass
        return None

    def _generate_summary_openai(self, profile: UserProfile, job: Job, keywords: list[str]) -> str:
        """Legacy: generate summary via LLM (delegates to _generate_summary_llm)."""
        out = self._generate_summary_llm(profile, job, keywords)
        return out or self._generate_summary_local(profile, job, keywords)
    
    def _tailor_experience_bullets(self, profile: UserProfile, job: Job, keywords: list[str]) -> list[dict]:
        """Tailor experience bullets to highlight relevant achievements."""
        tailored_experience = []
        keywords_lower = set(k.lower() for k in keywords)
        
        for exp in profile.experience:
            tailored_exp = exp.copy()
            highlights = exp.get("highlights", [])
            description = exp.get("description", "")
            
            scored_highlights = []
            for highlight in highlights:
                highlight_lower = highlight.lower()
                relevance = sum(1 for kw in keywords_lower if kw in highlight_lower)
                scored_highlights.append((relevance, highlight))
            
            scored_highlights.sort(reverse=True)
            
            reordered = [h for _, h in scored_highlights]
            
            improved_highlights = []
            for highlight in reordered:
                if not any(highlight.startswith(verb) for verb in self.ACTION_VERBS):
                    for verb in self.ACTION_VERBS:
                        if verb.lower() in highlight.lower():
                            highlight = f"{verb} {highlight[0].lower()}{highlight[1:]}"
                            break
                improved_highlights.append(highlight)
            
            tailored_exp["highlights"] = improved_highlights
            tailored_exp["relevance_score"] = scored_highlights[0][0] if scored_highlights else 0
            tailored_experience.append(tailored_exp)
        
        tailored_experience.sort(key=lambda x: x.get("relevance_score", 0), reverse=True)
        
        return tailored_experience
    
    def _calculate_ats_score(self, resume_text: str, job: Job) -> float:
        """Calculate ATS compatibility score."""
        job_text = f"{job.position} {job.description or ''}".lower()
        resume_lower = resume_text.lower()
        
        job_words = set(re.findall(r'\b\w{4,}\b', job_text))
        resume_words = set(re.findall(r'\b\w{4,}\b', resume_lower))
        
        stop_words = {"with", "that", "this", "have", "from", "they", "will", "what", "your"}
        job_words -= stop_words
        
        if not job_words:
            return 50.0
        
        matched = job_words.intersection(resume_words)
        base_score = (len(matched) / len(job_words)) * 100
        
        keywords = self._extract_job_keywords(job)
        keyword_matches = sum(1 for kw in keywords if kw.lower() in resume_lower)
        keyword_score = (keyword_matches / max(len(keywords), 1)) * 100
        
        final_score = (base_score * 0.4) + (keyword_score * 0.6)
        
        return min(round(final_score, 1), 100.0)
    
    def _generate_suggestions(self, profile: UserProfile, job: Job, keywords: list[str], ats_score: float) -> list[str]:
        """Generate suggestions for improving the resume."""
        suggestions = []
        
        profile_skills = set(s.lower() for s in profile.get_all_skills())
        missing_keywords = [kw for kw in keywords if kw.lower() not in profile_skills]
        
        if missing_keywords:
            suggestions.append(f"Consider adding these keywords if applicable: {', '.join(missing_keywords[:5])}")
        
        if ats_score < 60:
            suggestions.append("Resume could be better optimized for ATS. Add more job-specific keywords.")
        
        for exp in profile.experience:
            highlights = exp.get("highlights", [])
            for highlight in highlights:
                if not re.search(r'\d+%|\d+x|\$[\d,]+|\d+ (users|customers|team|projects)', highlight):
                    suggestions.append(f"Add quantifiable metrics to: '{highlight[:50]}...'")
                    break
            break
        
        if not profile.summary:
            suggestions.append("Add a professional summary section at the top of your resume.")
        
        if len(profile.get_all_skills()) < 8:
            suggestions.append("Consider listing more relevant technical skills.")
        
        return suggestions[:5]
    
    def _generate_resume_text(self, profile: UserProfile, summary: str, experience: list[dict], skills: list[str]) -> str:
        """Generate plain text resume."""
        sections = []
        
        sections.append(f"# {profile.name}")
        if profile.title:
            sections.append(profile.title)
        
        contact = []
        if profile.email:
            contact.append(profile.email)
        if profile.phone:
            contact.append(profile.phone)
        if profile.location:
            contact.append(profile.location)
        if contact:
            sections.append(" | ".join(contact))
        
        links = []
        if profile.linkedin_url:
            links.append(profile.linkedin_url)
        if profile.github_url:
            links.append(profile.github_url)
        if links:
            sections.append(" | ".join(links))
        
        sections.append(f"\n## Professional Summary\n{summary}")
        
        if skills:
            sections.append(f"\n## Technical Skills\n{', '.join(skills)}")
        
        if experience:
            sections.append("\n## Professional Experience")
            for exp in experience:
                title = exp.get("title", "")
                company = exp.get("company", "")
                duration = exp.get("duration", "")
                location = exp.get("location", "")
                
                sections.append(f"\n### {title}")
                sections.append(f"{company} | {location} | {duration}")
                
                for highlight in exp.get("highlights", []):
                    sections.append(f"• {highlight}")
        
        if profile.education:
            sections.append("\n## Education")
            for edu in profile.education:
                degree = edu.get("degree", "")
                school = edu.get("school", "")
                year = edu.get("year", "")
                sections.append(f"{degree} | {school} | {year}")
        
        if profile.certifications:
            sections.append(f"\n## Certifications\n• " + "\n• ".join(profile.certifications))
        
        return "\n".join(sections)
    
    def _generate_resume_html(self, profile: UserProfile, summary: str, experience: list[dict], skills: list[str]) -> str:
        """Generate HTML resume."""
        html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>{profile.name} - Resume</title>
    <style>
        body {{ font-family: 'Arial', sans-serif; max-width: 800px; margin: 0 auto; padding: 40px; line-height: 1.5; color: #333; }}
        h1 {{ margin-bottom: 5px; color: #1a1a1a; }}
        h2 {{ color: #2563eb; border-bottom: 2px solid #2563eb; padding-bottom: 5px; margin-top: 25px; }}
        h3 {{ margin-bottom: 5px; }}
        .contact {{ color: #666; margin-bottom: 10px; }}
        .links {{ margin-bottom: 20px; }}
        .links a {{ color: #2563eb; text-decoration: none; margin-right: 15px; }}
        .summary {{ background: #f8fafc; padding: 15px; border-radius: 8px; margin: 20px 0; }}
        .skills {{ display: flex; flex-wrap: wrap; gap: 8px; }}
        .skill {{ background: #e0e7ff; color: #3730a3; padding: 4px 12px; border-radius: 15px; font-size: 14px; }}
        .experience {{ margin-bottom: 20px; }}
        .exp-header {{ display: flex; justify-content: space-between; align-items: baseline; }}
        .company {{ color: #666; }}
        ul {{ margin-top: 8px; }}
        li {{ margin-bottom: 5px; }}
    </style>
</head>
<body>
    <h1>{profile.name}</h1>
    <p class="contact">{profile.title}</p>
    <p class="contact">{' | '.join(filter(None, [profile.email, profile.phone, profile.location]))}</p>
    <p class="links">
        {'<a href="' + profile.linkedin_url + '">LinkedIn</a>' if profile.linkedin_url else ''}
        {'<a href="' + profile.github_url + '">GitHub</a>' if profile.github_url else ''}
        {'<a href="' + profile.portfolio_url + '">Portfolio</a>' if profile.portfolio_url else ''}
    </p>
    
    <h2>Professional Summary</h2>
    <div class="summary">{summary}</div>
    
    <h2>Technical Skills</h2>
    <div class="skills">
        {''.join(f'<span class="skill">{s}</span>' for s in skills)}
    </div>
    
    <h2>Professional Experience</h2>
"""
        
        for exp in experience:
            html += f"""
    <div class="experience">
        <div class="exp-header">
            <h3>{exp.get('title', '')}</h3>
            <span>{exp.get('duration', '')}</span>
        </div>
        <p class="company">{exp.get('company', '')} | {exp.get('location', '')}</p>
        <ul>
            {''.join(f'<li>{h}</li>' for h in exp.get('highlights', []))}
        </ul>
    </div>
"""
        
        if profile.education:
            html += "\n    <h2>Education</h2>\n"
            for edu in profile.education:
                html += f"    <p><strong>{edu.get('degree', '')}</strong> - {edu.get('school', '')} ({edu.get('year', '')})</p>\n"
        
        if profile.certifications:
            html += "\n    <h2>Certifications</h2>\n    <ul>\n"
            for cert in profile.certifications:
                html += f"        <li>{cert}</li>\n"
            html += "    </ul>\n"
        
        html += """
</body>
</html>"""
        
        return html
    
    def tailor_resume(self, profile: UserProfile, job: Job) -> TailoredResume:
        """
        Create a resume tailored for a specific job.
        
        Args:
            profile: User profile with experience and skills.
            job: Target job to tailor resume for.
            
        Returns:
            TailoredResume with tailored content and analysis.
        """
        keywords = self._extract_job_keywords(job)
        
        summary = self._generate_tailored_summary(profile, job, keywords)
        
        experience = self._tailor_experience_bullets(profile, job, keywords)
        
        profile_skills = profile.get_all_skills()
        keywords_lower = set(k.lower() for k in keywords)
        
        prioritized_skills = []
        other_skills = []
        for skill in profile_skills:
            if skill.lower() in keywords_lower:
                prioritized_skills.append(skill)
            else:
                other_skills.append(skill)
        highlighted_skills = prioritized_skills + other_skills
        
        keywords_added = [kw for kw in keywords if kw.lower() in summary.lower()]
        
        resume_text = self._generate_resume_text(profile, summary, experience, highlighted_skills)
        resume_html = self._generate_resume_html(profile, summary, experience, highlighted_skills)
        
        ats_score = self._calculate_ats_score(resume_text, job)
        
        suggestions = self._generate_suggestions(profile, job, keywords, ats_score)
        
        return TailoredResume(
            job=job,
            profile=profile,
            summary=summary,
            highlighted_skills=highlighted_skills,
            experience_bullets=experience,
            keywords_added=keywords_added,
            resume_text=resume_text,
            resume_html=resume_html,
            ats_score=ats_score,
            suggestions=suggestions,
        )
