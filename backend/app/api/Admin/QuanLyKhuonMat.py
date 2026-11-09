from flask import Blueprint, request, jsonify, send_file
from app.core.KetNoiDB import get_db_connection
from app.core.XacThuc.PhanQuyen import require_admin, require_giangvien, require_giangvien_or_sinhvien
from app.services.face_recognition.face_capture import FaceCapture
from app.services.face_recognition.face_recognition_service import FaceRecognitionService
from app.services.face_recognition.validation import validate_input
import cv2
import numpy as np
import os
import base64
import tempfile
import shutil
from pathlib import Path
import logging
import pyodbc

logger = logging.getLogger(__name__)

quanlykhuonmat_bp = Blueprint('quanlykhuonmat_bp', __name__)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
MODEL_FILE = os.path.join(BASE_DIR, "face_model.yml")
METADATA_FILE = os.path.join(BASE_DIR, "face_metadata.json")

face_capture = FaceCapture()
face_service = FaceRecognitionService(
    model_file=MODEL_FILE,
    metadata_file=METADATA_FILE
)


@quanlykhuonmat_bp.route('/khuon-mat/upload-anh', methods=['POST'])
@require_giangvien
# upload ảnh khuôn mặt
def handle_upload_face_image():
    try:
        if 'files' not in request.files:
            return jsonify({
                "success": False,
                "message": "Không có ảnh được upload"
            }), 400
        
        files = request.files.getlist('files')
        student_code = request.form.get('student_code', '').strip()
        
        if not student_code:
            return jsonify({
                "success": False,
                "message": "Mã sinh viên không được để trống"
            }), 400
        
        if len(files) < 20:
            return jsonify({
                "success": False,
                "message": f"Cần ít nhất 20 ảnh (hiện có {len(files)})"
            }), 400
        
        allowed_extensions = {'jpg', 'jpeg', 'png'}
        for file in files:
            if not any(file.filename.lower().endswith(f'.{ext}') for ext in allowed_extensions):
                return jsonify({
                    "success": False,
                    "message": f"File {file.filename} không phải ảnh (jpg, png, jpeg)"
                }), 400
        
        save_dir = os.path.join(BASE_DIR, "face_data", student_code)
        if os.path.exists(save_dir):
            shutil.rmtree(save_dir)
        os.makedirs(save_dir, exist_ok=True)
        
        try:
            saved_count = 0
            for file in files:
                if file and file.filename:
                    filename = f"{student_code}_{saved_count+1}.jpg"
                    filepath = os.path.join(save_dir, filename)
                    file.save(filepath)
                    saved_count += 1
            
            logger.info(f"Đã lưu {saved_count} ảnh vào {save_dir}")
            
            conn = None
            try:
                conn = get_db_connection()
                if conn is None:
                    return jsonify({
                        "success": False,
                        "message": "Lỗi kết nối CSDL"
                    }), 500
                
                cursor = conn.cursor()
                
                cursor.execute("""
                    SELECT sv.MaSinhVien, nd.HoTen
                    FROM SinhVien sv
                    INNER JOIN NguoiDung nd ON sv.MaNguoiDung = nd.MaNguoiDung
                    WHERE sv.MaSinhVien = ? AND sv.MaLopHanhChinh IS NOT NULL
                """, (student_code,))
                
                row = cursor.fetchone()
                if not row:
                    shutil.rmtree(save_dir)
                    return jsonify({
                        "success": False,
                        "message": f"Không tìm thấy sinh viên {student_code}"
                    }), 404

                # Train model logic
                train_success, train_msg = face_service.add_student_faces(student_code, row.HoTen, save_dir)
                
                if not train_success:
                    logger.error(f"Lỗi train model: {train_msg}")
                    return jsonify({
                        "success": False, 
                        "message": f"Lưu ảnh thành công nhưng lỗi train model: {train_msg}"
                    }), 500

                cursor.execute("""
                        UPDATE SinhVien 
                        SET DuLieuKhuonMat = ?
                        WHERE MaSinhVien = ?
                """, ('trained', student_code))
                conn.commit()

                return jsonify({
                    "success": True,
                    "message": f"Cập nhật dữ liệu khuôn mặt thành công ({saved_count} ảnh)",
                    "images_count": saved_count
                })

            except pyodbc.Error as e:
                logger.error(f"Lỗi SQL: {e}")
                return jsonify({"success": False, "message": f"Lỗi CSDL: {str(e)}"}), 500
            finally:
                if conn: conn.close()

        except Exception as e:
            logger.error(f"Lỗi xử lý files: {e}")
            return jsonify({"success": False, "message": f"Lỗi: {str(e)}"}), 500
            
    except Exception as e:
        logger.error(f"Lỗi upload ảnh: {e}")
        return jsonify({"success": False, "message": f"Lỗi máy chủ: {str(e)}"}), 500


