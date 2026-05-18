# 📚 HƯỚNG DẪN SỬ DỤNG - XỬ LÝ DỮ LIỆU TRÙNG LẶP VÀ DỮ LIỆU XẤU

## 🎯 Tóm Tắt Nhanh

Bạn có 3 file Python để xử lý dữ liệu:

1. **deduplication.py** - Xử lý dữ liệu trùng lặp
2. **data_validation.py** - Xử lý dữ liệu xấu
3. **pipeline.py** - Kết hợp cả 2 (KHUYÊN DÙNG)

---

## 🚀 CÁCH 1: SỬ DỤNG PIPELINE (ĐƠN GIẢN NHẤT)

### Bước 1: Vào thư mục
```bash
cd Science/data_quality
```

### Bước 2: Chạy pipeline
```bash
python pipeline.py
```

**Xong!** Pipeline sẽ tự động:
- ✅ Kiểm tra và làm sạch dữ liệu xấu
- ✅ Loại bỏ dữ liệu trùng lặp
- ✅ Tạo file clean_it_jobs.csv
- ✅ Hiển thị báo cáo chi tiết

### Kết quả mẫu:
```
======================================================================
DATA QUALITY PIPELINE STARTED
======================================================================
Input: 5,000 jobs

[STEP 1/2] VALIDATION & CLEANING
----------------------------------------------------------------------
✓ Valid jobs: 4,750
✗ Invalid jobs: 250

[STEP 2/2] DEDUPLICATION
----------------------------------------------------------------------
After exact dedup: 4,500 jobs
After URL dedup: 4,450 jobs
✓ Unique jobs: 4,450

======================================================================
PIPELINE SUMMARY
======================================================================
Input jobs:              5,000
Output jobs:             4,450
Removed jobs:            550
Removal rate:            11.00%
Processing time:         2.35s
======================================================================
```

---

## 🔧 CÁCH 2: SỬ DỤNG RIÊNG LẺ

### A. Chỉ xử lý TRÙNG LẶP

```bash
cd Science/data_quality
python
```

Trong Python:
```python
from deduplication import DeduplicationEngine

# Tạo engine
engine = DeduplicationEngine()

# Xử lý trùng lặp trong database
removed = engine.deduplicate_in_database('jobs_realtime')
print(f"Đã xóa {removed} bản ghi trùng lặp")

# Xem thống kê
engine.print_stats()
```

### B. Chỉ xử lý DỮ LIỆU XẤU

```python
from data_validation import DataValidator

# Tạo validator
validator = DataValidator()

# Ví dụ: Kiểm tra 1 job
job = {
    'title': 'Senior Python Developer',
    'company': 'FPT Software',
    'location': 'Ha Noi',
    'skills': 'Python, Django, PostgreSQL'
}

is_valid, cleaned_job, errors = validator.validate_and_clean_job(job)

if is_valid:
    print("✓ Job hợp lệ!")
    print(f"Điểm chất lượng: {cleaned_job['quality_score']}")
else:
    print("✗ Job không hợp lệ:", errors)
```

---

## 📊 CÁCH 3: XỬ LÝ FILE CSV CỦA BẠN

### Tạo file test_my_data.py:

```python
from pipeline import DataQualityPipeline

# Tạo pipeline
pipeline = DataQualityPipeline()

# Xử lý file CSV của bạn
stats = pipeline.process_from_csv(
    input_csv='../crawler/it_jobs_vietnam.csv',  # File input
    output_csv='../clean_it_jobs.csv',           # File output
    validate=True,              # Có kiểm tra dữ liệu xấu
    deduplicate=True,           # Có loại bỏ trùng lặp
    reject_poor_quality=True,   # Từ chối job chất lượng kém
    use_fuzzy_dedup=False       # False = nhanh, True = chính xác hơn nhưng chậm
)

print("✓ Hoàn thành!")
```

Chạy:
```bash
python test_my_data.py
```

---

