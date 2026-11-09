# Backend - Flask REST API

API Server cho hệ thống Quản lý Điểm danh.

## 🚀 Chạy Server

```bash
pip install -r requirements.txt
python main.py
```

Server sẽ chạy trên: **http://127.0.0.1:5000**

## 📁 Cấu Trúc

```
backend/
├── main.py                    # Entry point - tạo Flask app
├── requirements.txt           # Dependencies
└── app/
    ├── __init__.py           # Tạo app + đăng ký blueprints
    ├── core/                 # Core modules
    │   ├── config.py         # Cấu hình database
    │   ├── KetNoiDB.py       # Database connection wrapper
    │   └── XacThuc/          # Authentication
    │       ├── DangNhap.py   # Login API
    │       ├── DoiMatKhau.py # Change password
    │       └── PhanQuyen.py  # Authorization
    │
    └── api/                  # API Endpoints
        ├── Admin/            # Admin-only APIs
        │   ├── QuanLySinhVien.py      # Student CRUD
        │   ├── QuanLyGiangVien.py     # Teacher CRUD
        │   ├── QuanLyKhoa.py          # Department CRUD
        │   ├── QuanLyMonHoc.py        # Subject CRUD
        │   ├── QuanLyLopHanhChinh.py  # Admin class CRUD
        │   ├── QuanLyLopHocPhan.py    # Class CRUD
        │   ├── QuanLyKhuonMat.py      # Face recognition
        │   ├── BaoCaoAdmin.py         # Admin reports
        │   └── InputSVTuFile.py       # Bulk import
        │
        ├── GiangVien/        # Teacher APIs
        │   ├── ChucNangGiangVien.py   # Get teacher's classes
        │   └── BaoCaoGiangVien.py     # Teacher reports
        │
        ├── SinhVien/         # Student APIs
        │   └── ChucNangSinhVien.py    # Student functions
        │
        ├── DiemDanh.py                # Attendance APIs
        ├── DangKyLop.py               # Class registration
        └── CapNhatThongTinCaNhan.py   # Profile update
```

## 🔌 API Blueprints

| Module | Prefix | Chức năng |
|--------|--------|----------|
| QuanLySinhVien | /api | Quản lý sinh viên |
| QuanLyGiangVien | /api | Quản lý giảng viên |
| QuanLyKhoa | /api | Quản lý khoa |
| QuanLyMonHoc | /api | Quản lý môn học |
| QuanLyLopHanhChinh | /api | Quản lý lớp hành chính |
| QuanLyLopHocPhan | /api | Quản lý lớp học phần |
| QuanLyKhuonMat | /api | Quản lý khuôn mặt |
| BaoCaoAdmin | /api | Báo cáo admin |
| BaoCaoGiangVien | /api | Báo cáo giảng viên |
| ChucNangGiangVien | /api | Chức năng giảng viên |
| ChucNangSinhVien | /api | Chức năng sinh viên |
| DiemDanh | /api | Điểm danh |
| DangKyLop | /api | Đăng ký lớp |
| CapNhatThongTinCaNhan | /api | Cập nhật thông tin cá nhân |
| DangNhap | /api | Đăng nhập |
| DoiMatKhau | /api | Đổi mật khẩu |
| PhanQuyen | /api | Phân quyền |

## 📦 Dependencies

- Flask - Web framework
- pyodbc - MSSQL driver (hoặc MySQL driver)
- opencv-python - Face recognition
- qrcode - QR code generation
- Pillow - Image processing
- openpyxl - Excel processing
- requests - HTTP client
- Werkzeug - WSGI utilities

## 🔐 Authentication

Tất cả API (trừ login) cần:
```python
@require_admin      # Chỉ Admin
@require_giangvien  # Chỉ Giảng viên
@require_sinhvien   # Chỉ Sinh viên
```

## 📊 Database

**Bảng chính:**
- NguoiDung (Users)
- Khoa (Departments)
- GiangVien (Teachers)
- LopHanhChinh (Admin Classes)
- SinhVien (Students)
- MonHoc (Subjects)
- LopHocPhan (Classes)
- BuoiHoc (Sessions)
- PhienDiemDanh (Attendance Sessions)
- LuotDiemDanh (Attendance Records)
- LichSuChinhSua (Audit Log)

Xem `../database/` cho SQL schema và stored procedure.

## 🧪 Test API

### Đăng nhập
```bash
curl -X POST http://127.0.0.1:5000/api/dang-nhap \
  -H "Content-Type: application/json" \
  -d '{"ma_nguoi_dung":"AD001", "mat_khau":"<mat_khau>"}'
```

### Lấy danh sách sinh viên
```bash
curl -X GET http://127.0.0.1:5000/api/sinh-vien \
  -H "Authorization: Bearer <token>"
```

## 🐛 Debug

1. Kích hoạt Flask debug mode trong main.py:
```python
app.run(debug=True)
```

2. Kiểm tra logs trong console

3. Xem request/response trong browser developer tools

## 📝 Ghi Chú

- Tất cả response là JSON
- Error responses chứa `error` key
- Success responses chứa `data` key
- Timestamps là ISO format
- IDs là string (ví dụ: "SV001", "GV002")

---

**Chạy kèm Frontend** để có ứng dụng hoàn chỉnh.
