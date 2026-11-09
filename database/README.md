# Database (SQL Server / Azure SQL Database)

Chạy theo thứ tự trong SQL Server Management Studio hoặc Azure Data Studio:

1. `schema.sql` – tạo 12 bảng (chuẩn BCNF) và khóa ngoại
2. `procedures/01_*.sql` → `procedures/15_*.sql` – stored procedure cho từng nghiệp vụ (đăng nhập, phân quyền, quản lý lớp, điểm danh, …)
3. `reports/*.sql` – stored procedure báo cáo cho quản trị viên, giảng viên và sinh viên

`sample_data/sinh_vien_mau.csv` là dữ liệu **giả** để thử chức năng nhập danh sách sinh viên từ file (Admin → Nhập từ Excel/CSV).
