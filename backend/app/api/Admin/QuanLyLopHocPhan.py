from flask import Blueprint, request, jsonify
from app.core.KetNoiDB import get_db_connection
from app.core.XacThuc.PhanQuyen import require_admin, require_giangvien
import pyodbc

quanlylophocphan_bp = Blueprint('quanlylophocphan_bp', __name__)


@quanlylophocphan_bp.route('/lophocphan', methods=['POST'])
@require_admin
# thêm lớp học phần
def handle_add_lophocphan():
    data = request.get_json()
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "{CALL sp_ThemLopHocPhan(?, ?, ?, ?, ?, ?)}",
            (
                data.get('ma_lhp'),
                data.get('ma_mon_hoc'),
                data.get('hoc_ky'),
                data.get('nam_hoc'),
                data.get('ma_giang_vien'),
                data.get('ghi_chu')
            )
        )
        result = cursor.fetchone()
        conn.commit()
        return jsonify({"success": True, "message": result[1]}), 201
    except pyodbc.Error as e:
        if conn:
            conn.rollback()
        return jsonify({"success": False, "message": str(e)}), 500
    finally:
        if conn:
            conn.close()


@quanlylophocphan_bp.route('/lophocphan', methods=['GET'])
@require_admin
# lấy danh sách lớp học phần
def handle_get_list_lhp():
    conn = None
    try:
        conn = get_db_connection()
        if conn is None:
            return jsonify({"success": False, "message": "Lỗi kết nối CSDL"}), 500

        cursor = conn.cursor()
        try:
            cursor.execute("{CALL sp_LayDanhSachLopHocPhan()}")
        except pyodbc.Error as e:
            print(f"Error executing stored procedure sp_LayDanhSachLopHocPhan: {e}")
            return jsonify({"success": False, "message": f"Lỗi gọi thủ tục: {e}"}), 500
        rows = cursor.fetchall()

        ds_lop = []
        for row in rows:
            ds_lop.append({
                "ma_lop_hoc_phan": row[0],
                "ma_mon_hoc": row[1],
                "ten_mon_hoc": row[2],
                "ma_giang_vien": row[3],
                "ten_giang_vien": row[4] if row[4] else "Chưa phân công",
                "hoc_ky": row[5],
                "nam_hoc": row[6],
                "si_so": row[7] if len(row) > 7 else 0
            })

        return jsonify({"success": True, "data": ds_lop})

    except pyodbc.Error as e:
        print(f"Pyodbc error: {e}")
        return jsonify({"success": False, "message": str(e)}), 500
    except Exception as e:
        print(f"General error in handle_get_list_lhp: {e}")
        return jsonify({"success": False, "message": f"Lỗi máy chủ: {e}"}), 500
    finally:
        if conn:
            conn.close()


@quanlylophocphan_bp.route('/buoihoc', methods=['POST'])
@require_admin
# thêm buổi học
def handle_add_buoihoc():
    data = request.get_json()
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "{CALL sp_ThemBuoiHoc(?, ?, ?, ?, ?, ?)}",
            (
                data.get('ma_lhp'),
                data.get('ngay_hoc'),
                data.get('phong_hoc'),
                data.get('thoi_gian_bat_dau'),
                data.get('thoi_gian_ket_thuc'),
                data.get('ghi_chu')
            )
        )
        result = cursor.fetchone()
        conn.commit()
        return jsonify({"success": True, "message": result[1]}), 201
    except pyodbc.Error as e:
        if conn:
            conn.rollback()
        return jsonify({"success": False, "message": str(e)}), 500
    finally:
        if conn:
            conn.close()


