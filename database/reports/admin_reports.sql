create or alter procedure sp_BaoCao_TongHopChuyenCan
    @HocKy INT,
    @NamHoc VARCHAR(20)
as
begin
    set nocount on;

    with 
    TongSV_CTE as (
        select 
            MaLopHocPhan, 
            COUNT(MaSinhVien) as TongSoSV
        from DangKyLopHocPhan
        group by MaLopHocPhan
    ),
    TongBuoiHoc_CTE as (
        select 
            MaLopHocPhan,
            COUNT(MaBuoiHoc) as TongSoBuoiHoc
        from BuoiHoc
        where TrangThai != N'Chưa diễn ra'
        group by MaLopHocPhan
    ),
    TongLuotDiemDanh_CTE as (
        select 
            bh.MaLopHocPhan,
            COUNT(ldd.MaLuotDiemDanh) as TongLuotCoMat
        from LuotDiemDanh as ldd
        join PhienDiemDanh as pd on ldd.MaPhienDiemDanh = pd.MaPhienDiemDanh
        join BuoiHoc as bh on pd.MaBuoiHoc = bh.MaBuoiHoc
        where ldd.TrangThaiDiemDanh = N'Có mặt'
        group by bh.MaLopHocPhan
    )
    select 
        lhp.MaLopHocPhan,
        mh.TenMonHoc,
        nd_gv.HoTen as TenGiangVien,
        ISNULL(sv.TongSoSV, 0) as TongSoSinhVien,
        ISNULL(bh.TongSoBuoiHoc, 0) as SoBuoiDaToChuc,
        
        CASE 
            WHEN (ISNULL(sv.TongSoSV, 0) * ISNULL(bh.TongSoBuoiHoc, 0)) = 0 THEN 0
            ELSE 
                (CAST(ISNULL(ldd.TongLuotCoMat, 0) AS FLOAT) * 100) / (sv.TongSoSV * bh.TongSoBuoiHoc)
        END as TyLeChuyenCanTrungBinh
        
    from LopHocPhan as lhp
    left join MonHoc as mh on lhp.MaMonHoc = mh.MaMonHoc
    left join GiangVien as gv on lhp.MaGiangVien = gv.MaGiangVien
    left join NguoiDung as nd_gv on gv.MaNguoiDung = nd_gv.MaNguoiDung
    left join TongSV_CTE as sv on lhp.MaLopHocPhan = sv.MaLopHocPhan
    left join TongBuoiHoc_CTE as bh on lhp.MaLopHocPhan = bh.MaLopHocPhan
    left join TongLuotDiemDanh_CTE as ldd on lhp.MaLopHocPhan = ldd.MaLopHocPhan
    
    where lhp.HocKy = @HocKy and lhp.NamHoc = @NamHoc;
    
end;
GO

create or alter procedure sp_BaoCao_ChuyenCanTheoGV
as
begin
    set nocount on;

    with 
    TongSV_CTE as (
        select 
            MaLopHocPhan, 
            COUNT(MaSinhVien) as TongSoSV
        from DangKyLopHocPhan
        group by MaLopHocPhan
    ),
    TongBuoiHoc_CTE as (
        select 
            MaLopHocPhan,
            COUNT(MaBuoiHoc) as TongSoBuoiHoc
        from BuoiHoc
        where TrangThai != N'Chưa diễn ra'
        group by MaLopHocPhan
    ),
    TongLuotDiemDanh_CTE as (
        select 
            bh.MaLopHocPhan,
            COUNT(ldd.MaLuotDiemDanh) as TongLuotCoMat
        from LuotDiemDanh as ldd
        join PhienDiemDanh as pd on ldd.MaPhienDiemDanh = pd.MaPhienDiemDanh
        join BuoiHoc as bh on pd.MaBuoiHoc = bh.MaBuoiHoc
        where ldd.TrangThaiDiemDanh = N'Có mặt'
        group by bh.MaLopHocPhan
    ),
    TyLeLopHocPhan_CTE as (
        select
            lhp.MaGiangVien,
            CASE 
                WHEN (ISNULL(sv.TongSoSV, 0) * ISNULL(bh.TongSoBuoiHoc, 0)) = 0 THEN NULL
                ELSE (CAST(ISNULL(ldd.TongLuotCoMat, 0) AS FLOAT) * 100) / (sv.TongSoSV * bh.TongSoBuoiHoc)
            END as TyLeChuyenCan
        from LopHocPhan as lhp
        left join TongSV_CTE as sv on lhp.MaLopHocPhan = sv.MaLopHocPhan
        left join TongBuoiHoc_CTE as bh on lhp.MaLopHocPhan = bh.MaLopHocPhan
        left join TongLuotDiemDanh_CTE as ldd on lhp.MaLopHocPhan = ldd.MaLopHocPhan
        where lhp.MaGiangVien IS NOT NULL
    )
    select 
        gv.MaGiangVien,
        nd_gv.HoTen as TenGiangVien,
        ISNULL(AVG(tllhp.TyLeChuyenCan), 0) as TyLeChuyenCanTrungBinh
    from GiangVien as gv
    join NguoiDung as nd_gv on gv.MaNguoiDung = nd_gv.MaNguoiDung
    left join TyLeLopHocPhan_CTE as tllhp on gv.MaGiangVien = tllhp.MaGiangVien
    group by gv.MaGiangVien, nd_gv.HoTen;

