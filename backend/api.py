"""
IT JOBS VIETNAM - REST API
Flask backend API for React frontend
"""

import os
import sqlite3
import threading
import unicodedata
from collections import Counter

import pandas as pd
from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_socketio import SocketIO

app = Flask(__name__)
CORS(app)  # Enable CORS for React frontend

_cors_origins_env = os.environ.get(
    'SOCKETIO_CORS_ORIGINS',
    'http://127.0.0.1:3000,http://localhost:3000,*',
)
_cors_origins = [x.strip() for x in _cors_origins_env.split(',') if x.strip()]

socketio = SocketIO(app, cors_allowed_origins=_cors_origins, async_mode='threading')

_ws_lock = threading.Lock()
_ws_connections = 0

CRAWL_NOTIFY_SECRET = os.environ.get('CRAWL_NOTIFY_SECRET', '').strip()

limiter = Limiter(
    key_func=get_remote_address,
    app=app,
    storage_uri=os.environ.get('RATE_LIMIT_STORAGE_URI', 'memory://'),
    default_limits=['300 per minute'],
    headers_enabled=True,
)


@socketio.on('connect')
def _ws_on_connect(_auth=None):
    global _ws_connections
    with _ws_lock:
        _ws_connections += 1


@socketio.on('disconnect')
def _ws_on_disconnect():
    global _ws_connections
    with _ws_lock:
        _ws_connections = max(0, _ws_connections - 1)

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


def table_exists(conn, table_name: str) -> bool:
    cur = conn.cursor()
    cur.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name=?",
        (table_name,),
    )
    return cur.fetchone() is not None


def column_exists(conn, table_name: str, column_name: str) -> bool:
    cur = conn.cursor()
    try:
        cur.execute(f"PRAGMA table_info({table_name})")
        return any(row[1] == column_name for row in cur.fetchall())
    except sqlite3.Error:
        return False


def get_skill_column(conn, table_name: str) -> str:
    return 'canonical_skill' if column_exists(conn, table_name, 'canonical_skill') else 'skill_name'


def get_location_column(conn, table_name: str) -> str:
    return 'canonical_location' if column_exists(conn, table_name, 'canonical_location') else 'location'

# ============================================================================
# ENDPOINTS
# ============================================================================

@app.route('/api/health', methods=['GET'])
@limiter.exempt
def health_check():
    """Health check endpoint (REST + SQLite reachability)."""
    api_ok = True
    db_reachable = False
    websocket_clients = 0
    with _ws_lock:
        websocket_clients = _ws_connections
    try:
        conn = get_db()
        conn.cursor().execute('SELECT 1')
        conn.close()
        db_reachable = True
    except sqlite3.Error:
        db_reachable = False

    overall = api_ok and db_reachable
    return jsonify(
        {
            'status': 'ok' if overall else 'degraded',
            'api': 'ok' if api_ok else 'down',
            'database': 'ok' if db_reachable else 'unreachable',
            'websocket_clients': websocket_clients,
        },
    )


@app.route('/api/monitoring/status', methods=['GET'])
@limiter.exempt
def monitoring_status():
    """Last crawl record + websocket fan-out (operators / Grafana-style polling)."""
    with _ws_lock:
        websocket_clients = _ws_connections

    crawl = None
    try:
        conn = get_db()
        cur = conn.cursor()
        cur.execute(
            '''
            SELECT name FROM sqlite_master
            WHERE type='table' AND name='crawl_runs'
            ''',
        )
        if cur.fetchone():
            cur.execute(
                '''
                SELECT started_at, finished_at, status, jobs_crawled,
                       new_jobs, updated_jobs, skipped_duplicates, error_message
                FROM crawl_runs
                ORDER BY id DESC LIMIT 1
                ''',
            )
            row = cur.fetchone()
            if row:
                crawl = {
                    'started_at': row[0],
                    'finished_at': row[1],
                    'status': row[2],
                    'jobs_crawled': row[3],
                    'new_jobs': row[4],
                    'updated_jobs': row[5],
                    'skipped_duplicates': row[6],
                    'error_message': row[7],
                }
        conn.close()
    except sqlite3.Error as e:
        return jsonify({'error': str(e), 'websocket_clients': websocket_clients}), 500

    return jsonify(
        {
            'websocket_clients': websocket_clients,
            'last_crawl': crawl,
            'secret_configured': bool(CRAWL_NOTIFY_SECRET),
        },
    )


