use qlsv;
go

create or alter procedure sp_ThemKhoa
    @MaKhoa VARCHAR(10),
    @TenKhoa NVARCHAR(100),
    @SoDienThoai VARCHAR(15) = NULL,
    @Email VARCHAR(100) = NULL,
    @PhongLamViec NVARCHAR(50) = NULL
as
begin
    set nocount on;
    begin try
        insert into Khoa (MaKhoa, TenKhoa, SoDienThoai, Email, PhongLamViec)
        values (@MaKhoa, @TenKhoa, @SoDienThoai, @Email, @PhongLamViec);
        
        select 1 as SuccessStatus, N'Thêm khoa thành công' as Message;
    end try
    begin catch
        declare @ErrorMessage_Khoa NVARCHAR(4000) = ERROR_MESSAGE();
        raiserror (@ErrorMessage_Khoa, 16, 1);
    end catch
end;
go

create or alter procedure sp_SuaKhoa
    @MaKhoa VARCHAR(10),
    @TenKhoa NVARCHAR(100),
    @SoDienThoai VARCHAR(15) = NULL,
    @Email VARCHAR(100) = NULL,
    @PhongLamViec NVARCHAR(50) = NULL
as
begin
    set nocount on;
    
    update Khoa
    set 
        TenKhoa = @TenKhoa,
        SoDienThoai = @SoDienThoai,
        Email = @Email,
        PhongLamViec = @PhongLamViec
    where MaKhoa = @MaKhoa;

    if @@ROWCOUNT = 0
    begin
        raiserror (N'Không tìm thấy khoa với mã này.', 16, 1);
        return;
    end

    select 1 as SuccessStatus, N'Cập nhật khoa thành công' as Message;
end;
GO

create or alter procedure sp_XoaKhoa
    @MaKhoa VARCHAR(10)
as
begin
    set nocount on;

    if exists (select 1 from GiangVien where MaKhoa = @MaKhoa)
    begin
        raiserror (N'Không thể xóa. Khoa này vẫn còn Giảng viên.', 16, 1);
        return;
    end
    
    if exists (select 1 from MonHoc where MaKhoa = @MaKhoa)
    begin
        raiserror (N'Không thể xóa. Khoa này vẫn còn Môn học.', 16, 1);
        return;
    end

    delete from Khoa
    where MaKhoa = @MaKhoa;

    if @@ROWCOUNT = 0
    begin
        raiserror (N'Không tìm thấy khoa với mã này.', 16, 1);
        return;
    end

    select 1 as SuccessStatus, N'Xóa khoa thành công' as Message;
end;
GO

create or alter procedure sp_LayChiTietKhoa
    @MaKhoa VARCHAR(10)
as
begin
    set nocount on;

    select 
        MaKhoa, 
        TenKhoa, 
        SoDienThoai, 
        Email, 
        PhongLamViec
    from Khoa
    where MaKhoa = @MaKhoa;
end;

create or alter procedure sp_LayDanhSachKhoa
as
begin
    set nocount on;
    select MaKhoa, TenKhoa, SoDienThoai, Email, PhongLamViec from Khoa;
end;
GO