end;
GO

create or alter procedure sp_BaoCao_DSVangQuaMuc
as
begin
    set nocount on;

    with TongSoBuoiDaHoc_CTE as (
        select 
            lhp.MaLopHocPhan, 
            count(bh.MaBuoiHoc) as TongSoBuoiHoc
        from LopHocPhan as lhp
        join BuoiHoc as bh on lhp.MaLopHocPhan = bh.MaLopHocPhan
        where bh.TrangThai != N'Chưa diễn ra'
        group by lhp.MaLopHocPhan
    ),
    TongSoBuoiVang_CTE as (
        select 
            bh.MaLopHocPhan,
            ldd.MaSinhVien,
            count(ldd.MaLuotDiemDanh) as TongSoBuoiVang
        from LuotDiemDanh as ldd
        join PhienDiemDanh as pd on ldd.MaPhienDiemDanh = pd.MaPhienDiemDanh
        join BuoiHoc as bh on pd.MaBuoiHoc = bh.MaBuoiHoc
        where ldd.TrangThaiDiemDanh = N'Vắng có phép' or 
              ldd.TrangThaiDiemDanh = N'Vắng không phép'
        group by bh.MaLopHocPhan, ldd.MaSinhVien
    )
    select 
        sv.MaSinhVien,
        nd.HoTen,
        lhc.TenLopHanhChinh,
        mh.TenMonHoc,
        isnull(v.TongSoBuoiVang, 0) as SoBuoiVang,
        (cast(isnull(v.TongSoBuoiVang, 0) as float) * 100.0) / bh.TongSoBuoiHoc as TyLeVang,
        case 
            when (cast(isnull(v.TongSoBuoiVang, 0) as float) * 100.0) / bh.TongSoBuoiHoc > 20.0 
            then N'Vượt quá 20%'
            else N'Trong giới hạn'
        end as TrangThai
    from DangKyLopHocPhan as dk
    join SinhVien as sv on dk.MaSinhVien = sv.MaSinhVien
    join NguoiDung as nd on sv.MaNguoiDung = nd.MaNguoiDung
    left join LopHanhChinh as lhc on sv.MaLopHanhChinh = lhc.MaLopHanhChinh
    join LopHocPhan as lhp on dk.MaLopHocPhan = lhp.MaLopHocPhan
    join MonHoc as mh on lhp.MaMonHoc = mh.MaMonHoc
    join TongSoBuoiDaHoc_CTE as bh on dk.MaLopHocPhan = bh.MaLopHocPhan
    left join TongSoBuoiVang_CTE as v on dk.MaSinhVien = v.MaSinhVien and dk.MaLopHocPhan = v.MaLopHocPhan
    where 
        bh.TongSoBuoiHoc > 0
        and (cast(isnull(v.TongSoBuoiVang, 0) as float) * 100.0) / bh.TongSoBuoiHoc > 20.0;
end;
go

create or alter procedure sp_BaoCao_ThongKeBuoiHocDiemDanh
as
begin
    set nocount on;

    select 
        count(distinct bh.MaBuoiHoc) as TongSoBuoiHoc,
        count(ldd.MaLuotDiemDanh) as TongLuotDiemDanh,
        count(case when ldd.TrangThaiDiemDanh = N'Có mặt' then 1 end) as TongLuotCoMat,
        count(case when ldd.TrangThaiDiemDanh = N'Vắng có phép' then 1 end) as TongLuotVangCoPhep,
        count(case when ldd.TrangThaiDiemDanh = N'Vắng không phép' then 1 end) as TongLuotVangKhongPhep
    from BuoiHoc as bh
    left join PhienDiemDanh as pd on bh.MaBuoiHoc = pd.MaBuoiHoc
    left join LuotDiemDanh as ldd on pd.MaPhienDiemDanh = ldd.MaPhienDiemDanh
    where bh.TrangThai != N'Chưa diễn ra';
