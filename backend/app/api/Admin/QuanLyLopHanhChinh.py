from flask import Blueprint, request, jsonify
from app.core.KetNoiDB import get_db_connection
from app.core.XacThuc.PhanQuyen import require_admin
import pyodbc

quanlylophc_bp = Blueprint('quanlylophc_bp', __name__)

@quanlylophc_bp.route('/lophanhchinh', methods=['POST'])
@require_admin
# thêm lớp hành chính
def handle_add_lophc():
    data = request.get_json()
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "{CALL sp_ThemLopHanhChinh(?, ?)}",
            (data.get('ma_lop'), data.get('ten_lop'))
        )
        result = cursor.fetchone()
        conn.commit()
        return jsonify({"success": True, "message": result[1]}), 201
    except pyodbc.Error as e:
        conn.rollback()
        return jsonify({"success": False, "message": str(e)}), 500
    finally:
        if conn:
            conn.close()

@quanlylophc_bp.route('/lophanhchinh', methods=['GET'])
@require_admin
# lấy danh sách lớp hành chính
def handle_get_all_lophc():
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("{CALL sp_LayDanhSachLopHC}")
        rows = cursor.fetchall()
        ds_lop_hanh_chinh = [{"ma_lop_hanh_chinh": row[0], "ten_lop_hanh_chinh": row[1]} for row in rows]
        return jsonify({"success": True, "data": ds_lop_hanh_chinh})
    except Exception as e:
        return jsonify({"success": False, "message": f"Lỗi: {e}"}), 500
    finally:
        if conn:
            conn.close()


@quanlylophc_bp.route('/lophanhchinh/<string:ma_lop>', methods=['GET'])
@require_admin
# lấy chi tiết lớp hành chính
def handle_get_lophc_detail(ma_lop):
    conn = None
    try:
        conn = get_db_connection()
        if conn is None:
            return jsonify({"success": False, "message": "Lỗi kết nối CSDL"}), 500

        cursor = conn.cursor()
        cursor.execute("{CALL sp_LayChiTietLopHC(?)}", (ma_lop))
        row = cursor.fetchone()

        if not row:
            return jsonify({"success": False, "message": "Không tìm thấy Lớp Hành Chính"}), 404

        lop_hanh_chinh_detail = {
            "ma_lop_hanh_chinh": row[0],
            "ten_lop_hanh_chinh": row[1]
        }

        return jsonify({"success": True, "data": lop_hanh_chinh_detail})

    except pyodbc.Error as e:
        return jsonify({"success": False, "message": str(e)}), 500
    except Exception as e:
        return jsonify({"success": False, "message": f"Lỗi máy chủ: {e}"}), 500
    finally:
        if conn:
            conn.close()


@quanlylophc_bp.route('/lophanhchinh/<string:ma_lop>', methods=['PUT'])
@require_admin
# cập nhật lớp hành chính
def handle_update_lophc(ma_lop):
    data = request.get_json()
    ten_lop = data.get('ten_lop')

    if not ten_lop:
        return jsonify({"success": False, "message": "Thiếu Tên Lớp"}), 400

    conn = None
    try:
        conn = get_db_connection()
        if conn is None:
            return jsonify({"success": False, "message": "Lỗi kết nối CSDL"}), 500

        cursor = conn.cursor()
        cursor.execute("{CALL sp_SuaLopHanhChinh(?, ?)}", (ma_lop, ten_lop))
        result = cursor.fetchone()

        conn.commit()

        return jsonify({"success": True, "message": result[1]})

    except pyodbc.Error as e:
        conn.rollback()
        if e.args[0] == '42000':
            return jsonify({"success": False, "message": str(e)}), 400
        return jsonify({"success": False, "message": str(e)}), 500
    except Exception as e:
        conn.rollback()
        return jsonify({"success": False, "message": f"Lỗi máy chủ: {e}"}), 500
    finally:
        if conn:
            conn.close()


@quanlylophc_bp.route('/lophanhchinh/<string:ma_lop>', methods=['DELETE'])
@require_admin
# xóa lớp hành chính
def handle_delete_lophc(ma_lop):
    conn = None
    try:
        conn = get_db_connection()
        if conn is None:
            return jsonify({"success": False, "message": "Lỗi kết nối CSDL"}), 500

        cursor = conn.cursor()
        cursor.execute("{CALL sp_XoaLopHanhChinh(?)}", (ma_lop))
        result = cursor.fetchone()

        conn.commit()

        return jsonify({"success": True, "message": result[1]})

    except pyodbc.Error as e:
        conn.rollback()
        if e.args[0] == '42000':
            return jsonify({"success": False, "message": str(e)}), 400
        return jsonify({"success": False, "message": str(e)}), 500
    except Exception as e:
        conn.rollback()
        return jsonify({"success": False, "message": f"Lỗi máy chủ: {e}"}), 500
    finally:
        if conn:
            conn.close()
