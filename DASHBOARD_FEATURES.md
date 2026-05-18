# Dashboard Features - Tính Năng Mới

## 📊 Tổng Quan

Dashboard đã được cải tiến với 2 tính năng chính:

### 1. ✅ Tính Năng Xuất Dữ Liệu (Export Data)

#### Mô tả
Người dùng có thể xuất toàn bộ dữ liệu việc làm IT từ dashboard ra file để phân tích offline hoặc chia sẻ.

#### Cách sử dụng
1. Nhấn nút **"Xuất Dữ Liệu"** ở góc trên bên phải của dashboard
2. Một hộp thoại sẽ xuất hiện:
   - Chọn **OK** để xuất dữ liệu dưới dạng **CSV**
   - Chọn **Cancel** để xuất dữ liệu dưới dạng **JSON**
3. File sẽ tự động được tải xuống với tên file có định dạng: `it_jobs_data_YYYY-MM-DD.csv` hoặc `it_jobs_data_YYYY-MM-DD.json`

#### Định dạng xuất

**CSV Format:**
- Chứa tất cả các công việc với đầy đủ thông tin
- Hỗ trợ UTF-8 với BOM để hiển thị đúng tiếng Việt trong Excel
- Tự động escape các ký tự đặc biệt (dấu phẩy, dấu ngoặc kép)

**JSON Format:**
- Bao gồm:
  - `exported_at`: Thời gian xuất dữ liệu
  - `stats`: Thống kê tổng quan (tổng số việc làm, công ty, địa điểm, kỹ năng)
  - `top_skills`: Top 15 kỹ năng được yêu cầu nhiều nhất
  - `top_locations`: Top 10 địa điểm
  - `job_levels`: Phân bổ cấp bậc công việc
  - `jobs`: Danh sách đầy đủ các công việc

#### Lợi ích
- 📥 Dễ dàng backup dữ liệu
- 📊 Phân tích sâu hơn với Excel, Python, R
- 📤 Chia sẻ dữ liệu với đồng nghiệp
- 📈 Tạo báo cáo tùy chỉnh

---

### 2. ✅ Thiết Kế Lại Biểu Đồ Top 15 Kỹ Năng

#### Vấn đề cũ
- Biểu đồ cột dọc (vertical bar chart) với labels xoay 45 độ
- Khó đọc tên kỹ năng vì bị chồng lên nhau
- Không hiển thị số lượng chính xác trên biểu đồ

#### Giải pháp mới
Đã chuyển sang **Horizontal Bar Chart** (biểu đồ thanh ngang) với các cải tiến:

#### Tính năng mới
1. **Dễ đọc hơn:**
   - Tên kỹ năng hiển thị ngang, không bị xoay
   - Mỗi kỹ năng có một hàng riêng biệt
   - Không bị chồng lấn

