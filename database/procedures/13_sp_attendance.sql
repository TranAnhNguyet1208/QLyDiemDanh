use qlsv;
go

-- 1. GV tạo phiên "Mã Nhập Tay" (ví dụ: "LOP123")
create or alter procedure sp_TaoPhienDiemDanh_MaCode
    @MaBuoiHoc INT,
    @MaCode VARCHAR(20)
as
begin
    set nocount on;
    declare @MaPhienDiemDanh INT;
    declare @ThoiGianKetThucPhien DATETIME;

    BEGIN
        declare @NgayHoc DATE;
        declare @ThoiGianKetThuc TIME;

        select @NgayHoc = NgayHoc, @ThoiGianKetThuc = ThoiGianKetThuc
        from BuoiHoc 
        where MaBuoiHoc = @MaBuoiHoc;

        if @NgayHoc is null or @ThoiGianKetThuc is null
        begin
            raiserror (N'Buổi học này chưa được Admin thiết lập Ngày hoặc Giờ kết thúc.', 16, 1);
            return;
        end

        -- Cập nhật trạng thái mới nhất
        exec sp_CapNhatTrangThaiBuoiHocTuDong;

        if not exists (select 1 from BuoiHoc where MaBuoiHoc = @MaBuoiHoc and TrangThai = N'Đang diễn ra')
        begin
            raiserror (N'Chỉ có thể tạo phiên điểm danh cho buổi học đang diễn ra.', 16, 1);
            return;
        end
        
        set @ThoiGianKetThucPhien = DATETIMEFROMPARTS(
            YEAR(@NgayHoc), MONTH(@NgayHoc), DAY(@NgayHoc), 
            DATEPART(hour, @ThoiGianKetThuc), DATEPART(minute, @ThoiGianKetThuc), 0, 0
        );
    END

    if exists (select 1 from PhienDiemDanh where MaCode = @MaCode and GETDATE() between ThoiGianBatDauPhien and ThoiGianKetThucPhien)
    begin
        raiserror (N'Mã code này đã tồn tại và đang hoạt động.', 16, 1);
        return;
    end

    insert into PhienDiemDanh (MaBuoiHoc, ThoiGianBatDauPhien, ThoiGianKetThucPhien, MaCode)
    values (@MaBuoiHoc, GETDATE(), @ThoiGianKetThucPhien, @MaCode);

    set @MaPhienDiemDanh = SCOPE_IDENTITY();
    
    select @MaPhienDiemDanh as MaPhienDiemDanh, @MaCode as MaCode;
end;
GO

-- 2. GV tạo phiên "Quét QR" (Hệ thống tạo MaPhien, MaCode = NULL)
create or alter procedure sp_TaoPhienDiemDanh_QR
    @MaBuoiHoc INT
as
begin
    set nocount on;
    declare @MaPhienDiemDanh INT;
    declare @ThoiGianKetThucPhien DATETIME;

    BEGIN
        declare @NgayHoc DATE;
        declare @ThoiGianKetThuc TIME;

        select @NgayHoc = NgayHoc, @ThoiGianKetThuc = ThoiGianKetThuc
        from BuoiHoc 
        where MaBuoiHoc = @MaBuoiHoc;

        if @NgayHoc is null or @ThoiGianKetThuc is null
        begin
            raiserror (N'Buổi học này chưa được Admin thiết lập Ngày hoặc Giờ kết thúc.', 16, 1);
            return;
        end

        -- Cập nhật trạng thái mới nhất
        exec sp_CapNhatTrangThaiBuoiHocTuDong;

        if not exists (select 1 from BuoiHoc where MaBuoiHoc = @MaBuoiHoc and TrangThai = N'Đang diễn ra')
        begin
            raiserror (N'Chỉ có thể tạo phiên điểm danh cho buổi học đang diễn ra.', 16, 1);
            return;
        end
        
        set @ThoiGianKetThucPhien = DATETIMEFROMPARTS(
            YEAR(@NgayHoc), MONTH(@NgayHoc), DAY(@NgayHoc), 
            DATEPART(hour, @ThoiGianKetThuc), DATEPART(minute, @ThoiGianKetThuc), 0, 0
        );
    END

    insert into PhienDiemDanh (MaBuoiHoc, ThoiGianBatDauPhien, ThoiGianKetThucPhien, MaCode)
    values (@MaBuoiHoc, GETDATE(), @ThoiGianKetThucPhien, NULL);

    set @MaPhienDiemDanh = SCOPE_IDENTITY();
    
    select @MaPhienDiemDanh as MaPhienDiemDanh;
