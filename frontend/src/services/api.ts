import type { 
  SearchFilters, 
  SearchResponse, 
  RankedSearchResponse,
  UserProfile,
  TailoredResume,
  CoverLetter,
  EvaluationMetrics,
  BiasAnalysis,
  MultiSourceSearchResponse,
  JobSourceInfo,
} from '../types/job';

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
  if (filters.sortBy) params.append('sort_by', filters.sortBy);
  if (filters.easyApply) params.append('easy_apply', 'true');
  if (filters.under10Applicants) params.append('under_10_applicants', 'true');
  if (filters.companySize) params.append('company_size', filters.companySize);
  params.append('limit', filters.limit.toString());
  if (filters.details) params.append('details', 'true');

  const response = await fetch(`${API_BASE}/api/search?${params}`);
  
  if (!response.ok) {
    throw new Error(`Search failed: ${response.statusText}`);
  }
  
  return response.json();
}

export async function searchJobsMultiSource(filters: SearchFilters): Promise<MultiSourceSearchResponse> {
  const params = new URLSearchParams();
  
  params.append('keyword', filters.keyword);
  if (filters.location) params.append('location', filters.location);
  if (filters.sources && filters.sources.length > 0) {
    params.append('sources', filters.sources.join(','));
  }
  if (filters.jobType) params.append('job_type', filters.jobType);
  if (filters.remote) params.append('remote', filters.remote);
  if (filters.experience) params.append('experience', filters.experience);
  if (filters.datePosted) params.append('date_posted', filters.datePosted);
  if (filters.salary) params.append('salary', filters.salary);
  if (filters.sortBy) params.append('sort_by', filters.sortBy);
  if (filters.easyApply) params.append('easy_apply', 'true');
  if (filters.companySize) params.append('company_size', filters.companySize);
  params.append('limit', filters.limit.toString());
  if (filters.details) params.append('details', 'true');

  const response = await fetch(`${API_BASE}/api/search/multi?${params}`);
  
  if (!response.ok) {
    throw new Error(`Multi-source search failed: ${response.statusText}`);
  }
  
  return response.json();
}

export async function getAvailableSources(): Promise<{ sources: JobSourceInfo[] }> {
  const response = await fetch(`${API_BASE}/api/sources`);
  
  if (!response.ok) {
    throw new Error(`Failed to get sources: ${response.statusText}`);
  }
  
  return response.json();
}

export async function getGreenhouseCompanies(): Promise<{ companies: string[]; count: number }> {
  const response = await fetch(`${API_BASE}/api/sources/greenhouse/companies`);
  
  if (!response.ok) {
    throw new Error(`Failed to get Greenhouse companies: ${response.statusText}`);
  }
  
  return response.json();
}

export async function createProfile(profile: UserProfile): Promise<{ profile_id: string; profile: UserProfile }> {
  const response = await fetch(`${API_BASE}/api/profile`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(profile),
  });
  
  if (!response.ok) {
    throw new Error(`Failed to create profile: ${response.statusText}`);
  }
  
  return response.json();
}

export async function parseResume(resumeText: string): Promise<{ profile_id: string; profile: UserProfile }> {
  const formData = new FormData();
  formData.append('resume_text', resumeText);
  
  const response = await fetch(`${API_BASE}/api/profile/parse`, {
    method: 'POST',
    body: formData,
  });
  
  if (!response.ok) {
    throw new Error(`Failed to parse resume: ${response.statusText}`);
  }
  
  return response.json();
}

export async function uploadPdfResume(file: File): Promise<{ profile_id: string; profile: UserProfile }> {
  const formData = new FormData();
  formData.append('file', file);
  
  const response = await fetch(`${API_BASE}/api/profile/upload-pdf`, {
    method: 'POST',
    body: formData,
  });
  
  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: response.statusText }));
    throw new Error(error.detail || `Failed to upload PDF: ${response.statusText}`);
  }
  
  return response.json();
}

