from typing import List, Dict, Any, Optional
from services.api_service import get_api_client
import logging

logger = logging.getLogger(__name__)


class DepartmentService:
    """Service xử lý các thao tác liên quan đến Khoa qua API"""

    def __init__(self):
        self.api_client = get_api_client()

    def get_all_departments(self) -> List[Dict[str, Any]]:
        """Lấy danh sách tất cả các khoa từ API"""
        success, data = self.api_client.get_all_departments()
        if not success:
            logger.error(f"Lỗi lấy danh sách khoa từ API: {data}")
            return []
        return data

    def get_department_by_id(self, department_id: str) -> Optional[Dict[str, Any]]:
        """Lấy thông tin khoa theo ID từ API"""
        success, data = self.api_client.get_department(department_id)
        if not success:
            logger.error(f"Lỗi lấy thông tin khoa {department_id} từ API: {data}")
            return None
        return data

    def create_department(self, department_data: Dict[str, Any]) -> tuple[bool, str]:
        """Tạo khoa mới qua API"""
        success, message = self.api_client.create_department(department_data)
        if not success:
            logger.error(f"Lỗi tạo khoa qua API: {message}")
        return success, message

    def update_department(self, department_id: str, department_data: Dict[str, Any]) -> tuple[bool, str]:
        """Cập nhật thông tin khoa qua API"""
        success, message = self.api_client.update_department(department_id, department_data)
        if not success:
            logger.error(f"Lỗi cập nhật khoa {department_id} qua API: {message}")
        return success, message

    def delete_department(self, department_id: str) -> tuple[bool, str]:
        """Xóa khoa qua API"""
        success, message = self.api_client.delete_department(department_id)
        if not success:
            logger.error(f"Lỗi xóa khoa {department_id} qua API: {message}")
        return success, message
