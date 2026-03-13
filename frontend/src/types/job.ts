export interface Job {
  position: string;
  company: string;
  company_logo: string | null;
  location: string;
  date: string;
  ago_time: string;
  salary: string;
  job_url: string;
  description?: string | null;
  skills?: string[] | null;
  apply_method?: string | null;
  applicant_count?: string | null;
  source?: string;
}

export type JobSource = 'linkedin' | 'indeed' | 'greenhouse';

export interface RankedJob {
  job: Job;
  score: number;
  skill_match: number;
  title_match: number;
  location_match: number;
  experience_match: number;
  matched_skills: string[];
  missing_skills: string[];
  match_reasons: string[];
}

export interface SavedJob extends Job {
  savedAt: string;
  notes?: string;
}

export interface AppliedJob extends Job {
  appliedAt: string;
  status: 'applied' | 'interviewing' | 'offered' | 'rejected' | 'withdrawn';
  notes?: string;
}

export interface SearchHistoryItem {
  id: string;
  keyword: string;
  location: string;
  timestamp: string;
  resultCount: number;
}

export interface SearchResponse {
  jobs: Job[];
  count: number;
  keyword: string;
  location: string;
}

export interface RankedSearchResponse {
  jobs: RankedJob[];
  count: number;
  keyword: string;
  location: string;
  profile_name: string;
  reasoning?: string | null;
}

export interface SearchFilters {
  keyword: string;
  location: string;
  jobType: string;
  remote: string;
  experience: string;
  datePosted: string;
  salary: string;
  sortBy: string;
  easyApply: boolean;
  under10Applicants: boolean;
  companySize: string;
  limit: number;
  details: boolean;
  sources: JobSource[];
}

export interface MultiSourceSearchResponse {
  jobs: Job[];
  count: number;
  keyword: string;
  location: string;
  sources: string[];
  jobs_by_source: Record<string, number>;
}

export interface JobSourceInfo {
  id: string;
  name: string;
  description: string;
  features: string[];
  companies?: string[];
}

export interface UserProfile {
  name: string;
  email: string;
  phone: string;
  location: string;
  linkedin_url: string;
  github_url: string;
  portfolio_url: string;
  title: string;
  summary: string;
  years_experience: number;
  skills: string[];
  programming_languages: string[];
  frameworks: string[];
  tools: string[];
  experience: WorkExperience[];
  education: Education[];
  certifications: string[];
  projects: Project[];
  target_roles: string[];
  target_companies: string[];
  preferred_locations: string[];
  remote_preference: string;
  min_salary: number;
}

export interface WorkExperience {
  title: string;
  company: string;
  location: string;
  duration: string;
  description: string;
  highlights: string[];
}

export interface Education {
  degree: string;
  school: string;
  year: string;
}

export interface Project {
  name: string;
  description: string;
  technologies: string[];
}

export interface TailoredResume {
  summary: string;
  highlighted_skills: string[];
  keywords_added: string[];
  resume_text: string;
  resume_html: string;
  ats_score: number;
  suggestions: string[];
}

export interface CoverLetter {
  content: string;
  html_content: string;
  word_count: number;
  key_points: string[];
  personalization_score: number;
}

export interface RecruiterFeedback {
  application_id: string;
  resume_score: number;
  cover_letter_score: number;
  decision: string;
  impression: string;
  strengths: string[];
  weaknesses: string[];
}

export interface EvaluationMetrics {
  total_applications: number;
  avg_match_score: number;
  avg_ats_score: number;
  avg_personalization_score: number;
  interview_rate: number;
  maybe_rate: number;
  rejection_rate: number;
  skill_coverage: number;
  recruiter_feedback: RecruiterFeedback[];
}

export interface OfflineAgentResult {
  reasoning?: string | null;
  ranked_jobs: RankedJob[];
  chosen_index: number;
  tailored_resume: TailoredResume;
}
