# Bước 1: Cài đặt (chỉ lần đầu)
cd Science
pip install -r requirements.txt

# Bước 2: Chạy crawler tự động
./START_CRAWLER_BACKGROUND.sh

# Bước 3: Kiểm tra
./CHECK_CRAWLER_STATUS.sh


🧪 NẾU MUỐN TEST NGAY:
cd Science
./RUN_CRAWLER_NOW.sh
Script này sẽ chạy crawler ngay lập tức (không cần đợi 6 giờ) để bạn test xem nó có hoạt động không.

📊 XEM DỮ LIỆU HIỆN TẠI:
cd Science
sqlite3 it_jobs_vietnam.db "SELECT date, total_jobs, ai_ml_jobs, python_jobs, java_jobs, react_jobs FROM job_trends ORDER BY date DESC LIMIT 5"
