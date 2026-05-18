"""
CẬP NHẬT LƯƠNG CHO DỮ LIỆU CŨ
Script này sẽ crawl lại các job cũ để lấy thông tin lương
"""

import sqlite3
import sys
import os
import time

sys.path.append(os.path.join(os.path.dirname(__file__), 'crawler'))

from crawler.http_client import post_json_with_retries
from crawler.salary_parser import normalize_salary

def update_old_jobs_with_salary():
    """
    Cập nhật thông tin lương cho các jobs cũ
    """
    
    print("="*70)
    print("🔄 CẬP NHẬT LƯƠNG CHO DỮ LIỆU CŨ")
    print("="*70)
    
    db_path = 'it_jobs_vietnam.db'
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Kiểm tra và thêm cột salary nếu chưa có
    print("\n[1] Kiểm tra cấu trúc database...")
    cursor.execute('PRAGMA table_info(jobs_realtime)')
    columns = [row[1] for row in cursor.fetchall()]
    
    columns_to_add = [
        ('salary_min_monthly', 'REAL'),
        ('salary_max_monthly', 'REAL'),
        ('salary_currency', 'TEXT DEFAULT "VND"'),
        ('salary_text', 'TEXT'),
        ('is_negotiable', 'BOOLEAN DEFAULT 0'),
    ]
    
    for col_name, col_type in columns_to_add:
        if col_name not in columns:
            print(f"   Thêm cột: {col_name}")
            cursor.execute(f'ALTER TABLE jobs_realtime ADD COLUMN {col_name} {col_type}')
    
    conn.commit()
    print("   ✓ Cấu trúc database OK")
    
    # Lấy danh sách jobs cần cập nhật (chưa có lương hoặc tất cả)
    print("\n[2] Lấy danh sách jobs cần cập nhật...")
    
    # Option 1: Chỉ cập nhật jobs chưa có lương
    cursor.execute("""
        SELECT job_id, title, company 
        FROM jobs_realtime 
        WHERE salary_min_monthly IS NULL 
          AND salary_max_monthly IS NULL
        LIMIT 100
    """)
    
    jobs_to_update = cursor.fetchall()
    total_jobs = len(jobs_to_update)
    
    print(f"   Tìm thấy {total_jobs} jobs cần cập nhật")
    
    if total_jobs == 0:
        print("\n✅ Tất cả jobs đã có thông tin lương!")
        conn.close()
        return
    
    # Hỏi user có muốn tiếp tục không
    print(f"\n⚠️  Sẽ crawl lại {total_jobs} jobs để lấy thông tin lương")
    print(f"   Ước tính thời gian: ~{total_jobs * 2} giây")
    
    response = input("\nTiếp tục? (y/n): ").strip().lower()
    if response != 'y':
        print("Đã hủy.")
        conn.close()
        return
    
    # Crawl lại từng job
    print("\n[3] Đang crawl thông tin lương...")
    
    url = "https://ms.vietnamworks.com/job-search/v1.0/search"
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Content-Type": "application/json"
    }
    
    updated_count = 0
    failed_count = 0
    
    for idx, (job_id, title, company) in enumerate(jobs_to_update, 1):
        print(f"\n   [{idx}/{total_jobs}] {title[:50]}...")
        
        try:
            # Search by job title and company
            payload = {
                "userId": 0,
                "query": f"{title} {company}",
                "filter": [],
                "ranges": [],
                "order": [],
                "hitsPerPage": 10,
                "page": 0,
                "retrieveFields": [
                    "jobTitle", "jobId", "companyName",
                    "salaryMin", "salaryMax", "salary"
                ]
            }
            
            response = post_json_with_retries(
                url,
                payload=payload,
                headers=headers,
                timeout=30.0
            )
            
            data = response.json()
            jobs = data.get("data", [])
            
            # Tìm job match với job_id
            found = False
            for job in jobs:
                if job.get("jobId") == job_id:
                    # Extract salary
                    api_salary_min = job.get("salaryMin")
                    api_salary_max = job.get("salaryMax")
                    salary_text = job.get("salary", "")
                    
                    salary_info = normalize_salary(
                        salary_min=None,
                        salary_max=None,
                        salary_text=salary_text,
                        api_min=api_salary_min,
                        api_max=api_salary_max
                    )
                    
                    # Update database
                    cursor.execute("""
                        UPDATE jobs_realtime
                        SET salary_min_monthly = ?,
                            salary_max_monthly = ?,
                            salary_currency = ?,
                            salary_text = ?,
                            is_negotiable = ?
                        WHERE job_id = ?
                    """, (
                        salary_info['salary_min_monthly'],
                        salary_info['salary_max_monthly'],
                        salary_info['salary_currency'],
                        salary_info['salary_text'],
                        1 if salary_info['is_negotiable'] else 0,
                        job_id
                    ))
                    
                    conn.commit()
                    updated_count += 1
                    found = True
                    
                    # Print salary info
                    if salary_info['is_negotiable']:
                        print(f"      Lương: Thỏa thuận")
                    elif salary_info['salary_min_monthly'] or salary_info['salary_max_monthly']:
                        min_sal = salary_info['salary_min_monthly'] or 0
                        max_sal = salary_info['salary_max_monthly'] or 0
                        print(f"      Lương: {min_sal:.1f} - {max_sal:.1f} triệu {salary_info['salary_currency']}")
                    else:
                        print(f"      Lương: Không có thông tin")
                    
                    break
            
            if not found:
                print(f"      ⚠️  Không tìm thấy job trên VietnamWorks")
                failed_count += 1
            
            # Delay để tránh bị block
            time.sleep(2)
            
        except Exception as e:
            print(f"      ❌ Lỗi: {e}")
            failed_count += 1
            continue
    
    conn.close()
    
    # Summary
    print("\n" + "="*70)
    print("📊 KẾT QUẢ CẬP NHẬT")
    print("="*70)
    print(f"Tổng số jobs:        {total_jobs}")
    print(f"✓ Cập nhật thành công: {updated_count}")
    print(f"✗ Thất bại:          {failed_count}")
    print(f"Tỷ lệ thành công:    {updated_count/total_jobs*100:.1f}%")
    print("="*70)
    
    print("\n💡 LƯU Ý:")
    print("   - Các jobs không tìm thấy có thể đã bị xóa khỏi VietnamWorks")
    print("   - Chạy lại script này để cập nhật thêm jobs khác")
    print("   - Crawler tự động sẽ cập nhật lương cho jobs mới")


