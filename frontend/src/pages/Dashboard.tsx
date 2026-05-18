import React, { useState, useEffect, useCallback } from 'react';
import { getStats, getTopSkills, getTopLocations, getJobLevels, getJobs } from '../api/api';
import { Stats, Skill, Location, JobLevel } from '../types';
import { useRealtime } from '../realtime/RealtimeProvider';

const Dashboard: React.FC = () => {
  const [stats, setStats] = useState<Stats | null>(null);
  const [topSkills, setTopSkills] = useState<Skill[]>([]);
  const [topLocations, setTopLocations] = useState<Location[]>([]);
  const [jobLevels, setJobLevels] = useState<JobLevel[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [exporting, setExporting] = useState<boolean>(false);
  const { refreshEpoch } = useRealtime();

  const loadData = useCallback(async (): Promise<void> => {
    try {
      setLoading(true);
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
  }, []);

  useEffect(() => {
    void loadData();
  }, [refreshEpoch, loadData]);

  const exportToCSV = useCallback(async (): Promise<void> => {
    try {
      setExporting(true);
      
      // Fetch all jobs data
      const response = await getJobs(1, 10000); // Get large batch
      const jobs = response.data.jobs;
      
      if (jobs.length === 0) {
        alert('Không có dữ liệu để xuất');
        setExporting(false);
        return;
      }
      
      // Convert to CSV
      const headers = Object.keys(jobs[0]);
      const csvContent = [
        headers.join(','),
        ...jobs.map(job => 
          headers.map(header => {
            const value = job[header as keyof typeof job];
            // Escape commas and quotes in values
            const stringValue = String(value || '');
            if (stringValue.includes(',') || stringValue.includes('"') || stringValue.includes('\n')) {
              return `"${stringValue.replace(/"/g, '""')}"`;
            }
            return stringValue;
          }).join(',')
        )
      ].join('\n');
      
      // Create download link
      const blob = new Blob(['\uFEFF' + csvContent], { type: 'text/csv;charset=utf-8;' });
      const link = document.createElement('a');
      const url = URL.createObjectURL(blob);
      link.setAttribute('href', url);
      link.setAttribute('download', `it_jobs_data_${new Date().toISOString().split('T')[0]}.csv`);
      link.style.visibility = 'hidden';
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      
      setExporting(false);
    } catch (error) {
      console.error('Error exporting data:', error);
      alert('Lỗi khi xuất dữ liệu');
      setExporting(false);
    }
  }, []);

  const exportToJSON = useCallback(async (): Promise<void> => {
    try {
      setExporting(true);
      
      // Fetch all jobs data
      const response = await getJobs(1, 10000);
      const jobs = response.data.jobs;
      
      if (jobs.length === 0) {
        alert('Không có dữ liệu để xuất');
        setExporting(false);
        return;
      }
      
      // Create comprehensive export with stats
      const exportData = {
        exported_at: new Date().toISOString(),
        stats: stats,
        top_skills: topSkills,
        top_locations: topLocations,
        job_levels: jobLevels,
        jobs: jobs
      };
      
      // Create download link
      const blob = new Blob([JSON.stringify(exportData, null, 2)], { type: 'application/json' });
      const link = document.createElement('a');
      const url = URL.createObjectURL(blob);
      link.setAttribute('href', url);
      link.setAttribute('download', `it_jobs_data_${new Date().toISOString().split('T')[0]}.json`);
      link.style.visibility = 'hidden';
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      
      setExporting(false);
    } catch (error) {
      console.error('Error exporting data:', error);
      alert('Lỗi khi xuất dữ liệu');
      setExporting(false);
    }
  }, [stats, topSkills, topLocations, jobLevels]);

  const handleExportClick = useCallback((): void => {
    const choice = window.confirm('Chọn OK để xuất CSV, Cancel để xuất JSON');
    if (choice) {
      void exportToCSV();
    } else {
      void exportToJSON();
    }
  }, [exportToCSV, exportToJSON]);

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
        Đang tải dữ liệu...
      </div>
    );
  }

  if (!stats) return (
    <div style={{ padding: '32px', fontFamily: 'Inter, sans-serif', color: '#6B7280' }}>
      Không có dữ liệu
    </div>
  );

  const maxLocationCount = Math.max(...topLocations.map(l => l.count));
  const maxSkillCount = Math.max(...topSkills.map(s => s.count));
  const totalJobs = jobLevels.reduce((sum, level) => sum + level.count, 0);

  return (
    <div style={{ 
      backgroundColor: '#F8FAFC', 
      minHeight: '100vh',
      padding: '32px',
      fontFamily: 'Inter, sans-serif'
    }}>
      <div style={{ maxWidth: '1440px', margin: '0 auto' }}>
        {/* Page Header */}
        <div style={{ marginBottom: '32px' }}>
          <div style={{ 
            display: 'flex', 
            justifyContent: 'space-between', 
            alignItems: 'flex-start',
            marginBottom: '8px'
          }}>
            <h1 style={{ 
              fontFamily: 'Noto Serif, serif',
              fontSize: '30px',
              fontWeight: 'bold',
              lineHeight: '40px',
              color: '#1E3A5F',
              margin: 0
            }}>
              IT Jobs Market Dashboard
            </h1>
            <div style={{ display: 'flex', gap: '8px' }}>
              <button 
                type="button"
                style={{
                  backgroundColor: '#FFFFFF',
                  border: '1px solid #CBD5E1',
                  borderRadius: '4px',
                  padding: '8px 14px',
                  fontSize: '13px',
                  fontWeight: '500',
                  color: exporting ? '#9CA3AF' : '#1E3A5F',
                  cursor: exporting ? 'not-allowed' : 'pointer',
                  height: '36px',
                  opacity: exporting ? 0.6 : 1
                }}
                onClick={handleExportClick}
                disabled={exporting}
              >
                {exporting ? 'Đang Xuất...' : 'Xuất Dữ Liệu'}
              </button>
              <button
                type="button"
                style={{
                  backgroundColor: '#1E3A5F',
                  border: 'none',
                  borderRadius: '4px',
                  padding: '8px 14px',
                  fontSize: '13px',
                  fontWeight: '500',
                  color: '#FFFFFF',
                  cursor: 'pointer',
                  height: '36px'
                }}
                onClick={() => void loadData()}
              >
                Làm Mới
              </button>
            </div>
          </div>
          <p style={{ 
            fontFamily: 'Inter, sans-serif',
            fontSize: '14px',
            lineHeight: '22px',
            color: '#6B7280',
            margin: 0
          }}>
            Phân tích thời gian thực về thị trường tuyển dụng IT Việt Nam
          </p>
        </div>

        {/* Stats Grid */}
        <div style={{ 
          display: 'grid', 
          gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))',
          gap: '16px',
          marginBottom: '32px'
        }}>
          {/* Total Jobs */}
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
              color: '#1E3A5F',
              marginBottom: '4px'
            }}>
              {stats.total_jobs.toLocaleString()}
            </div>
            <div style={{
              display: 'inline-block',
              backgroundColor: 'rgba(22, 163, 74, 0.1)',
              color: '#16A34A',
              fontSize: '12px',
              fontWeight: '600',
              padding: '4px 10px',
              borderRadius: '2px'
            }}>
              Đang Hoạt Động
            </div>
          </div>

          {/* Total Companies */}
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
              TỔNG SỐ CÔNG TY
            </div>
            <div style={{ 
              fontFamily: 'Noto Serif, serif',
              fontSize: '30px', 
              fontWeight: 'bold',
              color: '#1E3A5F',
              marginBottom: '4px'
            }}>
              {stats.total_companies.toLocaleString()}
            </div>
            <div style={{
              display: 'inline-block',
              backgroundColor: 'rgba(37, 99, 235, 0.1)',
              color: '#2563EB',
              fontSize: '12px',
              fontWeight: '600',
              padding: '4px 10px',
              borderRadius: '2px'
            }}>
              Đã Xác Minh
            </div>
          </div>

          {/* Total Locations */}
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
              ĐỊA ĐIỂM
            </div>
            <div style={{ 
              fontFamily: 'Noto Serif, serif',
              fontSize: '30px', 
              fontWeight: 'bold',
              color: '#1E3A5F',
              marginBottom: '4px'
            }}>
              {stats.total_locations}
            </div>
            <div style={{
              display: 'inline-block',
              backgroundColor: 'rgba(107, 114, 128, 0.1)',
              color: '#6B7280',
              fontSize: '12px',
              fontWeight: '600',
              padding: '4px 10px',
              borderRadius: '2px'
            }}>
              Toàn Quốc
            </div>
          </div>

          {/* Unique Skills */}
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
              KỸ NĂNG ĐỘC NHẤT
            </div>
            <div style={{ 
              fontFamily: 'Noto Serif, serif',
              fontSize: '30px', 
              fontWeight: 'bold',
              color: '#1E3A5F',
              marginBottom: '4px'
            }}>
              {stats.unique_skills.toLocaleString()}
            </div>
            <div style={{
              display: 'inline-block',
              backgroundColor: 'rgba(202, 138, 4, 0.1)',
              color: '#CA8A04',
              fontSize: '12px',
              fontWeight: '600',
              padding: '4px 10px',
              borderRadius: '2px'
            }}>
              Đang Theo Dõi
            </div>
          </div>
        </div>

        {/* Main Content Grid */}
        <div style={{ 
          display: 'grid', 
          gridTemplateColumns: 'repeat(12, 1fr)',
          gap: '16px',
          marginBottom: '32px'
        }}>
          {/* Top Skills - 8 columns */}
          <div style={{
            gridColumn: 'span 8',
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
                Top 15 Kỹ Năng Được Yêu Cầu Nhiều Nhất
              </h3>
            </div>
            <div style={{ padding: '16px' }}>
              <div style={{ 
                display: 'flex', 
                flexDirection: 'column',
                gap: '10px'
              }}>
                {topSkills.map((skill, idx) => {
                  const widthPercent = (skill.count / maxSkillCount) * 100;
                  const colors = [
                    '#2563EB', '#3B82F6', '#60A5FA', '#93C5FD', '#BFDBFE',
                    '#1E40AF', '#1E3A8A', '#312E81', '#4C1D95', '#6B21A8',
                    '#7C3AED', '#8B5CF6', '#A78BFA', '#C4B5FD', '#DDD6FE'
                  ];
                  return (
                    <div key={idx} style={{ 
                      display: 'flex',
                      alignItems: 'center',
                      gap: '12px'
                    }}>
                      <div style={{
                        minWidth: '30px',
                        textAlign: 'right',
                        fontSize: '12px',
                        fontWeight: '600',
                        color: '#6B7280'
                      }}>
                        #{idx + 1}
                      </div>
                      <div style={{
                        minWidth: '140px',
                        fontSize: '13px',
                        fontWeight: '500',
                        color: '#1E3A5F',
                        overflow: 'hidden',
                        textOverflow: 'ellipsis',
                        whiteSpace: 'nowrap'
                      }}
                      title={skill.skill}
                      >
                        {skill.skill}
                      </div>
                      <div style={{ flex: 1, position: 'relative' }}>
                        <div style={{
                          width: '100%',
                          height: '24px',
                          backgroundColor: '#F1F5F9',
                          borderRadius: '4px',
                          overflow: 'hidden',
                          position: 'relative'
                        }}>
                          <div 
                            style={{
                              width: `${widthPercent}%`,
                              height: '100%',
                              backgroundColor: colors[idx % colors.length],
                              transition: 'width 0.3s ease',
                              display: 'flex',
                              alignItems: 'center',
                              justifyContent: 'flex-end',
                              paddingRight: '8px'
                            }}
                          >
                            <span style={{
                              fontSize: '11px',
                              fontWeight: '600',
                              color: widthPercent > 30 ? '#FFFFFF' : 'transparent'
                            }}>
                              {skill.count}
                            </span>
                          </div>
                        </div>
                      </div>
                      <div style={{
                        minWidth: '60px',
                        textAlign: 'right',
                        fontSize: '13px',
                        fontWeight: '600',
                        color: '#1E3A5F'
                      }}>
                        {skill.count.toLocaleString()}
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          </div>

          {/* Job Levels - 4 columns */}
          <div style={{
            gridColumn: 'span 4',
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
                Phân Bổ Cấp Bậc Công Việc
              </h3>
            </div>
            <div style={{ padding: '24px 16px' }}>
              {jobLevels.map((level, idx) => {
                const percentage = ((level.count / totalJobs) * 100).toFixed(1);
                const colors = ['#1E3A5F', '#2563EB', '#6B7280', '#CA8A04'];
                return (
                  <div key={idx} style={{ marginBottom: '16px' }}>
                    <div style={{ 
                      display: 'flex', 
                      justifyContent: 'space-between',
                      marginBottom: '6px'
                    }}>
                      <span style={{ 
                        fontSize: '13px',
                        color: '#1E3A5F',
                        fontWeight: '500'
                      }}>
                        {level.level}
                      </span>
                      <span style={{ 
                        fontSize: '13px',
                        color: '#6B7280',
                        fontWeight: '600'
                      }}>
                        {percentage}%
                      </span>
                    </div>
                    <div style={{
                      width: '100%',
                      height: '8px',
                      backgroundColor: '#F1F5F9',
                      borderRadius: '2px',
                      overflow: 'hidden'
                    }}>
                      <div style={{
                        width: `${percentage}%`,
                        height: '100%',
                        backgroundColor: colors[idx % colors.length],
                        transition: 'width 0.3s'
                      }} />
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        </div>

        {/* Top Locations Table */}
        <div style={{
          backgroundColor: '#FFFFFF',
          border: '1px solid #E2E8F0',
          borderRadius: '4px',
          boxShadow: '0 1px 2px rgba(15, 23, 42, 0.04)',
          overflow: 'hidden',
          marginBottom: '32px'
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
              Top 10 Địa Điểm
            </h3>
          </div>
          <div style={{ padding: '0' }}>
            <table style={{ 
              width: '100%', 
              borderCollapse: 'collapse',
              fontSize: '13px'
            }}>
              <thead>
                <tr style={{ 
                  backgroundColor: '#F8FAFC',
                  borderBottom: '1px solid #E2E8F0'
                }}>
                  <th style={{ 
                    padding: '12px 16px',
                    textAlign: 'left',
                    fontWeight: '600',
                    color: '#6B7280',
                    fontSize: '11px',
                    textTransform: 'uppercase',
                    letterSpacing: '0.05em'
                  }}>
                    ĐỊA ĐIỂM
                  </th>
                  <th style={{ 
                    padding: '12px 16px',
                    textAlign: 'right',
                    fontWeight: '600',
                    color: '#6B7280',
                    fontSize: '11px',
                    textTransform: 'uppercase',
                    letterSpacing: '0.05em'
                  }}>
                    SỐ LƯỢNG VIỆC
                  </th>
                  <th style={{ 
                    padding: '12px 16px',
                    textAlign: 'left',
                    fontWeight: '600',
                    color: '#6B7280',
                    fontSize: '11px',
                    textTransform: 'uppercase',
                    letterSpacing: '0.05em',
                    width: '50%'
                  }}>
                    PHÂN BỐ
                  </th>
                </tr>
              </thead>
              <tbody>
                {topLocations.map((location, idx) => {
                  const widthPercent = (location.count / maxLocationCount) * 100;
                  return (
                    <tr key={idx} style={{ 
                      borderBottom: '1px solid #E2E8F0',
                      height: '40px'
                    }}>
                      <td style={{ 
                        padding: '8px 16px',
                        color: '#1E3A5F',
                        fontWeight: '500'
                      }}>
                        {location.location}
                      </td>
                      <td style={{ 
                        padding: '8px 16px',
                        textAlign: 'right',
                        color: '#1E3A5F',
                        fontWeight: '600'
                      }}>
                        {location.count.toLocaleString()}
                      </td>
                      <td style={{ padding: '8px 16px' }}>
                        <div style={{
                          width: '100%',
                          height: '8px',
                          backgroundColor: '#F1F5F9',
                          borderRadius: '2px',
                          overflow: 'hidden'
                        }}>
                          <div style={{
                            width: `${widthPercent}%`,
                            height: '100%',
                            backgroundColor: '#1E3A5F',
                            transition: 'width 0.3s'
                          }} />
                        </div>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </div>

        {/* Info Banner */}
        <div style={{
          backgroundColor: '#EFF6FF',
          border: '1px solid #BFDBFE',
          borderRadius: '4px',
          padding: '16px',
          display: 'flex',
          alignItems: 'center',
          gap: '12px'
        }}>
          <div style={{
            width: '32px',
            height: '32px',
            backgroundColor: '#2563EB',
            borderRadius: '4px',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            color: '#FFFFFF',
            fontSize: '18px',
            fontWeight: 'bold',
            flexShrink: 0
          }}>
            i
          </div>
          <div>
            <div style={{ 
              fontFamily: 'Noto Serif, serif',
              fontSize: '16px',
              fontWeight: '600',
              color: '#1E3A5F',
              marginBottom: '4px'
            }}>
              Dữ Liệu Được Cập Nhật Hàng Ngày
            </div>
            <div style={{ 
              fontSize: '13px',
              color: '#6B7280',
              lineHeight: '20px'
            }}>
              Dashboard này tổng hợp các tin tuyển dụng từ các nền tảng tuyển dụng IT lớn tại Việt Nam. 
              Dữ liệu được làm mới mỗi 24 giờ để đảm bảo độ chính xác và phù hợp.
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
