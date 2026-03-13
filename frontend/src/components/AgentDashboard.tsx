import React, { useState } from 'react';
import type { UserProfile, RankedJob, TailoredResume, CoverLetter, EvaluationMetrics } from '../types/job';
import { ProfileForm } from './ProfileForm';
import { RankedJobCard } from './RankedJobCard';
import { SkeletonList } from './SkeletonCard';
import { ErrorMessage } from './ErrorMessage';
import { createProfile, parseResume, uploadPdfResume, searchAndRankJobs, tailorResume, generateCoverLetter, evaluateApplications, runOfflineAgent } from '../services/api';

type AgentTab = 'profile' | 'search' | 'results' | 'evaluation';

export const AgentDashboard: React.FC = () => {
  const [activeTab, setActiveTab] = useState<AgentTab>('profile');
  const [profile, setProfile] = useState<UserProfile | null>(null);
  const [profileId, setProfileId] = useState<string | null>(null);
  const [rankedJobs, setRankedJobs] = useState<RankedJob[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  
  const [searchKeyword, setSearchKeyword] = useState('AI Engineer');
  const [searchLocation, setSearchLocation] = useState('');
  const [companySize, setCompanySize] = useState('mid');
  
  const [generatedResume, setGeneratedResume] = useState<TailoredResume | null>(null);
  const [generatedCoverLetter, setGeneratedCoverLetter] = useState<CoverLetter | null>(null);
  const [evaluation, setEvaluation] = useState<EvaluationMetrics | null>(null);
  const [agentMode, setAgentMode] = useState<'live' | 'offline'>('live');
  const [offlineReasoning, setOfflineReasoning] = useState<string | null>(null);

  const handleProfileSubmit = async (profileData: UserProfile) => {
    setIsLoading(true);
    setError(null);
    try {
      const result = await createProfile(profileData);
      setProfile(result.profile as unknown as UserProfile);
      setProfileId(result.profile_id);
      setActiveTab('search');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to save profile');
    } finally {
      setIsLoading(false);
    }
  };

  const handleParseResume = async (text: string) => {
    setIsLoading(true);
    setError(null);
    try {
      const result = await parseResume(text);
      setProfile(result.profile as unknown as UserProfile);
      setProfileId(result.profile_id);
      setActiveTab('search');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to parse resume');
    } finally {
      setIsLoading(false);
    }
  };

  const handleUploadPdf = async (file: File) => {
    setIsLoading(true);
    setError(null);
    try {
      const result = await uploadPdfResume(file);
      setProfile(result.profile as unknown as UserProfile);
      setProfileId(result.profile_id);
      setActiveTab('search');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to upload PDF resume');
    } finally {
      setIsLoading(false);
    }
  };

  const handleSearch = async () => {
    if (!profileId) return;
    
    setIsLoading(true);
    setError(null);
    try {
      if (agentMode === 'live') {
        const result = await searchAndRankJobs(searchKeyword, searchLocation, profileId, companySize, 50, 20);
        setRankedJobs(result.jobs);
        setOfflineReasoning(result.reasoning ?? null);
      } else {
        const result = await runOfflineAgent(profileId, 10, false);
        setRankedJobs(result.ranked_jobs);
        setOfflineReasoning(result.reasoning ?? null);
        // Optionally pre-load tailored resume for the best job
        setGeneratedResume(result.tailored_resume as unknown as TailoredResume);
      }
      setActiveTab('results');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Search failed');
    } finally {
      setIsLoading(false);
    }
  };

  const handleGenerateResume = async (jobUrl: string) => {
    if (!profileId) return;

    setIsLoading(true);
    try {
      const resume = await tailorResume(profileId, jobUrl);
      setGeneratedResume(resume);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to generate resume');
    } finally {
      setIsLoading(false);
    }
  };

  const handleGenerateCoverLetter = async (jobUrl: string) => {
    if (!profileId) return;

    setIsLoading(true);
    try {
      const letter = await generateCoverLetter(profileId, jobUrl);
      setGeneratedCoverLetter(letter);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to generate cover letter');
    } finally {
      setIsLoading(false);
    }
  };

  const handleRunEvaluation = async () => {
    if (!profileId) return;
    
    setIsLoading(true);
    setError(null);
    try {
      const result = await evaluateApplications(profileId, searchKeyword, 5);
      setEvaluation(result);
      setActiveTab('evaluation');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Evaluation failed');
    } finally {
      setIsLoading(false);
    }
  };

  const tabClass = (tab: AgentTab) =>
    `px-4 py-2 text-sm font-medium rounded-lg transition-colors ${
      activeTab === tab
        ? 'bg-teal-600 text-white'
        : 'text-gray-600 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-700'
    }`;

  return (
    <div>
      <div className="mb-6 flex flex-wrap items-center gap-2">
        <button onClick={() => setActiveTab('profile')} className={tabClass('profile')}>
          1. Profile
        </button>
        <button onClick={() => setActiveTab('search')} disabled={!profileId} className={tabClass('search')}>
          2. Search
        </button>
        <button onClick={() => setActiveTab('results')} disabled={rankedJobs.length === 0} className={tabClass('results')}>
          3. Results ({rankedJobs.length})
        </button>
        <button onClick={() => setActiveTab('evaluation')} disabled={!profileId} className={tabClass('evaluation')}>
          4. Evaluation
        </button>
      </div>

      {error && <ErrorMessage message={error} onRetry={() => setError(null)} />}

      {/* Profile Tab */}
      {activeTab === 'profile' && (
        <div>
          <h2 className="text-xl font-bold text-gray-900 dark:text-white mb-4">
            {profile ? 'Edit Your Profile' : 'Create Your Profile'}
          </h2>
          <ProfileForm
            onSubmit={handleProfileSubmit}
            onParseResume={handleParseResume}
            onUploadPdf={handleUploadPdf}
            initialProfile={profile || undefined}
            isLoading={isLoading}
          />
        </div>
      )}

      {/* Search Tab */}
      {activeTab === 'search' && profileId && (
        <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-6">
          <h2 className="text-xl font-bold text-gray-900 dark:text-white mb-4">
            AI Job Search
          </h2>
          
          <div className="mb-4 flex flex-wrap items-center gap-3">
            <span className="text-sm font-medium text-gray-700 dark:text-gray-300">Data Source:</span>
            <div className="inline-flex rounded-lg border border-gray-200 dark:border-gray-600 overflow-hidden">
              <button
                type="button"
                onClick={() => setAgentMode('live')}
                className={`px-3 py-1.5 text-xs sm:text-sm font-medium ${
                  agentMode === 'live'
                    ? 'bg-teal-600 text-white'
                    : 'bg-white dark:bg-gray-800 text-gray-700 dark:text-gray-300'
                }`}
              >
                Live Web (LinkedIn)
              </button>
              <button
                type="button"
                onClick={() => setAgentMode('offline')}
                className={`px-3 py-1.5 text-xs sm:text-sm font-medium border-l border-gray-200 dark:border-gray-600 ${
                  agentMode === 'offline'
                    ? 'bg-teal-600 text-white'
                    : 'bg-white dark:bg-gray-800 text-gray-700 dark:text-gray-300'
                }`}
              >
                Offline CSV Dataset
              </button>
            </div>
            {agentMode === 'offline' && (
              <span className="text-xs text-gray-500 dark:text-gray-400">
                Uses <code>data/jobs_dataset.csv</code> instead of live scraping.
              </span>
            )}
          </div>
          
          {profile && (
            <div className="mb-6 p-4 bg-teal-50 dark:bg-teal-900/20 rounded-lg">
              <p className="text-sm text-teal-700 dark:text-teal-300">
                Searching as <strong>{profile.name}</strong> • {profile.skills?.slice(0, 5).join(', ')}
              </p>
            </div>
          )}

          {agentMode === 'live' && (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                Job Title / Keywords
              </label>
              <input
                type="text"
                value={searchKeyword}
                onChange={(e) => setSearchKeyword(e.target.value)}
                placeholder="AI Engineer"
                className="w-full px-3 py-2 bg-gray-50 dark:bg-gray-700 border border-gray-200 dark:border-gray-600 rounded-lg text-gray-900 dark:text-white"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                Location
              </label>
              <input
                type="text"
                value={searchLocation}
                onChange={(e) => setSearchLocation(e.target.value)}
                placeholder="San Francisco or Remote"
                className="w-full px-3 py-2 bg-gray-50 dark:bg-gray-700 border border-gray-200 dark:border-gray-600 rounded-lg text-gray-900 dark:text-white"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                Company Size
              </label>
              <select
                value={companySize}
                onChange={(e) => setCompanySize(e.target.value)}
                className="w-full px-3 py-2 bg-gray-50 dark:bg-gray-700 border border-gray-200 dark:border-gray-600 rounded-lg text-gray-900 dark:text-white"
              >
                <option value="">All Sizes</option>
                <option value="small">Startups</option>
                <option value="mid">Mid-sized</option>
                <option value="large">Enterprise</option>
              </select>
            </div>
          </div>
          )}

          <button
            onClick={handleSearch}
            disabled={!searchKeyword || isLoading}
            className="w-full px-6 py-3 bg-teal-600 text-white rounded-xl font-semibold hover:bg-teal-700 disabled:bg-gray-300 dark:disabled:bg-gray-600 disabled:cursor-not-allowed transition-colors flex items-center justify-center gap-2"
          >
            {isLoading ? (
              <>
                <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin" />
                {agentMode === 'live' ? 'Searching & Ranking...' : 'Running Offline Agent...'}
              </>
            ) : (
              <>
                <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
                </svg>
                {agentMode === 'live' ? 'Search & Rank Jobs' : 'Run Offline CSV Agent'}
              </>
            )}
          </button>
        </div>
      )}

      {/* Results Tab */}
      {activeTab === 'results' && (
        <div>
          {offlineReasoning && (
            <div className="mb-4 p-4 bg-indigo-50 dark:bg-indigo-900/20 rounded-xl border border-indigo-100 dark:border-indigo-800">
              <h3 className="text-sm font-semibold text-indigo-800 dark:text-indigo-200 mb-1">
                LLM Reasoning & Trace
              </h3>
              <p className="text-xs text-indigo-900 dark:text-indigo-100 whitespace-pre-wrap">
                {offlineReasoning}
              </p>
            </div>
          )}
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-xl font-bold text-gray-900 dark:text-white">
              Top Matches for You
            </h2>
            <div className="flex gap-2">
              <button
                onClick={handleRunEvaluation}
                disabled={isLoading}
                className="px-4 py-2 bg-green-600 text-white text-sm rounded-lg hover:bg-green-700 transition-colors"
              >
                Run Evaluation
              </button>
            </div>
          </div>

          {isLoading ? (
            <SkeletonList count={6} />
          ) : (
            <div className="space-y-4">
              {rankedJobs.map((rankedJob, index) => (
                <RankedJobCard
                  key={`${rankedJob.job.job_url}-${index}`}
                  rankedJob={rankedJob}
                  onGenerateResume={handleGenerateResume}
                  onGenerateCoverLetter={handleGenerateCoverLetter}
                  isGenerating={isLoading}
                />
              ))}
            </div>
          )}
        </div>
      )}

      {/* Evaluation Tab */}
      {activeTab === 'evaluation' && (
        <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-6">
          <h2 className="text-xl font-bold text-gray-900 dark:text-white mb-2">
            Hiring Simulation Results
          </h2>
          <p className="text-sm text-gray-500 dark:text-gray-400 mb-4">
            A simulated recruiter reviewed your profile against sample jobs. Use these metrics to improve your applications.
          </p>
          
          {!evaluation ? (
            <div className="text-center py-12">
              <p className="text-gray-500 dark:text-gray-400 mb-4">
                Run a hiring simulation to see how your applications would perform
              </p>
              <p className="text-xs text-gray-400 dark:text-gray-500 mb-4">
                Uses benchmark data (~5 sec). No LinkedIn scraping needed.
              </p>
              <button
                onClick={handleRunEvaluation}
                disabled={isLoading}
                className="px-6 py-3 bg-teal-600 text-white rounded-xl font-semibold hover:bg-teal-700 transition-colors disabled:opacity-70"
              >
                {isLoading ? 'Running simulation...' : 'Start Simulation'}
              </button>
            </div>
          ) : (
            <div>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
                <div className="bg-teal-50 dark:bg-teal-900/20 rounded-xl p-4 text-center">
                  <p className="text-3xl font-bold text-teal-700 dark:text-teal-400">
                    {Math.round((evaluation.interview_rate <= 1 ? evaluation.interview_rate * 100 : evaluation.interview_rate))}%
                  </p>
                  <p className="text-sm font-medium text-teal-600 dark:text-teal-400">Interview Rate</p>
                  <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">% of apps that would get an interview</p>
                </div>
                <div className="bg-green-50 dark:bg-green-900/20 rounded-lg p-4 text-center">
                  <p className="text-3xl font-bold text-green-700 dark:text-green-400">
                    {Math.round(evaluation.avg_match_score)}
                  </p>
                  <p className="text-sm font-medium text-green-600 dark:text-green-400">Match Score</p>
                  <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">0–100: how well you fit the job</p>
                </div>
                <div className="bg-cyan-50 dark:bg-cyan-900/20 rounded-xl p-4 text-center">
                  <p className="text-3xl font-bold text-cyan-700 dark:text-cyan-400">
                    {Math.round(evaluation.avg_ats_score)}
                  </p>
                  <p className="text-sm font-medium text-cyan-600 dark:text-cyan-400">ATS Score</p>
                  <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">0–100: resume readability by systems</p>
                </div>
                <div className="bg-orange-50 dark:bg-orange-900/20 rounded-lg p-4 text-center">
                  <p className="text-3xl font-bold text-orange-700 dark:text-orange-400">
                    {Math.round((evaluation.skill_coverage <= 1 ? evaluation.skill_coverage * 100 : evaluation.skill_coverage))}%
                  </p>
                  <p className="text-sm font-medium text-orange-600 dark:text-orange-400">Skill Coverage</p>
                  <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">% of job skills you have</p>
                </div>
              </div>

              <h3 className="font-semibold text-gray-900 dark:text-white mb-1">Recruiter Feedback</h3>
              <p className="text-sm text-gray-500 dark:text-gray-400 mb-3">
                Per-application scores. Resume = ATS compatibility (0–100). Cover Letter = personalization (0–100). Advance = would interview.
              </p>
              <div className="space-y-3">
                {evaluation.recruiter_feedback.map((fb, i) => (
                  <div key={i} className="p-4 bg-gray-50 dark:bg-gray-700/50 rounded-lg">
                    <div className="flex items-center justify-between mb-2">
                      <span className="font-medium text-gray-900 dark:text-white">{fb.application_id}</span>
                      <span className={`px-3 py-1 rounded-full text-sm font-medium capitalize ${
                        fb.decision === 'interview' ? 'bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400' :
                        fb.decision === 'maybe' ? 'bg-yellow-100 text-yellow-700 dark:bg-yellow-900/30 dark:text-yellow-400' :
                        'bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400'
                      }`}>
                        {fb.decision === 'interview' ? 'Advance' : fb.decision}
                      </span>
                    </div>
                    <div className="flex gap-4 text-sm text-gray-600 dark:text-gray-400">
                      <span>Resume (ATS): {Math.round(fb.resume_score)}/100</span>
                      <span>Cover Letter: {Math.round(fb.cover_letter_score)}/100</span>
                    </div>
                    {fb.strengths.length > 0 && (
                      <p className="text-sm text-green-600 dark:text-green-400 mt-2">
                        ✓ {fb.strengths.join(' • ')}
                      </p>
                    )}
                    {fb.weaknesses.length > 0 && (
                      <p className="text-sm text-orange-600 dark:text-orange-400 mt-1">
                        △ {fb.weaknesses.join(' • ')}
                      </p>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      {/* Generated Content Modal */}
      {(generatedResume || generatedCoverLetter) && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50" onClick={() => { setGeneratedResume(null); setGeneratedCoverLetter(null); }}>
          <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-xl max-w-3xl w-full max-h-[80vh] overflow-hidden" onClick={e => e.stopPropagation()}>
            <div className="p-6 border-b border-gray-200 dark:border-gray-700 flex items-center justify-between">
              <h2 className="text-xl font-bold text-gray-900 dark:text-white">
                {generatedResume ? 'Tailored Resume' : 'Cover Letter'}
              </h2>
              <button
                onClick={() => { setGeneratedResume(null); setGeneratedCoverLetter(null); }}
                className="text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
              >
                <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>
            <div className="p-6 overflow-y-auto max-h-[60vh]">
              {generatedResume && (
                <div>
                  <div className="flex items-center gap-4 mb-4">
                    <div className="px-3 py-1 bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-400 rounded-full text-sm font-medium">
                      ATS Score: {generatedResume.ats_score}%
                    </div>
                  </div>
                  {generatedResume.suggestions.length > 0 && (
                    <div className="mb-4 p-3 bg-yellow-50 dark:bg-yellow-900/20 rounded-lg">
                      <p className="text-sm font-medium text-yellow-800 dark:text-yellow-300 mb-1">Suggestions:</p>
                      <ul className="text-sm text-yellow-700 dark:text-yellow-400 list-disc list-inside">
                        {generatedResume.suggestions.map((s, i) => <li key={i}>{s}</li>)}
                      </ul>
                    </div>
                  )}
                  <pre className="whitespace-pre-wrap text-sm text-gray-700 dark:text-gray-300 font-mono bg-gray-50 dark:bg-gray-700/50 p-4 rounded-lg">
                    {generatedResume.resume_text}
                  </pre>
                </div>
              )}
              {generatedCoverLetter && (
                <div>
                  <div className="flex items-center gap-4 mb-4">
                    <div className="px-3 py-1 bg-teal-100 dark:bg-teal-900/30 text-teal-700 dark:text-teal-400 rounded-full text-sm font-medium">
                      Personalization: {generatedCoverLetter.personalization_score}%
                    </div>
                    <div className="px-3 py-1 bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded-full text-sm">
                      {generatedCoverLetter.word_count} words
                    </div>
                  </div>
                  <pre className="whitespace-pre-wrap text-sm text-gray-700 dark:text-gray-300 bg-gray-50 dark:bg-gray-700/50 p-4 rounded-lg">
                    {generatedCoverLetter.content}
                  </pre>
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
