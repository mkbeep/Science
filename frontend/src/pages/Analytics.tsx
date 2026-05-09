import React, { useState, useEffect } from 'react';
import { Bar } from 'react-chartjs-2';
import { Chart as ChartJS, CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend } from 'chart.js';
import { compareCities, getAIMLStats, getTopCompanies } from '../api/api';
import { CitiesComparison, AIMLStats, Company } from '../types';

// Register Chart.js components
ChartJS.register(CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend);

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

  if (loading) {
    return (
      <div style={{ 
        display: 'flex', 
        alignItems: 'center', 
        justifyContent: 'center', 
        minHeight: '100vh',
        fontFamily: 'Inter, sans-serif',
        fontSize: '14px',
        color: '#6B7280'
      }}>
        Loading analytics data...
      </div>
    );
  }

  if (!citiesData || !aiData) {
    return (
      <div style={{ padding: '32px', fontFamily: 'Inter, sans-serif', color: '#6B7280' }}>
        No data available
      </div>
    );
  }

  const renderCitiesTab = () => {
    const cityComparisonData = {
      labels: ['Hà Nội', 'Hồ Chí Minh'],
      datasets: [{
        label: 'Job Count',
        data: [citiesData.hanoi.total_jobs, citiesData.hcm.total_jobs],
        backgroundColor: ['#1E3A5F', '#2563EB'],
      }]
    };

    return (
      <div>
        <div style={{ 
          display: 'grid', 
          gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))',
          gap: '16px',
          marginBottom: '32px'
        }}>
          <div style={{
            backgroundColor: '#FFFFFF',
            border: '1px solid #E2E8F0',
            borderRadius: '4px',
            padding: '16px',
            boxShadow: '0 1px 2px rgba(15, 23, 42, 0.04)'
          }}>
            <div style={{ 
              fontSize: '11px', 
              fontWeight: '600', 
              color: '#6B7280',
              textTransform: 'uppercase',
              letterSpacing: '0.05em',
              marginBottom: '8px'
            }}>
              HÀ NỘI JOBS
            </div>
            <div style={{ 
              fontFamily: 'Noto Serif, serif',
              fontSize: '30px', 
              fontWeight: 'bold',
              color: '#1E3A5F'
            }}>
              {citiesData.hanoi.total_jobs.toLocaleString()}
            </div>
          </div>
          <div style={{
            backgroundColor: '#FFFFFF',
            border: '1px solid #E2E8F0',
            borderRadius: '4px',
            padding: '16px',
            boxShadow: '0 1px 2px rgba(15, 23, 42, 0.04)'
          }}>
            <div style={{ 
              fontSize: '11px', 
              fontWeight: '600', 
              color: '#6B7280',
              textTransform: 'uppercase',
              letterSpacing: '0.05em',
              marginBottom: '8px'
            }}>
              HỒ CHÍ MINH JOBS
            </div>
            <div style={{ 
              fontFamily: 'Noto Serif, serif',
              fontSize: '30px', 
              fontWeight: 'bold',
              color: '#1E3A5F'
            }}>
              {citiesData.hcm.total_jobs.toLocaleString()}
            </div>
          </div>
        </div>

        <div style={{
          backgroundColor: '#FFFFFF',
          border: '1px solid #E2E8F0',
          borderRadius: '4px',
          padding: '16px',
          boxShadow: '0 1px 2px rgba(15, 23, 42, 0.04)',
          marginBottom: '16px'
        }}>
          <h2 style={{ 
            fontFamily: 'Noto Serif, serif',
            fontSize: '18px',
            fontWeight: '600',
            color: '#1E3A5F',
            marginBottom: '16px',
            paddingBottom: '12px',
            borderBottom: '1px solid #E2E8F0'
          }}>
            Job Count Comparison
          </h2>
          <Bar data={cityComparisonData} options={{ 
            responsive: true,
            plugins: {
              legend: {
                display: false
              }
            }
          }} />
        </div>

        <div style={{ 
          display: 'grid', 
          gridTemplateColumns: 'repeat(auto-fit, minmax(500px, 1fr))',
          gap: '16px'
        }}>
          <div style={{
            backgroundColor: '#FFFFFF',
            border: '1px solid #E2E8F0',
            borderRadius: '4px',
            boxShadow: '0 1px 2px rgba(15, 23, 42, 0.04)',
            overflow: 'hidden'
          }}>
            <div style={{
              padding: '12px 16px',
              borderBottom: '1px solid #E2E8F0',
              backgroundColor: '#F8FAFC'
            }}>
              <h3 style={{ 
                fontFamily: 'Noto Serif, serif',
                fontSize: '18px',
                fontWeight: '600',
                color: '#1E3A5F',
                margin: 0
              }}>
                Top Skills in Hà Nội
              </h3>
            </div>
            <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '13px' }}>
              <thead>
                <tr style={{ backgroundColor: '#F8FAFC', borderBottom: '1px solid #E2E8F0' }}>
                  <th style={{ 
                    padding: '12px 16px',
                    textAlign: 'left',
                    fontWeight: '600',
                    color: '#6B7280',
                    fontSize: '11px',
                    textTransform: 'uppercase',
                    letterSpacing: '0.05em'
                  }}>SKILL</th>
                  <th style={{ 
                    padding: '12px 16px',
                    textAlign: 'right',
                    fontWeight: '600',
                    color: '#6B7280',
                    fontSize: '11px',
                    textTransform: 'uppercase',
                    letterSpacing: '0.05em'
                  }}>COUNT</th>
                </tr>
              </thead>
              <tbody>
                {citiesData.hanoi.top_skills.map((skill, idx) => (
                  <tr key={idx} style={{ borderBottom: '1px solid #E2E8F0', height: '40px' }}>
                    <td style={{ padding: '8px 16px', color: '#1E3A5F', fontWeight: '500' }}>{skill.skill}</td>
                    <td style={{ padding: '8px 16px', textAlign: 'right', color: '#1E3A5F', fontWeight: '600' }}>{skill.count}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          <div style={{
            backgroundColor: '#FFFFFF',
            border: '1px solid #E2E8F0',
            borderRadius: '4px',
            boxShadow: '0 1px 2px rgba(15, 23, 42, 0.04)',
            overflow: 'hidden'
          }}>
            <div style={{
              padding: '12px 16px',
              borderBottom: '1px solid #E2E8F0',
              backgroundColor: '#F8FAFC'
            }}>
              <h3 style={{ 
                fontFamily: 'Noto Serif, serif',
                fontSize: '18px',
                fontWeight: '600',
                color: '#1E3A5F',
                margin: 0
              }}>
                Top Skills in HCM
              </h3>
            </div>
            <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '13px' }}>
              <thead>
                <tr style={{ backgroundColor: '#F8FAFC', borderBottom: '1px solid #E2E8F0' }}>
                  <th style={{ 
                    padding: '12px 16px',
                    textAlign: 'left',
                    fontWeight: '600',
                    color: '#6B7280',
                    fontSize: '11px',
                    textTransform: 'uppercase',
                    letterSpacing: '0.05em'
                  }}>SKILL</th>
                  <th style={{ 
                    padding: '12px 16px',
                    textAlign: 'right',
                    fontWeight: '600',
                    color: '#6B7280',
                    fontSize: '11px',
                    textTransform: 'uppercase',
                    letterSpacing: '0.05em'
                  }}>COUNT</th>
                </tr>
              </thead>
              <tbody>
                {citiesData.hcm.top_skills.map((skill, idx) => (
                  <tr key={idx} style={{ borderBottom: '1px solid #E2E8F0', height: '40px' }}>
                    <td style={{ padding: '8px 16px', color: '#1E3A5F', fontWeight: '500' }}>{skill.skill}</td>
                    <td style={{ padding: '8px 16px', textAlign: 'right', color: '#1E3A5F', fontWeight: '600' }}>{skill.count}</td>
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
        backgroundColor: '#2563EB',
      }]
    };

    return (
      <div>
        <div style={{ 
          display: 'grid', 
          gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))',
          gap: '16px',
          marginBottom: '32px'
        }}>
          <div style={{
            backgroundColor: '#FFFFFF',
            border: '1px solid #E2E8F0',
            borderRadius: '4px',
            padding: '16px',
            boxShadow: '0 1px 2px rgba(15, 23, 42, 0.04)'
          }}>
            <div style={{ 
              fontSize: '11px', 
              fontWeight: '600', 
              color: '#6B7280',
              textTransform: 'uppercase',
              letterSpacing: '0.05em',
              marginBottom: '8px'
            }}>
              AI/ML JOBS
            </div>
            <div style={{ 
              fontFamily: 'Noto Serif, serif',
              fontSize: '30px', 
              fontWeight: 'bold',
              color: '#1E3A5F'
            }}>
              {aiData.ai_jobs.toLocaleString()}
            </div>
          </div>
          <div style={{
            backgroundColor: '#FFFFFF',
            border: '1px solid #E2E8F0',
            borderRadius: '4px',
            padding: '16px',
            boxShadow: '0 1px 2px rgba(15, 23, 42, 0.04)'
          }}>
            <div style={{ 
              fontSize: '11px', 
              fontWeight: '600', 
              color: '#6B7280',
              textTransform: 'uppercase',
              letterSpacing: '0.05em',
              marginBottom: '8px'
            }}>
              PERCENTAGE
            </div>
            <div style={{ 
              fontFamily: 'Noto Serif, serif',
              fontSize: '30px', 
              fontWeight: 'bold',
              color: '#1E3A5F'
            }}>
              {aiData.percentage}%
            </div>
          </div>
          <div style={{
            backgroundColor: '#FFFFFF',
            border: '1px solid #E2E8F0',
            borderRadius: '4px',
            padding: '16px',
            boxShadow: '0 1px 2px rgba(15, 23, 42, 0.04)'
          }}>
            <div style={{ 
              fontSize: '11px', 
              fontWeight: '600', 
              color: '#6B7280',
              textTransform: 'uppercase',
              letterSpacing: '0.05em',
              marginBottom: '8px'
            }}>
              TOTAL JOBS
            </div>
            <div style={{ 
              fontFamily: 'Noto Serif, serif',
              fontSize: '30px', 
              fontWeight: 'bold',
              color: '#1E3A5F'
            }}>
              {aiData.total_jobs.toLocaleString()}
            </div>
          </div>
        </div>

        <div style={{
          backgroundColor: '#FFFFFF',
          border: '1px solid #E2E8F0',
          borderRadius: '4px',
          padding: '16px',
          boxShadow: '0 1px 2px rgba(15, 23, 42, 0.04)'
        }}>
          <h2 style={{ 
            fontFamily: 'Noto Serif, serif',
            fontSize: '18px',
            fontWeight: '600',
            color: '#1E3A5F',
            marginBottom: '16px',
            paddingBottom: '12px',
            borderBottom: '1px solid #E2E8F0'
          }}>
            AI/ML Skills Demand
          </h2>
          <Bar data={aiChartData} options={{ 
            responsive: true, 
            indexAxis: 'y',
            plugins: {
              legend: {
                display: false
              }
            }
          }} />
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
        backgroundColor: '#1E3A5F',
      }]
    };

    return (
      <div>
        <div style={{
          backgroundColor: '#FFFFFF',
          border: '1px solid #E2E8F0',
          borderRadius: '4px',
          padding: '16px',
          boxShadow: '0 1px 2px rgba(15, 23, 42, 0.04)',
          marginBottom: '16px'
        }}>
          <h2 style={{ 
            fontFamily: 'Noto Serif, serif',
            fontSize: '18px',
            fontWeight: '600',
            color: '#1E3A5F',
            marginBottom: '16px',
            paddingBottom: '12px',
            borderBottom: '1px solid #E2E8F0'
          }}>
            Top 15 Companies
          </h2>
          <Bar data={companiesChartData} options={{ 
            responsive: true, 
            indexAxis: 'y',
            plugins: {
              legend: {
                display: false
              }
            }
          }} />
        </div>

        <div style={{
          backgroundColor: '#FFFFFF',
          border: '1px solid #E2E8F0',
          borderRadius: '4px',
          boxShadow: '0 1px 2px rgba(15, 23, 42, 0.04)',
          overflow: 'hidden'
        }}>
          <div style={{
            padding: '12px 16px',
            borderBottom: '1px solid #E2E8F0',
            backgroundColor: '#F8FAFC'
          }}>
            <h3 style={{ 
              fontFamily: 'Noto Serif, serif',
              fontSize: '18px',
              fontWeight: '600',
              color: '#1E3A5F',
              margin: 0
            }}>
              Company Details
            </h3>
          </div>
          <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '13px' }}>
            <thead>
              <tr style={{ backgroundColor: '#F8FAFC', borderBottom: '1px solid #E2E8F0' }}>
                <th style={{ 
                  padding: '12px 16px',
                  textAlign: 'left',
                  fontWeight: '600',
                  color: '#6B7280',
                  fontSize: '11px',
                  textTransform: 'uppercase',
                  letterSpacing: '0.05em'
                }}>COMPANY</th>
                <th style={{ 
                  padding: '12px 16px',
                  textAlign: 'right',
                  fontWeight: '600',
                  color: '#6B7280',
                  fontSize: '11px',
                  textTransform: 'uppercase',
                  letterSpacing: '0.05em'
                }}>JOBS</th>
                <th style={{ 
                  padding: '12px 16px',
                  textAlign: 'right',
                  fontWeight: '600',
                  color: '#6B7280',
                  fontSize: '11px',
                  textTransform: 'uppercase',
                  letterSpacing: '0.05em'
                }}>%</th>
              </tr>
            </thead>
            <tbody>
              {companiesData.map((company, idx) => (
                <tr key={idx} style={{ borderBottom: '1px solid #E2E8F0', height: '40px' }}>
                  <td style={{ padding: '8px 16px', color: '#1E3A5F', fontWeight: '500' }}>{company.company}</td>
                  <td style={{ padding: '8px 16px', textAlign: 'right', color: '#1E3A5F', fontWeight: '600' }}>{company.count}</td>
                  <td style={{ padding: '8px 16px', textAlign: 'right', color: '#6B7280' }}>
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
    <div style={{ 
      backgroundColor: '#F8FAFC', 
      minHeight: '100vh',
      padding: '32px',
      fontFamily: 'Inter, sans-serif'
    }}>
      <div style={{ maxWidth: '1440px', margin: '0 auto' }}>
        <h1 style={{ 
          fontFamily: 'Noto Serif, serif',
          fontSize: '30px',
          fontWeight: 'bold',
          lineHeight: '40px',
          color: '#1E3A5F',
          marginBottom: '32px'
        }}>
          Analytics Dashboard
        </h1>

        <div style={{
          display: 'flex',
          gap: '4px',
          marginBottom: '24px',
          borderBottom: '1px solid #E2E8F0',
          backgroundColor: '#FFFFFF',
          padding: '0 16px',
          borderRadius: '4px 4px 0 0'
        }}>
          <button 
            style={{
              padding: '12px 16px',
              background: 'none',
              border: 'none',
              cursor: 'pointer',
              fontSize: '13px',
              fontWeight: activeTab === 'cities' ? '600' : '500',
              color: activeTab === 'cities' ? '#1E3A5F' : '#6B7280',
              borderBottom: activeTab === 'cities' ? '2px solid #1E3A5F' : '2px solid transparent',
              marginBottom: '-1px',
              transition: 'all 0.15s ease',
              fontFamily: 'Inter, sans-serif'
            }}
            onClick={() => setActiveTab('cities')}
            onMouseEnter={(e) => {
              if (activeTab !== 'cities') {
                e.currentTarget.style.color = '#1E3A5F';
                e.currentTarget.style.backgroundColor = '#F8FAFC';
              }
            }}
            onMouseLeave={(e) => {
              if (activeTab !== 'cities') {
                e.currentTarget.style.color = '#6B7280';
                e.currentTarget.style.backgroundColor = 'transparent';
              }
            }}
          >
            🏙️ Cities Comparison
          </button>
          <button 
            style={{
              padding: '12px 16px',
              background: 'none',
              border: 'none',
              cursor: 'pointer',
              fontSize: '13px',
              fontWeight: activeTab === 'ai' ? '600' : '500',
              color: activeTab === 'ai' ? '#1E3A5F' : '#6B7280',
              borderBottom: activeTab === 'ai' ? '2px solid #1E3A5F' : '2px solid transparent',
              marginBottom: '-1px',
              transition: 'all 0.15s ease',
              fontFamily: 'Inter, sans-serif'
            }}
            onClick={() => setActiveTab('ai')}
            onMouseEnter={(e) => {
              if (activeTab !== 'ai') {
                e.currentTarget.style.color = '#1E3A5F';
                e.currentTarget.style.backgroundColor = '#F8FAFC';
              }
            }}
            onMouseLeave={(e) => {
              if (activeTab !== 'ai') {
                e.currentTarget.style.color = '#6B7280';
                e.currentTarget.style.backgroundColor = 'transparent';
              }
            }}
          >
            🤖 AI/ML Analysis
          </button>
          <button 
            style={{
              padding: '12px 16px',
              background: 'none',
              border: 'none',
              cursor: 'pointer',
              fontSize: '13px',
              fontWeight: activeTab === 'companies' ? '600' : '500',
              color: activeTab === 'companies' ? '#1E3A5F' : '#6B7280',
              borderBottom: activeTab === 'companies' ? '2px solid #1E3A5F' : '2px solid transparent',
              marginBottom: '-1px',
              transition: 'all 0.15s ease',
              fontFamily: 'Inter, sans-serif'
            }}
            onClick={() => setActiveTab('companies')}
            onMouseEnter={(e) => {
              if (activeTab !== 'companies') {
                e.currentTarget.style.color = '#1E3A5F';
                e.currentTarget.style.backgroundColor = '#F8FAFC';
              }
            }}
            onMouseLeave={(e) => {
              if (activeTab !== 'companies') {
                e.currentTarget.style.color = '#6B7280';
                e.currentTarget.style.backgroundColor = 'transparent';
              }
            }}
          >
            🏢 Top Companies
          </button>
        </div>

        {activeTab === 'cities' && renderCitiesTab()}
        {activeTab === 'ai' && renderAITab()}
        {activeTab === 'companies' && renderCompaniesTab()}
      </div>
    </div>
  );
};

export default Analytics;