## 🎨 CÁCH 4: KIỂM TRA TRỰC QUAN

### Tạo file check_quality.py:

```python
import pandas as pd
from pipeline import DataQualityPipeline

# Đọc file CSV
df = pd.read_csv('../clean_it_jobs.csv')
jobs = df.to_dict('records')

# Tạo báo cáo chất lượng
pipeline = DataQualityPipeline()
pipeline.print_quality_report(jobs)
```

Chạy:
```bash
python check_quality.py
```

Kết quả:
```
======================================================================
DATA QUALITY REPORT
======================================================================

Total jobs: 4,450

Field Completeness:
  title               : 100.00% (4,450/4,450)
  company             : 100.00% (4,450/4,450)
  location            :  95.50% (4,250/4,450)
  skills              :  88.20% (3,925/4,450)
  job_level           :  75.30% (3,351/4,450)
  salary_min          :  45.60% (2,029/4,450)

Quality Score Distribution:
  mean      : 78.50
  median    : 80.00
  min       : 40.00
  max       : 100.00

Field Statistics:
  avg_skills_per_job            : 5.2
  unique_locations              : 63
  unique_companies              : 1,234
======================================================================
```

---

## 🧪 KIỂM TRA NHANH (TEST)

### Tạo file quick_test.py:

```python
from deduplication import DeduplicationEngine
from data_validation import DataValidator

print("="*60)
print("KIỂM TRA NHANH HỆ THỐNG")
print("="*60)

# Test 1: Deduplication
print("\n[TEST 1] Xử lý trùng lặp")
engine = DeduplicationEngine()

test_jobs = [
    {'title': 'Python Dev', 'company': 'FPT', 'url': 'http://a.com'},
    {'title': 'Python Dev', 'company': 'FPT', 'url': 'http://a.com'},  # Trùng
    {'title': 'Java Dev', 'company': 'VNG', 'url': 'http://b.com'},
]

unique = engine.deduplicate_all(test_jobs)
print(f"Input: {len(test_jobs)} jobs")
print(f"Output: {len(unique)} jobs")
print(f"✓ Đã loại bỏ {len(test_jobs) - len(unique)} job trùng lặp")

# Test 2: Validation
print("\n[TEST 2] Kiểm tra dữ liệu xấu")
validator = DataValidator()

good_job = {
    'title': 'Senior Python Developer',
    'company': 'FPT Software',
    'location': 'Ha Noi',
    'skills': 'Python, Django'
}

bad_job = {
    'title': 'X',  # Quá ngắn
    'company': '',  # Thiếu
}

is_valid1, cleaned1, errors1 = validator.validate_and_clean_job(good_job)
is_valid2, cleaned2, errors2 = validator.validate_and_clean_job(bad_job)

print(f"Job tốt: {'✓ Hợp lệ' if is_valid1 else '✗ Không hợp lệ'}")
if is_valid1:
    print(f"  Điểm chất lượng: {cleaned1['quality_score']}/100")

print(f"Job xấu: {'✓ Hợp lệ' if is_valid2 else '✗ Không hợp lệ'}")
if not is_valid2:
    print(f"  Lỗi: {', '.join(errors2)}")

print("\n" + "="*60)
print("✓ HỆ THỐNG HOẠT ĐỘNG BÌNH THƯỜNG")
print("="*60)
```

Chạy:
```bash
python quick_test.py
```

---

## 📝 CÁC TÌNH HUỐNG SỬ DỤNG

### Tình huống 1: Crawler vừa chạy xong, cần làm sạch dữ liệu
```bash
cd Science/data_quality
python pipeline.py
```

### Tình huống 2: Muốn xóa trùng lặp trong database
```python
from deduplication import DeduplicationEngine

engine = DeduplicationEngine()
removed = engine.deduplicate_in_database('jobs_realtime')
print(f"Đã xóa {removed} bản ghi trùng")
```