end;
go

create or alter procedure sp_BaoCao_BieuDoTronTyLeChuyenCan
as
begin
    set nocount on;

    with ThongKe as (
        select 
            count(case when ldd.TrangThaiDiemDanh = N'Có mặt' then 1 end) as CoMat,
            count(case when ldd.TrangThaiDiemDanh = N'Vắng có phép' then 1 end) as VangCoPhep,
            count(case when ldd.TrangThaiDiemDanh = N'Vắng không phép' then 1 end) as VangKhongPhep,
            count(ldd.MaLuotDiemDanh) as TongLuot
        from LuotDiemDanh as ldd
    )
    select 
        CoMat,
        VangCoPhep,
        VangKhongPhep,
        TongLuot,
        case when TongLuot > 0 then (cast(CoMat as float) * 100.0 / TongLuot) else 0 end as TyLeCoMat,
        case when TongLuot > 0 then (cast(VangCoPhep as float) * 100.0 / TongLuot) else 0 end as TyLeVangCoPhep,
        case when TongLuot > 0 then (cast(VangKhongPhep as float) * 100.0 / TongLuot) else 0 end as TyLeVangKhongPhep
    from ThongKe;
end;
go

create or alter procedure sp_BaoCao_DSDuKienDuThi
as
begin
    set nocount on;

    with TongSoBuoiDaHoc_CTE as (
        select 
            lhp.MaLopHocPhan, 
            count(bh.MaBuoiHoc) as TongSoBuoiHoc
        from LopHocPhan as lhp
        join BuoiHoc as bh on lhp.MaLopHocPhan = bh.MaLopHocPhan
        where bh.TrangThai != N'Chưa diễn ra'
        group by lhp.MaLopHocPhan
    ),
    TongSoBuoiVang_CTE as (
        select 
            bh.MaLopHocPhan,
            ldd.MaSinhVien,
            count(ldd.MaLuotDiemDanh) as TongSoBuoiVang
        from LuotDiemDanh as ldd
        join PhienDiemDanh as pd on ldd.MaPhienDiemDanh = pd.MaPhienDiemDanh
        join BuoiHoc as bh on pd.MaBuoiHoc = bh.MaBuoiHoc
        where ldd.TrangThaiDiemDanh = N'Vắng có phép' or 
              ldd.TrangThaiDiemDanh = N'Vắng không phép'
        group by bh.MaLopHocPhan, ldd.MaSinhVien
    )
    select 
        sv.MaSinhVien,
        nd.HoTen,
        lhc.TenLopHanhChinh,
        mh.TenMonHoc,
        lhp.MaLopHocPhan,
        bh.TongSoBuoiHoc,
        isnull(v.TongSoBuoiVang, 0) as SoBuoiVang,
        (cast(isnull(v.TongSoBuoiVang, 0) as float) * 100.0) / bh.TongSoBuoiHoc as TyLeVang,
        case 
            when (cast(isnull(v.TongSoBuoiVang, 0) as float) * 100.0) / bh.TongSoBuoiHoc > 20.0 
            then N'Không đủ điều kiện'
            else N'Đủ điều kiện'
        end as DuKienDuThi
    from DangKyLopHocPhan as dk
    join SinhVien as sv on dk.MaSinhVien = sv.MaSinhVien
    join NguoiDung as nd on sv.MaNguoiDung = nd.MaNguoiDung
    left join LopHanhChinh as lhc on sv.MaLopHanhChinh = lhc.MaLopHanhChinh
    join LopHocPhan as lhp on dk.MaLopHocPhan = lhp.MaLopHocPhan
    join MonHoc as mh on lhp.MaMonHoc = mh.MaMonHoc
    join TongSoBuoiDaHoc_CTE as bh on dk.MaLopHocPhan = bh.MaLopHocPhan
    left join TongSoBuoiVang_CTE as v on dk.MaSinhVien = v.MaSinhVien and dk.MaLopHocPhan = v.MaLopHocPhan
    where bh.TongSoBuoiHoc > 0;
end;
go

