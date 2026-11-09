from flask import Blueprint, request, jsonify
from app.core.KetNoiDB import get_db_connection
from app.core.XacThuc.PhanQuyen import require_admin
import pyodbc

quanlysinhvien_bp = Blueprint('quanlysinhvien_bp', __name__)


@quanlysinhvien_bp.route('/sinhvien', methods=['POST'])
@require_admin
# thêm sinh viên
def handle_add_student():
    data = request.get_json()
    ma_khoa = data.get('ma_khoa')
    ho_ten = data.get('ho_ten')
    ma_sv = data.get('ma_sv')
    ma_lop_hc = data.get('ma_lop_hc')
    ngay_sinh = data.get('ngay_sinh')
    dia_chi = data.get('dia_chi')
    gioi_tinh = data.get('gioi_tinh')

    if not ma_khoa or not ho_ten or not ma_sv:
        return jsonify({"success": False, "message": "Thiếu thông tin bắt buộc"}), 400

    conn = None
    try:
        conn = get_db_connection()
        if conn is None:
            return jsonify({"success": False, "message": "Lỗi kết nối CSDL"}), 500

        cursor = conn.cursor()

        cursor.execute(
            "{CALL sp_ThemSinhVien(?, ?, ?, ?, ?, ?, ?)}",
            (ma_khoa, ho_ten, ma_sv, ma_lop_hc, ngay_sinh, dia_chi, gioi_tinh)
        )

        result = cursor.fetchone()
        conn.commit()

        return jsonify({
            "success": True,
            "message": result[1],
            "generated_id": result[2]
        }), 201

    except pyodbc.Error as e:
        conn.rollback()
        return jsonify({"success": False, "message": str(e)}), 500
    except Exception as e:
        conn.rollback()
        return jsonify({"success": False, "message": f"Lỗi máy chủ: {e}"}), 500
    finally:
        if conn:
            conn.close()


@quanlysinhvien_bp.route('/sinhvien', methods=['GET'])
@require_admin
# lấy danh sách sinh viên
def handle_get_all_students():
    conn = None
    try:
        conn = get_db_connection()
        if conn is None:
            return jsonify({"success": False, "message": "Lỗi kết nối CSDL"}), 500

        cursor = conn.cursor()

        cursor = conn.cursor()
        
        class_id = request.args.get('class_id')
        cursor.execute("{CALL sp_LayDanhSachSV(?)}", (class_id))
        rows = cursor.fetchall()

        ds_sinh_vien = []
        for row in rows:
            ds_sinh_vien.append({
                "ma_sinh_vien": row[0],
                "ho_ten": row[1],
                "email": row[2],
                "trang_thai": row[3],
                "ten_lop_hanh_chinh": row[4],
                "ten_khoa": row[5],
                "so_dien_thoai": row[6],
                "gioi_tinh": row[7],
                "ngay_sinh": str(row[8]) if row[8] else None,
                "dia_chi": row[9],
                "du_lieu_khuon_mat": row[10]
            })

        return jsonify({"success": True, "data": ds_sinh_vien})

    except pyodbc.Error as e:
        return jsonify({"success": False, "message": str(e)}), 500
    except Exception as e:
        return jsonify({"success": False, "message": f"Lỗi máy chủ: {e}"}), 500
    finally:
        if conn:
            conn.close()


@quanlysinhvien_bp.route('/sinhvien/<string:ma_sv>', methods=['GET'])
@require_admin
# lấy chi tiết sinh viên
def handle_get_student_detail(ma_sv):
    conn = None
    try:
        conn = get_db_connection()
        if conn is None:
            return jsonify({"success": False, "message": "Lỗi kết nối CSDL"}), 500

        cursor = conn.cursor()

        cursor.execute("{CALL sp_LayChiTietSV(?)}", (ma_sv))
        row = cursor.fetchone()

        if not row:
            return jsonify({"success": False, "message": "Không tìm thấy sinh viên"}), 404

        sinh_vien_detail = {
            "ma_sinh_vien": row[0],
            "ma_lop_hanh_chinh": row[1],
            "ngay_sinh": row[2].strftime('%Y-%m-%d') if row[2] else None,
            "dia_chi": row[3],
            "gioi_tinh": row[4],
            "ma_nguoi_dung": row[5],
            "ho_ten": row[6],
            "email": row[7],
            "so_dien_thoai": row[8],
            "trang_thai": row[9],
            "ten_lop_hanh_chinh": row[10]
        }

        return jsonify({"success": True, "data": sinh_vien_detail})

    except pyodbc.Error as e:
        return jsonify({"success": False, "message": str(e)}), 500
    except Exception as e:
        return jsonify({"success": False, "message": f"Lỗi máy chủ: {e}"}), 500
    finally:
        if conn:
            conn.close()


@quanlysinhvien_bp.route('/admin/sinhvien/<string:ma_nguoi_dung>', methods=['PUT'])
@require_admin
# cập nhật thông tin sinh viên
def handle_admin_update_student(ma_nguoi_dung):
    data = request.get_json()
    ma_sv = data.get('ma_sinh_vien')

    if not ma_sv:
        return jsonify({"success": False, "message": "Thiếu Mã Sinh Viên (ma_sv)"}), 400

    conn = None
    try:
        conn = get_db_connection()
        if conn is None:
            return jsonify({"success": False, "message": "Lỗi kết nối CSDL"}), 500

        cursor = conn.cursor()
        cursor.execute(
            "{CALL sp_Admin_SuaThongTinSinhVien(?, ?, ?, ?, ?, ?, ?, ?, ?, ?)}",
            (
                ma_sv,
                ma_nguoi_dung,
                data.get('ho_ten'),
                data.get('email'),
                data.get('so_dien_thoai'),
                data.get('trang_thai'),
                data.get('ngay_sinh'),
                data.get('dia_chi'),
                data.get('gioi_tinh'),
                data.get('ma_lop_hanh_chinh')
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


@quanlysinhvien_bp.route('/sinhvien/<string:ma_sv>', methods=['DELETE'])
@require_admin
# xóa sinh viên
def handle_delete_student(ma_sv):
    conn = None
    try:
        conn = get_db_connection()
        if conn is None:
            return jsonify({"success": False, "message": "Lỗi kết nối CSDL"}), 500

        cursor = conn.cursor()

        cursor.execute("{CALL sp_XoaSinhVien(?)}", (ma_sv))
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
