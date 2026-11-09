create or alter procedure sp_LayLopHocCuaGiangVien
    @MaGiangVien VARCHAR(10)
as
begin
    set nocount on;

    select 
        lhp.MaLopHocPhan,
        mh.TenMonHoc,
        lhp.HocKy,
        lhp.NamHoc
    from LopHocPhan as lhp
    join MonHoc as mh on lhp.MaMonHoc = mh.MaMonHoc
    where lhp.MaGiangVien = @MaGiangVien;
end;
GO

