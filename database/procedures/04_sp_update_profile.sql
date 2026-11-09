create or alter procedure sp_CapNhatThongTinCaNhan
    @MaNguoiDung VARCHAR(10),
    @HoTen NVARCHAR(100) = NULL,
    @SoDienThoai VARCHAR(15) = NULL,
    @Email VARCHAR(100) = NULL,
    @NgaySinh DATE = NULL,
    @DiaChi NVARCHAR(255) = NULL,
    @GioiTinh NVARCHAR(10) = NULL
as
begin
    set nocount on;

    if not exists (select 1 from NguoiDung where MaNguoiDung = @MaNguoiDung)
    begin
        raiserror (N'Không tìm thấy người dùng với mã này.', 16, 1);
        return;
    end

    begin transaction;
    begin try
        
        update NguoiDung
        set 
            HoTen = ISNULL(@HoTen, HoTen),
            SoDienThoai = ISNULL(@SoDienThoai, SoDienThoai),
            Email = ISNULL(@Email, Email)
        where MaNguoiDung = @MaNguoiDung;

        if exists (select 1 from SinhVien where MaNguoiDung = @MaNguoiDung)
        begin
            update SinhVien
            set
                NgaySinh = ISNULL(@NgaySinh, NgaySinh),
                DiaChi = ISNULL(@DiaChi, DiaChi),
                GioiTinh = ISNULL(@GioiTinh, GioiTinh)
            where MaNguoiDung = @MaNguoiDung;
        end
        
        commit transaction;
        select 1 as SuccessStatus, N'Cập nhật thông tin cá nhân thành công.' as Message;

    end try
    begin catch
        rollback transaction;
        declare @ErrorMessage NVARCHAR(4000) = ERROR_MESSAGE();
        raiserror (@ErrorMessage, 16, 1);
    end catch
end;
go

create or alter procedure sp_LayThongTinCaNhan
    @MaNguoiDung VARCHAR(10)
as
begin
    set nocount on;

    -- Lấy thông tin cơ bản từ NguoiDung
    select
        nd.MaNguoiDung,
        nd.HoTen,
        nd.Email,
        nd.SoDienThoai,
        nd.VaiTro,
        nd.TrangThai,
        nd.MatKhau,
        -- Thông tin SinhVien (nếu là sinh viên)
        sv.MaSinhVien,
        sv.MaLopHanhChinh,
        sv.NgaySinh,
        sv.GioiTinh,
        sv.DiaChi,
        lhc.TenLopHanhChinh,
        -- Thông tin GiangVien (nếu là giảng viên)
        gv.MaGiangVien,
        gv.MaKhoa,
        gv.HocVi,
        k.TenKhoa
    from NguoiDung nd
    left join SinhVien sv on nd.MaNguoiDung = sv.MaNguoiDung
    left join LopHanhChinh lhc on sv.MaLopHanhChinh = lhc.MaLopHanhChinh
    left join GiangVien gv on nd.MaNguoiDung = gv.MaNguoiDung
    left join Khoa k on gv.MaKhoa = k.MaKhoa
    where nd.MaNguoiDung = @MaNguoiDung 
       OR sv.MaSinhVien = @MaNguoiDung
       OR gv.MaGiangVien = @MaNguoiDung;
end;
GO