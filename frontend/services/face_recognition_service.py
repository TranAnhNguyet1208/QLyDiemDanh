"""
Frontend Face Recognition Service
Kiến trúc: Frontend chụp frame → encode base64 → gửi lên Backend API → nhận kết quả
Frontend KHÔNG tự chạy AI cục bộ (không giữ model, không tự train).
Dữ liệu ảnh huấn luyện và model AI được quản lý hoàn toàn trên Backend Server.
"""
import os
import cv2
import numpy as np
from pathlib import Path
import logging
import base64
import requests
from services.api_service import get_api_client

logger = logging.getLogger(__name__)


class FaceRecognitionService:
    """
    Service nhận diện khuôn mặt phía Frontend.
    Mọi xử lý AI đều được thực hiện trên Backend.
    Frontend chỉ:
      - Chụp frame từ camera
      - Encode sang base64
      - Gửi lên POST /khuon-mat/nhan-dien
      - Nhận kết quả JSON từ Backend
    """

    def __init__(self):
        # Chỉ dùng để detect khuôn mặt trước khi gửi (tối ưu bandwidth — không gửi frame trống)
        self.face_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        )
        # Trạng thái: lấy từ API /khuon-mat/danh-sach
        self.is_trained = False
        self._check_model_status()

    def _check_model_status(self):
        """
        Kiểm tra xem Backend đã có model được huấn luyện chưa
        bằng cách gọi GET /khuon-mat/danh-sach.
        """
        try:
            api = get_api_client()
            success, students = api.get_registered_faces()
            if success and len(students) > 0:
                self.is_trained = True
                logger.info(f"Backend có {len(students)} sinh viên đã đăng ký khuôn mặt.")
            else:
                self.is_trained = False
                logger.warning("Backend chưa có dữ liệu khuôn mặt nào.")
        except Exception as e:
            logger.error(f"Không thể kiểm tra trạng thái model từ Backend: {e}")
            self.is_trained = False

    def sync_model_from_server(self) -> tuple:
        """
        Làm mới trạng thái is_trained bằng cách kiểm tra lại Backend.
        Frontend không download model — chỉ cần biết Backend đã có model chưa.
        """
        logger.info("Kiểm tra trạng thái model từ Backend...")
        self._check_model_status()
        if self.is_trained:
            return True, "Backend đã có model khuôn mặt sẵn sàng."
        else:
            return False, "Backend chưa có dữ liệu khuôn mặt nào được đăng ký."

    def recognize_face(self, image_array: np.ndarray) -> tuple:
        """
        Nhận diện khuôn mặt bằng cách gửi frame lên Backend API.

        Args:
            image_array: Frame BGR từ camera (numpy array)

        Returns:
            (success: bool, result: dict)
            - Nếu nhận diện được: (True, {'student_id': ..., 'name': ..., 'confidence': ...})
            - Nếu không nhận diện: (False, {'message': ...})
        """
        if image_array is None:
            return False, {"message": "Frame không hợp lệ"}

        # Kiểm tra nhanh có khuôn mặt trong frame không (tiết kiệm băng thông)
        gray = cv2.cvtColor(image_array, cv2.COLOR_BGR2GRAY)
        faces = self.face_cascade.detectMultiScale(
            gray, scaleFactor=1.1, minNeighbors=5, minSize=(60, 60)
        )
        if len(faces) == 0:
            return False, {"message": "Không phát hiện khuôn mặt trong frame"}

        try:
            # Encode frame thành base64 JPEG để gửi qua API
            ret, buffer = cv2.imencode('.jpg', image_array, [cv2.IMWRITE_JPEG_QUALITY, 85])
            if not ret:
                return False, {"message": "Không thể encode ảnh"}

            image_base64 = base64.b64encode(buffer).decode('utf-8')

            # Gọi Backend API nhận diện
            api = get_api_client()
            success, data = api.recognize_face(image_base64)

            if not success:
                error_msg = data.get('message', 'Lỗi kết nối Backend') if isinstance(data, dict) else 'Lỗi kết nối Backend'
                logger.warning(f"Backend trả về lỗi: {error_msg}")
                return False, {"message": error_msg}

            # Backend trả về success=True nhưng có thể recognized=False
            if data.get('recognized'):
                return True, {
                    "student_id": data.get("student_id"),
                    "name": data.get("name"),
                    "confidence": data.get("confidence", 0),
                }
            else:
                return False, {"message": data.get("message", "Không nhận diện được")}

        except Exception as e:
            logger.error(f"Lỗi gọi API nhận diện: {e}")
            return False, {"message": f"Lỗi: {str(e)}"}

    def register_person(self, name: str, student_code: str, image_folder: str) -> tuple:
        """
        Đăng ký khuôn mặt bằng cách upload ảnh lên Backend.
        Backend sẽ tự train lại model sau khi nhận ảnh.

        Args:
            name: Họ tên sinh viên
            student_code: Mã sinh viên
            image_folder: Đường dẫn thư mục chứa ảnh (trên máy Frontend)

        Returns:
            (success: bool, message: str)
        """
        logger.info(f"Đăng ký khuôn mặt: {name} ({student_code}) — Upload lên Backend")

        try:
            api = get_api_client()
            url = f"{api.base_url}/khuon-mat/upload-anh"
            headers = {'Authorization': f"Bearer {api.auth_token}"} if api.auth_token else {}

            # Tìm tất cả file ảnh trong thư mục
            image_path_obj = Path(image_folder)
            image_files = []
            for ext in ['*.jpg', '*.jpeg', '*.png']:
                image_files.extend(image_path_obj.glob(ext))

            if not image_files:
                return False, f"Không tìm thấy ảnh trong thư mục: {image_folder}"

            # Mở file và chuẩn bị multipart upload
            files = []
            opened_files = []
            try:
                for img_path in image_files:
                    f = open(img_path, 'rb')
                    opened_files.append(f)
                    files.append(('files', (img_path.name, f, 'image/jpeg')))

                data = {'student_code': student_code}
                logger.info(f"Đang upload {len(files)} ảnh lên {url}...")

                response = requests.post(url, headers=headers, data=data, files=files, timeout=120)
            finally:
                for f in opened_files:
                    f.close()

            if response.status_code == 200:
                res_data = response.json()
                if res_data.get('success'):
                    # Cập nhật trạng thái: Backend đã có model
                    self.is_trained = True
                    return True, res_data.get('message', 'Đăng ký thành công')
                else:
                    return False, res_data.get('message', 'Đăng ký thất bại')
            else:
                return False, f"Lỗi máy chủ: {response.status_code} — {response.text[:200]}"

        except requests.exceptions.ConnectionError:
            return False, "Không kết nối được với Backend. Vui lòng kiểm tra Backend đang chạy."
        except Exception as e:
            logger.error(f"Lỗi đăng ký khuôn mặt: {e}")
            return False, str(e)

    def remove_person(self, student_code: str) -> tuple:
        """
        Xóa dữ liệu khuôn mặt của sinh viên qua Backend API.

        Args:
            student_code: Mã sinh viên cần xóa

        Returns:
            (success: bool, message: str)
        """
        try:
            api = get_api_client()
            success, message = api.delete_face(student_code)
            if success:
                logger.info(f"Đã xóa dữ liệu khuôn mặt: {student_code}")
                # Kiểm tra lại trạng thái
                self._check_model_status()
            return success, message
        except Exception as e:
            logger.error(f"Lỗi xóa khuôn mặt {student_code}: {e}")
            return False, str(e)