from flask import Blueprint, request, jsonify
from app.core.KetNoiDB import get_db_connection
from app.core.XacThuc.PhanQuyen import require_admin
import pyodbc
import io
import openpyxl
from flask import send_file
from openpyxl.styles import Font

baocaoadmin_bp = Blueprint('baocaoadmin_bp', __name__)


@baocaoadmin_bp.route('/baocao/tonghop-chuyen-can', methods=['GET'])
@require_admin
# lấy báo cáo tổng hợp chuyên cần
def handle_get_report_1():
    hocky = request.args.get('hocky')
    namhoc = request.args.get('namhoc')

    if not hocky or not namhoc:
        return jsonify({"success": False, "message": "Thiếu thông tin Học kỳ hoặc Năm học"}), 400

    conn = None
    try:
        conn = get_db_connection()
        if conn is None:
            return jsonify({"success": False, "message": "Lỗi kết nối CSDL"}), 500

        cursor = conn.cursor()
        cursor.execute("{CALL sp_BaoCao_TongHopChuyenCan(?, ?)}", (hocky, namhoc))
        rows = cursor.fetchall()

        report_data = []
        for row in rows:
            report_data.append({
                "ma_lop_hoc_phan": row[0],
                "ten_mon_hoc": row[1],
                "ten_giang_vien": row[2],
                "tong_so_sinh_vien": row[3],
                "so_buoi_da_to_chuc": row[4],
                "ty_le_chuyen_can_trung_binh": row[5]
            })

        return jsonify({"success": True, "data": report_data})

    except pyodbc.Error as e:
        return jsonify({"success": False, "message": str(e)}), 500
    except Exception as e:
        return jsonify({"success": False, "message": f"Lỗi máy chủ: {e}"}), 500
    finally:
        if conn:
            conn.close()


@baocaoadmin_bp.route('/baocao/tonghop-chuyen-can/export', methods=['GET'])
@require_admin
# xuất báo cáo tổng hợp chuyên cần
def handle_export_report_1():
    hocky = request.args.get('hocky')
    namhoc = request.args.get('namhoc')

    if not hocky or not namhoc:
        return jsonify({"success": False, "message": "Thiếu thông tin Học kỳ hoặc Năm học"}), 400

    conn = None
    try:
        conn = get_db_connection()
        if conn is None:
            return jsonify({"success": False, "message": "Lỗi kết nối CSDL"}), 500

        cursor = conn.cursor()
        cursor.execute("{CALL sp_BaoCao_TongHopChuyenCan(?, ?)}", (hocky, namhoc))
        rows = cursor.fetchall()

        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = f"BaoCao_{hocky}_{namhoc}"

        headers = [
            "Mã Lớp Học Phần", "Tên Môn Học", "Tên Giảng Viên",
            "Tổng Số SV", "Số Buổi Đã Tổ Chức", "Tỷ Lệ Chuyên Cần (%)"
        ]
        ws.append(headers)

        for cell in ws[1]:
            cell.font = Font(bold=True)

        for row in rows:
            ws.append(list(row))

        stream = io.BytesIO()
        wb.save(stream)
        stream.seek(0)

        return send_file(
            stream,
            as_attachment=True,
            download_name=f'BaoCaoChuyenCan_{hocky}_{namhoc}.xlsx',
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )

    except pyodbc.Error as e:
        return jsonify({"success": False, "message": str(e)}), 500
    except Exception as e:
        return jsonify({"success": False, "message": f"Lỗi máy chủ: {e}"}), 500
    finally:
        if conn:
            conn.close()


@baocaoadmin_bp.route('/baocao/chuyencan-giangvien', methods=['GET'])
@require_admin
# lấy báo cáo chuyên cần theo giảng viên
def handle_get_report_2_gv():
    conn = None
    try:
        conn = get_db_connection()
        if conn is None:
            return jsonify({"success": False, "message": "Lỗi kết nối CSDL"}), 500

        cursor = conn.cursor()
        cursor.execute("{CALL sp_BaoCao_ChuyenCanTheoGV}")
        rows = cursor.fetchall()

        report_data = []
        for row in rows:
            report_data.append({
                "ma_giang_vien": row[0],
                "ten_giang_vien": row[1],
                "ty_le_chuyen_can_trung_binh": row[2]
            })

        return jsonify({"success": True, "data": report_data})

    except pyodbc.Error as e:
        return jsonify({"success": False, "message": str(e)}), 500
    except Exception as e:
        return jsonify({"success": False, "message": f"Lỗi máy chủ: {e}"}), 500
    finally:
        if conn:
            conn.close()


