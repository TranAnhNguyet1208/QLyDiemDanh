USE qlsv;
GO

DROP TABLE IF EXISTS LuotDiemDanh;
DROP TABLE IF EXISTS PhienDiemDanh;
DROP TABLE IF EXISTS BuoiHoc;
DROP TABLE IF EXISTS DangKyLopHocPhan;
DROP TABLE IF EXISTS LopHocPhan;
DROP TABLE IF EXISTS LichSuChinhSua;
DROP TABLE IF EXISTS MonHoc;
DROP TABLE IF EXISTS SinhVien;
DROP TABLE IF EXISTS GiangVien;
DROP TABLE IF EXISTS LopHanhChinh;
DROP TABLE IF EXISTS Khoa;
DROP TABLE IF EXISTS NguoiDung;
GO

-- Bang: 1. NguoiDung
CREATE TABLE NguoiDung (
    MaNguoiDung VARCHAR(10) PRIMARY KEY,
    HoTen NVARCHAR(100) NOT NULL,
    Email VARCHAR(100) UNIQUE NOT NULL,
    MatKhau VARCHAR(255) NOT NULL,
    SoDienThoai VARCHAR(15), -- ĐÃ XÓA UNIQUE
    VaiTro NVARCHAR(20) NOT NULL,
    TrangThai NVARCHAR(30) NOT NULL
);
GO

-- Bang: 2. Khoa
CREATE TABLE Khoa (
    MaKhoa VARCHAR(10) PRIMARY KEY,
    TenKhoa NVARCHAR(100) NOT NULL,
    SoDienThoai VARCHAR(15),
    Email VARCHAR(100),
    PhongLamViec NVARCHAR(50)
);
GO

-- Bang: 3. LopHanhChinh
CREATE TABLE LopHanhChinh (
    MaLopHanhChinh VARCHAR(10) PRIMARY KEY,
    TenLopHanhChinh NVARCHAR(50) NOT NULL
);
GO

-- Bang: 4. GiangVien
CREATE TABLE GiangVien (
    MaGiangVien VARCHAR(10) PRIMARY KEY,
    MaNguoiDung VARCHAR(10) UNIQUE NOT NULL,
    MaKhoa VARCHAR(10),
    HocVi NVARCHAR(50),
    GhiChu NVARCHAR(MAX),
    FOREIGN KEY (MaNguoiDung) REFERENCES NguoiDung(MaNguoiDung) ON DELETE CASCADE,
    FOREIGN KEY (MaKhoa) REFERENCES Khoa(MaKhoa) ON DELETE SET NULL
);
GO

-- Bang: 5. SinhVien
CREATE TABLE SinhVien (
    MaSinhVien VARCHAR(10) PRIMARY KEY,
    MaNguoiDung VARCHAR(10) UNIQUE NOT NULL,
    MaLopHanhChinh VARCHAR(10),
    NgaySinh DATE,
    DiaChi NVARCHAR(255),
    GioiTinh NVARCHAR(10),
    DuLieuKhuonMat NVARCHAR(MAX) NULL,
    GhiChu NVARCHAR(MAX),
    FOREIGN KEY (MaNguoiDung) REFERENCES NguoiDung(MaNguoiDung) ON DELETE CASCADE,
    FOREIGN KEY (MaLopHanhChinh) REFERENCES LopHanhChinh(MaLopHanhChinh) ON DELETE SET NULL
);
GO

-- Bang: 6. MonHoc
CREATE TABLE MonHoc (
    MaMonHoc VARCHAR(10) PRIMARY KEY,
    TenMonHoc NVARCHAR(100) NOT NULL,
    SoTinChi INT NOT NULL,
    MaKhoa VARCHAR(10),
    FOREIGN KEY (MaKhoa) REFERENCES Khoa(MaKhoa) ON DELETE SET NULL
);
GO