@quanlylophocphan_bp.route('/lophocphan/gan-giangvien', methods=['PUT'])
@require_admin
# phân công giảng viên cho lớp học phần
def handle_assign_lecturer_lhp():
    data = request.get_json()
    ma_lhp = data.get('ma_lhp')
    ma_gv = data.get('ma_gv_moi')

    if not ma_lhp or not ma_gv:
        return jsonify({"success": False, "message": "Thiếu thông tin bắt buộc"}), 400

    conn = None
    try:
        conn = get_db_connection()
        if conn is None:
            return jsonify({"success": False, "message": "Lỗi kết nối CSDL"}), 500

        cursor = conn.cursor()

        cursor.execute("{CALL sp_CapNhatGiangVienLHP(?, ?)}", (ma_lhp, ma_gv))
        result = cursor.fetchone()

        conn.commit()

        return jsonify({"success": True, "message": result[1]})

    except pyodbc.Error as e:
        if conn:
            conn.rollback()
        if e.args[0] == '42000':
            return jsonify({"success": False, "message": str(e)}), 400
        return jsonify({"success": False, "message": str(e)}), 500
    except Exception as e:
        if conn:
            conn.rollback()
        return jsonify({"success": False, "message": f"Lỗi máy chủ: {e}"}), 500
    finally:
        if conn:
            conn.close()


@quanlylophocphan_bp.route('/buoihoc/<int:ma_buoi_hoc>', methods=['PUT'])
@require_admin
# cập nhật buổi học
def handle_update_buoihoc(ma_buoi_hoc):
    data = request.get_json()
    conn = None
    try:
        conn = get_db_connection()
        if conn is None:
            return jsonify({"success": False, "message": "Lỗi kết nối CSDL"}), 500

        cursor = conn.cursor()

        cursor.execute(
            "{CALL sp_CapNhatBuoiHoc(?, ?, ?, ?, ?, ?, ?)}",
            (
                ma_buoi_hoc,
                data.get('ngay_hoc'),
                data.get('phong_hoc'),
                data.get('thoi_gian_bat_dau'),
                data.get('thoi_gian_ket_thuc'),
                data.get('trang_thai'),
                data.get('ghi_chu')
            )
        )
        result = cursor.fetchone()

        conn.commit()

        return jsonify({"success": True, "message": result[1]})

    except pyodbc.Error as e:
        if conn:
            conn.rollback()
        if e.args[0] == '42000':
            return jsonify({"success": False, "message": str(e)}), 400
        return jsonify({"success": False, "message": str(e)}), 500
    except Exception as e:
        if conn:
            conn.rollback()
        return jsonify({"success": False, "message": f"Lỗi máy chủ: {e}"}), 500
    finally:
        if conn:
            conn.close()


@quanlylophocphan_bp.route('/lophocphan/<string:ma_lhp>', methods=['GET'])
@require_admin
# lấy chi tiết lớp học phần
def handle_get_lhp_detail(ma_lhp):
    conn = None
    try:
        conn = get_db_connection()
        if conn is None:
            return jsonify({"success": False, "message": "Lỗi kết nối CSDL"}), 500

        cursor = conn.cursor()
        cursor.execute("{CALL sp_LayChiTietLHP(?)}", (ma_lhp,))
        row = cursor.fetchone()

        if not row:
            return jsonify({"success": False, "message": "Không tìm thấy lớp học phần"}), 404

        lhp_detail = {
            "ma_lop_hoc_phan": row[0],
            "ma_mon_hoc": row[1],
            "ten_mon_hoc": row[2],
            "ma_giang_vien": row[3],
            "ten_giang_vien": row[4],
            "hoc_ky": row[5],
            "nam_hoc": row[6],
            "ghi_chu": row[7]
        }

        return jsonify({"success": True, "data": lhp_detail})

    except pyodbc.Error as e:
        return jsonify({"success": False, "message": str(e)}), 500
    except Exception as e:
        return jsonify({"success": False, "message": f"Lỗi máy chủ: {e}"}), 500
    finally:
        if conn:
            conn.close()


