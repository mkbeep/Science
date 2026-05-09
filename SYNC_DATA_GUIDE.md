# 🔄 HƯỚNG DẪN ĐỒNG BỘ DỮ LIỆU

## 📊 HIỆN TRẠNG

### Dashboard (Dữ liệu TĨNH)
- **Nguồn:** `clean_it_jobs.csv`
- **Cập nhật:** Không tự động
- **Hiển thị:** Chi tiết từng job (skills, company, location...)

### Trends (Dữ liệu ĐỘNG)
- **Nguồn:** Bảng `job_trends` (crawler tự động)
- **Cập nhật:** Mỗi 6 giờ
- **Hiển thị:** Số lượng jobs theo thời gian

## ⚠️ VẤN ĐỀ

**Dashboard và Trends KHÔNG đồng bộ:**
- Dashboard hiển thị dữ liệu cũ từ CSV
- Trends hiển thị dữ liệu mới từ crawler
- Người dùng có thể thấy số liệu khác nhau!

---

## ✅ GIẢI PHÁP 1: CẬP NHẬT CSV TỪ CRAWLER

### Cách làm:

Sửa file `crawler/realtime_crawler.py` để lưu chi tiết jobs vào CSV:

```python
def save_jobs_to_csv(jobs):
    """Save detailed jobs to CSV for Dashboard"""
    import pandas as pd
    from datetime import datetime
    
    # Convert jobs to DataFrame
    df = pd.DataFrame(jobs)
    
    # Save to CSV (append mode)
    csv_path = '../clean_it_jobs.csv'
    
    # Read existing CSV
    try:
        existing_df = pd.read_csv(csv_path)
        # Remove duplicates based on job_id
        combined_df = pd.concat([existing_df, df])
        combined_df = combined_df.drop_duplicates(subset=['job_id'], keep='last')
    except FileNotFoundError:
        combined_df = df
    
    # Save back
    combined_df.to_csv(csv_path, index=False)
    print(f"✅ Updated CSV with {len(df)} new jobs")
```

Thêm vào cuối hàm `run_realtime_crawl()`:

```python
# Save detailed jobs to CSV
save_jobs_to_csv(jobs)
```

**Ưu điểm:**
- Dashboard luôn có dữ liệu mới nhất
- Không cần thay đổi code Dashboard

**Nhược điểm:**
- CSV file sẽ lớn dần theo thời gian
- Cần clean up định kỳ

---

## ✅ GIẢI PHÁP 2: DASHBOARD ĐỌC TỪ DATABASE

### Cách làm:

Sửa crawler để lưu chi tiết jobs vào database:

```python
def save_jobs_to_database(jobs):
    """Save detailed jobs to database"""
    import sqlite3
    
    db_path = '../it_jobs_vietnam.db'
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Create table if not exists
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS jobs_realtime (
            job_id TEXT PRIMARY KEY,
            title TEXT,
            company TEXT,
            location TEXT,
            skills TEXT,
            job_level TEXT,
            crawled_date DATE,
            search_keyword TEXT
        )
    ''')
    
    # Insert jobs
    for job in jobs:
        cursor.execute('''
            INSERT OR REPLACE INTO jobs_realtime 
            (job_id, title, company, location, skills, job_level, crawled_date, search_keyword)
            VALUES (?, ?, ?, ?, ?, ?, date('now'), ?)
        ''', (
            job['job_id'],
            job['title'],
            job['company'],
            job['location'],
            job['skills'],
            job['job_level'],
            job['search_keyword']
        ))
    
    conn.commit()
    conn.close()
    print(f"✅ Saved {len(jobs)} jobs to database")
```

Sửa `backend/api.py` để đọc từ database thay vì CSV:

```python
def load_data():
    """Load from database instead of CSV"""
    conn = get_db()
    df = pd.read_sql_query("SELECT * FROM jobs_realtime", conn)
    conn.close()
    return df
```

**Ưu điểm:**
- Tất cả dữ liệu trong 1 database
- Dễ quản lý và query
- Dashboard luôn sync với Trends

**Nhược điểm:**
- Cần sửa nhiều code hơn

---

## ✅ GIẢI PHÁP 3: THÊM TIMESTAMP VÀO DASHBOARD

### Cách làm:

Thêm thông báo vào Dashboard để người dùng biết dữ liệu cũ:

```tsx
<div style={{
  backgroundColor: '#FEF3C7',
  border: '1px solid #F59E0B',
  borderRadius: '4px',
  padding: '16px',
  marginBottom: '16px'
}}>
  <strong>⚠️ Lưu ý:</strong> Dashboard hiển thị dữ liệu snapshot tại thời điểm crawl ban đầu.
  Để xem xu hướng real-time, vui lòng truy cập tab <strong>"Xu Hướng Thị Trường"</strong>.
</div>
```

**Ưu điểm:**
- Không cần sửa code nhiều
- Người dùng hiểu rõ nguồn dữ liệu

**Nhược điểm:**
- Dashboard vẫn hiển thị dữ liệu cũ

---

## 🎯 KHUYẾN NGHỊ

### Cho đồ án/demo:
**Dùng GIẢI PHÁP 3** - Thêm thông báo

**Lý do:**
- Nhanh, đơn giản
- Không ảnh hưởng code hiện tại
- Người dùng hiểu rõ 2 trang khác nhau như thế nào

### Cho production:
**Dùng GIẢI PHÁP 2** - Dashboard đọc từ database

**Lý do:**
- Dữ liệu đồng bộ 100%
- Dễ maintain
- Scalable

---

## 📝 CÁCH TRIỂN KHAI NHANH (GIẢI PHÁP 3)

### 1. Sửa Dashboard.tsx:

Thêm banner này vào đầu component:

```tsx
{/* Data Source Notice */}
<div style={{
  backgroundColor: '#EFF6FF',
  border: '1px solid #BFDBFE',
  borderRadius: '4px',
  padding: '16px',
  marginBottom: '24px',
  display: 'flex',
  alignItems: 'center',
  gap: '12px'
}}>
  <div style={{
    width: '32px',
    height: '32px',
    backgroundColor: '#2563EB',
    borderRadius: '4px',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    color: '#FFFFFF',
    fontSize: '18px',
    fontWeight: 'bold',
    flexShrink: 0
  }}>
    📊
  </div>
  <div>
    <div style={{ 
      fontFamily: 'Noto Serif, serif',
      fontSize: '16px',
      fontWeight: '600',
      color: '#1E3A5F',
      marginBottom: '4px'
    }}>
      Dữ Liệu Snapshot
    </div>
    <div style={{ 
      fontSize: '13px',
      color: '#6B7280',
      lineHeight: '20px'
    }}>
      Dashboard này hiển thị phân tích chi tiết từ dữ liệu đã crawl. 
      Để xem <strong>xu hướng thay đổi theo thời gian</strong>, 
      vui lòng truy cập tab <strong>"Phân Tích"</strong>.
    </div>
  </div>
</div>
```

### 2. Sửa Analytics.tsx:

Thêm banner:

```tsx
{/* Real-time Data Notice */}
<div style={{
  backgroundColor: '#D1FAE5',
  border: '1px solid #10B981',
  borderRadius: '4px',
  padding: '16px',
  marginBottom: '24px',
  display: 'flex',
  alignItems: 'center',
  gap: '12px'
}}>
  <div style={{
    width: '32px',
    height: '32px',
    backgroundColor: '#10B981',
    borderRadius: '4px',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    color: '#FFFFFF',
    fontSize: '18px',
    fontWeight: 'bold',
    flexShrink: 0
  }}>
    🔄
  </div>
  <div>
    <div style={{ 
      fontFamily: 'Noto Serif, serif',
      fontSize: '16px',
      fontWeight: '600',
      color: '#1E3A5F',
      marginBottom: '4px'
    }}>
      Dữ Liệu Real-Time
    </div>
    <div style={{ 
      fontSize: '13px',
      color: '#6B7280',
      lineHeight: '20px'
    }}>
      Dữ liệu được crawler tự động cập nhật <strong>mỗi 6 giờ</strong> từ VietnamWorks. 
      Lần cập nhật gần nhất: <strong>{new Date().toLocaleString('vi-VN')}</strong>
    </div>
  </div>
</div>
```

---

## 📊 TÓM TẮT

| Trang | Nguồn Dữ Liệu | Cập Nhật | Mục Đích |
|-------|----------------|----------|----------|
| **Dashboard** | `clean_it_jobs.csv` | Không tự động | Phân tích CHI TIẾT snapshot |
| **Trends** | `job_trends` table | Mỗi 6 giờ | Theo dõi XU HƯỚNG theo thời gian |

**Kết luận:** 
- 2 trang có mục đích KHÁC NHAU
- Dashboard: Phân tích sâu (skills, companies, locations...)
- Trends: Theo dõi thay đổi (tăng/giảm theo thời gian)

**Để đồng bộ:** Dùng Giải pháp 3 (thêm thông báo) cho nhanh! 🚀
