# Phân Tích Cấu Trúc Database - AttendanceManagement

Tài liệu mô tả chi tiết cấu trúc cơ sở dữ liệu SQL Server của hệ thống Quản Lý Điểm Danh.

## 🗄️ Thông Tin Database

| Thuộc tính | Giá trị |
|-----------|---------|
| Tên database | `AttendanceManagement` (local) / `qlsv` (Azure) |
| Hệ quản trị | Microsoft SQL Server |
| Driver | ODBC Driver 17 for SQL Server |
| Encoding | NVARCHAR (Unicode, hỗ trợ tiếng Việt) |

---

## 📊 Sơ Đồ Quan Hệ (ERD Tổng Quan)

```
NguoiDung (1) ──── (1) GiangVien ──── (N) LopHocPhan
NguoiDung (1) ──── (1) SinhVien  ──── (N) DangKyLopHocPhan
                                           └── (N) LopHocPhan

Khoa      (1) ──── (N) GiangVien
Khoa      (1) ──── (N) MonHoc

LopHanhChinh (1) ── (N) SinhVien

MonHoc    (1) ──── (N) LopHocPhan
LopHocPhan(1) ──── (N) BuoiHoc
BuoiHoc   (1) ──── (N) PhienDiemDanh
PhienDiemDanh(1) ── (N) LuotDiemDanh
```

---

## 📋 Chi Tiết Các Bảng

### 1. NguoiDung — Người Dùng

Bảng trung tâm quản lý tài khoản đăng nhập của tất cả vai trò.

| Cột | Kiểu | Ràng buộc | Mô tả |
|-----|------|-----------|-------|
| MaNguoiDung | VARCHAR(10) | PRIMARY KEY | Mã người dùng |
| HoTen | NVARCHAR(100) | NOT NULL | Họ và tên |
| Email | VARCHAR(100) | UNIQUE, NOT NULL | Email đăng nhập |
| MatKhau | VARCHAR(255) | NOT NULL | Mật khẩu (đã hash) |
| SoDienThoai | VARCHAR(15) | — | Số điện thoại |
| VaiTro | NVARCHAR(20) | NOT NULL | `admin` / `giangvien` / `sinhvien` |
| TrangThai | NVARCHAR(30) | NOT NULL | Trạng thái tài khoản |

---

### 2. Khoa — Khoa / Bộ Môn

| Cột | Kiểu | Ràng buộc | Mô tả |
|-----|------|-----------|-------|
| MaKhoa | VARCHAR(10) | PRIMARY KEY | Mã khoa |
| TenKhoa | NVARCHAR(100) | NOT NULL | Tên khoa |
| SoDienThoai | VARCHAR(15) | — | SĐT khoa |
| Email | VARCHAR(100) | — | Email khoa |
| PhongLamViec | NVARCHAR(50) | — | Phòng làm việc |

---

### 3. LopHanhChinh — Lớp Hành Chính

| Cột | Kiểu | Ràng buộc | Mô tả |
|-----|------|-----------|-------|
| MaLopHanhChinh | VARCHAR(10) | PRIMARY KEY | Mã lớp HC |
| TenLopHanhChinh | NVARCHAR(50) | NOT NULL | Tên lớp HC |

---

### 4. GiangVien — Giảng Viên

Liên kết với `NguoiDung` (1-1) và thuộc về `Khoa`.

| Cột | Kiểu | Ràng buộc | Mô tả |
|-----|------|-----------|-------|
| MaGiangVien | VARCHAR(10) | PRIMARY KEY | Mã giảng viên |
| MaNguoiDung | VARCHAR(10) | FK → NguoiDung, UNIQUE | Tài khoản người dùng |
| MaKhoa | VARCHAR(10) | FK → Khoa (SET NULL) | Thuộc khoa |
| HocVi | NVARCHAR(50) | — | Học vị (ThS, TS, ...) |
| GhiChu | NVARCHAR(MAX) | — | Ghi chú |

---

### 5. SinhVien — Sinh Viên

Liên kết với `NguoiDung` (1-1) và thuộc về `LopHanhChinh`.

