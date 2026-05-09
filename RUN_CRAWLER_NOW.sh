#!/bin/bash

# Script để chạy crawler NGAY LẬP TỨC (không cần đợi 6 giờ)

echo "🚀 Running crawler NOW..."
echo ""

cd "$(dirname "$0")/crawler"

python realtime_crawler.py

echo ""
echo "✅ Done! Check database:"
echo "  sqlite3 ../it_jobs_vietnam.db \"SELECT date, total_jobs, ai_ml_jobs FROM job_trends ORDER BY date DESC LIMIT 3\""
