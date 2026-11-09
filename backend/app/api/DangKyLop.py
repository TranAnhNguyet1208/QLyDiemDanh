from flask import Blueprint, request, jsonify
from app.core.KetNoiDB import get_db_connection
from app.core.XacThuc.PhanQuyen import require_sinhvien, require_admin
import pyodbc

dangkylop_bp = Blueprint('dangkylop_bp', __name__)


@dangkylop_bp.route('/dangky', methods=['POST'])
@require_sinhvien
# đăng ký lớp học phần
def handle_add_registration():
    data = request.get_json()
    ma_sv = data.get('ma_sinh_vien')
    ma_lhp = data.get('ma_lhp')

    if not ma_sv or not ma_lhp:
        return jsonify({"success": False, "message": "Thiếu thông tin"}), 400

    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("{CALL sp_DangKyLopHocPhan(?, ?)}", (ma_sv, ma_lhp))
        result = cursor.fetchone()
        conn.commit()

        return jsonify({"success": True, "message": result[1]}), 201

    except pyodbc.Error as e:
        conn.rollback()
        return jsonify({"success": False, "message": str(e)}), 500
    except Exception as e:
        conn.rollback()
        return jsonify({"success": False, "message": f"Lỗi: {e}"}), 500
    finally:
        if conn:
            conn.close()


@dangkylop_bp.route('/dangky-hangloat', methods=['POST'])
@require_admin
# đăng ký lớp học phần hàng loạt
def handle_batch_registration():
    data = request.get_json()
    ma_lop_hc = data.get('ma_lop_hc')
    ma_lhp = data.get('ma_lhp')

    if not ma_lop_hc or not ma_lhp:
        return jsonify({"success": False, "message": "Thiếu thông tin"}), 400

    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("{CALL sp_DangKyLHP_TheoLopHanhChinh(?, ?)}", (ma_lop_hc, ma_lhp))
        result = cursor.fetchone()
        conn.commit()

        return jsonify({"success": True, "message": result[1], "so_luong_them": result[2]}), 201

    except pyodbc.Error as e:
        conn.rollback()
        return jsonify({"success": False, "message": str(e)}), 500
    except Exception as e:
        conn.rollback()
        return jsonify({"success": False, "message": f"Lỗi: {e}"}), 500
    finally:
        if conn:
            conn.close()


@dangkylop_bp.route('/dangky', methods=['DELETE'])
@require_sinhvien
# hủy đăng ký lớp học phần
def handle_delete_registration():
    data = request.get_json()
    ma_sv = data.get('ma_sinh_vien')
    ma_lhp = data.get('ma_lhp')

    if not ma_sv or not ma_lhp:
        return jsonify({"success": False, "message": "Thiếu thông tin"}), 400

    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("{CALL sp_HuyDangKyLopHocPhan(?, ?)}", (ma_sv, ma_lhp))
        result = cursor.fetchone()
        conn.commit()

        return jsonify({"success": True, "message": result[1]})

    except pyodbc.Error as e:
        conn.rollback()
        return jsonify({"success": False, "message": str(e)}), 500
    except Exception as e:
        conn.rollback()
        return jsonify({"success": False, "message": f"Lỗi: {e}"}), 500
    finally:
        if conn:
            conn.close()


@dangkylop_bp.route('/dangky/ds-lop', methods=['GET'])
@require_sinhvien
# lấy danh sách lớp học phần có thể đăng ký
def handle_get_available_classes():
    ma_sv = request.args.get('ma_sinh_vien')
    
    if not ma_sv:
        return jsonify({"success": False, "message": "Thiếu mã sinh viên"}), 400

    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("{CALL sp_LayDanhSachLopHocPhan_ChoSinhVien(?)}", (ma_sv,))
        rows = cursor.fetchall()

        classes = []
        for row in rows:
            classes.append({
                "ma_lhp": row[0],
                "ten_mon_hoc": row[1],
                "ten_giang_vien": row[2] if row[2] else "Chưa phân công",
                "hoc_ky": row[3],
                "nam_hoc": row[4],
                "si_so": row[5],
                "da_dang_ky": bool(row[6])
            })

        return jsonify({"success": True, "data": classes})

    except pyodbc.Error as e:
        return jsonify({"success": False, "message": str(e)}), 500
    except Exception as e:
        return jsonify({"success": False, "message": f"Lỗi: {e}"}), 500
    finally:
        if conn:
            conn.close()