-- Bang: 7. LopHocPhan
CREATE TABLE LopHocPhan (
    MaLopHocPhan VARCHAR(10) PRIMARY KEY,
    MaMonHoc VARCHAR(10) NOT NULL,
    MaGiangVien VARCHAR(10),
    HocKy INT NOT NULL,
    NamHoc VARCHAR(20) NOT NULL,
    GhiChu NVARCHAR(MAX),
    FOREIGN KEY (MaMonHoc) REFERENCES MonHoc(MaMonHoc) ON DELETE CASCADE,
    FOREIGN KEY (MaGiangVien) REFERENCES GiangVien(MaGiangVien) ON DELETE SET NULL
);
GO

-- Bang: 8. DangKyLopHocPhan
CREATE TABLE DangKyLopHocPhan (
    MaDangKy INT PRIMARY KEY IDENTITY(1,1),
    MaSinhVien VARCHAR(10) NOT NULL,
    MaLopHocPhan VARCHAR(10) NOT NULL,
    NgayDangKy DATE DEFAULT GETDATE(),
    TrangThai NVARCHAR(50),
    FOREIGN KEY (MaSinhVien) REFERENCES SinhVien(MaSinhVien) ON DELETE CASCADE,
    FOREIGN KEY (MaLopHocPhan) REFERENCES LopHocPhan(MaLopHocPhan) ON DELETE CASCADE,
    UNIQUE(MaSinhVien, MaLopHocPhan)
);
GO

-- Bang: 9. BuoiHoc
CREATE TABLE BuoiHoc (
    MaBuoiHoc INT PRIMARY KEY IDENTITY(1,1),
    MaLopHocPhan VARCHAR(10) NOT NULL,
    NgayHoc DATE NOT NULL,
    PhongHoc NVARCHAR(50),
    ThoiGianBatDau TIME,
    ThoiGianKetThuc TIME,
    TrangThai NVARCHAR(50),
    GhiChuBuoiHoc NVARCHAR(MAX),
    FOREIGN KEY (MaLopHocPhan) REFERENCES LopHocPhan(MaLopHocPhan) ON DELETE CASCADE
);
GO

-- Bang: 10. PhienDiemDanh
CREATE TABLE PhienDiemDanh (
    MaPhienDiemDanh INT PRIMARY KEY IDENTITY(1,1),
    MaBuoiHoc INT NOT NULL,
    ThoiGianBatDauPhien DATETIME DEFAULT GETDATE(),
    ThoiGianKetThucPhien DATETIME,
    MaCode VARCHAR(20) NULL,
    FOREIGN KEY (MaBuoiHoc) REFERENCES BuoiHoc(MaBuoiHoc) ON DELETE CASCADE
);
GO

-- Bang: 11. LuotDiemDanh
CREATE TABLE LuotDiemDanh (
    MaLuotDiemDanh INT PRIMARY KEY IDENTITY(1,1),
    MaPhienDiemDanh INT NOT NULL,
    MaSinhVien VARCHAR(10) NOT NULL,
    TrangThaiDiemDanh NVARCHAR(50) NOT NULL,
    PhuongThuc NVARCHAR(50),
    ThoiGianDiemDanh DATETIME DEFAULT GETDATE(),
    DiaChiIP VARCHAR(45),
    GhiChuLyDoVang NVARCHAR(500),
    FOREIGN KEY (MaPhienDiemDanh) REFERENCES PhienDiemDanh(MaPhienDiemDanh) ON DELETE CASCADE,
    FOREIGN KEY (MaSinhVien) REFERENCES SinhVien(MaSinhVien) ON DELETE NO ACTION
);
GO

-- Bang: 12. LichSuChinhSua
CREATE TABLE LichSuChinhSua (
    MaLog INT PRIMARY KEY IDENTITY(1,1),
    MaNguoiDung VARCHAR(10),
    HanhDong NVARCHAR(100),
    DoiTuong NVARCHAR(100),
    ThoiGian DATETIME DEFAULT GETDATE(),
    GhiChu NVARCHAR(MAX),
    FOREIGN KEY (MaNguoiDung) REFERENCES NguoiDung(MaNguoiDung) ON DELETE SET NULL
);
GO