end;
GO

-- 3. GV "Tick" 3 trạng thái (Tự tạo/dùng chung phiên MaCode = NULL)
CREATE OR ALTER PROCEDURE sp_DiemDanh_ThuCong
    @MaBuoiHoc INT,
    @MaSinhVien VARCHAR(10),
    @TrangThai NVARCHAR(50),
    @GhiChu NVARCHAR(MAX) = NULL
AS
BEGIN
    SET NOCOUNT ON;
    DECLARE @MaPhienDiemDanh INT;
    DECLARE @ThoiGianKetThucPhien DATETIME;

    -- TÌM HOẶC TẠO PHIÊN ĐIỂM DANH
    SELECT @MaPhienDiemDanh = MaPhienDiemDanh
    FROM PhienDiemDanh
    WHERE MaBuoiHoc = @MaBuoiHoc 
      AND MaCode IS NULL 
      AND GETDATE() BETWEEN ThoiGianBatDauPhien AND ThoiGianKetThucPhien;

    IF @MaPhienDiemDanh IS NULL
    BEGIN
        -- KIỂM TRA BUỔI HỌC CÓ THỜI GIAN KẾT THÚC KHÔNG
        DECLARE @NgayHoc DATE;
        DECLARE @ThoiGianKetThuc TIME;

        SELECT @NgayHoc = NgayHoc, @ThoiGianKetThuc = ThoiGianKetThuc
        FROM BuoiHoc 
        WHERE MaBuoiHoc = @MaBuoiHoc;

        IF @NgayHoc IS NULL OR @ThoiGianKetThuc IS NULL
        BEGIN
            RAISERROR (N'Buổi học này chưa được thiết lập Ngày hoặc Giờ kết thúc.', 16, 1);
            RETURN;
        END

        -- Cập nhật trạng thái mới nhất
        EXEC sp_CapNhatTrangThaiBuoiHocTuDong;

        IF NOT EXISTS (SELECT 1 FROM BuoiHoc WHERE MaBuoiHoc = @MaBuoiHoc AND TrangThai = N'Đang diễn ra')
        BEGIN
            RAISERROR (N'Chỉ có thể điểm danh cho buổi học đang diễn ra.', 16, 1);
            RETURN;
        END
        
        SET @ThoiGianKetThucPhien = DATETIMEFROMPARTS(
            YEAR(@NgayHoc), MONTH(@NgayHoc), DAY(@NgayHoc), 
            DATEPART(HOUR, @ThoiGianKetThuc), DATEPART(MINUTE, @ThoiGianKetThuc), 0, 0
        );
        
        -- TẠO PHIÊN ĐIỂM DANH MỚI
        INSERT INTO PhienDiemDanh (MaBuoiHoc, ThoiGianBatDauPhien, ThoiGianKetThucPhien, MaCode)
        VALUES (@MaBuoiHoc, GETDATE(), @ThoiGianKetThucPhien, NULL);
        
        SET @MaPhienDiemDanh = SCOPE_IDENTITY();
    END

    -- XÓA ĐIỂM DANH CŨ NẾU CÓ
    DELETE FROM LuotDiemDanh 
    WHERE MaPhienDiemDanh = @MaPhienDiemDanh AND MaSinhVien = @MaSinhVien;

    -- THÊM ĐIỂM DANH MỚI
    INSERT INTO LuotDiemDanh (
        MaPhienDiemDanh, MaSinhVien, TrangThaiDiemDanh, 
        PhuongThuc, ThoiGianDiemDanh, GhiChuLyDoVang
    )
    VALUES (
        @MaPhienDiemDanh, @MaSinhVien, @TrangThai, 
        N'Thủ công (GV)', GETDATE(), @GhiChu
    );
    
    SELECT 1 AS SuccessStatus, N'Lưu điểm danh thủ công thành công' AS Message;
END;
GO

