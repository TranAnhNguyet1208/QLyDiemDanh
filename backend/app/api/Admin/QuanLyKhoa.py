from flask import Blueprint, request, jsonify
from app.core.KetNoiDB import get_db_connection
from app.core.XacThuc.PhanQuyen import require_admin
import pyodbc

quanlykhoa_bp = Blueprint('quanlykhoa_bp', __name__)

@quanlykhoa_bp.route('/khoa', methods=['POST'])
@require_admin
# thêm khoa
def handle_add_khoa():
    data = request.get_json()
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "{CALL sp_ThemKhoa(?, ?, ?, ?, ?)}",
            (
                data.get('ma_khoa'),
                data.get('ten_khoa'),
                data.get('so_dien_thoai'),
                data.get('email'),
                data.get('phong_lam_viec')
            )
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

@quanlykhoa_bp.route('/khoa', methods=['GET'])
@require_admin
# lấy danh sách khoa
def handle_get_all_khoa():
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("{CALL sp_LayDanhSachKhoa}")
        rows = cursor.fetchall()
        data = [
            {
                "ma_khoa": row[0],
                "ten_khoa": row[1],
                "so_dien_thoai": row[2],
                "email": row[3],
                "phong_lam_viec": row[4]
            } for row in rows
        ]
        return jsonify({"success": True, "data": data})
    except Exception as e:
        return jsonify({"success": False, "message": f"Lỗi: {e}"}), 500
    finally:
        if conn:
            conn.close()


@quanlykhoa_bp.route('/khoa/<string:ma_khoa>', methods=['PUT'])
@require_admin
# cập nhật khoa
def handle_update_khoa(ma_khoa):
    data = request.get_json()
    conn = None
    try:
        conn = get_db_connection()
        if conn is None:
            return jsonify({"success": False, "message": "Lỗi kết nối CSDL"}), 500

        cursor = conn.cursor()
        cursor.execute(
            "{CALL sp_SuaKhoa(?, ?, ?, ?, ?)}",
            (
                ma_khoa,
                data.get('ten_khoa'),
                data.get('so_dien_thoai'),
                data.get('email'),
                data.get('phong_lam_viec')
            )
        )
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


@quanlykhoa_bp.route('/khoa/<string:ma_khoa>', methods=['DELETE'])
@require_admin
# xóa khoa
def handle_delete_khoa(ma_khoa):
    conn = None
    try:
        conn = get_db_connection()
        if conn is None:
            return jsonify({"success": False, "message": "Lỗi kết nối CSDL"}), 500

        cursor = conn.cursor()
        cursor.execute("{CALL sp_XoaKhoa(?)}", (ma_khoa))
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


@quanlykhoa_bp.route('/khoa/<string:ma_khoa>', methods=['GET'])
@require_admin
# lấy chi tiết khoa
def handle_get_khoa_detail(ma_khoa):
    conn = None
    try:
        conn = get_db_connection()
        if conn is None:
            return jsonify({"success": False, "message": "Lỗi kết nối CSDL"}), 500

        cursor = conn.cursor()
        cursor.execute("{CALL sp_LayChiTietKhoa(?)}", (ma_khoa))
        row = cursor.fetchone()

        if not row:
            return jsonify({"success": False, "message": "Không tìm thấy khoa"}), 404

        khoa_detail = {
            "ma_khoa": row[0],
            "ten_khoa": row[1],
            "so_dien_thoai": row[2],
            "email": row[3],
            "phong_lam_viec": row[4]
        }

        return jsonify({"success": True, "data": khoa_detail})

    except pyodbc.Error as e:
        return jsonify({"success": False, "message": str(e)}), 500
    except Exception as e:
        return jsonify({"success": False, "message": f"Lỗi máy chủ: {e}"}), 500
    finally:
        if conn:
            conn.close()