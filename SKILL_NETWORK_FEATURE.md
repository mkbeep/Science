# 🔗 SKILL RELATIONSHIP NETWORK - TÍNH NĂNG MỚI

## 🎯 TỔNG QUAN

**Skill Relationship Network** là tính năng phân tích nâng cao, hiển thị mối quan hệ giữa các kỹ năng trong tin tuyển dụng IT.

### ✨ ĐIỂM NỔI BẬT:

- 🔥 **Network Graph trực quan** - Dễ nhìn, dễ hiểu
- 📊 **Phân tích mối quan hệ** - Skills nào thường đi cùng nhau
- 🎓 **Giá trị học thuật cao** - Thể hiện kỹ năng Data Mining
- 💼 **Ứng dụng thực tế** - Giúp job seeker biết nên học thêm skill gì

---

## 🔍 CÁCH HOẠT ĐỘNG

### 1. Backend API (3 endpoints mới)

#### `/api/skills/relationships`
Trả về các cặp skills thường xuất hiện cùng nhau:
```json
[
  {
    "skill1": "Python",
    "skill2": "SQL",
    "count": 15
  },
  {
    "skill1": "Docker",
    "skill2": "Kubernetes",
    "count": 11
  }
]
```

#### `/api/skills/network`
Trả về dữ liệu cho network graph:
```json
{
  "nodes": [
    {"name": "Python", "value": 66},
    {"name": "SQL", "value": 79}
  ],
  "links": [
    {"source": "Python", "target": "SQL", "value": 15}
  ]
}
```

#### `/api/skills/tech-stacks`
Trả về các tech stack phổ biến:
```json
[
  {
    "skills": ["Python", "SQL", "Pandas"],
    "count": 8
  }
]
```

### 2. Frontend Component

**SkillNetwork.tsx** - Sử dụng React Flow để vẽ network graph:
- Nodes (tròn) = Skills
- Kích thước node = Số lượng jobs
- Edges (đường nối) = Mối quan hệ
- Độ dày edge = Số jobs có cả 2 skills
- Animated edge = Mối quan hệ mạnh (>10 jobs)

---

## 📊 VÍ DỤ PHÂN TÍCH

### Mối Quan Hệ Phát Hiện:

1. **Data Science Stack:**
   - Python ↔ SQL (15 jobs)
   - Python ↔ Pandas (8 jobs)
   - SQL ↔ Data Analysis (13 jobs)

2. **DevOps Stack:**
   - Docker ↔ Kubernetes (11 jobs)
   - AWS ↔ Docker (7 jobs)
   - Jenkins ↔ Docker (5 jobs)

3. **AI/ML Stack:**
   - AI ↔ Deep Learning (18 jobs)
   - Deep Learning ↔ Machine Learning (17 jobs)
   - TensorFlow ↔ PyTorch (6 jobs)

4. **Backend Stack:**
   - Java ↔ Spring Boot (13 jobs)
   - Node.js ↔ JavaScript (9 jobs)
   - C# ↔ .NET (8 jobs)

---

## 🎓 GIÁ TRỊ HỌC THUẬT

### 1. Kỹ Thuật Sử Dụng:

- **Data Mining:** Phát hiện patterns trong dữ liệu
- **Association Rule Mining:** Tìm mối quan hệ giữa items
- **Graph Theory:** Biểu diễn dữ liệu dạng graph
- **Network Analysis:** Phân tích mạng lưới quan hệ

### 2. Thuật Toán:

```sql
-- Tìm skill pairs xuất hiện cùng nhau
SELECT 
    s1.skill_name as skill1,
    s2.skill_name as skill2,
    COUNT(*) as count
FROM job_skills s1
JOIN job_skills s2 ON s1.job_id = s2.job_id
WHERE s1.skill_name < s2.skill_name
GROUP BY s1.skill_name, s2.skill_name
HAVING count >= min_threshold
ORDER BY count DESC
```

### 3. Metrics:

- **Support:** Số lượng jobs có cả 2 skills
- **Confidence:** Xác suất có skill B khi có skill A
- **Lift:** Mức độ quan hệ mạnh hơn ngẫu nhiên

---

## 💡 ỨNG DỤNG THỰC TẾ

### Cho Job Seekers:

1. **Biết nên học thêm skill gì:**
   - Đang biết Python → Nên học SQL (15 jobs)
   - Đang biết Docker → Nên học Kubernetes (11 jobs)

2. **Hiểu tech stack của thị trường:**
   - Data Science: Python + SQL + Pandas
   - DevOps: Docker + Kubernetes + AWS
   - AI/ML: Python + TensorFlow + PyTorch

