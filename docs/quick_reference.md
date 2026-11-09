# Quick Reference — QuanLyDiemDanh

Tóm tắt nhanh các thông tin quan trọng nhất của hệ thống.

---

## 🚀 Khởi Động Nhanh

```bash
# 1. Cài dependencies
cd backend && pip install -r requirements.txt
cd frontend && pip install -r requirements.txt

# 2. Cấu hình database
copy backend\.env.example backend\.env

# Chỉnh sửa backend\.env

# 3. Chạy backend (terminal 1)
cd backend && python main.py

# 4. Chạy frontend (terminal 2)
cd frontend && python run.py
```

Backend: **http://127.0.0.1:5000**

---

## 🔐 Tài khoản

Tài khoản quản trị đầu tiên được tạo trực tiếp trong database; giảng viên/sinh viên do admin tạo trong ứng dụng (mật khẩu mặc định đặt trong stored procedure, nên đổi ngay sau lần đăng nhập đầu).

---

## 🗄️ Database

| Thông tin | Giá trị |
|-----------|---------|
| Loại | Microsoft SQL Server (bắt buộc) |
| Driver | ODBC Driver 17 for SQL Server |
| Tên DB (local) | AttendanceManagement |
| Tên DB (Azure) | qlsv |

**File .env mẫu** (`backend/.env`):
```env
DB_DRIVER={ODBC Driver 17 for SQL Server}
DB_SERVER=127.0.0.1
DB_DATABASE=AttendanceManagement
DB_TRUSTED_CONNECTION=yes
```

---

## 🔌 API — Tóm Tắt Endpoints

### Auth
| Method | URL | Chức năng |
|--------|-----|-----------|
| POST | `/api/dang-nhap` | Đăng nhập |
| POST | `/api/doi-mat-khau` | Đổi mật khẩu |

### Thông tin cá nhân
| Method | URL | Chức năng |
|--------|-----|-----------|
| GET | `/api/taikhoan/<id>` | Lấy thông tin |
| PUT | `/api/taikhoan/<id>` | Cập nhật thông tin |

### Đăng ký lớp học phần
| Method | URL | Chức năng |
|--------|-----|-----------|
| POST | `/api/dangky` | Đăng ký (SV) |
| DELETE | `/api/dangky` | Hủy đăng ký (SV) |
| POST | `/api/dangky-hangloat` | Đăng ký hàng loạt (Admin) |
| GET | `/api/dangky/ds-lop` | DS lớp khả dụng |

### Sinh viên
| Method | URL | Chức năng |
|--------|-----|-----------|
| GET | `/api/sinhvien/lich-su-diem-danh/<ma_sv>` | Lịch sử điểm danh |
| GET | `/api/sinhvien/thong-ke-chuyen-can/<ma_sv>` | Thống kê |
| GET | `/api/sinhvien/canh-bao-chuyen-can/<ma_sv>` | Cảnh báo |

### Giảng viên
| Method | URL | Chức năng |
|--------|-----|-----------|
| GET | `/api/giangvien/lophocphan/<ma_gv>` | Lớp của GV |
| GET | `/api/lophocphan/<ma_lhp>/sinhvien` | SV trong lớp |
| GET | `/api/giangvien/baocao/chuyen-can-sinh-vien/<ma_lhp>` | Báo cáo chuyên cần |
| GET | `/api/giangvien/baocao/canh-bao-cam-thi/<ma_lhp>` | Cảnh báo cấm thi |

### Điểm danh
| Method | URL | Chức năng |
|--------|-----|-----------|
| POST | `/api/phien/tao-thu-cong` | Tạo phiên thủ công |
| POST | `/api/phien/tao-qr` | Tạo phiên QR |
| POST | `/api/diemdanh/thu-cong` | Điểm danh thủ công |
| POST | `/api/diemdanh/nhap-ma` | Điểm danh bằng mã |
| POST | `/api/diemdanh-qr-submit` | Điểm danh QR |
| POST | `/api/phien/<ma_phien>/ket-thuc` | Kết thúc phiên |

