"""
Test xem VietnamWorks API trả về thông tin lương không
"""

import requests
import json

url = "https://ms.vietnamworks.com/job-search/v1.0/search"
headers = {
    "User-Agent": "Mozilla/5.0",
    "Content-Type": "application/json"
}

payload = {
    "userId": 0,
    "query": "python developer",
    "filter": [],
    "ranges": [],
    "order": [],
    "hitsPerPage": 5,  # Chỉ lấy 5 jobs để test
    "page": 0,
    "retrieveFields": [
        "jobTitle", "jobId", "companyName",
        "salaryMin", "salaryMax", "salary", "prettySalary", "isSalaryVisible",
        "workingLocations", "skills", "jobUrl", "jobLevel"
    ]
}

print("="*70)
print("TEST VIETNAMWORKS API - SALARY INFORMATION")
print("="*70)

try:
    response = requests.post(url, json=payload, headers=headers, timeout=30)
    data = response.json()
    jobs = data.get("data", [])
    
    print(f"\n✓ Lấy được {len(jobs)} jobs")
    print("\nKiểm tra thông tin lương:")
    print("-"*70)
    
    for i, job in enumerate(jobs[:3], 1):
        print(f"\nJob {i}:")
        print(f"  Title: {job.get('jobTitle', 'N/A')}")
        print(f"  Company: {job.get('companyName', 'N/A')}")
        print(f"  salaryMin: {job.get('salaryMin', 'N/A')}")
        print(f"  salaryMax: {job.get('salaryMax', 'N/A')}")
        print(f"  salary (text): {job.get('salary', 'N/A')}")
        print(f"  prettySalary: {job.get('prettySalary', 'N/A')}")
        print(f"  isSalaryVisible: {job.get('isSalaryVisible', 'N/A')}")
        
        # In toàn bộ keys để xem có field nào khác không
        print(f"  All keys: {list(job.keys())}")
    
    # In raw JSON của 1 job để xem chi tiết
    if jobs:
        print("\n" + "="*70)
        print("RAW JSON của job đầu tiên:")
        print("="*70)
        print(json.dumps(jobs[0], indent=2, ensure_ascii=False))
    
except Exception as e:
    print(f"\n✗ Lỗi: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "="*70)