-- 4. GV quét camera (Tự tạo/dùng chung phiên MaCode = NULL)
CREATE OR ALTER PROCEDURE sp_DiemDanh_KhuonMat
    @MaBuoiHoc INT,
    @MaSinhVien VARCHAR(10)
AS
BEGIN
    SET NOCOUNT ON;
    DECLARE @MaPhienDiemDanh INT;
    DECLARE @ThoiGianKetThucPhien DATETIME;

    -- TÌM PHIÊN ĐANG HOẠT ĐỘNG
    SELECT @MaPhienDiemDanh = MaPhienDiemDanh
    FROM PhienDiemDanh
    WHERE MaBuoiHoc = @MaBuoiHoc 
      AND MaCode IS NULL 
      AND GETDATE() BETWEEN ThoiGianBatDauPhien AND ThoiGianKetThucPhien;

    -- NẾU KHÔNG TÌM THẤY PHIÊN HOẠT ĐỘNG
    IF @MaPhienDiemDanh IS NULL
    BEGIN
        -- KIỂM TRA BUỔI HỌC CÓ THỜI GIAN KẾT THÚC KHÔNG
        DECLARE @NgayHoc DATE;
        DECLARE @ThoiGianKetThuc TIME;

        SELECT @NgayHoc = NgayHoc, @ThoiGianKetThuc = ThoiGianKetThuc
        FROM BuoiHoc 
        WHERE MaBuoiHoc = @MaBuoiHoc;

        -- KIỂM TRA PHIÊN ĐÃ HẾT HẠN CHƯA
        IF EXISTS (
            SELECT 1 FROM PhienDiemDanh 
            WHERE MaBuoiHoc = @MaBuoiHoc 
              AND ThoiGianKetThucPhien < GETDATE()
        )
        BEGIN
            RAISERROR (N'Phiên điểm danh đã kết thúc.', 16, 1);
            RETURN;
        END

        -- TẠO PHIÊN MỚI NẾU CHƯA CÓ
        IF @NgayHoc IS NULL OR @ThoiGianKetThuc IS NULL
        BEGIN
            RAISERROR (N'Buổi học này chưa được thiết lập Ngày hoặc Giờ kết thúc.', 16, 1);
            RETURN;
        END

        -- Cập nhật trạng thái mới nhất
        EXEC sp_CapNhatTrangThaiBuoiHocTuDong;

        IF NOT EXISTS (SELECT 1 FROM BuoiHoc WHERE MaBuoiHoc = @MaBuoiHoc AND TrangThai = N'Đang diễn ra')
        BEGIN
            RAISERROR (N'Chỉ có thể điểm danh cho buổi học đang diễn ra.', 16, 1);
            RETURN;
        END
        
        SET @ThoiGianKetThucPhien = DATETIMEFROMPARTS(
            YEAR(@NgayHoc), MONTH(@NgayHoc), DAY(@NgayHoc), 
            DATEPART(HOUR, @ThoiGianKetThuc), DATEPART(MINUTE, @ThoiGianKetThuc), 0, 0
        );
        
        INSERT INTO PhienDiemDanh (MaBuoiHoc, ThoiGianBatDauPhien, ThoiGianKetThucPhien, MaCode)
        VALUES (@MaBuoiHoc, GETDATE(), @ThoiGianKetThucPhien, NULL);
        
        SET @MaPhienDiemDanh = SCOPE_IDENTITY();
    END

    -- KIỂM TRA ĐÃ ĐIỂM DANH CHƯA
    IF EXISTS (
        SELECT 1 
        FROM LuotDiemDanh 
        WHERE MaPhienDiemDanh = @MaPhienDiemDanh AND MaSinhVien = @MaSinhVien
    )
    BEGIN
        SELECT 2 AS SuccessStatus, N'Sinh viên đã điểm danh phiên này rồi.' AS Message;
        RETURN;
    END

    -- THÊM ĐIỂM DANH
    INSERT INTO LuotDiemDanh (MaPhienDiemDanh, MaSinhVien, TrangThaiDiemDanh, PhuongThuc, ThoiGianDiemDanh)
    VALUES (@MaPhienDiemDanh, @MaSinhVien, N'Có mặt', N'Khuôn mặt', GETDATE());

    SELECT 1 AS SuccessStatus, N'Điểm danh thành công.' AS Message;
