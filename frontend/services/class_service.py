from typing import List, Dict, Any, Optional
from services.api_service import get_api_client
import logging

logger = logging.getLogger(__name__)


class ClassService:
    """Service xử lý các thao tác liên quan đến Lớp học phần qua API"""

    def __init__(self):
        self.api_client = get_api_client()

    def get_all_classes(self) -> List[Dict[str, Any]]:
        """Lấy danh sách tất cả lớp học phần từ API"""
        success, data = self.api_client.get_all_classes()
        logger.info(f"get_all_classes - success: {success}, data type: {type(data)}, data: {data}")
        if not success:
            logger.error(f"Lỗi lấy danh sách lớp học phần từ API: {data}")
            return []
        if isinstance(data, dict):
            result = data.get("data", [])
            logger.info(f"Extracted from dict, result: {result}")
            return result
        elif isinstance(data, list):
            logger.info(f"Data is list, returning: {data}")
            return data
        logger.warning(f"Unknown data type: {type(data)}")
        return []

    def get_class_by_id(self, class_id: str) -> Optional[Dict[str, Any]]:
        """Lấy thông tin lớp học phần theo mã LHP từ API"""
        success, data = self.api_client.get_class(class_id)
        if not success:
            logger.error(f"Lỗi lấy thông tin lớp học phần {class_id} từ API: {data}")
            return None
        return data

    def create_class(self, class_data: Dict[str, Any]) -> tuple[bool, str]:
        """Tạo lớp học phần mới qua API"""
        success, message = self.api_client.create_class(class_data)
        if not success:
            logger.error(f"Lỗi tạo lớp học phần qua API: {message}")
        return success, message

    def update_class(self, class_id: str, class_data: Dict[str, Any]) -> tuple[bool, str]:
        """Cập nhật thông tin lớp học phần qua API"""
        success, message = self.api_client.update_class(class_id, class_data)
        if not success:
            logger.error(f"Lỗi cập nhật lớp học phần {class_id} qua API: {message}")
        return success, message

    def delete_class(self, class_id: str) -> tuple[bool, str]:
        """Xóa lớp học phần qua API"""
        success, message = self.api_client.delete_class(class_id)
        if not success:
            logger.error(f"Lỗi xóa lớp học phần {class_id} qua API: {message}")
        return success, message
        
    def assign_teacher_to_class(self, class_id: str, teacher_id: str) -> tuple[bool, str]:
        """Gán giảng viên cho lớp học phần qua API"""
        success, message = self.api_client.assign_teacher_to_class(class_id, teacher_id)
        if not success:
            logger.error(f"Lỗi gán giảng viên {teacher_id} cho lớp {class_id}: {message}")
        return success, message

    def get_students_in_class(self, class_id: str) -> List[Dict[str, Any]]:
        """Lấy danh sách sinh viên trong lớp từ API"""
        success, data = self.api_client.get_students_in_class(class_id)
        if not success:
            logger.error(f"Lỗi lấy danh sách sinh viên cho lớp {class_id}: {data}")
            return []
        return data

    def add_student_to_class(self, class_id: str, student_id: str) -> tuple[bool, str]:
        """Thêm sinh viên vào lớp qua API"""
        success, message = self.api_client.add_student_to_class(class_id, student_id)
        if not success:
            logger.error(f"Lỗi thêm sinh viên {student_id} vào lớp {class_id}: {message}")
        return success, message

    def remove_student_from_class(self, class_id: str, student_id: str) -> tuple[bool, str]:
        """Xóa sinh viên khỏi lớp qua API"""
        success, message = self.api_client.remove_student_from_class(class_id, student_id)
        if not success:
            logger.error(f"Lỗi xóa sinh viên {student_id} khỏi lớp {class_id}: {message}")
        return success, message

    def add_students_from_admin_class(self, class_id: str, admin_class_id: str) -> tuple[bool, str, int]:
        """Thêm hàng loạt sinh viên từ lớp hành chính vào lớp học phần."""
        success, response = self.api_client.add_students_from_admin_class(class_id, admin_class_id)
        if not success:
            logger.error(f"Lỗi thêm hàng loạt sinh viên từ lớp {admin_class_id} vào lớp {class_id}: {response}")
            return False, str(response), 0
        
        message = response.get('message', 'Thêm hàng loạt thành công')
        count = response.get('so_luong_them', 0)
        return True, message, count