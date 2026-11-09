create or alter procedure sp_ThemMonHoc
    @MaMonHoc VARCHAR(10),
    @TenMonHoc NVARCHAR(100),
    @SoTinChi INT,
    @MaKhoa VARCHAR(10)
as
begin
    set nocount on;

    if not exists (select 1 from Khoa where MaKhoa = @MaKhoa)
    begin
        raiserror (N'Mã Khoa không tồn tại.', 16, 1);
        return;
    end

    begin try
        insert into MonHoc (MaMonHoc, TenMonHoc, SoTinChi, MaKhoa)
        values (@MaMonHoc, @TenMonHoc, @SoTinChi, @MaKhoa);
        
        select 1 as SuccessStatus, N'Thêm môn học thành công' as Message;
    end try
    begin catch
        declare @ErrorMessage_MH NVARCHAR(4000) = ERROR_MESSAGE();
        raiserror (@ErrorMessage_MH, 16, 1);
    end catch
end;
go

create or alter procedure sp_SuaMonHoc
    @MaMonHoc VARCHAR(10),
    @TenMonHoc NVARCHAR(100) = NULL,
    @SoTinChi INT = NULL,
    @MaKhoa VARCHAR(10) = NULL
as
begin
    set nocount on;

    if @MaKhoa is not null and not exists (select 1 from Khoa where MaKhoa = @MaKhoa)
    begin
        raiserror (N'Mã Khoa mới không tồn tại.', 16, 1);
        return;
    end

    update MonHoc
    set
        TenMonHoc = ISNULL(@TenMonHoc, TenMonHoc),
        SoTinChi = ISNULL(@SoTinChi, SoTinChi),
        MaKhoa = ISNULL(@MaKhoa, MaKhoa)
    where MaMonHoc = @MaMonHoc;

    if @@ROWCOUNT = 0
    begin
        raiserror (N'Không tìm thấy Môn học.', 16, 1);
        return;
    end
    
    select 1 as SuccessStatus, N'Cập nhật thông tin Môn học thành công' as Message;
end;
GO

create or alter procedure sp_XoaMonHoc
    @MaMonHoc VARCHAR(10)
as
begin
    set nocount on;

    if exists (select 1 from LopHocPhan where MaMonHoc = @MaMonHoc)
    begin
        raiserror (N'Không thể xóa. Môn học này vẫn đang được Lớp học phần sử dụng.', 16, 1);
        return;
    end

    delete from MonHoc
    where MaMonHoc = @MaMonHoc;

    if @@ROWCOUNT = 0
    begin
        raiserror (N'Không tìm thấy Môn học với mã này.', 16, 1);
        return;
    end

    select 1 as SuccessStatus, N'Xóa Môn học thành công' as Message;
end;
GO

create or alter procedure sp_LayDanhSachMonHoc
as
begin
    set nocount on;

    select 
        mh.MaMonHoc,
        mh.TenMonHoc,
        mh.SoTinChi,
        mh.MaKhoa,
        k.TenKhoa
    from MonHoc as mh
    left join Khoa as k on mh.MaKhoa = k.MaKhoa;
end;
GO

create or alter procedure sp_LayChiTietMonHoc
    @MaMonHoc VARCHAR(10)
as
begin
    set nocount on;

    select
        mh.MaMonHoc,
        mh.TenMonHoc,
        mh.SoTinChi,
        mh.MaKhoa,
        k.TenKhoa
    from MonHoc as mh
    left join Khoa as k on mh.MaKhoa = k.MaKhoa
    where LTRIM(RTRIM(mh.MaMonHoc)) = LTRIM(RTRIM(@MaMonHoc));
end;
GO

