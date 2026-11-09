from flask import Blueprint, request, jsonify
from app.core.KetNoiDB import get_db_connection
from app.core.XacThuc.PhanQuyen import require_giangvien
import pyodbc
import openpyxl
import io
from flask import send_file
from openpyxl.styles import Font

baocaogiangvien_bp = Blueprint('baocaogiangvien_bp', __name__)


@baocaogiangvien_bp.route('/giangvien/baocao/chuyen-can-sinh-vien/<string:ma_lhp>', methods=['GET'])
@require_giangvien
# lấy báo cáo chuyên cần sinh viên
def handle_get_report_9_chuyen_can_sinh_vien(ma_lhp):
    conn = None
    try:
        conn = get_db_connection()
        if conn is None:
            return jsonify({"success": False, "message": "Loi ket noi CSDL"}), 500

        cursor = conn.cursor()
        cursor.execute("{CALL sp_BaoCaoGV_ChuyenCanTungSV(?)}", (ma_lhp))
        rows = cursor.fetchall()

        report_data = []
        for row in rows:
            report_data.append({
                "ma_sinh_vien": row[0],
                "ho_ten": row[1],
                "tong_buoi_hoc": row[2],
                "so_buoi_co_mat": row[3],
                "so_buoi_vang": row[4],
                "ty_le_chuyen_can": round(row[5], 2)
            })

        return jsonify({"success": True, "data": report_data})

    except pyodbc.Error as e:
        return jsonify({"success": False, "message": str(e)}), 500
    except Exception as e:
        return jsonify({"success": False, "message": f"Loi may chu: {e}"}), 500
    finally:
        if conn:
            conn.close()


@baocaogiangvien_bp.route('/giangvien/baocao/chuyen-can-sinh-vien/<string:ma_lhp>/export', methods=['GET'])
@require_giangvien
# xuất báo cáo chuyên cần sinh viên
def handle_export_report_9_chuyen_can_sinh_vien(ma_lhp):
    conn = None
    try:
        conn = get_db_connection()
        if conn is None:
            return jsonify({"success": False, "message": "Loi ket noi CSDL"}), 500

        cursor = conn.cursor()
        cursor.execute("{CALL sp_BaoCaoGV_ChuyenCanTungSV(?)}", (ma_lhp))
        rows = cursor.fetchall()

        cursor.execute("{CALL sp_LayTenMonHocLHP(?)}", (ma_lhp))
        mon_hoc_info = cursor.fetchone()
        ten_mon_hoc = mon_hoc_info[0] if mon_hoc_info else ma_lhp

        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "ChuyenCan_SV"

        headers = [
            "Ma Sinh Vien", "Ho Ten", "Tong Buoi Hoc",
            "So Buoi Co Mat", "So Buoi Vang", "Ty Le Chuyen Can (%)"
        ]
        ws.append(headers)

        for cell in ws[1]:
            cell.font = Font(bold=True)

        for row in rows:
            formatted_row = list(row)
            formatted_row[5] = round(formatted_row[5], 2)  # Làm tròn tỷ lệ
            ws.append(formatted_row)

        stream = io.BytesIO()
        wb.save(stream)
        stream.seek(0)

        return send_file(
            stream,
            as_attachment=True,
            download_name=f'BaoCao_ChuyenCan_{ten_mon_hoc}_{ma_lhp}.xlsx',
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )

    except pyodbc.Error as e:
        return jsonify({"success": False, "message": str(e)}), 500
    except Exception as e:
        return jsonify({"success": False, "message": f"Loi may chu: {e}"}), 500
    finally:
        if conn:
            conn.close()