@baocaoadmin_bp.route('/baocao/chuyencan-giangvien/export', methods=['GET'])
@require_admin
# xuất báo cáo chuyên cần theo giảng viên
def handle_export_report_2_gv():
    conn = None
    try:
        conn = get_db_connection()
        if conn is None:
            return jsonify({"success": False, "message": "Lỗi kết nối CSDL"}), 500

        cursor = conn.cursor()
        cursor.execute("{CALL sp_BaoCao_ChuyenCanTheoGV}")
        rows = cursor.fetchall()

        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "BaoCaoTheoGV"

        headers = [
            "Mã Giảng Viên", "Tên Giảng Viên", "Tỷ Lệ Chuyên Cần Trung Bình (%)"
        ]
        ws.append(headers)

        for cell in ws[1]:
            cell.font = Font(bold=True)

        for row in rows:
            ws.append(list(row))

        stream = io.BytesIO()
        wb.save(stream)
        stream.seek(0)

        return send_file(
            stream,
            as_attachment=True,
            download_name='BaoCaoChuyenCanTheoGiangVien.xlsx',
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )

    except pyodbc.Error as e:
        return jsonify({"success": False, "message": str(e)}), 500
    except Exception as e:
        return jsonify({"success": False, "message": f"Lỗi máy chủ: {e}"}), 500
    finally:
        if conn:
            conn.close()


@baocaoadmin_bp.route('/baocao/sinhvien-vang-qua-muc', methods=['GET'])
@require_admin
# lấy báo cáo sinh viên vắng quá mức
def handle_get_report_3_sv_vang_qua_muc():
    conn = None
    try:
        conn = get_db_connection()
        if conn is None:
            return jsonify({"success": False, "message": "Loi ket noi CSDL"}), 500

        cursor = conn.cursor()
        cursor.execute("{CALL sp_BaoCao_DSVangQuaMuc}")
        rows = cursor.fetchall()

        report_data = []
        for row in rows:
            report_data.append({
                "ma_sinh_vien": row[0],
                "ho_ten": row[1],
                "ten_lop_hanh_chinh": row[2],
                "ten_mon_hoc": row[3],
                "so_buoi_vang": row[4],
                "ty_le_vang": row[5],
                "trang_thai": row[6]
            })

        return jsonify({"success": True, "data": report_data})

    except pyodbc.Error as e:
        return jsonify({"success": False, "message": str(e)}), 500
    except Exception as e:
        return jsonify({"success": False, "message": f"Loi may chu: {e}"}), 500
    finally:
        if conn:
            conn.close()


@baocaoadmin_bp.route('/baocao/sinhvien-vang-qua-muc/export', methods=['GET'])
@require_admin
# xuất báo cáo sinh viên vắng quá mức
def handle_export_report_3_sv_vang_qua_muc():
    conn = None
    try:
        conn = get_db_connection()
        if conn is None:
            return jsonify({"success": False, "message": "Loi ket noi CSDL"}), 500

        cursor = conn.cursor()
        cursor.execute("{CALL sp_BaoCao_DSVangQuaMuc}")
        rows = cursor.fetchall()

        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "BaoCao_SV_Vang_Qua_Muc"

        headers = [
            "Ma Sinh Vien", "Ho Ten", "Ten Lop Hanh Chinh",
            "Ten Mon Hoc", "So Buoi Vang", "Ty Le Vang (%)", "Trang Thai"
        ]
        ws.append(headers)

        for cell in ws[1]:
            cell.font = Font(bold=True)

        for row in rows:
            ws.append(list(row))

        stream = io.BytesIO()
        wb.save(stream)
        stream.seek(0)

        return send_file(
            stream,
            as_attachment=True,
            download_name='BaoCao_SV_Vang_Qua_Muc.xlsx',
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )

    except pyodbc.Error as e:
        return jsonify({"success": False, "message": str(e)}), 500
    except Exception as e:
        return jsonify({"success": False, "message": f"Loi may chu: {e}"}), 500
    finally:
        if conn:
            conn.close()


