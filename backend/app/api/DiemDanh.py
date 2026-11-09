from flask import Blueprint, request, jsonify, g
from app.core.KetNoiDB import get_db_connection
from app.core.XacThuc.PhanQuyen import require_giangvien
import pyodbc
import qrcode
import io
import base64
import socket

diemdanh_bp = Blueprint('diemdanh_bp', __name__)

def get_lan_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "127.0.0.1"


@diemdanh_bp.route('/phien/tao-thu-cong', methods=['POST'])
@require_giangvien
# tạo phiên điểm danh thủ công
def handle_create_manual_session():
    data = request.get_json()
    ma_buoi_hoc = data.get('ma_buoi_hoc')
    ma_code_gv_nhap = data.get('ma_code')

    if not ma_buoi_hoc or not ma_code_gv_nhap:
        return jsonify({"success": False, "message": "Thiếu mã buổi học hoặc mã code"}), 400

    conn = None
    try:
        conn = get_db_connection()
        if conn is None:
            return jsonify({"success": False, "message": "Lỗi kết nối CSDL"}), 500

        cursor = conn.cursor()
        cursor.execute("{CALL sp_TaoPhienDiemDanh_MaCode(?, ?)}", (ma_buoi_hoc, ma_code_gv_nhap))
        result = cursor.fetchone()
        conn.commit()

        return jsonify({
            "success": True,
            "message": "Tạo phiên thủ công thành công",
            "ma_phien": result[0],
            "ma_code": result[1]
        }), 201

    except pyodbc.Error as e:
        conn.rollback()
        return jsonify({"success": False, "message": str(e)}), 500
    except Exception as e:
        conn.rollback()
        return jsonify({"success": False, "message": f"Lỗi máy chủ: {e}"}), 500
    finally:
        if conn: conn.close()


@diemdanh_bp.route('/phien/tao-qr', methods=['POST'])
@require_giangvien
# tạo phiên điểm danh qr
def handle_create_qr_session():
    data = request.get_json()
    ma_buoi_hoc = data.get('ma_buoi_hoc')

    if not ma_buoi_hoc:
        return jsonify({"success": False, "message": "Thiếu mã buổi học"}), 400

    conn = None
    try:
        conn = get_db_connection()
        if conn is None:
            return jsonify({"success": False, "message": "Lỗi kết nối CSDL"}), 500

        cursor = conn.cursor()
        cursor.execute("{CALL sp_TaoPhienDiemDanh_QR(?)}", (ma_buoi_hoc))
        result = cursor.fetchone()

        if not result:
            return jsonify({"success": False, "message": "Lỗi khi tạo phiên"}), 500

        ma_phien = result[0]
        conn.commit()

        
        scheme = request.scheme
        port = request.host.split(':')[-1] if ':' in request.host else '80'
        lan_ip = get_lan_ip()
        
        base_url = f"{scheme}://{lan_ip}:{port}/"
        qr_data_url = f"{base_url}api/diemdanh-web?phien={ma_phien}"

        qr_img = qrcode.make(qr_data_url)
        buf = io.BytesIO()
        qr_img.save(buf, format="PNG")
        qr_base64 = base64.b64encode(buf.getvalue()).decode('utf-8')

        return jsonify({
            "success": True,
            "message": "Tạo phiên QR thành công",
            "ma_phien": ma_phien,
            "qr_image_url": f"data:image/png;base64,{qr_base64}",
            "qr_link": qr_data_url
        }), 201

    except pyodbc.Error as e:
        conn.rollback()
        return jsonify({"success": False, "message": str(e)}), 500
    except Exception as e:
        conn.rollback()
        return jsonify({"success": False, "message": f"Lỗi máy chủ: {e}"}), 500
    finally:
        if conn: conn.close()


