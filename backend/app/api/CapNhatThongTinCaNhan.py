from flask import Blueprint, request, jsonify
from app.core.KetNoiDB import get_db_connection
from app.core.XacThuc.PhanQuyen import require_giangvien_or_sinhvien
import pyodbc

capnhatthongtin_bp = Blueprint('capnhatthongtin_bp', __name__)


@capnhatthongtin_bp.route('/taikhoan/<string:ma_nguoi_dung>', methods=['GET'])
@require_giangvien_or_sinhvien
# lấy thông tin cá nhân
def handle_get_personal_info(ma_nguoi_dung):
    conn = None
    try:
        conn = get_db_connection()
        if conn is None:
            return jsonify({"success": False, "message": "Lỗi kết nối CSDL"}), 500

        cursor = conn.cursor()

        cursor.execute("{CALL sp_LayThongTinCaNhan(?)}", (ma_nguoi_dung,))

        row = cursor.fetchone()
        if not row:
            return jsonify({"success": False, "message": "Không tìm thấy người dùng"}), 404

        info = {
            "ma_nguoi_dung": row[0],
            "ho_ten": row[1],
            "email": row[2],
            "so_dien_thoai": row[3],
            "vai_tro": row[4],
            "trang_thai": row[5],
            "mat_khau": "*" * len(row[6]) if row[6] else ""
        }

        if row[4] == 'sinhvien' and row[7]: 
            ngay_sinh = row[9]
            if ngay_sinh:
                if hasattr(ngay_sinh, 'strftime'):
                    ngay_sinh = ngay_sinh.strftime('%Y-%m-%d')
                else:
                    ngay_sinh = str(ngay_sinh)

            info.update({
                "ma_sinh_vien": row[7],
                "ma_lop_hanh_chinh": row[8],
                "ngay_sinh": ngay_sinh,
                "gioi_tinh": row[10],
                "dia_chi": row[11],
                "ten_lop_hanh_chinh": row[12]
            })

        elif row[4] == 'giangvien' and row[13]:  
            info.update({
                "ma_giang_vien": row[13],
                "ma_khoa": row[14],
                "hoc_vi": row[15],
                "ten_khoa": row[16]
            })

        return jsonify({"success": True, "data": info})
    except Exception as e:
        return jsonify({"success": False, "message": f"Lỗi máy chủ: {e}"}), 500
    finally:
        if conn:
            conn.close()


@capnhatthongtin_bp.route('/taikhoan/<string:ma_nguoi_dung>', methods=['PUT'])
@require_giangvien_or_sinhvien
# cập nhật thông tin cá nhân
def handle_update_personal_info(ma_nguoi_dung):
    data = request.get_json()

    conn = None
    try:
        conn = get_db_connection()
        if conn is None:
            return jsonify({"success": False, "message": "Lỗi kết nối CSDL"}), 500

        cursor = conn.cursor()

        cursor.execute(
            "{CALL sp_CapNhatThongTinCaNhan(?, ?, ?, ?, ?, ?, ?)}",
            (
                ma_nguoi_dung,
                data.get('ho_ten'),
                data.get('so_dien_thoai'),
                data.get('email'),
                data.get('ngay_sinh'),
                data.get('dia_chi'),
                data.get('gioi_tinh')
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