| Cột | Kiểu | Ràng buộc | Mô tả |
|-----|------|-----------|-------|
| MaSinhVien | VARCHAR(10) | PRIMARY KEY | Mã sinh viên |
| MaNguoiDung | VARCHAR(10) | FK → NguoiDung, UNIQUE | Tài khoản người dùng |
| MaLopHanhChinh | VARCHAR(10) | FK → LopHanhChinh (SET NULL) | Lớp hành chính |
| NgaySinh | DATE | — | Ngày sinh |
| DiaChi | NVARCHAR(255) | — | Địa chỉ |
| GioiTinh | NVARCHAR(10) | — | Giới tính |
| DuLieuKhuonMat | NVARCHAR(MAX) | NULL | Dữ liệu khuôn mặt (metadata) |
| GhiChu | NVARCHAR(MAX) | — | Ghi chú |

---

### 6. MonHoc — Môn Học

| Cột | Kiểu | Ràng buộc | Mô tả |
|-----|------|-----------|-------|
| MaMonHoc | VARCHAR(10) | PRIMARY KEY | Mã môn học |
| TenMonHoc | NVARCHAR(100) | NOT NULL | Tên môn học |
| SoTinChi | INT | NOT NULL | Số tín chỉ |
| MaKhoa | VARCHAR(10) | FK → Khoa (SET NULL) | Thuộc khoa |

---

### 7. LopHocPhan — Lớp Học Phần

| Cột | Kiểu | Ràng buộc | Mô tả |
|-----|------|-----------|-------|
| MaLopHocPhan | VARCHAR(10) | PRIMARY KEY | Mã lớp học phần |
| MaMonHoc | VARCHAR(10) | FK → MonHoc (CASCADE) | Môn học |
| MaGiangVien | VARCHAR(10) | FK → GiangVien (SET NULL) | Giảng viên phụ trách |
| HocKy | INT | NOT NULL | Học kỳ (1, 2, 3...) |
| NamHoc | VARCHAR(20) | NOT NULL | Năm học (vd: 2024-2025) |
| GhiChu | NVARCHAR(MAX) | — | Ghi chú |

---

### 8. DangKyLopHocPhan — Đăng Ký Lớp Học Phần

Bảng trung gian nhiều-nhiều giữa SinhVien và LopHocPhan.

| Cột | Kiểu | Ràng buộc | Mô tả |
|-----|------|-----------|-------|
| MaDangKy | INT | PRIMARY KEY, IDENTITY | Auto-increment |
| MaSinhVien | VARCHAR(10) | FK → SinhVien (CASCADE) | Sinh viên |
| MaLopHocPhan | VARCHAR(10) | FK → LopHocPhan (CASCADE) | Lớp học phần |
| NgayDangKy | DATE | DEFAULT GETDATE() | Ngày đăng ký |
| TrangThai | NVARCHAR(50) | — | Trạng thái đăng ký |
| — | — | UNIQUE(MaSinhVien, MaLopHocPhan) | Mỗi SV chỉ đăng ký 1 lần |

---

### 9. BuoiHoc — Buổi Học

| Cột | Kiểu | Ràng buộc | Mô tả |
|-----|------|-----------|-------|
| MaBuoiHoc | INT | PRIMARY KEY, IDENTITY | Auto-increment |
| MaLopHocPhan | VARCHAR(10) | FK → LopHocPhan (CASCADE) | Lớp học phần |
| NgayHoc | DATE | NOT NULL | Ngày học |
| PhongHoc | NVARCHAR(50) | — | Phòng học |
| ThoiGianBatDau | TIME | — | Giờ bắt đầu |
| ThoiGianKetThuc | TIME | — | Giờ kết thúc |
| TrangThai | NVARCHAR(50) | — | Trạng thái buổi học |
| GhiChuBuoiHoc | NVARCHAR(MAX) | — | Ghi chú |

---

### 10. PhienDiemDanh — Phiên Điểm Danh

Mỗi buổi học có thể có nhiều phiên điểm danh (thủ công, QR, khuôn mặt...).

| Cột | Kiểu | Ràng buộc | Mô tả |
|-----|------|-----------|-------|
| MaPhienDiemDanh | INT | PRIMARY KEY, IDENTITY | Auto-increment |
| MaBuoiHoc | INT | FK → BuoiHoc (CASCADE) | Buổi học |
| ThoiGianBatDauPhien | DATETIME | DEFAULT GETDATE() | Thời gian mở phiên |
| ThoiGianKetThucPhien | DATETIME | — | Thời gian đóng phiên |
| MaCode | VARCHAR(20) | NULL | Mã điểm danh (dùng cho nhập mã / QR) |

