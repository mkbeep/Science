"""
IT JOBS VIETNAM - REST API
Flask backend API for React frontend
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
import sqlite3
import pandas as pd
from collections import Counter

app = Flask(__name__)
CORS(app)  # Enable CORS for React frontend

# Database connection
def get_db():
    conn = sqlite3.connect('../it_jobs_vietnam.db')
    conn.row_factory = sqlite3.Row
    return conn

# Load CSV data
def load_csv():
    return pd.read_csv('../clean_it_jobs.csv')

# ============================================================================
# ENDPOINTS
# ============================================================================

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'ok', 'message': 'API is running'})

@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Get overall statistics"""
    df = load_csv()
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(DISTINCT skill_name) FROM job_skills")
    unique_skills = cursor.fetchone()[0]
    
    stats = {
        'total_jobs': len(df),
        'total_companies': df['company'].nunique(),
        'total_locations': df['location'].nunique(),
        'unique_skills': unique_skills
    }
    
    conn.close()
    return jsonify(stats)

@app.route('/api/jobs', methods=['GET'])
def get_jobs():
    """Get all jobs with pagination"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    
    df = load_csv()
    
    start = (page - 1) * per_page
    end = start + per_page
    
    jobs = df.iloc[start:end].to_dict('records')
    
    return jsonify({
        'jobs': jobs,
        'total': len(df),
        'page': page,
        'per_page': per_page,
        'total_pages': (len(df) + per_page - 1) // per_page
    })

@app.route('/api/jobs/search', methods=['GET'])
def search_jobs():
    """Search jobs by skill, location, level"""
    skill = request.args.get('skill', '')
    location = request.args.get('location', '')
    level = request.args.get('level', '')
    
    df = load_csv()
    
    if skill:
        df = df[df['skills'].str.contains(skill, case=False, na=False)]
    if location:
        df = df[df['location'] == location]
    if level:
        df = df[df['job_level'] == level]
    
    jobs = df.to_dict('records')
    
    return jsonify({
        'jobs': jobs,
        'total': len(jobs)
    })

@app.route('/api/skills/top', methods=['GET'])
def get_top_skills():
    """Get top N skills"""
    limit = request.args.get('limit', 15, type=int)
    
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT skill_name, COUNT(*) as count
        FROM job_skills
        GROUP BY skill_name
        ORDER BY count DESC
        LIMIT ?
    """, (limit,))
    
    skills = [{'skill': row[0], 'count': row[1]} for row in cursor.fetchall()]
    conn.close()
    
    return jsonify(skills)

@app.route('/api/locations/top', methods=['GET'])
def get_top_locations():
    """Get top locations"""
    limit = request.args.get('limit', 10, type=int)
    
    df = load_csv()
    top_locs = df['location'].value_counts().head(limit)
    
    locations = [{'location': loc, 'count': int(count)} 
                 for loc, count in top_locs.items()]
    
    return jsonify(locations)

@app.route('/api/companies/top', methods=['GET'])
def get_top_companies():
    """Get top companies"""
    limit = request.args.get('limit', 15, type=int)
    
    df = load_csv()
    top_companies = df['company'].value_counts().head(limit)
    
    companies = [{'company': comp, 'count': int(count)} 
                 for comp, count in top_companies.items()]
    
    return jsonify(companies)

@app.route('/api/levels', methods=['GET'])
def get_job_levels():
    """Get job level distribution"""
    df = load_csv()
    levels = df['job_level'].value_counts()
    
    level_data = [{'level': level, 'count': int(count)} 
                  for level, count in levels.items()]
    
    return jsonify(level_data)

