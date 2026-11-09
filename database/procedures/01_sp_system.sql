-- Procedure ghi log hệ thống
CREATE OR ALTER PROCEDURE sp_GhiLog
    @MaDinhDanh VARCHAR(20), -- MaGV, MaSV, or MaNguoiDung
    @HanhDong NVARCHAR(100),
    @DoiTuong NVARCHAR(100),
    @GhiChu NVARCHAR(MAX)
AS
BEGIN
    SET NOCOUNT ON;
    
    DECLARE @MaNguoiDung VARCHAR(10);

    -- Try to find MaNguoiDung from GiangVien
    SELECT @MaNguoiDung = MaNguoiDung FROM GiangVien WHERE MaGiangVien = @MaDinhDanh;
    
    -- If not found, try SinhVien
    IF @MaNguoiDung IS NULL
        SELECT @MaNguoiDung = MaNguoiDung FROM SinhVien WHERE MaSinhVien = @MaDinhDanh;

    -- If still not found, assume it is MaNguoiDung
    IF @MaNguoiDung IS NULL
        SELECT @MaNguoiDung = MaNguoiDung FROM NguoiDung WHERE MaNguoiDung = @MaDinhDanh;

    IF @MaNguoiDung IS NOT NULL
    BEGIN
        INSERT INTO LichSuChinhSua (MaNguoiDung, HanhDong, DoiTuong, ThoiGian, GhiChu)
        VALUES (@MaNguoiDung, @HanhDong, @DoiTuong, GETDATE(), @GhiChu);
    END
END;
GO
