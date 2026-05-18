# 💰 HƯỚNG DẪN TEST TÍNH NĂNG LƯƠNG

## 🎯 Tóm Tắt

Crawler đã được cập nhật để:
- ✅ Lấy thông tin lương từ VietnamWorks API
- ✅ Tự động chuyển đổi lương năm thành lương tháng (chia 12)
- ✅ Xử lý nhiều định dạng lương khác nhau
- ✅ Lưu vào database với đầy đủ thông tin

---

## 🧪 CÁCH 1: TEST NHANH SALARY PARSER

### Bước 1: Chạy test
```bash
cd Science/crawler
python salary_parser.py
```

### Kết quả mong đợi:
```
======================================================================
SALARY PARSER TESTS
======================================================================

[TEST 1] Parse salary text:
----------------------------------------------------------------------

Input:  15 - 25 triệu VND
Output: min=15.0, max=25.0, currency=VND, unit=month

Input:  180 - 300 triệu VND/năm
Output: min=180.0, max=300.0, currency=VND, unit=year

Input:  Thỏa thuận
Output: min=None, max=None, currency=VND, unit=month

[TEST 2] Normalize salary:
----------------------------------------------------------------------

Case 1: Lương năm
Input:  180 - 300 triệu VND/năm
Output: 15.0 - 25.0 triệu VND/tháng  ← Đã chia 12!

Case 2: API values
Input:  api_min=15, api_max=25
Output: 15.0 - 25.0 triệu VND/tháng

Case 3: Thỏa thuận
Input:  Thỏa thuận
Output: is_negotiable=True

✅ ALL TESTS COMPLETED
```

---

## 🚀 CÁCH 2: CHẠY CRAWLER ĐỂ LẤY DỮ LIỆU THẬT

### Bước 1: Chạy crawler
```bash
cd Science/crawler
python realtime_crawler.py
```

### Bước 2: Kiểm tra database
```bash
cd Science
sqlite3 it_jobs_vietnam.db
```

Trong SQLite:
```sql
-- Xem các cột mới
PRAGMA table_info(jobs_realtime);

-- Xem jobs có lương
SELECT 
    title, 
    company, 
    salary_min_monthly, 
    salary_max_monthly, 
    salary_currency,
    is_negotiable
FROM jobs_realtime 
WHERE salary_min_monthly IS NOT NULL 
   OR salary_max_monthly IS NOT NULL
LIMIT 10;

-- Thống kê lương
SELECT 
    COUNT(*) as total_jobs,
    COUNT(salary_min_monthly) as jobs_with_min_salary,
    COUNT(salary_max_monthly) as jobs_with_max_salary,
    SUM(is_negotiable) as negotiable_jobs,
    AVG(salary_min_monthly) as avg_min_salary,
    AVG(salary_max_monthly) as avg_max_salary
FROM jobs_realtime;

-- Thoát
.quit
```

---

## 📊 CÁCH 3: XEM TRÊN DASHBOARD

### Bước 1: Khởi động backend
```bash
cd Science/backend
python api.py
```

### Bước 2: Khởi động frontend
```bash
cd Science/frontend
npm start
```

### Bước 3: Mở trình duyệt
```
http://localhost:3000
```

Dashboard sẽ hiển thị thông tin lương trong danh sách jobs!

---

## 🔍 CÁC TRƯỜNG HỢP XỬ LÝ

### 1. Lương theo tháng (VND)
```
Input:  "15 - 25 triệu VND"
Output: min=15, max=25, unit=month
→ Lưu trực tiếp: 15-25 triệu/tháng
```

### 2. Lương theo năm (VND) ⭐
```
Input:  "180 - 300 triệu VND/năm"
Output: min=180, max=300, unit=year
→ Tự động chia 12: 15-25 triệu/tháng
```

### 3. Lương USD
```
Input:  "1000 - 1500 USD/month"
Output: min=1000, max=1500, currency=USD
→ Lưu: 1000-1500 USD/tháng
```

### 4. Thỏa thuận
```
Input:  "Thỏa thuận" hoặc "Negotiable"
Output: is_negotiable=True
→ Lưu: min=NULL, max=NULL, is_negotiable=1
```

### 5. Chỉ có max
```
Input:  "Up to 2000 USD"
Output: min=None, max=2000
→ Lưu: max=2000 USD/tháng
```

### 6. Chỉ có min
```
Input:  "From 20 triệu"
Output: min=20, max=None
→ Lưu: min=20 triệu/tháng
```

---

## 📝 CẤU TRÚC DATABASE

### Bảng jobs_realtime - Các cột mới:

| Column | Type | Description |
|--------|------|-------------|
| `salary_min_monthly` | REAL | Lương tối thiểu (triệu VND/tháng) |
| `salary_max_monthly` | REAL | Lương tối đa (triệu VND/tháng) |
| `salary_currency` | TEXT | Đơn vị tiền tệ (VND/USD) |
| `salary_text` | TEXT | Text gốc từ API |
| `is_negotiable` | BOOLEAN | Có phải "Thỏa thuận" không |

