from flask import Blueprint, jsonify, request
from app.core.KetNoiDB import get_db_connection
from app.core.XacThuc.PhanQuyen import require_sinhvien
import pyodbc
import openpyxl
import io
from flask import send_file
from openpyxl.styles import Font

chucnangsinhvien_bp = Blueprint('chucnangsinhvien_bp', __name__)


@chucnangsinhvien_bp.route('/sinhvien/lich-su-diem-danh/<string:ma_sv>', methods=['GET'])
@require_sinhvien
def handle_get_report_15_lich_su_diem_danh(ma_sv):
    conn = None
    try:
        conn = get_db_connection()
        if conn is None:
            return jsonify({"success": False, "message": "Loi ket noi CSDL"}), 500

        cursor = conn.cursor()
        cursor.execute("{CALL sp_BaoCaoSV_LichSuDiemDanh(?)}", (ma_sv))
        rows = cursor.fetchall()

        report_data = []
        for row in rows:
            report_data.append({
                "ma_buoi_hoc": row[0],
                "ten_mon_hoc": row[1],
                "ma_lop_hoc_phan": row[2],
                "ngay_hoc": row[3].strftime("%d/%m/%Y") if row[3] else "",
                "trang_thai_diem_danh": row[4],
                "thoi_gian_diem_danh": row[5].strftime("%H:%M:%S") if row[5] else "",
                "phuong_thuc": row[6]
            })

        return jsonify({"success": True, "data": report_data})

    except pyodbc.Error as e:
        return jsonify({"success": False, "message": str(e)}), 500
    except Exception as e:
        return jsonify({"success": False, "message": f"Loi may chu: {e}"}), 500
    finally:
        if conn:
            conn.close()


@chucnangsinhvien_bp.route('/sinhvien/lich-su-diem-danh/<string:ma_sv>/export', methods=['GET'])
@require_sinhvien
def handle_export_report_15_lich_su_diem_danh(ma_sv):
    conn = None
    try:
        conn = get_db_connection()
        if conn is None:
            return jsonify({"success": False, "message": "Loi ket noi CSDL"}), 500

        cursor = conn.cursor()
        cursor.execute("{CALL sp_BaoCaoSV_LichSuDiemDanh(?)}", (ma_sv))
        rows = cursor.fetchall()

        cursor.execute("{CALL sp_LayThongTinSinhVien(?)}", (ma_sv))
        sv_info = cursor.fetchone()
        ten_sinh_vien = sv_info[0] if sv_info else ma_sv

        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "LichSu_DiemDanh"

        ws.append([f"LICH SU DIEM DANH - SINH VIEN: {ten_sinh_vien} ({ma_sv})"])
        ws.append([])

        headers = [
            "Ma Buoi Hoc", "Ten Mon Hoc", "Ma Lop Hoc Phan",
            "Ngay Hoc", "Trang Thai", "Thoi Gian Diem Danh", "Phuong Thuc"
        ]
        ws.append(headers)

        for cell in ws[1]:
            cell.font = Font(bold=True, size=14)
        for cell in ws[3]:
            cell.font = Font(bold=True)

        for row in rows:
            formatted_row = [
                row[0],
                row[1],
                row[2],
                row[3].strftime("%d/%m/%Y") if row[3] else "",
                row[4],
                row[5].strftime("%H:%M:%S") if row[5] else "",
                row[6] or ""
            ]
            ws.append(formatted_row)

        stream = io.BytesIO()
        wb.save(stream)
        stream.seek(0)

        return send_file(
            stream,
            as_attachment=True,
            download_name=f'LichSu_DiemDanh_{ten_sinh_vien}_{ma_sv}.xlsx',
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )

    except pyodbc.Error as e:
        return jsonify({"success": False, "message": str(e)}), 500
    except Exception as e:
        return jsonify({"success": False, "message": f"Loi may chu: {e}"}), 500
    finally:
        if conn:
            conn.close()