export async function getProfile(profileId: string): Promise<UserProfile> {
  const response = await fetch(`${API_BASE}/api/profile/${profileId}`);
  
  if (!response.ok) {
    throw new Error(`Profile not found: ${response.statusText}`);
  }
  
  return response.json();
}

export async function searchAndRankJobs(
  keyword: string,
  location: string,
  profileId: string,
  companySize: string = 'mid',
  limit: number = 25,
  topN: number = 10,
): Promise<RankedSearchResponse> {
  const params = new URLSearchParams({
    keyword,
    location,
    profile_id: profileId,
    company_size: companySize,
    limit: limit.toString(),
    top_n: topN.toString(),
  });
  
  const response = await fetch(`${API_BASE}/api/search/ranked?${params}`, {
    method: 'POST',
  });
  
  if (!response.ok) {
    throw new Error(`Ranked search failed: ${response.statusText}`);
  }
  
  return response.json();
}

export async function tailorResume(
  profileId: string,
  jobUrl: string,
  useOpenAI: boolean = false,
): Promise<TailoredResume> {
  const params = new URLSearchParams({
    profile_id: profileId,
    job_url: jobUrl,
    use_openai: useOpenAI.toString(),
  });
  
  const response = await fetch(`${API_BASE}/api/tailor/resume?${params}`, {
    method: 'POST',
  });
  
  if (!response.ok) {
    throw new Error(`Resume tailoring failed: ${response.statusText}`);
  }
  
  return response.json();
}

export async function generateCoverLetter(
  profileId: string,
  jobUrl: string,
  useOpenAI: boolean = false,
): Promise<CoverLetter> {
  const params = new URLSearchParams({
    profile_id: profileId,
    job_url: jobUrl,
    use_openai: useOpenAI.toString(),
  });
  
  const response = await fetch(`${API_BASE}/api/generate/cover-letter?${params}`, {
    method: 'POST',
  });
  
  if (!response.ok) {
    throw new Error(`Cover letter generation failed: ${response.statusText}`);
  }
  
  return response.json();
}

export async function runAgentPipeline(
  profileId: string,
  keyword: string = 'AI Engineer',
  location: string = '',
  companySize: string = 'mid',
  limit: number = 50,
  topN: number = 5,
  useOpenAI: boolean = false,
): Promise<{ report: any; applications: any[] }> {
  const params = new URLSearchParams({
    profile_id: profileId,
    keyword,
    location,
    company_size: companySize,
    limit: limit.toString(),
    top_n: topN.toString(),
    use_openai: useOpenAI.toString(),
  });
  
  const response = await fetch(`${API_BASE}/api/agent/run?${params}`, {
    method: 'POST',
  });
  
  if (!response.ok) {
    throw new Error(`Agent pipeline failed: ${response.statusText}`);
  }
  
  return response.json();
}

export async function evaluateApplications(
  profileId: string,
  keyword: string = 'AI Engineer',
  numApplications: number = 5,
): Promise<EvaluationMetrics> {
  const params = new URLSearchParams({
    profile_id: profileId,
    keyword,
    num_applications: numApplications.toString(),
  });
  
  const response = await fetch(`${API_BASE}/api/evaluate?${params}`, {
    method: 'POST',
  });
  
  if (!response.ok) {
    throw new Error(`Evaluation failed: ${response.statusText}`);
  }
  
  return response.json();
}

export async function analyzeBias(
  profileId: string,
  keyword: string = 'AI Engineer',
  limit: number = 30,
): Promise<BiasAnalysis> {
  const params = new URLSearchParams({
    profile_id: profileId,
    keyword,
    limit: limit.toString(),
  });
  
  const response = await fetch(`${API_BASE}/api/analyze/bias?${params}`, {
    method: 'POST',
  });
  
  if (!response.ok) {
    throw new Error(`Bias analysis failed: ${response.statusText}`);
  }
  
  return response.json();
}
