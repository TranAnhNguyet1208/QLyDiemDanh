use qlsv;
go

create or alter procedure sp_LayDanhSachLopHocPhan_ChoSinhVien
    @MaSinhVien VARCHAR(10)
as
begin
    set nocount on;

    select 
        lhp.MaLopHocPhan,
        mh.TenMonHoc,
        nd.HoTen as TenGiangVien,
        lhp.HocKy,
        lhp.NamHoc,
        (SELECT COUNT(*) FROM DangKyLopHocPhan dk WHERE dk.MaLopHocPhan = lhp.MaLopHocPhan) as SiSo,
        CASE 
            WHEN EXISTS (SELECT 1 FROM DangKyLopHocPhan dk WHERE dk.MaLopHocPhan = lhp.MaLopHocPhan AND dk.MaSinhVien = @MaSinhVien) THEN 1 
            ELSE 0 
        END as DaDangKy
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

