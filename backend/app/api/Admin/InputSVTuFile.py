from flask import Blueprint, request, jsonify
from app.core.KetNoiDB import get_db_connection
from app.core.XacThuc.PhanQuyen import require_admin
import openpyxl
import csv
import io

inputsv_bp = Blueprint('inputsv_bp', __name__)


@inputsv_bp.route('/admin/sinhvien/import', methods=['POST'])
@require_admin
# nhập sinh viên từ file
def handle_import_students():
    if 'file' not in request.files:
        return jsonify({"success": False, "message": "Không tìm thấy file"}), 400

    file = request.files['file']
    filename = file.filename

    if filename == '':
        return jsonify({"success": False, "message": "Chưa chọn file"}), 400

    conn = None
    success_count = 0
    errors = []

    try:
        conn = get_db_connection()
        if conn is None:
            return jsonify({"success": False, "message": "Lỗi kết nối CSDL"}), 500

        cursor = conn.cursor()

        if filename.endswith('.xlsx'):
            workbook = openpyxl.load_workbook(file, read_only=True)
            sheet = workbook.active

            is_header = True
            for row in sheet.iter_rows(values_only=True):
                if is_header:
                    is_header = False
                    continue

                try:
                    ma_khoa = str(row[0])
                    ho_ten = str(row[1])
                    ma_sv = str(row[2])
                    ma_lop_hc = str(row[3]) if row[3] else None
                    ngay_sinh = str(row[4]) if len(row) > 4 and row[4] else None
                    dia_chi = str(row[5]) if len(row) > 5 and row[5] else None
                    gioi_tinh = str(row[6]) if len(row) > 6 and row[6] else None

                    if not ma_khoa or not ho_ten or not ma_sv:
                        errors.append(f"Hàng (Excel): Thiếu dữ liệu bắt buộc")
                        continue

                    cursor.execute("{CALL sp_ThemSinhVien(?, ?, ?, ?, ?, ?, ?)}",
                                   (ma_khoa, ho_ten, ma_sv, ma_lop_hc, ngay_sinh, dia_chi, gioi_tinh))
                    success_count += 1

                except Exception as e:
                    errors.append(f"Hàng (Excel): {row} | Lỗi: {str(e)}")

        elif filename.endswith('.csv'):
            stream = io.TextIOWrapper(file.stream, encoding='utf-8')
            reader = csv.reader(stream)

            is_header = True
            row_num = 1
            for row in reader:
                if is_header:
                    is_header = False
                    continue

                row_num += 1
                try:
                    ma_khoa = str(row[0])
                    ho_ten = str(row[1])
                    ma_sv = str(row[2])
                    ma_lop_hc = str(row[3]) if row[3] else None
                    ngay_sinh = str(row[4]) if len(row) > 4 and row[4] else None
                    dia_chi = str(row[5]) if len(row) > 5 and row[5] else None
                    gioi_tinh = str(row[6]) if len(row) > 6 and row[6] else None

                    if not ma_khoa or not ho_ten or not ma_sv:
                        errors.append(f"Hàng {row_num} (CSV): Thiếu dữ liệu bắt buộc")
                        continue

                    cursor.execute("{CALL sp_ThemSinhVien(?, ?, ?, ?, ?, ?, ?)}",
                                   (ma_khoa, ho_ten, ma_sv, ma_lop_hc, ngay_sinh, dia_chi, gioi_tinh))
                    success_count += 1

                except Exception as e:
                    errors.append(f"Hàng {row_num} (CSV): {row} | Lỗi: {str(e)}")

        else:
            return jsonify({"success": False, "message": "File không được hỗ trợ. Chỉ chấp nhận .xlsx hoặc .csv"}), 400

        conn.commit()
        return jsonify({
            "success": True,
            "message": f"Đã nhập thành công {success_count} sinh viên.",
            "errors": errors
        })

    except Exception as e:
        if conn:
            conn.rollback()
        return jsonify({"success": False, "message": f"Lỗi máy chủ: {e}"}), 500
    finally:
        if conn:
            conn.close()