@app.route('/api/internal/crawl-complete', methods=['POST'])
@limiter.exempt
def internal_crawl_complete():
    """Called by crawler to fan-out realtime messages to browsers."""
    if CRAWL_NOTIFY_SECRET:
        hdr = request.headers.get('X-Crawl-Secret', '')
        if hdr != CRAWL_NOTIFY_SECRET:
            return jsonify({'error': 'unauthorized'}), 401
    payload = request.get_json(silent=True) or {}
    socketio.emit('crawl_update', payload)
    with _ws_lock:
        n = _ws_connections
    return jsonify({'ok': True, 'websocket_clients': n})

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
        location_source_col = 'canonical_location' if 'canonical_location' in df.columns else 'location'
        df['location_normalized'] = df[location_source_col].apply(normalize_text)
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
        skill_col = get_skill_column(conn, 'job_skills_realtime')
        cursor.execute("""
            SELECT {skill_col}, COUNT(*) as count
            FROM job_skills_realtime
            WHERE {skill_col} IS NOT NULL AND TRIM({skill_col}) != ''
            GROUP BY {skill_col}
            ORDER BY count DESC
            LIMIT ?
        """.format(skill_col=skill_col), (limit,))
        skills = [{'skill': row[0], 'count': row[1]} for row in cursor.fetchall()]
        
        if len(skills) > 0:
            conn.close()
            return jsonify(skills)
    except:
        pass
    
    # Fallback to old table
    try:
        legacy_col = get_skill_column(conn, 'job_skills')
        cursor.execute("""
            SELECT {legacy_col}, COUNT(*) as count
            FROM job_skills
            WHERE {legacy_col} IS NOT NULL AND TRIM({legacy_col}) != ''
            GROUP BY {legacy_col}
            ORDER BY count DESC
            LIMIT ?
        """.format(legacy_col=legacy_col), (limit,))
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
    
    skill_col = get_skill_column(conn, table_name)

    # Get all skills and filter technical ones
    try:
        cursor.execute(f"""
            SELECT {skill_col}, COUNT(*) as count
            FROM {table_name}
            WHERE {skill_col} IS NOT NULL AND TRIM({skill_col}) != ''
            GROUP BY {skill_col}
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
    source_col = 'canonical_location' if 'canonical_location' in df.columns else 'location'
    top_locs = df[source_col].fillna('').replace('', 'Unknown').value_counts().head(limit)
    
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
    
    location_col = 'canonical_location' if 'canonical_location' in df.columns else 'location'
    hanoi = df[df[location_col] == 'Hà Nội']
    hcm = df[df[location_col] == 'Hồ Chí Minh']
    
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
    
    # Get TOTAL NEW JOBS in last 7 days (this week)
    cursor.execute("""
        SELECT SUM(new_jobs_today) as total_new_jobs
        FROM job_trends
        WHERE date >= date('now', '-7 days')
    """)
    last_week_new_result = cursor.fetchone()
    last_week_new_jobs = last_week_new_result[0] if last_week_new_result and last_week_new_result[0] else 0
    
    # Get TOTAL NEW JOBS in previous 7 days (last week)
    cursor.execute("""
        SELECT SUM(new_jobs_today) as total_new_jobs
        FROM job_trends
        WHERE date BETWEEN date('now', '-14 days') AND date('now', '-8 days')
    """)
    prev_week_new_result = cursor.fetchone()
    prev_week_new_jobs = prev_week_new_result[0] if prev_week_new_result and prev_week_new_result[0] else 0
    
    # Calculate weekly growth rate based on NEW JOBS
    weekly_growth_rate = 0
    if prev_week_new_jobs and prev_week_new_jobs > 0:
        weekly_growth_rate = round(((last_week_new_jobs - prev_week_new_jobs) / prev_week_new_jobs) * 100, 2)
    
    # Get new jobs today and yesterday
    cursor.execute("""
        SELECT new_jobs_today
        FROM job_trends
        WHERE date = date('now')
    """)
    today_new_result = cursor.fetchone()
    today_new_jobs = today_new_result[0] if today_new_result and today_new_result[0] is not None else 0
    
    cursor.execute("""
        SELECT new_jobs_today
        FROM job_trends
        WHERE date = date('now', '-1 day')
    """)
    yesterday_new_result = cursor.fetchone()
    yesterday_new_jobs = yesterday_new_result[0] if yesterday_new_result and yesterday_new_result[0] is not None else 0
    
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
        'today_new_jobs': today_new_jobs,  # NEW: jobs added today
        'yesterday_new_jobs': yesterday_new_jobs,  # NEW: jobs added yesterday
        'weekly_growth_rate': weekly_growth_rate,  # Weekly growth rate based on new jobs
        'last_week_new_jobs': int(last_week_new_jobs),  # Total new jobs this week
        'prev_week_new_jobs': int(prev_week_new_jobs)  # Total new jobs last week
    })

@app.route('/api/trends/new-jobs', methods=['GET'])
def get_new_jobs_trend():
    """Get new jobs added each day"""
    days = request.args.get('days', 30, type=int)
    
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT date, new_jobs_today, total_jobs, is_simulated
        FROM job_trends
        ORDER BY date DESC
        LIMIT ?
    """, (days,))
    
    rows = cursor.fetchall()
    conn.close()
    
    # Reverse to get chronological order
    data = [{
        'date': row[0], 
        'new_jobs': row[1] if row[1] is not None else 0,
        'total_jobs': row[2],
        'simulated': bool(row[3])
    } for row in reversed(rows)]
    
    return jsonify(data)


