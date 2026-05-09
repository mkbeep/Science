"""
IT JOBS VIETNAM - REST API
Flask backend API for React frontend
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
import sqlite3
import pandas as pd
from collections import Counter
import unicodedata

app = Flask(__name__)
CORS(app)  # Enable CORS for React frontend

# Helper function to normalize Vietnamese text
def normalize_text(text):
    """Normalize Vietnamese text for better search"""
    if pd.isna(text):
        return ''
    # Convert to lowercase and normalize Unicode
    text = str(text).lower()
    # Normalize Unicode (NFC form)
    text = unicodedata.normalize('NFC', text)
    return text

# Database connection
def get_db():
    conn = sqlite3.connect('../it_jobs_vietnam.db')
    conn.row_factory = sqlite3.Row
    return conn

# Load data from database (instead of CSV)
def load_data_from_db():
    """Load jobs from database instead of CSV"""
    conn = get_db()
    # Try to load from jobs_realtime first (real-time data)
    try:
        df = pd.read_sql_query("SELECT * FROM jobs_realtime", conn)
        if len(df) > 0:
            conn.close()
            return df
    except:
        pass
    
    # Fallback to old jobs table if jobs_realtime doesn't exist or is empty
    try:
        df = pd.read_sql_query("SELECT * FROM jobs", conn)
        conn.close()
        return df
    except:
        pass
    
    # Last resort: load from CSV
    conn.close()
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
    df = load_data_from_db()
    conn = get_db()
    cursor = conn.cursor()
    
    # Try to get unique skills from jobs_realtime first
    try:
        cursor.execute("SELECT COUNT(DISTINCT skill_name) FROM job_skills_realtime")
        unique_skills = cursor.fetchone()[0]
    except:
        # Fallback to old table
        try:
            cursor.execute("SELECT COUNT(DISTINCT skill_name) FROM job_skills")
            unique_skills = cursor.fetchone()[0]
        except:
            unique_skills = 0
    
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
    
    df = load_data_from_db()
    
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
    
    print(f"[SEARCH] Params - skill: '{skill}', location: '{location}', level: '{level}'")
    
    df = load_data_from_db()
    print(f"[SEARCH] Total jobs loaded: {len(df)}")
    
    # Normalize search term
    if skill:
        skill_normalized = normalize_text(skill)
        print(f"[SEARCH] Normalized skill: '{skill_normalized}'")
        
        # Create normalized columns for search
        df['skills_normalized'] = df['skills'].apply(normalize_text)
        df['title_normalized'] = df['title'].apply(normalize_text)
        
        # Search in normalized text
        mask = (
            df['skills_normalized'].str.contains(skill_normalized, na=False) |
            df['title_normalized'].str.contains(skill_normalized, na=False)
        )
        df = df[mask]
        print(f"[SEARCH] After skill filter: {len(df)} jobs")
    
    if location:
        location_normalized = normalize_text(location)
        df['location_normalized'] = df['location'].apply(normalize_text)
        df = df[df['location_normalized'].str.contains(location_normalized, na=False)]
        print(f"[SEARCH] After location filter: {len(df)} jobs")
    
    if level:
        level_normalized = normalize_text(level)
        df['job_level_normalized'] = df['job_level'].apply(normalize_text)
        df = df[df['job_level_normalized'].str.contains(level_normalized, na=False)]
        print(f"[SEARCH] After level filter: {len(df)} jobs")
    
    # Remove normalized columns before returning
    cols_to_drop = [col for col in df.columns if col.endswith('_normalized')]
    df = df.drop(columns=cols_to_drop, errors='ignore')
    
    # Replace NaN/None values with empty string for proper JSON serialization
    df = df.fillna('')
    
    jobs = df.to_dict('records')
    print(f"[SEARCH] Final result: {len(jobs)} jobs")
    
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
    
    # Try jobs_realtime first
    try:
        cursor.execute("""
            SELECT skill_name, COUNT(*) as count
            FROM job_skills_realtime
            GROUP BY skill_name
            ORDER BY count DESC
            LIMIT ?
        """, (limit,))
        skills = [{'skill': row[0], 'count': row[1]} for row in cursor.fetchall()]
        
        if len(skills) > 0:
            conn.close()
            return jsonify(skills)
    except:
        pass
    
    # Fallback to old table
    try:
        cursor.execute("""
            SELECT skill_name, COUNT(*) as count
            FROM job_skills
            GROUP BY skill_name
            ORDER BY count DESC
            LIMIT ?
        """, (limit,))
        skills = [{'skill': row[0], 'count': row[1]} for row in cursor.fetchall()]
    except:
        skills = []
    
    conn.close()
    return jsonify(skills)

@app.route('/api/skills/technical', methods=['GET'])
def get_technical_skills():
    """Get top technical skills only (exclude soft skills)"""
    limit = request.args.get('limit', 30, type=int)
    
    # Define technical skills categories
    technical_keywords = [
        # Programming Languages
        'Python', 'Java', 'JavaScript', 'TypeScript', 'C++', 'C#', 'PHP', 'Go', 'Rust', 
        'Ruby', 'Swift', 'Kotlin', 'Scala', 'R', 'MATLAB', 'Perl',
        
        # Web Technologies
        'HTML', 'CSS', 'React', 'Angular', 'Vue', 'Node.js', 'Express', 'Django', 
        'Flask', 'Spring', 'ASP.NET', 'Laravel', 'jQuery', 'Bootstrap', 'Tailwind',
        
        # Mobile
        'Android', 'iOS', 'React Native', 'Flutter', 'Xamarin',
        
        # Databases
        'SQL', 'MySQL', 'PostgreSQL', 'MongoDB', 'Oracle', 'Redis', 'Cassandra',
        'DynamoDB', 'SQLite', 'MariaDB', 'Elasticsearch',
        
        # Cloud & DevOps
        'AWS', 'Azure', 'GCP', 'Docker', 'Kubernetes', 'Jenkins', 'GitLab', 'GitHub',
        'Terraform', 'Ansible', 'CI/CD', 'DevOps',
        
        # Data & AI
        'Machine Learning', 'Deep Learning', 'AI', 'Data Science', 'Data Analysis',
        'TensorFlow', 'PyTorch', 'Keras', 'Pandas', 'NumPy', 'Scikit-learn',
        'Spark', 'Hadoop', 'Kafka', 'Airflow',
        
        # Tools & Others
        'Git', 'Linux', 'Unix', 'Windows Server', 'REST API', 'GraphQL', 
        'Microservices', 'Agile', 'Scrum', 'JIRA', 'Selenium', 'JUnit'
    ]
    
    conn = get_db()
    cursor = conn.cursor()
    
    # Try jobs_realtime first
    table_name = 'job_skills_realtime'
    try:
        cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
        count = cursor.fetchone()[0]
        if count == 0:
            raise Exception("Empty table")
    except:
        table_name = 'job_skills'
    
    # Get all skills and filter technical ones
    try:
        cursor.execute(f"""
            SELECT skill_name, COUNT(*) as count
            FROM {table_name}
            GROUP BY skill_name
            ORDER BY count DESC
        """)
        
        all_skills = cursor.fetchall()
        
        # Filter technical skills
        technical_skills = []
        for skill_name, count in all_skills:
            # Check if skill matches any technical keyword (case insensitive)
            skill_lower = skill_name.lower()
            is_technical = any(keyword.lower() in skill_lower for keyword in technical_keywords)
            
            if is_technical:
                technical_skills.append({'skill': skill_name, 'count': count})
                
                if len(technical_skills) >= limit:
                    break
        
        conn.close()
        return jsonify(technical_skills)
        
    except Exception as e:
        conn.close()
        return jsonify([])


@app.route('/api/locations/top', methods=['GET'])
def get_top_locations():
    """Get top locations"""
    limit = request.args.get('limit', 10, type=int)
    
    df = load_data_from_db()
    top_locs = df['location'].value_counts().head(limit)
    
    locations = [{'location': loc, 'count': int(count)} 
                 for loc, count in top_locs.items()]
    
    return jsonify(locations)

@app.route('/api/companies/top', methods=['GET'])
def get_top_companies():
    """Get top companies"""
    limit = request.args.get('limit', 15, type=int)
    
    df = load_data_from_db()
    top_companies = df['company'].value_counts().head(limit)
    
    companies = [{'company': comp, 'count': int(count)} 
                 for comp, count in top_companies.items()]
    
    return jsonify(companies)

@app.route('/api/levels', methods=['GET'])
def get_job_levels():
    """Get job level distribution"""
    df = load_data_from_db()
    levels = df['job_level'].value_counts()
    
    level_data = [{'level': level, 'count': int(count)} 
                  for level, count in levels.items()]
    
    return jsonify(level_data)

@app.route('/api/cities/compare', methods=['GET'])
def compare_cities():
    """Compare Hanoi vs HCM with technical skills only"""
    df = load_data_from_db()
    conn = get_db()
    cursor = conn.cursor()
    
    hanoi = df[df['location'] == 'Hà Nội']
    hcm = df[df['location'] == 'Hồ Chí Minh']
    
    # Define technical skills keywords (same as in get_technical_skills)
    technical_keywords = [
        'Python', 'Java', 'JavaScript', 'TypeScript', 'C++', 'C#', 'PHP', 'Go', 'Rust', 
        'Ruby', 'Swift', 'Kotlin', 'Scala', 'R', 'MATLAB', 'Perl',
        'HTML', 'CSS', 'React', 'Angular', 'Vue', 'Node.js', 'Express', 'Django', 
        'Flask', 'Spring', 'ASP.NET', 'Laravel', 'jQuery', 'Bootstrap', 'Tailwind',
        'Android', 'iOS', 'React Native', 'Flutter', 'Xamarin',
        'SQL', 'MySQL', 'PostgreSQL', 'MongoDB', 'Oracle', 'Redis', 'Cassandra',
        'DynamoDB', 'SQLite', 'MariaDB', 'Elasticsearch',
        'AWS', 'Azure', 'GCP', 'Docker', 'Kubernetes', 'Jenkins', 'GitLab', 'GitHub',
        'Terraform', 'Ansible', 'CI/CD', 'DevOps',
        'Machine Learning', 'Deep Learning', 'AI', 'Data Science', 'Data Analysis',
        'TensorFlow', 'PyTorch', 'Keras', 'Pandas', 'NumPy', 'Scikit-learn',
        'Spark', 'Hadoop', 'Kafka', 'Airflow',
        'Git', 'Linux', 'Unix', 'Windows Server', 'REST API', 'GraphQL', 
        'Microservices', 'Agile', 'Scrum', 'JIRA', 'Selenium', 'JUnit'
    ]
    
    # Determine which table to use
    table_name = 'job_skills_realtime'
    jobs_table = 'jobs_realtime'
    try:
        cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
        count = cursor.fetchone()[0]
        if count == 0:
            raise Exception("Empty table")
    except:
        table_name = 'job_skills'
        jobs_table = 'jobs'
    
    # Helper function to filter technical skills
    def filter_technical_skills(skills_list):
        technical_skills = []
        for skill_name, count in skills_list:
            skill_lower = skill_name.lower()
            is_technical = any(keyword.lower() in skill_lower for keyword in technical_keywords)
            if is_technical:
                technical_skills.append({'skill': skill_name, 'count': count})
                if len(technical_skills) >= 10:
                    break
        return technical_skills
    
    # Top skills in Hanoi
    try:
        cursor.execute(f"""
            SELECT js.skill_name, COUNT(*) as count
            FROM {table_name} js JOIN {jobs_table} j ON js.job_id = j.job_id
            WHERE j.location = 'Hà Nội'
            GROUP BY js.skill_name ORDER BY count DESC
        """)
        hanoi_all_skills = cursor.fetchall()
        hanoi_skills = filter_technical_skills(hanoi_all_skills)
    except:
        hanoi_skills = []
    
    # Top skills in HCM
    try:
        cursor.execute(f"""
            SELECT js.skill_name, COUNT(*) as count
            FROM {table_name} js JOIN {jobs_table} j ON js.job_id = j.job_id
            WHERE j.location = 'Hồ Chí Minh'
            GROUP BY js.skill_name ORDER BY count DESC
        """)
        hcm_all_skills = cursor.fetchall()
        hcm_skills = filter_technical_skills(hcm_all_skills)
    except:
        hcm_skills = []
    
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
    
    # Determine which table to use
    table_name = 'job_skills_realtime'
    jobs_table = 'jobs_realtime'
    try:
        cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
        count = cursor.fetchone()[0]
        if count == 0:
            raise Exception("Empty table")
    except:
        table_name = 'job_skills'
        jobs_table = 'jobs'
    
    # AI/ML jobs count
    try:
        cursor.execute(f"""
            SELECT COUNT(DISTINCT j.job_id)
            FROM {jobs_table} j JOIN {table_name} js ON j.job_id = js.job_id
            WHERE js.skill_name IN ('AI', 'Machine Learning', 'Deep Learning', 'Data Science')
        """)
        ai_jobs = cursor.fetchone()[0]
    except:
        ai_jobs = 0
    
    # AI/ML skills breakdown
    ai_skills = ['AI', 'Machine Learning', 'Deep Learning', 'Data Science', 
                 'TensorFlow', 'PyTorch', 'Keras']
    
    try:
        cursor.execute(f"""
            SELECT skill_name, COUNT(*) as count FROM {table_name}
            WHERE skill_name IN ({','.join(['?']*len(ai_skills))})
            GROUP BY skill_name ORDER BY count DESC
        """, ai_skills)
        skills_data = [{'skill': row[0], 'count': row[1]} for row in cursor.fetchall()]
    except:
        skills_data = []
    
    df = load_data_from_db()
    total_jobs = len(df)
    
    conn.close()
    
    return jsonify({
        'ai_jobs': ai_jobs,
        'total_jobs': total_jobs,
        'percentage': round(ai_jobs / total_jobs * 100, 2) if total_jobs > 0 else 0,
        'skills': skills_data
    })

@app.route('/api/technologies', methods=['GET'])
def get_technologies():
    """Get technology trends by category"""
    conn = get_db()
    cursor = conn.cursor()
    
    # Determine which table to use
    table_name = 'job_skills_realtime'
    try:
        cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
        count = cursor.fetchone()[0]
        if count == 0:
            raise Exception("Empty table")
    except:
        table_name = 'job_skills'
    
    categories = {
        'languages': ['Python', 'Java', 'JavaScript', 'C++', 'C#', 'PHP', 'Go'],
        'databases': ['SQL', 'MySQL', 'PostgreSQL', 'MongoDB', 'Oracle', 'Redis'],
        'frameworks': ['React', 'Angular', 'Vue.js', 'Node.js', 'Django', 'Flask'],
        'cloud': ['AWS', 'Azure', 'GCP', 'Docker', 'Kubernetes', 'Jenkins']
    }
    
    result = {}
    
    for category, skills in categories.items():
        try:
            cursor.execute(f"""
                SELECT skill_name, COUNT(*) as count FROM {table_name}
                WHERE skill_name IN ({','.join(['?']*len(skills))})
                GROUP BY skill_name ORDER BY count DESC
            """, skills)
            result[category] = [{'skill': row[0], 'count': row[1]} 
                               for row in cursor.fetchall()]
        except:
            result[category] = []
    
    conn.close()
    return jsonify(result)

@app.route('/api/filters', methods=['GET'])
def get_filters():
    """Get available filter options"""
    df = load_data_from_db()
    
    return jsonify({
        'locations': sorted(df['location'].unique().tolist()),
        'levels': sorted(df['job_level'].unique().tolist())
    })

# ============================================================================
# SKILL RELATIONSHIP ANALYSIS
# ============================================================================

@app.route('/api/skills/relationships', methods=['GET'])
def get_skill_relationships():
    """Analyze which skills appear together in job postings"""
    limit = request.args.get('limit', 20, type=int)
    min_count = request.args.get('min_count', 5, type=int)
    
    conn = get_db()
    cursor = conn.cursor()
    
    # Determine which table to use
    table_name = 'job_skills_realtime'
    try:
        cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
        count = cursor.fetchone()[0]
        if count == 0:
            raise Exception("Empty table")
    except:
        table_name = 'job_skills'
    
    # Define technical skills to focus on
    focus_skills = [
        'Python', 'Java', 'JavaScript', 'TypeScript', 'C++', 'C#', 'PHP', 'Go',
        'React', 'Angular', 'Vue', 'Node.js', 'Django', 'Flask', 'Spring',
        'SQL', 'MySQL', 'PostgreSQL', 'MongoDB', 'Oracle', 'Redis',
        'AWS', 'Azure', 'GCP', 'Docker', 'Kubernetes', 'Jenkins',
        'Machine Learning', 'Deep Learning', 'AI', 'Data Science', 'Data Analysis',
        'TensorFlow', 'PyTorch', 'Pandas', 'NumPy'
    ]
    
    # Get skill pairs that appear together
    try:
        cursor.execute(f"""
            SELECT 
                s1.skill_name as skill1,
                s2.skill_name as skill2,
                COUNT(*) as count
            FROM {table_name} s1
            JOIN {table_name} s2 ON s1.job_id = s2.job_id
            WHERE s1.skill_name < s2.skill_name
            GROUP BY s1.skill_name, s2.skill_name
            HAVING count >= ?
            ORDER BY count DESC
            LIMIT ?
        """, (min_count, limit * 3))
        
        all_pairs = cursor.fetchall()
        
        # Filter to only include focus skills
        relationships = []
        for skill1, skill2, count in all_pairs:
            # Check if both skills are in focus list (case insensitive)
            skill1_match = any(fs.lower() in skill1.lower() for fs in focus_skills)
            skill2_match = any(fs.lower() in skill2.lower() for fs in focus_skills)
            
            if skill1_match and skill2_match:
                relationships.append({
                    'skill1': skill1,
                    'skill2': skill2,
                    'count': count
                })
                
                if len(relationships) >= limit:
                    break
        
        conn.close()
        return jsonify(relationships)
        
    except Exception as e:
        conn.close()
        return jsonify([])

@app.route('/api/skills/network', methods=['GET'])
def get_skill_network():
    """Get skill network data for graph visualization"""
    top_skills_count = request.args.get('top_skills', 15, type=int)
    min_connection = request.args.get('min_connection', 3, type=int)
    
    conn = get_db()
    cursor = conn.cursor()
    
    # Determine which table to use
    table_name = 'job_skills_realtime'
    try:
        cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
        count = cursor.fetchone()[0]
        if count == 0:
            raise Exception("Empty table")
    except:
        table_name = 'job_skills'
    
    # Define technical skills
    focus_skills = [
        'Python', 'Java', 'JavaScript', 'TypeScript', 'C++', 'C#', 'React', 
        'Angular', 'Vue', 'Node.js', 'Django', 'Flask', 'SQL', 'MySQL', 
        'PostgreSQL', 'MongoDB', 'AWS', 'Azure', 'Docker', 'Kubernetes',
        'Machine Learning', 'AI', 'Data Science', 'Data Analysis', 'TensorFlow', 'PyTorch'
    ]
    
    try:
        # Get top technical skills
        cursor.execute(f"""
            SELECT skill_name, COUNT(*) as count
            FROM {table_name}
            GROUP BY skill_name
            ORDER BY count DESC
        """)
        
        all_skills = cursor.fetchall()
        
        # Filter technical skills
        top_skills = []
        for skill_name, count in all_skills:
            skill_lower = skill_name.lower()
            is_technical = any(fs.lower() in skill_lower for fs in focus_skills)
            if is_technical:
                top_skills.append({'name': skill_name, 'value': count})
                if len(top_skills) >= top_skills_count:
                    break
        
        skill_names = [s['name'] for s in top_skills]
        
        # Get connections between these skills
        placeholders = ','.join(['?'] * len(skill_names))
        cursor.execute(f"""
            SELECT 
                s1.skill_name as skill1,
                s2.skill_name as skill2,
                COUNT(*) as count
            FROM {table_name} s1
            JOIN {table_name} s2 ON s1.job_id = s2.job_id
            WHERE s1.skill_name < s2.skill_name
                AND s1.skill_name IN ({placeholders})
                AND s2.skill_name IN ({placeholders})
            GROUP BY s1.skill_name, s2.skill_name
            HAVING count >= ?
            ORDER BY count DESC
        """, skill_names + skill_names + [min_connection])
        
        links = []
        for skill1, skill2, count in cursor.fetchall():
            links.append({
                'source': skill1,
                'target': skill2,
                'value': count
            })
        
        conn.close()
        
        return jsonify({
            'nodes': top_skills,
            'links': links
        })
        
    except Exception as e:
        conn.close()
        return jsonify({'nodes': [], 'links': []})

@app.route('/api/skills/tech-stacks', methods=['GET'])
def get_tech_stacks():
    """Get common tech stacks (skill combinations)"""
    limit = request.args.get('limit', 10, type=int)
    
    conn = get_db()
    cursor = conn.cursor()
    
    # Determine which table to use
    table_name = 'job_skills_realtime'
    jobs_table = 'jobs_realtime'
    try:
        cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
        count = cursor.fetchone()[0]
        if count == 0:
            raise Exception("Empty table")
    except:
        table_name = 'job_skills'
        jobs_table = 'jobs'
    
    try:
        # Get jobs with their skills
        cursor.execute(f"""
            SELECT job_id, GROUP_CONCAT(skill_name, ', ') as skills
            FROM {table_name}
            GROUP BY job_id
        """)
        
        job_skills = cursor.fetchall()
        
        # Count skill combinations
        from collections import Counter
        tech_stacks = Counter()
        
        for job_id, skills_str in job_skills:
            if skills_str:
                skills = [s.strip() for s in skills_str.split(',')]
                # Only consider jobs with 2-5 skills
                if 2 <= len(skills) <= 5:
                    # Sort skills to normalize combinations
                    skills_tuple = tuple(sorted(skills))
                    tech_stacks[skills_tuple] += 1
        
        # Get top tech stacks
        top_stacks = []
        for skills_tuple, count in tech_stacks.most_common(limit):
            top_stacks.append({
                'skills': list(skills_tuple),
                'count': count
            })
        
        conn.close()
        return jsonify(top_stacks)
        
    except Exception as e:
        conn.close()
        return jsonify([])

# ============================================================================
# TREND ANALYSIS ENDPOINTS
# ============================================================================

@app.route('/api/trends/jobs', methods=['GET'])
def get_jobs_trend():
    """Get jobs posted over time"""
    days = request.args.get('days', 30, type=int)
    
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT date, total_jobs, is_simulated
        FROM job_trends
        ORDER BY date DESC
        LIMIT ?
    """, (days,))
    
    rows = cursor.fetchall()
    conn.close()
    
    # Reverse to get chronological order
    data = [{'date': row[0], 'count': row[1], 'simulated': bool(row[2])} 
            for row in reversed(rows)]
    
    return jsonify(data)

