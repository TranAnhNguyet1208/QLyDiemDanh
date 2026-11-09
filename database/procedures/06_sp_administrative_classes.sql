create or alter procedure sp_ThemLopHanhChinh
    @MaLopHanhChinh VARCHAR(10),
    @TenLopHanhChinh NVARCHAR(50)
as
begin
    set nocount on;
    begin try
        insert into LopHanhChinh (MaLopHanhChinh, TenLopHanhChinh)
        values (@MaLopHanhChinh, @TenLopHanhChinh);
        
        select 1 as SuccessStatus, N'Thêm lớp hành chính thành công' as Message;
    end try
    begin catch
        declare @ErrorMessage_LHC NVARCHAR(4000) = ERROR_MESSAGE();
        raiserror (@ErrorMessage_LHC, 16, 1);
    end catch
end;
go

create or alter procedure sp_LayDanhSachLopHC
as
begin
    set nocount on;

    select 
        MaLopHanhChinh,
        TenLopHanhChinh
    from LopHanhChinh;
end;
GO

create or alter procedure sp_SuaLopHanhChinh
    @MaLopHanhChinh VARCHAR(10),
    @TenLopHanhChinh NVARCHAR(50)
as
begin
    set nocount on;
    
    update LopHanhChinh
    set TenLopHanhChinh = @TenLopHanhChinh
    where MaLopHanhChinh = @MaLopHanhChinh;

    if @@ROWCOUNT = 0
    begin
        raiserror (N'Không tìm thấy Lớp Hành Chính với mã này.', 16, 1);
        return;
    end

    select 1 as SuccessStatus, N'Cập nhật Lớp Hành Chính thành công' as Message;
end;
GO

create or alter procedure sp_XoaLopHanhChinh
    @MaLopHanhChinh VARCHAR(10)
as
begin
    set nocount on;

    if exists (select 1 from SinhVien where MaLopHanhChinh = @MaLopHanhChinh)
    begin
        raiserror (N'Không thể xóa. Lớp Hành Chính này vẫn còn Sinh viên.', 16, 1);
        return;
    end

    delete from LopHanhChinh
    where MaLopHanhChinh = @MaLopHanhChinh;

    if @@ROWCOUNT = 0
    begin
        raiserror (N'Không tìm thấy Lớp Hành Chính với mã này.', 16, 1);
        return;
    end

    select 1 as SuccessStatus, N'Xóa Lớp Hành Chính thành công' as Message;
end;
GO

create or alter procedure sp_LayDanhSachLopHC
as
begin
    set nocount on;

    select 
        MaLopHanhChinh,
        TenLopHanhChinh
    from LopHanhChinh;
end;
GO

create or alter procedure sp_LayChiTietLopHC
    @MaLopHanhChinh VARCHAR(10)
as
begin
    set nocount on;

    select 
        MaLopHanhChinh,
        TenLopHanhChinh
    from LopHanhChinh
    where MaLopHanhChinh = @MaLopHanhChinh;
end;
GO

