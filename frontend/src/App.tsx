import { useState, useMemo } from 'react';
import { SearchForm } from './components/SearchForm';
import { JobList } from './components/JobList';
import { SearchHistory } from './components/SearchHistory';
import { SavedJobs } from './components/SavedJobs';
import { ApplicationTracker } from './components/ApplicationTracker';
import { ThemeToggle } from './components/ThemeToggle';
import { SkeletonList } from './components/SkeletonCard';
import { ErrorMessage } from './components/ErrorMessage';
import { CompanyInfoModal } from './components/CompanyInfoModal';
import { useTheme } from './hooks/useTheme';
import { useLocalStorage } from './hooks/useLocalStorage';
import { searchJobs } from './services/api';
import type { Job, SearchFilters, SearchHistoryItem, SavedJob, AppliedJob } from './types/job';

type Tab = 'search' | 'saved' | 'applications';

const ITEMS_PER_PAGE = 12;

function App() {
  const [theme, toggleTheme] = useTheme();
  const [activeTab, setActiveTab] = useState<Tab>('search');
  
  const [jobs, setJobs] = useState<Job[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [searchMeta, setSearchMeta] = useState({ keyword: '', location: '' });
  const [hasSearched, setHasSearched] = useState(false);
  const [currentPage, setCurrentPage] = useState(1);
  
  const [searchHistory, setSearchHistory] = useLocalStorage<SearchHistoryItem[]>('searchHistory', []);
  const [savedJobs, setSavedJobs] = useLocalStorage<SavedJob[]>('savedJobs', []);
  const [appliedJobs, setAppliedJobs] = useLocalStorage<AppliedJob[]>('appliedJobs', []);
  
  const [selectedCompany, setSelectedCompany] = useState<string | null>(null);
  const [pendingSearch, setPendingSearch] = useState<Partial<SearchFilters> | null>(null);
  const [lastFilters, setLastFilters] = useState<SearchFilters | null>(null);

  const totalPages = Math.ceil(jobs.length / ITEMS_PER_PAGE);
  const paginatedJobs = useMemo(() => {
    const start = (currentPage - 1) * ITEMS_PER_PAGE;
    return jobs.slice(start, start + ITEMS_PER_PAGE);
  }, [jobs, currentPage]);

  const handleSearch = async (filters: SearchFilters) => {
    setIsLoading(true);
    setError(null);
    setHasSearched(true);
    setCurrentPage(1);
    setLastFilters(filters);

    try {
      const response = await searchJobs(filters);
      setJobs(response.jobs);
      setSearchMeta({ keyword: response.keyword, location: response.location });

      const historyItem: SearchHistoryItem = {
        id: Date.now().toString(),
        keyword: filters.keyword,
        location: filters.location,
        timestamp: new Date().toISOString(),
        resultCount: response.jobs.length,
      };
      setSearchHistory(prev => {
        const filtered = prev.filter(h => !(h.keyword === filters.keyword && h.location === filters.location));
        return [historyItem, ...filtered].slice(0, 10);
      });
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Search failed');
      setJobs([]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleHistorySelect = (item: SearchHistoryItem) => {
    setPendingSearch({ keyword: item.keyword, location: item.location });
  };

  const handleSaveJob = (job: Job) => {
    const savedJob: SavedJob = {
      ...job,
      savedAt: new Date().toISOString(),
    };
    setSavedJobs(prev => [savedJob, ...prev.filter(j => j.job_url !== job.job_url)]);
  };

  const handleUnsaveJob = (jobUrl: string) => {
    setSavedJobs(prev => prev.filter(j => j.job_url !== jobUrl));
  };

  const handleUpdateSavedNotes = (jobUrl: string, notes: string) => {
    setSavedJobs(prev => prev.map(j => j.job_url === jobUrl ? { ...j, notes } : j));
  };

  const handleMarkApplied = (job: Job) => {
    const appliedJob: AppliedJob = {
      ...job,
      appliedAt: new Date().toISOString(),
      status: 'applied',
    };
    setAppliedJobs(prev => [appliedJob, ...prev.filter(j => j.job_url !== job.job_url)]);
  };

  const handleUpdateAppStatus = (jobUrl: string, status: AppliedJob['status']) => {
    setAppliedJobs(prev => prev.map(j => j.job_url === jobUrl ? { ...j, status } : j));
  };

  const handleUpdateAppNotes = (jobUrl: string, notes: string) => {
    setAppliedJobs(prev => prev.map(j => j.job_url === jobUrl ? { ...j, notes } : j));
  };

  const handleRemoveApp = (jobUrl: string) => {
    setAppliedJobs(prev => prev.filter(j => j.job_url !== jobUrl));
  };

  const handlePageChange = (page: number) => {
    setCurrentPage(page);
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  const tabClass = (tab: Tab) =>
    `px-4 py-2 text-sm font-medium rounded-lg transition-colors ${
      activeTab === tab
        ? 'bg-blue-600 text-white'
        : 'text-gray-600 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-700'
    }`;

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 transition-colors">
      <header className="bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700 sticky top-0 z-40">
        <div className="max-w-6xl mx-auto px-4 sm:px-6 py-3">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="w-9 h-9 bg-gradient-to-br from-blue-500 to-blue-700 rounded-xl flex items-center justify-center shadow-lg shadow-blue-500/25">
                <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 13.255A23.931 23.931 0 0112 15c-3.183 0-6.22-.62-9-1.745M16 6V4a2 2 0 00-2-2h-4a2 2 0 00-2 2v2m4 6h.01M5 20h14a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                </svg>
              </div>
              <div>
                <h1 className="text-lg font-bold text-gray-900 dark:text-white">LinkedIn Job Scraper</h1>
                <p className="text-xs text-gray-500 dark:text-gray-400 hidden sm:block">Find your next opportunity</p>
              </div>
            </div>
            
            <div className="flex items-center gap-2">
              <div className="hidden sm:flex items-center gap-1 bg-gray-100 dark:bg-gray-700 rounded-lg p-1">
                <button onClick={() => setActiveTab('search')} className={tabClass('search')}>
                  Search
                </button>
                <button onClick={() => setActiveTab('saved')} className={tabClass('saved')}>
                  Saved
                  {savedJobs.length > 0 && (
                    <span className="ml-1.5 bg-yellow-400 text-yellow-900 text-xs px-1.5 rounded-full">
                      {savedJobs.length}
                    </span>
                  )}
                </button>
                <button onClick={() => setActiveTab('applications')} className={tabClass('applications')}>
                  Applications
                  {appliedJobs.length > 0 && (
                    <span className="ml-1.5 bg-green-400 text-green-900 text-xs px-1.5 rounded-full">
                      {appliedJobs.length}
                    </span>
                  )}
                </button>
              </div>
              <ThemeToggle theme={theme} onToggle={toggleTheme} />
            </div>
          </div>
          
          {/* Mobile tabs */}
          <div className="flex sm:hidden items-center gap-1 mt-3 bg-gray-100 dark:bg-gray-700 rounded-lg p-1">
            <button onClick={() => setActiveTab('search')} className={`flex-1 ${tabClass('search')}`}>
              Search
            </button>
            <button onClick={() => setActiveTab('saved')} className={`flex-1 ${tabClass('saved')}`}>
              Saved {savedJobs.length > 0 && `(${savedJobs.length})`}
            </button>
            <button onClick={() => setActiveTab('applications')} className={`flex-1 ${tabClass('applications')}`}>
              Apps {appliedJobs.length > 0 && `(${appliedJobs.length})`}
            </button>
          </div>
        </div>
      </header>

      <main className="max-w-6xl mx-auto px-4 sm:px-6 py-6">
        {activeTab === 'search' && (
          <>
            <SearchHistory
              history={searchHistory}
              onSelect={handleHistorySelect}
              onClear={() => setSearchHistory([])}
              onRemove={(id) => setSearchHistory(prev => prev.filter(h => h.id !== id))}
            />

            <SearchForm 
              onSearch={handleSearch} 
              isLoading={isLoading}
              initialFilters={pendingSearch || undefined}
            />

            {error && (
              <ErrorMessage 
                message={error} 
                onRetry={lastFilters ? () => handleSearch(lastFilters) : undefined} 
              />
            )}

            {isLoading && <SkeletonList count={6} />}

            {hasSearched && !isLoading && !error && (
              <JobList 
                jobs={paginatedJobs} 
                keyword={searchMeta.keyword} 
                location={searchMeta.location}
                savedJobs={savedJobs}
                appliedJobs={appliedJobs}
                onSaveJob={handleSaveJob}
                onUnsaveJob={handleUnsaveJob}
                onMarkApplied={handleMarkApplied}
                onShowCompanyInfo={setSelectedCompany}
                currentPage={currentPage}
                totalPages={totalPages}
                onPageChange={handlePageChange}
                loading={isLoading}
              />
            )}

            {!hasSearched && !isLoading && (
              <div className="text-center py-20">
                <div className="w-20 h-20 mx-auto mb-6 bg-gradient-to-br from-blue-100 to-purple-100 dark:from-blue-900/30 dark:to-purple-900/30 rounded-full flex items-center justify-center">
                  <svg className="w-10 h-10 text-blue-600 dark:text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                  </svg>
                </div>
                <h2 className="text-xl font-bold text-gray-900 dark:text-white mb-2">
                  Find Your Dream Job
                </h2>
                <p className="text-gray-500 dark:text-gray-400 max-w-md mx-auto mb-8">
                  Search through thousands of LinkedIn job listings. Save jobs, track applications, and land your next role.
                </p>
                <div className="flex flex-wrap justify-center gap-2">
                  {['Software Engineer', 'Data Scientist', 'Product Manager', 'UX Designer'].map((term) => (
                    <button
                      key={term}
                      onClick={() => setPendingSearch({ keyword: term })}
                      className="px-4 py-2 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-full text-sm text-gray-700 dark:text-gray-300 hover:border-blue-500 hover:text-blue-600 dark:hover:text-blue-400 transition-colors"
                    >
                      {term}
                    </button>
                  ))}
                </div>
              </div>
            )}
          </>
        )}

        {activeTab === 'saved' && (
          <SavedJobs
            savedJobs={savedJobs}
            onRemove={handleUnsaveJob}
            onUpdateNotes={handleUpdateSavedNotes}
          />
        )}

        {activeTab === 'applications' && (
          <ApplicationTracker
            applications={appliedJobs}
            onUpdateStatus={handleUpdateAppStatus}
            onUpdateNotes={handleUpdateAppNotes}
            onRemove={handleRemoveApp}
          />
        )}
      </main>

      {selectedCompany && (
        <CompanyInfoModal
          company={selectedCompany}
          onClose={() => setSelectedCompany(null)}
        />
      )}
    </div>
  );
}

export default App;
