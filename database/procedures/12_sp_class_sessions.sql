use qlsv;
go

create or alter procedure sp_ThemBuoiHoc
    @MaLopHocPhan VARCHAR(10),
    @NgayHoc DATE,
    @PhongHoc NVARCHAR(50) = NULL,
    @ThoiGianBatDau TIME = NULL,
    @ThoiGianKetThuc TIME = NULL,
    @GhiChuBuoiHoc NVARCHAR(MAX) = NULL
as
begin
    set nocount on;

    if not exists (select 1 from LopHocPhan where MaLopHocPhan = @MaLopHocPhan)
    begin
        raiserror (N'Mã Lớp Học Phần không tồn tại.', 16, 1);
        return;
    end

    begin try
        insert into BuoiHoc (
            MaLopHocPhan, 
            NgayHoc, 
            PhongHoc, 
            ThoiGianBatDau, 
            ThoiGianKetThuc, 
            TrangThai, 
            GhiChuBuoiHoc
        )
        values (
            @MaLopHocPhan, 
            @NgayHoc, 
            @PhongHoc, 
            @ThoiGianBatDau, 
            @ThoiGianKetThuc, 
            N'Chưa diễn ra', 
            @GhiChuBuoiHoc
        );
        
        select 1 as SuccessStatus, N'Thêm buổi học thành công' as Message;
    end try
    begin catch
        declare @ErrorMessage_BH NVARCHAR(4000) = ERROR_MESSAGE();
        raiserror (@ErrorMessage_BH, 16, 1);
    end catch
end;
go

create or alter procedure sp_CapNhatBuoiHoc
    @MaBuoiHoc INT,
    @NgayHoc DATE = NULL,
    @PhongHoc NVARCHAR(50) = NULL,
    @ThoiGianBatDau TIME = NULL,
    @ThoiGianKetThuc TIME = NULL,
    @TrangThai NVARCHAR(50) = NULL,
    @GhiChuBuoiHoc NVARCHAR(MAX) = NULL
as
begin
    set nocount on;

    update BuoiHoc
    set
        NgayHoc = ISNULL(@NgayHoc, NgayHoc),
        PhongHoc = ISNULL(@PhongHoc, PhongHoc),
        ThoiGianBatDau = ISNULL(@ThoiGianBatDau, ThoiGianBatDau),
        ThoiGianKetThuc = ISNULL(@ThoiGianKetThuc, ThoiGianKetThuc),
        TrangThai = ISNULL(@TrangThai, TrangThai),
        GhiChuBuoiHoc = ISNULL(@GhiChuBuoiHoc, GhiChuBuoiHoc)
    where MaBuoiHoc = @MaBuoiHoc;

    if @@ROWCOUNT = 0
    begin
        raiserror (N'Không tìm thấy buổi học.', 16, 1);
        return;
    end
    
    select 1 as SuccessStatus, N'Cập nhật thông tin buổi học thành công' as Message;
end;
go

create or alter procedure sp_CapNhatTrangThaiBuoiHocTuDong
as
begin
    set nocount on;
    declare @CurrentDate DATE = GETDATE();
    declare @CurrentTime TIME = CAST(GETDATE() as TIME);

    -- Cập nhật trạng thái 'Đã kết thúc' cho các buổi học đã qua
    update BuoiHoc
    set TrangThai = N'Đã kết thúc'
    where TrangThai != N'Đã kết thúc'
      and (
          NgayHoc < @CurrentDate 
          or (NgayHoc = @CurrentDate and ThoiGianKetThuc < @CurrentTime)
      );
      
    -- Cập nhật trạng thái 'Đang diễn ra'
    update BuoiHoc
    set TrangThai = N'Đang diễn ra'
    where TrangThai != N'Đang diễn ra'
      and NgayHoc = @CurrentDate
      and ThoiGianBatDau <= @CurrentTime
      and ThoiGianKetThuc >= @CurrentTime;
end;
go

create or alter procedure sp_LayDanhSachBuoiHoc
    @NgayBatDau DATE = NULL,
    @NgayKetThuc DATE = NULL,
    @MaLopHocPhan VARCHAR(10) = NULL,
    @MaGiangVien VARCHAR(10) = NULL