---

### 11. LuotDiemDanh — Lượt Điểm Danh

Ghi nhận từng lần điểm danh của sinh viên.

| Cột | Kiểu | Ràng buộc | Mô tả |
|-----|------|-----------|-------|
| MaLuotDiemDanh | INT | PRIMARY KEY, IDENTITY | Auto-increment |
| MaPhienDiemDanh | INT | FK → PhienDiemDanh (CASCADE) | Phiên điểm danh |
| MaSinhVien | VARCHAR(10) | FK → SinhVien (NO ACTION) | Sinh viên |
| TrangThaiDiemDanh | NVARCHAR(50) | NOT NULL | `co_mat` / `vang` / ... |
| PhuongThuc | NVARCHAR(50) | — | `thu_cong` / `qr` / `khuon_mat` / `nhap_ma` |
| ThoiGianDiemDanh | DATETIME | DEFAULT GETDATE() | Thời điểm điểm danh |
| DiaChiIP | VARCHAR(45) | — | IP người điểm danh |
| GhiChuLyDoVang | NVARCHAR(500) | — | Lý do vắng (nếu có) |

---

### 12. LichSuChinhSua — Lịch Sử Chỉnh Sửa (Audit Log)

| Cột | Kiểu | Ràng buộc | Mô tả |
|-----|------|-----------|-------|
| MaLog | INT | PRIMARY KEY, IDENTITY | Auto-increment |
| MaNguoiDung | VARCHAR(10) | FK → NguoiDung (SET NULL) | Người thực hiện |
| HanhDong | NVARCHAR(100) | — | Hành động (INSERT/UPDATE/DELETE) |
| DoiTuong | NVARCHAR(100) | — | Đối tượng bị thay đổi |
| ThoiGian | DATETIME | DEFAULT GETDATE() | Thời điểm thay đổi |
| GhiChu | NVARCHAR(MAX) | — | Chi tiết thay đổi |

---

## 🔗 Thứ Tự Tạo Bảng (Dependencies)

Tạo bảng theo thứ tự để tránh lỗi FK:

```
1. NguoiDung
2. Khoa
3. LopHanhChinh
4. GiangVien        (→ NguoiDung, Khoa)
5. SinhVien         (→ NguoiDung, LopHanhChinh)
6. MonHoc           (→ Khoa)
7. LopHocPhan       (→ MonHoc, GiangVien)
8. DangKyLopHocPhan (→ SinhVien, LopHocPhan)
9. BuoiHoc          (→ LopHocPhan)
10. PhienDiemDanh   (→ BuoiHoc)
11. LuotDiemDanh    (→ PhienDiemDanh, SinhVien)
12. LichSuChinhSua  (→ NguoiDung)
```

> Xem file `database/schema.sql` để chạy script tạo bảng đầy đủ.

---

## 🔒 Chiến Lược Xóa (ON DELETE)

| Quan hệ | Chiến lược | Lý do |
|---------|-----------|-------|
| NguoiDung → GiangVien/SinhVien | CASCADE | Xóa user thì xóa hồ sơ |
| Khoa → GiangVien/MonHoc | SET NULL | Giữ dữ liệu, bỏ liên kết |
| LopHanhChinh → SinhVien | SET NULL | Giữ sinh viên khi xóa lớp HC |
| MonHoc → LopHocPhan | CASCADE | Xóa môn thì xóa lớp |
| LopHocPhan → BuoiHoc | CASCADE | Xóa lớp thì xóa buổi học |
| BuoiHoc → PhienDiemDanh | CASCADE | Xóa buổi thì xóa phiên |
| PhienDiemDanh → LuotDiemDanh | CASCADE | Xóa phiên thì xóa lượt |
| SinhVien → LuotDiemDanh | NO ACTION | Giữ lịch sử dù xóa SV |
| NguoiDung → LichSuChinhSua | SET NULL | Giữ audit log |

---

*Được tạo tự động từ `database/schema.sql`*