@baocaogiangvien_bp.route('/giangvien/baocao/danh-sach-diem-danh-buoi-hoc/<string:ma_lhp>', methods=['GET'])
@require_giangvien
# lấy danh sách điểm danh buổi học
def handle_get_report_10_danh_sach_diem_danh_buoi_hoc(ma_lhp):
    conn = None
    try:
        conn = get_db_connection()
        if conn is None:
            return jsonify({"success": False, "message": "Loi ket noi CSDL"}), 500

        cursor = conn.cursor()
        cursor.execute("{CALL sp_BaoCaoGV_DanhSachDiemDanhBuoiHoc(?)}", (ma_lhp))
        rows = cursor.fetchall()

        report_data = []
        for row in rows:
            report_data.append({
                "ma_buoi_hoc": row[0],
                "ngay_hoc": row[1].strftime("%d/%m/%Y") if row[1] else "",
                "phong_hoc": row[2],
                "ma_sinh_vien": row[3],
                "ho_ten": row[4],
                "trang_thai_diem_danh": row[5],
                "thoi_gian_diem_danh": row[6].strftime("%H:%M:%S") if row[6] else "",
                "phuong_thuc": row[7]
            })

        return jsonify({"success": True, "data": report_data})

    except pyodbc.Error as e:
        return jsonify({"success": False, "message": str(e)}), 500
    except Exception as e:
        return jsonify({"success": False, "message": f"Loi may chu: {e}"}), 500
    finally:
        if conn:
            conn.close()


@baocaogiangvien_bp.route('/giangvien/baocao/danh-sach-diem-danh-buoi-hoc/<string:ma_lhp>/export', methods=['GET'])
@require_giangvien
# xuất danh sách điểm danh buổi học
def handle_export_report_10_danh_sach_diem_danh_buoi_hoc(ma_lhp):
    conn = None
    try:
        conn = get_db_connection()
        if conn is None:
            return jsonify({"success": False, "message": "Loi ket noi CSDL"}), 500

        cursor = conn.cursor()
        cursor.execute("{CALL sp_BaoCaoGV_DanhSachDiemDanhBuoiHoc(?)}", (ma_lhp))
        rows = cursor.fetchall()

        # Dùng Procedure lấy tên môn học
        cursor.execute("{CALL sp_LayTenMonHocLHP(?)}", (ma_lhp))
        mon_hoc_info = cursor.fetchone()
        ten_mon_hoc = mon_hoc_info[0] if mon_hoc_info else ma_lhp

        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "DS_DiemDanh_BuoiHoc"

        headers = [
            "Ma Buoi Hoc", "Ngay Hoc", "Phong Hoc", "Ma Sinh Vien",
            "Ho Ten", "Trang Thai", "Thoi Gian Diem Danh", "Phuong Thuc"
        ]
        ws.append(headers)

        for cell in ws[1]:
            cell.font = Font(bold=True)

        for row in rows:
            formatted_row = [
                row[0],
                row[1].strftime("%d/%m/%Y") if row[1] else "",
                row[2] or "",
                row[3],
                row[4],
                row[5],
                row[6].strftime("%H:%M:%S") if row[6] else "",
                row[7] or ""
            ]
            ws.append(formatted_row)

        stream = io.BytesIO()
        wb.save(stream)
        stream.seek(0)

        return send_file(
            stream,
            as_attachment=True,
            download_name=f'BaoCao_DanhSach_DiemDanh_{ten_mon_hoc}_{ma_lhp}.xlsx',
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )

    except pyodbc.Error as e:
        return jsonify({"success": False, "message": str(e)}), 500
    except Exception as e:
        return jsonify({"success": False, "message": f"Loi may chu: {e}"}), 500
    finally:
        if conn:
            conn.close()


@baocaogiangvien_bp.route('/giangvien/baocao/xu-huong-chuyen-can/<string:ma_lhp>', methods=['GET'])
@require_giangvien
# lấy xu hướng chuyên cần
def handle_get_report_11_xu_huong_chuyen_can(ma_lhp):
    conn = None
    try:
        conn = get_db_connection()
        if conn is None:
            return jsonify({"success": False, "message": "Loi ket noi CSDL"}), 500

        cursor = conn.cursor()
        cursor.execute("{CALL sp_BaoCaoGV_XuHuongChuyenCan(?)}", (ma_lhp))
        rows = cursor.fetchall()

        labels = []
        ty_le_chuyen_can_data = []
        tong_luot_co_mat_data = []
        tong_luot_diem_danh_data = []

        for row in rows:
            tuan = row[0]
            thang = row[1]
            label = f"Tuan {tuan} - Thang {thang}"

            labels.append(label)
            ty_le_chuyen_can_data.append(round(row[5], 2))
            tong_luot_co_mat_data.append(row[4])
            tong_luot_diem_danh_data.append(row[3])

        chart_data = {
            "labels": labels,
            "datasets": [
                {
                    "label": "Ty le chuyen can (%)",
                    "data": ty_le_chuyen_can_data,
                    "type": "line",
                    "borderColor": "rgb(75, 192, 192)",
                    "backgroundColor": "rgba(75, 192, 192, 0.2)",
                    "yAxisID": "y"
                },
                {
                    "label": "So luot co mat",
                    "data": tong_luot_co_mat_data,
                    "type": "bar",
                    "backgroundColor": "rgba(54, 162, 235, 0.5)",
                    "yAxisID": "y1"
                },
                {
                    "label": "Tong luot diem danh",
                    "data": tong_luot_diem_danh_data,
                    "type": "bar",
                    "backgroundColor": "rgba(255, 99, 132, 0.5)",
                    "yAxisID": "y1"
                }
            ]
        }

        return jsonify({"success": True, "data": chart_data})

    except pyodbc.Error as e:
        return jsonify({"success": False, "message": str(e)}), 500
    except Exception as e:
        return jsonify({"success": False, "message": f"Loi may chu: {e}"}), 500
    finally:
        if conn:
            conn.close()


