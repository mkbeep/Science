"""
Insert data into database with duplicate checking
Uses INSERT OR IGNORE to prevent duplicates
"""

import sqlite3
import pandas as pd

def insert_data(csv_file='clean_it_jobs.csv', db_file='it_jobs_vietnam.db'):
    """Insert data with duplicate checking"""
    print("Loading cleaned data...")
    df = pd.read_csv(csv_file)
    print(f"Loaded {len(df)} jobs\n")
    
    print("Connecting to database...")
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    
    # Statistics
    jobs_inserted = 0
    jobs_skipped = 0
    skills_inserted = 0
    job_skills_inserted = 0
    all_skills = set()
    
    print("Inserting data (INSERT OR IGNORE)...\n")
    
    for idx, row in df.iterrows():
        try:
            # Insert job (INSERT OR IGNORE prevents duplicates)
            cursor.execute("""
                INSERT OR IGNORE INTO jobs 
                (job_id, title, company, job_level, location, salary_min, salary_max, 
                 salary_text, url, search_keyword, skill_count)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                int(row['job_id']),
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
                skills_list = [s.strip() for s in str(row['skills']).split(',') if s.strip()]
                
                for skill in skills_list:
                    # Insert skill if not exists
                    if skill not in all_skills:
                        cursor.execute("INSERT OR IGNORE INTO skills (skill_name) VALUES (?)", (skill,))
                        if cursor.rowcount > 0:
                            skills_inserted += 1
                        all_skills.add(skill)
                    
                    # Insert job-skill relationship
                    cursor.execute("""
                        INSERT OR IGNORE INTO job_skills (job_id, skill_name)
                        VALUES (?, ?)
                    """, (int(row['job_id']), skill))
                    
                    if cursor.rowcount > 0:
                        job_skills_inserted += 1
            
            # Commit every 100 rows
            if (idx + 1) % 100 == 0:
                conn.commit()
                print(f"   Processed {idx + 1}/{len(df)} jobs...")
        
        except Exception as e:
            print(f"   Error inserting job {row.get('job_id', 'unknown')}: {e}")
            continue
    
    conn.commit()
    conn.close()
    
    print(f"\n{'='*50}")
    print("DATABASE INSERT SUMMARY")
    print(f"{'='*50}")
    print(f"✓ Jobs inserted (new):        {jobs_inserted}")
    print(f"⊘ Jobs skipped (duplicates):  {jobs_skipped}")
    print(f"✓ Unique skills inserted:     {skills_inserted}")
    print(f"✓ Job-skill relationships:    {job_skills_inserted}")
    print(f"{'='*50}\n")
    
    return jobs_inserted, jobs_skipped

if __name__ == "__main__":
    insert_data()