@chucnangsinhvien_bp.route('/sinhvien/thong-ke-chuyen-can/<string:ma_sv>', methods=['GET'])
@require_sinhvien
def handle_get_report_16_thong_ke_chuyen_can(ma_sv):
    conn = None
    try:
        conn = get_db_connection()
        if conn is None:
            return jsonify({"success": False, "message": "Loi ket noi CSDL"}), 500

        cursor = conn.cursor()
        cursor.execute("{CALL sp_BaoCaoSV_ThongKeChuyenCan(?)}", (ma_sv))
        rows = cursor.fetchall()

        report_data = []
        for row in rows:
            report_data.append({
                "ma_lop_hoc_phan": row[0],
                "ten_mon_hoc": row[1],
                "hoc_ky": row[2],
                "nam_hoc": row[3],
                "tong_buoi_hoc": row[4],
                "so_buoi_co_mat": row[5],
                "so_buoi_vang": row[6],
                "ty_le_chuyen_can": round(row[7], 2)
            })

        return jsonify({"success": True, "data": report_data})

    except pyodbc.Error as e:
        return jsonify({"success": False, "message": str(e)}), 500
    except Exception as e:
        return jsonify({"success": False, "message": f"Loi may chu: {e}"}), 500
    finally:
        if conn:
            conn.close()


@chucnangsinhvien_bp.route('/sinhvien/thong-ke-chuyen-can/<string:ma_sv>/export', methods=['GET'])
@require_sinhvien
def handle_export_report_16_thong_ke_chuyen_can(ma_sv):
    conn = None
    try:
        conn = get_db_connection()
        if conn is None:
            return jsonify({"success": False, "message": "Loi ket noi CSDL"}), 500

        cursor = conn.cursor()
        cursor.execute("{CALL sp_BaoCaoSV_ThongKeChuyenCan(?)}", (ma_sv))
        rows = cursor.fetchall()

        cursor.execute("{CALL sp_LayThongTinSinhVien(?)}", (ma_sv))
        sv_info = cursor.fetchone()
        ten_sinh_vien = sv_info[0] if sv_info else ma_sv

        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "ThongKe_ChuyenCan"

        ws.append([f"THONG KE CHUYEN CAN - SINH VIEN: {ten_sinh_vien} ({ma_sv})"])
        ws.append([])

        headers = [
            "Ma Lop Hoc Phan", "Ten Mon Hoc", "Hoc Ky", "Nam Hoc",
            "Tong Buoi Hoc", "So Buoi Co Mat", "So Buoi Vang", "Ty Le Chuyen Can (%)"
        ]
        ws.append(headers)

        for cell in ws[1]:
            cell.font = Font(bold=True, size=14)
        for cell in ws[3]:
            cell.font = Font(bold=True)

        for row in rows:
            formatted_row = list(row)
            formatted_row[7] = round(formatted_row[7], 2)
            ws.append(formatted_row)

        if rows:
            ws.append([])
            tong_ty_le = sum(row[7] for row in rows)
            trung_binh = round(tong_ty_le / len(rows), 2) if rows else 0
            ws.append(["TRUNG BINH CHUYEN CAN:", "", "", "", "", "", "", trung_binh])

        stream = io.BytesIO()
        wb.save(stream)
        stream.seek(0)

        return send_file(
            stream,
            as_attachment=True,
            download_name=f'ThongKe_ChuyenCan_{ten_sinh_vien}_{ma_sv}.xlsx',
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )

    except pyodbc.Error as e:
        return jsonify({"success": False, "message": str(e)}), 500
    except Exception as e:
        return jsonify({"success": False, "message": f"Loi may chu: {e}"}), 500
    finally:
        if conn:
            conn.close()


@chucnangsinhvien_bp.route('/sinhvien/canh-bao-chuyen-can/<string:ma_sv>', methods=['GET'])
@require_sinhvien
def handle_get_report_17_canh_bao_chuyen_can(ma_sv):
    conn = None
    try:
        conn = get_db_connection()
        if conn is None:
            return jsonify({"success": False, "message": "Loi ket noi CSDL"}), 500

        cursor = conn.cursor()
        cursor.execute("{CALL sp_BaoCaoSV_CanhBaoChuyenCan(?)}", (ma_sv))
        rows = cursor.fetchall()

        canh_bao_data = []
        co_canh_bao_do = False
        co_canh_bao_vang = False

        for row in rows:
            ty_le_vang_tong = row[8]
            ty_le_vang_kp = row[9]
            muc_do_canh_bao = row[11]

            canh_bao_info = {
                "ma_lop_hoc_phan": row[0],
                "ten_mon_hoc": row[1],
                "tong_buoi_hoc": row[2],
                "so_buoi_co_mat": row[3],
                "so_buoi_vang_cp": row[4],
                "so_buoi_vang_kp": row[5],
                "so_buoi_vang_tong": row[6],
                "ty_le_chuyen_can": round(row[7], 2),
                "ty_le_vang_tong": round(ty_le_vang_tong, 2),
                "ty_le_vang_khong_phep": round(ty_le_vang_kp, 2),
                "thong_bao": row[10],
                "muc_do_canh_bao": muc_do_canh_bao
            }

            canh_bao_data.append(canh_bao_info)

            if muc_do_canh_bao == 3:
                co_canh_bao_do = True
            elif muc_do_canh_bao == 2:
                co_canh_bao_vang = True

        return jsonify({
            "success": True,
            "co_canh_bao_do": co_canh_bao_do,
            "co_canh_bao_vang": co_canh_bao_vang,
            "so_lop_canh_bao": len(canh_bao_data),
            "data": canh_bao_data
        })

    except pyodbc.Error as e:
        return jsonify({"success": False, "message": str(e)}), 500
    except Exception as e:
        return jsonify({"success": False, "message": f"Loi may chu: {e}"}), 500
    finally:
        if conn:
            conn.close()