@app.route('/api/trends/emerging-skills', methods=['GET'])
def get_emerging_skills():
    """Top emerging skills by recent growth vs previous window."""
    days = request.args.get('days', 14, type=int)
    limit = request.args.get('limit', 15, type=int)

    conn = get_db()
    if not table_exists(conn, 'job_skills_realtime') or not table_exists(conn, 'jobs_realtime'):
        conn.close()
        return jsonify([])

    skill_col = get_skill_column(conn, 'job_skills_realtime')
    location_col = get_location_column(conn, 'jobs_realtime')
    cursor = conn.cursor()
    cursor.execute(
        f"""
        WITH recent AS (
            SELECT js.{skill_col} AS skill, COUNT(*) AS cnt
            FROM job_skills_realtime js
            JOIN jobs_realtime j ON j.job_id = js.job_id
            WHERE date(j.crawled_date) >= date('now', ?)
              AND js.{skill_col} IS NOT NULL
              AND TRIM(js.{skill_col}) != ''
            GROUP BY js.{skill_col}
        ),
        previous AS (
            SELECT js.{skill_col} AS skill, COUNT(*) AS cnt
            FROM job_skills_realtime js
            JOIN jobs_realtime j ON j.job_id = js.job_id
            WHERE date(j.crawled_date) < date('now', ?)
              AND date(j.crawled_date) >= date('now', ?)
              AND js.{skill_col} IS NOT NULL
              AND TRIM(js.{skill_col}) != ''
            GROUP BY js.{skill_col}
        )
        SELECT
            r.skill,
            r.cnt AS recent_count,
            COALESCE(p.cnt, 0) AS previous_count,
            (r.cnt - COALESCE(p.cnt, 0)) AS delta
        FROM recent r
        LEFT JOIN previous p ON p.skill = r.skill
        ORDER BY delta DESC, recent_count DESC
        LIMIT ?
        """,
        (f'-{days} days', f'-{days} days', f'-{days * 2} days', limit),
    )
    rows = cursor.fetchall()

    cursor.execute(
        f"""
        SELECT {location_col}, COUNT(*)
        FROM jobs_realtime
        GROUP BY {location_col}
        ORDER BY COUNT(*) DESC
        LIMIT 5
        """
    )
    top_locations = [{'location': row[0] or 'Unknown', 'count': row[1]} for row in cursor.fetchall()]
    conn.close()

    return jsonify({
        'window_days': days,
        'skills': [
            {
                'skill': row[0],
                'recent_count': int(row[1]),
                'previous_count': int(row[2]),
                'delta': int(row[3]),
                'growth_rate': round((row[3] / row[2]) * 100, 2) if row[2] else None,
            }
            for row in rows
        ],
        'top_locations': top_locations,
    })


