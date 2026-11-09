from flask import Blueprint, request, jsonify
from app.core.KetNoiDB import get_db_connection
from app.core.XacThuc.PhanQuyen import require_admin
import pyodbc

quanlymonhoc_bp = Blueprint('quanlymonhoc_bp', __name__)

@quanlymonhoc_bp.route('/monhoc', methods=['POST'])
@require_admin
# thêm môn học
def handle_add_monhoc():
    data = request.get_json()
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "{CALL sp_ThemMonHoc(?, ?, ?, ?)}",
            (
                data.get('ma_mon_hoc'),
                data.get('ten_mon_hoc'),
                data.get('so_tin_chi'),
                data.get('ma_khoa')
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

@quanlymonhoc_bp.route('/monhoc', methods=['GET'])
@require_admin
# lấy danh sách môn học
def handle_get_all_monhoc():
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("{CALL sp_LayDanhSachMonHoc}")
        rows = cursor.fetchall()
        ds_mon_hoc = [{"ma_mon_hoc": row[0], "ten_mon_hoc": row[1], "so_tin_chi": row[2], "ma_khoa": row[3], "ten_khoa": row[4]} for row in rows]
        return jsonify({"success": True, "data": ds_mon_hoc})
    except Exception as e:
        return jsonify({"success": False, "message": f"Lỗi: {e}"}), 500
    finally:
        if conn:
            conn.close()


@quanlymonhoc_bp.route('/monhoc/<string:ma_mon_hoc>', methods=['GET'])
@require_admin
# lấy chi tiết môn học
def handle_get_monhoc_detail(ma_mon_hoc):
    conn = None
    try:
        conn = get_db_connection()
        if conn is None:
            return jsonify({"success": False, "message": "Lỗi kết nối CSDL"}), 500

        cursor = conn.cursor()
        cursor.execute("{CALL sp_LayChiTietMonHoc(?)}", (ma_mon_hoc))
        row = cursor.fetchone()

        if not row:
            return jsonify({"success": False, "message": "Không tìm thấy môn học"}), 404

        mon_hoc_detail = {
            "ma_mon_hoc": row[0],
            "ten_mon_hoc": row[1],
            "so_tin_chi": row[2],
            "ma_khoa": row[3],
            "ten_khoa": row[4]
        }

        return jsonify({"success": True, "data": mon_hoc_detail})

    except pyodbc.Error as e:
        return jsonify({"success": False, "message": str(e)}), 500
    except Exception as e:
        return jsonify({"success": False, "message": f"Lỗi máy chủ: {e}"}), 500
    finally:
        if conn:
            conn.close()


@quanlymonhoc_bp.route('/monhoc/<string:ma_mon_hoc>', methods=['PUT'])
@require_admin
# cập nhật môn học
def handle_update_monhoc(ma_mon_hoc):
    data = request.get_json()
    conn = None
    try:
        conn = get_db_connection()
        if conn is None:
            return jsonify({"success": False, "message": "Lỗi kết nối CSDL"}), 500

        cursor = conn.cursor()
        cursor.execute(
            "{CALL sp_SuaMonHoc(?, ?, ?, ?)}",
            (
                ma_mon_hoc,
                data.get('ten_mon_hoc'),
                data.get('so_tin_chi'),
                data.get('ma_khoa')
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


@quanlymonhoc_bp.route('/monhoc/<string:ma_mon_hoc>', methods=['DELETE'])
@require_admin
# xóa môn học
def handle_delete_monhoc(ma_mon_hoc):
    conn = None
    try:
        conn = get_db_connection()
        if conn is None:
            return jsonify({"success": False, "message": "Lỗi kết nối CSDL"}), 500

        cursor = conn.cursor()
        cursor.execute("{CALL sp_XoaMonHoc(?)}", (ma_mon_hoc))
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
