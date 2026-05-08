import requests
import pandas as pd
import time

url = "https://ms.vietnamworks.com/job-search/v1.0/search"

headers = {
    "User-Agent": "Mozilla/5.0",
    "Content-Type": "application/json"
}

# Các từ khóa liên quan đến CNTT
it_keywords = [
    "information technology",
    "software engineer",
    "software developer",
    "programmer",
    "web developer",
    "frontend developer",
    "backend developer",
    "fullstack developer",
    "mobile developer",
    "android developer",
    "ios developer",
    "react developer",
    "java developer",
    "python developer",
    ".net developer",
    "php developer",
    "nodejs developer",
    "data analyst",
    "data scientist",
    "data engineer",
    "machine learning",
    "AI engineer",
    "devops engineer",
    "cloud engineer",
    "system administrator",
    "network engineer",
    "security engineer",
    "database administrator",
    "IT support",
    "technical support",
    "QA engineer",
    "QA tester",
    "automation tester",
    "business analyst",
    "product manager",
    "project manager IT",
    "scrum master",
    "UI UX designer",
    "game developer"
]

all_jobs = []
job_ids_seen = set()  # Tránh trùng lặp

for keyword in it_keywords:
    print(f"\n=== Crawling keyword: {keyword} ===")
    
    # Crawl 20 pages cho mỗi keyword
    for page in range(0, 20):
        payload = {
            "userId": 0,
            "query": keyword,
            "filter": [],
            "ranges": [],
            "order": [],
            "hitsPerPage": 50,
            "page": page,
            "retrieveFields": [
                "jobTitle",
                "jobId",
                "companyName",
                "salaryMin",
                "salaryMax",
                "salary",
                "workingLocations",
                "jobDescription",
                "jobRequirement",
                "skills",
                "jobUrl",
                "jobLevel"
            ]
        }
        
        try:
            response = requests.post(url, json=payload, headers=headers)
            data = response.json()
            jobs = data.get("data", [])
            
            if not jobs:
                print(f"  Page {page}: No jobs found")
                break  # Hết jobs cho keyword này
                
            print(f"  Page {page}: {len(jobs)} jobs")
            
            for job in jobs:
                try:
                    if not job or not isinstance(job, dict):
                        continue
                    
                    job_id = job.get("jobId", "")
                    
                    # Skip nếu đã crawl job này rồi
                    if job_id in job_ids_seen:
                        continue
                    
                    job_ids_seen.add(job_id)
                    
                    # Extract skills safely
                    skills = []
                    skills_data = job.get("skills")
                    if skills_data and isinstance(skills_data, list):
                        for skill in skills_data:
                            if skill and isinstance(skill, dict):
                                skill_name = skill.get("skillName", "")
                                if skill_name:
                                    skills.append(skill_name)
                    
                    # Extract location safely
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
                        "salary_min": job.get("salaryMin", ""),
                        "salary_max": job.get("salaryMax", ""),
                        "salary_text": job.get("salary", ""),
                        "location": location,
                        "skills": ", ".join(skills),
                        "url": job.get("jobUrl", ""),
                        "search_keyword": keyword
                    }
                    all_jobs.append(job_data)
                    
                except Exception as e:
                    print(f"  Error processing job: {e}")
                    continue
            
        except Exception as e:
            print(f"  Error on page {page}: {e}")
            continue
        
        time.sleep(1)  # Delay giữa các request

print(f"\n=== SUMMARY ===")
print(f"Total unique jobs collected: {len(all_jobs)}")

if all_jobs:
    df = pd.DataFrame(all_jobs)
    
    print("\nJobs by keyword:")
    print(df['search_keyword'].value_counts())
    
    print("\nTop 10 skills:")
    all_skills = []
    for skills_str in df['skills']:
        if skills_str:
            all_skills.extend([s.strip() for s in skills_str.split(',')])
    skills_series = pd.Series(all_skills)
    print(skills_series.value_counts().head(10))
    
    print("\nFirst 5 jobs:")
    print(df.head())
    
    df.to_csv("it_jobs_vietnam.csv", index=False, encoding="utf-8-sig")
    print(f"\nSaved {len(all_jobs)} IT jobs to it_jobs_vietnam.csv successfully!")
else:
    print("No jobs collected!")
