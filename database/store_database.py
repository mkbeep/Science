"""
Store data to database - Main pipeline
Incremental insert: only adds new jobs, skips duplicates
"""

import sqlite3
from create_tables import create_tables
from insert_data import insert_data

def verify_database(db_file='it_jobs_vietnam.db'):
    """Verify database contents"""
    print("="*50)
    print("DATABASE VERIFICATION")
    print("="*50)
    
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    
    # Total counts
    cursor.execute("SELECT COUNT(*) FROM jobs")
    job_count = cursor.fetchone()[0]
    print(f"Total jobs in database:       {job_count}")
    
    cursor.execute("SELECT COUNT(*) FROM skills")
    skill_count = cursor.fetchone()[0]
    print(f"Total unique skills:          {skill_count}")
    
    cursor.execute("SELECT COUNT(*) FROM job_skills")
    job_skill_count = cursor.fetchone()[0]
    print(f"Total job-skill relationships: {job_skill_count}")
    
    # Top 10 skills
    print(f"\n{'='*50}")
    print("TOP 10 MOST DEMANDED SKILLS")
    print(f"{'='*50}")
    cursor.execute("""
        SELECT skill_name, COUNT(*) as count
        FROM job_skills
        GROUP BY skill_name
        ORDER BY count DESC
        LIMIT 10
    """)
    for i, (skill, count) in enumerate(cursor.fetchall(), 1):
        print(f"{i:2d}. {skill:30s} {count:4d} jobs")
    
    # Jobs by location
    print(f"\n{'='*50}")
    print("TOP 5 LOCATIONS")
    print(f"{'='*50}")
    cursor.execute("""
        SELECT location, COUNT(*) as count
        FROM jobs
        GROUP BY location
        ORDER BY count DESC
        LIMIT 5
    """)
    for loc, count in cursor.fetchall():
        print(f"   {loc:25s} {count:4d} jobs")
    
    conn.close()
    print(f"\n{'='*50}\n")

def main():
    """Main execution"""
    print("\n" + "="*50)
    print("PHASE 4: STORE DATA TO DATABASE")
    print("="*50 + "\n")
    
    db_file = 'it_jobs_vietnam.db'
    
    # Step 1: Create tables
    create_tables(db_file)
    print()
    
    # Step 2: Insert data (incremental)
    jobs_inserted, jobs_skipped = insert_data('clean_it_jobs.csv', db_file)
    
    # Step 3: Verify
    verify_database(db_file)
    
    # Summary
    print("="*50)
    print("✓ DATABASE STORAGE COMPLETE")
    print("="*50)
    print(f"Database file: {db_file}")
    print(f"New jobs added: {jobs_inserted}")
    print(f"Duplicates skipped: {jobs_skipped}")
    print("\nFeatures:")
    print("  ✓ PRIMARY KEY on job_id (prevents duplicates)")
    print("  ✓ INSERT OR IGNORE (incremental insert)")
    print("  ✓ No data overwrite (safe to run multiple times)")
    print("="*50 + "\n")

if __name__ == "__main__":
    main()