@quanlylophocphan_bp.route('/lophocphan/<string:ma_lhp>', methods=['PUT'])
@require_admin
# cập nhật lớp học phần
def handle_update_lhp(ma_lhp):
    data = request.get_json()
    conn = None
    try:
        conn = get_db_connection()
        if conn is None:
            return jsonify({"success": False, "message": "Lỗi kết nối CSDL"}), 500

        cursor = conn.cursor()
        cursor.execute(
            "{CALL sp_SuaLopHocPhan(?, ?, ?, ?, ?, ?)}",
            (
                ma_lhp,
                data.get('ma_mon_hoc'),
                data.get('ma_giang_vien'),
                data.get('hoc_ky'),
                data.get('nam_hoc'),
                data.get('ghi_chu')
            )
        )

        result = cursor.fetchone()
        conn.commit()

        return jsonify({"success": True, "message": result[1]})

    except pyodbc.Error as e:
        if conn:
            conn.rollback()
        if e.args[0] == '42000':
            return jsonify({"success": False, "message": str(e)}), 400
        return jsonify({"success": False, "message": str(e)}), 500
    except Exception as e:
        if conn:
            conn.rollback()
        return jsonify({"success": False, "message": f"Lỗi máy chủ: {e}"}), 500
    finally:
        if conn:
            conn.close()


@quanlylophocphan_bp.route('/buoihoc', methods=['GET'])
@require_giangvien
# lấy danh sách buổi học
def handle_get_sessions_list():
    conn = None
    try:
        conn = get_db_connection()
        if conn is None:
            return jsonify({"success": False, "message": "Lỗi kết nối CSDL"}), 500

        cursor = conn.cursor()
        
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        ma_lhp = request.args.get('class_id')
        ma_gv = request.args.get('teacher_id')

        cursor.execute(
            "{CALL sp_LayDanhSachBuoiHoc(?, ?, ?, ?)}",
            (start_date, end_date, ma_lhp, ma_gv)
        )
        rows = cursor.fetchall()
        conn.commit()

        ds_bh = []
        for row in rows:
            ds_bh.append({
                "ma_buoi_hoc": row[0],
                "ngay_hoc": row[1].strftime('%Y-%m-%d') if row[1] else None,
                "thoi_gian_bat_dau": str(row[2]) if row[2] else None,
                "thoi_gian_ket_thuc": str(row[3]) if row[3] else None,
                "phong_hoc": row[4],
                "trang_thai": row[5],
                "ma_lhp": row[6],
                "ten_mon_hoc": row[7],
                "ma_giang_vien": row[8],
                "ten_giang_vien": row[9] if len(row) > 9 and row[9] else "Chưa phân công",
                "ghi_chu": row[10] if len(row) > 10 else ""
            })

        return jsonify({"success": True, "data": ds_bh})

    except pyodbc.Error as e:
        return jsonify({"success": False, "message": str(e)}), 500
    except Exception as e:
        return jsonify({"success": False, "message": f"Lỗi máy chủ: {e}"}), 500
    finally:
        if conn:
            conn.close()


@quanlylophocphan_bp.route('/buoihoc/<int:ma_buoi_hoc>', methods=['GET'])
@require_giangvien
# lấy chi tiết buổi học
def handle_get_session_detail(ma_buoi_hoc):
    conn = None
    try:
        conn = get_db_connection()
        if conn is None:
            return jsonify({"success": False, "message": "Lỗi kết nối CSDL"}), 500

        cursor = conn.cursor()
        cursor.execute("{CALL sp_LayChiTietBuoiHoc(?)}", (ma_buoi_hoc,))
        row = cursor.fetchone()

        if not row:
            return jsonify({"success": False, "message": "Không tìm thấy buổi học"}), 404

        buoi_hoc = {
            "ma_buoi_hoc": row[0],
            "ma_lhp": row[1],
            "ma_mon_hoc": row[2],
            "ten_mon_hoc": row[3],
            "ma_giang_vien": row[4],
            "ten_giang_vien": row[5] if row[5] else "Chưa phân công",
            "ngay_hoc": row[6].strftime('%Y-%m-%d') if row[6] else None,
            "thoi_gian_bat_dau": str(row[7]) if row[7] else None,
            "thoi_gian_ket_thuc": str(row[8]) if row[8] else None,
            "phong_hoc": row[9],
            "trang_thai": row[10],
            "ghi_chu": row[11]
        }

        return jsonify({"success": True, "data": buoi_hoc})

    except pyodbc.Error as e:
        return jsonify({"success": False, "message": str(e)}), 500
    except Exception as e:
        return jsonify({"success": False, "message": f"Lỗi máy chủ: {e}"}), 500
    finally:
        if conn:
            conn.close()


