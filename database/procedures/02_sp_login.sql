use qlsv;
go

create or alter procedure sp_CheckLogin
    @InputIdentifier varchar(100), -- Có thể là MaNguoiDung, Email, MaSinhVien, hoặc MaGiangVien
    @MatKhau varchar(255)
as
begin
    set nocount on;

    select 
        case 
            when nd.VaiTro = 'giangvien' then isnull(gv.MaGiangVien, nd.MaNguoiDung)
            when nd.VaiTro = 'sinhvien' then isnull(sv.MaSinhVien, nd.MaNguoiDung)
            else nd.MaNguoiDung 
        end as MaDinhDanh, 

        nd.HoTen, 
        nd.VaiTro
    from NguoiDung as nd
    left join SinhVien as sv on nd.MaNguoiDung = sv.MaNguoiDung
    left join GiangVien as gv on nd.MaNguoiDung = gv.MaNguoiDung
    where 
        nd.MatKhau = @MatKhau
        and nd.TrangThai = N'Hoạt động'
        and (
            nd.MaNguoiDung = @InputIdentifier 
            or nd.Email = @InputIdentifier
            or sv.MaSinhVien = @InputIdentifier
            or gv.MaGiangVien = @InputIdentifier
        );
end;
go


