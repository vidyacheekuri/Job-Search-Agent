import { useState } from 'react';
import type { SearchFilters } from '../types/job';

interface SearchFormProps {
  onSearch: (filters: SearchFilters) => void;
  isLoading: boolean;
}

const defaultFilters: SearchFilters = {
  keyword: '',
  location: '',
  jobType: '',
  remote: '',
  experience: '',
  datePosted: '',
  salary: '',
  sortBy: 'relevant',
  easyApply: false,
  under10Applicants: false,
  limit: 25,
  details: false,
};

export function SearchForm({ onSearch, isLoading }: SearchFormProps) {
  const [filters, setFilters] = useState<SearchFilters>(defaultFilters);
  const [showFilters, setShowFilters] = useState(false);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (filters.keyword.trim()) {
      onSearch(filters);
    }
  };

  const updateFilter = <K extends keyof SearchFilters>(key: K, value: SearchFilters[K]) => {
    setFilters((prev) => ({ ...prev, [key]: value }));
  };

  const activeFilterCount = [
    filters.jobType,
    filters.remote,
    filters.experience,
    filters.datePosted,
    filters.salary,
    filters.easyApply,
    filters.under10Applicants,
  ].filter(Boolean).length;

  return (
    <form onSubmit={handleSubmit} className="mb-6">
      {/* Main Search Bar */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-4">
        <div className="flex flex-col sm:flex-row gap-3">
          <div className="flex-1 relative">
            <svg className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
            </svg>
            <input
              type="text"
              value={filters.keyword}
              onChange={(e) => updateFilter('keyword', e.target.value)}
              placeholder="Job title or keywords"
              className="w-full pl-10 pr-4 py-2.5 bg-gray-50 border border-gray-200 rounded-lg focus:bg-white focus:border-blue-500 focus:ring-2 focus:ring-blue-100 transition-all"
            />
          </div>
          
          <div className="flex-1 relative">
            <svg className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
            </svg>
            <input
              type="text"
              value={filters.location}
              onChange={(e) => updateFilter('location', e.target.value)}
              placeholder="Location"
              className="w-full pl-10 pr-4 py-2.5 bg-gray-50 border border-gray-200 rounded-lg focus:bg-white focus:border-blue-500 focus:ring-2 focus:ring-blue-100 transition-all"
            />
          </div>

          <button
            type="submit"
            disabled={isLoading || !filters.keyword.trim()}
            className="px-6 py-2.5 bg-blue-600 text-white font-medium rounded-lg hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors flex items-center justify-center gap-2"
          >
            {isLoading ? (
              <>
                <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                <span>Searching</span>
              </>
            ) : (
              'Search'
            )}
          </button>
        </div>

        {/* Filter Toggle */}
        <div className="mt-3 pt-3 border-t border-gray-100 flex items-center justify-between">
          <button
            type="button"
            onClick={() => setShowFilters(!showFilters)}
            className="text-sm text-gray-600 hover:text-gray-900 flex items-center gap-1.5"
          >
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6V4m0 2a2 2 0 100 4m0-4a2 2 0 110 4m-6 8a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4m6 6v10m6-2a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4" />
            </svg>
            Filters
            {activeFilterCount > 0 && (
              <span className="bg-blue-100 text-blue-700 text-xs font-medium px-1.5 py-0.5 rounded">
                {activeFilterCount}
              </span>
            )}
          </button>

          <div className="flex items-center gap-4">
            <label className="flex items-center gap-2 cursor-pointer">
              <input
                type="checkbox"
                checked={filters.easyApply}
                onChange={(e) => updateFilter('easyApply', e.target.checked)}
                className="w-4 h-4 text-blue-600 rounded border-gray-300 focus:ring-blue-500"
              />
              <span className="text-sm text-gray-600">Easy Apply</span>
            </label>
          </div>
        </div>

        {/* Expanded Filters */}
        {showFilters && (
          <div className="mt-4 pt-4 border-t border-gray-100 grid grid-cols-2 sm:grid-cols-3 md:grid-cols-5 gap-3">
            <select
              value={filters.jobType}
              onChange={(e) => updateFilter('jobType', e.target.value)}
              className="px-3 py-2 text-sm bg-gray-50 border border-gray-200 rounded-lg focus:bg-white focus:border-blue-500"
            >
              <option value="">Job Type</option>
              <option value="full-time">Full-time</option>
              <option value="part-time">Part-time</option>
              <option value="contract">Contract</option>
              <option value="internship">Internship</option>
            </select>

            <select
              value={filters.remote}
              onChange={(e) => updateFilter('remote', e.target.value)}
              className="px-3 py-2 text-sm bg-gray-50 border border-gray-200 rounded-lg focus:bg-white focus:border-blue-500"
            >
              <option value="">Work Type</option>
              <option value="remote">Remote</option>
              <option value="hybrid">Hybrid</option>
              <option value="on-site">On-site</option>
            </select>

            <select
              value={filters.experience}
              onChange={(e) => updateFilter('experience', e.target.value)}
              className="px-3 py-2 text-sm bg-gray-50 border border-gray-200 rounded-lg focus:bg-white focus:border-blue-500"
            >
              <option value="">Experience</option>
              <option value="internship">Internship</option>
              <option value="entry-level">Entry Level</option>
              <option value="associate">Associate</option>
              <option value="senior">Senior</option>
              <option value="director">Director</option>
            </select>

            <select
              value={filters.datePosted}
              onChange={(e) => updateFilter('datePosted', e.target.value)}
              className="px-3 py-2 text-sm bg-gray-50 border border-gray-200 rounded-lg focus:bg-white focus:border-blue-500"
            >
              <option value="">Date Posted</option>
              <option value="24hr">Past 24 hours</option>
              <option value="past-week">Past week</option>
              <option value="past-month">Past month</option>
            </select>

            <select
              value={filters.limit}
              onChange={(e) => updateFilter('limit', Number(e.target.value))}
              className="px-3 py-2 text-sm bg-gray-50 border border-gray-200 rounded-lg focus:bg-white focus:border-blue-500"
            >
              <option value="10">10 results</option>
              <option value="25">25 results</option>
              <option value="50">50 results</option>
            </select>
          </div>
        )}
      </div>
    </form>
  );
}
