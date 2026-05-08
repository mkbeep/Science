import sqlite3
import pandas as pd
from datetime import datetime

print("=== PHASE 4: STORE DATA TO DATABASE ===\n")

# Load cleaned data
print("Loading cleaned data...")
df = pd.read_csv("clean_it_jobs.csv")
print(f"Loaded {len(df)} jobs\n")

# Connect to SQLite database (will create if not exists)
db_file = "it_jobs_vietnam.db"
print(f"Connecting to database: {db_file}")
conn = sqlite3.connect(db_file)
cursor = conn.cursor()

# Create tables
print("\nCreating database tables...")

# 1. Jobs table
cursor.execute("""
CREATE TABLE IF NOT EXISTS jobs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    job_id TEXT UNIQUE NOT NULL,
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
    job_id TEXT NOT NULL,
    skill_name TEXT NOT NULL,
    FOREIGN KEY (job_id) REFERENCES jobs(job_id),
    FOREIGN KEY (skill_name) REFERENCES skills(skill_name),
    UNIQUE(job_id, skill_name)
)
""")

print("   Tables created successfully\n")

# Insert data
print("Inserting data into database...")

# Track statistics
jobs_inserted = 0
jobs_skipped = 0
skills_inserted = 0
job_skills_inserted = 0

all_skills = set()

for idx, row in df.iterrows():
    try:
        # Insert job
        cursor.execute("""
            INSERT OR IGNORE INTO jobs 
            (job_id, title, company, job_level, location, salary_min, salary_max, 
             salary_text, url, search_keyword, skill_count)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            row['job_id'],
            row['title'],
            row['company'],
            row.get('job_level', ''),
            row['location'],
            row.get('salary_min'),
            row.get('salary_max'),
            row.get('salary_text', ''),
            row.get('url', ''),
            row['search_keyword'],
            row['skill_count']
        ))
        
        if cursor.rowcount > 0:
            jobs_inserted += 1
        else:
            jobs_skipped += 1
        
        # Process skills
        if pd.notna(row['skills']) and row['skills']:
            skills_list = [s.strip() for s in str(row['skills']).split(',')]
            skills_list = [s for s in skills_list if s]
            
            for skill in skills_list:
                # Insert skill if not exists
                if skill not in all_skills:
                    cursor.execute("""
                        INSERT OR IGNORE INTO skills (skill_name)
                        VALUES (?)
                    """, (skill,))
                    if cursor.rowcount > 0:
                        skills_inserted += 1
                    all_skills.add(skill)
                
                # Insert job-skill relationship
                cursor.execute("""
                    INSERT OR IGNORE INTO job_skills (job_id, skill_name)
                    VALUES (?, ?)
                """, (row['job_id'], skill))
                
                if cursor.rowcount > 0:
                    job_skills_inserted += 1
        
        # Commit every 100 rows
        if (idx + 1) % 100 == 0:
            conn.commit()
            print(f"   Processed {idx + 1}/{len(df)} jobs...")
    
    except Exception as e:
        print(f"   Error inserting job {row.get('job_id', 'unknown')}: {e}")
        continue

# Final commit
conn.commit()

print(f"\n=== DATABASE STORAGE SUMMARY ===")
print(f"Jobs inserted: {jobs_inserted}")
print(f"Jobs skipped (duplicates): {jobs_skipped}")
print(f"Unique skills inserted: {skills_inserted}")
print(f"Job-skill relationships: {job_skills_inserted}")

# Verify data
print("\n=== DATABASE VERIFICATION ===")

cursor.execute("SELECT COUNT(*) FROM jobs")
job_count = cursor.fetchone()[0]
print(f"Total jobs in database: {job_count}")

cursor.execute("SELECT COUNT(*) FROM skills")
skill_count = cursor.fetchone()[0]
print(f"Total unique skills: {skill_count}")

cursor.execute("SELECT COUNT(*) FROM job_skills")
job_skill_count = cursor.fetchone()[0]
print(f"Total job-skill relationships: {job_skill_count}")

# Show top 10 skills
print("\n=== TOP 10 MOST DEMANDED SKILLS ===")
cursor.execute("""
    SELECT skill_name, COUNT(*) as count
    FROM job_skills
    GROUP BY skill_name
    ORDER BY count DESC
    LIMIT 10
""")
top_skills = cursor.fetchall()
for i, (skill, count) in enumerate(top_skills, 1):
    print(f"{i:2d}. {skill:30s} - {count:4d} jobs")

# Show jobs by location
print("\n=== JOBS BY LOCATION ===")
cursor.execute("""
    SELECT location, COUNT(*) as count
    FROM jobs
    GROUP BY location
    ORDER BY count DESC
    LIMIT 5
""")
locations = cursor.fetchall()
for loc, count in locations:
    print(f"   {loc:20s} - {count:4d} jobs")

# Close connection
conn.close()

print(f"\n✓ Database saved successfully: {db_file}")
print("\nPipeline complete: Crawl → Clean → Store ✓")
