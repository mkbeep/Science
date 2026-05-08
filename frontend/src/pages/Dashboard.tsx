import React, { useState, useEffect } from 'react';
import { Bar, Pie } from 'react-chartjs-2';
import { Chart as ChartJS, CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend, ArcElement } from 'chart.js';
import { getStats, getTopSkills, getTopLocations, getJobLevels } from '../api/api';
import { Stats, Skill, Location, JobLevel } from '../types';

ChartJS.register(CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend, ArcElement);

const Dashboard: React.FC = () => {
  const [stats, setStats] = useState<Stats | null>(null);
  const [topSkills, setTopSkills] = useState<Skill[]>([]);
  const [topLocations, setTopLocations] = useState<Location[]>([]);
  const [jobLevels, setJobLevels] = useState<JobLevel[]>([]);
  const [loading, setLoading] = useState<boolean>(true);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async (): Promise<void> => {
    try {
      const [statsRes, skillsRes, locsRes, levelsRes] = await Promise.all([
        getStats(),
        getTopSkills(15),
        getTopLocations(10),
        getJobLevels()
      ]);

      setStats(statsRes.data);
      setTopSkills(skillsRes.data);
      setTopLocations(locsRes.data);
      setJobLevels(levelsRes.data);
      setLoading(false);
    } catch (error) {
      console.error('Error loading data:', error);
      setLoading(false);
    }
  };

  if (loading) return <div className="loading">Loading...</div>;
  if (!stats) return <div className="loading">No data available</div>;

  const skillsChartData = {
    labels: topSkills.map(s => s.skill),
    datasets: [{
      label: 'Demand Count',
      data: topSkills.map(s => s.count),
      backgroundColor: 'rgba(102, 126, 234, 0.8)',
    }]
  };

  const locationsChartData = {
    labels: topLocations.map(l => l.location),
    datasets: [{
      label: 'Job Count',
      data: topLocations.map(l => l.count),
      backgroundColor: 'rgba(118, 75, 162, 0.8)',
    }]
  };

  const levelsChartData = {
    labels: jobLevels.map(l => l.level),
    datasets: [{
      data: jobLevels.map(l => l.count),
      backgroundColor: [
        'rgba(255, 99, 132, 0.8)',
        'rgba(54, 162, 235, 0.8)',
        'rgba(255, 206, 86, 0.8)',
        'rgba(75, 192, 192, 0.8)',
        'rgba(153, 102, 255, 0.8)',
      ],
    }]
  };

  return (
    <div>
      <h1 style={{ marginBottom: '2rem', color: '#2d3748' }}>📊 Dashboard Overview</h1>

      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-label">Total Jobs</div>
          <div className="stat-value">{stats.total_jobs.toLocaleString()}</div>
        </div>
        <div className="stat-card">
          <div className="stat-label">Companies</div>
          <div className="stat-value">{stats.total_companies.toLocaleString()}</div>
        </div>
        <div className="stat-card">
          <div className="stat-label">Locations</div>
          <div className="stat-value">{stats.total_locations}</div>
        </div>
        <div className="stat-card">
          <div className="stat-label">Unique Skills</div>
          <div className="stat-value">{stats.unique_skills.toLocaleString()}</div>
        </div>
      </div>

      <div className="charts-grid">
        <div className="chart-container">
          <h2>🔥 Top 15 Skills</h2>
          <Bar data={skillsChartData} options={{ responsive: true, maintainAspectRatio: true }} />
        </div>

        <div className="chart-container">
          <h2>📍 Top 10 Locations</h2>
          <Bar data={locationsChartData} options={{ responsive: true, indexAxis: 'y' }} />
        </div>
      </div>

      <div className="chart-container">
        <h2>💼 Job Level Distribution</h2>
        <div style={{ maxWidth: '500px', margin: '0 auto' }}>
          <Pie data={levelsChartData} />
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
