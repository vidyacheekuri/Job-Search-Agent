import type { SearchFilters, SearchResponse } from '../types/job';

const API_BASE = 'http://localhost:8000';

export async function searchJobs(filters: SearchFilters): Promise<SearchResponse> {
  const params = new URLSearchParams();
  
  params.append('keyword', filters.keyword);
  if (filters.location) params.append('location', filters.location);
  if (filters.jobType) params.append('job_type', filters.jobType);
  if (filters.remote) params.append('remote', filters.remote);
  if (filters.experience) params.append('experience', filters.experience);
  if (filters.datePosted) params.append('date_posted', filters.datePosted);
  if (filters.salary) params.append('salary', filters.salary);
  params.append('sort_by', filters.sortBy);
  params.append('easy_apply', String(filters.easyApply));
  params.append('under_10_applicants', String(filters.under10Applicants));
  params.append('limit', String(filters.limit));
  params.append('details', String(filters.details));

  const response = await fetch(`${API_BASE}/api/search?${params.toString()}`);
  
  if (!response.ok) {
    throw new Error(`Search failed: ${response.statusText}`);
  }
  
  return response.json();
}
