// API Response Types
export interface Stats {
  total_jobs: number;
  total_companies: number;
  total_locations: number;
  unique_skills: number;
}

export interface Job {
  job_id: number;
  title: string;
  company: string;
  location: string;
  job_level: string;
  skills: string;
  salary_min?: number;
  salary_max?: number;
  url?: string;
}

export interface Skill {
  skill: string;
  count: number;
}

export interface Location {
  location: string;
  count: number;
}

export interface Company {
  company: string;
  count: number;
}

export interface JobLevel {
  level: string;
  count: number;
}

export interface CityData {
  total_jobs: number;
  top_skills: Skill[];
}

export interface CitiesComparison {
  hanoi: CityData;
  hcm: CityData;
}

export interface AIMLStats {
  ai_jobs: number;
  total_jobs: number;
  percentage: number;
  skills: Skill[];
}

export interface TechnologyData {
  skill: string;
  count: number;
}

export interface Technologies {
  languages: TechnologyData[];
  databases: TechnologyData[];
  frameworks: TechnologyData[];
  cloud: TechnologyData[];
}

export interface Filters {
  locations: string[];
  levels: string[];
}

export interface JobsResponse {
  jobs: Job[];
  total: number;
  page?: number;
  per_page?: number;
  total_pages?: number;
}

export interface SearchParams {
  skill?: string;
  location?: string;
  level?: string;
}

// Trend Analysis Types
export interface TrendDataPoint {
  date: string;
  count: number;
  simulated: boolean;
}

export interface AITrendDataPoint {
  date: string;
  ai_jobs: number;
  total_jobs: number;
  percentage: number;
  simulated: boolean;
}

export interface SkillTrendDataPoint {
  date: string;
  Python: number;
  Java: number;
  React: number;
  'Data Analysis': number;
  simulated: boolean;
}

export interface TrendSummary {
  min_jobs: number;
  max_jobs: number;
  avg_jobs: number;
  min_ai: number;
  max_ai: number;
  avg_ai: number;
  growth_rate: number;  // Daily growth rate
  today_jobs: number;
  yesterday_jobs: number;
  today_new_jobs: number;  // NEW: jobs added today
  yesterday_new_jobs: number;  // NEW: jobs added yesterday
  weekly_growth_rate: number;  // Weekly growth rate based on new jobs
  last_week_new_jobs: number;  // Total new jobs this week
  prev_week_new_jobs: number;  // Total new jobs last week
}

export interface EmergingSkill {
  skill: string;
  recent_count: number;
  previous_count: number;
  delta: number;
  growth_rate: number | null;
}

export interface EmergingSkillsResponse {
  window_days: number;
  skills: EmergingSkill[];
  top_locations: Location[];
}

export interface DataQualityInsights {
  total_jobs: number;
  avg_completeness_score: number;
  avg_dedupe_score: number;
  avg_quality_score: number;
  canonicalized_locations: number;
  canonicalized_skills: number;
  location_coverage_pct: number;
}
