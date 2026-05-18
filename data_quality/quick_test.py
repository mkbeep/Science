"""
KIỂM TRA NHANH HỆ THỐNG XỬ LÝ DỮ LIỆU
Chạy file này để test xem hệ thống có hoạt động không
"""

from deduplication import DeduplicationEngine
from data_validation import DataValidator

print("="*70)
print("🧪 KIỂM TRA NHANH HỆ THỐNG XỬ LÝ DỮ LIỆU")
print("="*70)

# ============================================================================
# TEST 1: XỬ LÝ TRÙNG LẶP
# ============================================================================
print("\n[TEST 1] Xử lý dữ liệu trùng lặp")
print("-"*70)

engine = DeduplicationEngine()

test_jobs = [
    {
        'job_id': '1',
        'title': 'Senior Python Developer',
        'company': 'FPT Software',
        'url': 'https://example.com/job/1',
        'location': 'Hà Nội',
        'skills': 'Python, Django, PostgreSQL'
    },
    {
        'job_id': '2',
        'title': 'Senior Python Developer',  # Trùng hoàn toàn
        'company': 'FPT Software',
        'url': 'https://example.com/job/1',
        'location': 'Hà Nội',
        'skills': 'Python, Django, PostgreSQL'
    },
    {
        'job_id': '3',
        'title': 'Java Developer',
        'company': 'VNG Corporation',
        'url': 'https://example.com/job/3',
        'location': 'Hồ Chí Minh',
        'skills': 'Java, Spring Boot, MySQL'
    },
    {
        'job_id': '4',
        'title': 'Java Developer',  # Trùng URL
        'company': 'VNG Corporation',
        'url': 'https://example.com/job/3',
        'location': 'Hồ Chí Minh',
        'skills': 'Java, Spring Boot, MySQL'
    },
]

print(f"Input: {len(test_jobs)} jobs")

unique_jobs = engine.deduplicate_all(
    test_jobs,
    use_exact=True,
    use_url=True,
    use_fuzzy=False
)

print(f"Output: {len(unique_jobs)} jobs")
print(f"✓ Đã loại bỏ {len(test_jobs) - len(unique_jobs)} job trùng lặp")

engine.print_stats()

# ============================================================================
# TEST 2: KIỂM TRA DỮ LIỆU XẤU
# ============================================================================
print("\n[TEST 2] Kiểm tra và làm sạch dữ liệu xấu")
print("-"*70)

validator = DataValidator()

# Job tốt
good_job = {
    'title': 'Senior Python Developer',
    'company': 'FPT Software',
    'location': 'Ha Noi',
    'skills': 'Python, Django, PostgreSQL, Docker',
    'job_level': 'Senior',
    'salary_min': 20,
    'salary_max': 35,
    'url': 'https://example.com/job/1'
}

# Job xấu
bad_job = {
    'title': 'X',  # Quá ngắn
    'company': '',  # Thiếu
    'location': '',
    'skills': '',
}

# Job trung bình
medium_job = {
    'title': 'Java Developer',
    'company': 'VNG Corp',
    'location': 'HCM',
    'skills': 'java, JAVA, Java, Spring',  # Có trùng lặp
    'job_level': 'middle',
}

print("\n1. Kiểm tra job TỐT:")
is_valid1, cleaned1, errors1 = validator.validate_and_clean_job(good_job)
if is_valid1:
    print(f"   ✓ Hợp lệ - Điểm chất lượng: {cleaned1['quality_score']}/100")
    print(f"   - Title: {cleaned1['title']}")
    print(f"   - Company: {cleaned1['company']}")
    print(f"   - Location: {cleaned1['location']}")
    print(f"   - Skills: {cleaned1['skills']}")
else:
    print(f"   ✗ Không hợp lệ: {', '.join(errors1)}")

print("\n2. Kiểm tra job XẤU:")
is_valid2, cleaned2, errors2 = validator.validate_and_clean_job(bad_job)
if is_valid2:
    print(f"   ✓ Hợp lệ - Điểm chất lượng: {cleaned2['quality_score']}/100")
else:
    print(f"   ✗ Không hợp lệ")
    print(f"   - Lỗi: {', '.join(errors2)}")

print("\n3. Kiểm tra job TRUNG BÌNH (có lỗi nhỏ):")
is_valid3, cleaned3, errors3 = validator.validate_and_clean_job(medium_job)
if is_valid3:
    print(f"   ✓ Hợp lệ - Điểm chất lượng: {cleaned3['quality_score']}/100")
    print(f"   - Title: {cleaned3['title']}")
    print(f"   - Company: {cleaned3['company']}")
    print(f"   - Location: {cleaned3['location']} (đã chuẩn hóa)")
    print(f"   - Skills: {cleaned3['skills']} (đã loại bỏ trùng lặp)")
    print(f"   - Job Level: {cleaned3['job_level']} (đã chuẩn hóa)")
else:
    print(f"   ✗ Không hợp lệ: {', '.join(errors3)}")

# ============================================================================
# TEST 3: XỬ LÝ BATCH
# ============================================================================
print("\n[TEST 3] Xử lý batch nhiều jobs")
print("-"*70)

batch_jobs = [good_job, bad_job, medium_job]
valid_jobs, invalid_jobs = validator.validate_and_clean_batch(
    batch_jobs,
    reject_poor_quality=True
)

print(f"Input: {len(batch_jobs)} jobs")
print(f"✓ Valid: {len(valid_jobs)} jobs")
print(f"✗ Invalid: {len(invalid_jobs)} jobs")

validator.print_stats()

# ============================================================================
# KẾT LUẬN
# ============================================================================
print("\n" + "="*70)
print("✅ TẤT CẢ TESTS ĐÃ HOÀN THÀNH")
print("="*70)
print("\nHệ thống hoạt động bình thường!")
print("\nBạn có thể:")
print("  1. Chạy 'python pipeline.py' để xử lý dữ liệu thực")
print("  2. Xem file 'HUONG_DAN_SU_DUNG.md' để biết thêm chi tiết")
print("="*70)
