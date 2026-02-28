import type { Job } from '../types/job';

interface JobCardProps {
  job: Job;
}

export function JobCard({ job }: JobCardProps) {
  return (
    <div className="bg-white rounded-lg border border-gray-200 p-4 hover:border-gray-300 hover:shadow-sm transition-all">
      <div className="flex gap-4">
        {/* Company Logo */}
        <div className="flex-shrink-0">
          {job.company_logo ? (
            <img
              src={job.company_logo}
              alt=""
              className="w-12 h-12 rounded-lg object-cover bg-gray-100"
              onError={(e) => {
                (e.target as HTMLImageElement).style.display = 'none';
                (e.target as HTMLImageElement).nextElementSibling?.classList.remove('hidden');
              }}
            />
          ) : null}
          <div className={`w-12 h-12 rounded-lg bg-gradient-to-br from-blue-500 to-blue-600 flex items-center justify-center text-white font-semibold text-lg ${job.company_logo ? 'hidden' : ''}`}>
            {job.company.charAt(0)}
          </div>
        </div>

        {/* Job Info */}
        <div className="flex-1 min-w-0">
          <h3 className="font-semibold text-gray-900 truncate">{job.position}</h3>
          <p className="text-blue-600 text-sm font-medium">{job.company}</p>
          
          <div className="flex flex-wrap items-center gap-x-3 gap-y-1 mt-2 text-sm text-gray-500">
            <span className="flex items-center gap-1">
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
              </svg>
              {job.location}
            </span>
            
            {job.ago_time && (
              <span className="flex items-center gap-1">
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                {job.ago_time}
              </span>
            )}
            
            {job.salary && (
              <span className="text-green-600 font-medium">{job.salary}</span>
            )}
          </div>

          {job.applicant_count && (
            <p className="text-xs text-gray-400 mt-1">{job.applicant_count}</p>
          )}
        </div>

        {/* Action */}
        <div className="flex-shrink-0">
          <a
            href={job.job_url}
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex items-center gap-1 px-4 py-2 text-sm font-medium text-blue-600 bg-blue-50 rounded-lg hover:bg-blue-100 transition-colors"
          >
            Apply
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
            </svg>
          </a>
        </div>
      </div>

      {/* Description Preview */}
      {job.description && (
        <p className="text-sm text-gray-600 mt-3 line-clamp-2 pl-16">
          {job.description}
        </p>
      )}
    </div>
  );
}
