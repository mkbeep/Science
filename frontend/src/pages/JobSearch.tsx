import React, { useState, useEffect } from 'react';
import { searchJobs, getFilters } from '../api/api';
import { Job, Filters, SearchParams } from '../types';

const JobSearch: React.FC = () => {
  const [filters, setFilters] = useState<SearchParams>({ skill: '', location: '', level: '' });
  const [availableFilters, setAvailableFilters] = useState<Filters>({ locations: [], levels: [] });
  const [jobs, setJobs] = useState<Job[]>([]);
  const [loading, setLoading] = useState<boolean>(false);
  const [searched, setSearched] = useState<boolean>(false);

  useEffect(() => {
    loadFilters();
  }, []);

  const loadFilters = async (): Promise<void> => {
    try {
      const res = await getFilters();
      setAvailableFilters(res.data);
    } catch (error) {
      console.error('Error loading filters:', error);
    }
  };

  const handleSearch = async (): Promise<void> => {
    setLoading(true);
    setSearched(true);
    try {
      const params: SearchParams = {};
      if (filters.skill) params.skill = filters.skill;
      if (filters.location) params.location = filters.location;
      if (filters.level) params.level = filters.level;

      const res = await searchJobs(params);
      setJobs(res.data.jobs);
    } catch (error) {
      console.error('Error searching jobs:', error);
    }
    setLoading(false);
  };

  const handleFilterChange = (key: keyof SearchParams, value: string): void => {
    setFilters({ ...filters, [key]: value });
  };

  return (
    <div>
      <h1 style={{ marginBottom: '2rem', color: '#2d3748' }}>🔎 Job Search</h1>

      <div className="search-container">
        <div className="search-filters">
          <input
            type="text"
            placeholder="Search by skill (e.g., Python, Java)"
            value={filters.skill || ''}
            onChange={(e) => handleFilterChange('skill', e.target.value)}
          />

          <select
            value={filters.location || ''}
            onChange={(e) => handleFilterChange('location', e.target.value)}
          >
            <option value="">All Locations</option>
            {availableFilters.locations.map((loc, idx) => (
              <option key={idx} value={loc}>{loc}</option>
            ))}
          </select>

          <select
            value={filters.level || ''}
            onChange={(e) => handleFilterChange('level', e.target.value)}
          >
            <option value="">All Levels</option>
            {availableFilters.levels.map((level, idx) => (
              <option key={idx} value={level}>{level}</option>
            ))}
          </select>
        </div>

        <button className="search-button" onClick={handleSearch}>
          Search Jobs
        </button>
      </div>

      {loading && <div className="loading">Searching...</div>}

      {!loading && searched && (
        <div>
          <h2 style={{ marginBottom: '1rem', color: '#2d3748' }}>
            Found {jobs.length} jobs
          </h2>

          {jobs.length === 0 ? (
            <div className="card">
              <p style={{ textAlign: 'center', color: '#718096' }}>
                No jobs found matching your criteria.
              </p>
            </div>
          ) : (
            jobs.slice(0, 50).map((job, idx) => (
              <div key={idx} className="job-card">
                <div className="job-title">{job.title}</div>
                <div className="job-company">{job.company}</div>
                <div className="job-details">
                  <span>📍 {job.location}</span>
                  <span>💼 {job.job_level}</span>
                  <span>🆔 {job.job_id}</span>
                </div>
                {job.skills && (
                  <div className="job-skills">
                    <strong>Skills:</strong> {job.skills}
                  </div>
                )}
              </div>
            ))
          )}
        </div>
      )}
    </div>
  );
};

export default JobSearch;
