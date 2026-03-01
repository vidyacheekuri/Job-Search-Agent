"""User profile management for the job search agent."""

import json
import re
from dataclasses import dataclass, field, asdict
from typing import Optional
from pathlib import Path


@dataclass
class UserProfile:
    """Represents a job seeker's profile for matching and tailoring."""
    
    name: str = ""
    email: str = ""
    phone: str = ""
    location: str = ""
    linkedin_url: str = ""
    github_url: str = ""
    portfolio_url: str = ""
    
    title: str = ""
    summary: str = ""
    years_experience: int = 0
    
    skills: list[str] = field(default_factory=list)
    programming_languages: list[str] = field(default_factory=list)
    frameworks: list[str] = field(default_factory=list)
    tools: list[str] = field(default_factory=list)
    
    experience: list[dict] = field(default_factory=list)
    education: list[dict] = field(default_factory=list)
    certifications: list[str] = field(default_factory=list)
    projects: list[dict] = field(default_factory=list)
    
    target_roles: list[str] = field(default_factory=list)
    target_companies: list[str] = field(default_factory=list)
    preferred_locations: list[str] = field(default_factory=list)
    remote_preference: str = "flexible"
    min_salary: int = 0
    
    def to_dict(self) -> dict:
        """Convert profile to dictionary."""
        return asdict(self)
    
    def to_json(self) -> str:
        """Convert profile to JSON string."""
        return json.dumps(self.to_dict(), indent=2)
    
    @classmethod
    def from_dict(cls, data: dict) -> "UserProfile":
        """Create profile from dictionary."""
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})
    
    @classmethod
    def from_json(cls, json_str: str) -> "UserProfile":
        """Create profile from JSON string."""
        return cls.from_dict(json.loads(json_str))
    
    @classmethod
    def from_file(cls, path: str) -> "UserProfile":
        """Load profile from JSON file."""
        with open(path, 'r') as f:
            return cls.from_json(f.read())
    
    def save(self, path: str) -> None:
        """Save profile to JSON file."""
        with open(path, 'w') as f:
            f.write(self.to_json())
    
    def get_all_skills(self) -> list[str]:
        """Get all skills combined."""
        all_skills = set(self.skills)
        all_skills.update(self.programming_languages)
        all_skills.update(self.frameworks)
        all_skills.update(self.tools)
        return list(all_skills)
    
    def get_experience_summary(self) -> str:
        """Get a text summary of work experience."""
        if not self.experience:
            return ""
        
        lines = []
        for exp in self.experience:
            title = exp.get("title", "")
            company = exp.get("company", "")
            duration = exp.get("duration", "")
            description = exp.get("description", "")
            
            lines.append(f"{title} at {company} ({duration})")
            if description:
                lines.append(f"  {description[:200]}...")
        
        return "\n".join(lines)
    
    def get_resume_text(self) -> str:
        """Generate plain text resume from profile."""
        sections = []
        
        sections.append(f"# {self.name}")
        if self.title:
            sections.append(self.title)
        
        contact = []
        if self.email:
            contact.append(self.email)
        if self.phone:
            contact.append(self.phone)
        if self.location:
            contact.append(self.location)
        if contact:
            sections.append(" | ".join(contact))
        
        links = []
        if self.linkedin_url:
            links.append(f"LinkedIn: {self.linkedin_url}")
        if self.github_url:
            links.append(f"GitHub: {self.github_url}")
        if self.portfolio_url:
            links.append(f"Portfolio: {self.portfolio_url}")
        if links:
            sections.append(" | ".join(links))
        
        if self.summary:
            sections.append(f"\n## Summary\n{self.summary}")
        
        all_skills = self.get_all_skills()
        if all_skills:
            sections.append(f"\n## Skills\n{', '.join(all_skills)}")
        
        if self.experience:
            sections.append("\n## Experience")
            for exp in self.experience:
                title = exp.get("title", "")
                company = exp.get("company", "")
                duration = exp.get("duration", "")
                description = exp.get("description", "")
                highlights = exp.get("highlights", [])
                
                sections.append(f"\n### {title}")
                sections.append(f"{company} | {duration}")
                if description:
                    sections.append(description)
                for highlight in highlights:
                    sections.append(f"• {highlight}")
        
        if self.education:
            sections.append("\n## Education")
            for edu in self.education:
                degree = edu.get("degree", "")
                school = edu.get("school", "")
                year = edu.get("year", "")
                sections.append(f"{degree} - {school} ({year})")
        
        if self.certifications:
            sections.append(f"\n## Certifications\n{', '.join(self.certifications)}")
        
        if self.projects:
            sections.append("\n## Projects")
            for proj in self.projects:
                name = proj.get("name", "")
                description = proj.get("description", "")
                tech = proj.get("technologies", [])
                sections.append(f"\n### {name}")
                if description:
                    sections.append(description)
                if tech:
                    sections.append(f"Technologies: {', '.join(tech)}")
        
        return "\n".join(sections)


def parse_resume_text(text: str) -> UserProfile:
    """
    Parse plain text resume into a UserProfile.
    Uses heuristics to extract information.
    """
    profile = UserProfile()
    lines = text.strip().split('\n')
    
    if lines:
        first_line = lines[0].strip().lstrip('#').strip()
        if len(first_line) < 50 and not any(c in first_line for c in ['@', ':', '|']):
            profile.name = first_line
    
    email_pattern = r'[\w\.-]+@[\w\.-]+\.\w+'
    emails = re.findall(email_pattern, text)
    if emails:
        profile.email = emails[0]
    
    phone_pattern = r'\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}'
    phones = re.findall(phone_pattern, text)
    if phones:
        profile.phone = phones[0]
    
    linkedin_pattern = r'linkedin\.com/in/[\w-]+'
    linkedin = re.findall(linkedin_pattern, text.lower())
    if linkedin:
        profile.linkedin_url = f"https://www.{linkedin[0]}"
    
    github_pattern = r'github\.com/[\w-]+'
    github = re.findall(github_pattern, text.lower())
    if github:
        profile.github_url = f"https://www.{github[0]}"
    
    common_skills = [
        "Python", "JavaScript", "TypeScript", "Java", "C++", "C#", "Go", "Rust", "Ruby", "PHP",
        "React", "Vue", "Angular", "Node.js", "Django", "Flask", "FastAPI", "Spring", "Express",
        "TensorFlow", "PyTorch", "Keras", "Scikit-learn", "Pandas", "NumPy",
        "AWS", "Azure", "GCP", "Docker", "Kubernetes", "Git", "Linux", "SQL", "MongoDB",
        "Machine Learning", "Deep Learning", "NLP", "Computer Vision", "AI", "Data Science",
        "REST API", "GraphQL", "Microservices", "CI/CD", "Agile", "Scrum",
    ]
    
    text_lower = text.lower()
    found_skills = []
    for skill in common_skills:
        if skill.lower() in text_lower:
            found_skills.append(skill)
    profile.skills = found_skills
    
    title_keywords = ["engineer", "developer", "scientist", "analyst", "manager", "architect", "lead"]
    for line in lines[1:10]:
        line_lower = line.lower().strip()
        if any(kw in line_lower for kw in title_keywords) and len(line) < 60:
            profile.title = line.strip()
            break
    
    return profile