@quanlylophocphan_bp.route('/lophocphan/<string:ma_lhp>/sinhvien', methods=['GET'])
@require_giangvien
# lấy danh sách sinh viên trong lớp học phần
def handle_get_students_in_class(ma_lhp):
    conn = None
    try:
        conn = get_db_connection()
        if conn is None:
            return jsonify({"success": False, "message": "Lỗi kết nối CSDL"}), 500
        
        cursor = conn.cursor()
        cursor.execute("{CALL sp_LayDanhSachSV_LHP(?)}", (ma_lhp,))
        rows = cursor.fetchall()

        ds_sinh_vien = []
        for row in rows:
            ds_sinh_vien.append({
                "ma_sinh_vien": row[0],
                "ho_ten": row[1],
                "email": row[2],
                "trang_thai_dang_ky": row[3]
            })

        return jsonify({"success": True, "data": ds_sinh_vien})

    except pyodbc.Error as e:
        return jsonify({"success": False, "message": str(e)}), 500
    except Exception as e:
        return jsonify({"success": False, "message": f"Lỗi máy chủ: {e}"}), 500
    finally:
        if conn:
            conn.close()


@quanlylophocphan_bp.route('/lophocphan/<string:ma_lhp>/sinhvien', methods=['POST'])
@require_admin
# thêm sinh viên vào lớp học phần
def handle_add_students_to_class(ma_lhp):
    data = request.get_json()

    if 'ma_sinh_vien' in data:
        danh_sach_sv = [data['ma_sinh_vien']]
    elif 'danh_sach_sinh_vien' in data:
        danh_sach_sv = data['danh_sach_sinh_vien']
    else:
        danh_sach_sv = []

    if not danh_sach_sv:
        return jsonify({"success": False, "message": "Danh sách sinh viên không được để trống"}), 400

    conn = None
    try:
        conn = get_db_connection()
        if conn is None:
            return jsonify({"success": False, "message": "Lỗi kết nối CSDL"}), 500

        cursor = conn.cursor()
        success_count = 0
        error_messages = []

        for ma_sv in danh_sach_sv:
            try:
                cursor.execute("{CALL sp_ThemSinhVienVaoLHP(?, ?)}", (ma_lhp, ma_sv))
                result = cursor.fetchone()
                if result and result[0] == 1: 
                    success_count += 1
                else:
                    error_messages.append(f"Không thể thêm sinh viên {ma_sv}: {result[1] if result else 'Lỗi không xác định'}")
            except pyodbc.Error as e:
                error_messages.append(f"Lỗi khi thêm sinh viên {ma_sv}: {str(e)}")

        conn.commit()

        message = f"Đã thêm thành công {success_count}/{len(danh_sach_sv)} sinh viên"
        if error_messages:
            message += ". Chi tiết lỗi: " + "; ".join(error_messages)

        return jsonify({"success": True, "message": message, "success_count": success_count})

    except pyodbc.Error as e:
        if conn:
            conn.rollback()
        return jsonify({"success": False, "message": str(e)}), 500
    except Exception as e:
        if conn:
            conn.rollback()
        return jsonify({"success": False, "message": f"Lỗi máy chủ: {e}"}), 500
    finally:
        if conn:
            conn.close()
