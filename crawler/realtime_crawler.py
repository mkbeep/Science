"""
Real-Time Crawler - CRAWL THẬT TỪ VIETNAMWORKS
Crawls VietnamWorks API to get latest jobs
"""

import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import hashlib
import re
import unicodedata
from datetime import datetime
import sqlite3

from alerting import notify_webhook
from http_client import MIN_REQUEST_INTERVAL_SEC, TransientHTTPError, post_json_with_retries, post_notify


def _normalize_dedupe_part(text: str) -> str:
    if not text:
        return ''
    text = unicodedata.normalize('NFC', str(text)).strip().lower()
    text = re.sub(r'\s+', ' ', text)
    return text


def content_fingerprint(title: str, company: str, job_url: str = '') -> str:
    """
    Fingerprint for duplicate detection across keyword searches and reposted job IDs.
    """
    blob = '|'.join((
        _normalize_dedupe_part(title),
        _normalize_dedupe_part(company),
        _normalize_dedupe_part(job_url),
    ))
    return hashlib.sha256(blob.encode('utf-8')).hexdigest()


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
    fingerprints_seen = set()
    
    print("📡 Crawling VietnamWorks...")
    print(f"🔍 Keywords: {len(keywords)}")
    print(f"⏳ Min request interval: {MIN_REQUEST_INTERVAL_SEC}s")
    
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
                response = post_json_with_retries(
                    url,
                    payload=payload,
                    headers=headers,
                    timeout=float(os.environ.get("CRAWL_HTTP_TIMEOUT", "30")),
                )
                try:
                    data = response.json()
                except ValueError:
                    print(f"    Invalid JSON on page {page}")
                    break
                jobs = data.get("data", [])
                
                if not jobs:
                    break
                
                for job in jobs:
                    try:
                        if not job or not isinstance(job, dict):
                            continue
                        
                        job_id = job.get("jobId", "")
                        raw_title = job.get("jobTitle", "") or ""
                        raw_company = job.get("companyName", "") or ""
                        raw_url = (job.get("jobUrl") or "").strip()

                        fp = content_fingerprint(raw_title, raw_company, raw_url)
                        if fp in fingerprints_seen:
                            continue
                        if job_id and job_id in job_ids_seen:
                            continue

                        fingerprints_seen.add(fp)
                        if job_id:
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
                            "title": raw_title or job.get("jobTitle", ""),
                            "company": raw_company or job.get("companyName", ""),
                            "job_level": job.get("jobLevel", ""),
                            "location": location,
                            "skills": ", ".join(skills),
                            "search_keyword": keyword,
                            "content_fingerprint": fp,
                            "job_url": raw_url,
                        }
                        all_jobs.append(job_data)
                        
                    except Exception:
                        continue
                
            except TransientHTTPError as e:
                print(f"    Transient HTTP error on page {page}: {e}")
                continue
            except Exception as e:
                print(f"    Error on page {page}: {e}")
                continue
    
    print(f"✅ Crawled {len(all_jobs)} unique jobs ({len(job_ids_seen)} distinct job IDs, {len(fingerprints_seen)} fingerprints)")
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

def _ensure_jobs_realtime_extra_columns(cursor):
    cursor.execute('PRAGMA table_info(jobs_realtime)')
    columns = [row[1] for row in cursor.fetchall()]
    if 'content_fingerprint' not in columns:
        cursor.execute('ALTER TABLE jobs_realtime ADD COLUMN content_fingerprint TEXT')
    if 'job_url' not in columns:
        cursor.execute('ALTER TABLE jobs_realtime ADD COLUMN job_url TEXT')


