create or alter procedure sp_BaoCaoSV_LichSuDiemDanh
    @MaSinhVien varchar(10)
as
begin
    set nocount on;

    select 
        bh.MaBuoiHoc,
        mh.TenMonHoc,
        lhp.MaLopHocPhan,
        bh.NgayHoc,
        isnull(ldd.TrangThaiDiemDanh, N'Chưa điểm danh') as TrangThaiDiemDanh,
        ldd.ThoiGianDiemDanh,
        ldd.PhuongThuc
    from DangKyLopHocPhan as dk
    join LopHocPhan as lhp on dk.MaLopHocPhan = lhp.MaLopHocPhan
    join MonHoc as mh on lhp.MaMonHoc = mh.MaMonHoc
    join BuoiHoc as bh on lhp.MaLopHocPhan = bh.MaLopHocPhan
    left join PhienDiemDanh as pd on bh.MaBuoiHoc = pd.MaBuoiHoc
    left join LuotDiemDanh as ldd on pd.MaPhienDiemDanh = ldd.MaPhienDiemDanh and ldd.MaSinhVien = @MaSinhVien
    where dk.MaSinhVien = @MaSinhVien
      and bh.TrangThai != N'Chưa diễn ra'
    order by bh.NgayHoc desc, bh.MaBuoiHoc desc;
end;
go

create or alter procedure sp_BaoCaoSV_ThongKeChuyenCan
    @MaSinhVien varchar(10)
as
begin
    set nocount on;

    with ThongKeMonHoc as (
        select 
            lhp.MaLopHocPhan,
            mh.TenMonHoc,
            lhp.HocKy,
            lhp.NamHoc,
            count(distinct bh.MaBuoiHoc) as TongBuoiHoc,
            count(case when ldd.TrangThaiDiemDanh = N'Có mặt' then 1 end) as SoBuoiCoMat,
            count(case when ldd.TrangThaiDiemDanh in (N'Vắng có phép', N'Vắng không phép') then 1 end) as SoBuoiVang,
            case 
                when count(distinct bh.MaBuoiHoc) > 0 then 
                    (cast(count(case when ldd.TrangThaiDiemDanh = N'Có mặt' then 1 end) as float) * 100.0 / count(distinct bh.MaBuoiHoc))
                else 0 
            end as TyLeChuyenCan
        from DangKyLopHocPhan as dk
        join LopHocPhan as lhp on dk.MaLopHocPhan = lhp.MaLopHocPhan
        join MonHoc as mh on lhp.MaMonHoc = mh.MaMonHoc
        left join BuoiHoc as bh on lhp.MaLopHocPhan = bh.MaLopHocPhan and bh.TrangThai != N'Chưa diễn ra'
        left join PhienDiemDanh as pd on bh.MaBuoiHoc = pd.MaBuoiHoc
        left join LuotDiemDanh as ldd on pd.MaPhienDiemDanh = ldd.MaPhienDiemDanh and ldd.MaSinhVien = @MaSinhVien
        where dk.MaSinhVien = @MaSinhVien
        group by lhp.MaLopHocPhan, mh.TenMonHoc, lhp.HocKy, lhp.NamHoc
    )
    select 
        MaLopHocPhan,
        TenMonHoc,
        HocKy,
        NamHoc,
        TongBuoiHoc,
        SoBuoiCoMat,
        SoBuoiVang,
        TyLeChuyenCan
    from ThongKeMonHoc
    order by NamHoc desc, HocKy desc, TenMonHoc;
end;
go

create or alter procedure sp_LayThongTinSinhVien
    @MaSinhVien varchar(10)
as
begin
    set nocount on;
    
    select nd.HoTen 
    from NguoiDung as nd
    join SinhVien as sv on nd.MaNguoiDung = sv.MaNguoiDung
    where sv.MaSinhVien = @MaSinhVien;
end;
go

create or alter procedure sp_BaoCaoSV_CanhBaoChuyenCan
    @MaSinhVien varchar(10)
