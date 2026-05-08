import React, { useState, useEffect } from 'react';
import { Bar } from 'react-chartjs-2';
import { compareCities, getAIMLStats, getTopCompanies } from '../api/api';
import { CitiesComparison, AIMLStats, Company } from '../types';

type TabType = 'cities' | 'ai' | 'companies';

const Analytics: React.FC = () => {
  const [activeTab, setActiveTab] = useState<TabType>('cities');
  const [citiesData, setCitiesData] = useState<CitiesComparison | null>(null);
  const [aiData, setAiData] = useState<AIMLStats | null>(null);
  const [companiesData, setCompaniesData] = useState<Company[]>([]);
  const [loading, setLoading] = useState<boolean>(true);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async (): Promise<void> => {
    try {
      const [citiesRes, aiRes, companiesRes] = await Promise.all([
        compareCities(),
        getAIMLStats(),
        getTopCompanies(15)
      ]);

      setCitiesData(citiesRes.data);
      setAiData(aiRes.data);
      setCompaniesData(companiesRes.data);
      setLoading(false);
    } catch (error) {
      console.error('Error loading analytics:', error);
      setLoading(false);
    }
  };

  if (loading) return <div className="loading">Loading...</div>;
  if (!citiesData || !aiData) return <div className="loading">No data available</div>;

  const renderCitiesTab = () => {
    const cityComparisonData = {
      labels: ['Hà Nội', 'Hồ Chí Minh'],
      datasets: [{
        label: 'Job Count',
        data: [citiesData.hanoi.total_jobs, citiesData.hcm.total_jobs],
        backgroundColor: ['rgba(255, 107, 107, 0.8)', 'rgba(78, 205, 196, 0.8)'],
      }]
    };

    return (
      <div>
        <div className="stats-grid">
          <div className="stat-card">
            <div className="stat-label">Hà Nội Jobs</div>
            <div className="stat-value">{citiesData.hanoi.total_jobs}</div>
          </div>
          <div className="stat-card">
            <div className="stat-label">HCM Jobs</div>
            <div className="stat-value">{citiesData.hcm.total_jobs}</div>
          </div>
        </div>

        <div className="chart-container">
          <h2>Job Count Comparison</h2>
          <Bar data={cityComparisonData} options={{ responsive: true }} />
        </div>

        <div className="charts-grid">
          <div className="card">
            <h3>Top Skills in Hà Nội</h3>
            <table style={{ width: '100%', marginTop: '1rem' }}>
              <thead>
                <tr style={{ borderBottom: '2px solid #e2e8f0' }}>
                  <th style={{ textAlign: 'left', padding: '0.5rem' }}>Skill</th>
                  <th style={{ textAlign: 'right', padding: '0.5rem' }}>Count</th>
                </tr>
              </thead>
              <tbody>
                {citiesData.hanoi.top_skills.map((skill, idx) => (
                  <tr key={idx} style={{ borderBottom: '1px solid #e2e8f0' }}>
                    <td style={{ padding: '0.5rem' }}>{skill.skill}</td>
                    <td style={{ textAlign: 'right', padding: '0.5rem' }}>{skill.count}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          <div className="card">
            <h3>Top Skills in HCM</h3>
            <table style={{ width: '100%', marginTop: '1rem' }}>
              <thead>
                <tr style={{ borderBottom: '2px solid #e2e8f0' }}>
                  <th style={{ textAlign: 'left', padding: '0.5rem' }}>Skill</th>
                  <th style={{ textAlign: 'right', padding: '0.5rem' }}>Count</th>
                </tr>
              </thead>
              <tbody>
                {citiesData.hcm.top_skills.map((skill, idx) => (
                  <tr key={idx} style={{ borderBottom: '1px solid #e2e8f0' }}>
                    <td style={{ padding: '0.5rem' }}>{skill.skill}</td>
                    <td style={{ textAlign: 'right', padding: '0.5rem' }}>{skill.count}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    );
  };

  const renderAITab = () => {
    const aiChartData = {
      labels: aiData.skills.map(s => s.skill),
      datasets: [{
        label: 'Job Mentions',
        data: aiData.skills.map(s => s.count),
        backgroundColor: 'rgba(156, 39, 176, 0.8)',
      }]
    };

    return (
      <div>
        <div className="stats-grid">
          <div className="stat-card">
            <div className="stat-label">AI/ML Jobs</div>
            <div className="stat-value">{aiData.ai_jobs}</div>
          </div>
          <div className="stat-card">
            <div className="stat-label">Percentage</div>
            <div className="stat-value">{aiData.percentage}%</div>
          </div>
          <div className="stat-card">
            <div className="stat-label">Total Jobs</div>
            <div className="stat-value">{aiData.total_jobs}</div>
          </div>
        </div>

        <div className="chart-container">
          <h2>AI/ML Skills Demand</h2>
          <Bar data={aiChartData} options={{ responsive: true, indexAxis: 'y' }} />
        </div>
      </div>
    );
  };

  const renderCompaniesTab = () => {
    const companiesChartData = {
      labels: companiesData.map(c => c.company.substring(0, 30)),
      datasets: [{
        label: 'Job Count',
        data: companiesData.map(c => c.count),
        backgroundColor: 'rgba(255, 152, 0, 0.8)',
      }]
    };

    return (
      <div>
        <div className="chart-container">
          <h2>Top 15 Companies</h2>
          <Bar data={companiesChartData} options={{ responsive: true, indexAxis: 'y' }} />
        </div>

        <div className="card">
          <h3>Company Details</h3>
          <table style={{ width: '100%', marginTop: '1rem' }}>
            <thead>
              <tr style={{ borderBottom: '2px solid #e2e8f0' }}>
                <th style={{ textAlign: 'left', padding: '0.5rem' }}>Company</th>
                <th style={{ textAlign: 'right', padding: '0.5rem' }}>Jobs</th>
                <th style={{ textAlign: 'right', padding: '0.5rem' }}>%</th>
              </tr>
            </thead>
            <tbody>
              {companiesData.map((company, idx) => (
                <tr key={idx} style={{ borderBottom: '1px solid #e2e8f0' }}>
                  <td style={{ padding: '0.5rem' }}>{company.company}</td>
                  <td style={{ textAlign: 'right', padding: '0.5rem' }}>{company.count}</td>
                  <td style={{ textAlign: 'right', padding: '0.5rem' }}>
                    {((company.count / aiData.total_jobs) * 100).toFixed(2)}%
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    );
  };

  return (
    <div>
      <h1 style={{ marginBottom: '2rem', color: '#2d3748' }}>📊 Analytics</h1>

      <div className="tabs">
        <button 
          className={`tab ${activeTab === 'cities' ? 'active' : ''}`} 
          onClick={() => setActiveTab('cities')}
        >
          🏙️ Cities
        </button>
        <button 
          className={`tab ${activeTab === 'ai' ? 'active' : ''}`} 
          onClick={() => setActiveTab('ai')}
        >
          🤖 AI/ML
        </button>
        <button 
          className={`tab ${activeTab === 'companies' ? 'active' : ''}`} 
          onClick={() => setActiveTab('companies')}
        >
          🏢 Companies
        </button>
      </div>

      {activeTab === 'cities' && renderCitiesTab()}
      {activeTab === 'ai' && renderAITab()}
      {activeTab === 'companies' && renderCompaniesTab()}
    </div>
  );
};

export default Analytics;
