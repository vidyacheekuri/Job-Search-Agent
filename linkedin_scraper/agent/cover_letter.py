"""AI-powered cover letter generation for job applications."""

import os
import re
from typing import Optional
from dataclasses import dataclass

from ..scraper import Job
from .profile import UserProfile


@dataclass
class CoverLetter:
    """A generated cover letter for a job application."""
    job: Job
    profile: UserProfile
    content: str
    html_content: str
    word_count: int
    key_points: list[str]
    personalization_score: float


class CoverLetterGenerator:
    """
    Generates personalized cover letters for job applications.
    Can use either local templates or OpenAI API.
    """
    
    TEMPLATES = {
        "ai_engineer": """Dear Hiring Manager,

I am writing to express my strong interest in the {position} role at {company}. With {years} years of experience in artificial intelligence and machine learning, I am confident in my ability to contribute to your team's success.

{experience_paragraph}

{skills_paragraph}

{company_paragraph}

I am excited about the opportunity to bring my expertise in {top_skills} to {company}. I would welcome the chance to discuss how my background and skills would be a great fit for your team.

Thank you for considering my application. I look forward to hearing from you.

Sincerely,
{name}""",

        "software_engineer": """Dear Hiring Manager,

I am excited to apply for the {position} position at {company}. As a software engineer with {years} years of experience, I have developed a strong foundation in building scalable, maintainable systems.

{experience_paragraph}

{skills_paragraph}

{company_paragraph}

I am eager to contribute my expertise in {top_skills} to {company}'s continued success. I believe my technical skills and passion for building great software make me an excellent candidate for this role.

Thank you for your time and consideration.

Best regards,
{name}""",

        "data_scientist": """Dear Hiring Manager,

I am thrilled to apply for the {position} role at {company}. With {years} years of experience in data science and analytics, I have a proven track record of turning complex data into actionable insights.

{experience_paragraph}

{skills_paragraph}

{company_paragraph}

I am passionate about using data to drive decision-making and would love to bring my expertise in {top_skills} to {company}. I am confident that my analytical skills and experience would be a valuable addition to your team.

Thank you for considering my application.

Sincerely,
{name}""",
    }
    
    def __init__(self, use_openai: bool = False, api_key: Optional[str] = None):
        """
        Initialize cover letter generator.
        
        Args:
            use_openai: Whether to use OpenAI API for generation.
            api_key: OpenAI API key (or set OPENAI_API_KEY env var).
        """
        self.use_openai = use_openai
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self._openai_client = None
        
        if self.use_openai and self.api_key:
            try:
                from openai import OpenAI
                self._openai_client = OpenAI(api_key=self.api_key)
            except ImportError:
                self.use_openai = False
    
    def _determine_job_category(self, job: Job) -> str:
        """Determine job category for template selection."""
        title_lower = job.position.lower()
        
        if any(kw in title_lower for kw in ["ai", "machine learning", "ml", "deep learning", "nlp"]):
            return "ai_engineer"
        elif any(kw in title_lower for kw in ["data scientist", "data science", "analytics"]):
            return "data_scientist"
        else:
            return "software_engineer"
    
    def _extract_company_info(self, job: Job) -> dict:
        """Extract information about the company from job posting."""
        description = job.description or ""
        
        info = {
            "industry": "",
            "mission": "",
            "products": [],
            "values": [],
        }
        
        tech_keywords = ["saas", "fintech", "healthcare", "e-commerce", "edtech", "ai/ml", "cybersecurity"]
        for kw in tech_keywords:
            if kw in description.lower():
                info["industry"] = kw.capitalize()
                break
        
        mission_patterns = [
            r"our mission is ([^.]+)\.",
            r"we are dedicated to ([^.]+)\.",
            r"we're building ([^.]+)\.",
            r"we help ([^.]+)\.",
        ]
        for pattern in mission_patterns:
            match = re.search(pattern, description.lower())
            if match:
                info["mission"] = match.group(1).strip()
                break
        
        value_keywords = ["innovation", "diversity", "collaboration", "excellence", "integrity", "growth"]
        info["values"] = [v for v in value_keywords if v in description.lower()]
        
        return info
    
    def _generate_experience_paragraph(self, profile: UserProfile, job: Job) -> str:
        """Generate paragraph highlighting relevant experience."""
        if not profile.experience:
            return "Throughout my career, I have developed strong technical skills and a passion for solving complex problems."
        
        recent_exp = profile.experience[0]
        title = recent_exp.get("title", "my role")
        company = recent_exp.get("company", "my previous company")
        highlights = recent_exp.get("highlights", [])
        
        if highlights:
            job_text = f"{job.position} {job.description or ''}".lower()
            
            relevant_highlight = highlights[0]
            for h in highlights:
                h_lower = h.lower()
                if any(kw in h_lower for kw in ["ai", "machine learning", "model", "data", "system"]):
                    if any(kw in job_text for kw in ["ai", "machine learning", "model", "data"]):
                        relevant_highlight = h
                        break
            
            return f"In my current role as {title} at {company}, I have {relevant_highlight[0].lower()}{relevant_highlight[1:] if not relevant_highlight[0].isupper() else relevant_highlight[1:]}. This experience has honed my ability to deliver results in fast-paced environments."
        
        return f"As a {title} at {company}, I have gained valuable experience in developing innovative solutions and collaborating with cross-functional teams."
    
    def _generate_skills_paragraph(self, profile: UserProfile, job: Job) -> str:
        """Generate paragraph about technical skills."""
        skills = profile.get_all_skills()
        
        if not skills:
            return "I have developed a diverse skill set that enables me to tackle complex technical challenges."
        
        job_text = f"{job.position} {job.description or ''}".lower()
        
        relevant_skills = []
        other_skills = []
        for skill in skills:
            if skill.lower() in job_text:
                relevant_skills.append(skill)
            else:
                other_skills.append(skill)
        
        top_skills = (relevant_skills + other_skills)[:5]
        
        if len(top_skills) >= 3:
            skills_str = f"{', '.join(top_skills[:-1])}, and {top_skills[-1]}"
        else:
            skills_str = " and ".join(top_skills)
        
        return f"My technical expertise includes {skills_str}. I am constantly learning and staying current with industry best practices to deliver cutting-edge solutions."
    
    def _generate_company_paragraph(self, profile: UserProfile, job: Job) -> str:
        """Generate paragraph about interest in the company."""
        company_info = self._extract_company_info(job)
        company = job.company
        
        if company_info["mission"]:
            return f"I am particularly drawn to {company}'s mission to {company_info['mission']}. This aligns with my own passion for creating technology that makes a meaningful impact."
        
        if company_info["industry"]:
            return f"I am excited about {company}'s work in the {company_info['industry']} space. The opportunity to apply my skills in this innovative field is very appealing to me."
        
        if company_info["values"]:
            values_str = " and ".join(company_info["values"][:2])
            return f"I admire {company}'s commitment to {values_str}. These values resonate with my own professional philosophy and approach to work."
        
        return f"I have been following {company}'s growth and am impressed by the innovative work your team is doing. I would be honored to contribute to your mission."
    
    def _generate_cover_letter_local(self, profile: UserProfile, job: Job) -> str:
        """Generate cover letter using local templates."""
        category = self._determine_job_category(job)
        template = self.TEMPLATES.get(category, self.TEMPLATES["software_engineer"])
        
        top_skills = profile.get_all_skills()[:3]
        top_skills_str = ", ".join(top_skills) if top_skills else "software development"
        
        letter = template.format(
            position=job.position,
            company=job.company,
            years=profile.years_experience or 3,
            name=profile.name or "Your Name",
            top_skills=top_skills_str,
            experience_paragraph=self._generate_experience_paragraph(profile, job),
            skills_paragraph=self._generate_skills_paragraph(profile, job),
            company_paragraph=self._generate_company_paragraph(profile, job),
        )
        
        return letter
    
    def _generate_cover_letter_openai(self, profile: UserProfile, job: Job) -> str:
        """Generate cover letter using OpenAI API."""
        prompt = f"""Write a professional cover letter for a job application.

Candidate Information:
- Name: {profile.name}
- Current Title: {profile.title}
- Years of Experience: {profile.years_experience}
- Key Skills: {', '.join(profile.get_all_skills()[:10])}
- Summary: {profile.summary}
- Recent Experience: {profile.experience[0] if profile.experience else 'N/A'}

Job Information:
- Position: {job.position}
- Company: {job.company}
- Location: {job.location}
- Description: {(job.description or '')[:1000]}

Write a compelling, personalized cover letter (about 300-400 words) that:
1. Shows enthusiasm for the specific role and company
2. Highlights relevant experience and skills
3. Demonstrates knowledge of the company's work
4. Includes a strong opening and closing
5. Maintains a professional but personable tone

Do not include placeholders - write the complete letter."""

        try:
            response = self._openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=800,
                temperature=0.7
            )
            return response.choices[0].message.content.strip()
        except Exception:
            return self._generate_cover_letter_local(profile, job)
    
    def _generate_html(self, content: str, profile: UserProfile, job: Job) -> str:
        """Generate HTML version of cover letter."""
        paragraphs = content.split('\n\n')
        html_paragraphs = '\n'.join(f'<p>{p.replace(chr(10), "<br>")}</p>' for p in paragraphs if p.strip())
        
        return f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Cover Letter - {profile.name} - {job.position} at {job.company}</title>
    <style>
        body {{
            font-family: 'Georgia', serif;
            max-width: 700px;
            margin: 0 auto;
            padding: 60px 40px;
            line-height: 1.8;
            color: #333;
        }}
        .header {{
            margin-bottom: 40px;
        }}
        .date {{
            color: #666;
            margin-bottom: 20px;
        }}
        p {{
            margin-bottom: 16px;
            text-align: justify;
        }}
        .signature {{
            margin-top: 30px;
        }}
    </style>
