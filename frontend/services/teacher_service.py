from typing import List, Dict, Any, Optional
from services.api_service import get_api_client
import logging

logger = logging.getLogger(__name__)


class TeacherService:
    """Service xử lý các thao tác liên quan đến giảng viên qua API"""

    def __init__(self):
        self.api_client = get_api_client()

    def get_all_teachers(self) -> List[Dict[str, Any]]:
        """Lấy danh sách tất cả giảng viên từ API"""
        success, data = self.api_client.get_all_teachers()
        if not success:
            logger.error(f"Lỗi lấy danh sách giảng viên từ API: {data}")
            return []
        return data

    def get_teacher_by_code(self, teacher_code: str) -> Optional[Dict[str, Any]]:
        """Lấy thông tin giảng viên theo mã GV từ API"""
        success, data = self.api_client.get_teacher(teacher_code)
        if not success:
            logger.error(f"Lỗi lấy thông tin giảng viên {teacher_code} từ API: {data}")
            return None
        return data

    def get_teacher_schedule(self, teacher_code: str, from_date: str = None, to_date: str = None) -> List[Dict[str, Any]]:
        """Lấy lịch dạy của giảng viên từ API"""
        success, data = self.api_client.get_teacher_schedule(teacher_code, from_date, to_date)
        if not success:
            logger.error(f"Lỗi lấy lịch dạy cho giảng viên {teacher_code}: {data}")
            return []
        return data

    def get_teacher_classes(self, teacher_code: str) -> List[Dict[str, Any]]:
        """Lấy danh sách lớp giảng viên đang dạy từ API"""
        success, data = self.api_client.get_teacher_classes(teacher_code)
        if not success:
            logger.error(f"Lỗi lấy danh sách lớp cho giảng viên {teacher_code}: {data}")
            return []
        return data

    def get_class_students(self, class_id: str) -> List[Dict[str, Any]]:
        """Lấy danh sách sinh viên của lớp học phần (cho giảng viên)"""
        success, data = self.api_client.get_teacher_class_students(class_id)
        if not success:
            logger.error(f"Lỗi lấy danh sách sinh viên cho lớp {class_id}: {data}")
            return []
        return data

    def create_teacher(self, teacher_data: Dict[str, Any]) -> tuple[bool, str]:
        """Tạo giảng viên mới qua API"""
        success, message = self.api_client.create_teacher(teacher_data)
        if not success:
            logger.error(f"Lỗi tạo giảng viên qua API: {message}")
        return success, message

    def update_teacher(self, user_id: str, teacher_data: Dict[str, Any]) -> tuple[bool, str]:
        """Cập nhật thông tin giảng viên qua API"""
        success, message = self.api_client.update_teacher(user_id, teacher_data)
        if not success:
            logger.error(f"Lỗi cập nhật giảng viên {user_id} qua API: {message}")
        return success, message

    def delete_teacher(self, teacher_code: str) -> tuple[bool, str]:
        """Xóa giảng viên qua API"""
        success, message = self.api_client.delete_teacher(teacher_code)
        if not success:
            logger.error(f"Lỗi xóa giảng viên {teacher_code} qua API: {message}")
        return success, message