@app.route('/api/insights/data-quality', methods=['GET'])
def get_data_quality_insights():
    """Summarize completeness and dedupe quality from crawler outputs."""
    conn = get_db()
    cursor = conn.cursor()
    has_quality = table_exists(conn, 'jobs_quality_scores')
    has_jobs_rt = table_exists(conn, 'jobs_realtime')
    if not has_jobs_rt:
        # Fallback to jobs table
        has_jobs_rt = table_exists(conn, 'jobs')
        jobs_table = 'jobs'
    else:
        jobs_table = 'jobs_realtime'

    cursor.execute(f"SELECT COUNT(*) FROM {jobs_table}")
    total_jobs = int(cursor.fetchone()[0])

    if has_quality:
        cursor.execute(
            """
            SELECT
                AVG(completeness_score),
                AVG(dedupe_score),
                AVG(quality_score)
            FROM jobs_quality_scores
            """
        )
        avg_row = cursor.fetchone() or (0, 0, 0)
    else:
        avg_row = (0, 0, 0)

    # Check if canonical_location column exists
    location_col = get_location_column(conn, jobs_table)
    
    cursor.execute(
        f"""
        SELECT COUNT(*)
        FROM {jobs_table}
        WHERE {location_col} IS NOT NULL AND TRIM({location_col}) != ''
        """
    )
    canonicalized_locations = int(cursor.fetchone()[0])

    if table_exists(conn, 'job_skills_realtime'):
        skill_col = get_skill_column(conn, 'job_skills_realtime')
        cursor.execute(
            f"""
            SELECT COUNT(*)
            FROM job_skills_realtime
            WHERE {skill_col} IS NOT NULL AND TRIM({skill_col}) != ''
            """
        )
        canonicalized_skills = int(cursor.fetchone()[0])
    elif table_exists(conn, 'job_skills'):
        skill_col = get_skill_column(conn, 'job_skills')
        cursor.execute(
            f"""
            SELECT COUNT(*)
            FROM job_skills
            WHERE {skill_col} IS NOT NULL AND TRIM({skill_col}) != ''
            """
        )
        canonicalized_skills = int(cursor.fetchone()[0])
    else:
        canonicalized_skills = 0
    conn.close()

    return jsonify({
        'total_jobs': total_jobs,
        'avg_completeness_score': round(float(avg_row[0] or 0), 2),
        'avg_dedupe_score': round(float(avg_row[1] or 0), 4),
        'avg_quality_score': round(float(avg_row[2] or 0), 2),
        'canonicalized_locations': canonicalized_locations,
        'canonicalized_skills': canonicalized_skills,
        'location_coverage_pct': round((canonicalized_locations / total_jobs) * 100, 2) if total_jobs else 0,
    })

# ============================================================================
# AI INSIGHTS ENDPOINTS
# ============================================================================

# ============================================================================
# SALARY ANALYSIS ENDPOINTS
# ============================================================================

