#!/bin/bash

# Script để chạy crawler ở background (không cần treo terminal)

# Save original directory
ORIGINAL_DIR="$(cd "$(dirname "$0")" && pwd)"

cd "$(dirname "$0")/crawler"

# Check if already running
if pgrep -f "realtime_scheduler.py" > /dev/null; then
    echo "⚠️  Crawler đã đang chạy!"
    echo ""
    echo "Process ID:"
    pgrep -f "realtime_scheduler.py"
    echo ""
    echo "Để xem log:"
    echo "  tail -f /tmp/realtime_crawler.log"
    echo ""
    echo "Để dừng:"
    echo "  ./STOP_CRAWLER.sh"
    exit 0
fi

echo "🚀 Starting Real-Time Crawler in background..."
echo ""

# Use absolute path to venv Python (from original directory, go up 1 level)
VENV_PYTHON="$ORIGINAL_DIR/../venv/bin/python3"

if [ -f "$VENV_PYTHON" ]; then
    echo "✅ Using venv Python: $VENV_PYTHON"
    PYTHON_CMD="$VENV_PYTHON"
else
    echo "⚠️  venv not found at $VENV_PYTHON, using system Python"
    PYTHON_CMD="python3"
fi

# Start in background with nohup
nohup "$PYTHON_CMD" realtime_scheduler.py > /tmp/realtime_crawler.log 2>&1 &
PID=$!

sleep 2

# Check if started successfully
if ps -p $PID > /dev/null; then
    echo "✅ Crawler started successfully!"
    echo ""
    echo "📊 Process ID: $PID"
    echo "📝 Log file: /tmp/realtime_crawler.log"
    echo ""
    echo "📖 Useful commands:"
    echo "  - Xem log:  tail -f /tmp/realtime_crawler.log"
    echo "  - Check:    ps aux | grep realtime_scheduler"
    echo "  - Dừng:     ./STOP_CRAWLER.sh"
    echo ""
    echo "🔄 Crawler sẽ chạy mỗi 6 giờ tự động"
    echo "💡 Bạn có thể tắt terminal, crawler vẫn chạy!"
else
    echo "❌ Failed to start crawler"
    echo "Check log: cat /tmp/realtime_crawler.log"
fi
