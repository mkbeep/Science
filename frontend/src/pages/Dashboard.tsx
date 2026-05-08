import React, { useState, useEffect } from 'react';
import { Bar } from 'react-chartjs-2';
import { Chart as ChartJS, CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend } from 'chart.js';
import { getStats, getTopSkills, getTopLocations, getJobLevels } from '../api/api';
import { Stats, Skill, Location, JobLevel } from '../types';

ChartJS.register(CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend);

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

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-lg">Loading...</div>
      </div>
    );
  }

  if (!stats) return <div className="p-8">No data available</div>;

  // Calculate max for location bars
  const maxLocationCount = Math.max(...topLocations.map(l => l.count));

  // Calculate max for skills bars
  const maxSkillCount = Math.max(...topSkills.map(s => s.count));

  // Calculate total for job levels
  const totalJobs = jobLevels.reduce((sum, level) => sum + level.count, 0);

  return (
    <div className="p-6 lg:p-8 max-w-[1440px] mx-auto">
      {/* Page Header */}
      <div className="mb-8 flex flex-col lg:flex-row justify-between items-start lg:items-end gap-4">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Market Intelligence Dashboard</h1>
          <p className="text-gray-600 text-lg">Real-time overview of the Vietnamese IT recruitment landscape.</p>
        </div>
        <div className="flex gap-2">
          <button className="bg-white border border-gray-300 px-4 py-2 rounded-lg flex items-center gap-2 text-sm font-medium hover:bg-gray-50 transition-colors">
            <span className="material-symbols-outlined text-base">calendar_today</span>
            Last 30 Days
          </button>
          <button className="bg-blue-600 text-white px-4 py-2 rounded-lg flex items-center gap-2 text-sm font-medium shadow-sm hover:bg-blue-700 transition-colors">
            <span className="material-symbols-outlined text-base">download</span>
            Export Report
          </button>
        </div>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        {/* Total Jobs */}
        <div className="bg-white border border-gray-200 p-6 rounded-lg shadow-sm hover:-translate-y-1 transition-transform">
          <div className="flex justify-between items-start mb-4">
            <div className="p-2 bg-blue-100 rounded-lg">
              <span className="material-symbols-outlined text-blue-600">work</span>
            </div>
            <span className="text-green-600 text-xs font-semibold flex items-center bg-green-50 px-2 py-1 rounded">
              +12.5%
            </span>
          </div>
          <p className="text-gray-500 text-xs font-semibold mb-1 uppercase tracking-wider">Total Jobs</p>
          <h2 className="text-4xl font-bold text-gray-900">{stats.total_jobs.toLocaleString()}</h2>
        </div>

        {/* Total Companies */}
        <div className="bg-white border border-gray-200 p-6 rounded-lg shadow-sm hover:-translate-y-1 transition-transform">
          <div className="flex justify-between items-start mb-4">
            <div className="p-2 bg-purple-100 rounded-lg">
              <span className="material-symbols-outlined text-purple-600">business</span>
            </div>
            <span className="text-green-600 text-xs font-semibold flex items-center bg-green-50 px-2 py-1 rounded">
              +4.2%
            </span>
          </div>
          <p className="text-gray-500 text-xs font-semibold mb-1 uppercase tracking-wider">Total Companies</p>
          <h2 className="text-4xl font-bold text-gray-900">{stats.total_companies.toLocaleString()}</h2>
        </div>

        {/* Total Locations */}
        <div className="bg-white border border-gray-200 p-6 rounded-lg shadow-sm hover:-translate-y-1 transition-transform">
          <div className="flex justify-between items-start mb-4">
            <div className="p-2 bg-orange-100 rounded-lg">
              <span className="material-symbols-outlined text-orange-600">location_on</span>
            </div>
            <span className="text-gray-500 text-xs font-semibold flex items-center bg-gray-100 px-2 py-1 rounded">
              Stable
            </span>
          </div>
          <p className="text-gray-500 text-xs font-semibold mb-1 uppercase tracking-wider">Total Locations</p>
          <h2 className="text-4xl font-bold text-gray-900">{stats.total_locations}</h2>
        </div>

        {/* Unique Skills */}
        <div className="bg-white border border-gray-200 p-6 rounded-lg shadow-sm hover:-translate-y-1 transition-transform">
          <div className="flex justify-between items-start mb-4">
            <div className="p-2 bg-blue-100 rounded-lg">
              <span className="material-symbols-outlined text-blue-600">psychology</span>
            </div>
            <span className="text-green-600 text-xs font-semibold flex items-center bg-green-50 px-2 py-1 rounded">
              +18%
            </span>
          </div>
          <p className="text-gray-500 text-xs font-semibold mb-1 uppercase tracking-wider">Unique Skills</p>
          <h2 className="text-4xl font-bold text-gray-900">{stats.unique_skills.toLocaleString()}</h2>
        </div>
      </div>

      {/* Dashboard Bento Grid */}
      <div className="grid grid-cols-12 gap-6 mb-8">
        {/* Top 15 Skills - Col Span 8 */}
        <div className="col-span-12 lg:col-span-8 bg-white border border-gray-200 rounded-lg shadow-sm overflow-hidden">
          <div className="px-6 py-4 border-b border-gray-200 bg-gray-50 flex justify-between items-center">
            <h3 className="text-lg font-semibold text-gray-900">Top 15 Skills Demand</h3>
            <button className="text-blue-600 text-sm font-medium hover:underline">Full Analytics</button>
          </div>
          <div className="p-6 h-[400px] flex items-end justify-between gap-1">
            {topSkills.map((skill, idx) => {
              const heightPercent = (skill.count / maxSkillCount) * 100;
              return (
                <div key={idx} className="flex flex-col items-center gap-2 flex-1">
                  <div 
                    className="w-full bg-blue-200 rounded-t-sm hover:opacity-80 transition-opacity cursor-pointer"
                    style={{ height: `${heightPercent}%` }}
                    title={`${skill.skill}: ${skill.count}`}
                  ></div>
                  <span className="text-[10px] text-gray-600 rotate-45 origin-left whitespace-nowrap">
                    {skill.skill}
                  </span>
                </div>
              );
            })}
          </div>
        </div>

        {/* Job Level Distribution - Col Span 4 */}
        <div className="col-span-12 lg:col-span-4 bg-white border border-gray-200 rounded-lg shadow-sm overflow-hidden">
          <div className="px-6 py-4 border-b border-gray-200 bg-gray-50">
            <h3 className="text-lg font-semibold text-gray-900">Job Level Distribution</h3>
          </div>
          <div className="p-6 flex flex-col items-center justify-center h-[400px]">
            {/* Donut Chart Simulated */}
            <div className="relative w-48 h-48 rounded-full border-[18px] border-blue-200" 
                 style={{
                   borderLeftColor: '#6664e4',
                   borderBottomColor: '#ac6300',
                   borderRightColor: '#e2e2e7'
                 }}>
              <div className="absolute inset-0 flex flex-col items-center justify-center">
                <span className="text-lg font-bold text-gray-900">By Level</span>
              </div>
            </div>
            <div className="mt-6 w-full space-y-2">
              {jobLevels.slice(0, 4).map((level, idx) => {
                const colors = ['bg-blue-200', 'bg-purple-200', 'bg-orange-200', 'bg-gray-300'];
                const percentage = ((level.count / totalJobs) * 100).toFixed(0);
                return (
                  <div key={idx} className="flex justify-between items-center">
                    <div className="flex items-center gap-2">
                      <div className={`w-3 h-3 rounded-full ${colors[idx]}`}></div>
                      <span className="text-sm text-gray-600">{level.level}</span>
                    </div>
                    <span className="font-semibold text-gray-900">{percentage}%</span>
                  </div>
                );
              })}
            </div>
          </div>
        </div>

        {/* Top 10 Locations - Col Span 12 */}
        <div className="col-span-12 bg-white border border-gray-200 rounded-lg shadow-sm overflow-hidden">
          <div className="px-6 py-4 border-b border-gray-200 bg-gray-50 flex justify-between items-center">
            <h3 className="text-lg font-semibold text-gray-900">Top 10 Locations</h3>
            <div className="flex items-center gap-4">
              <span className="flex items-center gap-2 text-sm text-gray-600">
                <span className="w-2 h-2 rounded-full bg-blue-600"></span>
                Total Openings
              </span>
            </div>
          </div>
          <div className="p-6 grid grid-cols-1 md:grid-cols-2 gap-x-8 gap-y-4">
            {topLocations.map((location, idx) => {
              const widthPercent = (location.count / maxLocationCount) * 100;
              return (
                <div key={idx} className="space-y-1">
                  <div className="flex justify-between text-sm mb-1">
                    <span className="text-gray-900 font-medium">{location.location}</span>
                    <span className="text-gray-600">{location.count.toLocaleString()}</span>
                  </div>
                  <div className="h-3 w-full bg-gray-100 rounded-full overflow-hidden">
                    <div 
                      className="h-full bg-blue-600 transition-all duration-500"
                      style={{ width: `${widthPercent}%` }}
                    ></div>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      </div>

      {/* Premium Insights Card */}
      <div className="bg-blue-600 text-white p-8 rounded-lg mb-8 relative overflow-hidden flex flex-col md:flex-row items-center justify-between">
        <div className="relative z-10">
          <h3 className="text-3xl font-bold mb-2">Premium Insights Ready</h3>
          <p className="text-lg opacity-90 max-w-xl">
            Deep dive into salary benchmarking and candidate movement trends across 12 sectors. 
            Update your enterprise plan to access full data exports.
          </p>
          <button className="mt-6 bg-white text-blue-600 px-8 py-3 rounded-lg font-bold hover:bg-gray-100 transition-colors">
            Upgrade to Pro
          </button>
        </div>
        <div className="mt-8 md:mt-0 opacity-20 pointer-events-none">
          <span className="material-symbols-outlined text-[160px]">monitoring</span>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
