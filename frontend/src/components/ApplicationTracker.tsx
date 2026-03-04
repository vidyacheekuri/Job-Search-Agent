import React, { useState } from 'react';
import type { AppliedJob } from '../types/job';

interface ApplicationTrackerProps {
  applications: AppliedJob[];
  onUpdateStatus: (jobUrl: string, status: AppliedJob['status']) => void;
  onUpdateNotes: (jobUrl: string, notes: string) => void;
  onRemove: (jobUrl: string) => void;
}

const statusConfig: Record<AppliedJob['status'], { label: string; color: string; bgColor: string }> = {
  applied: { label: 'Applied', color: 'text-teal-700 dark:text-teal-400', bgColor: 'bg-teal-100 dark:bg-teal-900/30' },
  interviewing: { label: 'Interviewing', color: 'text-yellow-700 dark:text-yellow-400', bgColor: 'bg-yellow-100 dark:bg-yellow-900/30' },
  offered: { label: 'Offered', color: 'text-green-700 dark:text-green-400', bgColor: 'bg-green-100 dark:bg-green-900/30' },
  rejected: { label: 'Rejected', color: 'text-red-700 dark:text-red-400', bgColor: 'bg-red-100 dark:bg-red-900/30' },
  withdrawn: { label: 'Withdrawn', color: 'text-gray-700 dark:text-gray-400', bgColor: 'bg-gray-100 dark:bg-gray-700' },
};