2. **Thông tin chi tiết hơn:**
   - Hiển thị thứ hạng (#1, #2, #3...)
   - Tên kỹ năng rõ ràng
   - Thanh tiến trình màu sắc đa dạng
   - Số lượng chính xác ở bên phải

3. **Trực quan hơn:**
   - 15 màu sắc khác nhau cho mỗi kỹ năng
   - Animation mượt mà khi load dữ liệu
   - Responsive design, tự động điều chỉnh theo kích thước màn hình

4. **Tương tác tốt hơn:**
   - Hover để xem tooltip
   - Số lượng hiển thị bên trong thanh (nếu đủ rộng) và bên ngoài

#### Cấu trúc hiển thị
```
#1  Python          [████████████████████████] 1,234
#2  Java            [████████████████████] 987
#3  JavaScript      [██████████████████] 856
...
```

#### Màu sắc
- Sử dụng palette màu xanh dương (blue) với nhiều tông màu khác nhau
- Từ xanh đậm (#2563EB) đến xanh nhạt (#DDD6FE)
- Tạo sự phân biệt rõ ràng giữa các kỹ năng

---

## 🚀 Cách Chạy và Test

### Khởi động Backend
```bash
cd Science/backend
python api.py
```

### Khởi động Frontend
```bash
cd Science/frontend
npm start
```

### Truy cập Dashboard
Mở trình duyệt và truy cập: `http://localhost:3000`

---

## 🔧 Technical Details

### Dependencies
Không cần thêm thư viện mới, sử dụng:
- React hooks (useState, useEffect, useCallback)
- Axios cho API calls
- Native browser APIs cho file download

### API Endpoints sử dụng
- `GET /api/stats` - Lấy thống kê tổng quan
- `GET /api/skills/top?limit=15` - Lấy top 15 kỹ năng
- `GET /api/locations/top?limit=10` - Lấy top 10 địa điểm
- `GET /api/levels` - Lấy phân bổ cấp bậc
- `GET /api/jobs?page=1&per_page=10000` - Lấy tất cả jobs để xuất

### Browser Compatibility
- Chrome/Edge: ✅ Full support
- Firefox: ✅ Full support
- Safari: ✅ Full support
- IE11: ❌ Not supported (requires modern browser)

---

## 📝 Notes

### Export Data
- Giới hạn xuất tối đa 10,000 jobs mỗi lần
- Nếu cần xuất nhiều hơn, có thể tăng limit trong code
- File CSV có BOM để Excel đọc đúng tiếng Việt

### Performance
- Export có thể mất vài giây với dataset lớn
- Có loading state để người dùng biết đang xử lý
- Sử dụng async/await để không block UI

### Future Improvements
- [ ] Thêm filter trước khi xuất (theo location, skill, level)
- [ ] Xuất dưới dạng Excel (.xlsx) với formatting
- [ ] Xuất biểu đồ dưới dạng hình ảnh (PNG/SVG)
- [ ] Lên lịch xuất tự động hàng ngày/tuần
- [ ] Thêm tùy chọn chọn columns để xuất

---

## 🐛 Troubleshooting

### Lỗi "Không có dữ liệu để xuất"
- Kiểm tra backend có đang chạy không
- Kiểm tra database có dữ liệu không
- Xem console log để biết lỗi chi tiết

### File CSV không hiển thị đúng tiếng Việt trong Excel
- File đã có BOM, nếu vẫn lỗi, thử:
  - Mở bằng Excel > Data > From Text/CSV
  - Chọn encoding UTF-8
  - Import

### Biểu đồ không hiển thị
- Kiểm tra API `/api/skills/top` có trả về dữ liệu không
- Xem console log để debug
- Refresh lại trang

---

## 👨‍💻 Developer Notes

### Code Structure
```
Dashboard.tsx
├── State Management
│   ├── stats, topSkills, topLocations, jobLevels
│   ├── loading, exporting
│   └── refreshEpoch (realtime updates)
├── Data Loading
│   └── loadData() - Fetch all dashboard data
├── Export Functions
│   ├── exportToCSV() - Export to CSV format
│   ├── exportToJSON() - Export to JSON format
│   └── handleExportClick() - Handle user click
└── UI Components
    ├── Stats Grid (4 cards)
    ├── Top Skills Chart (horizontal bars)
    ├── Job Levels Chart (vertical bars)
    └── Top Locations Table
```

### Key Functions

**exportToCSV()**
- Fetches all jobs from API
- Converts to CSV format with proper escaping
- Creates Blob and triggers download
- Handles UTF-8 with BOM for Vietnamese

**exportToJSON()**
- Fetches all jobs from API
- Combines with stats, skills, locations, levels
- Creates comprehensive export object
- Pretty-prints JSON with 2-space indent

**Top Skills Chart**
- Uses horizontal layout for better readability
- Each skill gets unique color from palette
- Shows rank, name, progress bar, and count
- Responsive and accessible

---

## 📄 License

Part of IT Jobs Vietnam project.
