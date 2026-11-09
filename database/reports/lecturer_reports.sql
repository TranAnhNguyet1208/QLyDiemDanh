create or alter procedure sp_BaoCaoGV_ChuyenCanTungSV
    @MaLopHocPhan varchar(10)
as
begin
    set nocount on;

    with TongBuoiHoc as (
        select 
            count(distinct bh.MaBuoiHoc) as TongSoBuoi
        from BuoiHoc as bh
        where bh.MaLopHocPhan = @MaLopHocPhan
          and bh.TrangThai != N'Chưa diễn ra'
    ),
    DiemDanhSV as (
        select 
            sv.MaSinhVien,
            nd.HoTen,
            count(case when ldd.TrangThaiDiemDanh = N'Có mặt' then 1 end) as SoBuoiCoMat,
            count(case when ldd.TrangThaiDiemDanh in (N'Vắng có phép', N'Vắng không phép') then 1 end) as SoBuoiVang
        from DangKyLopHocPhan as dk
        join SinhVien as sv on dk.MaSinhVien = sv.MaSinhVien
        join NguoiDung as nd on sv.MaNguoiDung = nd.MaNguoiDung
        left join PhienDiemDanh as pd on pd.MaBuoiHoc in (
            select MaBuoiHoc from BuoiHoc where MaLopHocPhan = @MaLopHocPhan
        )
        left join LuotDiemDanh as ldd on pd.MaPhienDiemDanh = ldd.MaPhienDiemDanh and ldd.MaSinhVien = sv.MaSinhVien
        where dk.MaLopHocPhan = @MaLopHocPhan
        group by sv.MaSinhVien, nd.HoTen
    )
    select 
        ddsv.MaSinhVien,
        ddsv.HoTen,
        tb.TongSoBuoi as TongBuoiHoc,
        ddsv.SoBuoiCoMat,
        ddsv.SoBuoiVang,
        case 
            when tb.TongSoBuoi > 0 then (cast(ddsv.SoBuoiCoMat as float) * 100.0 / tb.TongSoBuoi)
            else 0 
        end as TyLeChuyenCan
    from DiemDanhSV as ddsv
    cross join TongBuoiHoc as tb
    order by TyLeChuyenCan desc;
end;
go

create or alter procedure sp_BaoCaoGV_DanhSachDiemDanhBuoiHoc
    @MaLopHocPhan varchar(10)
as
begin
    set nocount on;

    select 
        bh.MaBuoiHoc,
        bh.NgayHoc,
        bh.PhongHoc,
        sv.MaSinhVien,
        nd.HoTen,
        isnull(ldd.TrangThaiDiemDanh, N'Chưa điểm danh') as TrangThaiDiemDanh,
        ldd.ThoiGianDiemDanh,
        ldd.PhuongThuc
    from BuoiHoc as bh
    cross join DangKyLopHocPhan as dk
    join SinhVien as sv on dk.MaSinhVien = sv.MaSinhVien
    join NguoiDung as nd on sv.MaNguoiDung = nd.MaNguoiDung
    left join PhienDiemDanh as pd on pd.MaBuoiHoc = bh.MaBuoiHoc
    left join LuotDiemDanh as ldd on ldd.MaPhienDiemDanh = pd.MaPhienDiemDanh and ldd.MaSinhVien = sv.MaSinhVien
    where bh.MaLopHocPhan = @MaLopHocPhan
      and dk.MaLopHocPhan = @MaLopHocPhan
    order by bh.MaBuoiHoc, sv.MaSinhVien;
end;
go

create or alter procedure sp_LayTenMonHocLHP
    @MaLopHocPhan varchar(10)
as
begin
    set nocount on;
    
    select mh.TenMonHoc 
    from LopHocPhan as lhp
    join MonHoc as mh on lhp.MaMonHoc = mh.MaMonHoc
    where lhp.MaLopHocPhan = @MaLopHocPhan;
end;
go

create or alter procedure sp_BaoCaoGV_XuHuongChuyenCan
    @MaLopHocPhan varchar(10)
as
begin
    set nocount on;

    with BuoiHocTheoThoiGian as (
        select 
            bh.MaBuoiHoc,
            bh.NgayHoc,
            datepart(week, bh.NgayHoc) as Tuan,
            datepart(month, bh.NgayHoc) as Thang,
            datepart(year, bh.NgayHoc) as Nam
        from BuoiHoc as bh
        where bh.MaLopHocPhan = @MaLopHocPhan
          and bh.TrangThai != N'Chưa diễn ra'
    ),
    ThongKeTheoTuanThang as (
        select 
            bhtt.Tuan,
            bhtt.Thang,
            count(distinct bhtt.MaBuoiHoc) as TongBuoiHoc,
            count(ldd.MaLuotDiemDanh) as TongLuotDiemDanh,
            count(case when ldd.TrangThaiDiemDanh = N'Có mặt' then 1 end) as TongLuotCoMat
        from BuoiHocTheoThoiGian as bhtt
        left join PhienDiemDanh as pd on bhtt.MaBuoiHoc = pd.MaBuoiHoc
        left join LuotDiemDanh as ldd on pd.MaPhienDiemDanh = ldd.MaPhienDiemDanh
        group by bhtt.Tuan, bhtt.Thang, bhtt.Nam
    )
    select 
        Tuan,
        Thang,
        TongBuoiHoc,
        TongLuotDiemDanh,
        TongLuotCoMat,
        case 
            when TongLuotDiemDanh > 0 then (cast(TongLuotCoMat as float) * 100.0 / TongLuotDiemDanh)
            else 0 
        end as TyLeChuyenCan
    from ThongKeTheoTuanThang
    order by Thang, Tuan;
