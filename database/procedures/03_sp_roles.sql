create or alter procedure sp_LayDanhSachQuyen
as
begin
    select 'admin' as MaQuyen, N'Quản trị viên' as TenQuyen, N'Toàn quyền hệ thống' as MoTa
    union select 'giangvien', N'Giảng viên', N'Quản lý lớp học phần'
    union select 'sinhvien', N'Sinh viên', N'Xem thông tin cá nhân và điểm danh'
end;
go

create or alter procedure sp_PhanQuyenNguoiDung
    @MaNguoiDung varchar(10),
    @MaQuyen varchar(20)
as
begin
    update NguoiDung 
    set VaiTro = @MaQuyen 
    where MaNguoiDung = @MaNguoiDung;
    
    select 1 as SuccessStatus, N'Phân quyền thành công' as Message;
end;
go