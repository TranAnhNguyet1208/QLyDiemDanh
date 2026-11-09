use qlsv;
go

create or alter procedure sp_ThemLopHocPhan
    @MaLopHocPhan VARCHAR(10),
    @MaMonHoc VARCHAR(10),
    @HocKy INT,
    @NamHoc VARCHAR(20),
    @MaGiangVien VARCHAR(10) = NULL,
    @GhiChu NVARCHAR(MAX) = NULL
as
begin
    set nocount on;

    if not exists (select 1 from MonHoc where MaMonHoc = @MaMonHoc)
    begin
        raiserror (N'Mã Môn Học không tồn tại.', 16, 1);
        return;
    end

    if @MaGiangVien is not null and not exists (select 1 from GiangVien where MaGiangVien = @MaGiangVien)
    begin
        raiserror (N'Mã Giảng Viên không tồn tại.', 16, 1);
        return;
    end

    begin try
        insert into LopHocPhan (MaLopHocPhan, MaMonHoc, MaGiangVien, HocKy, NamHoc, GhiChu)
        values (@MaLopHocPhan, @MaMonHoc, @MaGiangVien, @HocKy, @NamHoc, @GhiChu);
        
        select 1 as SuccessStatus, N'Thêm lớp học phần thành công' as Message;
    end try
    begin catch
        declare @ErrorMessage_LHP NVARCHAR(4000) = ERROR_MESSAGE();
        raiserror (@ErrorMessage_LHP, 16, 1);
    end catch
end;
go

create or alter procedure sp_CapNhatGiangVienLHP
    @MaLopHocPhan VARCHAR(10),
    @MaGiangVienMoi VARCHAR(10)
as
begin
    set nocount on;

    if not exists (select 1 from GiangVien where MaGiangVien = @MaGiangVienMoi)
    begin
        raiserror (N'Mã Giảng Viên mới không tồn tại.', 16, 1);
        return;
    end

    update LopHocPhan
    set MaGiangVien = @MaGiangVienMoi
    where MaLopHocPhan = @MaLopHocPhan;

    if @@ROWCOUNT = 0
    begin
        raiserror (N'Không tìm thấy Lớp Học Phần với mã này.', 16, 1);
        return;
    end
    
    select 1 as SuccessStatus, N'Cập nhật giảng viên cho lớp học phần thành công' as Message;
end;
go

create or alter procedure sp_SuaLopHocPhan
    @MaLopHocPhan VARCHAR(10),
    @MaMonHoc VARCHAR(10) = NULL,
    @MaGiangVien VARCHAR(10) = NULL,
    @HocKy INT = NULL,
    @NamHoc VARCHAR(20) = NULL,
    @GhiChu NVARCHAR(MAX) = NULL
as
begin
    set nocount on;

    if @MaMonHoc is not null and not exists (select 1 from MonHoc where MaMonHoc = @MaMonHoc)
    begin
        raiserror (N'Mã Môn Học mới không tồn tại.', 16, 1);
        return;
    end

    if @MaGiangVien is not null and not exists (select 1 from GiangVien where MaGiangVien = @MaGiangVien)
    begin
        raiserror (N'Mã Giảng Viên mới không tồn tại.', 16, 1);
        return;
    end

    update LopHocPhan
    set
        MaMonHoc = ISNULL(@MaMonHoc, MaMonHoc),
        MaGiangVien = ISNULL(@MaGiangVien, MaGiangVien),
        HocKy = ISNULL(@HocKy, HocKy),
        NamHoc = ISNULL(@NamHoc, NamHoc),
        GhiChu = ISNULL(@GhiChu, GhiChu)
    where MaLopHocPhan = @MaLopHocPhan;

    if @@ROWCOUNT = 0
    begin
        raiserror (N'Không tìm thấy Lớp học phần.', 16, 1);
        return;
    end
    
    select 1 as SuccessStatus, N'Cập nhật thông tin Lớp học phần thành công' as Message;
end;
GO

create or alter procedure sp_XoaLopHocPhan
    @MaLopHocPhan VARCHAR(10)