@app.route('/api/trends/ai', methods=['GET'])
def get_ai_trend():
    """Get AI/ML jobs growth over time"""
    days = request.args.get('days', 30, type=int)
    
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT date, ai_ml_jobs, total_jobs, is_simulated
        FROM job_trends
        ORDER BY date DESC
        LIMIT ?
    """, (days,))
    
    rows = cursor.fetchall()
    conn.close()
    
    data = [{
        'date': row[0], 
        'ai_jobs': row[1],
        'total_jobs': row[2],
        'percentage': round((row[1] / row[2]) * 100, 2) if row[2] > 0 else 0,
        'simulated': bool(row[3])
    } for row in reversed(rows)]
    
    return jsonify(data)

@app.route('/api/trends/skills', methods=['GET'])
def get_skills_trend():
    """Get top skills demand over time"""
    days = request.args.get('days', 30, type=int)
    
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT date, python_jobs, java_jobs, react_jobs, data_analysis_jobs, is_simulated
        FROM job_trends
        ORDER BY date DESC
        LIMIT ?
    """, (days,))
    
    rows = cursor.fetchall()
    conn.close()
    
    data = [{
        'date': row[0],
        'Python': row[1],
        'Java': row[2],
        'React': row[3],
        'Data Analysis': row[4],
        'simulated': bool(row[5])
    } for row in reversed(rows)]
    
    return jsonify(data)

