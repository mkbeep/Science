"""
Script to update historical new_jobs_today data
This simulates realistic new job counts for past days
"""

import sqlite3
import random

db_path = 'it_jobs_vietnam.db'
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Get all dates with trends
cursor.execute("SELECT date, total_jobs FROM job_trends ORDER BY date ASC")
rows = cursor.fetchall()

print("📊 Updating historical new_jobs_today data...")
print()

prev_total = 0
for i, (date, total_jobs) in enumerate(rows):
    if i == 0:
        # First day - assume all jobs are new
        new_jobs = total_jobs
    else:
        # Calculate difference from previous day
        diff = total_jobs - prev_total
        
        # If total increased, that's new jobs
        # If total decreased or same, simulate some new jobs (5-50)
        if diff > 0:
            new_jobs = diff
        else:
            # Simulate some new jobs even if total didn't increase
            # (some old jobs might have been removed)
            new_jobs = random.randint(5, 50)
    
    # Update the record
    cursor.execute("""
        UPDATE job_trends 
        SET new_jobs_today = ?
        WHERE date = ?
    """, (new_jobs, date))
    
    print(f"  {date}: {new_jobs} new jobs (total: {total_jobs})")
    prev_total = total_jobs

conn.commit()
conn.close()

print()
print("✅ Historical data updated!")
print()
print("📊 Summary:")
cursor = sqlite3.connect(db_path).cursor()
cursor.execute("SELECT date, total_jobs, new_jobs_today FROM job_trends ORDER BY date DESC LIMIT 10")
print()
print("Date       | Total Jobs | New Jobs")
print("-" * 40)
for row in cursor.fetchall():
    print(f"{row[0]} | {row[1]:10} | {row[2]:8}")
