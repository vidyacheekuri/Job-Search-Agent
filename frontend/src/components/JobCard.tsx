import { useState } from 'react';
import type { Job } from '../types/job';

interface JobCardProps {
  job: Job;
  isSaved?: boolean;
  isApplied?: boolean;
  onSave?: (job: Job) => void;
  onUnsave?: (jobUrl: string) => void;
  onMarkApplied?: (job: Job) => void;
  onShowCompanyInfo?: (company: string) => void;
}

const SOURCE_BADGES: Record<string, { label: string; color: string; icon: string }> = {
  linkedin: { label: 'LinkedIn', color: 'bg-teal-100 text-teal-700 dark:bg-teal-900/30 dark:text-teal-400', icon: '💼' },
  indeed: { label: 'Indeed', color: 'bg-cyan-100 text-cyan-700 dark:bg-cyan-900/30 dark:text-cyan-400', icon: '🔍' },
  greenhouse: { label: 'Greenhouse', color: 'bg-emerald-100 text-emerald-700 dark:bg-emerald-900/30 dark:text-emerald-400', icon: '🌱' },
};

const estimateSalary = (position: string, location: string): string | null => {
  const positionLower = position.toLowerCase();
  const locationLower = location.toLowerCase();
  
  let baseSalary = 70000;
  
  if (positionLower.includes('senior') || positionLower.includes('lead') || positionLower.includes('principal')) {
    baseSalary = 130000;
  } else if (positionLower.includes('manager') || positionLower.includes('director')) {
    baseSalary = 150000;
  } else if (positionLower.includes('junior') || positionLower.includes('entry') || positionLower.includes('intern')) {
    baseSalary = 55000;
  } else if (positionLower.includes('engineer') || positionLower.includes('developer')) {
    baseSalary = 100000;
  } else if (positionLower.includes('analyst')) {
    baseSalary = 75000;
  } else if (positionLower.includes('designer')) {
    baseSalary = 85000;
  }
  
  if (locationLower.includes('san francisco') || locationLower.includes('new york') || locationLower.includes('seattle')) {
    baseSalary = Math.round(baseSalary * 1.3);
  } else if (locationLower.includes('remote')) {
    baseSalary = Math.round(baseSalary * 1.1);
  } else if (locationLower.includes('austin') || locationLower.includes('denver') || locationLower.includes('boston')) {
    baseSalary = Math.round(baseSalary * 1.15);
  }
  
  const lowEnd = Math.round(baseSalary * 0.85 / 1000) * 1000;
  const highEnd = Math.round(baseSalary * 1.15 / 1000) * 1000;
  
  return `$${(lowEnd / 1000).toFixed(0)}K - $${(highEnd / 1000).toFixed(0)}K (est.)`;
};

