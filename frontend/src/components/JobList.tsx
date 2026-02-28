import type { Job } from '../types/job';
import { JobCard } from './JobCard';

interface JobListProps {
  jobs: Job[];
  keyword: string;
  location: string;
}

export function JobList({ jobs, keyword, location }: JobListProps) {
  if (jobs.length === 0) {
    return (
      <div className="text-center py-16">
        <div className="w-14 h-14 mx-auto mb-4 bg-gray-100 rounded-full flex items-center justify-center">
          <svg className="w-7 h-7 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9.172 16.172a4 4 0 015.656 0M9 10h.01M15 10h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
        </div>
        <h3 className="text-base font-medium text-gray-900 mb-1">No jobs found</h3>
        <p className="text-sm text-gray-500">Try different keywords or adjust your filters</p>
      </div>
    );
  }

  return (
    <div>
      {/* Results Header */}
      <div className="flex items-center justify-between mb-4">
        <p className="text-sm text-gray-600">
          <span className="font-medium text-gray-900">{jobs.length}</span> jobs found
          {keyword && <span> for <span className="font-medium">"{keyword}"</span></span>}
          {location && <span> in <span className="font-medium">{location}</span></span>}
        </p>
      </div>

      {/* Job Cards */}
      <div className="space-y-3">
        {jobs.map((job, index) => (
          <JobCard key={`${job.job_url}-${index}`} job={job} />
        ))}
      </div>
    </div>
  );
}
