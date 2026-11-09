from flask import Blueprint, request, jsonify
from app.core.KetNoiDB import get_db_connection
import pyodbc

doimatkhau_bp = Blueprint('doimatkhau_bp', __name__)


@doimatkhau_bp.route('/doimatkhau', methods=['PUT'])
def handle_change_password():
    data = request.get_json()

    ma_nguoi_dung = data.get('ma_nguoi_dung')
    mat_khau_cu = data.get('mat_khau_cu')
    mat_khau_moi = data.get('mat_khau_moi')

    if not ma_nguoi_dung or not mat_khau_cu or not mat_khau_moi:
        return jsonify({"success": False, "message": "Thiếu thông tin bắt buộc"}), 400

    conn = None
    try:
        conn = get_db_connection()
        if conn is None:
            return jsonify({"success": False, "message": "Lỗi kết nối CSDL"}), 500

        cursor = conn.cursor()

        cursor.execute(
            "{CALL sp_DoiMatKhau(?, ?, ?)}",
            (ma_nguoi_dung, mat_khau_cu, mat_khau_moi)
        )

        result = cursor.fetchone()
        conn.commit()

        if result and len(result) > 1:
            return jsonify({"success": True, "message": result[1]})
        else:
            return jsonify({"success": False, "message": "Không nhận được phản hồi hợp lệ từ cơ sở dữ liệu"}), 500

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