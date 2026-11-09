from flask import Blueprint, request, jsonify, g
from functools import wraps
from app.core.KetNoiDB import get_db_connection
import pyodbc

phanquyen_bp = Blueprint('phanquyen_bp', __name__)


def require_role(allowed_roles):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            auth_header = request.headers.get('Authorization')
            if not auth_header:
                return jsonify({"success": False, "message": "Thieu token"}), 401

            try:
                token_parts = auth_header.split(' ')
                if len(token_parts) != 2 or token_parts[0] != 'Bearer':
                    return jsonify({"success": False, "message": "Token khong hop le"}), 401

                token_data = token_parts[1].split(':')
                if len(token_data) != 2:
                    return jsonify({"success": False, "message": "Token khong hop le"}), 401

                user_role = token_data[0]
                user_id = token_data[1]

                if user_role not in allowed_roles:
                    return jsonify({"success": False, "message": "Khong co quyen truy cap"}), 403

                g.user_id = user_id
                g.user_role = user_role

                return f(*args, **kwargs)

            except Exception as e:
                return jsonify({"success": False, "message": f"Loi xac thuc: {str(e)}"}), 401

        return decorated_function

    return decorator


def require_admin(f):
    return require_role(['admin'])(f)


def require_giangvien(f):
    return require_role(['giangvien', 'admin'])(f)


def require_sinhvien(f):
    return require_role(['sinhvien', 'admin'])(f)


def require_giangvien_or_sinhvien(f):
    return require_role(['giangvien', 'sinhvien', 'admin'])(f)


@phanquyen_bp.route('/phanquyen', methods=['GET'])
@require_admin
def handle_get_permissions():
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("{CALL sp_LayDanhSachQuyen}")
        rows = cursor.fetchall()

        permissions = []
        for row in rows:
            permissions.append({
                "MaQuyen": row[0],
                "TenQuyen": row[1],
                "MoTa": row[2]
            })

        return jsonify({"success": True, "data": permissions})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500
    finally:
        if conn:
            conn.close()


@phanquyen_bp.route('/phanquyen/nguoidung', methods=['POST'])
@require_admin
def handle_assign_permission():
    data = request.get_json()
    ma_nguoi_dung = data.get('ma_nguoi_dung')
    ma_quyen = data.get('ma_quyen')

    if not ma_nguoi_dung or not ma_quyen:
        return jsonify({"success": False, "message": "Thieu thong tin"}), 400

    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("{CALL sp_PhanQuyenNguoiDung(?, ?)}", (ma_nguoi_dung, ma_quyen))
        result = cursor.fetchone()
        conn.commit()

        return jsonify({"success": True, "message": result[1]})
    except pyodbc.Error as e:
        conn.rollback()
        return jsonify({"success": False, "message": str(e)}), 500
    except Exception as e:
        conn.rollback()
        return jsonify({"success": False, "message": f"Loi may chu: {e}"}), 500
    finally:
        if conn:
            conn.close()

