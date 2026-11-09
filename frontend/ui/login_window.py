from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from services.auth_service import get_auth
import logging

logger = logging.getLogger(__name__)

class LoginWindow(QMainWindow):
    login_successful = pyqtSignal(dict)

    def __init__(self):
        super().__init__()
        self.auth_service = get_auth()
        self.setWindowTitle("Đăng nhập hệ thống")
        self.setFixedSize(1200, 1500)
        self.init_ui()

    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        central_widget.setStyleSheet("""
            QWidget {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #2c3e50, stop:1 #3498db);
            }
        """)
        
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(100, 100, 100, 100)
        layout.setSpacing(50)
        
        title_label = QLabel("EduCheck")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 80px;
                font-weight: bold;
                background: transparent;
                margin-bottom: 40px;
            }
        """)
        layout.addWidget(title_label)
        
        form_frame = QFrame()
        form_frame.setStyleSheet("""
            QFrame {
                background: white;
                border-radius: 30px;
                padding: 50px;
            }
            QLineEdit {
                border: 3px solid #ddd;
                border-radius: 15px;
                padding: 10px 20px;
                font-size: 35px;
                background: #f9f9f9;
                color: #333;
                min-height: 80px;
            }
            QLineEdit:focus {
                border: 5px solid #3498db;
                background: white;
            }
            QLabel {
                color: #333;
                font-weight: bold;
                font-size: 35px;
                background: transparent;
                margin-bottom: 5px;
            }
        """)
        
        form_layout = QVBoxLayout(form_frame)
        form_layout.setSpacing(35)
        
        user_label = QLabel("Tên đăng nhập")
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Nhập tên đăng nhập...")
        form_layout.addWidget(user_label)
        form_layout.addWidget(self.username_input)
        
        pass_label = QLabel("Mật khẩu")
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setPlaceholderText("Nhập mật khẩu...")
        self.password_input.returnPressed.connect(self.handle_login)
        form_layout.addWidget(pass_label)
        form_layout.addWidget(self.password_input)
        
        self.login_btn = QPushButton("ĐĂNG NHẬP")
        self.login_btn.setCursor(Qt.PointingHandCursor)
        self.login_btn.setFixedHeight(130)
        self.login_btn.clicked.connect(self.handle_login)
        self.login_btn.setStyleSheet("""
            QPushButton {
                background-color: #2980b9;
                color: white;
                border: none;
                border-radius: 20px;
                font-size: 50px;
                font-weight: bold;
                margin-top: 30px;
                padding: 10px;
            }
            QPushButton:hover {
                background-color: #3498db;
            }
            QPushButton:pressed {
                background-color: #2573a7;
            }
        """)
        form_layout.addWidget(self.login_btn)
        
        layout.addWidget(form_frame)
        layout.addStretch()
        
        footer_label = QLabel("© 2025 University Attendance System")
        footer_label.setAlignment(Qt.AlignCenter)
        footer_label.setStyleSheet("color: rgba(255,255,255,0.7); font-size: 30px; background: transparent;")
        layout.addWidget(footer_label)

    def handle_login(self):
        username = self.username_input.text().strip()
        password = self.password_input.text().strip()
        
        if not username or not password:
            QMessageBox.warning(self, "Cảnh báo", "Vui lòng nhập đầy đủ tên đăng nhập và mật khẩu!")
            return
            
        self.login_btn.setEnabled(False)
        self.login_btn.setText("Đang xử lý...")
        QApplication.processEvents()
        
        try:
            success, message, user_data = self.auth_service.login(username, password)
            
            if success:
                logger.info(f"Login successful for user: {username}")
                self.login_successful.emit(user_data)
            else:
                QMessageBox.warning(self, "Đăng nhập thất bại", message)
                
        except Exception as e:
            logger.error(f"Login error: {e}")
            QMessageBox.critical(self, "Lỗi", f"Có lỗi xảy ra khi đăng nhập:\n{str(e)}")
            
        finally:
            self.login_btn.setEnabled(True)
            self.login_btn.setText("ĐĂNG NHẬP")