### Khuôn mặt
| Method | URL | Chức năng |
|--------|-----|-----------|
| POST | `/api/khuon-mat/upload-anh` | Upload ảnh |
| POST | `/api/khuon-mat/nhan-dien` | Nhận diện |
| GET | `/api/khuon-mat/danh-sach` | Danh sách đã đăng ký |
| DELETE | `/api/khuon-mat/xoa/<ma_sv>` | Xóa dữ liệu |
| GET | `/api/khuon-mat/trang-thai` | Trạng thái hệ thống |

### Admin — CRUD
| Đối tượng | Base URL |
|-----------|----------|
| Sinh viên | `/api/sinh-vien` |
| Giảng viên | `/api/giang-vien` |
| Lớp học phần | `/api/lop-hoc-phan` |
| Lớp hành chính | `/api/lop-hanh-chinh` |
| Môn học | `/api/mon-hoc` |

> Tất cả CRUD đều hỗ trợ: `GET` (list), `POST` (tạo), `GET /<id>` (chi tiết), `PUT /<id>` (sửa), `DELETE /<id>` (xóa)

### Admin — Báo cáo
| Method | URL | Chức năng |
|--------|-----|-----------|
| GET | `/api/baocao/tong-hop` | BC tổng hợp |
| GET | `/api/baocao/thong-ke-theo-giang-vien` | BC theo GV |
| GET | `/api/baocao/danh-sach-vang-qua-nguong` | SV vắng quá ngưỡng |
| GET | `/api/baocao/danh-sach-du-thi` | Danh sách dự thi |
| GET | `/api/baocao/so-sanh-khoa` | So sánh khoa |
| GET | `/api/baocao/lich-su-chinh-sua` | Audit log |

---

## 📁 Cấu Trúc Codebase (Tóm Tắt)

```
backend/app/
├── core/
│   ├── config.py          # Biến môi trường DB / Flask
│   ├── KetNoiDB.py        # Connection pool
│   └── XacThuc/           # Đăng nhập, đổi mật khẩu, phân quyền
├── api/
│   ├── DiemDanh.py        # Tất cả API điểm danh
│   ├── DangKyLop.py       # Đăng ký lớp học phần
│   ├── CapNhatThongTinCaNhan.py
│   ├── Admin/             # CRUD + báo cáo admin
│   ├── GiangVien/         # API cho giảng viên
│   └── SinhVien/          # API cho sinh viên
└── services/face_recognition/  # Nhận diện khuôn mặt

frontend/
├── ui/                    # Giao diện PyQt5
│   ├── admin_dashboard.py
│   ├── teacher_dashboard.py
│   └── student_dashboard.py
└── services/              # Gọi API backend
```

---

## 🗂️ Bảng Database (12 bảng)

| # | Bảng | Mô tả |
|---|------|-------|
| 1 | NguoiDung | Tài khoản người dùng |
| 2 | Khoa | Khoa / Bộ môn |
| 3 | LopHanhChinh | Lớp hành chính |
| 4 | GiangVien | Hồ sơ giảng viên |
| 5 | SinhVien | Hồ sơ sinh viên |
| 6 | MonHoc | Môn học |
| 7 | LopHocPhan | Lớp học phần |
| 8 | DangKyLopHocPhan | Đăng ký lớp (SV ↔ LHP) |
| 9 | BuoiHoc | Buổi học |
| 10 | PhienDiemDanh | Phiên điểm danh |
| 11 | LuotDiemDanh | Lượt điểm danh |
| 12 | LichSuChinhSua | Audit log |

---

## 🔑 Phân Quyền

| Decorator | Vai trò | Áp dụng cho |
|-----------|---------|-------------|
| `@require_admin` | Admin | CRUD dữ liệu, báo cáo tổng hợp |
| `@require_giangvien` | Giảng viên | Quản lý lớp được phân công |
| `@require_sinhvien` | Sinh viên | Xem lịch sử, đăng ký lớp |
| `@require_giangvien_or_sinhvien` | GV hoặc SV | Cập nhật thông tin cá nhân |

---

## 🐛 Debug & Log

| File | Mô tả |
|------|-------|
| `backend/backend.log` | Log cơ bản của backend |
| `backend/backend_debug.log` | Log chi tiết debug |
| `frontend/app.log` | Log của frontend |

---

*Xem README.md để biết hướng dẫn đầy đủ. Xem DATABASE_STRUCTURE_ANALYSIS.md để biết chi tiết schema.*