as
begin
    set nocount on;

    -- Tự động cập nhật trạng thái trước khi lấy dữ liệu
    exec sp_CapNhatTrangThaiBuoiHocTuDong;

    select 
        bh.MaBuoiHoc,           -- [0]
        bh.NgayHoc,             -- [1]
        bh.ThoiGianBatDau,      -- [2]
        bh.ThoiGianKetThuc,     -- [3]
        bh.PhongHoc,            -- [4]
        bh.TrangThai,           -- [5]
        lhp.MaLopHocPhan,       -- [6]
        mh.TenMonHoc,           -- [7]
        lhp.MaGiangVien,        -- [8]
        nd_gv.HoTen as TenGiangVien, -- [9]
        bh.GhiChuBuoiHoc        -- [10]
    from BuoiHoc as bh
    join LopHocPhan as lhp on bh.MaLopHocPhan = lhp.MaLopHocPhan
    left join MonHoc as mh on lhp.MaMonHoc = mh.MaMonHoc
    left join GiangVien as gv on lhp.MaGiangVien = gv.MaGiangVien
    left join NguoiDung as nd_gv on gv.MaNguoiDung = nd_gv.MaNguoiDung
    where 
        (bh.NgayHoc >= @NgayBatDau or @NgayBatDau is NULL)
        and (bh.NgayHoc <= @NgayKetThuc or @NgayKetThuc is NULL)
        and (lhp.MaLopHocPhan = @MaLopHocPhan or @MaLopHocPhan is NULL)
        and (lhp.MaGiangVien = @MaGiangVien or @MaGiangVien is NULL)
    order by bh.NgayHoc desc, bh.ThoiGianBatDau desc;
end;
go

create or alter procedure sp_LayChiTietBuoiHoc
    @MaBuoiHoc INT
as
begin
    set nocount on;

    select 
        bh.MaBuoiHoc,
        bh.MaLopHocPhan,
        lhp.MaMonHoc,
        mh.TenMonHoc,
        lhp.MaGiangVien,
        nd_gv.HoTen as TenGiangVien,
        bh.NgayHoc,
        bh.ThoiGianBatDau,
        bh.ThoiGianKetThuc,
        bh.PhongHoc,
        bh.TrangThai,
        bh.GhiChuBuoiHoc
    from BuoiHoc as bh
    join LopHocPhan as lhp on bh.MaLopHocPhan = lhp.MaLopHocPhan
    left join MonHoc as mh on lhp.MaMonHoc = mh.MaMonHoc
    left join GiangVien as gv on lhp.MaGiangVien = gv.MaGiangVien
    left join NguoiDung as nd_gv on gv.MaNguoiDung = nd_gv.MaNguoiDung
    where bh.MaBuoiHoc = @MaBuoiHoc;
end;
go

create or alter procedure sp_LayBuoiHocCuaSinhVien
    @MaSinhVien VARCHAR(10),
    @NgayBatDau DATE = NULL,
    @NgayKetThuc DATE = NULL
as
begin
    set nocount on;

    select 
        bh.MaBuoiHoc,           -- [0]
        bh.NgayHoc,             -- [1]
        bh.ThoiGianBatDau,      -- [2]
        bh.ThoiGianKetThuc,     -- [3]
        bh.PhongHoc,            -- [4]
        bh.TrangThai,           -- [5]
        lhp.MaLopHocPhan,       -- [6]
        mh.TenMonHoc,           -- [7]
        lhp.MaGiangVien,        -- [8]
        nd_gv.HoTen as TenGiangVien, -- [9]
        ISNULL(st.TrangThaiDiemDanh, N'Chưa điểm danh') as TrangThaiDiemDanh -- [10]
    from BuoiHoc as bh
    join LopHocPhan as lhp on bh.MaLopHocPhan = lhp.MaLopHocPhan
    left join MonHoc as mh on lhp.MaMonHoc = mh.MaMonHoc
    left join GiangVien as gv on lhp.MaGiangVien = gv.MaGiangVien
    left join NguoiDung as nd_gv on gv.MaNguoiDung = nd_gv.MaNguoiDung
    join DangKyLopHocPhan as dkhp on lhp.MaLopHocPhan = dkhp.MaLopHocPhan
    outer apply (
        select top 1 ldd.TrangThaiDiemDanh
        from PhienDiemDanh as pdd
        join LuotDiemDanh as ldd on pdd.MaPhienDiemDanh = ldd.MaPhienDiemDanh
        where pdd.MaBuoiHoc = bh.MaBuoiHoc and ldd.MaSinhVien = @MaSinhVien
    ) as st
    where 
        dkhp.MaSinhVien = @MaSinhVien
        and (bh.NgayHoc >= @NgayBatDau or @NgayBatDau is NULL)
        and (bh.NgayHoc <= @NgayKetThuc or @NgayKetThuc is NULL)
    order by bh.NgayHoc asc, bh.ThoiGianBatDau asc;
end;
go

create or alter procedure sp_LayDanhSachBuoiHocTheoLHP
    @MaLopHocPhan VARCHAR(10)
as
begin
    set nocount on;

    select
        bh.MaBuoiHoc,
        bh.NgayHoc,
        bh.PhongHoc,
        bh.ThoiGianBatDau,
        bh.ThoiGianKetThuc,
        bh.TrangThai,
        bh.GhiChuBuoiHoc
    from BuoiHoc as bh
    where bh.MaLopHocPhan = @MaLopHocPhan
    order by bh.NgayHoc desc;
end;
GO