@baocaoadmin_bp.route('/baocao/thong-ke-buoi-hoc-diem-danh', methods=['GET'])
@require_admin
# lấy thống kê buổi học điểm danh
def handle_get_report_4_thong_ke_buoi_hoc_diem_danh():
    conn = None
    try:
        conn = get_db_connection()
        if conn is None:
            return jsonify({"success": False, "message": "Loi ket noi CSDL"}), 500

        cursor = conn.cursor()
        cursor.execute("{CALL sp_BaoCao_ThongKeBuoiHocDiemDanh}")
        row = cursor.fetchone()

        if row:
            thong_ke = {
                "tong_so_buoi_hoc": row[0],
                "tong_luot_diem_danh": row[1],
                "tong_luot_co_mat": row[2],
                "tong_luot_vang_co_phep": row[3],
                "tong_luot_vang_khong_phep": row[4]
            }
            return jsonify({"success": True, "data": thong_ke})
        else:
            return jsonify({"success": False, "message": "Khong co du lieu"}), 404

    except pyodbc.Error as e:
        return jsonify({"success": False, "message": str(e)}), 500
    except Exception as e:
        return jsonify({"success": False, "message": f"Loi may chu: {e}"}), 500
    finally:
        if conn:
            conn.close()


@baocaoadmin_bp.route('/baocao/thong-ke-buoi-hoc-diem-danh/export', methods=['GET'])
@require_admin
# xuất thống kê buổi học điểm danh
def handle_export_report_4_thong_ke_buoi_hoc_diem_danh():
    conn = None
    try:
        conn = get_db_connection()
        if conn is None:
            return jsonify({"success": False, "message": "Loi ket noi CSDL"}), 500

        cursor = conn.cursor()
        cursor.execute("{CALL sp_BaoCao_ThongKeBuoiHocDiemDanh}")
        row = cursor.fetchone()

        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "BaoCao_ThongKe_BuoiHoc_DiemDanh"

        headers = ["Chi Tieu", "So Luong"]
        ws.append(headers)

        data = [
            ["Tong so buoi hoc da to chuc", row[0]],
            ["Tong luot diem danh", row[1]],
            ["Tong luot co mat", row[2]],
            ["Tong luot vang co phep", row[3]],
            ["Tong luot vang khong phep", row[4]]
        ]

        for cell in ws[1]:
            cell.font = Font(bold=True)

        for item in data:
            ws.append(item)

        stream = io.BytesIO()
        wb.save(stream)
        stream.seek(0)

        return send_file(
            stream,
            as_attachment=True,
            download_name='BaoCao_ThongKe_BuoiHoc_DiemDanh.xlsx',
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )

    except pyodbc.Error as e:
        return jsonify({"success": False, "message": str(e)}), 500
    except Exception as e:
        return jsonify({"success": False, "message": f"Loi may chu: {e}"}), 500
    finally:
        if conn:
            conn.close()


@baocaoadmin_bp.route('/baocao/bieu-do-tron-ty-le-chuyen-can', methods=['GET'])
@require_admin
# lấy biểu đồ tròn tỷ lệ chuyên cần
def handle_get_report_5_bieu_do_tron_ty_le_chuyen_can():
    conn = None
    try:
        conn = get_db_connection()
        if conn is None:
            return jsonify({"success": False, "message": "Loi ket noi CSDL"}), 500

        cursor = conn.cursor()
        cursor.execute("{CALL sp_BaoCao_BieuDoTronTyLeChuyenCan}")
        row = cursor.fetchone()

        if row:
            bieu_do_data = {
                "so_luong": {
                    "co_mat": row[0],
                    "vang_co_phep": row[1],
                    "vang_khong_phep": row[2],
                    "tong_luot": row[3]
                },
                "ty_le": {
                    "co_mat": round(row[4], 2),
                    "vang_co_phep": round(row[5], 2),
                    "vang_khong_phep": round(row[6], 2)
                }
            }
            return jsonify({"success": True, "data": bieu_do_data})
        else:
            return jsonify({"success": False, "message": "Khong co du lieu"}), 404

    except pyodbc.Error as e:
        return jsonify({"success": False, "message": str(e)}), 500
    except Exception as e:
        return jsonify({"success": False, "message": f"Loi may chu: {e}"}), 500
    finally:
        if conn:
            conn.close()


@baocaoadmin_bp.route('/baocao/danh-sach-du-kien-du-thi', methods=['GET'])
@require_admin
# lấy danh sách dự kiến dự thi
def handle_get_report_6_danh_sach_du_kien_du_thi():
    conn = None
    try:
        conn = get_db_connection()
        if conn is None:
            return jsonify({"success": False, "message": "Loi ket noi CSDL"}), 500

        cursor = conn.cursor()
        cursor.execute("{CALL sp_BaoCao_DSDuKienDuThi}")
        rows = cursor.fetchall()

        report_data = []
        for row in rows:
            report_data.append({
                "ma_sinh_vien": row[0],
                "ho_ten": row[1],
                "ten_lop_hanh_chinh": row[2],
                "ten_mon_hoc": row[3],
                "ma_lop_hoc_phan": row[4],
                "tong_so_buoi_hoc": row[5],
                "so_buoi_vang": row[6],
                "ty_le_vang": row[7],
                "du_kien_du_thi": row[8]
            })

        return jsonify({"success": True, "data": report_data})

    except pyodbc.Error as e:
        return jsonify({"success": False, "message": str(e)}), 500
    except Exception as e:
        return jsonify({"success": False, "message": f"Loi may chu: {e}"}), 500
    finally:
        if conn:
            conn.close()