3. **Tối ưu CV:**
   - Nhấn mạnh skill combinations phổ biến
   - Tăng cơ hội match với job requirements

### Cho Recruiters:

1. **Hiểu yêu cầu thị trường:**
   - Skills nào thường đi cùng nhau
   - Tech stacks phổ biến

2. **Viết job description tốt hơn:**
   - Yêu cầu skills hợp lý
   - Không yêu cầu quá nhiều skills không liên quan

---

## 🚀 CÁCH SỬ DỤNG

### 1. Start Backend:
```bash
cd Science/backend
python api.py
```

### 2. Start Frontend:
```bash
cd Science/frontend
npm start
```

### 3. Truy cập:
```
http://localhost:3000/skill-network
```

### 4. Tương tác:

- **Zoom:** Scroll chuột
- **Pan:** Click và kéo background
- **Move nodes:** Click và kéo node
- **Hover:** Xem thông tin chi tiết

---

## 📈 TỰ ĐỘNG CẬP NHẬT

Network graph sẽ tự động cập nhật khi:

1. **Crawler chạy mỗi 6 giờ** → Thêm jobs mới
2. **Jobs mới có skills mới** → Thêm nodes mới
3. **Skills xuất hiện cùng nhau** → Thêm/cập nhật edges
4. **Refresh trang** → Thấy network mới!

---

## 🎨 CUSTOMIZATION

### Thay đổi số lượng nodes:
```typescript
// SkillNetwork.tsx
const response = await axios.get(
  'http://localhost:5001/api/skills/network?top_skills=20&min_connection=5'
);
```

### Thay đổi màu sắc:
```typescript
style: {
  background: '#10B981',  // Màu xanh lá
  border: '2px solid #059669',
}
```

### Thay đổi layout:
```typescript
// Circular layout
const angle = (index / data.nodes.length) * 2 * Math.PI;
const radius = 300;
const x = 400 + radius * Math.cos(angle);
const y = 300 + radius * Math.sin(angle);
```

---

## 🔥 TẠI SAO GIẢNG VIÊN SẼ THÍCH?

### 1. Khác Biệt:
- ❌ Đồ án khác: Chỉ có bar chart, pie chart
- ✅ Đồ án này: Network graph, phân tích mối quan hệ

### 2. Kỹ Thuật Cao:
- Data Mining
- Graph Theory
- Network Analysis
- Interactive Visualization

### 3. Ứng Dụng Thực Tế:
- Giúp job seekers
- Giúp recruiters
- Phân tích thị trường

### 4. Trình Bày Đẹp:
- Interactive graph
- Smooth animations
- Professional UI

---

## 📊 DEMO SCRIPT

**Khi trình bày với giảng viên:**

1. **Mở trang Skill Network**
   - "Em xin giới thiệu tính năng phân tích mối quan hệ skills"

2. **Giải thích graph:**
   - "Mỗi node là một skill, kích thước tương ứng với số lượng jobs"
   - "Các đường nối thể hiện skills thường xuất hiện cùng nhau"

3. **Point out insights:**
   - "Ví dụ Python và SQL có mối quan hệ mạnh với 15 jobs"
   - "Docker và Kubernetes thường đi cùng nhau trong DevOps jobs"

4. **Giải thích giá trị:**
   - "Giúp job seekers biết nên học thêm skill gì"
   - "Giúp hiểu tech stack phổ biến của thị trường"

5. **Highlight kỹ thuật:**
   - "Em sử dụng thuật toán Association Rule Mining"
   - "Dữ liệu tự động cập nhật từ crawler"

---

## ✅ CHECKLIST DEMO

- [ ] Backend đang chạy (port 5001)
- [ ] Frontend đang chạy (port 3000)
- [ ] Crawler đã chạy ít nhất 1 lần (có dữ liệu)
- [ ] Test API: `curl http://localhost:5001/api/skills/network`
- [ ] Mở trang: `http://localhost:3000/skill-network`
- [ ] Graph hiển thị đúng
- [ ] Có thể zoom, pan, move nodes
- [ ] Insights hiển thị đúng

---

## 🎉 KẾT LUẬN

**Skill Relationship Network** là tính năng nổi bật nhất của đồ án:

✅ Kỹ thuật cao (Data Mining, Graph Theory)  
✅ Trực quan đẹp (Interactive Network Graph)  
✅ Ứng dụng thực tế (Giúp job seekers & recruiters)  
✅ Tự động cập nhật (Từ crawler)  

**→ Giảng viên sẽ rất ấn tượng!** 🔥🔥🔥

---

**Version:** 1.0  
**Created:** May 2026  
**Tech Stack:** Python (Backend) + React + React Flow (Frontend)