def save_jobs_to_database(jobs):
    """Save detailed jobs to database for Dashboard/Analytics"""

    db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'it_jobs_vietnam.db')
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute(
        '''
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
        '''
    )
    _ensure_jobs_realtime_extra_columns(cursor)

    cursor.execute(
        '''
        CREATE TABLE IF NOT EXISTS job_skills_realtime (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            job_id TEXT,
            skill_name TEXT,
            FOREIGN KEY (job_id) REFERENCES jobs_realtime(job_id)
        )
        '''
    )
    cursor.execute(
        '''
        CREATE INDEX IF NOT EXISTS idx_jobs_content_fp
        ON jobs_realtime(content_fingerprint)
        '''
    )

    new_jobs = 0
    updated_jobs = 0
    skipped_duplicates = 0

    for job in jobs:
        jid = job.get('job_id') or ''
        fp = job.get('content_fingerprint') or ''
        job_url = (job.get('job_url') or '').strip()

        if not jid:
            continue

        if fp:
            cursor.execute(
                '''
                SELECT job_id FROM jobs_realtime
                WHERE content_fingerprint = ?
                  AND job_id != ?
                ''',
                (fp, jid),
            )
            if cursor.fetchone():
                skipped_duplicates += 1
                continue

        cursor.execute('SELECT job_id FROM jobs_realtime WHERE job_id = ?', (jid,))
        exists = cursor.fetchone()

        if exists:
            cursor.execute(
                '''
                UPDATE jobs_realtime
                SET title = ?, company = ?, location = ?, skills = ?,
                    job_level = ?, crawled_date = date('now'), search_keyword = ?,
                    content_fingerprint = ?, job_url = ?
                WHERE job_id = ?
                ''',
                (
                    job['title'],
                    job['company'],
                    job['location'],
                    job['skills'],
                    job['job_level'],
                    job['search_keyword'],
                    fp or None,
                    job_url or None,
                    jid,
                ),
            )
            updated_jobs += 1
        else:
            cursor.execute(
                '''
                INSERT INTO jobs_realtime
                (job_id, title, company, location, skills, job_level, crawled_date,
                 search_keyword, content_fingerprint, job_url)
                VALUES (?, ?, ?, ?, ?, ?, date('now'), ?, ?, ?)
                ''',
                (
                    jid,
                    job['title'],
                    job['company'],
                    job['location'],
                    job['skills'],
                    job['job_level'],
                    job['search_keyword'],
                    fp or None,
                    job_url or None,
                ),
            )
            new_jobs += 1

        cursor.execute('DELETE FROM job_skills_realtime WHERE job_id = ?', (jid,))

        if job['skills']:
            skills_list = [s.strip() for s in job['skills'].split(',') if s.strip()]
            for skill in skills_list:
                cursor.execute(
                    '''
                    INSERT INTO job_skills_realtime (job_id, skill_name)
                    VALUES (?, ?)
                    ''',
                    (jid, skill),
                )

    conn.commit()
    conn.close()

    print(
        f"✅ Saved to database: {new_jobs} new jobs, "
        f"{updated_jobs} updated, {skipped_duplicates} duplicates skipped"
    )

    return {
        'new_jobs': new_jobs,
        'updated_jobs': updated_jobs,
        'skipped_duplicates': skipped_duplicates,
    }

