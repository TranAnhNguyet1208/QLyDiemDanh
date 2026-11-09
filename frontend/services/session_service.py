from typing import List, Dict, Any, Optional
from services.api_service import get_api_client
import logging

logger = logging.getLogger(__name__)


class SessionService:
    """Service xử lý các nghiệp vụ liên quan đến buổi học qua API"""

    def __init__(self):
        self.api_client = get_api_client()

    def get_sessions_by_filter(self, start_date: str, end_date: str, class_id: str = None, teacher_id: str = None, student_id: str = None) -> List[Dict[str, Any]]:
        try:
            params = {
                'start_date': start_date,
                'end_date': end_date,
                'class_id': class_id,
                'teacher_id': teacher_id,
                'student_id': student_id
            }
            params = {k: v for k, v in params.items() if v is not None}

            success, sessions = self.api_client.get_sessions(params)
            if not success:
                logger.error(f"Lỗi lấy danh sách buổi học từ API: {sessions}")
                return []
            return sessions
        except Exception as e:
            logger.error(f"Lỗi khi gọi API lấy danh sách buổi học: {e}")
            return []

    def get_session_detail(self, session_id: int) -> Optional[Dict[str, Any]]:
        """Lấy chi tiết buổi học từ API"""
        success, session = self.api_client.get_session(session_id)
        if not success:
            logger.error(f"Lỗi lấy chi tiết buổi học {session_id} từ API: {session}")
            return None
        return session

    def create_session(self, session_data: Dict[str, Any]) -> tuple[bool, str]:
        success, message = self.api_client.create_session(session_data)
        if not success:
            logger.error(f"Lỗi tạo buổi học qua API: {message}")
        return success, message

    def update_session(self, session_id: int, session_data: Dict[str, Any]) -> tuple[bool, str]:
        """Cập nhật buổi học qua API"""
        success, message = self.api_client.update_session(session_id, session_data)
        if not success:
            logger.error(f"Lỗi cập nhật buổi học {session_id} qua API: {message}")
        return success, message

    def delete_session(self, session_id: int) -> tuple[bool, str]:
        """
        Xóa buổi học qua API.
        Backend sẽ xử lý logic nghiệp vụ (ví dụ: kiểm tra điểm danh đã tồn tại chưa).
        """
        success, message = self.api_client.delete_session(session_id)
        if not success:
            logger.error(f"Lỗi xóa buổi học {session_id} qua API: {message}")
        return success, message