### Tình huống 3: Kiểm tra chất lượng dữ liệu hiện tại
```python
from pipeline import DataQualityPipeline
import pandas as pd

df = pd.read_csv('../clean_it_jobs.csv')
jobs = df.to_dict('records')

pipeline = DataQualityPipeline()
pipeline.print_quality_report(jobs)
```

### Tình huống 4: Xử lý file CSV mới
```python
from pipeline import DataQualityPipeline

pipeline = DataQualityPipeline()
pipeline.process_from_csv(
    input_csv='my_new_data.csv',
    output_csv='my_clean_data.csv'
)
```

---

## ⚙️ TÙY CHỈNH

### Thay đổi ngưỡng chất lượng:

Sửa trong `data_validation.py`, dòng ~450:
```python
# Mặc định: từ chối job có điểm < 40
if reject_poor_quality and quality == DataQuality.BAD:
    # Thay đổi thành:
    # if reject_poor_quality and score < 50:  # Ngưỡng 50 điểm
```

### Bật fuzzy deduplication (chính xác hơn):

```python
pipeline.process_from_csv(
    input_csv='input.csv',
    output_csv='output.csv',
    use_fuzzy_dedup=True  # Bật fuzzy matching
)
```

**Lưu ý:** Fuzzy dedup chậm hơn nhiều với dataset lớn!

---

## 🐛 XỬ LÝ LỖI

### Lỗi: "No module named 'deduplication'"
```bash
# Đảm bảo bạn đang ở đúng thư mục
cd Science/data_quality
python pipeline.py
```

### Lỗi: "File not found"
```bash
# Kiểm tra file có tồn tại không
ls ../crawler/it_jobs_vietnam.csv

# Hoặc chạy crawler trước
cd ../crawler
python crawl_it_jobs.py
```

### Lỗi: "Database locked"
```bash
# Đóng tất cả kết nối database
# Hoặc đợi crawler chạy xong
```

---

## 📊 HIỂU KẾT QUẢ

### Các loại trùng lặp:
- **Exact duplicates**: Giống hệt nhau (title, company, url)
- **URL duplicates**: Cùng URL
- **Fuzzy duplicates**: Giống ~85% (Python Dev vs Python Developer)
- **Content duplicates**: Cùng nội dung mô tả

### Điểm chất lượng (0-100):
- **90-100**: Excellent - Đầy đủ thông tin
- **75-89**: Good - Thiếu 1-2 trường không quan trọng
- **60-74**: Acceptable - Thiếu một số trường
- **40-59**: Poor - Thiếu nhiều trường quan trọng
- **0-39**: Bad - Không sử dụng được (bị từ chối)

---

## 🎯 KHUYẾN NGHỊ

### Cho dataset nhỏ (< 10,000 jobs):
```python
pipeline.process_from_csv(
    input_csv='input.csv',
    output_csv='output.csv',
    validate=True,
    deduplicate=True,
    reject_poor_quality=True,
    use_fuzzy_dedup=True  # Bật để chính xác hơn
)
```

### Cho dataset lớn (> 10,000 jobs):
```python
pipeline.process_from_csv(
    input_csv='input.csv',
    output_csv='output.csv',
    validate=True,
    deduplicate=True,
    reject_poor_quality=True,
    use_fuzzy_dedup=False  # Tắt để nhanh hơn
)
```

---

## 📞 HỖ TRỢ

Nếu gặp vấn đề:
1. Chạy `python quick_test.py` để kiểm tra hệ thống
2. Xem log chi tiết trong console
3. Kiểm tra file input có đúng format không

---

## ✅ CHECKLIST

- [ ] Đã cài đặt Python 3.7+
- [ ] Đã cài đặt pandas: `pip install pandas`
- [ ] Đã có file CSV hoặc database để xử lý
- [ ] Đã chạy `python quick_test.py` thành công
- [ ] Đã chạy `python pipeline.py` thành công
- [ ] Đã kiểm tra file output

**Chúc bạn xử lý dữ liệu thành công! 🎉**