### Ví dụ dữ liệu:

```
job_id: 12345
title: Senior Python Developer
company: FPT Software
salary_min_monthly: 20.0
salary_max_monthly: 35.0
salary_currency: VND
salary_text: 20 - 35 triệu VND
is_negotiable: 0
```

```
job_id: 67890
title: Java Developer
company: VNG Corporation
salary_min_monthly: 15.0
salary_max_monthly: 25.0
salary_currency: VND
salary_text: 180 - 300 triệu VND/năm  ← Gốc là năm
is_negotiable: 0
```

---

## 🎨 QUERY MẪU

### 1. Top 10 jobs có lương cao nhất
```sql
SELECT 
    title, 
    company, 
    salary_max_monthly,
    salary_currency
FROM jobs_realtime 
WHERE salary_max_monthly IS NOT NULL
ORDER BY salary_max_monthly DESC
LIMIT 10;
```

### 2. Lương trung bình theo location
```sql
SELECT 
    canonical_location,
    COUNT(*) as job_count,
    AVG(salary_min_monthly) as avg_min,
    AVG(salary_max_monthly) as avg_max
FROM jobs_realtime 
WHERE salary_min_monthly IS NOT NULL
GROUP BY canonical_location
ORDER BY avg_max DESC;
```

### 3. Lương trung bình theo skill
```sql
SELECT 
    js.canonical_skill,
    COUNT(DISTINCT jr.job_id) as job_count,
    AVG(jr.salary_max_monthly) as avg_max_salary
FROM jobs_realtime jr
JOIN job_skills_realtime js ON jr.job_id = js.job_id
WHERE jr.salary_max_monthly IS NOT NULL
GROUP BY js.canonical_skill
HAVING job_count >= 5
ORDER BY avg_max_salary DESC
LIMIT 20;
```

### 4. Phân bố lương
```sql
SELECT 
    CASE 
        WHEN salary_max_monthly < 10 THEN '< 10 triệu'
        WHEN salary_max_monthly < 20 THEN '10-20 triệu'
        WHEN salary_max_monthly < 30 THEN '20-30 triệu'
        WHEN salary_max_monthly < 50 THEN '30-50 triệu'
        ELSE '> 50 triệu'
    END as salary_range,
    COUNT(*) as job_count
FROM jobs_realtime
WHERE salary_max_monthly IS NOT NULL
GROUP BY salary_range
ORDER BY 
    CASE salary_range
        WHEN '< 10 triệu' THEN 1
        WHEN '10-20 triệu' THEN 2
        WHEN '20-30 triệu' THEN 3
        WHEN '30-50 triệu' THEN 4
        ELSE 5
    END;
```

---

## ⚠️ LƯU Ý

### 1. Lương năm tự động chia 12
- VietnamWorks đôi khi hiển thị lương theo năm
- Hệ thống tự động phát hiện và chia cho 12
- Kết quả luôn là lương tháng

### 2. Đơn vị tiền tệ
- VND: Triệu đồng/tháng (15 = 15 triệu VND)
- USD: Đô la/tháng (1500 = 1500 USD)

### 3. Thỏa thuận
- Nếu là "Thỏa thuận" hoặc "Negotiable"
- `is_negotiable = 1`
- `salary_min_monthly = NULL`
- `salary_max_monthly = NULL`

### 4. Dữ liệu thiếu
- Một số job không có thông tin lương
- Các trường salary sẽ là NULL
- Vẫn lưu job bình thường

---

## 🐛 TROUBLESHOOTING

### Lỗi: "No module named 'salary_parser'"
```bash
# Đảm bảo file salary_parser.py ở cùng thư mục
cd Science/crawler
ls salary_parser.py  # Phải thấy file này
```

### Lỗi: Database không có cột salary
```bash
# Chạy lại crawler, nó sẽ tự động thêm cột
cd Science/crawler
python realtime_crawler.py
```

### Lương hiển thị sai
```bash
# Kiểm tra salary_text gốc
sqlite3 ../it_jobs_vietnam.db
SELECT job_id, salary_text, salary_min_monthly, salary_max_monthly 
FROM jobs_realtime 
WHERE job_id = 'YOUR_JOB_ID';
```

---

## ✅ CHECKLIST

- [ ] Đã chạy `python salary_parser.py` thành công
- [ ] Đã chạy `python realtime_crawler.py` thành công
- [ ] Đã kiểm tra database có cột salary
- [ ] Đã thấy dữ liệu lương trong database
- [ ] Lương năm đã được chia 12 đúng
- [ ] Dashboard hiển thị lương

**Chúc bạn crawl dữ liệu lương thành công! 💰**