@diemdanh_bp.route('/diemdanh-web', methods=['GET'])
# hiển thị trang điểm danh
def show_web_attendance_page():
    ma_phien = request.args.get('phien')

    if not ma_phien:
        return "<h1>Lỗi: Không tìm thấy mã phiên.</h1>", 400

    html_page = f"""
    <!DOCTYPE html>
    <html lang="vi">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>EduCheck - Điểm Danh</title>
        <script src="https://cdn.tailwindcss.com"></script>
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
        <style>body {{ font-family: 'Inter', sans-serif; }}</style>
    </head>
    <body class="bg-gray-100 flex items-center justify-center min-h-screen">
        <div class="bg-white p-8 rounded-lg shadow-xl w-full max-w-sm">
            <h1 class="text-3xl font-bold text-center text-blue-600 mb-2">EduCheck</h1>
            <h2 class="text-lg font-semibold text-center text-gray-700 mb-6">Xác Nhận Điểm Danh</h2>

            <div id="attendance-form">
                <input type="hidden" id="ma_phien" value="{ma_phien}">
                <div class="mb-4">
                    <label for="ma_sv" class="block text-sm font-medium text-gray-700 mb-2">Mã Số Sinh Viên</label>
                    <input type="text" id="ma_sv" class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500" placeholder="Nhập mã sinh viên...">
                </div>
                <button onclick="submitAttendance()" id="btnSubmit" class="w-full bg-blue-600 text-white py-3 rounded-lg font-semibold hover:bg-blue-700 transition shadow-md">
                    Điểm Danh Ngay
                </button>
            </div>

            <div id="message" class="mt-6 text-center"></div>
        </div>

        <script>
            async function submitAttendance() {{
                const maPhien = document.getElementById("ma_phien").value;
                const maSV = document.getElementById("ma_sv").value.trim();
                const msgEl = document.getElementById("message");
                const btn = document.getElementById("btnSubmit");

                if (!maSV) {{
                    msgEl.innerHTML = '<span class="text-red-500 font-medium">Vui lòng nhập Mã Sinh Viên!</span>';
                    return;
                }}

                btn.disabled = true;
                btn.innerText = "Đang xử lý...";
                msgEl.innerHTML = "";

                try {{
                    const response = await fetch('/api/diemdanh-qr-submit', {{
                        method: 'POST',
                        headers: {{ 'Content-Type': 'application/json' }},
                        body: JSON.stringify({{ "ma_phien": maPhien, "ma_sv": maSV }})
                    }});

                    const result = await response.json();

                    if (result.success) {{
                        document.getElementById("attendance-form").style.display = "none";
                        msgEl.innerHTML = `
                            <div class="text-green-600 font-semibold animate-bounce">
                                <svg class="w-16 h-16 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>
                            </div>
                            <div class="text-xl font-bold text-gray-800 mb-2">Điểm danh thành công!</div>
                            <div class="text-gray-600">Xin chào: <span class="font-bold text-blue-600 text-lg">${{result.ten_sinh_vien}}</span></div>
                            <div class="text-sm text-gray-500 mt-2">Mã SV: ${{maSV}}</div>
                        `;
                    }} else {{
                        btn.disabled = false;
                        btn.innerText = "Điểm Danh Ngay";
                        msgEl.innerHTML = `<span class="text-red-500 font-medium">❌ Lỗi: ${{result.message}}</span>`;
                    }}
                }} catch (err) {{
                    btn.disabled = false;
                    btn.innerText = "Thử Lại";
                    msgEl.innerHTML = `<span class="text-red-500">Lỗi kết nối máy chủ!</span>`;
                }}
            }}
        </script>
    </body>
    </html>
    """
    return html_page


@diemdanh_bp.route('/diemdanh-qr-submit', methods=['POST'])
# xử lý điểm danh qr
def handle_qr_submit():
    data = request.get_json()
    ma_phien = data.get('ma_phien')
    ma_sv = data.get('ma_sv')

    if not ma_phien or not ma_sv:
        return jsonify({"success": False, "message": "Thiếu thông tin"}), 400

    conn = None
    try:
        conn = get_db_connection()
        if conn is None:
            return jsonify({"success": False, "message": "Lỗi kết nối CSDL"}), 500

        cursor = conn.cursor()

        cursor.execute("{CALL sp_LuotDiemDanh_QR(?, ?, ?)}", (ma_phien, ma_sv, request.remote_addr))
        result_diemdanh = cursor.fetchone()

        if not result_diemdanh or result_diemdanh[0] == 2:  # 2 là đã điểm danh rồi hoặc lỗi
            conn.rollback()
            return jsonify(
                {"success": False, "message": result_diemdanh[1] if result_diemdanh else "Lỗi không xác định"}), 400

        cursor.execute("{CALL sp_LayThongTinSinhVien(?)}", (ma_sv))
        result_sv = cursor.fetchone()

        ten_sv = "Sinh viên"
        if result_sv:
            ten_sv = result_sv[0]

        conn.commit()

        return jsonify({
            "success": True,
            "message": result_diemdanh[1],
            "ten_sinh_vien": ten_sv
        })

    except pyodbc.Error as e:
        conn.rollback()
        return jsonify({"success": False, "message": str(e)}), 500
    except Exception as e:
        conn.rollback()
        return jsonify({"success": False, "message": f"Lỗi máy chủ: {e}"}), 500
    finally:
        if conn: conn.close()


