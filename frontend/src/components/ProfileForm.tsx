import React, { useState } from 'react';
import type { UserProfile, WorkExperience } from '../types/job';

interface ProfileFormProps {
  onSubmit: (profile: UserProfile) => void;
  onParseResume: (text: string) => void;
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
  initialProfile, 
  isLoading 
}) => {
  const [profile, setProfile] = useState<UserProfile>({ ...defaultProfile, ...initialProfile });
  const [resumeText, setResumeText] = useState('');
  const [activeTab, setActiveTab] = useState<'form' | 'paste'>('form');
  const [skillInput, setSkillInput] = useState('');

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

  const inputClass = "w-full px-3 py-2 bg-gray-50 dark:bg-gray-700 border border-gray-200 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 text-gray-900 dark:text-white";
  const labelClass = "block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1";

  return (
    <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-6">
      <div className="flex gap-2 mb-6">
        <button
          type="button"
          onClick={() => setActiveTab('form')}
          className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
            activeTab === 'form'
              ? 'bg-blue-600 text-white'
              : 'bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300'
          }`}
        >
          Fill Form
        </button>
        <button
          type="button"
          onClick={() => setActiveTab('paste')}
          className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
            activeTab === 'paste'
              ? 'bg-blue-600 text-white'
              : 'bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300'
          }`}
        >
          Paste Resume
        </button>
      </div>

      {activeTab === 'paste' ? (
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
            className="mt-4 px-6 py-2 bg-blue-600 text-white rounded-lg font-medium hover:bg-blue-700 disabled:bg-gray-300 dark:disabled:bg-gray-600 disabled:cursor-not-allowed transition-colors"
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
                  className="inline-flex items-center gap-1 px-3 py-1 bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-300 rounded-full text-sm"
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
                className="text-sm text-blue-600 dark:text-blue-400 hover:underline"
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
            className="w-full px-6 py-3 bg-blue-600 text-white rounded-lg font-medium hover:bg-blue-700 disabled:bg-gray-300 dark:disabled:bg-gray-600 disabled:cursor-not-allowed transition-colors"
          >
            {isLoading ? 'Saving...' : 'Save Profile'}
          </button>
        </form>
      )}
    </div>
  );
};
