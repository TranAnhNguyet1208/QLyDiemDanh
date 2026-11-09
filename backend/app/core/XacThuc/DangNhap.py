from flask import Blueprint, request, jsonify
from app.core.KetNoiDB import get_db_connection
import pyodbc

dangnhap_bp = Blueprint('dangnhap_bp', __name__)


@dangnhap_bp.route('/dangnhap', methods=['POST'])
def handle_login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({"success": False, "message": "Nhap day du ten dang nhap va mat khau"}), 400

    conn = None
    try:
        conn = get_db_connection()
        if conn is None:
            return jsonify({"success": False, "message": "Loi ket noi CSDL"}), 500

        cursor = conn.cursor()
        cursor.execute("{CALL sp_CheckLogin(?, ?)}", (username, password))
        result = cursor.fetchone()

        if result:
            user_data = {
                "user_id": result[0],
                "ho_ten": result[1],
                "vai_tro": result[2],
                "username": username
            }
            
            if result[2] == 'sinhvien':
                user_data['ma_sinh_vien'] = result[0]
            elif result[2] == 'giangvien':
                user_data['ma_giang_vien'] = result[0]
                
            token = f"{result[2]}:{result[0]}"

            return jsonify({
                "success": True,
                "message": "Dang nhap thanh cong",
                "user": user_data,
                "token": token
            })
        else:
            return jsonify({"success": False, "message": "Sai ten dang nhap hoac mat khau"}), 401

    except pyodbc.Error as e:
        return jsonify({"success": False, "message": f"Loi may chu: {e}"}), 500
    except Exception as e:
        return jsonify({"success": False, "message": f"Loi may chu: {e}"}), 500
    finally:
        if conn:
            conn.close()