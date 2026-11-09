from flask import Blueprint, jsonify, request
from app.core.KetNoiDB import get_db_connection
from app.core.XacThuc.PhanQuyen import require_giangvien
import pyodbc

chucnanggiangvien_bp = Blueprint('chucnanggiangvien_bp', __name__)


@chucnanggiangvien_bp.route('/giangvien/lophocphan/<string:ma_gv>', methods=['GET'])
@require_giangvien
def handle_get_lecturer_classes(ma_gv):
    conn = None
    try:
        conn = get_db_connection()
        if conn is None:
            return jsonify({"success": False, "message": "Lỗi kết nối CSDL"}), 500

        cursor = conn.cursor()
        cursor.execute("{CALL sp_LayLopHocCuaGiangVien(?)}", (ma_gv))
        rows = cursor.fetchall()

        ds_lop_hoc_phan = []
        for row in rows:
            ds_lop_hoc_phan.append({
                "ma_lop_hoc_phan": row[0],
                "ten_mon_hoc": row[1],
                "hoc_ky": row[2],
                "nam_hoc": row[3]
            })

        return jsonify({"success": True, "data": ds_lop_hoc_phan})

    except pyodbc.Error as e:
        return jsonify({"success": False, "message": str(e)}), 500
    except Exception as e:
        return jsonify({"success": False, "message": f"Lỗi máy chủ: {e}"}), 500
    finally:
        if conn:
            conn.close()


@chucnanggiangvien_bp.route('/giangvien/lophocphan/<string:ma_lhp>/sinhvien', methods=['GET'])
@require_giangvien
def handle_get_students_of_class(ma_lhp):
    conn = None
    try:
        conn = get_db_connection()
        if conn is None:
            return jsonify({"success": False, "message": "Lỗi kết nối CSDL"}), 500

        cursor = conn.cursor()
        cursor.execute("{CALL sp_LayDanhSachSV_LHP(?)}", (ma_lhp))
        rows = cursor.fetchall()

        ds_sinh_vien = []
        for row in rows:
            ds_sinh_vien.append({
                "ma_sinh_vien": row[0],
                "ho_ten": row[1],
                "email": row[2],
                "trang_thai_dang_ky": row[3],
                "so_dien_thoai": row[4]
            })

        return jsonify({"success": True, "data": ds_sinh_vien})

    except pyodbc.Error as e:
        return jsonify({"success": False, "message": str(e)}), 500
    except Exception as e:
        return jsonify({"success": False, "message": f"Lỗi máy chủ: {e}"}), 500
    finally:
        if conn:
            conn.close()

@chucnanggiangvien_bp.route('/giangvien/<string:ma_gv>/lichday', methods=['GET'])
@require_giangvien
def handle_get_teacher_schedule(ma_gv):
    conn = None
    try:
        from_date = request.args.get('from_date')
        to_date = request.args.get('to_date')

        if not from_date: from_date = None
        if not to_date: to_date = None

        conn = get_db_connection()
        if conn is None:
            return jsonify({"success": False, "message": "Lỗi kết nối CSDL"}), 500

        cursor = conn.cursor()
        cursor.execute("{CALL sp_LayLichDayGiangVien(?, ?, ?)}", (ma_gv, from_date, to_date))
        rows = cursor.fetchall()

        lich_day = []
        for row in rows:
            lich_day.append({
                "ma_buoi_hoc": row[0],
                "ma_lhp": row[1],        
                "ten_mon_hoc": row[2],     
                "ngay_hoc": str(row[3]),   
                "phong_hoc": row[4],       
                "thoi_gian_bat_dau": str(row[5]) if row[5] else "", 
                "thoi_gian_ket_thuc": str(row[6]) if row[6] else "", 
                
                "loai_buoi_hoc": row[7],
                "ghi_chu": row[8]
            })

        return jsonify({"success": True, "data": lich_day})

    except pyodbc.Error as e:
        return jsonify({"success": False, "message": str(e)}), 500
    except Exception as e:
        return jsonify({"success": False, "message": f"Lỗi máy chủ: {e}"}), 500
    finally:
        if conn:
            conn.close()