import React, { useState, useEffect } from 'react';
import { searchJobs, getFilters } from '../api/api';
import { Job, Filters, SearchParams } from '../types';
import { useRealtime } from '../realtime/RealtimeProvider';

const JobSearch: React.FC = () => {
  const [filters, setFilters] = useState<SearchParams>({ skill: '', location: '', level: '' });
  const [availableFilters, setAvailableFilters] = useState<Filters>({ locations: [], levels: [] });
  const [jobs, setJobs] = useState<Job[]>([]); // Khởi tạo với array rỗng thay vì undefined
  const [loading, setLoading] = useState<boolean>(false);
  const [searched, setSearched] = useState<boolean>(false);
  const { refreshEpoch } = useRealtime();

  useEffect(() => {
    loadFilters();
  }, [refreshEpoch]);

  const loadFilters = async (): Promise<void> => {
    try {
      const res = await getFilters();
      setAvailableFilters(res.data);
    } catch (error) {
      console.error('Error loading filters:', error);
    }
  };

  const handleSearch = async (): Promise<void> => {
    console.log('[JobSearch] Starting search...');
    setLoading(true);
    setSearched(true);
    
    try {
      const params: SearchParams = {};
      if (filters.skill) params.skill = filters.skill;
      if (filters.location) params.location = filters.location;
      if (filters.level) params.level = filters.level;

      console.log('[JobSearch] Searching with params:', params);
      const res = await searchJobs(params);
      console.log('[JobSearch] Raw response:', res);
      console.log('[JobSearch] Response data:', res.data);
      console.log('[JobSearch] Jobs array:', res.data.jobs);
      console.log('[JobSearch] Jobs is array?', Array.isArray(res.data.jobs));
      console.log('[JobSearch] Jobs length:', res.data.jobs?.length);
      
      // Đảm bảo jobs luôn là array
      if (res && res.data && Array.isArray(res.data.jobs)) {
        console.log('[JobSearch] Setting jobs state with', res.data.jobs.length, 'items');
        setJobs(res.data.jobs);
        console.log('[JobSearch] Jobs state updated');
      } else {
        console.warn('[JobSearch] Invalid response format:', res);
        setJobs([]);
      }
    } catch (error) {
      console.error('[JobSearch] Error searching jobs:', error);
      setJobs([]);
    } finally {
      setLoading(false);
      console.log('[JobSearch] Search completed');
    }
  };

  const handleFilterChange = (key: keyof SearchParams, value: string): void => {
    setFilters({ ...filters, [key]: value });
  };

  const handleKeyPress = (e: React.KeyboardEvent): void => {
    if (e.key === 'Enter') {
      handleSearch();
    }
  };

  // Debug logging
  console.log('[JobSearch] Render - loading:', loading, 'searched:', searched, 'jobs:', jobs?.length);

  return (
    <div style={{ 
      backgroundColor: '#F8FAFC', 
      minHeight: '100vh',
      padding: '32px',
      fontFamily: 'Inter, sans-serif'
    }}>
      <div style={{ maxWidth: '1440px', margin: '0 auto' }}>
        {/* Page Header */}
        <h1 style={{ 
          fontFamily: 'Noto Serif, serif',
          fontSize: '30px',
          fontWeight: 'bold',
          lineHeight: '40px',
          color: '#1E3A5F',
          marginBottom: '8px'
        }}>
          Tìm Kiếm Việc Làm
        </h1>
        <p style={{ 
          fontFamily: 'Inter, sans-serif',
          fontSize: '14px',
          lineHeight: '22px',
          color: '#6B7280',
          margin: '0 0 32px 0'
        }}>
          Tìm kiếm công việc IT phù hợp với kỹ năng và vị trí của bạn
        </p>

        {/* Search Container */}
        <div style={{
          backgroundColor: '#FFFFFF',
          border: '1px solid #E2E8F0',
          borderRadius: '4px',
          padding: '24px',
          boxShadow: '0 1px 2px rgba(15, 23, 42, 0.04)',
          marginBottom: '32px'
        }}>
          <div style={{ 
            display: 'grid', 
            gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))',
            gap: '16px',
            marginBottom: '16px'
          }}>
            <div>
              <label style={{
                display: 'block',
                fontSize: '13px',
                fontWeight: '500',
                color: '#1E3A5F',
                marginBottom: '6px'
              }}>
                Kỹ Năng
              </label>
              <input
                type="text"
                placeholder="Ví dụ: Python, Java, React..."
                value={filters.skill || ''}
                onChange={(e) => handleFilterChange('skill', e.target.value)}
                onKeyPress={handleKeyPress}
                style={{
                  width: '100%',
                  padding: '8px 12px',
                  border: '1px solid #CBD5E1',
                  borderRadius: '4px',
                  fontSize: '13px',
                  fontFamily: 'Inter, sans-serif',
                  color: '#1E3A5F',
                  backgroundColor: '#FFFFFF',
                  height: '36px',
                  outline: 'none'
                }}
                onFocus={(e) => {
                  e.target.style.borderColor = '#1E3A5F';
                  e.target.style.boxShadow = '0 0 0 2px rgba(30, 58, 95, 0.12)';
                }}
                onBlur={(e) => {
                  e.target.style.borderColor = '#CBD5E1';
                  e.target.style.boxShadow = 'none';
                }}
              />
            </div>

            <div>
              <label style={{
                display: 'block',
                fontSize: '13px',
                fontWeight: '500',
                color: '#1E3A5F',
                marginBottom: '6px'
              }}>
                Địa Điểm
              </label>
              <select
                value={filters.location || ''}
                onChange={(e) => handleFilterChange('location', e.target.value)}
                style={{
                  width: '100%',
                  padding: '8px 12px',
                  border: '1px solid #CBD5E1',
                  borderRadius: '4px',
                  fontSize: '13px',
                  fontFamily: 'Inter, sans-serif',
                  color: '#1E3A5F',
                  backgroundColor: '#FFFFFF',
                  height: '36px',
                  outline: 'none',
                  cursor: 'pointer'
                }}
                onFocus={(e) => {
                  e.target.style.borderColor = '#1E3A5F';
                  e.target.style.boxShadow = '0 0 0 2px rgba(30, 58, 95, 0.12)';
                }}
                onBlur={(e) => {
                  e.target.style.borderColor = '#CBD5E1';
                  e.target.style.boxShadow = 'none';
                }}
              >
                <option value="">Tất Cả Địa Điểm</option>
                {availableFilters.locations.map((loc, idx) => (
                  <option key={idx} value={loc}>{loc}</option>
                ))}
              </select>
            </div>

            <div>
              <label style={{
                display: 'block',
                fontSize: '13px',
                fontWeight: '500',
                color: '#1E3A5F',
                marginBottom: '6px'
              }}>
                Cấp Bậc
              </label>
              <select
                value={filters.level || ''}
                onChange={(e) => handleFilterChange('level', e.target.value)}
                style={{
                  width: '100%',
                  padding: '8px 12px',
                  border: '1px solid #CBD5E1',
                  borderRadius: '4px',
                  fontSize: '13px',
                  fontFamily: 'Inter, sans-serif',
                  color: '#1E3A5F',
                  backgroundColor: '#FFFFFF',
                  height: '36px',
                  outline: 'none',
                  cursor: 'pointer'
                }}
                onFocus={(e) => {
                  e.target.style.borderColor = '#1E3A5F';
                  e.target.style.boxShadow = '0 0 0 2px rgba(30, 58, 95, 0.12)';
                }}
                onBlur={(e) => {
                  e.target.style.borderColor = '#CBD5E1';
                  e.target.style.boxShadow = 'none';
                }}
              >
                <option value="">Tất Cả Cấp Bậc</option>
                {availableFilters.levels.map((level, idx) => (
                  <option key={idx} value={level}>{level}</option>
                ))}
              </select>
            </div>
          </div>

          <button 
            onClick={handleSearch}
            disabled={loading}
            style={{
              backgroundColor: loading ? '#94A3B8' : '#1E3A5F',
              color: '#FFFFFF',
              border: 'none',
              padding: '8px 24px',
              borderRadius: '4px',
              fontSize: '13px',
              fontWeight: '500',
              cursor: loading ? 'not-allowed' : 'pointer',
              height: '36px',
              transition: 'all 0.15s ease'
            }}
            onMouseEnter={(e) => {
              if (!loading) e.currentTarget.style.backgroundColor = '#162D4A';
            }}
            onMouseLeave={(e) => {
              if (!loading) e.currentTarget.style.backgroundColor = '#1E3A5F';
            }}
          >
            {loading ? 'Đang Tìm Kiếm...' : '🔍 Tìm Kiếm'}
          </button>
        </div>

        {/* Results */}
        {loading && (
          <div style={{ 
            textAlign: 'center', 
            padding: '48px',
            color: '#6B7280',
            fontSize: '14px'
          }}>
            Đang tìm kiếm công việc...
          </div>
        )}

        {!loading && searched && (
          <div>
            <div style={{
              marginBottom: '16px',
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'center'
            }}>
              <h2 style={{ 
                fontFamily: 'Noto Serif, serif',
                fontSize: '18px',
                fontWeight: '600',
                color: '#1E3A5F',
                margin: 0
              }}>
                Tìm Thấy {jobs?.length || 0} Công Việc
              </h2>
              {jobs && jobs.length > 0 && (
                <span style={{
                  fontSize: '12px',
                  color: '#6B7280'
                }}>
                  Hiển thị {Math.min(50, jobs.length)} kết quả đầu tiên
                </span>
              )}
            </div>

            {!jobs || jobs.length === 0 ? (
              <div style={{
                backgroundColor: '#FFFFFF',
                border: '1px solid #E2E8F0',
                borderRadius: '4px',
                padding: '48px',
                boxShadow: '0 1px 2px rgba(15, 23, 42, 0.04)',
                textAlign: 'center'
              }}>
                <div style={{ fontSize: '48px', marginBottom: '16px' }}>🔍</div>
                <p style={{ 
                  color: '#6B7280',
                  fontSize: '14px',
                  margin: 0
                }}>
                  Không tìm thấy công việc phù hợp với tiêu chí của bạn.
                  <br />
                  Hãy thử thay đổi bộ lọc tìm kiếm.
                </p>
              </div>
            ) : (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                {jobs.slice(0, 50).map((job, idx) => (
                  <div key={idx} style={{
                    backgroundColor: '#FFFFFF',
                    border: '1px solid #E2E8F0',
                    borderRadius: '4px',
                    padding: '16px',
                    boxShadow: '0 1px 2px rgba(15, 23, 42, 0.04)',
                    transition: 'all 0.15s ease',
                    cursor: 'pointer'
                  }}
                  onMouseEnter={(e) => {
                    e.currentTarget.style.boxShadow = '0 2px 6px rgba(15, 23, 42, 0.06)';
                    e.currentTarget.style.borderColor = '#CBD5E1';
                  }}
                  onMouseLeave={(e) => {
                    e.currentTarget.style.boxShadow = '0 1px 2px rgba(15, 23, 42, 0.04)';
                    e.currentTarget.style.borderColor = '#E2E8F0';
                  }}>
                    <div style={{ 
                      fontFamily: 'Noto Serif, serif',
                      color: '#1E3A5F',
                      fontSize: '16px',
                      fontWeight: '600',
                      marginBottom: '8px'
                    }}>
                      {job.title}
                    </div>
                    <div style={{ 
                      color: '#2563EB',
                      fontWeight: '500',
                      fontSize: '14px',
                      marginBottom: '8px'
                    }}>
                      {job.company}
                    </div>
                    <div style={{ 
                      display: 'flex',
                      gap: '16px',
                      color: '#6B7280',
                      fontSize: '13px',
                      marginBottom: '8px',
                      flexWrap: 'wrap'
                    }}>
                      <span>📍 {job.location}</span>
                      <span>💼 {job.job_level}</span>
                      <span>🆔 {job.job_id}</span>
                    </div>
                    {job.skills && (
                      <div style={{ 
                        color: '#1E3A5F',
                        fontSize: '13px',
                        marginTop: '8px',
                        paddingTop: '8px',
                        borderTop: '1px solid #F1F5F9'
                      }}>
                        <strong style={{ color: '#6B7280' }}>Kỹ năng:</strong> {job.skills}
                      </div>
                    )}
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {/* Initial State */}
        {!loading && !searched && (
          <div style={{
            backgroundColor: '#FFFFFF',
            border: '1px solid #E2E8F0',
            borderRadius: '4px',
            padding: '48px',
            boxShadow: '0 1px 2px rgba(15, 23, 42, 0.04)',
            textAlign: 'center'
          }}>
            <div style={{ fontSize: '64px', marginBottom: '16px' }}>💼</div>
            <h3 style={{ 
              fontFamily: 'Noto Serif, serif',
              fontSize: '18px',
              fontWeight: '600',
              color: '#1E3A5F',
              marginBottom: '8px'
            }}>
              Bắt Đầu Tìm Kiếm Công Việc
            </h3>
            <p style={{ 
              color: '#6B7280',
              fontSize: '14px',
              margin: 0,
              maxWidth: '500px',
              marginLeft: 'auto',
              marginRight: 'auto'
            }}>
              Sử dụng bộ lọc phía trên để tìm kiếm công việc IT phù hợp với kỹ năng, 
              địa điểm và cấp bậc mong muốn của bạn.
            </p>
          </div>
        )}
      </div>
    </div>
  );
};

export default JobSearch;
