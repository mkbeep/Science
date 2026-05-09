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
  Filters
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

export default api;