create or alter procedure sp_BaoCao_LichSuChinhSua
as
begin
    set nocount on;

    select 
        ls.ThoiGian,
        nd.HoTen as NguoiThucHien,
        ls.HanhDong,
        ls.DoiTuong,
        ls.GhiChu
    from LichSuChinhSua as ls
    left join NguoiDung as nd on ls.MaNguoiDung = nd.MaNguoiDung
    order by ls.ThoiGian desc;
end;
go

create or alter procedure sp_BaoCao_SoSanhTyLeChuyenCanKhoa
as
begin
    set nocount on;

    with TongSoBuoiDaHoc_CTE as (
        select 
            k.MaKhoa,
            count(distinct bh.MaBuoiHoc) as TongSoBuoiHoc
        from Khoa as k
        left join GiangVien as gv on k.MaKhoa = gv.MaKhoa
        left join LopHocPhan as lhp on gv.MaGiangVien = lhp.MaGiangVien
        left join BuoiHoc as bh on lhp.MaLopHocPhan = bh.MaLopHocPhan and bh.TrangThai != N'Chưa diễn ra'
        group by k.MaKhoa
    ),
    TongLuotDiemDanh_CTE as (
        select 
            k.MaKhoa,
            count(ldd.MaLuotDiemDanh) as TongLuotDiemDanh,
            count(case when ldd.TrangThaiDiemDanh = N'Có mặt' then 1 end) as TongLuotCoMat
        from Khoa as k
        left join GiangVien as gv on k.MaKhoa = gv.MaKhoa
        left join LopHocPhan as lhp on gv.MaGiangVien = lhp.MaGiangVien
        left join BuoiHoc as bh on lhp.MaLopHocPhan = bh.MaLopHocPhan
        left join PhienDiemDanh as pd on bh.MaBuoiHoc = pd.MaBuoiHoc
        left join LuotDiemDanh as ldd on pd.MaPhienDiemDanh = ldd.MaPhienDiemDanh
        group by k.MaKhoa
    ),
    SoLopHocPhan_CTE as (
        select 
            k.MaKhoa,
            count(distinct lhp.MaLopHocPhan) as SoLopHocPhan
        from Khoa as k
        left join GiangVien as gv on k.MaKhoa = gv.MaKhoa
        left join LopHocPhan as lhp on gv.MaGiangVien = lhp.MaGiangVien
        group by k.MaKhoa
    )
    select 
        k.MaKhoa,
        k.TenKhoa,
        ISNULL(slhp.SoLopHocPhan, 0) as SoLopHocPhan,
        ISNULL(bh.TongSoBuoiHoc, 0) as TongSoBuoiHoc,
        ISNULL(ldd.TongLuotDiemDanh, 0) as TongLuotDiemDanh,
        ISNULL(ldd.TongLuotCoMat, 0) as TongLuotCoMat,
        CASE 
            WHEN ISNULL(ldd.TongLuotDiemDanh, 0) = 0 THEN 0
            ELSE (CAST(ISNULL(ldd.TongLuotCoMat, 0) AS FLOAT) * 100.0) / ISNULL(ldd.TongLuotDiemDanh, 0)
        END as TyLeChuyenCan
    from Khoa as k
    left join TongSoBuoiDaHoc_CTE as bh on k.MaKhoa = bh.MaKhoa
    left join TongLuotDiemDanh_CTE as ldd on k.MaKhoa = ldd.MaKhoa
    left join SoLopHocPhan_CTE as slhp on k.MaKhoa = slhp.MaKhoa
    order by k.TenKhoa;
end;
go

create or alter procedure sp_LayThongKeTongQuan
as
begin
    set nocount on;

    declare @tong_sinh_vien int;
    declare @tong_giang_vien int;
    declare @tong_lop_hoc_phan int;
    declare @buoi_hoc_sap_toi int;

    select @tong_sinh_vien = COUNT(*) from SinhVien;
    select @tong_giang_vien = COUNT(*) from GiangVien;
    select @tong_lop_hoc_phan = COUNT(*) from LopHocPhan;
    select @buoi_hoc_sap_toi = COUNT(*) from BuoiHoc where NgayHoc >= CAST(GETDATE() AS DATE);

    select
        @tong_sinh_vien as tong_sinh_vien,
        @tong_giang_vien as tong_giang_vien,
        @tong_lop_hoc_phan as tong_lop_hoc_phan,
        @buoi_hoc_sap_toi as buoi_hoc_sap_toi;
end;
GO