as
begin
    set nocount on;

    with ThongKe as (
        select 
            lhp.MaLopHocPhan,
            mh.TenMonHoc,
            count(distinct bh.MaBuoiHoc) as TongBuoiHoc,
            count(case when ldd.TrangThaiDiemDanh = N'Có mặt' then 1 end) as SoBuoiCoMat,
            count(case when ldd.TrangThaiDiemDanh = N'Vắng có phép' then 1 end) as SoBuoiVangCP,
            count(case when ldd.TrangThaiDiemDanh = N'Vắng không phép' then 1 end) as SoBuoiVangKP,
            count(case when ldd.TrangThaiDiemDanh in (N'Vắng có phép', N'Vắng không phép') then 1 end) as SoBuoiVangTong,
            case 
                when count(distinct bh.MaBuoiHoc) > 0 then 
                    (cast(count(case when ldd.TrangThaiDiemDanh = N'Có mặt' then 1 end) as float) * 100.0 / count(distinct bh.MaBuoiHoc))
                else 0 
            end as TyLeChuyenCan,
            case 
                when count(distinct bh.MaBuoiHoc) > 0 then 
                    (cast(count(case when ldd.TrangThaiDiemDanh in (N'Vắng có phép', N'Vắng không phép') then 1 end) as float) * 100.0 / count(distinct bh.MaBuoiHoc))
                else 0 
            end as TyLeVangTong,
            case 
                when count(distinct bh.MaBuoiHoc) > 0 then 
                    (cast(count(case when ldd.TrangThaiDiemDanh = N'Vắng không phép' then 1 end) as float) * 100.0 / count(distinct bh.MaBuoiHoc))
                else 0 
            end as TyLeVangKhongPhep
        from DangKyLopHocPhan as dk
        join LopHocPhan as lhp on dk.MaLopHocPhan = lhp.MaLopHocPhan
        join MonHoc as mh on lhp.MaMonHoc = mh.MaMonHoc
        left join BuoiHoc as bh on lhp.MaLopHocPhan = bh.MaLopHocPhan and bh.TrangThai != N'Chưa diễn ra'
        left join PhienDiemDanh as pd on bh.MaBuoiHoc = pd.MaBuoiHoc
        left join LuotDiemDanh as ldd on pd.MaPhienDiemDanh = ldd.MaPhienDiemDanh and ldd.MaSinhVien = @MaSinhVien
        where dk.MaSinhVien = @MaSinhVien
        group by lhp.MaLopHocPhan, mh.TenMonHoc
        having count(distinct bh.MaBuoiHoc) > 0
    )
    select 
        MaLopHocPhan,
        TenMonHoc,
        TongBuoiHoc,
        SoBuoiCoMat,
        SoBuoiVangCP,
        SoBuoiVangKP,
        SoBuoiVangTong,
        TyLeChuyenCan,
        TyLeVangTong,
        TyLeVangKhongPhep,
        case 
            when TyLeVangKhongPhep > 20.0 then N'Tỉ lệ vắng không phép lớp ' + TenMonHoc + N' đã vượt 20%. Nguy cơ cao bị cấm thi.'
            when TyLeVangKhongPhep >= 15.0 then N'Tỉ lệ vắng không phép lớp ' + TenMonHoc + N' từ 15-20%. Cảnh báo! Tỉ lệ vắng sắp vượt mức cho phép'
            when TyLeVangTong >= 30.0 then N'Tỉ lệ vắng lớp ' + TenMonHoc + N' đã vượt 30%. Nguy cơ cao bị cấm thi.'
            when TyLeVangTong >= 20.0 then N'Tỉ lệ vắng lớp ' + TenMonHoc + N' từ 20-30%. Cảnh báo! Tỉ lệ vắng sắp vượt mức cho phép'
        end as ThongBao,
        case 
            when TyLeVangKhongPhep > 20.0 then 3  -- Đỏ: vắng KP > 20%
            when TyLeVangKhongPhep >= 15.0 then 2  -- Vàng: vắng KP 15-20%
            when TyLeVangTong >= 30.0 then 3  -- Đỏ: tổng vắng >= 30%
            when TyLeVangTong >= 20.0 then 2  -- Vàng: tổng vắng 20-30%
        end as MucDoCanhBao
    from ThongKe
    where TyLeVangKhongPhep >= 15.0 or TyLeVangTong >= 20.0
    order by MucDoCanhBao desc, TyLeVangKhongPhep desc, TyLeVangTong desc;
