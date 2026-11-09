from flask import Flask


def create_app():
    app = Flask(__name__)

    # Import và đăng ký các package
    from app.core.XacThuc.DangNhap import dangnhap_bp
    from app.core.XacThuc.DoiMatKhau import doimatkhau_bp
    from app.core.XacThuc.PhanQuyen import phanquyen_bp
    from app.api.CapNhatThongTinCaNhan import capnhatthongtin_bp
    from app.api.Admin.QuanLySinhVien import quanlysinhvien_bp
    from app.api.DiemDanh import diemdanh_bp
    from app.api.Admin.QuanLyGiangVien import quanlygiangvien_bp
    from app.api.Admin.QuanLyKhoa import quanlykhoa_bp
    from app.api.Admin.QuanLyLopHanhChinh import quanlylophc_bp
    from app.api.Admin.QuanLyMonHoc import quanlymonhoc_bp
    from app.api.Admin.QuanLyLopHocPhan import quanlylophocphan_bp
    from app.api.DangKyLop import dangkylop_bp
    from app.api.Admin.InputSVTuFile import inputsv_bp
    from app.api.Admin.BaoCaoAdmin import baocaoadmin_bp
    from app.api.Admin.QuanLyKhuonMat import quanlykhuonmat_bp
    from app.api.GiangVien.BaoCaoGiangVien import baocaogiangvien_bp
    from app.api.GiangVien.ChucNangGiangVien import chucnanggiangvien_bp
    from app.api.SinhVien.ChucNangSinhVien import chucnangsinhvien_bp

    # Đăng ký các blueprint với url_prefix
    app.register_blueprint(dangnhap_bp, url_prefix='/api')
    app.register_blueprint(doimatkhau_bp, url_prefix='/api')
    app.register_blueprint(capnhatthongtin_bp, url_prefix='/api')
    app.register_blueprint(quanlysinhvien_bp, url_prefix='/api')
    app.register_blueprint(diemdanh_bp, url_prefix='/api')
    app.register_blueprint(quanlygiangvien_bp, url_prefix='/api')
    app.register_blueprint(quanlykhoa_bp, url_prefix='/api')
    app.register_blueprint(quanlylophc_bp, url_prefix='/api')
    app.register_blueprint(quanlymonhoc_bp, url_prefix='/api')
    app.register_blueprint(quanlylophocphan_bp, url_prefix='/api')
    app.register_blueprint(dangkylop_bp, url_prefix='/api')
    app.register_blueprint(inputsv_bp, url_prefix='/api')
    app.register_blueprint(baocaoadmin_bp, url_prefix='/api')
    app.register_blueprint(quanlykhuonmat_bp, url_prefix='/api')
    app.register_blueprint(baocaogiangvien_bp, url_prefix='/api')
    app.register_blueprint(chucnanggiangvien_bp, url_prefix='/api')
    app.register_blueprint(chucnangsinhvien_bp, url_prefix='/api')
    app.register_blueprint(phanquyen_bp, url_prefix='/api')

    return app