end;
go

create or alter procedure sp_BaoCaoGV_SinhVienDacBiet
    @MaLopHocPhan varchar(10),
    @Loai varchar(10) = 'cao'  -- 'cao' hoặc 'thap'
as
begin
    set nocount on;

    with ThongKeSV as (
        select 
            sv.MaSinhVien,
            nd.HoTen,
            count(distinct bh.MaBuoiHoc) as TongBuoiHoc,
            count(case when ldd.TrangThaiDiemDanh = N'Có mặt' then 1 end) as SoBuoiCoMat,
            count(case when ldd.TrangThaiDiemDanh in (N'Vắng có phép', N'Vắng không phép') then 1 end) as SoBuoiVang,
            case 
                when count(distinct bh.MaBuoiHoc) > 0 then 
                    (cast(count(case when ldd.TrangThaiDiemDanh = N'Có mặt' then 1 end) as float) * 100.0 / count(distinct bh.MaBuoiHoc))
                else 0 
            end as TyLeChuyenCan,
            row_number() over (order by 
                case 
                    when count(distinct bh.MaBuoiHoc) > 0 then 
                        (cast(count(case when ldd.TrangThaiDiemDanh = N'Có mặt' then 1 end) as float) * 100.0 / count(distinct bh.MaBuoiHoc))
                    else 0 
                end desc
            ) as XepHang
        from DangKyLopHocPhan as dk
        join SinhVien as sv on dk.MaSinhVien = sv.MaSinhVien
        join NguoiDung as nd on sv.MaNguoiDung = nd.MaNguoiDung
        left join BuoiHoc as bh on dk.MaLopHocPhan = bh.MaLopHocPhan and bh.TrangThai != N'Chưa diễn ra'
        left join PhienDiemDanh as pd on pd.MaBuoiHoc = bh.MaBuoiHoc
        left join LuotDiemDanh as ldd on pd.MaPhienDiemDanh = ldd.MaPhienDiemDanh and ldd.MaSinhVien = sv.MaSinhVien
        where dk.MaLopHocPhan = @MaLopHocPhan
        group by sv.MaSinhVien, nd.HoTen
    )
    select top 10
        MaSinhVien,
        HoTen,
        TongBuoiHoc,
        SoBuoiCoMat,
        SoBuoiVang,
        TyLeChuyenCan,
        XepHang
    from ThongKeSV
    where (@Loai = 'cao' and XepHang <= 10)  -- Top 10 cao nhất
       or (@Loai = 'thap' and XepHang > (select count(*) from ThongKeSV) - 10)  -- Top 10 thấp nhất
    order by 
        case when @Loai = 'cao' then TyLeChuyenCan end desc,
        case when @Loai = 'thap' then TyLeChuyenCan end asc;
end;
go

create or alter procedure sp_BaoCaoGV_TongHopChuyenCan
    @MaGiangVien varchar(10)
as
begin
    set nocount on;

    with ThongKeLHP as (
        select 
            lhp.MaLopHocPhan,
            mh.TenMonHoc,
            lhp.HocKy,
            lhp.NamHoc,
            count(distinct dk.MaSinhVien) as TongSinhVien,
            count(distinct bh.MaBuoiHoc) as TongBuoiHoc,
            count(ldd.MaLuotDiemDanh) as TongLuotDiemDanh,
            count(case when ldd.TrangThaiDiemDanh = N'Có mặt' then 1 end) as TongLuotCoMat
        from LopHocPhan as lhp
        join MonHoc as mh on lhp.MaMonHoc = mh.MaMonHoc
        left join DangKyLopHocPhan as dk on lhp.MaLopHocPhan = dk.MaLopHocPhan
        left join BuoiHoc as bh on lhp.MaLopHocPhan = bh.MaLopHocPhan and bh.TrangThai != N'Chưa diễn ra'
        left join PhienDiemDanh as pd on bh.MaBuoiHoc = pd.MaBuoiHoc
        left join LuotDiemDanh as ldd on pd.MaPhienDiemDanh = ldd.MaPhienDiemDanh
        where lhp.MaGiangVien = @MaGiangVien
        group by lhp.MaLopHocPhan, mh.TenMonHoc, lhp.HocKy, lhp.NamHoc
    )
    select 
        MaLopHocPhan,
        TenMonHoc,
        HocKy,
        NamHoc,
        TongSinhVien,
        TongBuoiHoc,
        TongLuotDiemDanh,
        TongLuotCoMat,
        case 
            when TongLuotDiemDanh > 0 then (cast(TongLuotCoMat as float) * 100.0 / TongLuotDiemDanh)
            else 0 
        end as TyLeChuyenCan
    from ThongKeLHP
    order by NamHoc desc, HocKy desc, TenMonHoc;