export const JobCard: React.FC<JobCardProps> = ({ 
  job, 
  isSaved = false, 
  isApplied = false,
  onSave, 
  onUnsave, 
  onMarkApplied,
  onShowCompanyInfo 
}) => {
  const [showFullDescription, setShowFullDescription] = useState(false);
  
  const displaySalary = job.salary || estimateSalary(job.position, job.location);
  const isEstimatedSalary = !job.salary;

  return (
    <div className="bg-white dark:bg-gray-800/80 rounded-2xl border border-stone-200 dark:border-gray-700 p-4 sm:p-5 hover:border-teal-200 dark:hover:border-teal-800 hover:shadow-lg transition-all">
      <div className="flex flex-col sm:flex-row gap-4">
        {/* Company Logo */}
        <div className="flex-shrink-0 hidden sm:block">
          {job.company_logo ? (
            <img
              src={job.company_logo}
              alt={job.company}
              className="w-14 h-14 rounded-xl object-cover bg-gray-100 dark:bg-gray-700"
              onError={(e) => {
                (e.target as HTMLImageElement).style.display = 'none';
                (e.target as HTMLImageElement).nextElementSibling?.classList.remove('hidden');
              }}
            />
          ) : null}
          <div className={`w-14 h-14 rounded-xl bg-gradient-to-br from-teal-500 to-cyan-600 flex items-center justify-center text-white font-bold text-xl ${job.company_logo ? 'hidden' : ''}`}>
            {job.company.charAt(0)}
          </div>
        </div>

        {/* Job Info */}
        <div className="flex-1 min-w-0">
          <div className="flex items-start justify-between gap-2">
            <div className="min-w-0">
              <h3 className="font-semibold text-gray-900 dark:text-white text-lg leading-tight line-clamp-2">
                {job.position}
              </h3>
              <button
                onClick={() => onShowCompanyInfo?.(job.company)}
                className="text-teal-600 dark:text-teal-400 text-sm font-medium hover:underline text-left"
              >
                {job.company}
              </button>
            </div>
            
            {/* Mobile Logo */}
            <div className="sm:hidden flex-shrink-0">
              {job.company_logo ? (
                <img src={job.company_logo} alt="" className="w-10 h-10 rounded-lg object-cover" />
              ) : (
                <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-teal-500 to-cyan-600 flex items-center justify-center text-white font-bold">
                  {job.company.charAt(0)}
                </div>
              )}
            </div>
          </div>
          
          <div className="flex flex-wrap items-center gap-x-3 gap-y-1.5 mt-2.5 text-sm">
            {/* Source Badge */}
            {job.source && SOURCE_BADGES[job.source] && (
              <span className={`inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-medium ${SOURCE_BADGES[job.source].color}`}>
                <span>{SOURCE_BADGES[job.source].icon}</span>
                {SOURCE_BADGES[job.source].label}
              </span>
            )}
            
            <span className="flex items-center gap-1 text-gray-600 dark:text-gray-400">
              <svg className="w-4 h-4 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
              </svg>
              <span className="truncate">{job.location}</span>
            </span>
            
            {job.ago_time && (
              <span className="flex items-center gap-1 text-gray-500 dark:text-gray-500">
                <svg className="w-4 h-4 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                {job.ago_time}
              </span>
            )}
            
            {displaySalary && (
              <span className={`font-medium ${isEstimatedSalary ? 'text-gray-500 dark:text-gray-400 italic' : 'text-green-600 dark:text-green-400'}`}>
                {displaySalary}
              </span>
            )}
          </div>

          {job.applicant_count && (
            <p className="text-xs text-gray-400 dark:text-gray-500 mt-1.5">{job.applicant_count}</p>
          )}

          {job.skills && job.skills.length > 0 && (
            <div className="flex flex-wrap gap-1.5 mt-2.5">
              {job.skills.slice(0, 4).map((skill, i) => (
                <span key={i} className="px-2 py-0.5 bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-400 text-xs rounded-full">
                  {skill}
                </span>
              ))}
              {job.skills.length > 4 && (
                <span className="text-xs text-gray-400 dark:text-gray-500">+{job.skills.length - 4} more</span>
              )}
            </div>
          )}
        </div>
      </div>

      {/* Description Preview */}
      {job.description && (
        <div className="mt-3 sm:pl-[72px]">
          <p className={`text-sm text-gray-600 dark:text-gray-400 ${showFullDescription ? '' : 'line-clamp-2'}`}>
            {job.description}
          </p>
          {job.description.length > 150 && (
            <button
              onClick={() => setShowFullDescription(!showFullDescription)}
              className="text-xs text-teal-600 dark:text-teal-400 hover:underline mt-1"
            >
              {showFullDescription ? 'Show less' : 'Show more'}
            </button>
          )}
        </div>
      )}

      {/* Actions */}
      <div className="flex flex-wrap items-center justify-between gap-3 mt-4 pt-4 border-t border-gray-100 dark:border-gray-700 sm:pl-[72px]">
        <div className="flex items-center gap-2">
          <button
            onClick={() => isSaved ? onUnsave?.(job.job_url) : onSave?.(job)}
            className={`p-2 rounded-lg transition-colors ${
              isSaved 
                ? 'text-yellow-500 bg-yellow-50 dark:bg-yellow-900/20 hover:bg-yellow-100 dark:hover:bg-yellow-900/30' 
                : 'text-gray-400 hover:text-yellow-500 hover:bg-gray-100 dark:hover:bg-gray-700'
            }`}
            title={isSaved ? 'Remove from saved' : 'Save job'}
          >
            <svg className="w-5 h-5" fill={isSaved ? 'currentColor' : 'none'} viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 5a2 2 0 012-2h10a2 2 0 012 2v16l-7-3.5L5 21V5z" />
            </svg>
          </button>
          
          {!isApplied && (
            <button
              onClick={() => onMarkApplied?.(job)}
              className="px-3 py-1.5 text-sm text-gray-600 dark:text-gray-400 hover:text-teal-600 dark:hover:text-teal-400 hover:bg-teal-50 dark:hover:bg-teal-900/20 rounded-lg transition-colors"
            >
              Mark Applied
            </button>
          )}
          
          {isApplied && (
            <span className="px-3 py-1.5 text-sm text-green-600 dark:text-green-400 bg-green-50 dark:bg-green-900/20 rounded-lg">
              ✓ Applied
            </span>
          )}
        </div>
        
        <a
          href={job.job_url}
          target="_blank"
          rel="noopener noreferrer"
          className="inline-flex items-center gap-1.5 px-4 py-2 text-sm font-semibold text-white bg-teal-600 rounded-xl hover:bg-teal-700 transition-colors shadow-md shadow-teal-500/20"
        >
          View Job
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
          </svg>
        </a>
      </div>
    </div>
  );
};
