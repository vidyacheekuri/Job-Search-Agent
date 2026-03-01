import React, { useState } from 'react';
import type { SavedJob } from '../types/job';

interface SavedJobsProps {
  savedJobs: SavedJob[];
  onRemove: (jobUrl: string) => void;
  onUpdateNotes: (jobUrl: string, notes: string) => void;
}

export const SavedJobs: React.FC<SavedJobsProps> = ({ savedJobs, onRemove, onUpdateNotes }) => {
  const [editingNotes, setEditingNotes] = useState<string | null>(null);
  const [noteText, setNoteText] = useState('');

  if (savedJobs.length === 0) {
    return (
      <div className="text-center py-12">
        <svg className="w-16 h-16 mx-auto text-gray-300 dark:text-gray-600 mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M5 5a2 2 0 012-2h10a2 2 0 012 2v16l-7-3.5L5 21V5z" />
        </svg>
        <h3 className="text-lg font-medium text-gray-700 dark:text-gray-300 mb-2">No saved jobs yet</h3>
        <p className="text-gray-500 dark:text-gray-400">Click the bookmark icon on any job to save it here</p>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {savedJobs.map((job) => (
        <div key={job.job_url} className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-4">
          <div className="flex items-start justify-between">
            <div className="flex gap-3">
              {job.company_logo ? (
                <img src={job.company_logo} alt={job.company} className="w-12 h-12 rounded-lg object-cover" />
              ) : (
                <div className="w-12 h-12 rounded-lg bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center text-white font-bold text-lg">
                  {job.company.charAt(0)}
                </div>
              )}
              <div>
                <a href={job.job_url} target="_blank" rel="noopener noreferrer" className="font-semibold text-gray-900 dark:text-white hover:text-blue-600 dark:hover:text-blue-400 transition-colors">
                  {job.position}
                </a>
                <p className="text-sm text-gray-600 dark:text-gray-400">{job.company} • {job.location}</p>
                <p className="text-xs text-gray-500 dark:text-gray-500 mt-1">
                  Saved {new Date(job.savedAt).toLocaleDateString()}
                </p>
              </div>
            </div>
            <button
              onClick={() => onRemove(job.job_url)}
              className="text-gray-400 hover:text-red-500 transition-colors"
            >
              <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
              </svg>
            </button>
          </div>
          
          {editingNotes === job.job_url ? (
            <div className="mt-3">
              <textarea
                value={noteText}
                onChange={(e) => setNoteText(e.target.value)}
                placeholder="Add notes about this job..."
                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white text-sm resize-none focus:ring-2 focus:ring-blue-500"
                rows={2}
              />
              <div className="flex gap-2 mt-2">
                <button
                  onClick={() => {
                    onUpdateNotes(job.job_url, noteText);
                    setEditingNotes(null);
                  }}
                  className="px-3 py-1 bg-blue-600 text-white rounded text-sm hover:bg-blue-700 transition-colors"
                >
                  Save
                </button>
                <button
                  onClick={() => setEditingNotes(null)}
                  className="px-3 py-1 text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white text-sm transition-colors"
                >
                  Cancel
                </button>
              </div>
            </div>
          ) : (
            <div className="mt-3">
              {job.notes ? (
                <p className="text-sm text-gray-600 dark:text-gray-400 bg-gray-50 dark:bg-gray-700/50 rounded-lg p-2">
                  {job.notes}
                </p>
              ) : null}
              <button
                onClick={() => {
                  setEditingNotes(job.job_url);
                  setNoteText(job.notes || '');
                }}
                className="text-xs text-blue-600 dark:text-blue-400 hover:underline mt-2"
              >
                {job.notes ? 'Edit notes' : 'Add notes'}
              </button>
            </div>
          )}
        </div>
      ))}
    </div>
  );
};