end;
go

create or alter procedure sp_BaoCaoGV_CanhBaoCamThi
    @MaLopHocPhan varchar(10)
as
begin
    set nocount on;

    with ThongKeVang as (
        select 
            sv.MaSinhVien,
            nd.HoTen,
            count(distinct bh.MaBuoiHoc) as TongBuoiHoc,
            count(case when ldd.TrangThaiDiemDanh in (N'Vắng có phép', N'Vắng không phép') then 1 end) as SoBuoiVang,
            case 
                when count(distinct bh.MaBuoiHoc) > 0 then 
                    (cast(count(case when ldd.TrangThaiDiemDanh in (N'Vắng có phép', N'Vắng không phép') then 1 end) as float) * 100.0 / count(distinct bh.MaBuoiHoc))
                else 0 
            end as TyLeVang
        from DangKyLopHocPhan as dk
        join SinhVien as sv on dk.MaSinhVien = sv.MaSinhVien
        join NguoiDung as nd on sv.MaNguoiDung = nd.MaNguoiDung
        left join BuoiHoc as bh on dk.MaLopHocPhan = bh.MaLopHocPhan and bh.TrangThai != N'Chưa diễn ra'
        left join PhienDiemDanh as pd on pd.MaBuoiHoc = bh.MaBuoiHoc
        left join LuotDiemDanh as ldd on pd.MaPhienDiemDanh = ldd.MaPhienDiemDanh and ldd.MaSinhVien = sv.MaSinhVien
        where dk.MaLopHocPhan = @MaLopHocPhan
        group by sv.MaSinhVien, nd.HoTen
    )
    select 
        MaSinhVien,
        HoTen,
        TongBuoiHoc,
        SoBuoiVang,
        TyLeVang,
        case 
            when TyLeVang > 20 then N'NGUY CƠ CẤM THI'
            else N'Trong giới hạn'
        end as MucDoCanhBao
    from ThongKeVang
    where TyLeVang > 20  -- Trên 20% là có nguy cơ cấm thi
    order by TyLeVang desc;
end;
go

use qlsv;
go

-- 1. Procedure lấy Tên môn học từ Mã lớp học phần
-- (Dùng cho chức năng Export báo cáo sinh viên, điểm danh...)
create or alter procedure sp_LayTenMonHocLHP
    @MaLopHocPhan varchar(10)
as
begin
    set nocount on;
    
    select mh.TenMonHoc 
    from LopHocPhan as lhp
    join MonHoc as mh on lhp.MaMonHoc = mh.MaMonHoc
    where lhp.MaLopHocPhan = @MaLopHocPhan;
end;
go

-- 2. Procedure lấy Tên giảng viên từ Mã giảng viên
-- (Dùng cho chức năng Export báo cáo tổng hợp)
create or alter procedure sp_LayTenGiangVien
    @MaGiangVien varchar(10)
as
begin
    set nocount on;

    select nd.HoTen
    from GiangVien as gv
    join NguoiDung as nd on gv.MaNguoiDung = nd.MaNguoiDung
    where gv.MaGiangVien = @MaGiangVien;
end;
go

use qlsv;
go

create or alter procedure sp_LayLichDayGiangVien
    @MaGiangVien varchar(10),
    @TuNgay date = null, -- Có thể NULL
    @DenNgay date = null -- Có thể NULL
as
begin
    select 
        bh.MaBuoiHoc,
        lhp.MaLopHocPhan,
        mh.TenMonHoc,
        bh.NgayHoc,
        bh.PhongHoc,
        bh.ThoiGianBatDau,
        bh.ThoiGianKetThuc,
        bh.TrangThai,
        bh.GhiChuBuoiHoc
    from BuoiHoc bh
    join LopHocPhan lhp on bh.MaLopHocPhan = lhp.MaLopHocPhan
    join MonHoc mh on lhp.MaMonHoc = mh.MaMonHoc
    where lhp.MaGiangVien = @MaGiangVien
    -- Logic lọc ngày: Nếu tham số NULL thì bỏ qua điều kiện đó
    and (@TuNgay is null or bh.NgayHoc >= @TuNgay)
    and (@DenNgay is null or bh.NgayHoc <= @DenNgay)
    order by bh.NgayHoc desc, bh.ThoiGianBatDau asc;
end;
go