export const ApplicationTracker: React.FC<ApplicationTrackerProps> = ({ 
  applications, 
  onUpdateStatus, 
  onUpdateNotes, 
  onRemove 
}) => {
  const [editingNotes, setEditingNotes] = useState<string | null>(null);
  const [noteText, setNoteText] = useState('');
  const [filter, setFilter] = useState<AppliedJob['status'] | 'all'>('all');

  const filteredApps = filter === 'all' ? applications : applications.filter(app => app.status === filter);

  const stats = {
    total: applications.length,
    applied: applications.filter(a => a.status === 'applied').length,
    interviewing: applications.filter(a => a.status === 'interviewing').length,
    offered: applications.filter(a => a.status === 'offered').length,
    rejected: applications.filter(a => a.status === 'rejected').length,
  };

  if (applications.length === 0) {
    return (
      <div className="text-center py-12">
        <svg className="w-16 h-16 mx-auto text-gray-300 dark:text-gray-600 mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-3 7h3m-3 4h3m-6-4h.01M9 16h.01" />
        </svg>
        <h3 className="text-lg font-medium text-gray-700 dark:text-gray-300 mb-2">No applications tracked yet</h3>
        <p className="text-gray-500 dark:text-gray-400">Click "Mark as Applied" on any job to start tracking</p>
      </div>
    );
  }

  return (
    <div>
      <div className="grid grid-cols-2 sm:grid-cols-5 gap-3 mb-6">
        <div className="bg-white dark:bg-gray-800 rounded-lg p-3 border border-gray-200 dark:border-gray-700 text-center">
          <p className="text-2xl font-bold text-gray-900 dark:text-white">{stats.total}</p>
          <p className="text-xs text-gray-500 dark:text-gray-400">Total</p>
        </div>
        <div className="bg-teal-50 dark:bg-teal-900/20 rounded-lg p-3 border border-teal-200 dark:border-teal-800 text-center">
          <p className="text-2xl font-bold text-teal-700 dark:text-teal-400">{stats.applied}</p>
          <p className="text-xs text-teal-600 dark:text-teal-400">Applied</p>
        </div>
        <div className="bg-yellow-50 dark:bg-yellow-900/20 rounded-lg p-3 border border-yellow-200 dark:border-yellow-800 text-center">
          <p className="text-2xl font-bold text-yellow-700 dark:text-yellow-400">{stats.interviewing}</p>
          <p className="text-xs text-yellow-600 dark:text-yellow-400">Interviewing</p>
        </div>
        <div className="bg-green-50 dark:bg-green-900/20 rounded-lg p-3 border border-green-200 dark:border-green-800 text-center">
          <p className="text-2xl font-bold text-green-700 dark:text-green-400">{stats.offered}</p>
          <p className="text-xs text-green-600 dark:text-green-400">Offered</p>
        </div>
        <div className="bg-red-50 dark:bg-red-900/20 rounded-lg p-3 border border-red-200 dark:border-red-800 text-center">
          <p className="text-2xl font-bold text-red-700 dark:text-red-400">{stats.rejected}</p>
          <p className="text-xs text-red-600 dark:text-red-400">Rejected</p>
        </div>
      </div>

      <div className="flex gap-2 mb-4 overflow-x-auto pb-2">
        {(['all', 'applied', 'interviewing', 'offered', 'rejected', 'withdrawn'] as const).map((status) => (
          <button
            key={status}
            onClick={() => setFilter(status)}
            className={`px-3 py-1.5 rounded-full text-sm font-medium whitespace-nowrap transition-colors ${
              filter === status
                ? 'bg-teal-600 text-white'
                : 'bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-600'
            }`}
          >
            {status === 'all' ? 'All' : statusConfig[status].label}
          </button>
        ))}
      </div>

      <div className="space-y-4">
        {filteredApps.map((app) => (
          <div key={app.job_url} className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-4">
            <div className="flex items-start justify-between gap-4">
              <div className="flex gap-3 min-w-0">
                {app.company_logo ? (
                  <img src={app.company_logo} alt={app.company} className="w-12 h-12 rounded-lg object-cover flex-shrink-0" />
                ) : (
                  <div className="w-12 h-12 rounded-lg bg-gradient-to-br from-teal-500 to-cyan-600 flex items-center justify-center text-white font-bold text-lg flex-shrink-0">
                    {app.company.charAt(0)}
                  </div>
                )}
                <div className="min-w-0">
                  <a href={app.job_url} target="_blank" rel="noopener noreferrer" className="font-semibold text-gray-900 dark:text-white hover:text-teal-600 dark:hover:text-teal-400 transition-colors line-clamp-1">
                    {app.position}
                  </a>
                  <p className="text-sm text-gray-600 dark:text-gray-400 line-clamp-1">{app.company} • {app.location}</p>
                  <p className="text-xs text-gray-500 dark:text-gray-500 mt-1">
                    Applied {new Date(app.appliedAt).toLocaleDateString()}
                  </p>
                </div>
              </div>
              <div className="flex items-center gap-2 flex-shrink-0">
                <select
                  value={app.status}
                  onChange={(e) => onUpdateStatus(app.job_url, e.target.value as AppliedJob['status'])}
                  className={`px-3 py-1.5 rounded-full text-sm font-medium border-0 cursor-pointer ${statusConfig[app.status].bgColor} ${statusConfig[app.status].color}`}
                >
                  {Object.entries(statusConfig).map(([value, config]) => (
                    <option key={value} value={value}>{config.label}</option>
                  ))}
                </select>
                <button
                  onClick={() => onRemove(app.job_url)}
                  className="text-gray-400 hover:text-red-500 transition-colors p-1"
                >
                  <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                  </svg>
                </button>
              </div>
            </div>
            
            {editingNotes === app.job_url ? (
              <div className="mt-3">
                <textarea
                  value={noteText}
                  onChange={(e) => setNoteText(e.target.value)}
                  placeholder="Add interview notes, contacts, follow-up dates..."
                  className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white text-sm resize-none focus:ring-2 focus:ring-teal-500"
                  rows={3}
                />
                <div className="flex gap-2 mt-2">
                  <button
                    onClick={() => {
                      onUpdateNotes(app.job_url, noteText);
                      setEditingNotes(null);
                    }}
                    className="px-3 py-1 bg-teal-600 text-white rounded-lg text-sm hover:bg-teal-700 font-medium transition-colors"
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
                {app.notes && (
                  <p className="text-sm text-gray-600 dark:text-gray-400 bg-gray-50 dark:bg-gray-700/50 rounded-lg p-2 mb-2">
                    {app.notes}
                  </p>
                )}
                <button
                  onClick={() => {
                    setEditingNotes(app.job_url);
                    setNoteText(app.notes || '');
                  }}
                  className="text-xs text-teal-600 dark:text-teal-400 hover:underline"
                >
                  {app.notes ? 'Edit notes' : 'Add notes'}
                </button>
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
};
