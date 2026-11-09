use qlsv;
go

create or alter procedure sp_LayDuLieuKhuonMat
    @MaSinhVien VARCHAR(10)
as
begin
    set nocount on;
    select DuLieuKhuonMat from SinhVien where MaSinhVien = @MaSinhVien;
end;
go

create or alter procedure sp_CapNhatDuLieuKhuonMat
    @MaSinhVien VARCHAR(10),
    @DuLieuKhuonMat VARBINARY(MAX)
as
begin
    set nocount on;
    update SinhVien
    set DuLieuKhuonMat = @DuLieuKhuonMat
    where MaSinhVien = @MaSinhVien;
end;
go