@baocaoadmin_bp.route('/baocao/danh-sach-du-kien-du-thi/export', methods=['GET'])
@require_admin
# xuất danh sách dự kiến dự thi
def handle_export_report_6_danh_sach_du_kien_du_thi():
    conn = None
    try:
        conn = get_db_connection()
        if conn is None:
            return jsonify({"success": False, "message": "Loi ket noi CSDL"}), 500

        cursor = conn.cursor()
        cursor.execute("{CALL sp_BaoCao_DSDuKienDuThi}")
        rows = cursor.fetchall()

        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "BaoCao_DuKienDuThi"

        headers = [
            "Ma Sinh Vien", "Ho Ten", "Ten Lop Hanh Chinh",
            "Ten Mon Hoc", "Ma Lop Hoc Phan", "Tong So Buoi Hoc",
            "So Buoi Vang", "Ty Le Vang (%)", "Du Kien Du Thi"
        ]
        ws.append(headers)

        for cell in ws[1]:
            cell.font = Font(bold=True)

        for row in rows:
            ws.append(list(row))

        stream = io.BytesIO()
        wb.save(stream)
        stream.seek(0)

        return send_file(
            stream,
            as_attachment=True,
            download_name='BaoCao_DanhSach_DuKienDuThi.xlsx',
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )

    except pyodbc.Error as e:
        return jsonify({"success": False, "message": str(e)}), 500
    except Exception as e:
        return jsonify({"success": False, "message": f"Loi may chu: {e}"}), 500
    finally:
        if conn:
            conn.close()


@baocaoadmin_bp.route('/baocao/so-sanh-ty-le-chuyen-can-khoa', methods=['GET'])
@require_admin
# so sánh tỷ lệ chuyên cần giữa các khoa
def handle_get_report_7_so_sanh_ty_le_chuyen_can_khoa():
    conn = None
    try:
        conn = get_db_connection()
        if conn is None:
            return jsonify({"success": False, "message": "Loi ket noi CSDL"}), 500

        cursor = conn.cursor()
        cursor.execute("{CALL sp_BaoCao_SoSanhTyLeChuyenCanKhoa}")
        rows = cursor.fetchall()

        report_data = []
        for row in rows:
            report_data.append({
                "ma_khoa": row[0],
                "ten_khoa": row[1],
                "so_lop_hoc_phan": row[2],
                "tong_so_buoi_hoc": row[3],
                "tong_luot_diem_danh": row[4],
                "tong_luot_co_mat": row[5],
                "ty_le_chuyen_can": round(row[6], 2)
            })

        return jsonify({"success": True, "data": report_data})

    except pyodbc.Error as e:
        return jsonify({"success": False, "message": str(e)}), 500
    except Exception as e:
        return jsonify({"success": False, "message": f"Loi may chu: {e}"}), 500
    finally:
        if conn:
            conn.close()


@baocaoadmin_bp.route('/baocao/so-sanh-ty-le-chuyen-can-khoa/export', methods=['GET'])
@require_admin
# xuất báo cáo so sánh tỷ lệ chuyên cần khoa
def handle_export_report_7_so_sanh_ty_le_chuyen_can_khoa():
    conn = None
    try:
        conn = get_db_connection()
        if conn is None:
            return jsonify({"success": False, "message": "Loi ket noi CSDL"}), 500

        cursor = conn.cursor()
        cursor.execute("{CALL sp_BaoCao_SoSanhTyLeChuyenCanKhoa}")
        rows = cursor.fetchall()

        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "BaoCao_SoSanh_Khoa"

        headers = [
            "Ma Khoa", "Ten Khoa", "So Lop Hoc Phan",
            "Tong So Buoi Hoc", "Tong Luot Diem Danh",
            "Tong Luot Co Mat", "Ty Le Chuyen Can (%)"
        ]
        ws.append(headers)

        for cell in ws[1]:
            cell.font = Font(bold=True)

        for row in rows:
            formatted_row = list(row)
            formatted_row[6] = round(formatted_row[6], 2)  # Làm tròn tỷ lệ
            ws.append(formatted_row)

        stream = io.BytesIO()
        wb.save(stream)
        stream.seek(0)

        return send_file(
            stream,
            as_attachment=True,
            download_name='BaoCao_SoSanh_TyLeChuyenCan_Khoa.xlsx',
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )

    except pyodbc.Error as e:
        return jsonify({"success": False, "message": str(e)}), 500
    except Exception as e:
        return jsonify({"success": False, "message": f"Loi may chu: {e}"}), 500
    finally:
        if conn:
            conn.close()


