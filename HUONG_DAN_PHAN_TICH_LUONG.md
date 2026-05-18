# 💰 HƯỚNG DẪN SỬ DỤNG TÍNH NĂNG PHÂN TÍCH LƯƠNG

## 📋 Tổng Quan

Tính năng **Phân Tích Lương** cho phép bạn:
- Xem tổng quan về mức lương IT Jobs tại Việt Nam
- Phân tích lương theo kỹ năng (skill)
- Phân tích lương theo cấp bậc (job level)
- Phân tích lương theo địa điểm
- Phân tích lương theo công ty
- Xem phân bố mức lương

## 🚀 Bước 1: Thu Thập Dữ Liệu Lương

Crawler đã được cấu hình để **tự động lấy thông tin lương** từ VietnamWorks API.

### Chạy Crawler Ngay

```bash
# Chạy crawler một lần
./RUN_CRAWLER_NOW.sh

# Hoặc chạy trực tiếp
python3 crawler/realtime_crawler.py
```

### Chạy Crawler Định Kỳ (Background)

```bash
# Chạy crawler mỗi 6 giờ tự động
./START_CRAWLER_BACKGROUND.sh

# Kiểm tra trạng thái
./CHECK_CRAWLER_STATUS.sh

# Dừng crawler
./STOP_CRAWLER.sh
```

## 📊 Bước 2: Xem Phân Tích Lương

### Khởi động Backend API

```bash
cd backend
python3 api.py
```

Backend sẽ chạy tại: `http://localhost:5001`

### Khởi động Frontend

```bash
cd frontend
npm start
```

Frontend sẽ chạy tại: `http://localhost:3000`

### Truy cập trang Phân Tích Lương

Mở trình duyệt và truy cập:
```
http://localhost:3000/salary
```

Hoặc click vào menu **"💰 Phân Tích Lương"** ở sidebar.

## 📈 Các Biểu Đồ Phân Tích

### 1. **Overview Cards**
- Tổng số jobs
- Jobs có thông tin lương
- Lương trung bình
- Jobs thỏa thuận

### 2. **Phân Bố Mức Lương**
Biểu đồ cột hiển thị số lượng jobs theo các khoảng lương:
- 0-10 triệu
- 10-20 triệu
- 20-30 triệu
- 30-40 triệu
- 40-50 triệu
- 50-70 triệu
- 70-100 triệu
- 100+ triệu

### 3. **Lương Theo Cấp Bậc**
So sánh lương trung bình theo các cấp bậc:
- Intern
- Fresher
- Junior
- Middle/Senior
- Lead/Manager
- Director

### 4. **Top 15 Kỹ Năng Có Lương Cao Nhất**
Xếp hạng các kỹ năng có mức lương trung bình cao nhất.

### 5. **Lương Theo Địa Điểm**
So sánh mức lương giữa các thành phố:
- Hà Nội
- Hồ Chí Minh
- Đà Nẵng
- Các tỉnh khác

### 6. **Top 15 Công Ty Trả Lương Cao Nhất**
Danh sách các công ty có mức lương trung bình cao nhất.

## 🔧 API Endpoints

Các endpoint API cho phân tích lương:

```bash
# Tổng quan
GET /api/salary/overview

# Lương theo kỹ năng
GET /api/salary/by-skill?limit=15

# Lương theo cấp bậc
GET /api/salary/by-level

# Lương theo địa điểm
GET /api/salary/by-location

# Phân bố lương
GET /api/salary/distribution

# Lương theo công ty
GET /api/salary/by-company?limit=15

# Ma trận lương theo skill và level
GET /api/salary/skill-level-matrix?skills=Python,Java,React
```

## 📝 Cấu Trúc Dữ Liệu Lương

Crawler lưu các thông tin sau vào database:

```sql
-- Bảng jobs_realtime
salary_min_monthly REAL          -- Lương tối thiểu (triệu VND/tháng)
salary_max_monthly REAL          -- Lương tối đa (triệu VND/tháng)
salary_currency TEXT             -- Đơn vị tiền tệ (VND, USD)
salary_text TEXT                 -- Text gốc từ API
is_negotiable BOOLEAN            -- Có thể thỏa thuận hay không
```

## 🎯 Lưu Ý

### Độ Phủ Dữ Liệu
- Không phải tất cả jobs đều có thông tin lương công khai
- Một số jobs chỉ hiển thị "Thỏa thuận"
- Crawler chỉ lấy được lương từ các jobs có `isSalaryVisible = true`

### Đơn Vị Lương
- Mặc định: **Triệu VND/tháng**
- Một số jobs có thể có đơn vị USD (sẽ được ghi rõ)

### Cập Nhật Dữ Liệu
- Chạy crawler định kỳ để có dữ liệu mới nhất
- Dữ liệu lương có thể thay đổi theo thời gian
- Nên chạy crawler ít nhất 1 lần/ngày

## 🐛 Xử Lý Lỗi

### Không có dữ liệu lương?

1. **Kiểm tra crawler đã chạy chưa:**
```bash
sqlite3 it_jobs_vietnam.db "SELECT COUNT(*) FROM jobs_realtime WHERE salary_min_monthly > 0;"
```

2. **Chạy lại crawler:**
```bash
./RUN_CRAWLER_NOW.sh
```

3. **Kiểm tra log crawler:**
```bash
tail -f crawler.log
```

### API trả về lỗi?

1. **Kiểm tra backend đang chạy:**
```bash
curl http://localhost:5001/api/health
```

2. **Restart backend:**
```bash
cd backend
python3 api.py
```

## 📞 Hỗ Trợ

Nếu gặp vấn đề, vui lòng:
1. Kiểm tra log crawler
2. Kiểm tra database có dữ liệu không
3. Kiểm tra backend API đang chạy
4. Kiểm tra frontend kết nối được backend không

## 🎉 Kết Quả Mong Đợi

Sau khi chạy crawler và truy cập trang Phân Tích Lương, bạn sẽ thấy:
- ✅ Các card thống kê tổng quan
- ✅ Biểu đồ phân bố lương
- ✅ Bảng xếp hạng kỹ năng theo lương
- ✅ So sánh lương theo cấp bậc
- ✅ So sánh lương theo địa điểm
- ✅ Top công ty trả lương cao

Chúc bạn phân tích thành công! 🚀
