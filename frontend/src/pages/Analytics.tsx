import React, { useState, useEffect } from 'react';
import { Bar, Line } from 'react-chartjs-2';
import { Chart as ChartJS, CategoryScale, LinearScale, BarElement, PointElement, LineElement, Title, Tooltip, Legend } from 'chart.js';
import { compareCities, getAIMLStats, getTopCompanies, getTechnicalSkills, getJobsTrend, getAITrend, getSkillsTrend, getTrendsSummary } from '../api/api';
import { CitiesComparison, AIMLStats, Company, Skill, TrendDataPoint, AITrendDataPoint, SkillTrendDataPoint, TrendSummary } from '../types';
import { useRealtime } from '../realtime/RealtimeProvider';

// Register Chart.js components
ChartJS.register(CategoryScale, LinearScale, BarElement, PointElement, LineElement, Title, Tooltip, Legend);

type TabType = 'trends' | 'technologies' | 'cities' | 'ai' | 'companies';

const Analytics: React.FC = () => {
  const [activeTab, setActiveTab] = useState<TabType>('trends');
  const [topSkills, setTopSkills] = useState<Skill[]>([]);
  const [citiesData, setCitiesData] = useState<CitiesComparison | null>(null);
  const [aiData, setAiData] = useState<AIMLStats | null>(null);
  const [companiesData, setCompaniesData] = useState<Company[]>([]);
  const [jobsTrend, setJobsTrend] = useState<TrendDataPoint[]>([]);
  const [aiTrend, setAiTrend] = useState<AITrendDataPoint[]>([]);
  const [skillsTrend, setSkillsTrend] = useState<SkillTrendDataPoint[]>([]);
  const [trendSummary, setTrendSummary] = useState<TrendSummary | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [trendDays, setTrendDays] = useState<number>(30);
  const { refreshEpoch } = useRealtime();

  // Intentionally refresh dashboards when crawler pushes a new epoch.
  /* eslint-disable react-hooks/exhaustive-deps */
  useEffect(() => {
    loadData();
  }, [refreshEpoch]);

  useEffect(() => {
    if (activeTab === 'trends') {
      loadTrendData();
    }
  }, [activeTab, trendDays, refreshEpoch]);
  /* eslint-enable react-hooks/exhaustive-deps */

  const loadData = async (): Promise<void> => {
    try {
      const [skillsRes, citiesRes, aiRes, companiesRes] = await Promise.all([
        getTechnicalSkills(30),  // Use technical skills API
        compareCities(),
        getAIMLStats(),
        getTopCompanies(15)
      ]);

      setTopSkills(skillsRes.data);
      setCitiesData(citiesRes.data);
      setAiData(aiRes.data);
      setCompaniesData(companiesRes.data);
      setLoading(false);
    } catch (error) {
      console.error('Error loading analytics:', error);
      setLoading(false);
    }
  };

  const loadTrendData = async (): Promise<void> => {
    try {
      const [jobsRes, aiRes, skillsRes, summaryRes] = await Promise.all([
        getJobsTrend(trendDays),
        getAITrend(trendDays),
        getSkillsTrend(trendDays),
        getTrendsSummary()
      ]);

      setJobsTrend(jobsRes.data);
      setAiTrend(aiRes.data);
      setSkillsTrend(skillsRes.data);
      setTrendSummary(summaryRes.data);
    } catch (error) {
      console.error('Error loading trend data:', error);
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
        Đang tải dữ liệu phân tích...
      </div>
    );
  }

  if (!topSkills.length || !citiesData || !aiData) {
    return (
      <div style={{ padding: '32px', fontFamily: 'Inter, sans-serif', color: '#6B7280' }}>
        Không có dữ liệu
      </div>
    );
  }

  const renderTrendsTab = () => {
    // Jobs Trend Chart
    const jobsTrendData = {
      labels: jobsTrend.map(d => {
        const date = new Date(d.date);
        return `${date.getDate()}/${date.getMonth() + 1}`;
      }),
      datasets: [{
        label: 'Tổng Số Việc Làm',
        data: jobsTrend.map(d => d.count),
        borderColor: '#2563EB',
        backgroundColor: 'rgba(37, 99, 235, 0.1)',
        tension: 0.4,
        fill: true,
        pointRadius: 3,
        pointHoverRadius: 5
      }]
    };

    // AI Trend Chart
    const aiTrendData = {
      labels: aiTrend.map(d => {
        const date = new Date(d.date);
        return `${date.getDate()}/${date.getMonth() + 1}`;
      }),
      datasets: [
        {
          label: 'AI/ML Jobs',
          data: aiTrend.map(d => d.ai_jobs),
          borderColor: '#10B981',
          backgroundColor: 'rgba(16, 185, 129, 0.1)',
          tension: 0.4,
          fill: true,
          yAxisID: 'y',
        },
        {
          label: 'Tỷ Lệ %',
          data: aiTrend.map(d => d.percentage),
          borderColor: '#F59E0B',
          backgroundColor: 'rgba(245, 158, 11, 0.1)',
          tension: 0.4,
          fill: false,
          yAxisID: 'y1',
        }
      ]
    };

    // Skills Trend Chart
    const skillsTrendData = {
      labels: skillsTrend.map(d => {
        const date = new Date(d.date);
        return `${date.getDate()}/${date.getMonth() + 1}`;
      }),
      datasets: [
        {
          label: 'Python',
          data: skillsTrend.map(d => d.Python),
          borderColor: '#3B82F6',
          tension: 0.4,
          fill: false,
        },
        {
          label: 'Java',
          data: skillsTrend.map(d => d.Java),
          borderColor: '#EF4444',
          tension: 0.4,
          fill: false,
        },
        {
          label: 'React',
          data: skillsTrend.map(d => d.React),
          borderColor: '#06B6D4',
          tension: 0.4,
          fill: false,
        },
        {
          label: 'Data Analysis',
          data: skillsTrend.map(d => d['Data Analysis']),
          borderColor: '#8B5CF6',
          tension: 0.4,
          fill: false,
        }
      ]
    };

    return (
      <div>
        {/* Time Range Selector */}
        <div style={{
          backgroundColor: '#FFFFFF',
          border: '1px solid #E2E8F0',
          borderRadius: '4px',
          padding: '16px',
          marginBottom: '16px',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center'
        }}>
          <div>
            <span style={{ fontSize: '13px', color: '#6B7280', marginRight: '12px' }}>
              Khoảng Thời Gian:
            </span>
            {[7, 14, 30, 60, 90].map(days => (
              <button
                key={days}
                onClick={() => setTrendDays(days)}
                style={{
                  padding: '6px 12px',
                  marginRight: '8px',
                  backgroundColor: trendDays === days ? '#1E3A5F' : '#FFFFFF',
                  color: trendDays === days ? '#FFFFFF' : '#6B7280',
                  border: '1px solid #E2E8F0',
                  borderRadius: '4px',
                  fontSize: '12px',
                  cursor: 'pointer',
                  fontWeight: trendDays === days ? '600' : '400',
                  transition: 'all 0.15s ease'
                }}
                onMouseEnter={(e) => {
                  if (trendDays !== days) {
                    e.currentTarget.style.backgroundColor = '#F8FAFC';
                    e.currentTarget.style.borderColor = '#CBD5E1';
                  }
                }}
                onMouseLeave={(e) => {
                  if (trendDays !== days) {
                    e.currentTarget.style.backgroundColor = '#FFFFFF';
                    e.currentTarget.style.borderColor = '#E2E8F0';
                  }
                }}
              >
                {days} ngày
              </button>
            ))}
          </div>
          <div style={{
            fontSize: '11px',
            color: '#F59E0B',
            backgroundColor: '#FEF3C7',
            padding: '4px 8px',
            borderRadius: '4px',
            fontWeight: '500'
          }}>
            ⚠️ Dữ liệu mô phỏng cho demo
          </div>
        </div>

        {/* Summary Cards */}
        {trendSummary && (
          <div style={{ 
            display: 'grid', 
            gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
            gap: '16px',
            marginBottom: '24px'
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
                JOB MỚI/NGÀY
              </div>
              <div style={{ 
                fontFamily: 'Noto Serif, serif',
                fontSize: '30px', 
                fontWeight: 'bold',
                color: '#10B981'
              }}>
                {trendSummary.today_new_jobs || 0}
              </div>
              <div style={{ fontSize: '11px', color: '#6B7280', marginTop: '4px' }}>
                Hôm nay: {trendSummary.today_new_jobs || 0} vs Hôm qua: {trendSummary.yesterday_new_jobs || 0} jobs mới
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
                JOB MỚI/TUẦN
              </div>
              <div style={{ 
                fontFamily: 'Noto Serif, serif',
                fontSize: '30px', 
                fontWeight: 'bold',
                color: trendSummary.weekly_growth_rate >= 0 ? '#10B981' : '#EF4444'
              }}>
                {trendSummary.weekly_growth_rate >= 0 ? '+' : ''}{trendSummary.weekly_growth_rate}%
              </div>
              <div style={{ fontSize: '11px', color: '#6B7280', marginTop: '4px' }}>
                Tuần này: {trendSummary.last_week_new_jobs} vs Tuần trước: {trendSummary.prev_week_new_jobs} jobs mới
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
                CAO NHẤT
              </div>
              <div style={{ 
                fontFamily: 'Noto Serif, serif',
                fontSize: '30px', 
                fontWeight: 'bold',
                color: '#1E3A5F'
              }}>
                {trendSummary.max_jobs.toLocaleString()}
              </div>
              <div style={{ fontSize: '11px', color: '#6B7280', marginTop: '4px' }}>
                jobs trong 30 ngày
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
                AI/ML TRUNG BÌNH
              </div>
              <div style={{ 
                fontFamily: 'Noto Serif, serif',
                fontSize: '30px', 
                fontWeight: 'bold',
                color: '#10B981'
              }}>
                {trendSummary.avg_ai.toFixed(0)}
              </div>
              <div style={{ fontSize: '11px', color: '#6B7280', marginTop: '4px' }}>
                AI/ML jobs/ngày
              </div>
            </div>
          </div>
        )}

        {/* Jobs Trend Chart */}
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
            📈 Xu Hướng Tổng Số Việc Làm
          </h2>
          <Line data={jobsTrendData} options={{ 
            responsive: true,
            plugins: {
              legend: {
                display: true,
                position: 'top' as const,
              },
              tooltip: {
                mode: 'index' as const,
                intersect: false,
              }
            },
            scales: {
              y: {
                beginAtZero: false,
                grid: {
                  color: '#F1F5F9'
                }
              },
              x: {
                grid: {
                  display: false
                }
              }
            }
          }} />
        </div>

        {/* AI/ML Trend Chart */}
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
            🤖 Tăng Trưởng AI/ML Jobs
          </h2>
          <Line data={aiTrendData} options={{ 
            responsive: true,
            interaction: {
              mode: 'index' as const,
              intersect: false,
            },
            plugins: {
              legend: {
                display: true,
                position: 'top' as const,
              }
            },
            scales: {
              y: {
                type: 'linear' as const,
                display: true,
                position: 'left' as const,
                title: {
                  display: true,
                  text: 'Số Lượng Jobs'
                },
                grid: {
                  color: '#F1F5F9'
                }
              },
              y1: {
                type: 'linear' as const,
                display: true,
                position: 'right' as const,
                title: {
                  display: true,
                  text: 'Tỷ Lệ %'
                },
                grid: {
                  drawOnChartArea: false,
                }
              },
              x: {
                grid: {
                  display: false
                }
              }
            }
          }} />
        </div>

        {/* Skills Trend Chart */}
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
            💻 Xu Hướng Nhu Cầu Công Nghệ
          </h2>
          <Line data={skillsTrendData} options={{ 
            responsive: true,
            plugins: {
              legend: {
                display: true,
                position: 'top' as const,
              },
              tooltip: {
                mode: 'index' as const,
                intersect: false,
              }
            },
            scales: {
              y: {
                beginAtZero: true,
                grid: {
                  color: '#F1F5F9'
                }
              },
              x: {
                grid: {
                  display: false
                }
              }
            }
          }} />
        </div>
      </div>
    );
  };

  const renderTechnologiesTab = () => {
    const topSkillsChartData = {
      labels: topSkills.slice(0, 20).map(s => s.skill),
      datasets: [{
        label: 'Số Lượng Việc Làm',
        data: topSkills.slice(0, 20).map(s => s.count),
        backgroundColor: '#2563EB',
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
            Top 20 Công Nghệ Phổ Biến Nhất
          </h2>
          <Bar data={topSkillsChartData} options={{ 
            responsive: true, 
            indexAxis: 'y',
            plugins: {
              legend: {
                display: false
              }
            },
            scales: {
              x: {
                grid: {
                  display: true,
                  color: '#F1F5F9'
                }
              },
              y: {
                grid: {
                  display: false
                }
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
              Bảng Xếp Hạng Công Nghệ
            </h3>
          </div>
          <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '13px' }}>
            <thead>
              <tr style={{ backgroundColor: '#F8FAFC', borderBottom: '1px solid #E2E8F0' }}>
                <th style={{ 
                  padding: '12px 16px',
                  textAlign: 'center',
                  fontWeight: '600',
                  color: '#6B7280',
                  fontSize: '11px',
                  textTransform: 'uppercase',
                  letterSpacing: '0.05em',
                  width: '80px'
                }}>RANK</th>
                <th style={{ 
                  padding: '12px 16px',
                  textAlign: 'left',
                  fontWeight: '600',
                  color: '#6B7280',
                  fontSize: '11px',
                  textTransform: 'uppercase',
                  letterSpacing: '0.05em'
                }}>CÔNG NGHỆ</th>
                <th style={{ 
                  padding: '12px 16px',
                  textAlign: 'right',
                  fontWeight: '600',
                  color: '#6B7280',
                  fontSize: '11px',
                  textTransform: 'uppercase',
                  letterSpacing: '0.05em',
                  width: '120px'
                }}>VIỆC LÀM</th>
                <th style={{ 
                  padding: '12px 16px',
                  textAlign: 'right',
                  fontWeight: '600',
                  color: '#6B7280',
                  fontSize: '11px',
                  textTransform: 'uppercase',
                  letterSpacing: '0.05em',
                  width: '100px'
                }}>TỶ LỆ</th>
              </tr>
            </thead>
            <tbody>
              {topSkills.map((skill, idx) => (
                <tr key={idx} style={{ 
                  borderBottom: '1px solid #E2E8F0', 
                  height: '48px',
                  backgroundColor: idx < 3 ? '#FEF3C7' : 'transparent'
                }}>
                  <td style={{ 
                    padding: '8px 16px', 
                    textAlign: 'center',
                    color: '#1E3A5F',
                    fontWeight: '700',
                    fontSize: '16px'
                  }}>
                    {idx === 0 && '🥇'}
                    {idx === 1 && '🥈'}
                    {idx === 2 && '🥉'}
                    {idx > 2 && (idx + 1)}
                  </td>
                  <td style={{ 
                    padding: '8px 16px', 
                    color: '#1E3A5F', 
                    fontWeight: idx < 5 ? '600' : '500',
                    fontSize: idx < 3 ? '14px' : '13px'
                  }}>
                    {skill.skill}
                    {idx < 3 && ' 🔥'}
                  </td>
                  <td style={{ 
                    padding: '8px 16px', 
                    textAlign: 'right', 
                    color: '#1E3A5F', 
                    fontWeight: '600',
                    fontSize: '14px'
                  }}>
                    {skill.count.toLocaleString()}
                  </td>
                  <td style={{ 
                    padding: '8px 16px', 
                    textAlign: 'right', 
                    color: '#6B7280',
                    fontSize: '13px'
                  }}>
                    {aiData ? ((skill.count / aiData.total_jobs) * 100).toFixed(1) : '0'}%
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    );
  };

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
            So Sánh Số Lượng Việc Làm
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
                Top Kỹ Năng Tại Hà Nội
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
                  }}>KỸ NĂNG</th>
                  <th style={{ 
                    padding: '12px 16px',
                    textAlign: 'right',
                    fontWeight: '600',
                    color: '#6B7280',
                    fontSize: '11px',
                    textTransform: 'uppercase',
                    letterSpacing: '0.05em'
                  }}>SỐ LƯỢNG</th>
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
                Top Kỹ Năng Tại HCM
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
                  }}>KỸ NĂNG</th>
                  <th style={{ 
                    padding: '12px 16px',
                    textAlign: 'right',
                    fontWeight: '600',
                    color: '#6B7280',
                    fontSize: '11px',
                    textTransform: 'uppercase',
                    letterSpacing: '0.05em'
                  }}>SỐ LƯỢNG</th>
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
              TỶ LỆ PHẦN TRĂM
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
              TỔNG SỐ VIỆC LÀM
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
            Nhu Cầu Kỹ Năng AI/ML
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
            Top 15 Công Ty
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
              Chi Tiết Công Ty
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
                }}>CÔNG TY</th>
                <th style={{ 
                  padding: '12px 16px',
                  textAlign: 'right',
                  fontWeight: '600',
                  color: '#6B7280',
                  fontSize: '11px',
                  textTransform: 'uppercase',
                  letterSpacing: '0.05em'
                }}>VIỆC LÀM</th>
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
          Bảng Phân Tích
        </h1>

        <div style={{
          display: 'flex',
          gap: '4px',
          marginBottom: '24px',
          borderBottom: '1px solid #E2E8F0',
          backgroundColor: '#FFFFFF',
          padding: '0 16px',
          borderRadius: '4px 4px 0 0',
          overflowX: 'auto'
        }}>
          <button 
            style={{
              padding: '12px 16px',
              background: 'none',
              border: 'none',
              cursor: 'pointer',
              fontSize: '13px',
              fontWeight: activeTab === 'trends' ? '600' : '500',
              color: activeTab === 'trends' ? '#1E3A5F' : '#6B7280',
              borderBottom: activeTab === 'trends' ? '2px solid #1E3A5F' : '2px solid transparent',
              marginBottom: '-1px',
              transition: 'all 0.15s ease',
              fontFamily: 'Inter, sans-serif',
              whiteSpace: 'nowrap'
            }}
            onClick={() => setActiveTab('trends')}
            onMouseEnter={(e) => {
              if (activeTab !== 'trends') {
                e.currentTarget.style.color = '#1E3A5F';
                e.currentTarget.style.backgroundColor = '#F8FAFC';
              }
            }}
            onMouseLeave={(e) => {
              if (activeTab !== 'trends') {
                e.currentTarget.style.color = '#6B7280';
                e.currentTarget.style.backgroundColor = 'transparent';
              }
            }}
          >
            📈 Xu Hướng Thị Trường
          </button>
          <button 
            style={{
              padding: '12px 16px',
              background: 'none',
              border: 'none',
              cursor: 'pointer',
              fontSize: '13px',
              fontWeight: activeTab === 'technologies' ? '600' : '500',
              color: activeTab === 'technologies' ? '#1E3A5F' : '#6B7280',
              borderBottom: activeTab === 'technologies' ? '2px solid #1E3A5F' : '2px solid transparent',
              marginBottom: '-1px',
              transition: 'all 0.15s ease',
              fontFamily: 'Inter, sans-serif',
              whiteSpace: 'nowrap'
            }}
            onClick={() => setActiveTab('technologies')}
            onMouseEnter={(e) => {
              if (activeTab !== 'technologies') {
                e.currentTarget.style.color = '#1E3A5F';
                e.currentTarget.style.backgroundColor = '#F8FAFC';
              }
            }}
            onMouseLeave={(e) => {
              if (activeTab !== 'technologies') {
                e.currentTarget.style.color = '#6B7280';
                e.currentTarget.style.backgroundColor = 'transparent';
              }
            }}
          >
            🔥 Top Công Nghệ
          </button>
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
            🏙️ So Sánh Thành Phố
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
            🤖 Phân Tích AI/ML
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
            🏢 Top Công Ty
          </button>
        </div>

        {activeTab === 'trends' && renderTrendsTab()}
        {activeTab === 'technologies' && renderTechnologiesTab()}
        {activeTab === 'cities' && renderCitiesTab()}
        {activeTab === 'ai' && renderAITab()}
        {activeTab === 'companies' && renderCompaniesTab()}
      </div>
    </div>
  );
};

export default Analytics;
