from typing import List, Dict, Any, Optional
from services.api_service import get_api_client
import logging

logger = logging.getLogger(__name__)


class StudentService:
    """Service xử lý các thao tác liên quan đến sinh viên qua API"""

    def __init__(self):
        self.api_client = get_api_client()

    def get_all_students(self, class_id: str = None) -> List[Dict[str, Any]]:
        """Lấy danh sách tất cả sinh viên từ API (có thể lọc theo lớp)"""
        success, data = self.api_client.get_all_students(class_id=class_id)
        logger.info(f"Dữ liệu sinh viên nhận được từ API client: {data}")
        if not success:
            logger.error(f"Lỗi lấy danh sách sinh viên từ API: {data}")
            return []
        return data

    def get_student_by_code(self, student_code: str) -> Optional[Dict[str, Any]]:
        """Lấy thông tin sinh viên theo mã SV từ API"""
        success, data = self.api_client.get_student(student_code)
        if not success:
            logger.error(f"Lỗi lấy thông tin sinh viên {student_code} từ API: {data}")
            return None
        return data

    def create_student(self, student_data: Dict[str, Any]) -> tuple[bool, str]:
        """
        Tạo sinh viên mới qua API.
        Backend sẽ xử lý tất cả logic phức tạp (tạo người dùng, băm mật khẩu, v.v.).
        """
        success, message = self.api_client.create_student(student_data)
        if not success:
            logger.error(f"Lỗi tạo sinh viên qua API: {message}")
        return success, message

    def update_student(self, user_id: str, student_data: Dict[str, Any]) -> tuple[bool, str]:
        """Cập nhật thông tin sinh viên qua API"""
        success, message = self.api_client.update_student(user_id, student_data)
        if not success:
            logger.error(f"Lỗi cập nhật sinh viên {user_id} qua API: {message}")
        return success, message

    def delete_student(self, student_code: str) -> tuple[bool, str]:
        """
        Xóa sinh viên qua API.
        Backend sẽ xử lý soft delete và xóa dữ liệu khuôn mặt.
        """
        success, message = self.api_client.delete_student(student_code)
        if not success:
            logger.error(f"Lỗi xóa sinh viên {student_code} qua API: {message}")
        return success, message

    def import_students(self, file_path: str) -> tuple[bool, str]:
        """Nhập sinh viên từ file Excel/CSV"""
        success, data = self.api_client.import_students(file_path)
        if not success:
            logger.error(f"Lỗi nhập sinh viên từ file: {data.get('message')}")
            return False, data.get('message', 'Lỗi không xác định')
        return True, data.get('message', 'Thành công')