def check_salary_coverage():
    """
    Kiểm tra bao nhiêu % jobs đã có thông tin lương
    """
    
    print("\n" + "="*70)
    print("📊 KIỂM TRA ĐỘ PHỦ THÔNG TIN LƯƠNG")
    print("="*70)
    
    db_path = 'it_jobs_vietnam.db'
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Total jobs
    cursor.execute("SELECT COUNT(*) FROM jobs_realtime")
    total_jobs = cursor.fetchone()[0]
    
    # Jobs with salary
    cursor.execute("""
        SELECT COUNT(*) FROM jobs_realtime 
        WHERE salary_min_monthly IS NOT NULL 
           OR salary_max_monthly IS NOT NULL
    """)
    jobs_with_salary = cursor.fetchone()[0]
    
    # Negotiable jobs
    cursor.execute("""
        SELECT COUNT(*) FROM jobs_realtime 
        WHERE is_negotiable = 1
    """)
    negotiable_jobs = cursor.fetchone()[0]
    
    # Jobs without salary info
    jobs_without_salary = total_jobs - jobs_with_salary - negotiable_jobs
    
    conn.close()
    
    print(f"\nTổng số jobs:              {total_jobs:,}")
    print(f"Jobs có thông tin lương:   {jobs_with_salary:,} ({jobs_with_salary/total_jobs*100:.1f}%)")
    print(f"Jobs thỏa thuận:           {negotiable_jobs:,} ({negotiable_jobs/total_jobs*100:.1f}%)")
    print(f"Jobs chưa có lương:        {jobs_without_salary:,} ({jobs_without_salary/total_jobs*100:.1f}%)")
    
    if jobs_without_salary > 0:
        print(f"\n💡 Chạy script này để cập nhật {jobs_without_salary:,} jobs còn lại")
    else:
        print(f"\n✅ Tất cả jobs đã có thông tin lương!")
    
    print("="*70)


if __name__ == '__main__':
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == 'check':
        # Chỉ kiểm tra, không cập nhật
        check_salary_coverage()
    else:
        # Kiểm tra trước
        check_salary_coverage()
        
        # Hỏi có muốn cập nhật không
        print("\n")
        update_old_jobs_with_salary()
