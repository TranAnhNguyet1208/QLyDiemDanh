# Class Attendance Management System – Hệ thống quản lý điểm danh lớp học

Ứng dụng desktop quản lý chuyên cần cho trường đại học, gồm **ứng dụng PyQt5** cho 3 vai trò (Quản trị viên, Giảng viên, Sinh viên), **Flask REST API** và **cơ sở dữ liệu Azure SQL** với toàn bộ nghiệp vụ đóng gói trong stored procedure.

> Đồ án môn Lập trình Python – Trường Đại học CMC, 11/2025 (nhóm 5 sinh viên).

**English summary.** Desktop attendance system for a university: PyQt5 client for admins, lecturers and students; Flask REST API (40+ endpoints); Azure SQL Database with a 12-table BCNF schema and stored procedures for every operation, including 17 role-based attendance reports with Excel export. Check-in methods: manual, code, QR code and face recognition (OpenCV LBPH).

---

## Tính năng chính

- **4 cách điểm danh:** thủ công (có mặt / vắng có phép / vắng không phép), nhập mã, quét QR, nhận diện khuôn mặt (OpenCV LBPH).
- **Phân quyền 3 vai trò:** quản trị viên quản lý khoa, lớp, môn, giảng viên, sinh viên, lớp học phần, buổi học; giảng viên điểm danh và xem báo cáo lớp mình; sinh viên tự điểm danh và xem lịch sử chuyên cần.
- **17 báo cáo theo vai trò**, xuất Excel: sinh viên vắng quá 20%, danh sách đủ / không đủ điều kiện dự thi, xu hướng chuyên cần theo tuần/tháng, tỷ lệ chuyên cần theo giảng viên và theo khoa, lịch sử chỉnh sửa (audit log), …
- **Nhập danh sách sinh viên** từ Excel/CSV.

## Kiến trúc

```
PyQt5 desktop (frontend/)  ──HTTP/JSON──▶  Flask REST API (backend/)  ──pyodbc──▶  Azure SQL Database
  ├─ dashboard theo vai trò                 ├─ api/ theo vai trò                       ├─ 12 bảng chuẩn BCNF
  ├─ báo cáo + biểu đồ (matplotlib)         ├─ core/ kết nối DB, xác thực, phân quyền  └─ stored procedure (database/)
  └─ camera + nhận diện khuôn mặt           └─ services/face_recognition
```

## Cấu trúc thư mục

```
class-attendance-management/
├── backend/                 # Flask REST API
│   ├── main.py              # Điểm khởi chạy (http://127.0.0.1:5000)
│   ├── requirements.txt
│   ├── .env.example         # Mẫu cấu hình kết nối database
│   └── app/
│       ├── core/            # config, kết nối DB, đăng nhập / đổi mật khẩu / phân quyền
│       ├── api/             # endpoint cho Admin, GiangVien, SinhVien, điểm danh, đăng ký lớp
│       └── services/face_recognition/
├── frontend/                # Ứng dụng desktop PyQt5
│   ├── run.py / app.py      # Điểm khởi chạy
│   ├── requirements.txt
│   ├── services/            # gọi API backend, nhận diện khuôn mặt
│   └── ui/                  # đăng nhập, dashboard, dialog, báo cáo
├── database/
│   ├── schema.sql           # 12 bảng
│   ├── procedures/          # stored procedure nghiệp vụ (chạy theo số thứ tự)
│   ├── reports/             # stored procedure báo cáo
│   └── sample_data/         # dữ liệu sinh viên GIẢ để thử chức năng nhập file
└── docs/                    # mô tả cấu trúc database, tra cứu nhanh API
```

## Cài đặt và chạy

Yêu cầu: Python 3.10+, SQL Server hoặc Azure SQL Database, [ODBC Driver 17 for SQL Server](https://learn.microsoft.com/sql/connect/odbc/download-odbc-driver-for-sql-server), webcam (nếu dùng điểm danh khuôn mặt).

```bash
# 1. Database: chạy database/schema.sql, rồi procedures/ và reports/ (xem database/README.md)

# 2. Backend
cd backend
python -m venv .venv && .venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env        # điền DB_SERVER, DB_USERNAME, DB_PASSWORD
python main.py

# 3. Frontend (terminal khác)
cd frontend
python -m venv .venv && .venv\Scripts\activate
pip install -r requirements.txt
python run.py
```

## Dữ liệu và bảo mật

- File `.env` (thông tin kết nối database) **không** được đưa lên Git; dùng `.env.example` làm mẫu.
- Ảnh khuôn mặt (`face_data/`) và model đã huấn luyện (`face_model.yml`) là dữ liệu sinh trắc học, được tạo khi chạy ứng dụng và **không** đưa lên Git.
- Danh sách sinh viên thật không có trong repo; `database/sample_data/` chỉ chứa dữ liệu giả.

## Tác giả

Trần Ánh Nguyệt – trưởng nhóm, thiết kế database và backend · [github.com/TranAnhNguyet1208](https://github.com/TranAnhNguyet1208)
