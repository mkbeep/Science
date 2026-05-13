#!/bin/bash

# Script để check status của crawler

echo "📊 CRAWLER STATUS CHECK"
echo "======================="
echo ""

# Check if running
PID=$(pgrep -f "realtime_scheduler.py")

if [ -z "$PID" ]; then
    echo "❌ Crawler KHÔNG đang chạy"
    echo ""
    echo "Để start:"
    echo "  ./START_CRAWLER_BACKGROUND.sh"
else
    echo "✅ Crawler ĐANG CHẠY"
    echo ""
    echo "📊 Process ID: $PID"
    echo "⏰ Started: $(ps -p $PID -o lstart=)"
    echo "💾 Memory: $(ps -p $PID -o rss= | awk '{print $1/1024 " MB"}')"
    echo ""
    
    # Show last 10 lines of log
    if [ -f /tmp/realtime_crawler.log ]; then
        echo "📝 Last log entries:"
        echo "-------------------"
        tail -10 /tmp/realtime_crawler.log
    fi
fi

echo ""
echo "📊 Database Status:"
echo "-------------------"
sqlite3 it_jobs_vietnam.db "SELECT date, total_jobs, ai_ml_jobs FROM job_trends ORDER BY date DESC LIMIT 5" 2>/dev/null || echo "Cannot read database"

echo ""
echo "📖 Commands:"
echo "  - View log:  tail -f /tmp/realtime_crawler.log"
echo "  - Stop:      ./STOP_CRAWLER.sh"
echo "  - Restart:   ./STOP_CRAWLER.sh && ./START_CRAWLER_BACKGROUND.sh"
