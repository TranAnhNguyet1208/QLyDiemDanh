create or alter procedure sp_ThemSinhVien
    @MaKhoa VARCHAR(10),
    @HoTen NVARCHAR(100),
    @MaSinhVien VARCHAR(10),
    @MaLopHanhChinh VARCHAR(10) = NULL,
    @NgaySinh DATE = NULL,
    @DiaChi NVARCHAR(255) = NULL,
    @GioiTinh NVARCHAR(10) = NULL
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
    
    declare @Email_Auto VARCHAR(100) = @MaSinhVien + '@st.cmcu.edu.vn';
    declare @MatKhau_Default VARCHAR(255) = 'Abc@123';

    declare @TranCounter INT = @@TRANCOUNT;
    declare @SavePointName VARCHAR(32) = 'sp_ThemSinhVien';

    if @TranCounter > 0
        save transaction @SavePointName;
    else
        begin transaction;
    
    begin try
        insert into NguoiDung (
            MaNguoiDung, HoTen, Email, MatKhau, 
            SoDienThoai, VaiTro, TrangThai
        )
        values (
            @NewMaNguoiDung, @HoTen, @Email_Auto, @MatKhau_Default,
            NULL, 'sinhvien', N'Hoạt động'
        );
        
        insert into SinhVien (
            MaSinhVien, MaNguoiDung, MaLopHanhChinh,
            NgaySinh, DiaChi, GioiTinh, DuLieuKhuonMat, GhiChu
        )
        values (
            @MaSinhVien, @NewMaNguoiDung, @MaLopHanhChinh,
            @NgaySinh, @DiaChi, @GioiTinh, NULL, NULL
        );

        if @TranCounter = 0
            commit transaction;
        
        select 1 as SuccessStatus, N'Thêm sinh viên thành công' as Message, @NewMaNguoiDung as GeneratedID;
        
    end try
    begin catch
        if @TranCounter > 0
            rollback transaction @SavePointName;
        else
            rollback transaction;

        declare @ErrorMessage_SV NVARCHAR(4000) = ERROR_MESSAGE();
        raiserror (@ErrorMessage_SV, 16, 1);
    end catch
end;
go

create or alter procedure sp_XoaSinhVien
    @MaSinhVien VARCHAR(10)
as
begin
    set nocount on;
    
    declare @MaNguoiDung VARCHAR(10);
    select @MaNguoiDung = MaNguoiDung from SinhVien where MaSinhVien = @MaSinhVien;

    if @MaNguoiDung is null
    begin
        raiserror (N'Không tìm thấy sinh viên với mã này.', 16, 1);
        return;
    end

    begin transaction;
    begin try
        -- BƯỚC 1: Xóa lịch sử điểm danh của sinh viên này trước
        -- (Vì bảng LuotDiemDanh khóa ngoại là NO ACTION nên phải xóa tay)
        delete from LuotDiemDanh 
        where MaSinhVien = @MaSinhVien;

        -- BƯỚC 2: Xóa Người dùng
        -- (Bảng SinhVien và DangKyLopHocPhan có ON DELETE CASCADE nên sẽ tự bay màu theo)
        delete from NguoiDung
        where MaNguoiDung = @MaNguoiDung;

        commit transaction;
        select 1 as SuccessStatus, N'Xóa sinh viên và dữ liệu liên quan thành công' as Message;
    end try
    begin catch
        rollback transaction;
        declare @ErrorMessage NVARCHAR(4000) = ERROR_MESSAGE();
        raiserror (@ErrorMessage, 16, 1);
    end catch
end;
go

create or alter procedure sp_Admin_SuaThongTinSinhVien
    @MaSinhVien VARCHAR(10),
    @MaNguoiDung VARCHAR(10),
    @HoTen NVARCHAR(100) = NULL,
    @Email VARCHAR(100) = NULL,
    @SoDienThoai VARCHAR(15) = NULL,
    @TrangThai NVARCHAR(30) = NULL,
    @NgaySinh DATE = NULL,
    @DiaChi NVARCHAR(255) = NULL,
    @GioiTinh NVARCHAR(10) = NULL,
    @MaLopHanhChinh VARCHAR(10) = NULL
as
begin
    set nocount on;

    if not exists (select 1 from SinhVien where MaSinhVien = @MaSinhVien and MaNguoiDung = @MaNguoiDung)
    begin
        raiserror (N'Không tìm thấy Sinh viên với Mã Sinh viên và Mã Người dùng tương ứng.', 16, 1);
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

        update SinhVien
        set
            NgaySinh = ISNULL(@NgaySinh, NgaySinh),
            DiaChi = ISNULL(@DiaChi, DiaChi),
            GioiTinh = ISNULL(@GioiTinh, GioiTinh),
            MaLopHanhChinh = ISNULL(@MaLopHanhChinh, MaLopHanhChinh)
        where MaSinhVien = @MaSinhVien;
        
        commit transaction;
        select 1 as SuccessStatus, N'Cập nhật thông tin sinh viên thành công.' as Message;

    end try
    begin catch
        rollback transaction;
        declare @ErrorMessage NVARCHAR(4000) = ERROR_MESSAGE();
        raiserror (@ErrorMessage, 16, 1);
    end catch
end;
GO

create or alter procedure sp_LayDanhSachSV
    @MaLopHanhChinh VARCHAR(10) = NULL
as
begin
    set nocount on;

    select 
        sv.MaSinhVien, 
        nd.HoTen, 
        nd.Email, 
        nd.TrangThai,
        lhc.TenLopHanhChinh,
        k.TenKhoa,
        nd.SoDienThoai,
        sv.GioiTinh,
        sv.NgaySinh,
        sv.DiaChi,
        sv.DuLieuKhuonMat
    from SinhVien as sv
    join NguoiDung as nd on sv.MaNguoiDung = nd.MaNguoiDung
    left join LopHanhChinh as lhc on sv.MaLopHanhChinh = lhc.MaLopHanhChinh
    left join Khoa as k on k.MaKhoa = LEFT(nd.MaNguoiDung, 3)

    where nd.VaiTro = 'sinhvien'
    and (@MaLopHanhChinh IS NULL OR sv.MaLopHanhChinh = @MaLopHanhChinh);
end;
GO

create or alter procedure sp_LayChiTietSV
    @MaSinhVien VARCHAR(10)
as
begin
    set nocount on;

    select 
        sv.MaSinhVien, 
        sv.MaLopHanhChinh,
        sv.NgaySinh,
        sv.DiaChi,
        sv.GioiTinh,
        nd.MaNguoiDung,
        nd.HoTen, 
        nd.Email, 
        nd.SoDienThoai,
        nd.TrangThai,
        lhc.TenLopHanhChinh
    from SinhVien as sv
    join NguoiDung as nd on sv.MaNguoiDung = nd.MaNguoiDung
    left join LopHanhChinh as lhc on sv.MaLopHanhChinh = lhc.MaLopHanhChinh
    where sv.MaSinhVien = @MaSinhVien;
end;
GO

create or alter procedure sp_LayThongTinSinhVien
    @MaSinhVien VARCHAR(10)
as
begin
    set nocount on;

    select 
        nd.HoTen
    from SinhVien as sv
    join NguoiDung as nd on sv.MaNguoiDung = nd.MaNguoiDung
    where sv.MaSinhVien = @MaSinhVien;
end;
go