@quanlykhuonmat_bp.route('/khuon-mat/nhan-dien', methods=['POST'])
# nhận diện khuôn mặt
def handle_recognize_face():
    try:
        data = request.get_json()
        if not data or 'image' not in data:
            return jsonify({"success": False, "message": "Yêu cầu phải có trường 'image'"}), 400

        image_data = data['image']

        # Kiểm tra model đã được train chưa
        if not face_service.is_trained:
            return jsonify({
                "success": False,
                "message": "Model chưa được huấn luyện. Vui lòng đăng ký khuôn mặt sinh viên trước."
            }), 503

        # Decode base64 → numpy array (BGR frame)
        try:
            # Loại bỏ header data URI nếu có (vd: "data:image/jpeg;base64,...")
            if ',' in image_data:
                image_data = image_data.split(',', 1)[1]

            image_bytes = base64.b64decode(image_data)
            nparr = np.frombuffer(image_bytes, np.uint8)
            frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

            if frame is None:
                return jsonify({"success": False, "message": "Không thể giải mã ảnh"}), 400

        except Exception as e:
            logger.error(f"Lỗi decode ảnh: {e}")
            return jsonify({"success": False, "message": f"Dữ liệu ảnh không hợp lệ: {str(e)}"}), 400

        # Nhận diện khuôn mặt bằng LBPH model
        recognized, result = face_service.recognize_face(frame)

        if recognized:
            return jsonify({
                "success": True,
                "recognized": True,
                "message": "Nhận diện thành công",
                "student_id": result.get("student_id"),
                "name": result.get("name"),
                "confidence": result.get("confidence", 0),
            })
        else:
            return jsonify({
                "success": True,
                "recognized": False,
                "message": result.get("message", "Không nhận diện được khuôn mặt"),
                "confidence": result.get("confidence", 0),
            })

    except Exception as e:
        logger.error(f"Lỗi nhận diện: {e}")
        return jsonify({"success": False, "message": f"Lỗi máy chủ: {str(e)}"}), 500


@quanlykhuonmat_bp.route('/khuon-mat/danh-sach', methods=['GET'])
@require_giangvien
# lấy danh sách sinh viên đã đăng ký khuôn mặt
def handle_get_registered_faces():
    conn = None
    try:
        conn = get_db_connection()
        if conn is None:
            return jsonify({"success": False, "message": "Lỗi kết nối CSDL"}), 500
        
        cursor = conn.cursor()
        cursor.execute("""
            SELECT 
                sv.MaSinhVien,
                nd.HoTen,
                sv.DuLieuKhuonMat
            FROM SinhVien sv
            INNER JOIN NguoiDung nd ON sv.MaNguoiDung = nd.MaNguoiDung
            WHERE sv.DuLieuKhuonMat IS NOT NULL AND sv.MaLopHanhChinh IS NOT NULL
            ORDER BY sv.MaSinhVien
        """)
        rows = cursor.fetchall()
        
        students = []
        for row in rows:
            students.append({
                "student_code": row[0],
                "student_name": row[1],
                "registered": True
            })
            
        return jsonify({
            "success": True,
            "count": len(students),
            "data": students
        })

    except Exception as e:
        logger.error(f"Lỗi: {e}")
        return jsonify({"success": False, "message": f"Lỗi máy chủ: {str(e)}"}), 500
    finally:
        if conn: conn.close()


@quanlykhuonmat_bp.route('/khuon-mat/<string:student_code>', methods=['DELETE'])
@require_admin
# xóa dữ liệu khuôn mặt
def handle_delete_face_data(student_code):
    if not student_code:
         return jsonify({"success": False, "message": "Mã sinh viên không được để trống"}), 400

    conn = None
    try:
        conn = get_db_connection()
        if conn is None:
            return jsonify({"success": False, "message": "Lỗi kết nối CSDL"}), 500
            
        cursor = conn.cursor()
        
        # Check existence
        cursor.execute("SELECT MaSinhVien FROM SinhVien WHERE MaSinhVien = ?", (student_code,))
        if not cursor.fetchone():
             return jsonify({"success": False, "message": f"Không tìm thấy sinh viên {student_code}"}), 404
             
        cursor.execute("""
            UPDATE SinhVien
            SET DuLieuKhuonMat = NULL
            WHERE MaSinhVien = ?
        """, (student_code,))
        
        conn.commit()
        
        return jsonify({"success": True, "message": f"Đã xóa dữ liệu khuôn mặt cho sinh viên {student_code}"})

    except Exception as e:
        logger.error(f"Lỗi: {e}")
        return jsonify({"success": False, "message": f"Lỗi máy chủ: {str(e)}"}), 500
    finally:
        if conn: conn.close()


@quanlykhuonmat_bp.route('/khuon-mat/trang-thai', methods=['GET'])
@require_giangvien_or_sinhvien
# lấy trạng thái hệ thống
def handle_get_system_status():
    try:
        return jsonify({
            "success": True,
            "message": "Hệ thống hoạt động bình thường"
        })
    except Exception as e:
        logger.error(f"Lỗi: {e}")
        return jsonify({"success": False, "message": f"Lỗi máy chủ: {str(e)}"}), 500

@quanlykhuonmat_bp.route('/khuon-mat/model', methods=['GET'])
def handle_get_model():
    """Download trained face model"""
    try:
        if os.path.exists(MODEL_FILE):
            return send_file(MODEL_FILE, as_attachment=True)
        return jsonify({"success": False, "message": "Model not found"}), 404
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

@quanlykhuonmat_bp.route('/khuon-mat/metadata', methods=['GET'])
def handle_get_metadata():
    """Download face metadata"""
    try:
        if os.path.exists(METADATA_FILE):
            return send_file(METADATA_FILE, as_attachment=True)
        return jsonify({"success": False, "message": "Metadata not found"}), 404
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500
