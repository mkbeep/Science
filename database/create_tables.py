"""
Create database tables with proper schema
"""

import sqlite3

def create_tables(db_file='it_jobs_vietnam.db'):
    """Create database tables if not exist"""
    print("Creating database tables...")
    
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    
    # 1. Jobs table - job_id as PRIMARY KEY
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS jobs (
        job_id INTEGER PRIMARY KEY,
        title TEXT NOT NULL,
        company TEXT NOT NULL,
        job_level TEXT,
        location TEXT,
        salary_min REAL,
        salary_max REAL,
        salary_text TEXT,
        url TEXT,
        search_keyword TEXT,
        skill_count INTEGER,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)
    
    # 2. Skills table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS skills (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        skill_name TEXT UNIQUE NOT NULL
    )
    """)
    
    # 3. Job-Skills relationship table (many-to-many)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS job_skills (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        job_id INTEGER NOT NULL,
        skill_name TEXT NOT NULL,
        FOREIGN KEY (job_id) REFERENCES jobs(job_id),
        FOREIGN KEY (skill_name) REFERENCES skills(skill_name),
        UNIQUE(job_id, skill_name)
    )
    """)
    
    conn.commit()
    conn.close()
    
    print("✓ Tables created successfully")
    print("  - jobs (job_id as PRIMARY KEY)")
    print("  - skills")
    print("  - job_skills (relationship)")

if __name__ == "__main__":
    create_tables()