as
begin
    set nocount on;

    if exists (select 1 from DangKyLopHocPhan where MaLopHocPhan = @MaLopHocPhan)
    begin
        raiserror (N'Không thể xóa. Lớp học phần này vẫn còn Sinh viên đăng ký.', 16, 1);
        return;
    end
    
    if exists (select 1 from BuoiHoc where MaLopHocPhan = @MaLopHocPhan)
    begin
        raiserror (N'Không thể xóa. Lớp học phần này vẫn còn Buổi học.', 16, 1);
        return;
    end

    delete from LopHocPhan
    where MaLopHocPhan = @MaLopHocPhan;

    if @@ROWCOUNT = 0
    begin
        raiserror (N'Không tìm thấy Lớp học phần với mã này.', 16, 1);
        return;
    end

    select 1 as SuccessStatus, N'Xóa Lớp học phần thành công' as Message;
end;
GO

create or alter procedure sp_LayChiTietLHP
    @MaLopHocPhan VARCHAR(10)
as
begin
    set nocount on;

    select 
        lhp.MaLopHocPhan,
        lhp.MaMonHoc,
        mh.TenMonHoc,
        lhp.MaGiangVien,
        nd_gv.HoTen as TenGiangVien,
        lhp.HocKy,
        lhp.NamHoc,
        lhp.GhiChu
    from LopHocPhan as lhp
    left join MonHoc as mh on lhp.MaMonHoc = mh.MaMonHoc
    left join GiangVien as gv on lhp.MaGiangVien = gv.MaGiangVien
    left join NguoiDung as nd_gv on gv.MaNguoiDung = nd_gv.MaNguoiDung
    where lhp.MaLopHocPhan = @MaLopHocPhan;
end;
GO


GO

create or alter procedure sp_LayDanhSachLopHocPhan
as
begin
    set nocount on;

    select 
        lhp.MaLopHocPhan,
        lhp.MaMonHoc,
        mh.TenMonHoc,
        lhp.MaGiangVien,
        nd.HoTen as TenGiangVien,
        lhp.HocKy,
        lhp.NamHoc,
        (SELECT COUNT(*) FROM DangKyLopHocPhan dk WHERE dk.MaLopHocPhan = lhp.MaLopHocPhan) as SiSo
    from LopHocPhan as lhp
    left join MonHoc as mh on lhp.MaMonHoc = mh.MaMonHoc
    left join GiangVien as gv on lhp.MaGiangVien = gv.MaGiangVien
    left join NguoiDung as nd on gv.MaNguoiDung = nd.MaNguoiDung
    order by lhp.NamHoc desc, lhp.HocKy desc, lhp.MaLopHocPhan asc;
end;
go

create or alter procedure sp_DangKyLopHocPhan
    @MaSinhVien VARCHAR(10),
    @MaLopHocPhan VARCHAR(10)
as
begin
    set nocount on;

    if not exists (select 1 from SinhVien where MaSinhVien = @MaSinhVien)
    begin
        raiserror (N'Mã Sinh Viên không tồn tại.', 16, 1);
        return;
    end

    if not exists (select 1 from LopHocPhan where MaLopHocPhan = @MaLopHocPhan)
    begin
        raiserror (N'Mã Lớp Học Phần không tồn tại.', 16, 1);
        return;
    end

    if exists (select 1 from DangKyLopHocPhan where MaSinhVien = @MaSinhVien and MaLopHocPhan = @MaLopHocPhan)
    begin
        raiserror (N'Sinh viên đã đăng ký lớp học phần này từ trước.', 16, 1);
        return;
    end

    begin try
        insert into DangKyLopHocPhan (
            MaSinhVien, 
            MaLopHocPhan, 
            NgayDangKy, 
            TrangThai
        )
        values (
            @MaSinhVien, 
            @MaLopHocPhan, 
            GETDATE(), 
            N'Đã đăng ký'
        );
        
        select 1 as SuccessStatus, N'Đăng ký lớp học phần thành công' as Message;
    end try
    begin catch
        declare @ErrorMessage_DK NVARCHAR(4000) = ERROR_MESSAGE();
        raiserror (@ErrorMessage_DK, 16, 1);
    end catch
end;
go

create or alter procedure sp_DangKyLHP_TheoLopHanhChinh
    @MaLopHanhChinh VARCHAR(10),
    @MaLopHocPhan VARCHAR(10)