end;
go

create or alter procedure sp_BaoCaoSV_TrangThaiCanhBaoTong
    @MaSinhVien varchar(10)
as
begin
    set nocount on;

    with ThongKe as (
        select 
            lhp.MaLopHocPhan,
            mh.TenMonHoc,
            count(distinct bh.MaBuoiHoc) as TongBuoiHoc,
            count(case when ldd.TrangThaiDiemDanh in (N'Vắng có phép', N'Vắng không phép') then 1 end) as SoBuoiVangTong,
            count(case when ldd.TrangThaiDiemDanh = N'Vắng không phép' then 1 end) as SoBuoiVangKP,
            case 
                when count(distinct bh.MaBuoiHoc) > 0 then 
                    (cast(count(case when ldd.TrangThaiDiemDanh in (N'Vắng có phép', N'Vắng không phép') then 1 end) as float) * 100.0 / count(distinct bh.MaBuoiHoc))
                else 0 
            end as TyLeVangTong,
            case 
                when count(distinct bh.MaBuoiHoc) > 0 then 
                    (cast(count(case when ldd.TrangThaiDiemDanh = N'Vắng không phép' then 1 end) as float) * 100.0 / count(distinct bh.MaBuoiHoc))
                else 0 
            end as TyLeVangKP,
            case 
                when count(distinct bh.MaBuoiHoc) > 0 and (cast(count(case when ldd.TrangThaiDiemDanh = N'Vắng không phép' then 1 end) as float) * 100.0 / count(distinct bh.MaBuoiHoc)) > 20.0 then 3
                when count(distinct bh.MaBuoiHoc) > 0 and (cast(count(case when ldd.TrangThaiDiemDanh = N'Vắng không phép' then 1 end) as float) * 100.0 / count(distinct bh.MaBuoiHoc)) >= 15.0 then 2
                when count(distinct bh.MaBuoiHoc) > 0 and (cast(count(case when ldd.TrangThaiDiemDanh in (N'Vắng có phép', N'Vắng không phép') then 1 end) as float) * 100.0 / count(distinct bh.MaBuoiHoc)) >= 30.0 then 3
                when count(distinct bh.MaBuoiHoc) > 0 and (cast(count(case when ldd.TrangThaiDiemDanh in (N'Vắng có phép', N'Vắng không phép') then 1 end) as float) * 100.0 / count(distinct bh.MaBuoiHoc)) >= 20.0 then 2
                else 0
            end as MucDoCanhBao
        from DangKyLopHocPhan as dk
        join LopHocPhan as lhp on dk.MaLopHocPhan = lhp.MaLopHocPhan
        join MonHoc as mh on lhp.MaMonHoc = mh.MaMonHoc
        left join BuoiHoc as bh on lhp.MaLopHocPhan = bh.MaLopHocPhan and bh.TrangThai != N'Chưa diễn ra'
        left join PhienDiemDanh as pd on bh.MaBuoiHoc = pd.MaBuoiHoc
        left join LuotDiemDanh as ldd on pd.MaPhienDiemDanh = ldd.MaPhienDiemDanh and ldd.MaSinhVien = @MaSinhVien
        where dk.MaSinhVien = @MaSinhVien
        group by lhp.MaLopHocPhan, mh.TenMonHoc
        having count(distinct bh.MaBuoiHoc) > 0
    )
    select 
        (select max(MucDoCanhBao) from ThongKe where MucDoCanhBao > 0) as MucDoCanhBaoTong,
        (select count(*) from ThongKe where MucDoCanhBao > 0) as SoLopCanhBao,
        (select count(*) from ThongKe where MucDoCanhBao = 3) as SoLopDo,
        (select count(*) from ThongKe where MucDoCanhBao = 2) as SoLopVang,
        (select STRING_AGG(TenMonHoc, ', ') from ThongKe where MucDoCanhBao > 0) as DanhSachLopCanhBao
end;
go

