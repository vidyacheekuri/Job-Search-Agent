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
}

export interface SearchResponse {
  jobs: Job[];
  count: number;
  keyword: string;
  location: string;
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
  limit: number;
  details: boolean;
}
