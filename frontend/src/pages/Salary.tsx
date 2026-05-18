import React, { useEffect, useState } from 'react';
import {
  BarChart, Bar,
  XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer
} from 'recharts';
import { getSalaryOverview, getSalaryBySkill, getSalaryByLevel, getSalaryByLocation, getSalaryDistribution, getSalaryByCompany } from '../api/api';

const Salary: React.FC = () => {
  const [overview, setOverview] = useState<any>(null);
  const [salaryBySkill, setSalaryBySkill] = useState<any[]>([]);
  const [salaryByLevel, setSalaryByLevel] = useState<any[]>([]);
  const [salaryByLocation, setSalaryByLocation] = useState<any[]>([]);
  const [salaryDistribution, setSalaryDistribution] = useState<any[]>([]);
  const [salaryByCompany, setSalaryByCompany] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      setLoading(true);
      const [overviewData, skillData, levelData, locationData, distributionData, companyData] = await Promise.all([
        getSalaryOverview(),
        getSalaryBySkill(15),
        getSalaryByLevel(),
        getSalaryByLocation(),
        getSalaryDistribution(),
        getSalaryByCompany(15)
      ]);

      setOverview(overviewData);
      setSalaryBySkill(skillData);
      setSalaryByLevel(levelData);
      setSalaryByLocation(locationData);
      setSalaryDistribution(distributionData);
      setSalaryByCompany(companyData);
    } catch (error) {
      console.error('Error loading salary data:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div style={{ padding: '20px', textAlign: 'center' }}>
        <h2>Đang tải dữ liệu phân tích lương...</h2>
      </div>
    );
  }

  return (
    <div style={{ padding: '20px', backgroundColor: '#f5f5f5', minHeight: '100vh' }}>
      <h1 style={{ marginBottom: '30px', color: '#333' }}>📊 Phân Tích Lương IT Jobs</h1>

      {/* Overview Cards */}
      {overview && (
        <div style={{ 
          display: 'grid', 
          gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', 
          gap: '20px', 
          marginBottom: '30px' 
        }}>
          <div style={{ 
            backgroundColor: 'white', 
            padding: '20px', 
            borderRadius: '8px', 
            boxShadow: '0 2px 4px rgba(0,0,0,0.1)' 
          }}>
            <h3 style={{ margin: '0 0 10px 0', color: '#666', fontSize: '14px' }}>Tổng số Jobs</h3>
            <p style={{ margin: 0, fontSize: '32px', fontWeight: 'bold', color: '#0088FE' }}>
              {overview.total_jobs.toLocaleString()}
            </p>
          </div>

          <div style={{ 
            backgroundColor: 'white', 
            padding: '20px', 
            borderRadius: '8px', 
            boxShadow: '0 2px 4px rgba(0,0,0,0.1)' 
          }}>
            <h3 style={{ margin: '0 0 10px 0', color: '#666', fontSize: '14px' }}>Jobs có thông tin lương</h3>
            <p style={{ margin: 0, fontSize: '32px', fontWeight: 'bold', color: '#00C49F' }}>
              {overview.jobs_with_salary.toLocaleString()}
            </p>
            <p style={{ margin: '5px 0 0 0', fontSize: '14px', color: '#999' }}>
              {overview.coverage_percentage}% tổng số jobs
            </p>
          </div>

          <div style={{ 
            backgroundColor: 'white', 
            padding: '20px', 
            borderRadius: '8px', 
            boxShadow: '0 2px 4px rgba(0,0,0,0.1)' 
          }}>
            <h3 style={{ margin: '0 0 10px 0', color: '#666', fontSize: '14px' }}>Lương trung bình</h3>
            <p style={{ margin: 0, fontSize: '28px', fontWeight: 'bold', color: '#FFBB28' }}>
              {overview.avg_min_salary.toFixed(1)} - {overview.avg_max_salary.toFixed(1)} triệu
            </p>
            <p style={{ margin: '5px 0 0 0', fontSize: '14px', color: '#999' }}>VND/tháng</p>
          </div>

          <div style={{ 
            backgroundColor: 'white', 
            padding: '20px', 
            borderRadius: '8px', 
            boxShadow: '0 2px 4px rgba(0,0,0,0.1)' 
          }}>
            <h3 style={{ margin: '0 0 10px 0', color: '#666', fontSize: '14px' }}>Jobs thỏa thuận</h3>
            <p style={{ margin: 0, fontSize: '32px', fontWeight: 'bold', color: '#FF8042' }}>
              {overview.negotiable_jobs.toLocaleString()}
            </p>
            <p style={{ margin: '5px 0 0 0', fontSize: '14px', color: '#999' }}>
              {((overview.negotiable_jobs / overview.total_jobs) * 100).toFixed(1)}% tổng số jobs
            </p>
          </div>
        </div>
      )}

      {/* Salary Distribution */}
      {salaryDistribution.length > 0 && (
        <div style={{ 
          backgroundColor: 'white', 
          padding: '20px', 
          borderRadius: '8px', 
          boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
          marginBottom: '30px'
        }}>
          <h2 style={{ marginTop: 0, color: '#333' }}>Phân Bố Mức Lương</h2>
          <ResponsiveContainer width="100%" height={400}>
            <BarChart data={salaryDistribution}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="range" />
              <YAxis />
              <Tooltip />
              <Legend />
              <Bar dataKey="count" fill="#0088FE" name="Số lượng jobs" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      )}

      {/* Salary by Level */}
      {salaryByLevel.length > 0 && (
        <div style={{ 
          backgroundColor: 'white', 
          padding: '20px', 
          borderRadius: '8px', 
          boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
          marginBottom: '30px'
        }}>
          <h2 style={{ marginTop: 0, color: '#333' }}>Lương Theo Cấp Bậc</h2>
          <ResponsiveContainer width="100%" height={400}>
            <BarChart data={salaryByLevel} layout="vertical">
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis type="number" label={{ value: 'Triệu VND/tháng', position: 'insideBottom', offset: -5 }} />
              <YAxis type="category" dataKey="level" width={150} />
              <Tooltip />
              <Legend />
              <Bar dataKey="avg_min_salary" fill="#00C49F" name="Lương tối thiểu TB" />
              <Bar dataKey="avg_max_salary" fill="#0088FE" name="Lương tối đa TB" />
            </BarChart>
          </ResponsiveContainer>
          
          {/* Table view */}
          <div style={{ marginTop: '20px', overflowX: 'auto' }}>
            <table style={{ width: '100%', borderCollapse: 'collapse' }}>
              <thead>
                <tr style={{ backgroundColor: '#f0f0f0' }}>
                  <th style={{ padding: '10px', textAlign: 'left', borderBottom: '2px solid #ddd' }}>Cấp bậc</th>
                  <th style={{ padding: '10px', textAlign: 'right', borderBottom: '2px solid #ddd' }}>Số jobs</th>
                  <th style={{ padding: '10px', textAlign: 'right', borderBottom: '2px solid #ddd' }}>Lương TB (triệu)</th>
                  <th style={{ padding: '10px', textAlign: 'right', borderBottom: '2px solid #ddd' }}>Min - Max (triệu)</th>
                </tr>
              </thead>
              <tbody>
                {salaryByLevel.map((item, index) => (
                  <tr key={index} style={{ borderBottom: '1px solid #eee' }}>
                    <td style={{ padding: '10px' }}>{item.level}</td>
                    <td style={{ padding: '10px', textAlign: 'right' }}>{item.job_count}</td>
                    <td style={{ padding: '10px', textAlign: 'right', fontWeight: 'bold' }}>
                      {item.avg_salary.toFixed(1)}
                    </td>
                    <td style={{ padding: '10px', textAlign: 'right', color: '#666' }}>
                      {item.min_salary.toFixed(1)} - {item.max_salary.toFixed(1)}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Salary by Skill */}
      {salaryBySkill.length > 0 && (
        <div style={{ 
          backgroundColor: 'white', 
          padding: '20px', 
          borderRadius: '8px', 
          boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
          marginBottom: '30px'
        }}>
          <h2 style={{ marginTop: 0, color: '#333' }}>Top 15 Kỹ Năng Có Lương Cao Nhất</h2>
          <ResponsiveContainer width="100%" height={500}>
            <BarChart data={salaryBySkill} layout="vertical">
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis type="number" label={{ value: 'Triệu VND/tháng', position: 'insideBottom', offset: -5 }} />
              <YAxis type="category" dataKey="skill" width={120} />
              <Tooltip />
              <Legend />
              <Bar dataKey="avg_salary" fill="#FFBB28" name="Lương trung bình" />
            </BarChart>
          </ResponsiveContainer>

          {/* Table view */}
          <div style={{ marginTop: '20px', overflowX: 'auto' }}>
            <table style={{ width: '100%', borderCollapse: 'collapse' }}>
              <thead>
                <tr style={{ backgroundColor: '#f0f0f0' }}>
                  <th style={{ padding: '10px', textAlign: 'left', borderBottom: '2px solid #ddd' }}>Kỹ năng</th>
                  <th style={{ padding: '10px', textAlign: 'right', borderBottom: '2px solid #ddd' }}>Số jobs</th>
                  <th style={{ padding: '10px', textAlign: 'right', borderBottom: '2px solid #ddd' }}>Lương TB (triệu)</th>
                  <th style={{ padding: '10px', textAlign: 'right', borderBottom: '2px solid #ddd' }}>Min - Max (triệu)</th>
                </tr>
              </thead>
              <tbody>
                {salaryBySkill.map((item, index) => (
                  <tr key={index} style={{ borderBottom: '1px solid #eee' }}>
                    <td style={{ padding: '10px' }}>{item.skill}</td>
                    <td style={{ padding: '10px', textAlign: 'right' }}>{item.job_count}</td>
                    <td style={{ padding: '10px', textAlign: 'right', fontWeight: 'bold', color: '#FFBB28' }}>
                      {item.avg_salary.toFixed(1)}
                    </td>
                    <td style={{ padding: '10px', textAlign: 'right', color: '#666' }}>
                      {item.min_salary.toFixed(1)} - {item.max_salary.toFixed(1)}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Salary by Location */}
      {salaryByLocation.length > 0 && (
        <div style={{ 
          backgroundColor: 'white', 
          padding: '20px', 
          borderRadius: '8px', 
          boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
          marginBottom: '30px'
        }}>
          <h2 style={{ marginTop: 0, color: '#333' }}>Lương Theo Địa Điểm</h2>
          <ResponsiveContainer width="100%" height={400}>
            <BarChart data={salaryByLocation}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="location" />
              <YAxis label={{ value: 'Triệu VND/tháng', angle: -90, position: 'insideLeft' }} />
              <Tooltip />
              <Legend />
              <Bar dataKey="avg_salary" fill="#00C49F" name="Lương trung bình" />
            </BarChart>
          </ResponsiveContainer>

          {/* Table view */}
          <div style={{ marginTop: '20px', overflowX: 'auto' }}>
            <table style={{ width: '100%', borderCollapse: 'collapse' }}>
              <thead>
                <tr style={{ backgroundColor: '#f0f0f0' }}>
                  <th style={{ padding: '10px', textAlign: 'left', borderBottom: '2px solid #ddd' }}>Địa điểm</th>
                  <th style={{ padding: '10px', textAlign: 'right', borderBottom: '2px solid #ddd' }}>Số jobs</th>
                  <th style={{ padding: '10px', textAlign: 'right', borderBottom: '2px solid #ddd' }}>Lương TB (triệu)</th>
                  <th style={{ padding: '10px', textAlign: 'right', borderBottom: '2px solid #ddd' }}>Min - Max (triệu)</th>
                </tr>
              </thead>
              <tbody>
                {salaryByLocation.map((item, index) => (
                  <tr key={index} style={{ borderBottom: '1px solid #eee' }}>
                    <td style={{ padding: '10px' }}>{item.location}</td>
                    <td style={{ padding: '10px', textAlign: 'right' }}>{item.job_count}</td>
                    <td style={{ padding: '10px', textAlign: 'right', fontWeight: 'bold', color: '#00C49F' }}>
                      {item.avg_salary.toFixed(1)}
                    </td>
                    <td style={{ padding: '10px', textAlign: 'right', color: '#666' }}>
                      {item.min_salary.toFixed(1)} - {item.max_salary.toFixed(1)}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Salary by Company */}
      {salaryByCompany.length > 0 && (
        <div style={{ 
          backgroundColor: 'white', 
          padding: '20px', 
          borderRadius: '8px', 
          boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
          marginBottom: '30px'
        }}>
          <h2 style={{ marginTop: 0, color: '#333' }}>Top 15 Công Ty Trả Lương Cao Nhất</h2>
          <ResponsiveContainer width="100%" height={500}>
            <BarChart data={salaryByCompany} layout="vertical">
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis type="number" label={{ value: 'Triệu VND/tháng', position: 'insideBottom', offset: -5 }} />
              <YAxis type="category" dataKey="company" width={200} />
              <Tooltip />
              <Legend />
              <Bar dataKey="avg_salary" fill="#FF8042" name="Lương trung bình" />
            </BarChart>
          </ResponsiveContainer>

          {/* Table view */}
          <div style={{ marginTop: '20px', overflowX: 'auto' }}>
            <table style={{ width: '100%', borderCollapse: 'collapse' }}>
              <thead>
                <tr style={{ backgroundColor: '#f0f0f0' }}>
                  <th style={{ padding: '10px', textAlign: 'left', borderBottom: '2px solid #ddd' }}>Công ty</th>
                  <th style={{ padding: '10px', textAlign: 'right', borderBottom: '2px solid #ddd' }}>Số jobs</th>
                  <th style={{ padding: '10px', textAlign: 'right', borderBottom: '2px solid #ddd' }}>Lương TB (triệu)</th>
                  <th style={{ padding: '10px', textAlign: 'right', borderBottom: '2px solid #ddd' }}>Min - Max (triệu)</th>
                </tr>
              </thead>
              <tbody>
                {salaryByCompany.map((item, index) => (
                  <tr key={index} style={{ borderBottom: '1px solid #eee' }}>
                    <td style={{ padding: '10px' }}>{item.company}</td>
                    <td style={{ padding: '10px', textAlign: 'right' }}>{item.job_count}</td>
                    <td style={{ padding: '10px', textAlign: 'right', fontWeight: 'bold', color: '#FF8042' }}>
                      {item.avg_salary.toFixed(1)}
                    </td>
                    <td style={{ padding: '10px', textAlign: 'right', color: '#666' }}>
                      {item.min_salary.toFixed(1)} - {item.max_salary.toFixed(1)}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* No data message */}
      {!overview || ((salaryBySkill.length === 0) && (salaryByLevel.length === 0)) && (
        <div style={{ 
          backgroundColor: 'white', 
          padding: '40px', 
          borderRadius: '8px', 
          boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
          textAlign: 'center'
        }}>
          <h2 style={{ color: '#999' }}>⚠️ Chưa có dữ liệu lương</h2>
          <p style={{ color: '#666' }}>
            Vui lòng chạy crawler để thu thập dữ liệu lương từ VietnamWorks.
          </p>
          <p style={{ color: '#666', marginTop: '10px' }}>
            Chạy lệnh: <code style={{ backgroundColor: '#f0f0f0', padding: '5px 10px', borderRadius: '4px' }}>
              ./RUN_CRAWLER_NOW.sh
            </code>
          </p>
        </div>
      )}
    </div>
  );
};

export default Salary;
