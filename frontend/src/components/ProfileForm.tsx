import React, { useState } from 'react';
import type { UserProfile, WorkExperience } from '../types/job';

interface ProfileFormProps {
  onSubmit: (profile: UserProfile) => void;
  onParseResume: (text: string) => void;
  onUploadPdf: (file: File) => void;
  initialProfile?: Partial<UserProfile>;
  isLoading?: boolean;
}

const defaultProfile: UserProfile = {
  name: '',
  email: '',
  phone: '',
  location: '',
  linkedin_url: '',
  github_url: '',
  portfolio_url: '',
  title: '',
  summary: '',
  years_experience: 0,
  skills: [],
  programming_languages: [],
  frameworks: [],
  tools: [],
  experience: [],
  education: [],
  certifications: [],
  projects: [],
  target_roles: [],
  target_companies: [],
  preferred_locations: [],
  remote_preference: 'flexible',
  min_salary: 0,
};

export const ProfileForm: React.FC<ProfileFormProps> = ({ 
  onSubmit, 
  onParseResume,
  onUploadPdf,
  initialProfile, 
  isLoading 
}) => {
  const [profile, setProfile] = useState<UserProfile>({ ...defaultProfile, ...initialProfile });
  const [resumeText, setResumeText] = useState('');
  const [activeTab, setActiveTab] = useState<'form' | 'paste' | 'upload'>('form');
  const [skillInput, setSkillInput] = useState('');
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [dragActive, setDragActive] = useState(false);

  const updateField = <K extends keyof UserProfile>(field: K, value: UserProfile[K]) => {
    setProfile(prev => ({ ...prev, [field]: value }));
  };

  const addSkill = () => {
    if (skillInput.trim() && !profile.skills.includes(skillInput.trim())) {
      updateField('skills', [...profile.skills, skillInput.trim()]);
      setSkillInput('');
    }
  };

  const removeSkill = (skill: string) => {
    updateField('skills', profile.skills.filter(s => s !== skill));
  };

  const addExperience = () => {
    const newExp: WorkExperience = {
      title: '',
      company: '',
      location: '',
      duration: '',
      description: '',
      highlights: [],
    };
    updateField('experience', [...profile.experience, newExp]);
  };

  const updateExperience = (index: number, field: keyof WorkExperience, value: any) => {
    const updated = [...profile.experience];
    updated[index] = { ...updated[index], [field]: value };
    updateField('experience', updated);
  };

  const removeExperience = (index: number) => {
    updateField('experience', profile.experience.filter((_, i) => i !== index));
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSubmit(profile);
  };

  const handlePasteResume = () => {
    if (resumeText.trim()) {
      onParseResume(resumeText);
    }
  };

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file && file.type === 'application/pdf') {
      setSelectedFile(file);
    }
  };

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    
    const file = e.dataTransfer.files?.[0];
    if (file && file.type === 'application/pdf') {
      setSelectedFile(file);
    }
  };

  const handleUploadPdf = () => {
    if (selectedFile) {
      onUploadPdf(selectedFile);
    }
  };

  const inputClass = "w-full px-3 py-2 bg-gray-50 dark:bg-gray-700 border border-gray-200 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-teal-500 text-gray-900 dark:text-white";
  const labelClass = "block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1";

  return (
    <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-6">
      <div className="flex gap-2 mb-6">
        <button
          type="button"
          onClick={() => setActiveTab('form')}
          className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
            activeTab === 'form'
              ? 'bg-teal-600 text-white'
              : 'bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300'
          }`}
        >
          Fill Form
        </button>
        <button
          type="button"
          onClick={() => setActiveTab('upload')}
          className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
            activeTab === 'upload'
              ? 'bg-teal-600 text-white'
              : 'bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300'
          }`}
        >
          Upload PDF
        </button>
        <button
          type="button"
          onClick={() => setActiveTab('paste')}
          className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
            activeTab === 'paste'
              ? 'bg-teal-600 text-white'
              : 'bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300'
          }`}
        >
          Paste Text
        </button>
      </div>

      {activeTab === 'upload' ? (
        <div>
          <label className={labelClass}>Upload your resume (PDF)</label>
          <div
            onDragEnter={handleDrag}
            onDragLeave={handleDrag}
            onDragOver={handleDrag}
            onDrop={handleDrop}
            className={`relative border-2 border-dashed rounded-lg p-8 text-center transition-colors ${
              dragActive
                ? 'border-teal-500 bg-teal-50 dark:bg-teal-900/20'
                : 'border-gray-300 dark:border-gray-600 hover:border-gray-400 dark:hover:border-gray-500'
            }`}
          >
            <input
              type="file"
              accept=".pdf,application/pdf"
              onChange={handleFileSelect}
              className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
            />
            <div className="space-y-2">
              <svg
                className="mx-auto h-12 w-12 text-gray-400"
                stroke="currentColor"
                fill="none"
                viewBox="0 0 48 48"
              >
                <path
                  d="M28 8H12a4 4 0 00-4 4v20m0 0v4a4 4 0 004 4h20a4 4 0 004-4V28m-8-20l8 8m0 0v8m0-8h-8"
                  strokeWidth={2}
                  strokeLinecap="round"
                  strokeLinejoin="round"
                />
              </svg>
              <div className="text-gray-600 dark:text-gray-400">
                <span className="font-medium text-teal-600 dark:text-teal-400">
                  Click to upload
                </span>{' '}
                or drag and drop
              </div>
              <p className="text-xs text-gray-500 dark:text-gray-500">PDF files only</p>
            </div>
          </div>
          
          {selectedFile && (
            <div className="mt-4 p-3 bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded-lg flex items-center justify-between">
              <div className="flex items-center gap-2">
                <svg className="w-5 h-5 text-green-600" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M4 4a2 2 0 012-2h4.586A2 2 0 0112 2.586L15.414 6A2 2 0 0116 7.414V16a2 2 0 01-2 2H6a2 2 0 01-2-2V4z" clipRule="evenodd" />
                </svg>
                <span className="text-sm text-green-700 dark:text-green-300 font-medium">
                  {selectedFile.name}
                </span>
                <span className="text-xs text-green-600 dark:text-green-400">
                  ({(selectedFile.size / 1024).toFixed(1)} KB)
                </span>
              </div>
              <button
                type="button"
                onClick={() => setSelectedFile(null)}
                className="text-green-600 hover:text-red-500 transition-colors"
              >
                <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clipRule="evenodd" />
                </svg>
              </button>
            </div>
          )}
          
          <button
            type="button"
            onClick={handleUploadPdf}
            disabled={!selectedFile || isLoading}
            className="mt-4 px-6 py-2 bg-teal-600 text-white rounded-lg font-medium hover:bg-teal-700 disabled:bg-gray-300 dark:disabled:bg-gray-600 disabled:cursor-not-allowed transition-colors"
          >
            {isLoading ? 'Uploading...' : 'Upload & Parse PDF'}
          </button>
        </div>
      ) : activeTab === 'paste' ? (
        <div>
          <label className={labelClass}>Paste your resume text</label>
          <textarea
            value={resumeText}
            onChange={(e) => setResumeText(e.target.value)}
            placeholder="Paste your resume content here and we'll automatically extract your information..."
            className={`${inputClass} h-64 resize-none`}
          />
          <button
            type="button"
            onClick={handlePasteResume}
            disabled={!resumeText.trim() || isLoading}
            className="mt-4 px-6 py-2 bg-teal-600 text-white rounded-lg font-medium hover:bg-teal-700 disabled:bg-gray-300 dark:disabled:bg-gray-600 disabled:cursor-not-allowed transition-colors"
          >
            {isLoading ? 'Parsing...' : 'Parse Resume'}
          </button>
        </div>
      ) : (
        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Basic Info */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className={labelClass}>Full Name *</label>
              <input
                type="text"
                value={profile.name}
                onChange={(e) => updateField('name', e.target.value)}
                className={inputClass}
                required
              />
            </div>
            <div>
              <label className={labelClass}>Professional Title</label>
              <input
                type="text"
                value={profile.title}
                onChange={(e) => updateField('title', e.target.value)}
                placeholder="e.g., AI Engineer"
                className={inputClass}
              />
            </div>
            <div>
              <label className={labelClass}>Email *</label>
              <input
                type="email"
                value={profile.email}
                onChange={(e) => updateField('email', e.target.value)}
                className={inputClass}
                required
              />
            </div>
            <div>
              <label className={labelClass}>Phone</label>
              <input
                type="tel"
                value={profile.phone}
                onChange={(e) => updateField('phone', e.target.value)}
                className={inputClass}
              />
            </div>
            <div>
              <label className={labelClass}>Location</label>
              <input
                type="text"
                value={profile.location}
                onChange={(e) => updateField('location', e.target.value)}
                placeholder="e.g., San Francisco, CA"
                className={inputClass}
              />
            </div>
            <div>
              <label className={labelClass}>Years of Experience</label>
              <input
                type="number"
                value={profile.years_experience}
                onChange={(e) => updateField('years_experience', parseInt(e.target.value) || 0)}
                min={0}
                max={50}
                className={inputClass}
              />
            </div>
          </div>

          {/* Links */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <label className={labelClass}>LinkedIn URL</label>
              <input
                type="url"
                value={profile.linkedin_url}
                onChange={(e) => updateField('linkedin_url', e.target.value)}
                className={inputClass}
              />
            </div>
            <div>
              <label className={labelClass}>GitHub URL</label>
              <input
                type="url"
                value={profile.github_url}
                onChange={(e) => updateField('github_url', e.target.value)}
                className={inputClass}
              />
            </div>
            <div>
              <label className={labelClass}>Portfolio URL</label>
              <input
                type="url"
                value={profile.portfolio_url}
                onChange={(e) => updateField('portfolio_url', e.target.value)}
                className={inputClass}
              />
            </div>
          </div>

          {/* Summary */}
          <div>
            <label className={labelClass}>Professional Summary</label>
            <textarea
              value={profile.summary}
              onChange={(e) => updateField('summary', e.target.value)}
              placeholder="Brief overview of your experience and career goals..."
              className={`${inputClass} h-24 resize-none`}
            />
          </div>

          {/* Skills */}
          <div>
            <label className={labelClass}>Skills</label>
            <div className="flex gap-2 mb-2">
              <input
                type="text"
                value={skillInput}
                onChange={(e) => setSkillInput(e.target.value)}
                onKeyDown={(e) => e.key === 'Enter' && (e.preventDefault(), addSkill())}
                placeholder="Add a skill and press Enter"
                className={`${inputClass} flex-1`}
              />
              <button
                type="button"
                onClick={addSkill}
                className="px-4 py-2 bg-gray-200 dark:bg-gray-600 text-gray-700 dark:text-gray-300 rounded-lg hover:bg-gray-300 dark:hover:bg-gray-500 transition-colors"
              >
                Add
              </button>
            </div>
            <div className="flex flex-wrap gap-2">
              {profile.skills.map((skill) => (
                <span
                  key={skill}
                  className="inline-flex items-center gap-1 px-3 py-1 bg-teal-100 dark:bg-teal-900/30 text-teal-700 dark:text-teal-300 rounded-full text-sm"
                >
                  {skill}
                  <button
                    type="button"
                    onClick={() => removeSkill(skill)}
                    className="hover:text-red-500"
                  >
                    ×
                  </button>
                </span>
              ))}
            </div>
          </div>

          {/* Experience */}
          <div>
            <div className="flex items-center justify-between mb-2">
              <label className={labelClass}>Work Experience</label>
              <button
                type="button"
                onClick={addExperience}
                className="text-sm text-teal-600 dark:text-teal-400 hover:underline"
              >
                + Add Experience
              </button>
            </div>
            <div className="space-y-4">
              {profile.experience.map((exp, index) => (
                <div key={index} className="p-4 bg-gray-50 dark:bg-gray-700/50 rounded-lg">
                  <div className="flex justify-between mb-3">
                    <span className="text-sm font-medium text-gray-500 dark:text-gray-400">
                      Experience #{index + 1}
                    </span>
                    <button
                      type="button"
                      onClick={() => removeExperience(index)}
                      className="text-red-500 hover:text-red-700 text-sm"
                    >
                      Remove
                    </button>
                  </div>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                    <input
                      type="text"
                      value={exp.title}
                      onChange={(e) => updateExperience(index, 'title', e.target.value)}
                      placeholder="Job Title"
                      className={inputClass}
                    />
                    <input
                      type="text"
                      value={exp.company}
                      onChange={(e) => updateExperience(index, 'company', e.target.value)}
                      placeholder="Company"
                      className={inputClass}
                    />
                    <input
                      type="text"
                      value={exp.location}
                      onChange={(e) => updateExperience(index, 'location', e.target.value)}
                      placeholder="Location"
                      className={inputClass}
                    />
                    <input
                      type="text"
                      value={exp.duration}
                      onChange={(e) => updateExperience(index, 'duration', e.target.value)}
                      placeholder="Duration (e.g., 2020 - Present)"
                      className={inputClass}
                    />
                  </div>
                  <textarea
                    value={exp.highlights.join('\n')}
                    onChange={(e) => updateExperience(index, 'highlights', e.target.value.split('\n').filter(h => h.trim()))}
                    placeholder="Key achievements (one per line)"
                    className={`${inputClass} mt-3 h-20 resize-none`}
                  />
                </div>
              ))}
            </div>
          </div>

          {/* Target Preferences */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className={labelClass}>Target Roles (comma-separated)</label>
              <input
                type="text"
                value={profile.target_roles.join(', ')}
                onChange={(e) => updateField('target_roles', e.target.value.split(',').map(s => s.trim()).filter(Boolean))}
                placeholder="AI Engineer, ML Engineer"
                className={inputClass}
              />
            </div>
            <div>
              <label className={labelClass}>Preferred Locations (comma-separated)</label>
              <input
                type="text"
                value={profile.preferred_locations.join(', ')}
                onChange={(e) => updateField('preferred_locations', e.target.value.split(',').map(s => s.trim()).filter(Boolean))}
                placeholder="San Francisco, Remote"
                className={inputClass}
              />
            </div>
            <div>
              <label className={labelClass}>Remote Preference</label>
              <select
                value={profile.remote_preference}
                onChange={(e) => updateField('remote_preference', e.target.value)}
                className={inputClass}
              >
                <option value="flexible">Flexible</option>
                <option value="remote">Remote Only</option>
                <option value="hybrid">Hybrid</option>
                <option value="onsite">On-site</option>
              </select>
            </div>
            <div>
              <label className={labelClass}>Minimum Salary</label>
              <input
                type="number"
                value={profile.min_salary}
                onChange={(e) => updateField('min_salary', parseInt(e.target.value) || 0)}
                placeholder="100000"
                className={inputClass}
              />
            </div>
          </div>

          <button
            type="submit"
            disabled={!profile.name || !profile.email || isLoading}
            className="w-full px-6 py-3 bg-teal-600 text-white rounded-lg font-medium hover:bg-teal-700 disabled:bg-gray-300 dark:disabled:bg-gray-600 disabled:cursor-not-allowed transition-colors"
          >
            {isLoading ? 'Saving...' : 'Save Profile'}
          </button>
        </form>
      )}
    </div>
  );
};