as
begin
    set nocount on;

    if not exists (select 1 from LopHanhChinh where MaLopHanhChinh = @MaLopHanhChinh)
    begin
        raiserror (N'Mã Lớp Hành Chính không tồn tại.', 16, 1);
        return;
    end

    if not exists (select 1 from LopHocPhan where MaLopHocPhan = @MaLopHocPhan)
    begin
        raiserror (N'Mã Lớp Học Phần không tồn tại.', 16, 1);
        return;
    end

    insert into DangKyLopHocPhan (
        MaSinhVien, 
        MaLopHocPhan, 
        NgayDangKy, 
        TrangThai
    )
    select 
        sv.MaSinhVien,
        @MaLopHocPhan,
        GETDATE(),
        N'Đã đăng ký'
    from SinhVien as sv
    where sv.MaLopHanhChinh = @MaLopHanhChinh
        and not exists (
            select 1 
            from DangKyLopHocPhan as dk
            where dk.MaSinhVien = sv.MaSinhVien 
              and dk.MaLopHocPhan = @MaLopHocPhan
        );
    
    select 1 as SuccessStatus, N'Đăng ký hàng loạt thành công.' as Message, @@ROWCOUNT as SoLuongDaThem;
end;
go

create or alter procedure sp_HuyDangKyLopHocPhan
    @MaSinhVien VARCHAR(10),
    @MaLopHocPhan VARCHAR(10)
as
begin
    set nocount on;

    delete from DangKyLopHocPhan
    where MaSinhVien = @MaSinhVien 
      and MaLopHocPhan = @MaLopHocPhan;

    if @@ROWCOUNT = 0
    begin
        raiserror (N'Không tìm thấy thông tin đăng ký để hủy.', 16, 1);
        return;
    end

    select 1 as SuccessStatus, N'Hủy đăng ký thành công.' as Message;
end;
go

CREATE OR ALTER PROCEDURE sp_LayDanhSachSV_LHP
    @MaLopHocPhan VARCHAR(10)
AS
BEGIN
    SET NOCOUNT ON;

    SELECT
        sv.MaSinhVien,
        nd.HoTen,
        nd.Email,
        dk.TrangThai as TrangThaiDangKy,
        nd.SoDienThoai
    FROM SinhVien sv
    INNER JOIN NguoiDung nd ON sv.MaNguoiDung = nd.MaNguoiDung
    INNER JOIN DangKyLopHocPhan dk ON sv.MaSinhVien = dk.MaSinhVien
    WHERE dk.MaLopHocPhan = @MaLopHocPhan;
END
GO

CREATE OR ALTER PROCEDURE sp_ThemSinhVienVaoLHP
    @MaLopHocPhan VARCHAR(10),
    @MaSinhVien VARCHAR(10)
AS
BEGIN
    SET NOCOUNT ON;

    IF NOT EXISTS (SELECT 1 FROM SinhVien WHERE MaSinhVien = @MaSinhVien)
    BEGIN
        SELECT 0 AS SuccessStatus, N'Mã sinh viên không tồn tại' AS Message;
        RETURN;
    END

    IF NOT EXISTS (SELECT 1 FROM LopHocPhan WHERE MaLopHocPhan = @MaLopHocPhan)
    BEGIN
        SELECT 0 AS SuccessStatus, N'Mã lớp học phần không tồn tại' AS Message;
        RETURN;
    END

    IF EXISTS (SELECT 1 FROM DangKyLopHocPhan WHERE MaSinhVien = @MaSinhVien AND MaLopHocPhan = @MaLopHocPhan)
    BEGIN
        SELECT 0 AS SuccessStatus, N'Sinh viên đã đăng ký lớp học phần này' AS Message;
        RETURN;
    END

    INSERT INTO DangKyLopHocPhan (MaSinhVien, MaLopHocPhan, NgayDangKy, TrangThai)
    VALUES (@MaSinhVien, @MaLopHocPhan, GETDATE(), N'Đã đăng ký');

    SELECT 1 AS SuccessStatus, N'Thêm sinh viên vào lớp học phần thành công' AS Message;
END
GO
