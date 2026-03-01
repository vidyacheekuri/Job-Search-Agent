import React, { useState } from 'react';
import type { RankedJob } from '../types/job';

interface RankedJobCardProps {
  rankedJob: RankedJob;
  onGenerateResume?: (jobUrl: string) => void;
  onGenerateCoverLetter?: (jobUrl: string) => void;
  isGenerating?: boolean;
}

export const RankedJobCard: React.FC<RankedJobCardProps> = ({ 
  rankedJob, 
  onGenerateResume, 
  onGenerateCoverLetter,
  isGenerating 
}) => {
  const [showDetails, setShowDetails] = useState(false);
  const { job, score, skill_match, title_match, location_match, matched_skills, missing_skills, match_reasons } = rankedJob;

  const getScoreColor = (s: number) => {
    if (s >= 70) return 'text-green-600 dark:text-green-400';
    if (s >= 50) return 'text-yellow-600 dark:text-yellow-400';
    return 'text-red-600 dark:text-red-400';
  };

  const getScoreBg = (s: number) => {
    if (s >= 70) return 'bg-green-100 dark:bg-green-900/30';
    if (s >= 50) return 'bg-yellow-100 dark:bg-yellow-900/30';
    return 'bg-red-100 dark:bg-red-900/30';
  };

  return (
    <div className="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 p-5 hover:shadow-lg transition-all">
      <div className="flex items-start gap-4">
        {/* Score Badge */}
        <div className={`flex-shrink-0 w-16 h-16 rounded-xl ${getScoreBg(score)} flex flex-col items-center justify-center`}>
          <span className={`text-2xl font-bold ${getScoreColor(score)}`}>{Math.round(score)}</span>
          <span className="text-xs text-gray-500 dark:text-gray-400">match</span>
        </div>

        {/* Job Info */}
        <div className="flex-1 min-w-0">
          <h3 className="font-semibold text-gray-900 dark:text-white text-lg leading-tight">
            {job.position}
          </h3>
          <p className="text-blue-600 dark:text-blue-400 text-sm font-medium">
            {job.company}
          </p>
          <div className="flex flex-wrap items-center gap-2 mt-2 text-sm text-gray-500 dark:text-gray-400">
            <span>{job.location}</span>
            {job.salary && (
              <>
                <span>•</span>
                <span className="text-green-600 dark:text-green-400 font-medium">{job.salary}</span>
              </>
            )}
            {job.ago_time && (
              <>
                <span>•</span>
                <span>{job.ago_time}</span>
              </>
            )}
          </div>
        </div>
      </div>

      {/* Match Reasons */}
      {match_reasons.length > 0 && (
        <div className="mt-4 flex flex-wrap gap-2">
          {match_reasons.map((reason, i) => (
            <span key={i} className="px-2 py-1 bg-blue-50 dark:bg-blue-900/20 text-blue-700 dark:text-blue-300 text-xs rounded-full">
              {reason}
            </span>
          ))}
        </div>
      )}

      {/* Score Breakdown */}
      <button
        onClick={() => setShowDetails(!showDetails)}
        className="mt-4 text-sm text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300 flex items-center gap-1"
      >
        {showDetails ? 'Hide' : 'Show'} score breakdown
        <svg className={`w-4 h-4 transition-transform ${showDetails ? 'rotate-180' : ''}`} fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
        </svg>
      </button>

      {showDetails && (
        <div className="mt-4 p-4 bg-gray-50 dark:bg-gray-700/50 rounded-lg">
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 mb-4">
            <div>
              <p className="text-xs text-gray-500 dark:text-gray-400">Skills</p>
              <p className={`text-lg font-semibold ${getScoreColor(skill_match)}`}>{skill_match}%</p>
            </div>
            <div>
              <p className="text-xs text-gray-500 dark:text-gray-400">Title</p>
              <p className={`text-lg font-semibold ${getScoreColor(title_match)}`}>{title_match}%</p>
            </div>
            <div>
              <p className="text-xs text-gray-500 dark:text-gray-400">Location</p>
              <p className={`text-lg font-semibold ${getScoreColor(location_match)}`}>{location_match}%</p>
            </div>
            <div>
              <p className="text-xs text-gray-500 dark:text-gray-400">Overall</p>
              <p className={`text-lg font-semibold ${getScoreColor(score)}`}>{score}%</p>
            </div>
          </div>

          {matched_skills.length > 0 && (
            <div className="mb-3">
              <p className="text-xs font-medium text-gray-500 dark:text-gray-400 mb-1">Matched Skills:</p>
              <div className="flex flex-wrap gap-1">
                {matched_skills.map((skill, i) => (
                  <span key={i} className="px-2 py-0.5 bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-300 text-xs rounded">
                    {skill}
                  </span>
                ))}
              </div>
            </div>
          )}

          {missing_skills.length > 0 && (
            <div>
              <p className="text-xs font-medium text-gray-500 dark:text-gray-400 mb-1">Skills to Learn:</p>
              <div className="flex flex-wrap gap-1">
                {missing_skills.map((skill, i) => (
                  <span key={i} className="px-2 py-0.5 bg-orange-100 dark:bg-orange-900/30 text-orange-700 dark:text-orange-300 text-xs rounded">
                    {skill}
                  </span>
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      {/* Actions */}
      <div className="mt-4 pt-4 border-t border-gray-100 dark:border-gray-700 flex flex-wrap gap-2">
        <button
          onClick={() => onGenerateResume?.(job.job_url)}
          disabled={isGenerating}
          className="px-4 py-2 bg-purple-600 text-white text-sm font-medium rounded-lg hover:bg-purple-700 disabled:bg-gray-300 dark:disabled:bg-gray-600 transition-colors"
        >
          Generate Resume
        </button>
        <button
          onClick={() => onGenerateCoverLetter?.(job.job_url)}
          disabled={isGenerating}
          className="px-4 py-2 bg-indigo-600 text-white text-sm font-medium rounded-lg hover:bg-indigo-700 disabled:bg-gray-300 dark:disabled:bg-gray-600 transition-colors"
        >
          Generate Cover Letter
        </button>
        <a
          href={job.job_url}
          target="_blank"
          rel="noopener noreferrer"
          className="px-4 py-2 bg-blue-600 text-white text-sm font-medium rounded-lg hover:bg-blue-700 transition-colors"
        >
          View Job
        </a>
      </div>
    </div>
  );
};
