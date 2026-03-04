import { useState, useMemo } from 'react';
import { SearchForm } from './components/SearchForm';
import { JobList } from './components/JobList';
import { SearchHistory } from './components/SearchHistory';
import { SavedJobs } from './components/SavedJobs';
import { ApplicationTracker } from './components/ApplicationTracker';
import { AgentDashboard } from './components/AgentDashboard';
import { ThemeToggle } from './components/ThemeToggle';
import { SkeletonList } from './components/SkeletonCard';
import { ErrorMessage } from './components/ErrorMessage';
import { CompanyInfoModal } from './components/CompanyInfoModal';
import { useTheme } from './hooks/useTheme';
import { useLocalStorage } from './hooks/useLocalStorage';
import { searchJobsMultiSource } from './services/api';
import type { Job, SearchFilters, SearchHistoryItem, SavedJob, AppliedJob } from './types/job';

type Tab = 'search' | 'agent' | 'saved' | 'applications';

const ITEMS_PER_PAGE = 12;

function App() {
  const [theme, toggleTheme] = useTheme();
  const [activeTab, setActiveTab] = useState<Tab>('search');
  
  const [jobs, setJobs] = useState<Job[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [searchMeta, setSearchMeta] = useState({ keyword: '', location: '', sources: [] as string[], jobsBySource: {} as Record<string, number> });
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
      const response = await searchJobsMultiSource(filters);
      setJobs(response.jobs);
      setSearchMeta({ 
        keyword: response.keyword, 
        location: response.location,
        sources: response.sources,
        jobsBySource: response.jobs_by_source,
      });

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
    `px-4 py-2.5 text-sm font-medium transition-colors border-b-2 -mb-px ${
      activeTab === tab
        ? 'border-teal-600 text-teal-600 dark:border-teal-400 dark:text-teal-400'
        : 'border-transparent text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-200 hover:border-gray-300 dark:hover:border-gray-600'
    }`;

  return (
    <div className="min-h-screen bg-stone-50 dark:bg-gray-950 transition-colors">
      <header className="bg-white/90 dark:bg-gray-900/90 backdrop-blur-sm border-b border-stone-200 dark:border-gray-800 sticky top-0 z-40">
        <div className="max-w-6xl mx-auto px-4 sm:px-6 py-3">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 bg-gradient-to-br from-teal-500 to-cyan-600 rounded-2xl flex items-center justify-center shadow-lg shadow-teal-500/20 ring-2 ring-white dark:ring-gray-800">
                <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0zM10 7v3m0 0v3m0-3h3m-3 0H7" />
                </svg>
              </div>
              <div>
                <h1 className="text-xl font-bold text-stone-900 dark:text-white tracking-tight">Career Match</h1>
                <p className="text-xs text-stone-500 dark:text-gray-400 hidden sm:block">Middle America AI jobs · Tailored applications</p>
              </div>
            </div>
            
            <div className="flex items-center gap-2">
              <nav className="hidden md:flex items-center gap-0 border-b border-stone-200 dark:border-gray-700">
                <button onClick={() => setActiveTab('search')} className={tabClass('search')}>
                  Search
                </button>
                <button onClick={() => setActiveTab('agent')} className={`${tabClass('agent')} flex items-center gap-1.5`}>
                  <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                  </svg>
                  AI Agent
                </button>
                <button onClick={() => setActiveTab('saved')} className={tabClass('saved')}>
                  Saved
                  {savedJobs.length > 0 && (
                    <span className="bg-amber-500/20 text-amber-700 dark:text-amber-400 text-xs px-1.5 py-0.5 rounded-md font-medium ml-1">
                      {savedJobs.length}
                    </span>
                  )}
                </button>
                <button onClick={() => setActiveTab('applications')} className={`${tabClass('applications')} flex items-center gap-1.5`}>
                  Applications
                  {appliedJobs.length > 0 && (
                    <span className="bg-emerald-500/20 text-emerald-700 dark:text-emerald-400 text-xs px-1.5 py-0.5 rounded-md font-medium">
                      {appliedJobs.length}
                    </span>
                  )}
                </button>
              </nav>
              <ThemeToggle theme={theme} onToggle={toggleTheme} />
            </div>
          </div>
          
          {/* Mobile tabs */}
          <div className="flex md:hidden items-center gap-0 mt-3 border-b border-stone-200 dark:border-gray-700 overflow-x-auto pb-px">
            <button onClick={() => setActiveTab('search')} className={`flex-shrink-0 ${tabClass('search')}`}>
              Search
            </button>
            <button onClick={() => setActiveTab('agent')} className={`flex-shrink-0 ${tabClass('agent')}`}>
              AI Agent
            </button>
            <button onClick={() => setActiveTab('saved')} className={`flex-shrink-0 ${tabClass('saved')}`}>
              Saved {savedJobs.length > 0 && `(${savedJobs.length})`}
            </button>
            <button onClick={() => setActiveTab('applications')} className={`flex-shrink-0 ${tabClass('applications')}`}>
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
                <div className="w-24 h-24 mx-auto mb-6 bg-gradient-to-br from-teal-100 to-cyan-100 dark:from-teal-900/30 dark:to-cyan-900/30 rounded-3xl flex items-center justify-center">
                  <svg className="w-12 h-12 text-teal-600 dark:text-teal-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                  </svg>
                </div>
                <h2 className="text-2xl font-bold text-stone-900 dark:text-white mb-2 tracking-tight">
                  Find Middle America AI Jobs
                </h2>
                <p className="text-stone-600 dark:text-gray-400 max-w-md mx-auto mb-6">
                  Search LinkedIn, Indeed & Greenhouse. Filter out big tech, rank by fit, get tailored resumes.
                </p>
                <p className="text-sm text-teal-600 dark:text-teal-400 mb-6">
                  Use the <button onClick={() => setActiveTab('agent')} className="font-semibold hover:underline">AI Agent</button> for profile-based matching & cover letters
                </p>
                <div className="flex flex-wrap justify-center gap-2">
                  {['AI Engineer', 'Machine Learning', 'Data Scientist', 'ML Engineer'].map((term) => (
                    <button
                      key={term}
                      onClick={() => setPendingSearch({ keyword: term })}
                      className="px-5 py-2.5 bg-white dark:bg-gray-800/80 border border-stone-200 dark:border-gray-700 rounded-xl text-sm font-medium text-stone-700 dark:text-gray-300 hover:border-teal-400 hover:text-teal-600 dark:hover:text-teal-400 hover:shadow-sm transition-all"
                    >
                      {term}
                    </button>
                  ))}
                </div>
              </div>
            )}
          </>
        )}

        {activeTab === 'agent' && (
          <AgentDashboard />
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
