from flask import Blueprint, request, jsonify
from app.core.KetNoiDB import get_db_connection
from app.core.XacThuc.PhanQuyen import require_admin
import pyodbc

quanlygiangvien_bp = Blueprint('quanlygiangvien_bp', __name__)


@quanlygiangvien_bp.route('/giangvien', methods=['POST'])
@require_admin
# thêm giảng viên
def handle_add_lecturer():
    data = request.get_json()
    try:
        conn = get_db_connection()
        if conn is None:
            return jsonify({"success": False, "message": "Lỗi kết nối CSDL"}), 500

        cursor = conn.cursor()
        cursor.execute(
            "{CALL sp_ThemGiangVien(?, ?, ?, ?)}",
            (
                data.get('ma_khoa'),
                data.get('ho_ten'),
                data.get('ma_gv'),
                data.get('hoc_vi')
            )
        )

        result = cursor.fetchone()
        conn.commit()
        return jsonify({"success": True, "message": result[1], "generated_id": result[2]}), 201

    except pyodbc.Error as e:
        conn.rollback()
        return jsonify({"success": False, "message": str(e)}), 500
    except Exception as e:
        conn.rollback()
        return jsonify({"success": False, "message": f"Lỗi máy chủ: {e}"}), 500
    finally:
        if 'conn' in locals() and conn:
            conn.close()


@quanlygiangvien_bp.route('/giangvien', methods=['GET'])
@require_admin
# lấy danh sách giảng viên
def handle_get_all_lecturers():
    conn = None
    try:
        conn = get_db_connection()
        if conn is None:
            return jsonify({"success": False, "message": "Lỗi kết nối CSDL"}), 500

        cursor = conn.cursor()
        cursor.execute("{CALL sp_LayDanhSachGV}")
        rows = cursor.fetchall()

        ds_giang_vien = []
        for row in rows:
            ds_giang_vien.append({
                "ma_giang_vien": row[0],
                "ho_ten": row[1],
                "email": row[2],
                "trang_thai": row[3],
                "ten_khoa": row[4],
                "hoc_vi": row[5],
                "so_dien_thoai": row[6] if row[6] else ""
            })

        return jsonify({"success": True, "data": ds_giang_vien})

    except pyodbc.Error as e:
        return jsonify({"success": False, "message": str(e)}), 500
    except Exception as e:
        return jsonify({"success": False, "message": f"Lỗi máy chủ: {e}"}), 500
    finally:
        if conn:
            conn.close()


@quanlygiangvien_bp.route('/giangvien/<string:ma_gv>', methods=['GET'])
@require_admin
# lấy chi tiết giảng viên
def handle_get_lecturer_detail(ma_gv):
    conn = None
    try:
        conn = get_db_connection()
        if conn is None:
            return jsonify({"success": False, "message": "Lỗi kết nối CSDL"}), 500

        cursor = conn.cursor()
        cursor.execute("{CALL sp_LayChiTietGiangVien(?)}", (ma_gv))
        row = cursor.fetchone()

        if not row:
            return jsonify({"success": False, "message": "Không tìm thấy giảng viên"}), 404

        giang_vien_detail = {
            "ma_giang_vien": row[0],
            "ma_nguoi_dung": row[1],
            "ho_ten": row[2],
            "email": row[3],
            "so_dien_thoai": row[4],
            "trang_thai": row[5],
            "ma_khoa": row[6],
            "ten_khoa": row[7],
            "hoc_vi": row[8]
        }

        return jsonify({"success": True, "data": giang_vien_detail})

    except pyodbc.Error as e:
        return jsonify({"success": False, "message": str(e)}), 500
    except Exception as e:
        return jsonify({"success": False, "message": f"Lỗi máy chủ: {e}"}), 500
    finally:
        if conn:
            conn.close()


@quanlygiangvien_bp.route('/admin/giangvien/<string:ma_nguoi_dung>', methods=['PUT'])
@require_admin
# cập nhật thông tin giảng viên
def handle_admin_update_lecturer(ma_nguoi_dung):
    data = request.get_json()
    ma_gv = data.get('ma_giang_vien')

    if not ma_gv:
        return jsonify({"success": False, "message": "Thiếu Mã Giảng Viên (ma_giang_vien)"}), 400

    conn = None
    try:
        conn = get_db_connection()
        if conn is None:
            return jsonify({"success": False, "message": "Lỗi kết nối CSDL"}), 500

        cursor = conn.cursor()
        cursor.execute(
            "{CALL sp_Admin_SuaThongTinGiangVien(?, ?, ?, ?, ?, ?, ?, ?)}",
            (
                ma_gv,
                ma_nguoi_dung,
                data.get('ho_ten'),
                data.get('email'),
                data.get('so_dien_thoai'),
                data.get('trang_thai'),
                data.get('ma_khoa'),
                data.get('hoc_vi')
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


@quanlygiangvien_bp.route('/giangvien/<string:ma_gv>', methods=['DELETE'])
@require_admin
# xóa giảng viên
def handle_delete_lecturer(ma_gv):
    conn = None
    try:
        conn = get_db_connection()
        if conn is None:
            return jsonify({"success": False, "message": "Lỗi kết nối CSDL"}), 500

        cursor = conn.cursor()
        cursor.execute("{CALL sp_XoaGiangVien(?)}", (ma_gv))
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