@app.route('/api/salary/overview', methods=['GET'])
def get_salary_overview():
    """Get salary overview statistics"""
    conn = get_db()
    cursor = conn.cursor()
    
    # Check which table to use
    table_name = 'jobs_realtime' if table_exists(conn, 'jobs_realtime') else 'jobs'
    
    try:
        # Total jobs with salary info
        cursor.execute(f"""
            SELECT COUNT(*) FROM {table_name}
            WHERE (salary_min_monthly IS NOT NULL AND salary_min_monthly > 0)
               OR (salary_max_monthly IS NOT NULL AND salary_max_monthly > 0)
               OR is_negotiable = 1
        """)
        jobs_with_salary = cursor.fetchone()[0]
        
        # Total jobs
        cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
        total_jobs = cursor.fetchone()[0]
        
        # Average salary (only non-negotiable jobs)
        cursor.execute(f"""
            SELECT 
                AVG(salary_min_monthly) as avg_min,
                AVG(salary_max_monthly) as avg_max,
                MIN(salary_min_monthly) as min_salary,
                MAX(salary_max_monthly) as max_salary
            FROM {table_name}
            WHERE is_negotiable = 0
              AND salary_min_monthly > 0
              AND salary_max_monthly > 0
        """)
        row = cursor.fetchone()
        
        # Negotiable jobs count
        cursor.execute(f"""
            SELECT COUNT(*) FROM {table_name}
            WHERE is_negotiable = 1
        """)
        negotiable_count = cursor.fetchone()[0]
        
        conn.close()
        
        return jsonify({
            'total_jobs': total_jobs,
            'jobs_with_salary': jobs_with_salary,
            'jobs_without_salary': total_jobs - jobs_with_salary,
            'negotiable_jobs': negotiable_count,
            'coverage_percentage': round((jobs_with_salary / total_jobs * 100), 2) if total_jobs > 0 else 0,
            'avg_min_salary': round(row[0], 1) if row[0] else 0,
            'avg_max_salary': round(row[1], 1) if row[1] else 0,
            'min_salary': round(row[2], 1) if row[2] else 0,
            'max_salary': round(row[3], 1) if row[3] else 0,
        })
        
    except Exception as e:
        conn.close()
        return jsonify({'error': str(e)}), 500


@app.route('/api/salary/by-skill', methods=['GET'])
def get_salary_by_skill():
    """Get average salary by skill"""
    limit = request.args.get('limit', 15, type=int)
    
    conn = get_db()
    cursor = conn.cursor()
    
    # Check which tables to use
    jobs_table = 'jobs_realtime' if table_exists(conn, 'jobs_realtime') else 'jobs'
    skills_table = 'job_skills_realtime' if table_exists(conn, 'job_skills_realtime') else 'job_skills'
    
    skill_col = get_skill_column(conn, skills_table)
    
    try:
        cursor.execute(f"""
            SELECT 
                js.{skill_col} as skill,
                COUNT(DISTINCT j.job_id) as job_count,
                AVG((j.salary_min_monthly + j.salary_max_monthly) / 2) as avg_salary,
                MIN(j.salary_min_monthly) as min_salary,
                MAX(j.salary_max_monthly) as max_salary
            FROM {skills_table} js
            JOIN {jobs_table} j ON js.job_id = j.job_id
            WHERE j.is_negotiable = 0
              AND j.salary_min_monthly > 0
              AND j.salary_max_monthly > 0
              AND j.salary_currency = 'VND'
              AND js.{skill_col} IS NOT NULL
              AND TRIM(js.{skill_col}) != ''
            GROUP BY js.{skill_col}
            HAVING job_count >= 2
            ORDER BY avg_salary DESC
            LIMIT ?
        """, (limit,))
        
        results = []
        for row in cursor.fetchall():
            results.append({
                'skill': row[0],
                'job_count': row[1],
                'avg_salary': round(row[2], 1) if row[2] else 0,
                'min_salary': round(row[3], 1) if row[3] else 0,
                'max_salary': round(row[4], 1) if row[4] else 0,
            })
        
        conn.close()
        return jsonify(results)
        
    except Exception as e:
        conn.close()
        return jsonify({'error': str(e)}), 500