END;
GO

---

--- 2. Hành động của Sinh viên (SV)

-- 5. SV nhập mã "LOP123" (Tìm theo MaCode)
CREATE OR ALTER PROCEDURE sp_LuotDiemDanh_MaCode
    @MaCode VARCHAR(20),
    @MaSinhVien VARCHAR(10),
    @DiaChiIP VARCHAR(45) = NULL
AS
BEGIN
    SET NOCOUNT ON;
    DECLARE @MaPhienDiemDanh INT;
    DECLARE @MaLopHocPhan VARCHAR(10);

    SELECT 
        @MaPhienDiemDanh = pd.MaPhienDiemDanh,
        @MaLopHocPhan = bh.MaLopHocPhan
    FROM PhienDiemDanh pd
    JOIN BuoiHoc bh ON pd.MaBuoiHoc = bh.MaBuoiHoc
    WHERE pd.MaCode = @MaCode 
      AND GETDATE() BETWEEN pd.ThoiGianBatDauPhien AND pd.ThoiGianKetThucPhien;

    IF @MaPhienDiemDanh IS NULL
    BEGIN
        RAISERROR (N'Mã điểm danh không hợp lệ hoặc đã hết hạn.', 16, 1);
        RETURN;
    END

    IF NOT EXISTS (
        SELECT 1 
        FROM DangKyLopHocPhan 
        WHERE MaLopHocPhan = @MaLopHocPhan AND MaSinhVien = @MaSinhVien
    )
    BEGIN
        RAISERROR (N'Sinh viên không có trong lớp học phần này.', 16, 1);
        RETURN;
    END

    IF EXISTS (
        SELECT 1
        FROM LuotDiemDanh
        WHERE MaPhienDiemDanh = @MaPhienDiemDanh AND MaSinhVien = @MaSinhVien
    )
    BEGIN
        SELECT 2 AS SuccessStatus, N'Sinh viên đã điểm danh phiên này rồi.' AS Message;
        RETURN;
    END

    INSERT INTO LuotDiemDanh (
        MaPhienDiemDanh, MaSinhVien, TrangThaiDiemDanh, 
        PhuongThuc, ThoiGianDiemDanh, DiaChiIP
    )
    VALUES (
        @MaPhienDiemDanh, @MaSinhVien, N'Có mặt', 
        N'Nhập mã', GETDATE(), @DiaChiIP
    );

    SELECT 1 AS SuccessStatus, N'Điểm danh thành công.' AS Message;
END;
GO

-- 6. SV quét QR (Tìm theo MaPhien)
CREATE OR ALTER PROCEDURE sp_LuotDiemDanh_QR
    @MaPhienDiemDanh INT,
    @MaSinhVien VARCHAR(10),
    @DiaChiIP VARCHAR(45) = NULL
AS
BEGIN
    SET NOCOUNT ON;
    DECLARE @MaLopHocPhan VARCHAR(10);

    -- KIỂM TRA PHIÊN CÒN HOẠT ĐỘNG KHÔNG
    IF NOT EXISTS (
        SELECT 1 FROM PhienDiemDanh 
        WHERE MaPhienDiemDanh = @MaPhienDiemDanh 
          AND GETDATE() BETWEEN ThoiGianBatDauPhien AND ThoiGianKetThucPhien
    )
    BEGIN
        RAISERROR (N'Phiên điểm danh không hợp lệ hoặc đã hết hạn.', 16, 1);
        RETURN;
    END

    SELECT @MaLopHocPhan = bh.MaLopHocPhan
    FROM PhienDiemDanh pd
    JOIN BuoiHoc bh ON pd.MaBuoiHoc = bh.MaBuoiHoc
    WHERE pd.MaPhienDiemDanh = @MaPhienDiemDanh;

    IF @MaLopHocPhan IS NULL
    BEGIN
        RAISERROR (N'Phiên điểm danh không hợp lệ.', 16, 1);
        RETURN;
    END

    IF NOT EXISTS (
        SELECT 1 
        FROM DangKyLopHocPhan 
        WHERE MaLopHocPhan = @MaLopHocPhan AND MaSinhVien = @MaSinhVien
    )
    BEGIN
        RAISERROR (N'Sinh viên không có trong lớp học phần này.', 16, 1);
        RETURN;
    END

    IF EXISTS (
        SELECT 1
        FROM LuotDiemDanh
        WHERE MaPhienDiemDanh = @MaPhienDiemDanh AND MaSinhVien = @MaSinhVien
    )
    BEGIN
        SELECT 2 AS SuccessStatus, N'Sinh viên đã điểm danh phiên này rồi.' AS Message;
        RETURN;
    END

    INSERT INTO LuotDiemDanh (
        MaPhienDiemDanh, MaSinhVien, TrangThaiDiemDanh, 
        PhuongThuc, ThoiGianDiemDanh, DiaChiIP
    )
    VALUES (
        @MaPhienDiemDanh, @MaSinhVien, N'Có mặt', 
        N'QR Web', GETDATE(), @DiaChiIP
    );

    SELECT 1 AS SuccessStatus, N'Điểm danh thành công.' AS Message;
