create or alter procedure sp_ThemGiangVien
    @MaKhoa VARCHAR(10), 
    @HoTen NVARCHAR(100),
    @MaGiangVien VARCHAR(10),
    @HocVi NVARCHAR(50) = NULL
as
begin
    set nocount on;
    
    if not exists (select 1 from Khoa where MaKhoa = @MaKhoa)
    begin
        raiserror (N'Mã Khoa không tồn tại.', 16, 1);
        return;
    end
    
    declare @Prefix VARCHAR(3) = LEFT(@MaKhoa, 3);
    declare @NewMaNguoiDung VARCHAR(10);
    declare @CurrentMax INT;

    select @CurrentMax = MAX(CAST(SUBSTRING(MaNguoiDung, 4, 7) as INT))
    from NguoiDung
    where MaNguoiDung like @Prefix + '%';

    set @NewMaNguoiDung = @Prefix + FORMAT(ISNULL(@CurrentMax, 0) + 1, 'D7');

    declare @Email_Auto VARCHAR(100) = @MaGiangVien + '@cmcu.edu.vn';
    declare @MatKhau_Default VARCHAR(255) = 'Abc@123';

    begin transaction;
    
    begin try
        insert into NguoiDung (
            MaNguoiDung, HoTen, Email, MatKhau, 
            SoDienThoai, VaiTro, TrangThai
        )
        values (
            @NewMaNguoiDung, @HoTen, @Email_Auto, @MatKhau_Default, 
            NULL, 'giangvien', N'Hoạt động'
        );
        
        insert into GiangVien (
            MaGiangVien, MaNguoiDung, MaKhoa, HocVi, GhiChu
        )
        values (
            @MaGiangVien, @NewMaNguoiDung, @MaKhoa, @HocVi, NULL
        );

        commit transaction;
        
        select 1 as SuccessStatus, N'Thêm giảng viên thành công' as Message, @NewMaNguoiDung as GeneratedID;
        
    end try
    begin catch
        rollback transaction;
        declare @ErrorMessage_GV NVARCHAR(4000) = ERROR_MESSAGE();
        raiserror (@ErrorMessage_GV, 16, 1);
    end catch
end;
go

create or alter procedure sp_Admin_SuaThongTinGiangVien
    @MaGiangVien VARCHAR(10),
    @MaNguoiDung VARCHAR(10),
    @HoTen NVARCHAR(100) = NULL,
    @Email VARCHAR(100) = NULL,
    @SoDienThoai VARCHAR(15) = NULL,
    @TrangThai NVARCHAR(30) = NULL,
    @MaKhoa VARCHAR(10) = NULL,
    @HocVi NVARCHAR(50) = NULL
as
begin
    set nocount on;

    if not exists (select 1 from GiangVien where MaGiangVien = @MaGiangVien and MaNguoiDung = @MaNguoiDung)
    begin
        raiserror (N'Không tìm thấy Giảng viên với Mã Giảng viên và Mã Người dùng tương ứng.', 16, 1);
        return;
    end

    begin transaction;
    begin try
        
        update NguoiDung
        set 
            HoTen = ISNULL(@HoTen, HoTen),
            SoDienThoai = ISNULL(@SoDienThoai, SoDienThoai),
            Email = ISNULL(@Email, Email),
            TrangThai = ISNULL(@TrangThai, TrangThai)
        where MaNguoiDung = @MaNguoiDung;

        update GiangVien
        set
            MaKhoa = ISNULL(@MaKhoa, MaKhoa),
            HocVi = ISNULL(@HocVi, HocVi)
        where MaGiangVien = @MaGiangVien;
        
        commit transaction;
        select 1 as SuccessStatus, N'Cập nhật thông tin giảng viên thành công.' as Message;

    end try
    begin catch
        rollback transaction;
        declare @ErrorMessage NVARCHAR(4000) = ERROR_MESSAGE();
        raiserror (@ErrorMessage, 16, 1);
    end catch
end;
GO

create or alter procedure sp_XoaGiangVien
    @MaGiangVien VARCHAR(10)
as
begin
    set nocount on;

    if exists (select 1 from LopHocPhan where MaGiangVien = @MaGiangVien)
    begin
        raiserror (N'Không thể xóa. Giảng viên này vẫn đang phụ trách Lớp học phần.', 16, 1);
        return;
    end

    declare @MaNguoiDung VARCHAR(10);
    select @MaNguoiDung = MaNguoiDung from GiangVien where MaGiangVien = @MaGiangVien;

    if @MaNguoiDung is null
    begin
        raiserror (N'Không tìm thấy giảng viên với mã này.', 16, 1);
        return;
    end

    begin transaction;
    begin try
        delete from NguoiDung
        where MaNguoiDung = @MaNguoiDung;

        commit transaction;
        select 1 as SuccessStatus, N'Xóa giảng viên thành công' as Message;
    end try
    begin catch
        rollback transaction;
        declare @ErrorMessage NVARCHAR(4000) = ERROR_MESSAGE();
        raiserror (@ErrorMessage, 16, 1);
    end catch
end;
GO

create or alter procedure sp_LayDanhSachGV
as
begin
    set nocount on;

    select 
        gv.MaGiangVien,  -- [0]
        nd.HoTen,        -- [1]
        nd.Email,        -- [2]
        nd.TrangThai,    -- [3]
        k.TenKhoa,       -- [4]
        gv.HocVi,        -- [5]
        nd.SoDienThoai   -- [6]
    from GiangVien as gv
    join NguoiDung as nd on gv.MaNguoiDung = nd.MaNguoiDung
    left join Khoa as k on gv.MaKhoa = k.MaKhoa
    where nd.VaiTro = 'giangvien';
end;
GO

create or alter procedure sp_LayChiTietGiangVien
    @MaGiangVien VARCHAR(10)
as
begin
    set nocount on;

    select 
        gv.MaGiangVien,
        gv.MaNguoiDung,
        nd.HoTen,
        nd.Email,
        nd.SoDienThoai,
        nd.TrangThai,
        gv.MaKhoa,
        k.TenKhoa,
        gv.HocVi
    from GiangVien as gv
    join NguoiDung as nd on gv.MaNguoiDung = nd.MaNguoiDung
    left join Khoa as k on gv.MaKhoa = k.MaKhoa
    where gv.MaGiangVien = @MaGiangVien;
end;
GO