@app.route('/api/salary/by-level', methods=['GET'])
def get_salary_by_level():
    """Get average salary by job level"""
    conn = get_db()
    cursor = conn.cursor()
    
    table_name = 'jobs_realtime' if table_exists(conn, 'jobs_realtime') else 'jobs'
    
    try:
        cursor.execute(f"""
            SELECT 
                job_level,
                COUNT(*) as job_count,
                AVG((salary_min_monthly + salary_max_monthly) / 2) as avg_salary,
                MIN(salary_min_monthly) as min_salary,
                MAX(salary_max_monthly) as max_salary,
                AVG(salary_min_monthly) as avg_min,
                AVG(salary_max_monthly) as avg_max
            FROM {table_name}
            WHERE is_negotiable = 0
              AND salary_min_monthly > 0
              AND salary_max_monthly > 0
              AND salary_currency = 'VND'
              AND job_level IS NOT NULL
              AND TRIM(job_level) != ''
            GROUP BY job_level
            ORDER BY avg_salary DESC
        """)
        
        results = []
        for row in cursor.fetchall():
            results.append({
                'level': row[0],
                'job_count': row[1],
                'avg_salary': round(row[2], 1) if row[2] else 0,
                'min_salary': round(row[3], 1) if row[3] else 0,
                'max_salary': round(row[4], 1) if row[4] else 0,
                'avg_min_salary': round(row[5], 1) if row[5] else 0,
                'avg_max_salary': round(row[6], 1) if row[6] else 0,
            })
        
        conn.close()
        return jsonify(results)
        
    except Exception as e:
        conn.close()
        return jsonify({'error': str(e)}), 500


@app.route('/api/salary/by-location', methods=['GET'])
def get_salary_by_location():
    """Get average salary by location"""
    conn = get_db()
    cursor = conn.cursor()
    
    table_name = 'jobs_realtime' if table_exists(conn, 'jobs_realtime') else 'jobs'
    location_col = get_location_column(conn, table_name)
    
    try:
        cursor.execute(f"""
            SELECT 
                {location_col} as location,
                COUNT(*) as job_count,
                AVG((salary_min_monthly + salary_max_monthly) / 2) as avg_salary,
                MIN(salary_min_monthly) as min_salary,
                MAX(salary_max_monthly) as max_salary
            FROM {table_name}
            WHERE is_negotiable = 0
              AND salary_min_monthly > 0
              AND salary_max_monthly > 0
              AND salary_currency = 'VND'
              AND {location_col} IS NOT NULL
              AND TRIM({location_col}) != ''
            GROUP BY {location_col}
            HAVING job_count >= 3
            ORDER BY avg_salary DESC
        """)
        
        results = []
        for row in cursor.fetchall():
            results.append({
                'location': row[0],
                'job_count': row[1],
                'avg_salary': round(row[2], 1) if row[2] else 0,
                'min_salary': round(row[3], 1) if row[3] else 0,
                'max_salary': round(row[4], 1) if row[4] else 0,
            })
        
        conn.close()
        return jsonify(results)
        
    except Exception as e:
        conn.close()
        return jsonify({'error': str(e)}), 500


@app.route('/api/salary/distribution', methods=['GET'])
def get_salary_distribution():
    """Get salary distribution (histogram data)"""
    conn = get_db()
    cursor = conn.cursor()
    
    table_name = 'jobs_realtime' if table_exists(conn, 'jobs_realtime') else 'jobs'
    
    try:
        # Get all salaries
        cursor.execute(f"""
            SELECT (salary_min_monthly + salary_max_monthly) / 2 as avg_salary
            FROM {table_name}
            WHERE is_negotiable = 0
              AND salary_min_monthly > 0
              AND salary_max_monthly > 0
              AND salary_currency = 'VND'
        """)
        
        salaries = [row[0] for row in cursor.fetchall()]
        
        # Create salary ranges (bins)
        ranges = [
            {'range': '0-10 triệu', 'min': 0, 'max': 10, 'count': 0},
            {'range': '10-20 triệu', 'min': 10, 'max': 20, 'count': 0},
            {'range': '20-30 triệu', 'min': 20, 'max': 30, 'count': 0},
            {'range': '30-40 triệu', 'min': 30, 'max': 40, 'count': 0},
            {'range': '40-50 triệu', 'min': 40, 'max': 50, 'count': 0},
            {'range': '50-70 triệu', 'min': 50, 'max': 70, 'count': 0},
            {'range': '70-100 triệu', 'min': 70, 'max': 100, 'count': 0},
            {'range': '100+ triệu', 'min': 100, 'max': 9999, 'count': 0},
        ]
        
        # Count salaries in each range
        for salary in salaries:
            for r in ranges:
                if r['min'] <= salary < r['max']:
                    r['count'] += 1
                    break
        
        conn.close()
        return jsonify(ranges)
        
    except Exception as e:
        conn.close()
        return jsonify({'error': str(e)}), 500