@diemdanh_bp.route('/diemdanh/nhap-ma', methods=['POST'])
# xử lý điểm danh bằng mã code
def handle_code_submit():
    data = request.get_json()
    ma_code = data.get('ma_code')
    ma_sv = data.get('ma_sv')

    if not ma_code or not ma_sv:
        return jsonify({"success": False, "message": "Thiếu mã code hoặc mã sinh viên"}), 400

    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("{CALL sp_LuotDiemDanh_MaCode(?, ?, ?)}", (ma_code, ma_sv, request.remote_addr))
        result = cursor.fetchone()
        conn.commit()

        if not result or result[0] == 2:
            return jsonify({"success": False, "message": result[1]}), 400

        return jsonify({"success": True, "message": result[1]})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500
    finally:
        if conn: conn.close()


@diemdanh_bp.route('/diemdanh/khuon-mat', methods=['POST'])
# xử lý điểm danh bằng khuôn mặt
def handle_face_attendance():
    data = request.get_json()
    ma_buoi_hoc = data.get('ma_buoi_hoc')
    ma_sv = data.get('ma_sv')
    do_tin_cay = data.get('do_tin_cay')

    if not ma_buoi_hoc or not ma_sv:
        return jsonify({"success": False, "message": "Thiếu thông tin"}), 400

    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("{CALL sp_DiemDanh_KhuonMat(?, ?)}", (ma_buoi_hoc, ma_sv))
        result = cursor.fetchone()
        

        conn.commit()
        
        if not result:
             return jsonify({"success": False, "message": "Lỗi không xác định"}), 500

        if result[0] == 2: # Đã điểm danh rồi
             return jsonify({"success": True, "message": result[1]}), 200 # Vẫn trả về success=True nhưng message khác

        return jsonify({"success": True, "message": result[1]})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500
    finally:
        if conn: conn.close()


@diemdanh_bp.route('/diemdanh/thu-cong', methods=['POST'])
@require_giangvien
# xử lý điểm danh thủ công
def handle_manual_attendance():
    data = request.get_json()
    ma_buoi_hoc = data.get('ma_buoi_hoc')
    ma_sv = data.get('ma_sv')
    trang_thai = data.get('trang_thai')

    if not ma_buoi_hoc or not ma_sv or not trang_thai:
        return jsonify({"success": False, "message": "Thiếu thông tin"}), 400

    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("{CALL sp_DiemDanh_ThuCong(?, ?, ?, ?)}", (ma_buoi_hoc, ma_sv, trang_thai, data.get('ghi_chu')))
        result = cursor.fetchone()
        
        # Log action
        if hasattr(g, 'user_id'):
             hanh_dong = 'Cập nhật điểm danh thủ công'
             doi_tuong = f"Sinh viên {ma_sv} - Buổi {ma_buoi_hoc}"
             ghi_chu = f"Trạng thái: {trang_thai}"
             cursor.execute("{CALL sp_GhiLog(?, ?, ?, ?)}", (g.user_id, hanh_dong, doi_tuong, ghi_chu))

        conn.commit()
        return jsonify({"success": True, "message": result[1]})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500
    finally:
        if conn: conn.close()


@diemdanh_bp.route('/phien/<int:ma_phien>/ket-thuc', methods=['POST'])
@require_giangvien
# kết thúc phiên điểm danh
def handle_ket_thuc_phien(ma_phien):
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("{CALL sp_KetThucPhien(?)}", (ma_phien,))
        result = cursor.fetchone()
        conn.commit()
        return jsonify({"success": True, "message": result[1]})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500
    finally:
        if conn: conn.close()


@diemdanh_bp.route('/phien/<int:ma_buoi_hoc>/danh-sach', methods=['GET'])
@require_giangvien
# lấy danh sách điểm danh của buổi học
def handle_get_session_attendance_list(ma_buoi_hoc):
    conn = None
    try:
        conn = get_db_connection()
        if conn is None:
            return jsonify({"success": False, "message": "Lỗi kết nối CSDL"}), 500

        cursor = conn.cursor()
        
        cursor.execute("{CALL sp_LayDanhSachDiemDanh_BuoiHoc(?)}", (ma_buoi_hoc))
        
        rows = cursor.fetchall()
        attendance_list = []
        
        for row in rows:
            attendance_list.append({
                "ma_sinh_vien": row[0],
                "ho_ten": row[1],
                "trang_thai": row[2],
                "phuong_thuc": row[3],
                "thoi_gian_diem_danh": str(row[4]) if row[4] else None,
                "ip": row[5]
            })
        
        return jsonify({"success": True, "data": attendance_list})
    
    except pyodbc.Error as e:
        return jsonify({"success": False, "message": str(e)}), 500
    except Exception as e:
        return jsonify({"success": False, "message": f"Lỗi máy chủ: {e}"}), 500
    finally:
        if conn: conn.close()