@baocaoadmin_bp.route('/baocao/lich-su-chinh-sua', methods=['GET'])
@require_admin
# lấy lịch sử chỉnh sửa
def handle_get_report_8_lich_su_chinh_sua():
    conn = None
    try:
        conn = get_db_connection()
        if conn is None:
            return jsonify({"success": False, "message": "Loi ket noi CSDL"}), 500

        cursor = conn.cursor()
        cursor.execute("{CALL sp_BaoCao_LichSuChinhSua}")
        rows = cursor.fetchall()

        report_data = []
        for row in rows:
            report_data.append({
                "thoi_gian": row[0].strftime("%d/%m/%Y %H:%M:%S") if row[0] else "",
                "nguoi_thuc_hien": row[1],
                "hanh_dong": row[2],
                "doi_tuong": row[3],
                "ghi_chu": row[4]
            })

        return jsonify({"success": True, "data": report_data})

    except pyodbc.Error as e:
        return jsonify({"success": False, "message": str(e)}), 500
    except Exception as e:
        return jsonify({"success": False, "message": f"Loi may chu: {e}"}), 500
    finally:
        if conn:
            conn.close()


@baocaoadmin_bp.route('/baocao/lich-su-chinh-sua/export', methods=['GET'])
@require_admin
# xuất lịch sử chỉnh sửa
def handle_export_report_8_lich_su_chinh_sua():
    conn = None
    try:
        conn = get_db_connection()
        if conn is None:
            return jsonify({"success": False, "message": "Loi ket noi CSDL"}), 500

        cursor = conn.cursor()
        cursor.execute("{CALL sp_BaoCao_LichSuChinhSua}")
        rows = cursor.fetchall()

        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "BaoCao_LichSu_ChinhSua"

        headers = [
            "Thoi Gian", "Nguoi Thuc Hien", "Hanh Dong",
            "Doi Tuong", "Ghi Chu"
        ]
        ws.append(headers)

        for cell in ws[1]:
            cell.font = Font(bold=True)

        for row in rows:
            formatted_row = [
                row[0].strftime("%d/%m/%Y %H:%M:%S") if row[0] else "",
                row[1] or "",
                row[2] or "",
                row[3] or "",
                row[4] or ""
            ]
            ws.append(formatted_row)

        stream = io.BytesIO()
        wb.save(stream)
        stream.seek(0)

        return send_file(
            stream,
            as_attachment=True,
            download_name='BaoCao_LichSu_ChinhSua.xlsx',
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )

    except pyodbc.Error as e:
        return jsonify({"success": False, "message": str(e)}), 500
    except Exception as e:
        return jsonify({"success": False, "message": f"Loi may chu: {e}"}), 500
    finally:
        if conn:
            conn.close()


@baocaoadmin_bp.route('/baocao/tongquan', methods=['GET'])
@require_admin
# lấy thống kê tổng quan
def handle_get_overview_stats():
    """GET /baocao/tongquan - Lấy thống kê tổng quan cho admin"""
    conn = None
    try:
        conn = get_db_connection()
        if conn is None:
            return jsonify({"success": False, "message": "Lỗi kết nối CSDL"}), 500

        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM SinhVien")
        total_students = cursor.fetchone()[0] or 0
        
        cursor.execute("SELECT COUNT(*) FROM GiangVien")
        total_teachers = cursor.fetchone()[0] or 0
        
        cursor.execute("SELECT COUNT(*) FROM LopHocPhan")
        total_classes = cursor.fetchone()[0] or 0
        
        cursor.execute("""
            SELECT COUNT(*) FROM BuoiHoc 
            WHERE NgayHoc = CAST(GETDATE() AS DATE)
        """)
        today_sessions = cursor.fetchone()[0] or 0
        
        return jsonify({
            "success": True, 
            "data": {
                "total_students": total_students,
                "total_teachers": total_teachers,
                "total_classes": total_classes,
                "today_sessions": today_sessions
            }
        })

    except Exception as e:
        return jsonify({"success": False, "message": f"Lỗi máy chủ: {e}"}), 500
    finally:
        if conn:
            conn.close()