@app.route('/api/trends/summary', methods=['GET'])
def get_trends_summary():
    """Get trend summary statistics"""
    conn = get_db()
    cursor = conn.cursor()
    
    # Get last 30 days
    cursor.execute("""
        SELECT 
            MIN(total_jobs) as min_jobs,
            MAX(total_jobs) as max_jobs,
            AVG(total_jobs) as avg_jobs,
            MIN(ai_ml_jobs) as min_ai,
            MAX(ai_ml_jobs) as max_ai,
            AVG(ai_ml_jobs) as avg_ai
        FROM job_trends
        WHERE date >= date('now', '-30 days')
    """)
    
    row = cursor.fetchone()
    
    # Get growth rate (compare TODAY vs YESTERDAY)
    cursor.execute("""
        SELECT total_jobs
        FROM job_trends
        WHERE date = date('now')
    """)
    today_result = cursor.fetchone()
    today_jobs = today_result[0] if today_result else 0
    
    cursor.execute("""
        SELECT total_jobs
        FROM job_trends
        WHERE date = date('now', '-1 day')
    """)
    yesterday_result = cursor.fetchone()
    yesterday_jobs = yesterday_result[0] if yesterday_result else 0
    
    # Calculate daily growth rate
    growth_rate = 0
    if yesterday_jobs and yesterday_jobs > 0:
        growth_rate = round(((today_jobs - yesterday_jobs) / yesterday_jobs) * 100, 2)
    
    # Get last 7 days average for comparison
    cursor.execute("""
        SELECT AVG(total_jobs) as avg_jobs
        FROM job_trends
        WHERE date >= date('now', '-7 days')
    """)
    last_week_avg_result = cursor.fetchone()
    last_week_avg = last_week_avg_result[0] if last_week_avg_result else 0
    
    cursor.execute("""
        SELECT AVG(total_jobs) as avg_jobs
        FROM job_trends
        WHERE date BETWEEN date('now', '-14 days') AND date('now', '-7 days')
    """)
    prev_week_avg_result = cursor.fetchone()
    prev_week_avg = prev_week_avg_result[0] if prev_week_avg_result else 0
    
    # Calculate weekly growth rate
    weekly_growth_rate = 0
    if prev_week_avg and prev_week_avg > 0:
        weekly_growth_rate = round(((last_week_avg - prev_week_avg) / prev_week_avg) * 100, 2)
    
    conn.close()
    
    return jsonify({
        'min_jobs': int(row[0]) if row[0] else 0,
        'max_jobs': int(row[1]) if row[1] else 0,
        'avg_jobs': round(row[2], 0) if row[2] else 0,
        'min_ai': int(row[3]) if row[3] else 0,
        'max_ai': int(row[4]) if row[4] else 0,
        'avg_ai': round(row[5], 0) if row[5] else 0,
        'growth_rate': growth_rate,  # Daily growth rate
        'today_jobs': today_jobs,
        'yesterday_jobs': yesterday_jobs,
        'weekly_growth_rate': weekly_growth_rate,  # Weekly growth rate
        'last_week_avg': round(last_week_avg, 0) if last_week_avg else 0,
        'prev_week_avg': round(prev_week_avg, 0) if prev_week_avg else 0
    })

# ============================================================================
# AI INSIGHTS ENDPOINTS
# ============================================================================

# ============================================================================
# RUN SERVER
# ============================================================================

if __name__ == '__main__':
    app.run(debug=True, port=5001)