@app.route('/api/cities/compare', methods=['GET'])
def compare_cities():
    """Compare Hanoi vs HCM"""
    df = load_csv()
    conn = get_db()
    cursor = conn.cursor()
    
    hanoi = df[df['location'] == 'Hà Nội']
    hcm = df[df['location'] == 'Hồ Chí Minh']
    
    # Top skills in Hanoi
    cursor.execute("""
        SELECT js.skill_name, COUNT(*) as count
        FROM job_skills js JOIN jobs j ON js.job_id = j.job_id
        WHERE j.location = 'Hà Nội'
        GROUP BY js.skill_name ORDER BY count DESC LIMIT 10
    """)
    hanoi_skills = [{'skill': row[0], 'count': row[1]} for row in cursor.fetchall()]
    
    # Top skills in HCM
    cursor.execute("""
        SELECT js.skill_name, COUNT(*) as count
        FROM job_skills js JOIN jobs j ON js.job_id = j.job_id
        WHERE j.location = 'Hồ Chí Minh'
        GROUP BY js.skill_name ORDER BY count DESC LIMIT 10
    """)
    hcm_skills = [{'skill': row[0], 'count': row[1]} for row in cursor.fetchall()]
    
    conn.close()
    
    return jsonify({
        'hanoi': {
            'total_jobs': len(hanoi),
            'top_skills': hanoi_skills
        },
        'hcm': {
            'total_jobs': len(hcm),
            'top_skills': hcm_skills
        }
    })

@app.route('/api/ai-ml', methods=['GET'])
def get_ai_ml_stats():
    """Get AI/ML statistics"""
    conn = get_db()
    cursor = conn.cursor()
    
    # AI/ML jobs count
    cursor.execute("""
        SELECT COUNT(DISTINCT j.job_id)
        FROM jobs j JOIN job_skills js ON j.job_id = js.job_id
        WHERE js.skill_name IN ('AI', 'Machine Learning', 'Deep Learning', 'Data Science')
    """)
    ai_jobs = cursor.fetchone()[0]
    
    # AI/ML skills breakdown
    ai_skills = ['AI', 'Machine Learning', 'Deep Learning', 'Data Science', 
                 'TensorFlow', 'PyTorch', 'Keras']
    
    cursor.execute(f"""
        SELECT skill_name, COUNT(*) as count FROM job_skills
        WHERE skill_name IN ({','.join(['?']*len(ai_skills))})
        GROUP BY skill_name ORDER BY count DESC
    """, ai_skills)
    
    skills_data = [{'skill': row[0], 'count': row[1]} for row in cursor.fetchall()]
    
    df = load_csv()
    total_jobs = len(df)
    
    conn.close()
    
    return jsonify({
        'ai_jobs': ai_jobs,
        'total_jobs': total_jobs,
        'percentage': round(ai_jobs / total_jobs * 100, 2),
        'skills': skills_data
    })

@app.route('/api/technologies', methods=['GET'])
def get_technologies():
    """Get technology trends by category"""
    conn = get_db()
    cursor = conn.cursor()
    
    categories = {
        'languages': ['Python', 'Java', 'JavaScript', 'C++', 'C#', 'PHP', 'Go'],
        'databases': ['SQL', 'MySQL', 'PostgreSQL', 'MongoDB', 'Oracle', 'Redis'],
        'frameworks': ['React', 'Angular', 'Vue.js', 'Node.js', 'Django', 'Flask'],
        'cloud': ['AWS', 'Azure', 'GCP', 'Docker', 'Kubernetes', 'Jenkins']
    }
    
    result = {}
    
    for category, skills in categories.items():
        cursor.execute(f"""
            SELECT skill_name, COUNT(*) as count FROM job_skills
            WHERE skill_name IN ({','.join(['?']*len(skills))})
            GROUP BY skill_name ORDER BY count DESC
        """, skills)
        
        result[category] = [{'skill': row[0], 'count': row[1]} 
                           for row in cursor.fetchall()]
    
    conn.close()
    return jsonify(result)

@app.route('/api/filters', methods=['GET'])
def get_filters():
    """Get available filter options"""
    df = load_csv()
    
    return jsonify({
        'locations': sorted(df['location'].unique().tolist()),
        'levels': sorted(df['job_level'].unique().tolist())
    })

# ============================================================================
# RUN SERVER
# ============================================================================

if __name__ == '__main__':
    app.run(debug=True, port=5001)
