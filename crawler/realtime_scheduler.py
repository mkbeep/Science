"""
Real-Time Scheduler - Crawl VietnamWorks nhiều lần trong ngày
Chạy mỗi 6 giờ để cập nhật dữ liệu real-time
"""

import schedule
import time
from datetime import datetime
from realtime_crawler import run_realtime_crawl

def job():
    """Wrapper function for scheduled job"""
    print("\n" + "="*70)
    print(f"⏰ Scheduled crawl triggered at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*70 + "\n")
    run_realtime_crawl()
    print(f"\n⏰ Next crawl in 6 hours...")
    print()

# Schedule: Chạy mỗi 6 giờ
schedule.every(6).hours.do(job)

# Hoặc chạy vào các giờ cố định trong ngày:
# schedule.every().day.at("06:00").do(job)  # 6 AM
# schedule.every().day.at("12:00").do(job)  # 12 PM
# schedule.every().day.at("18:00").do(job)  # 6 PM
# schedule.every().day.at("23:00").do(job)  # 11 PM

print("🤖 REAL-TIME CRAWLER SCHEDULER")
print("="*70)
print("🔄 Schedule: Every 6 hours (4 times per day)")
print("📊 Purpose: Track real-time job market changes")
print("⏹️  Press Ctrl+C to stop")
print("="*70)
print()

# Show next run time
next_run = schedule.next_run()
if next_run:
    print(f"⏰ Next run: {next_run.strftime('%Y-%m-%d %H:%M:%S')}")
    print()

# Run immediately on start
print("🚀 Running initial crawl...")
job()

# Main loop
try:
    while True:
        schedule.run_pending()
        time.sleep(60)  # Check every minute
except KeyboardInterrupt:
    print("\n\n⏹️  Scheduler stopped by user")
    print("👋 Goodbye!")
