import React, { useState, useEffect, useCallback } from 'react';
import { Bar } from 'react-chartjs-2';
import { getTechnologies } from '../api/api';
import { Technologies, TechnologyData } from '../types';
import { useRealtime } from '../realtime/RealtimeProvider';

const Trends: React.FC = () => {
  const [techData, setTechData] = useState<Technologies | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const { refreshEpoch } = useRealtime();

  const loadData = useCallback(async (): Promise<void> => {
    try {
      setLoading(true);
      const res = await getTechnologies();
      setTechData(res.data);
      setLoading(false);
    } catch (error) {
      console.error('Error loading technologies:', error);
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    void loadData();
  }, [refreshEpoch, loadData]);

  const createChartData = (data: TechnologyData[], color: string) => ({
    labels: data.map(d => d.skill),
    datasets: [{
      label: 'Demand Count',
      data: data.map(d => d.count),
      backgroundColor: color,
    }]
  });

  if (loading) return <div className="loading">Loading...</div>;
  if (!techData) return <div className="loading">No data available</div>;

  return (
    <div>
      <h1 style={{ marginBottom: '2rem', color: '#2d3748' }}>📈 Technology Trends</h1>

      <div className="charts-grid">
        <div className="chart-container">
          <h2>💻 Programming Languages</h2>
          {techData.languages.length > 0 ? (
            <Bar 
              data={createChartData(techData.languages, 'rgba(244, 67, 54, 0.8)')} 
              options={{ responsive: true, indexAxis: 'y' }} 
            />
          ) : (
            <p>No data available</p>
          )}
        </div>

        <div className="chart-container">
          <h2>🗄️ Databases</h2>
          {techData.databases.length > 0 ? (
            <Bar 
              data={createChartData(techData.databases, 'rgba(33, 150, 243, 0.8)')} 
              options={{ responsive: true, indexAxis: 'y' }} 
            />
          ) : (
            <p>No data available</p>
          )}
        </div>
      </div>

      <div className="charts-grid">
        <div className="card">
          <h2>🌐 Web Frameworks</h2>
          {techData.frameworks.length > 0 ? (
            <table style={{ width: '100%', marginTop: '1rem' }}>
              <thead>
                <tr style={{ borderBottom: '2px solid #e2e8f0' }}>
                  <th style={{ textAlign: 'left', padding: '0.5rem' }}>Framework</th>
                  <th style={{ textAlign: 'right', padding: '0.5rem' }}>Count</th>
                </tr>
              </thead>
              <tbody>
                {techData.frameworks.map((fw, idx) => (
                  <tr key={idx} style={{ borderBottom: '1px solid #e2e8f0' }}>
                    <td style={{ padding: '0.5rem' }}>{fw.skill}</td>
                    <td style={{ textAlign: 'right', padding: '0.5rem' }}>{fw.count}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          ) : (
            <p>No data available</p>
          )}
        </div>

        <div className="card">
          <h2>☁️ Cloud & DevOps</h2>
          {techData.cloud.length > 0 ? (
            <table style={{ width: '100%', marginTop: '1rem' }}>
              <thead>
                <tr style={{ borderBottom: '2px solid #e2e8f0' }}>
                  <th style={{ textAlign: 'left', padding: '0.5rem' }}>Technology</th>
                  <th style={{ textAlign: 'right', padding: '0.5rem' }}>Count</th>
                </tr>
              </thead>
              <tbody>
                {techData.cloud.map((tech, idx) => (
                  <tr key={idx} style={{ borderBottom: '1px solid #e2e8f0' }}>
                    <td style={{ padding: '0.5rem' }}>{tech.skill}</td>
                    <td style={{ textAlign: 'right', padding: '0.5rem' }}>{tech.count}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          ) : (
            <p>No data available</p>
          )}
        </div>
      </div>
    </div>
  );
};

export default Trends;