@baocaogiangvien_bp.route('/giangvien/baocao/sinh-vien-dac-biet/<string:ma_lhp>', methods=['GET'])
@require_giangvien
# lấy danh sách sinh viên đặc biệt
def handle_get_report_12_sinh_vien_dac_biet(ma_lhp):
    loai = request.args.get('loai', 'cao')

    conn = None
    try:
        conn = get_db_connection()
        if conn is None:
            return jsonify({"success": False, "message": "Loi ket noi CSDL"}), 500

        cursor = conn.cursor()
        cursor.execute("{CALL sp_BaoCaoGV_SinhVienDacBiet(?, ?)}", (ma_lhp, loai))
        rows = cursor.fetchall()

        report_data = []
        for row in rows:
            report_data.append({
                "ma_sinh_vien": row[0],
                "ho_ten": row[1],
                "tong_buoi_hoc": row[2],
                "so_buoi_co_mat": row[3],
                "so_buoi_vang": row[4],
                "ty_le_chuyen_can": round(row[5], 2),
                "xep_hang": row[6]
            })

        return jsonify({"success": True, "data": report_data})

    except pyodbc.Error as e:
        return jsonify({"success": False, "message": str(e)}), 500
    except Exception as e:
        return jsonify({"success": False, "message": f"Loi may chu: {e}"}), 500
    finally:
        if conn:
            conn.close()


@baocaogiangvien_bp.route('/giangvien/baocao/sinh-vien-dac-biet/<string:ma_lhp>/export', methods=['GET'])
@require_giangvien
# xuất danh sách sinh viên đặc biệt
def handle_export_report_12_sinh_vien_dac_biet(ma_lhp):
    loai = request.args.get('loai', 'cao')

    conn = None
    try:
        conn = get_db_connection()
        if conn is None:
            return jsonify({"success": False, "message": "Loi ket noi CSDL"}), 500

        cursor = conn.cursor()
        cursor.execute("{CALL sp_BaoCaoGV_SinhVienDacBiet(?, ?)}", (ma_lhp, loai))
        rows = cursor.fetchall()

        cursor.execute("{CALL sp_LayTenMonHocLHP(?)}", (ma_lhp))
        mon_hoc_info = cursor.fetchone()
        ten_mon_hoc = mon_hoc_info[0] if mon_hoc_info else ma_lhp

        wb = openpyxl.Workbook()
        ws = wb.active

        if loai == 'cao':
            ws.title = "SV_ChuyenCan_Cao"
            title = "DANH SACH SINH VIEN CHUYEN CAN CAO NHAT"
        else:
            ws.title = "SV_ChuyenCan_Thap"
            title = "DANH SACH SINH VIEN CHUYEN CAN THAP NHAT"

        ws.append([title])
        ws.append([])

        headers = [
            "Ma Sinh Vien", "Ho Ten", "Tong Buoi Hoc",
            "So Buoi Co Mat", "So Buoi Vang", "Ty Le Chuyen Can (%)", "Xep Hang"
        ]
        ws.append(headers)

        for cell in ws[1]:
            cell.font = Font(bold=True, size=14)
        for cell in ws[3]:
            cell.font = Font(bold=True)

        for row in rows:
            formatted_row = list(row)
            formatted_row[5] = round(formatted_row[5], 2)
            ws.append(formatted_row)

        stream = io.BytesIO()
        wb.save(stream)
        stream.seek(0)

        loai_file = "CaoNhat" if loai == 'cao' else "ThapNhat"
        return send_file(
            stream,
            as_attachment=True,
            download_name=f'BaoCao_SV_ChuyenCan_{loai_file}_{ten_mon_hoc}_{ma_lhp}.xlsx',
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )

    except pyodbc.Error as e:
        return jsonify({"success": False, "message": str(e)}), 500
    except Exception as e:
        return jsonify({"success": False, "message": f"Loi may chu: {e}"}), 500
    finally:
        if conn:
            conn.close()


