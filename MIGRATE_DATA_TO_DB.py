#!/usr/bin/env python3
"""
MIGRATE CSV DATA TO DATABASE
Chuyển dữ liệu từ clean_it_jobs.csv vào SQLite database
"""

import pandas as pd
import sqlite3
import os

def migrate_csv_to_database():
    """Migrate CSV data to database"""
    
    print("=" * 70)
    print("🔄 MIGRATING CSV DATA TO DATABASE")
    print("=" * 70)
    print()
    
    # Read CSV
    csv_path = 'clean_it_jobs.csv'
    if not os.path.exists(csv_path):
        print(f"❌ File {csv_path} không tồn tại!")
        return
    
    print(f"📖 Reading {csv_path}...")
    df = pd.read_csv(csv_path)
    print(f"✅ Loaded {len(df)} jobs from CSV")
    print()
    
    # Connect to database
    db_path = 'it_jobs_vietnam.db'
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Create jobs_realtime table
    print("📊 Creating jobs_realtime table...")
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS jobs_realtime (
            job_id TEXT PRIMARY KEY,
            title TEXT,
            company TEXT,
            location TEXT,
            skills TEXT,
            job_level TEXT,
            crawled_date DATE,
            search_keyword TEXT
        )
    ''')
    
    # Create job_skills_realtime table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS job_skills_realtime (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            job_id TEXT,
            skill_name TEXT,
            FOREIGN KEY (job_id) REFERENCES jobs_realtime(job_id)
        )
    ''')
    print("✅ Tables created")
    print()
    
    # Insert jobs
    print("💾 Inserting jobs into database...")
    inserted = 0
    skipped = 0
    
    for idx, row in df.iterrows():
        try:
            # Generate job_id if not exists
            job_id = row.get('job_id', f'job_{idx}')
            
            cursor.execute('''
                INSERT OR REPLACE INTO jobs_realtime 
                (job_id, title, company, location, skills, job_level, crawled_date, search_keyword)
                VALUES (?, ?, ?, ?, ?, ?, date('now'), ?)
            ''', (
                str(job_id),
                str(row.get('title', '')),
                str(row.get('company', '')),
                str(row.get('location', '')),
                str(row.get('skills', '')),
                str(row.get('job_level', '')),
                'migrated_from_csv'
            ))
            
            # Delete old skills for this job
            cursor.execute('DELETE FROM job_skills_realtime WHERE job_id = ?', (str(job_id),))
            
            # Insert individual skills
            skills_str = str(row.get('skills', ''))
            if skills_str and skills_str != 'nan':
                skills_list = [s.strip() for s in skills_str.split(',') if s.strip()]
                for skill in skills_list:
                    cursor.execute('''
                        INSERT INTO job_skills_realtime (job_id, skill_name)
                        VALUES (?, ?)
                    ''', (str(job_id), skill))
            
            inserted += 1
            
            if (idx + 1) % 100 == 0:
                print(f"  Processed {idx + 1}/{len(df)} jobs...")
                
        except Exception as e:
            skipped += 1
            print(f"  ⚠️  Skipped job {idx}: {e}")
            continue
    
    conn.commit()
    conn.close()
    
    print()
    print("=" * 70)
    print("✅ MIGRATION COMPLETED!")
    print("=" * 70)
    print(f"📊 Inserted: {inserted} jobs")
    print(f"⚠️  Skipped: {skipped} jobs")
    print()
    print("🎉 Bây giờ tất cả trang (Dashboard, Analytics, Search, Trends)")
    print("   đều sẽ đọc dữ liệu từ SQLite database!")
    print()
    print("💡 Crawler sẽ tự động cập nhật database mỗi 6 giờ")
    print()

if __name__ == '__main__':
    migrate_csv_to_database()
