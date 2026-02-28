import { useState } from 'react';
import { SearchForm } from './components/SearchForm';
import { JobList } from './components/JobList';
import { searchJobs } from './services/api';
import type { Job, SearchFilters } from './types/job';

function App() {
  const [jobs, setJobs] = useState<Job[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [searchMeta, setSearchMeta] = useState({ keyword: '', location: '' });
  const [hasSearched, setHasSearched] = useState(false);

  const handleSearch = async (filters: SearchFilters) => {
    setIsLoading(true);
    setError(null);
    setHasSearched(true);

    try {
      const response = await searchJobs(filters);
      setJobs(response.jobs);
      setSearchMeta({ keyword: response.keyword, location: response.location });
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Search failed');
      setJobs([]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white border-b border-gray-200">
        <div className="max-w-5xl mx-auto px-4 sm:px-6 py-4">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 bg-blue-600 rounded-lg flex items-center justify-center">
              <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 13.255A23.931 23.931 0 0112 15c-3.183 0-6.22-.62-9-1.745M16 6V4a2 2 0 00-2-2h-4a2 2 0 00-2 2v2m4 6h.01M5 20h14a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
              </svg>
            </div>
            <h1 className="text-xl font-semibold text-gray-900">Job Search</h1>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-5xl mx-auto px-4 sm:px-6 py-6">
        <SearchForm onSearch={handleSearch} isLoading={isLoading} />

        {/* Error State */}
        {error && (
          <div className="bg-red-50 border border-red-100 rounded-lg p-4 mb-6">
            <div className="flex gap-3">
              <svg className="w-5 h-5 text-red-500 flex-shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <div>
                <p className="text-sm font-medium text-red-800">Connection Error</p>
                <p className="text-sm text-red-600 mt-1">
                  Could not connect to the server. Make sure the API is running:
                </p>
                <code className="text-xs bg-red-100 px-2 py-1 rounded mt-2 inline-block text-red-700">
                  python api/main.py
                </code>
              </div>
            </div>
          </div>
        )}

        {/* Loading State */}
        {isLoading && (
          <div className="flex flex-col items-center justify-center py-16">
            <div className="w-10 h-10 border-3 border-blue-600 border-t-transparent rounded-full animate-spin mb-4"></div>
            <p className="text-gray-500">Searching for jobs...</p>
          </div>
        )}

        {/* Results */}
        {hasSearched && !isLoading && !error && (
          <JobList 
            jobs={jobs} 
            keyword={searchMeta.keyword} 
            location={searchMeta.location} 
          />
        )}

        {/* Empty State */}
        {!hasSearched && !isLoading && (
          <div className="text-center py-20">
            <div className="w-16 h-16 mx-auto mb-4 bg-gray-100 rounded-full flex items-center justify-center">
              <svg className="w-8 h-8 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
              </svg>
            </div>
            <h2 className="text-lg font-medium text-gray-900 mb-1">
              Search for jobs
            </h2>
            <p className="text-gray-500 text-sm max-w-sm mx-auto">
              Enter a job title or keywords to find opportunities on LinkedIn
            </p>
          </div>
        )}
      </main>
    </div>
  );
}

export default App;