@baocaogiangvien_bp.route('/giangvien/baocao/tong-hop-chuyen-can/<string:ma_gv>', methods=['GET'])
@require_giangvien
# lấy báo cáo tổng hợp chuyên cần
def handle_get_report_13_tong_hop_chuyen_can(ma_gv):
    conn = None
    try:
        conn = get_db_connection()
        if conn is None:
            return jsonify({"success": False, "message": "Loi ket noi CSDL"}), 500

        cursor = conn.cursor()
        cursor.execute("{CALL sp_BaoCaoGV_TongHopChuyenCan(?)}", (ma_gv))
        rows = cursor.fetchall()

        report_data = []
        for row in rows:
            report_data.append({
                "ma_lop_hoc_phan": row[0],
                "ten_mon_hoc": row[1],
                "hoc_ky": row[2],
                "nam_hoc": row[3],
                "tong_sinh_vien": row[4],
                "tong_buoi_hoc": row[5],
                "tong_luot_diem_danh": row[6],
                "tong_luot_co_mat": row[7],
                "ty_le_chuyen_can": round(row[8], 2)
            })

        return jsonify({"success": True, "data": report_data})

    except pyodbc.Error as e:
        return jsonify({"success": False, "message": str(e)}), 500
    except Exception as e:
        return jsonify({"success": False, "message": f"Loi may chu: {e}"}), 500
    finally:
        if conn:
            conn.close()


@baocaogiangvien_bp.route('/giangvien/baocao/tong-hop-chuyen-can/<string:ma_gv>/export', methods=['GET'])
@require_giangvien
# xuất báo cáo tổng hợp chuyên cần
def handle_export_report_13_tong_hop_chuyen_can(ma_gv):
    conn = None
    try:
        conn = get_db_connection()
        if conn is None:
            return jsonify({"success": False, "message": "Loi ket noi CSDL"}), 500

        cursor = conn.cursor()
        cursor.execute("{CALL sp_BaoCaoGV_TongHopChuyenCan(?)}", (ma_gv))
        rows = cursor.fetchall()

        # --- ĐÃ SỬA: Dùng Procedure mới để lấy tên giảng viên ---
        cursor.execute("{CALL sp_LayTenGiangVien(?)}", (ma_gv))
        gv_info = cursor.fetchone()
        ten_giang_vien = gv_info[0] if gv_info else ma_gv

        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "TongHop_ChuyenCan"

        ws.append([f"BAO CAO TONG HOP CHUYEN CAN - GIANG VIEN: {ten_giang_vien}"])
        ws.append([])

        headers = [
            "Ma Lop Hoc Phan", "Ten Mon Hoc", "Hoc Ky", "Nam Hoc",
            "Tong Sinh Vien", "Tong Buoi Hoc", "Tong Luot Diem Danh",
            "Tong Luot Co Mat", "Ty Le Chuyen Can (%)"
        ]
        ws.append(headers)

        for cell in ws[1]:
            cell.font = Font(bold=True, size=14)
        for cell in ws[3]:
            cell.font = Font(bold=True)

        for row in rows:
            formatted_row = list(row)
            formatted_row[8] = round(formatted_row[8], 2)
            ws.append(formatted_row)

        if rows:
            ws.append([])
            ws.append(["TONG KET:", "", "", "",
                       sum(row[4] for row in rows),
                       sum(row[5] for row in rows),
                       sum(row[6] for row in rows),
                       sum(row[7] for row in rows),
                       round(sum(row[8] for row in rows) / len(rows), 2)])

        stream = io.BytesIO()
        wb.save(stream)
        stream.seek(0)

        return send_file(
            stream,
            as_attachment=True,
            download_name=f'BaoCao_TongHop_ChuyenCan_{ten_giang_vien}_{ma_gv}.xlsx',
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )

    except pyodbc.Error as e:
        return jsonify({"success": False, "message": str(e)}), 500
    except Exception as e:
        return jsonify({"success": False, "message": f"Loi may chu: {e}"}), 500
    finally:
        if conn:
            conn.close()