@chucnangsinhvien_bp.route('/sinhvien/trang-thai-canh-bao/<string:ma_sv>', methods=['GET'])
@require_sinhvien
def handle_get_trang_thai_canh_bao_tong(ma_sv):
    conn = None
    try:
        conn = get_db_connection()
        if conn is None:
            return jsonify({"success": False, "message": "Loi ket noi CSDL"}), 500

        cursor = conn.cursor()
        cursor.execute("{CALL sp_BaoCaoSV_TrangThaiCanhBaoTong(?)}", (ma_sv))
        row = cursor.fetchone()

        if row is None or row[0] is None:
            return jsonify({
                "success": True,
                "muc_do": 0,
                "so_lop_canh_bao": 0,
                "so_lop_do": 0,
                "so_lop_vang": 0,
                "danh_sach_lop": "",
                "message": ""
            })

        muc_do_tong = row[0]
        so_lop_canh_bao = row[1]
        so_lop_do = row[2]
        so_lop_vang = row[3]
        danh_sach_lop = row[4] if row[4] else ""

        message = ""
        if muc_do_tong == 3:
            message = f"Tỉ lệ vắng của bạn đã vượt mức quy định (>30%). Bạn có nguy cơ bị cấm thi trong lớp: {danh_sach_lop}"
        elif muc_do_tong == 2:
            message = f"Tỉ lệ vắng của bạn sắp vượt mức quy định (20-30%). Vui lòng kiểm tra lại lớp: {danh_sach_lop}"

        return jsonify({
            "success": True,
            "muc_do": muc_do_tong,
            "so_lop_canh_bao": so_lop_canh_bao,
            "so_lop_do": so_lop_do,
            "so_lop_vang": so_lop_vang,
            "danh_sach_lop": danh_sach_lop,
            "message": message
        })

    except pyodbc.Error as e:
        return jsonify({"success": False, "message": str(e)}), 500
    except Exception as e:
        return jsonify({"success": False, "message": f"Loi may chu: {e}"}), 500
    finally:
        if conn:
            conn.close()


@chucnangsinhvien_bp.route('/sinhvien/buoi-hoc/<string:ma_sv>', methods=['GET'])
@require_sinhvien
def handle_get_sessions_for_student(ma_sv):
    conn = None
    try:
        conn = get_db_connection()
        if conn is None:
            return jsonify({"success": False, "message": "Loi ket noi CSDL"}), 500

        cursor = conn.cursor()
        
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        cursor.execute(
            "{CALL sp_LayBuoiHocCuaSinhVien(?, ?, ?)}",
            (ma_sv, start_date, end_date)
        )
        rows = cursor.fetchall()

        ds_buoi_hoc = []
        for row in rows:
            ds_buoi_hoc.append({
                "ma_buoi_hoc": row[0],
                "ngay_hoc": row[1].strftime('%Y-%m-%d') if row[1] else None,
                "thoi_gian_bat_dau": str(row[2]) if row[2] else None,
                "thoi_gian_ket_thuc": str(row[3]) if row[3] else None,
                "phong_hoc": row[4],
                "trang_thai": row[5],
                "ma_lhp": row[6],
                "ten_mon_hoc": row[7],
                "ma_giang_vien": row[8],
                "ten_giang_vien": row[9] if row[9] else "Chưa phân công",
                "trang_thai_diem_danh": row[10] if len(row) > 10 else "Chưa điểm danh"
            })

        return jsonify({"success": True, "data": ds_buoi_hoc})

    except pyodbc.Error as e:
        return jsonify({"success": False, "message": str(e)}), 500
    except Exception as e:
        return jsonify({"success": False, "message": f"Loi may chu: {e}"}), 500
    finally:
        if conn:
            conn.close()