</head>
<body>
    <div class="header">
        <p><strong>{profile.name}</strong><br>
        {profile.email}<br>
        {profile.phone}<br>
        {profile.location}</p>
    </div>
    
    {html_paragraphs}
</body>
</html>"""
    
    def _extract_key_points(self, content: str) -> list[str]:
        """Extract key points from cover letter."""
        points = []
        
        skill_pattern = r'expertise in ([^,.]+)'
        skill_matches = re.findall(skill_pattern, content.lower())
        if skill_matches:
            points.append(f"Highlights skills: {skill_matches[0]}")
        
        experience_patterns = [
            r'(\d+)\s*years?\s*(of)?\s*experience',
            r'in my (?:current|previous) role as ([^,]+)',
        ]
        for pattern in experience_patterns:
            match = re.search(pattern, content.lower())
            if match:
                points.append(f"Mentions: {match.group(0)}")
                break
        
        company_mentions = content.count(re.sub(r'[^\w]', '', content.split(',')[0] if content else ''))
        if company_mentions > 1:
            points.append("Personalizes for company")
        
        action_words = ["delivered", "achieved", "built", "led", "developed", "implemented"]
        for word in action_words:
            if word in content.lower():
                points.append(f"Uses action verb: {word}")
                break
        
        return points[:5]
    
    def _calculate_personalization_score(self, content: str, job: Job) -> float:
        """Calculate how personalized the cover letter is."""
        score = 0.0
        
        if job.company.lower() in content.lower():
            score += 25
        
        if job.position.lower() in content.lower():
            score += 20
        
        job_keywords = set(re.findall(r'\b\w{5,}\b', (job.description or '').lower()))
        letter_keywords = set(re.findall(r'\b\w{5,}\b', content.lower()))
        
        if job_keywords:
            overlap = len(job_keywords.intersection(letter_keywords)) / len(job_keywords)
            score += overlap * 30
        
        if len(content.split()) > 250:
            score += 15
        elif len(content.split()) > 150:
            score += 10
        
        if any(phrase in content.lower() for phrase in ["your mission", "your team", "your company", "your work"]):
            score += 10
        
        return min(score, 100.0)
    
    def generate(self, profile: UserProfile, job: Job) -> CoverLetter:
        """
        Generate a personalized cover letter for a job application.
        
        Args:
            profile: User profile with experience and background.
            job: Target job to write cover letter for.
            
        Returns:
            CoverLetter with content and analysis.
        """
        if self.use_openai and self._openai_client:
            content = self._generate_cover_letter_openai(profile, job)
        else:
            content = self._generate_cover_letter_local(profile, job)
        
        html_content = self._generate_html(content, profile, job)
        word_count = len(content.split())
        key_points = self._extract_key_points(content)
        personalization_score = self._calculate_personalization_score(content, job)
        
        return CoverLetter(
            job=job,
            profile=profile,
            content=content,
            html_content=html_content,
            word_count=word_count,
            key_points=key_points,
            personalization_score=personalization_score,
        )
