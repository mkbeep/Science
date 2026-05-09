"""
Real-Time Crawler - CRAWL THẬT TỪ VIETNAMWORKS
Crawls VietnamWorks API to get latest jobs
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import datetime
import sqlite3
import requests
import time

def crawl_vietnamworks():
    """Crawl jobs from VietnamWorks API"""
    
    url = "https://ms.vietnamworks.com/job-search/v1.0/search"
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Content-Type": "application/json"
    }
    
    # Crawl nhiều keywords để có nhiều jobs hơn
    keywords = [
        "information technology",
        "software engineer",
        "software developer",
        "frontend developer",
        "backend developer",
        "fullstack developer",
        "mobile developer",
        "data analyst",
        "data scientist",
        "data engineer",
        "AI engineer",
        "machine learning",
        "devops engineer",
        "QA engineer",
        "python developer",
        "java developer",
        "javascript developer",
        "react developer",
        "nodejs developer",
        "cloud engineer"
    ]
    
    all_jobs = []
    job_ids_seen = set()
    
    print("📡 Crawling VietnamWorks...")
    print(f"🔍 Keywords: {len(keywords)}")
    
    for keyword in keywords:
        print(f"  - Keyword: {keyword}")
        
        # Crawl 10 pages để có nhiều jobs hơn
        for page in range(0, 10):
            payload = {
                "userId": 0,
                "query": keyword,
                "filter": [],
                "ranges": [],
                "order": [],
                "hitsPerPage": 50,
                "page": page,
                "retrieveFields": [
                    "jobTitle", "jobId", "companyName",
                    "salaryMin", "salaryMax", "salary",
                    "workingLocations", "skills", "jobUrl", "jobLevel"
                ]
            }
            
            try:
                response = requests.post(url, json=payload, headers=headers, timeout=10)
                data = response.json()
                jobs = data.get("data", [])
                
                if not jobs:
                    break
                
                for job in jobs:
                    try:
                        if not job or not isinstance(job, dict):
                            continue
                        
                        job_id = job.get("jobId", "")
                        if job_id in job_ids_seen:
                            continue
                        
                        job_ids_seen.add(job_id)
                        
                        # Extract skills
                        skills = []
                        skills_data = job.get("skills")
                        if skills_data and isinstance(skills_data, list):
                            for skill in skills_data:
                                if skill and isinstance(skill, dict):
                                    skill_name = skill.get("skillName", "")
                                    if skill_name:
                                        skills.append(skill_name)
                        
                        # Extract location
                        location = ""
                        locations_data = job.get("workingLocations")
                        if locations_data and isinstance(locations_data, list) and len(locations_data) > 0:
                            if isinstance(locations_data[0], dict):
                                location = locations_data[0].get("cityNameVI", "")
                        
                        job_data = {
                            "job_id": job_id,
                            "title": job.get("jobTitle", ""),
                            "company": job.get("companyName", ""),
                            "job_level": job.get("jobLevel", ""),
                            "location": location,
                            "skills": ", ".join(skills),
                            "search_keyword": keyword
                        }
                        all_jobs.append(job_data)
                        
                    except Exception as e:
                        continue
                
                time.sleep(0.5)  # Delay giữa requests
                
            except Exception as e:
                print(f"    Error on page {page}: {e}")
                continue
    
    print(f"✅ Crawled {len(all_jobs)} unique jobs")
    return all_jobs

def count_jobs_by_criteria(jobs):
    """Count jobs by different criteria"""
    
    total_jobs = len(jobs)
    
    # AI/ML jobs
    ai_keywords = ['ai', 'machine learning', 'deep learning', 'data science', 'ml', 'artificial intelligence']
    ai_ml_jobs = 0
    for job in jobs:
        title_lower = job.get('title', '').lower()
        skills_lower = job.get('skills', '').lower()
        if any(keyword in title_lower or keyword in skills_lower for keyword in ai_keywords):
            ai_ml_jobs += 1
    
    # Data Analysis jobs
    data_keywords = ['data analysis', 'phân tích dữ liệu', 'data analyst']
    data_analysis_jobs = 0
    for job in jobs:
        title_lower = job.get('title', '').lower()
        skills_lower = job.get('skills', '').lower()
        if any(keyword in title_lower or keyword in skills_lower for keyword in data_keywords):
            data_analysis_jobs += 1
    
    # Python jobs
    python_jobs = sum(1 for job in jobs if 'python' in job.get('skills', '').lower())
    
    # Java jobs
    java_jobs = sum(1 for job in jobs if 'java' in job.get('skills', '').lower())
    
    # React jobs
    react_jobs = sum(1 for job in jobs if 'react' in job.get('skills', '').lower())
    
    return {
        'total_jobs': total_jobs,
        'ai_ml_jobs': ai_ml_jobs,
        'data_analysis_jobs': data_analysis_jobs,
        'python_jobs': python_jobs,
        'java_jobs': java_jobs,
        'react_jobs': react_jobs
    }

def save_jobs_to_database(jobs):
    """Save detailed jobs to database for Dashboard/Analytics"""
    
    db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'it_jobs_vietnam.db')
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Create jobs_realtime table if not exists
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
    
    # Create job_skills_realtime table if not exists
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS job_skills_realtime (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            job_id TEXT,
            skill_name TEXT,
            FOREIGN KEY (job_id) REFERENCES jobs_realtime(job_id)
        )
    ''')
    
    new_jobs = 0
    updated_jobs = 0
    
    # Insert/update jobs
    for job in jobs:
        # Check if job exists
        cursor.execute('SELECT job_id FROM jobs_realtime WHERE job_id = ?', (job['job_id'],))
        exists = cursor.fetchone()
        
        if exists:
            # Update existing job
            cursor.execute('''
                UPDATE jobs_realtime 
                SET title = ?, company = ?, location = ?, skills = ?, 
                    job_level = ?, crawled_date = date('now'), search_keyword = ?
                WHERE job_id = ?
            ''', (
                job['title'],
                job['company'],
                job['location'],
                job['skills'],
                job['job_level'],
                job['search_keyword'],
                job['job_id']
            ))
            updated_jobs += 1
        else:
            # Insert new job
            cursor.execute('''
                INSERT INTO jobs_realtime 
                (job_id, title, company, location, skills, job_level, crawled_date, search_keyword)
                VALUES (?, ?, ?, ?, ?, ?, date('now'), ?)
            ''', (
                job['job_id'],
                job['title'],
                job['company'],
                job['location'],
                job['skills'],
                job['job_level'],
                job['search_keyword']
            ))
            new_jobs += 1
        
        # Delete old skills for this job
        cursor.execute('DELETE FROM job_skills_realtime WHERE job_id = ?', (job['job_id'],))
        
        # Insert individual skills
        if job['skills']:
            skills_list = [s.strip() for s in job['skills'].split(',') if s.strip()]
            for skill in skills_list:
                cursor.execute('''
                    INSERT INTO job_skills_realtime (job_id, skill_name)
                    VALUES (?, ?)
                ''', (job['job_id'], skill))
    
    conn.commit()
    conn.close()
    
    print(f"✅ Saved to database: {new_jobs} new jobs, {updated_jobs} updated jobs")

def save_realtime_trend(date, counts):
    """Save real-time trend data to database"""
    
    db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'it_jobs_vietnam.db')
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Create table if not exists
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS job_trends (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date DATE NOT NULL UNIQUE,
            total_jobs INTEGER NOT NULL,
            ai_ml_jobs INTEGER NOT NULL,
            data_analysis_jobs INTEGER NOT NULL,
            python_jobs INTEGER NOT NULL,
            java_jobs INTEGER NOT NULL,
            react_jobs INTEGER NOT NULL,
            is_simulated BOOLEAN DEFAULT 0
        )
    ''')
    
    # Get TOTAL jobs in database (not just today's crawl)
    cursor.execute('SELECT COUNT(*) FROM jobs_realtime')
    total_jobs_in_db = cursor.fetchone()[0]
    
    # Count AI/ML jobs in entire database
    cursor.execute('''
        SELECT COUNT(DISTINCT jr.job_id)
        FROM jobs_realtime jr
        WHERE LOWER(jr.title) LIKE '%ai%' 
           OR LOWER(jr.title) LIKE '%machine learning%'
           OR LOWER(jr.title) LIKE '%deep learning%'
           OR LOWER(jr.title) LIKE '%data science%'
           OR LOWER(jr.skills) LIKE '%ai%'
           OR LOWER(jr.skills) LIKE '%machine learning%'
           OR LOWER(jr.skills) LIKE '%deep learning%'
           OR LOWER(jr.skills) LIKE '%data science%'
    ''')
    ai_ml_total = cursor.fetchone()[0]
    
    # Count Data Analysis jobs
    cursor.execute('''
        SELECT COUNT(DISTINCT jr.job_id)
        FROM jobs_realtime jr
        WHERE LOWER(jr.title) LIKE '%data analyst%'
           OR LOWER(jr.title) LIKE '%data analysis%'
           OR LOWER(jr.skills) LIKE '%data analysis%'
    ''')
    data_analysis_total = cursor.fetchone()[0]
    
    # Count Python jobs
    cursor.execute('''
        SELECT COUNT(DISTINCT jr.job_id)
        FROM jobs_realtime jr
        WHERE LOWER(jr.skills) LIKE '%python%'
    ''')
    python_total = cursor.fetchone()[0]
    
    # Count Java jobs
    cursor.execute('''
        SELECT COUNT(DISTINCT jr.job_id)
        FROM jobs_realtime jr
        WHERE LOWER(jr.skills) LIKE '%java%'
    ''')
    java_total = cursor.fetchone()[0]
    
    # Count React jobs
    cursor.execute('''
        SELECT COUNT(DISTINCT jr.job_id)
        FROM jobs_realtime jr
        WHERE LOWER(jr.skills) LIKE '%react%'
    ''')
    react_total = cursor.fetchone()[0]
    
    # Insert or replace today's data with TOTAL counts
    cursor.execute('''
        INSERT OR REPLACE INTO job_trends 
        (date, total_jobs, ai_ml_jobs, data_analysis_jobs, python_jobs, java_jobs, react_jobs, is_simulated)
        VALUES (?, ?, ?, ?, ?, ?, ?, 0)
    ''', (
        date,
        total_jobs_in_db,
        ai_ml_total,
        data_analysis_total,
        python_total,
        java_total,
        react_total
    ))
    
    conn.commit()
    conn.close()
    
    print(f"✅ Updated trend data for {date}")
    print(f"   Total in DB: {total_jobs_in_db} jobs (crawled today: {counts['total_jobs']} new/updated)")

def run_realtime_crawl():
    """Run real-time crawl from VietnamWorks"""
    
    print("=" * 70)
    print("🔄 REAL-TIME CRAWLER - VietnamWorks IT Jobs")
    print("=" * 70)
    print(f"⏰ Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    try:
        # Crawl jobs from VietnamWorks
        jobs = crawl_vietnamworks()
        
        if not jobs:
            print("❌ No jobs found!")
            return
        
        print()
        
        # Count by criteria
        print("📊 Analyzing jobs...")
        counts = count_jobs_by_criteria(jobs)
        
        print(f"  Total Jobs: {counts['total_jobs']}")
        print(f"  AI/ML Jobs: {counts['ai_ml_jobs']} ({(counts['ai_ml_jobs']/counts['total_jobs']*100):.1f}%)")
        print(f"  Data Analysis: {counts['data_analysis_jobs']}")
        print(f"  Python: {counts['python_jobs']}")
        print(f"  Java: {counts['java_jobs']}")
        print(f"  React: {counts['react_jobs']}")
        print()
        
        # Save detailed jobs to database (for Dashboard/Analytics)
        print(f"💾 Saving {len(jobs)} jobs to database...")
        save_jobs_to_database(jobs)
        print()
        
        # Save trend data (for Trends page)
        today = datetime.now().strftime('%Y-%m-%d')
        print(f"💾 Saving trend data for {today}...")
        save_realtime_trend(today, counts)
        print()
        
        print("=" * 70)
        print("✅ REAL-TIME CRAWL COMPLETED!")
        print("=" * 70)
        print()
        
    except Exception as e:
        print(f"❌ Error during crawl: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    run_realtime_crawl()
