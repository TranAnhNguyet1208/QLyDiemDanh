"""Service quản lý điểm danh qua API"""
from typing import List, Dict, Any, Optional
from services.api_service import get_api_client
import logging

logger = logging.getLogger(__name__)


class AttendanceService:
    """Service xử lý các thao tác liên quan đến điểm danh qua API"""

    def __init__(self):
        self.api_client = get_api_client()

    def generate_attendance_code(self, session_id: int, code: str) -> tuple[bool, str]:
        """Tạo phiên điểm danh bằng mã cho một buổi học đã có."""
        success, data = self.api_client.create_manual_attendance_session(session_id, code)
        return success, data.get('message', 'Lỗi không xác định')

    def generate_qr_code_session(self, session_id: int) -> tuple[bool, str, Optional[str], Optional[str]]:
        """
        Tạo phiên điểm danh bằng QR code.
        Trả về (success, message, qr_image_base64, qr_link)
        """
        success, data = self.api_client.create_qr_attendance_session(session_id)
        if success:
            return True, data.get('message', 'Tạo mã QR thành công'), data.get('qr_image'), data.get('qr_link')
        return False, data.get('message', 'Lỗi tạo mã QR'), None, None

    def attend_by_code(self, student_code: str, attendance_code: str) -> tuple[bool, str]:
        """Điểm danh bằng mã qua API"""
        success, data = self.api_client.attend_by_code(student_code, attendance_code)
        return success, data.get('message', 'Lỗi không xác định')

    def attend_by_face(self, student_code: str, session_id: int, confidence: float) -> tuple[bool, str]:
        """Điểm danh bằng nhận diện khuôn mặt qua API"""
        success, data = self.api_client.attend_by_face(student_code, session_id, confidence)
        return success, data.get('message', 'Lỗi không xác định')

    def attend_manual(self, session_id: int, student_id: int, status: str, note: str = None) -> tuple[bool, str]:
        """Điểm danh thủ công qua API"""
        success, data = self.api_client.attend_manual(session_id, student_id, status, note)
        return success, data.get('message', 'Lỗi không xác định')

    def get_session_attendance(self, session_id: int) -> List[Dict[str, Any]]:
        """Lấy danh sách điểm danh của buổi học từ API"""
        success, data = self.api_client.get_session_attendance(session_id)
        if not success:
            logger.error(f"Lỗi lấy danh sách điểm danh cho buổi học {session_id}: {data}")
            return []
        return data

    def get_attendance_statistics(self, session_id: int) -> Dict[str, Any]:
        """Lấy thống kê điểm danh của buổi học từ API"""
        success, data = self.api_client.get_attendance_stats(session_id)
        if not success:
            logger.error(f"Lỗi lấy thống kê điểm danh cho buổi học {session_id}: {data}")
            return {}
        return data