@baocaogiangvien_bp.route('/giangvien/baocao/canh-bao-cam-thi/<string:ma_lhp>', methods=['GET'])
@require_giangvien
# lấy cảnh báo cấm thi
def handle_get_report_14_canh_bao_cam_thi(ma_lhp):
    conn = None
    try:
        conn = get_db_connection()
        if conn is None:
            return jsonify({"success": False, "message": "Loi ket noi CSDL"}), 500

        cursor = conn.cursor()
        cursor.execute("{CALL sp_BaoCaoGV_CanhBaoCamThi(?)}", (ma_lhp))
        rows = cursor.fetchall()

        report_data = []
        for row in rows:
            report_data.append({
                "ma_sinh_vien": row[0],
                "ho_ten": row[1],
                "tong_buoi_hoc": row[2],
                "so_buoi_vang": row[3],
                "ty_le_vang": round(row[4], 2),
                "muc_do_canh_bao": row[5]
            })

        return jsonify({"success": True, "data": report_data})

    except pyodbc.Error as e:
        return jsonify({"success": False, "message": str(e)}), 500
    except Exception as e:
        return jsonify({"success": False, "message": f"Loi may chu: {e}"}), 500
    finally:
        if conn:
            conn.close()


@baocaogiangvien_bp.route('/giangvien/baocao/canh-bao-cam-thi/<string:ma_lhp>/export', methods=['GET'])
@require_giangvien
# xuất cảnh báo cấm thi
def handle_export_report_14_canh_bao_cam_thi(ma_lhp):
    conn = None
    try:
        conn = get_db_connection()
        if conn is None:
            return jsonify({"success": False, "message": "Loi ket noi CSDL"}), 500

        cursor = conn.cursor()
        cursor.execute("{CALL sp_BaoCaoGV_CanhBaoCamThi(?)}", (ma_lhp))
        rows = cursor.fetchall()

        # Dùng Procedure lấy tên môn học
        cursor.execute("{CALL sp_LayTenMonHocLHP(?)}", (ma_lhp))
        mon_hoc_info = cursor.fetchone()
        ten_mon_hoc = mon_hoc_info[0] if mon_hoc_info else ma_lhp

        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "CanhBao_CamThi"

        ws.append([f"DANH SACH CANH BAO CAM THI - {ten_mon_hoc} ({ma_lhp})"])
        ws.append(["Luu y: Sinh vien co ty le vang tren 20% co nguy co bi cam thi"])
        ws.append([])

        headers = [
            "Ma Sinh Vien", "Ho Ten", "Tong Buoi Hoc",
            "So Buoi Vang", "Ty Le Vang (%)", "Muc Do Canh Bao"
        ]
        ws.append(headers)

        for cell in ws[1]:
            cell.font = Font(bold=True, size=14)
        for cell in ws[2]:
            cell.font = Font(color="FF0000", italic=True)
        for cell in ws[4]:
            cell.font = Font(bold=True)

        for row in rows:
            formatted_row = list(row)
            formatted_row[4] = round(formatted_row[4], 2)
            ws.append(formatted_row)

        for row_idx, row in enumerate(rows, start=5):
            ty_le_vang = row[4]
            if ty_le_vang > 20:
                for col in range(1, 7):
                    ws.cell(row=row_idx, column=col).fill = openpyxl.styles.PatternFill(start_color="FFB6C1",
                                                                                        end_color="FFB6C1",
                                                                                        fill_type="solid")

        stream = io.BytesIO()
        wb.save(stream)
        stream.seek(0)

        return send_file(
            stream,
            as_attachment=True,
            download_name=f'BaoCao_CanhBao_CamThi_{ten_mon_hoc}_{ma_lhp}.xlsx',
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )

    except pyodbc.Error as e:
        return jsonify({"success": False, "message": str(e)}), 500
    except Exception as e:
        return jsonify({"success": False, "message": f"Loi may chu: {e}"}), 500
    finally:
        if conn:
            conn.close()
