import React from 'react';
import type { Job, SavedJob, AppliedJob } from '../types/job';
import { JobCard } from './JobCard';
import { Pagination } from './Pagination';

interface JobListProps {
  jobs: Job[];
  keyword: string;
  location: string;
  savedJobs: SavedJob[];
  appliedJobs: AppliedJob[];
  onSaveJob: (job: Job) => void;
  onUnsaveJob: (jobUrl: string) => void;
  onMarkApplied: (job: Job) => void;
  onShowCompanyInfo: (company: string) => void;
  currentPage: number;
  totalPages: number;
  onPageChange: (page: number) => void;
  loading?: boolean;
}

export const JobList: React.FC<JobListProps> = ({ 
  jobs, 
  keyword, 
  location,
  savedJobs,
  appliedJobs,
  onSaveJob,
  onUnsaveJob,
  onMarkApplied,
  onShowCompanyInfo,
  currentPage,
  totalPages,
  onPageChange,
  loading
}) => {
  const savedJobUrls = new Set(savedJobs.map(j => j.job_url));
  const appliedJobUrls = new Set(appliedJobs.map(j => j.job_url));

  if (jobs.length === 0) {
    return (
      <div className="text-center py-16">
        <div className="w-16 h-16 mx-auto mb-4 bg-gray-100 dark:bg-gray-700 rounded-full flex items-center justify-center">
          <svg className="w-8 h-8 text-gray-400 dark:text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9.172 16.172a4 4 0 015.656 0M9 10h.01M15 10h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
        </div>
        <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-1">No jobs found</h3>
        <p className="text-sm text-gray-500 dark:text-gray-400">Try different keywords or adjust your filters</p>
      </div>
    );
  }

  return (
    <div>
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 mb-4">
        <p className="text-sm text-gray-600 dark:text-gray-400">
          <span className="font-semibold text-gray-900 dark:text-white">{jobs.length}</span> jobs found
          {keyword && <span> for <span className="font-medium text-teal-600 dark:text-teal-400">"{keyword}"</span></span>}
          {location && <span> in <span className="font-medium">{location}</span></span>}
        </p>
        {totalPages > 1 && (
          <p className="text-xs text-gray-500 dark:text-gray-500">
            Page {currentPage} of {totalPages}
          </p>
        )}
      </div>

      <div className="space-y-4">
        {jobs.map((job, index) => (
          <JobCard 
            key={`${job.job_url}-${index}`} 
            job={job}
            isSaved={savedJobUrls.has(job.job_url)}
            isApplied={appliedJobUrls.has(job.job_url)}
            onSave={onSaveJob}
            onUnsave={onUnsaveJob}
            onMarkApplied={onMarkApplied}
            onShowCompanyInfo={onShowCompanyInfo}
          />
        ))}
      </div>

      <Pagination
        currentPage={currentPage}
        totalPages={totalPages}
        onPageChange={onPageChange}
        loading={loading}
      />
    </div>
  );
};