@app.route('/api/salary/by-company', methods=['GET'])
def get_salary_by_company():
    """Get average salary by top companies"""
    limit = request.args.get('limit', 15, type=int)
    
    conn = get_db()
    cursor = conn.cursor()
    
    table_name = 'jobs_realtime' if table_exists(conn, 'jobs_realtime') else 'jobs'
    
    try:
        cursor.execute(f"""
            SELECT 
                company,
                COUNT(*) as job_count,
                AVG((salary_min_monthly + salary_max_monthly) / 2) as avg_salary,
                MIN(salary_min_monthly) as min_salary,
                MAX(salary_max_monthly) as max_salary
            FROM {table_name}
            WHERE is_negotiable = 0
              AND salary_min_monthly > 0
              AND salary_max_monthly > 0
              AND salary_currency = 'VND'
              AND company IS NOT NULL
              AND TRIM(company) != ''
            GROUP BY company
            HAVING job_count >= 2
            ORDER BY avg_salary DESC
            LIMIT ?
        """, (limit,))
        
        results = []
        for row in cursor.fetchall():
            results.append({
                'company': row[0],
                'job_count': row[1],
                'avg_salary': round(row[2], 1) if row[2] else 0,
                'min_salary': round(row[3], 1) if row[3] else 0,
                'max_salary': round(row[4], 1) if row[4] else 0,
            })
        
        conn.close()
        return jsonify(results)
        
    except Exception as e:
        conn.close()
        return jsonify({'error': str(e)}), 500


@app.route('/api/salary/skill-level-matrix', methods=['GET'])
def get_salary_skill_level_matrix():
    """Get salary matrix by skill and level"""
    skills = request.args.getlist('skills')
    
    if not skills:
        # Default top skills
        skills = ['Python', 'Java', 'JavaScript', 'React', 'Node.js']
    
    conn = get_db()
    cursor = conn.cursor()
    
    jobs_table = 'jobs_realtime' if table_exists(conn, 'jobs_realtime') else 'jobs'
    skills_table = 'job_skills_realtime' if table_exists(conn, 'job_skills_realtime') else 'job_skills'
    skill_col = get_skill_column(conn, skills_table)
    
    try:
        results = []
        
        for skill in skills:
            cursor.execute(f"""
                SELECT 
                    j.job_level,
                    AVG((j.salary_min_monthly + j.salary_max_monthly) / 2) as avg_salary,
                    COUNT(*) as job_count
                FROM {skills_table} js
                JOIN {jobs_table} j ON js.job_id = j.job_id
                WHERE js.{skill_col} LIKE ?
                  AND j.is_negotiable = 0
                  AND j.salary_min_monthly > 0
                  AND j.salary_max_monthly > 0
                  AND j.job_level IS NOT NULL
                  AND TRIM(j.job_level) != ''
                GROUP BY j.job_level
            """, (f'%{skill}%',))
            
            skill_data = {
                'skill': skill,
                'levels': []
            }
            
            for row in cursor.fetchall():
                skill_data['levels'].append({
                    'level': row[0],
                    'avg_salary': round(row[1], 1) if row[1] else 0,
                    'job_count': row[2]
                })
            
            results.append(skill_data)
        
        conn.close()
        return jsonify(results)
        
    except Exception as e:
        conn.close()
        return jsonify({'error': str(e)}), 500

# ============================================================================
# RUN SERVER
# ============================================================================

if __name__ == '__main__':
    socketio.run(
        app,
        debug=os.environ.get('FLASK_DEBUG', '1') == '1',
        host=os.environ.get('BIND_HOST', '0.0.0.0'),
        port=int(os.environ.get('PORT', '5001')),
        allow_unsafe_werkzeug=True,
    )
