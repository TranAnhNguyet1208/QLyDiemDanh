"""
Main application entry point - Hệ thống quản lý điểm danh sinh viên
"""
import sys
import os
import logging
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QMessageBox
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.auth_service import get_auth
from ui.login_window import LoginWindow

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('app.log', encoding='utf-8')
    ]
)
logger = logging.getLogger(__name__)

class AttendanceManagementApp:
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.app.setStyle('Fusion')
        
        self.auth_service = get_auth()
        self.login_window = None
        self.dashboard_window = None
        
        self.setup_styles()
    
    def setup_styles(self):
        """Thiết lập style chung cho ứng dụng"""
        self.app.setStyleSheet("""
            QMainWindow, QWidget {
                font-family: 'Segoe UI', Arial, sans-serif;
                font-size: 10pt;
            }
            QTableWidget {
                gridline-color: #dcdcdc;
                selection-background-color: #e0e0e0;
            }
            QTableWidget::item {
                padding: 5px;
            }
            QHeaderView::section {
                background-color: #f0f0f0;
                padding: 8px;
                border: 1px solid #dcdcdc;
                font-weight: bold;
            }
            QPushButton {
                min-height: 30px;
                padding: 5px 15px;
            }
            QLineEdit, QComboBox, QDateEdit, QTimeEdit {
                padding: 8px;
                border: 1px solid #ccc;
                border-radius: 3px;
            }
            QLineEdit:focus, QComboBox:focus {
                border: 2px solid #3498db;
            }
        """)

    def show_login(self):
        """Hiển thị màn hình đăng nhập"""
        self.login_window = LoginWindow()
        self.login_window.login_successful.connect(self.on_login_success)
        self.login_window.show()
    
    def on_login_success(self, user_data):
        """
        Xử lý sau khi đăng nhập thành công
        Điều hướng đến dashboard tương ứng
        """
        role = user_data.get('RoleName')
        
        logger.info(f"User {user_data.get('Username')} logged in as {role}")
        
        try:
            if role == 'Admin':
                from ui.admin_dashboard import AdminDashboard
                self.dashboard_window = AdminDashboard(user_data)
            elif role == 'Giảng viên':
                from ui.teacher_dashboard import TeacherDashboard
                self.dashboard_window = TeacherDashboard(user_data)
            elif role == 'Sinh viên':
                from ui.student_dashboard import StudentDashboard
                self.dashboard_window = StudentDashboard(user_data)
            else:
                QMessageBox.critical(None, 'Lỗi', f'Vai trò không hợp lệ: {role}')
                return
            
            self.dashboard_window.logout_requested.connect(self.on_logout)
            
            self.dashboard_window.show()
            self.login_window.close()
            
        except ImportError as e:
            logger.error(f"Lỗi import dashboard: {str(e)}")
            QMessageBox.critical(
                None, 
                'Lỗi', 
                f'Không thể tải giao diện cho vai trò {role}\n'
                f'Chi tiết: {str(e)}'
            )
            self.show_login()
    
    def on_logout(self):
        """Xử lý đăng xuất"""
        reply = QMessageBox.question(
            None,
            'Xác nhận',
            'Bạn có chắc chắn muốn đăng xuất?',
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            if self.dashboard_window:
                self.dashboard_window.close()
                self.dashboard_window = None
            
            self.auth_service.logout()
            
            logger.info("User logged out")
            
            self.show_login()
    
    def run(self):
        """Khởi chạy ứng dụng"""
        logger.info("Starting Attendance Management System")
        
        self.show_login()
        
        return self.app.exec_()


def main():
    try:
        app = AttendanceManagementApp()
        sys.exit(app.run())
    except Exception as e:
        logger.critical(f"Critical error: {str(e)}", exc_info=True)
        # Create a simple app to show error if main app failed
        if not QApplication.instance():
            app = QApplication(sys.argv)
        QMessageBox.critical(
            None,
            'Lỗi nghiêm trọng',
            f'Ứng dụng gặp lỗi nghiêm trọng:\n{str(e)}'
        )
        sys.exit(1)


if __name__ == '__main__':
    main()
