from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from services.api_service import get_api_client
import logging

logger = logging.getLogger(__name__)


class AuthService:
    """Service xử lý authentication và authorization qua API"""

    def __init__(self):
        self.api_client = get_api_client()
        self.current_user = None
        self.session_start_time = None

    def login(self, username: str, password: str) -> tuple[bool, str, Optional[Dict[str, Any]]]:
        try:
            success, data = self.api_client.login(username, password)

            if not success:
                message = data.get("message", "Tên đăng nhập hoặc mật khẩu không đúng")
                return False, message, None

            # API call thành công, backend đã xác thực
            user_data = data.get("user")
            token = data.get("token")

            if not user_data or not token:
                return False, "Phản hồi từ API không hợp lệ", None

            # Thiết lập token cho các request tiếp theo
            self.api_client.set_auth_token(token)

            # Lưu session cục bộ
            self.current_user = user_data
            self.session_start_time = datetime.now()

            logger.info(f"User {username} đăng nhập thành công")

            # Map vai trò từ database sang frontend format
            # Frontend: 'Admin', 'Giảng viên', 'Sinh viên'
            vai_tro = self.current_user.get('vai_tro', '').lower()
            if vai_tro == 'admin':
                self.current_user['RoleName'] = 'Admin'
            elif vai_tro == 'giangvien':
                self.current_user['RoleName'] = 'Giảng viên'
            elif vai_tro == 'sinhvien':
                self.current_user['RoleName'] = 'Sinh viên'
            else:
                self.current_user['RoleName'] = vai_tro
            
            # Map username
            self.current_user['Username'] = self.current_user.get('username') or self.current_user.get('ho_ten')

            return True, "Đăng nhập thành công", self.current_user

        except Exception as e:
            logger.error(f"Lỗi đăng nhập: {str(e)}")
            return False, f"Lỗi hệ thống: {str(e)}", None

    def logout(self):
        """Đăng xuất khỏi hệ thống"""
        if self.current_user:
            logger.info(f"User {self.current_user.get('Username')} đăng xuất")
        self.current_user = None
        self.session_start_time = None
        self.api_client.set_auth_token(None) # Xóa token

    def is_authenticated(self) -> bool:
        """Kiểm tra user đã đăng nhập chưa"""
        return self.current_user is not None

    def get_current_user(self) -> Optional[Dict[str, Any]]:
        """Lấy thông tin user hiện tại"""
        return self.current_user

    def get_user_role(self) -> Optional[str]:
        """Lấy vai trò của user hiện tại"""
        if self.current_user:
            return self.current_user.get('RoleName') or self.current_user.get('vai_tro')
        return None

    def is_admin(self) -> bool:
        """Kiểm tra user có phải admin không"""
        return self.get_user_role() == 'Admin'

    def is_teacher(self) -> bool:
        """Kiểm tra user có phải giảng viên không"""
        return self.get_user_role() == 'Giảng viên'

    def is_student(self) -> bool:
        """Kiểm tra user có phải sinh viên không"""
        return self.get_user_role() == 'Sinh viên'

    def change_password(self, old_password: str, new_password: str) -> tuple[bool, str]:
        logger.warning("Chức năng đổi mật khẩu chưa được kết nối với API.")
        return False, "Chức năng này chưa được hỗ trợ."

    def session_is_valid(self, timeout_minutes: int = 60) -> bool:
        if not self.is_authenticated():
            return False

        if not self.session_start_time:
            return False

        elapsed = datetime.now() - self.session_start_time
        return elapsed < timedelta(minutes=timeout_minutes)


_auth_instance = None

def get_auth() -> 'AuthService':
    """Lấy instance AuthService singleton"""
    global _auth_instance
    if _auth_instance is None:
        _auth_instance = AuthService()
    return _auth_instance