END;
GO

-- 7. Lấy danh sách điểm danh của buổi học (kèm trạng thái, phương thức, IP)
CREATE OR ALTER PROCEDURE sp_LayDanhSachDiemDanh_BuoiHoc
    @MaBuoiHoc INT
AS
BEGIN
    SET NOCOUNT ON;
    
    -- CTE để lấy thông tin điểm danh mới nhất/quan trọng nhất của mỗi sinh viên trong buổi học
    WITH DiemDanhSummary AS (
        SELECT 
            ldd.MaSinhVien,
            ldd.TrangThaiDiemDanh,
            ldd.PhuongThuc,
            ldd.ThoiGianDiemDanh,
            ldd.DiaChiIP,
            ROW_NUMBER() OVER (
                PARTITION BY ldd.MaSinhVien 
                ORDER BY 
                    -- Ưu tiên trạng thái: Có mặt (1) > Muộn (2) > Vắng CP (3) > Vắng KP (4) > Khác
                    CASE ldd.TrangThaiDiemDanh 
                        WHEN N'Có mặt' THEN 1 
                        WHEN N'Muộn' THEN 2 
                        WHEN N'Vắng có phép' THEN 3 
                        WHEN N'Vắng không phép' THEN 4 
                        ELSE 5 
                    END ASC,
                    ldd.ThoiGianDiemDanh DESC
            ) as RowNum
        FROM LuotDiemDanh ldd
        JOIN PhienDiemDanh pd ON ldd.MaPhienDiemDanh = pd.MaPhienDiemDanh
        WHERE pd.MaBuoiHoc = @MaBuoiHoc
    )
    SELECT 
        sv.MaSinhVien,
        nd.HoTen,
        ISNULL(dds.TrangThaiDiemDanh, N'Chưa điểm danh') as TrangThaiDiemDanh,
        ISNULL(dds.PhuongThuc, '') as PhuongThuc,
        dds.ThoiGianDiemDanh,
        ISNULL(dds.DiaChiIP, '') as DiaChiIP
    FROM BuoiHoc bh
    INNER JOIN LopHocPhan lhp ON bh.MaLopHocPhan = lhp.MaLopHocPhan
    INNER JOIN DangKyLopHocPhan dklhp ON lhp.MaLopHocPhan = dklhp.MaLopHocPhan
    INNER JOIN SinhVien sv ON dklhp.MaSinhVien = sv.MaSinhVien
    INNER JOIN NguoiDung nd ON sv.MaNguoiDung = nd.MaNguoiDung
    LEFT JOIN DiemDanhSummary dds ON sv.MaSinhVien = dds.MaSinhVien AND dds.RowNum = 1
    WHERE bh.MaBuoiHoc = @MaBuoiHoc
    ORDER BY nd.HoTen;
END;
GO

-- 8. Kết thúc phiên điểm danh
CREATE OR ALTER PROCEDURE sp_KetThucPhien
    @MaPhienDiemDanh INT
AS
BEGIN
    SET NOCOUNT ON;

    UPDATE PhienDiemDanh
    SET ThoiGianKetThucPhien = GETDATE()
    WHERE MaPhienDiemDanh = @MaPhienDiemDanh;

    SELECT 1 AS SuccessStatus, N'Đã kết thúc phiên điểm danh.' AS Message;
END;
GO

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
