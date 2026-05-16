import axios, { AxiosResponse } from 'axios';
import {
  Stats,
  JobsResponse,
  SearchParams,
  Skill,
  Location,
  Company,
  JobLevel,
  CitiesComparison,
  AIMLStats,
  Technologies,
  Filters,
  TrendDataPoint,
  AITrendDataPoint,
  SkillTrendDataPoint,
  TrendSummary,
  EmergingSkillsResponse,
  DataQualityInsights
} from '../types';

const API_BASE_URL = 'http://localhost:5001/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const getStats = (): Promise<AxiosResponse<Stats>> => 
  api.get<Stats>('/stats');

export const getJobs = (page = 1, perPage = 20): Promise<AxiosResponse<JobsResponse>> => 
  api.get<JobsResponse>(`/jobs?page=${page}&per_page=${perPage}`);

export const searchJobs = (params: SearchParams): Promise<AxiosResponse<JobsResponse>> => 
  api.get<JobsResponse>('/jobs/search', { params });

export const getTopSkills = (limit = 15): Promise<AxiosResponse<Skill[]>> => 
  api.get<Skill[]>(`/skills/top?limit=${limit}`);

export const getTechnicalSkills = (limit = 30): Promise<AxiosResponse<Skill[]>> => 
  api.get<Skill[]>(`/skills/technical?limit=${limit}`);

export const getTopLocations = (limit = 10): Promise<AxiosResponse<Location[]>> => 
  api.get<Location[]>(`/locations/top?limit=${limit}`);

export const getTopCompanies = (limit = 15): Promise<AxiosResponse<Company[]>> => 
  api.get<Company[]>(`/companies/top?limit=${limit}`);

export const getJobLevels = (): Promise<AxiosResponse<JobLevel[]>> => 
  api.get<JobLevel[]>('/levels');

export const compareCities = (): Promise<AxiosResponse<CitiesComparison>> => 
  api.get<CitiesComparison>('/cities/compare');

export const getAIMLStats = (): Promise<AxiosResponse<AIMLStats>> => 
  api.get<AIMLStats>('/ai-ml');

export const getTechnologies = (): Promise<AxiosResponse<Technologies>> => 
  api.get<Technologies>('/technologies');

export const getFilters = (): Promise<AxiosResponse<Filters>> => 
  api.get<Filters>('/filters');

// Trend Analysis APIs
export const getJobsTrend = (days = 30): Promise<AxiosResponse<TrendDataPoint[]>> => 
  api.get<TrendDataPoint[]>(`/trends/jobs?days=${days}`);

export const getAITrend = (days = 30): Promise<AxiosResponse<AITrendDataPoint[]>> => 
  api.get<AITrendDataPoint[]>(`/trends/ai?days=${days}`);

export const getSkillsTrend = (days = 30): Promise<AxiosResponse<SkillTrendDataPoint[]>> => 
  api.get<SkillTrendDataPoint[]>(`/trends/skills?days=${days}`);

export const getTrendsSummary = (): Promise<AxiosResponse<TrendSummary>> => 
  api.get<TrendSummary>('/trends/summary');

export const getEmergingSkills = (
  days = 14,
  limit = 15,
): Promise<AxiosResponse<EmergingSkillsResponse>> =>
  api.get<EmergingSkillsResponse>(`/trends/emerging-skills?days=${days}&limit=${limit}`);

export const getDataQualityInsights = (): Promise<AxiosResponse<DataQualityInsights>> =>
  api.get<DataQualityInsights>('/insights/data-quality');

// AI Insights APIs
export const fetchAIInsights = async () => {
  const response = await api.get('/ai-insights');
  return response.data;
};

export const fetchInsightsByCategory = async (category: string) => {
  const response = await api.get(`/ai-insights/category/${category}`);
  return response.data;
};

export const fetchTopInsights = async (limit = 10) => {
  const response = await api.get(`/ai-insights/top?limit=${limit}`);
  return response.data;
};

export const fetchInsightCategories = async () => {
  const response = await api.get('/ai-insights/categories');
  return response.data;
};

export default api;