def save_realtime_trend(date, counts, save_stats):
    """Save real-time trend data to database"""
    
    db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'it_jobs_vietnam.db')
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Create table if not exists - ADD new_jobs_today column
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS job_trends (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date DATE NOT NULL UNIQUE,
            total_jobs INTEGER NOT NULL,
            new_jobs_today INTEGER DEFAULT 0,
            ai_ml_jobs INTEGER NOT NULL,
            data_analysis_jobs INTEGER NOT NULL,
            python_jobs INTEGER NOT NULL,
            java_jobs INTEGER NOT NULL,
            react_jobs INTEGER NOT NULL,
            is_simulated BOOLEAN DEFAULT 0
        )
    ''')
    
    # Check if column exists, if not add it
    cursor.execute("PRAGMA table_info(job_trends)")
    columns = [col[1] for col in cursor.fetchall()]
    if 'new_jobs_today' not in columns:
        cursor.execute('ALTER TABLE job_trends ADD COLUMN new_jobs_today INTEGER DEFAULT 0')
    
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
    
    # Get new jobs count from save_stats
    new_jobs_today = save_stats.get('new_jobs', 0)
    
    # Insert or replace today's data with TOTAL counts AND new jobs count
    cursor.execute('''
        INSERT OR REPLACE INTO job_trends 
        (date, total_jobs, new_jobs_today, ai_ml_jobs, data_analysis_jobs, python_jobs, java_jobs, react_jobs, is_simulated)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, 0)
    ''', (
        date,
        total_jobs_in_db,
        new_jobs_today,
        ai_ml_total,
        data_analysis_total,
        python_total,
        java_total,
        react_total
    ))
    
    conn.commit()
    conn.close()
    
    print(f"✅ Updated trend data for {date}")
    print(f"   Total in DB: {total_jobs_in_db} jobs")
    print(f"   New jobs today: {new_jobs_today} jobs")
    print(f"   Updated jobs: {save_stats.get('updated_jobs', 0)} jobs")


def _database_path():
    return os.path.join(os.path.dirname(os.path.dirname(__file__)), 'it_jobs_vietnam.db')


def _ensure_crawl_runs_table(cursor):
    cursor.execute(
        '''
        CREATE TABLE IF NOT EXISTS crawl_runs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            started_at TEXT NOT NULL,
            finished_at TEXT,
            status TEXT NOT NULL,
            jobs_crawled INTEGER DEFAULT 0,
            new_jobs INTEGER DEFAULT 0,
            updated_jobs INTEGER DEFAULT 0,
            skipped_duplicates INTEGER DEFAULT 0,
            error_message TEXT
        )
        '''
    )


def _start_crawl_run_record():
    conn = sqlite3.connect(_database_path())
    cursor = conn.cursor()
    _ensure_crawl_runs_table(cursor)
    started = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    cursor.execute(
        '''
        INSERT INTO crawl_runs
        (started_at, finished_at, status, jobs_crawled)
        VALUES (?, NULL, ?, 0)
        ''',
        (started, 'running'),
    )
    run_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return run_id


def _finish_crawl_run_record(
    run_id,
    *,
    status,
    jobs_crawled=0,
    new_jobs=0,
    updated_jobs=0,
    skipped_duplicates=0,
    error_message=None,
):
    finished = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    conn = sqlite3.connect(_database_path())
    cursor = conn.cursor()
    cursor.execute(
        '''
        UPDATE crawl_runs
        SET finished_at = ?, status = ?, jobs_crawled = ?, new_jobs = ?,
            updated_jobs = ?, skipped_duplicates = ?, error_message = ?
        WHERE id = ?
        ''',
        (
            finished,
            status,
            jobs_crawled,
            new_jobs,
            updated_jobs,
            skipped_duplicates,
            error_message,
            run_id,
        ),
    )
    conn.commit()
    conn.close()


def _notify_api_crawl(payload: dict) -> None:
    url = os.environ.get(
        'CRAWL_NOTIFY_URL',
        'http://127.0.0.1:5001/api/internal/crawl-complete',
    ).strip()
    secret = os.environ.get('CRAWL_NOTIFY_SECRET', '').strip()
    headers = {'Content-Type': 'application/json'}
    if secret:
        headers['X-Crawl-Secret'] = secret
    if not post_notify(url, json_body=payload, headers=headers, timeout=12):
        print('⚠️  Could not reach API WebSocket notifier (backend may be down)')


def run_realtime_crawl():
    """Run real-time crawl from VietnamWorks"""

    print('=' * 70)
    print('🔄 REAL-TIME CRAWLER - VietnamWorks IT Jobs')
    print('=' * 70)
    print(f"⏰ Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    crawl_run_id = _start_crawl_run_record()

    try:
        jobs = crawl_vietnamworks()

        if not jobs:
            print('❌ No jobs found!')
            _finish_crawl_run_record(
                crawl_run_id,
                status='warning',
                error_message='no jobs returned',
            )
            notify_webhook(
                'Crawler finished with zero jobs returned',
                severity='warning',
            )
            _notify_api_crawl(
                {'event': 'crawl_warning', 'message': 'zero jobs', 'run_id': crawl_run_id},
            )
            return

        print()
        print('📊 Analyzing jobs...')
        counts = count_jobs_by_criteria(jobs)

        print(f"  Total Jobs: {counts['total_jobs']}")
        print(
            f"  AI/ML Jobs: {counts['ai_ml_jobs']} "
            f"({(counts['ai_ml_jobs'] / counts['total_jobs'] * 100):.1f}%)"
        )
        print(f"  Data Analysis: {counts['data_analysis_jobs']}")
        print(f"  Python: {counts['python_jobs']}")
        print(f"  Java: {counts['java_jobs']}")
        print(f"  React: {counts['react_jobs']}")
        print()

        print(f'💾 Saving {len(jobs)} jobs to database...')
        save_stats = save_jobs_to_database(jobs)
        print()

        today = datetime.now().strftime('%Y-%m-%d')
        print(f'💾 Saving trend data for {today}...')
        save_realtime_trend(today, counts, save_stats)
        print()

        _finish_crawl_run_record(
            crawl_run_id,
            status='success',
            jobs_crawled=len(jobs),
            new_jobs=save_stats.get('new_jobs', 0),
            updated_jobs=save_stats.get('updated_jobs', 0),
            skipped_duplicates=save_stats.get('skipped_duplicates', 0),
        )

        iso_ts = datetime.now().isoformat()
        notify_webhook(
            f"Crawl OK: +{save_stats.get('new_jobs', 0)} new / "
            f"{save_stats.get('updated_jobs', 0)} updated jobs",
            severity='info',
            extra={'run_id': crawl_run_id, 'jobs': len(jobs)},
        )
        _notify_api_crawl(
            {
                'event': 'crawl_complete',
                'run_id': crawl_run_id,
                'jobs_crawled': len(jobs),
                'new_jobs': save_stats.get('new_jobs', 0),
                'updated_jobs': save_stats.get('updated_jobs', 0),
                'skipped_duplicates': save_stats.get('skipped_duplicates', 0),
                'summary': counts,
                'finished_at': iso_ts,
            },
        )

        print('=' * 70)
        print('✅ REAL-TIME CRAWL COMPLETED!')
        print('=' * 70)
        print()

    except Exception as e:
        print(f'❌ Error during crawl: {e}')
        import traceback

        tb = traceback.format_exc()
        traceback.print_exc()
        _finish_crawl_run_record(
            crawl_run_id,
            status='failed',
            error_message=str(e)[:2000],
        )
        notify_webhook(
            f'Crawler failed: {e}',
            severity='error',
            extra={'traceback': tb[:4000]},
        )
        raise

if __name__ == '__main__':
    run_realtime_crawl()
