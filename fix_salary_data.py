"""
FIX SALARY DATA - Cập nhật lại salary cho toàn bộ jobs trong DB
Chạy: python3 fix_salary_data.py
"""

import sqlite3
import sys
import os
import time
import requests

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'crawler'))
from salary_parser import normalize_salary

DB_PATH = os.path.join(os.path.dirname(__file__), 'it_jobs_vietnam.db')
API_URL = "https://ms.vietnamworks.com/job-search/v1.0/search"
HEADERS = {"User-Agent": "Mozilla/5.0", "Content-Type": "application/json"}

KEYWORDS = [
    "information technology", "software engineer", "software developer",
    "frontend developer", "backend developer", "fullstack developer",
    "mobile developer", "data analyst", "data scientist", "data engineer",
    "AI engineer", "machine learning", "devops engineer", "QA engineer",
    "python developer", "java developer", "javascript developer",
    "react developer", "nodejs developer", "cloud engineer"
]

def fetch_jobs_from_api():
    """Crawl jobs từ API, trả về dict {job_id -> salary_info}"""
    salary_map = {}
    
    for keyword in KEYWORDS:
        print(f"  Crawling keyword: {keyword}")
        for page in range(0, 10):
            payload = {
                "userId": 0, "query": keyword,
                "filter": [], "ranges": [], "order": [],
                "hitsPerPage": 50, "page": page,
                "retrieveFields": [
                    "jobId", "salaryMin", "salaryMax",
                    "salary", "prettySalary", "isSalaryVisible"
                ]
            }
            try:
                resp = requests.post(API_URL, json=payload, headers=HEADERS, timeout=20)
                data = resp.json()
                jobs = data.get("data", [])
                if not jobs:
                    break
                
                for job in jobs:
                    job_id = str(job.get("jobId", ""))
                    if not job_id or job_id in salary_map:
                        continue
                    
                    api_min = job.get("salaryMin") or 0
                    api_max = job.get("salaryMax") or 0
                    # Ưu tiên prettySalary (có format đẹp), fallback sang salary
                    salary_text = job.get("prettySalary") or job.get("salary") or ""
                    if salary_text == "0":
                        salary_text = ""
                    is_salary_visible = job.get("isSalaryVisible", False)
                    
                    # Chỉ normalize khi có dữ liệu
                    if is_salary_visible or salary_text or api_min > 0 or api_max > 0:
                        salary_info = normalize_salary(
                            salary_min=None, salary_max=None,
                            salary_text=str(salary_text),
                            api_min=api_min if api_min > 0 else None,
                            api_max=api_max if api_max > 0 else None,
                        )
                    else:
                        salary_info = {
                            'salary_min_monthly': None,
                            'salary_max_monthly': None,
                            'salary_currency': 'VND',
                            'salary_text': '',
                            'is_negotiable': False,
                        }
                    
                    salary_map[job_id] = salary_info
                
                time.sleep(0.5)
                
            except Exception as e:
                print(f"    Error page {page}: {e}")
                break
    
    return salary_map


def update_db(salary_map):
    """Cập nhật salary vào DB"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    updated = 0
    negotiable = 0
    no_data = 0
    
    for job_id, info in salary_map.items():
        cursor.execute("""
            UPDATE jobs_realtime
            SET salary_min_monthly = ?,
                salary_max_monthly = ?,
                salary_currency = ?,
                salary_text = ?,
                is_negotiable = ?
            WHERE job_id = ?
        """, (
            info['salary_min_monthly'],
            info['salary_max_monthly'],
            info['salary_currency'],
            info['salary_text'],
            1 if info['is_negotiable'] else 0,
            job_id,
        ))
        
        if cursor.rowcount > 0:
            if info['is_negotiable']:
                negotiable += 1
            elif info['salary_min_monthly'] or info['salary_max_monthly']:
                updated += 1
            else:
                no_data += 1
    
    conn.commit()
    
    # Stats
    cursor.execute("SELECT COUNT(*) FROM jobs_realtime")
    total = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM jobs_realtime WHERE salary_min_monthly IS NOT NULL OR salary_max_monthly IS NOT NULL")
    with_salary = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM jobs_realtime WHERE is_negotiable = 1")
    neg_total = cursor.fetchone()[0]
    
    conn.close()
    
    print(f"\n{'='*60}")
    print(f"✅ KẾT QUẢ CẬP NHẬT")
    print(f"{'='*60}")
    print(f"  API trả về:        {len(salary_map):,} jobs")
    print(f"  Có lương cụ thể:   {updated:,}")
    print(f"  Thỏa thuận:        {negotiable:,}")
    print(f"  Không có lương:    {no_data:,}")
    print(f"{'='*60}")
    print(f"  TRONG DATABASE ({total:,} jobs tổng):")
    print(f"  Có lương cụ thể:   {with_salary:,} ({with_salary/total*100:.1f}%)")
    print(f"  Thỏa thuận:        {neg_total:,} ({neg_total/total*100:.1f}%)")
    print(f"  Không có data:     {total - with_salary - neg_total:,} ({(total - with_salary - neg_total)/total*100:.1f}%)")
    print(f"{'='*60}")


if __name__ == '__main__':
    print("="*60)
    print("🔄 FIX SALARY DATA - Crawl lại từ VietnamWorks API")
    print("="*60)
    print(f"📂 DB: {DB_PATH}")
    print(f"🔍 Keywords: {len(KEYWORDS)}")
    print()
    
    print("📡 Đang crawl salary data từ API...")
    salary_map = fetch_jobs_from_api()
    print(f"\n✅ Crawled salary cho {len(salary_map):,} jobs từ API")
    
    print("\n💾 Đang cập nhật database...")
    update_db(salary_map)
    
    print("\n🎉 XONG! Khởi động lại backend để xem kết quả.")
