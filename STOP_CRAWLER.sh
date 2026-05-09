#!/bin/bash

# Script để dừng crawler

echo "🛑 Stopping Real-Time Crawler..."
echo ""

# Find process
PID=$(pgrep -f "realtime_scheduler.py")

if [ -z "$PID" ]; then
    echo "⚠️  Crawler không đang chạy"
    exit 0
fi

echo "📊 Found process: $PID"

# Kill process
kill $PID

sleep 1

# Check if stopped
if ps -p $PID > /dev/null 2>&1; then
    echo "⚠️  Process vẫn chạy, forcing stop..."
    kill -9 $PID
    sleep 1
fi

if ps -p $PID > /dev/null 2>&1; then
    echo "❌ Failed to stop process"
else
    echo "✅ Crawler stopped successfully!"
fi

echo ""
echo "📝 Log file vẫn còn tại: /tmp/realtime_crawler.log"
