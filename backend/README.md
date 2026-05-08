# IT Jobs Vietnam - Backend API

Flask REST API for IT Jobs Vietnam Dashboard

## Installation

```bash
cd backend
pip install -r requirements.txt
```

## Run Server

```bash
python api.py
```

Server runs at: `http://localhost:5000`

## API Endpoints

### General
- `GET /api/health` - Health check
- `GET /api/stats` - Overall statistics

### Jobs
- `GET /api/jobs` - Get all jobs (paginated)
- `GET /api/jobs/search?skill=Python&location=Hà Nội&level=Experienced` - Search jobs

### Skills & Companies
- `GET /api/skills/top?limit=15` - Top skills
- `GET /api/companies/top?limit=15` - Top companies
- `GET /api/locations/top?limit=10` - Top locations

### Analytics
- `GET /api/levels` - Job level distribution
- `GET /api/cities/compare` - Hanoi vs HCM comparison
- `GET /api/ai-ml` - AI/ML statistics
- `GET /api/technologies` - Technology trends by category

### Filters
- `GET /api/filters` - Get available filter options

## CORS

CORS is enabled for all origins to allow React frontend access.
