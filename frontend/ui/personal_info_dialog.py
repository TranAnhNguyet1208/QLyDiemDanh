
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
                             QTextEdit, QPushButton, QMessageBox, QDateEdit, QComboBox,
                             QFrame, QGroupBox, QWidget, QApplication, QFormLayout)
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtGui import QIcon, QPixmap
from services.api_service import get_api_client
import logging

logger = logging.getLogger(__name__)


class PasswordChangeDialog(QDialog):
    """Dialog để đổi mật khẩu"""

    def __init__(self, parent, ma_nguoi_dung):
        super().__init__(parent)
        self.ma_nguoi_dung = ma_nguoi_dung
        self.api_client = get_api_client()

        self.setWindowTitle("Đổi mật khẩu")
        self.setFixedSize(400, 250)
        self.setModal(True)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)

        # Form layout for inputs
        form_layout = QFormLayout()
        
        self.old_password_input = QLineEdit()
        self.old_password_input.setEchoMode(QLineEdit.Password)
        form_layout.addRow("Mật khẩu cũ:", self.old_password_input)

        self.new_password_input = QLineEdit()
        self.new_password_input.setEchoMode(QLineEdit.Password)
        form_layout.addRow("Mật khẩu mới:", self.new_password_input)

        self.confirm_password_input = QLineEdit()
        self.confirm_password_input.setEchoMode(QLineEdit.Password)
        form_layout.addRow("Xác nhận MK:", self.confirm_password_input)
        
        layout.addLayout(form_layout)

        # Buttons
        button_layout = QHBoxLayout()
        
        change_btn = QPushButton("🔄 Đổi mật khẩu")
        change_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                padding: 8px 16px;
                border: none;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        change_btn.clicked.connect(self.change_password)
        
        cancel_btn = QPushButton("❌ Hủy")
        cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                padding: 8px 16px;
                border: none;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """)
        cancel_btn.clicked.connect(self.reject)
        
        button_layout.addWidget(change_btn)
        button_layout.addWidget(cancel_btn)
        layout.addLayout(button_layout)

    def change_password(self):
        old_pass = self.old_password_input.text()
        new_pass = self.new_password_input.text()
        confirm_pass = self.confirm_password_input.text()

        if not old_pass or not new_pass or not confirm_pass:
            QMessageBox.warning(self, "Lỗi", "Vui lòng điền đầy đủ thông tin!")
            return

        if new_pass != confirm_pass:
            QMessageBox.warning(self, "Lỗi", "Mật khẩu xác nhận không khớp!")
            return

        try:
            success, message = self.api_client.change_password(self.ma_nguoi_dung, old_pass, new_pass)
            if success:
                QMessageBox.information(self, "Thành công", "Đổi mật khẩu thành công!")
                self.accept()
            else:
                QMessageBox.warning(self, "Lỗi", f"Đổi mật khẩu thất bại: {message}")
        except Exception as e:
            logger.error(f"Lỗi đổi mật khẩu: {e}")
            QMessageBox.critical(self, "Lỗi", f"Lỗi: {str(e)}")


class PersonalInfoDialog(QDialog):
    """Dialog để xem và sửa thông tin cá nhân"""

    def __init__(self, parent, user_data):
        super().__init__(parent)
        self.user_data = user_data
        self.api_client = get_api_client()

        # Lấy ID người dùng từ user_data
        self.ma_nguoi_dung = user_data.get('user_id') or user_data.get('ma_nguoi_dung') or user_data.get('student_code', '')
        self.user_role = user_data.get('role', '')

        self.setWindowTitle("Thông tin cá nhân")
        self.resize(600, 700)
        
        # Center dialog
        if parent:
            self.move(parent.window().frameGeometry().center() - self.rect().center())
        else:
            screen_geometry = QApplication.desktop().screenGeometry()
            x = (screen_geometry.width() - self.width()) // 2
            y = (screen_geometry.height() - self.height()) // 2
            self.move(x, y)
            
        self.init_ui()
        self.load_data()

    def init_ui(self):
        """Khởi tạo giao diện"""
        layout = QVBoxLayout(self)

        # Thông tin cơ bản
        basic_group = QGroupBox("Thông tin cơ bản")
        basic_layout = QVBoxLayout()

        # Họ tên
        ho_ten_layout = QHBoxLayout()
        ho_ten_layout.addWidget(QLabel("Họ tên:"))
        self.ho_ten_input = QLineEdit()
        ho_ten_layout.addWidget(self.ho_ten_input)
        basic_layout.addLayout(ho_ten_layout)

        # Email
        email_layout = QHBoxLayout()
        email_layout.addWidget(QLabel("Email:"))
        self.email_input = QLineEdit()
        email_layout.addWidget(self.email_input)
        basic_layout.addLayout(email_layout)

        # Số điện thoại
        sdt_layout = QHBoxLayout()
        sdt_layout.addWidget(QLabel("Số điện thoại:"))
        self.sdt_input = QLineEdit()
        sdt_layout.addWidget(self.sdt_input)
        basic_layout.addLayout(sdt_layout)

        # Mật khẩu (chỉ hiển thị, không cho sửa trực tiếp)
        password_layout = QHBoxLayout()
        password_layout.addWidget(QLabel("Mật khẩu:"))
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setReadOnly(True)
        password_layout.addWidget(self.password_input)

        # Nút hiển thị/ẩn mật khẩu
        self.eye_btn = QPushButton("👁")
        self.eye_btn.setFixedSize(30, 30)
        self.eye_btn.setStyleSheet("QPushButton { border: none; background: transparent; }")
        self.eye_btn.clicked.connect(self.toggle_password_visibility)
        password_layout.addWidget(self.eye_btn)
        basic_layout.addLayout(password_layout)

        basic_group.setLayout(basic_layout)
        layout.addWidget(basic_group)

        # Thông tin theo vai trò
        self.role_group = QGroupBox("Thông tin chuyên biệt")
        role_layout = QVBoxLayout()

        # Ngày sinh (cho sinh viên)
        self.birth_widget = QWidget()
        self.birth_layout = QHBoxLayout(self.birth_widget)
        self.birth_layout.setContentsMargins(0, 0, 0, 0)
        self.birth_layout.addWidget(QLabel("Ngày sinh:"))
        self.ns_input = QDateEdit()
        self.ns_input.setCalendarPopup(True)
        self.ns_input.setDisplayFormat("dd/MM/yyyy")
        self.birth_layout.addWidget(self.ns_input)
        role_layout.addWidget(self.birth_widget)

        # Giới tính (cho sinh viên)
        self.gender_widget = QWidget()
        self.gender_layout = QHBoxLayout(self.gender_widget)
        self.gender_layout.setContentsMargins(0, 0, 0, 0)
        self.gender_layout.addWidget(QLabel("Giới tính:"))
        self.gt_combo = QComboBox()
        self.gt_combo.addItems(["Nam", "Nữ", "Khác"])
        self.gender_layout.addWidget(self.gt_combo)
        role_layout.addWidget(self.gender_widget)

        # Địa chỉ (cho sinh viên)
        self.address_widget = QWidget()
        self.address_layout = QHBoxLayout(self.address_widget)
        self.address_layout.setContentsMargins(0, 0, 0, 0)
        self.address_layout.addWidget(QLabel("Địa chỉ:"))
        self.dc_input = QTextEdit()
        self.dc_input.setMaximumHeight(60)
        self.address_layout.addWidget(self.dc_input)
        role_layout.addWidget(self.address_widget)

        # Học vị (cho giảng viên)
        self.degree_widget = QWidget()
        self.degree_layout = QHBoxLayout(self.degree_widget)
        self.degree_layout.setContentsMargins(0, 0, 0, 0)
        self.degree_layout.addWidget(QLabel("Học vị:"))
        self.degree_input = QLineEdit()
        self.degree_layout.addWidget(self.degree_input)
        role_layout.addWidget(self.degree_widget)

        # Khoa (cho giảng viên) - chỉ hiển thị tên
        self.department_widget = QWidget()
        self.department_layout = QHBoxLayout(self.department_widget)
        self.department_layout.setContentsMargins(0, 0, 0, 0)
        self.department_layout.addWidget(QLabel("Khoa:"))
        self.department_label = QLabel()
        self.department_layout.addWidget(self.department_label)
        role_layout.addWidget(self.department_widget)

        self.role_group.setLayout(role_layout)
        layout.addWidget(self.role_group)

        # Buttons
        button_layout = QHBoxLayout()

        # Nút đổi mật khẩu
        change_pass_btn = QPushButton("🔑 Đổi mật khẩu")
        change_pass_btn.setStyleSheet("""
            QPushButton {
                background-color: #f39c12;
                color: white;
                padding: 8px 16px;
                border: none;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #d35400;
            }
        """)
        change_pass_btn.clicked.connect(self.show_password_change_dialog)
        
        save_btn = QPushButton("💾 Lưu")
        save_btn.setStyleSheet("""
            QPushButton {
                background-color: #2ecc71;
                color: white;
                padding: 8px 16px;
                border: none;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #27ae60;
            }
        """)
        save_btn.clicked.connect(self.save_info)
        
        cancel_btn = QPushButton("❌ Hủy")
        cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                padding: 8px 16px;
                border: none;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """)
        cancel_btn.clicked.connect(self.reject)

        button_layout.addWidget(change_pass_btn)
        button_layout.addStretch()
        button_layout.addWidget(save_btn)
        button_layout.addWidget(cancel_btn)
        
        layout.addLayout(button_layout)

    def toggle_password_visibility(self):
        """Chuyển đổi chế độ hiển thị mật khẩu"""
        if self.password_input.echoMode() == QLineEdit.Password:
            self.password_input.setEchoMode(QLineEdit.Normal)
            self.eye_btn.setText("🙈")
        else:
            self.password_input.setEchoMode(QLineEdit.Password)
            self.eye_btn.setText("👁")

    def show_password_change_dialog(self):
        """Hiển thị dialog đổi mật khẩu"""
        dialog = PasswordChangeDialog(self, self.ma_nguoi_dung)
        dialog.exec_()

    def load_data(self):
        """Load thông tin cá nhân từ API"""
        try:
            success, info_data = self.api_client.get_personal_info(self.ma_nguoi_dung)

            if success and info_data:
                # Thông tin cơ bản
                self.ho_ten_input.setText(info_data.get('ho_ten', ''))
                self.email_input.setText(info_data.get('email', ''))
                self.sdt_input.setText(info_data.get('so_dien_thoai', ''))
                self.password_input.setText(info_data.get('mat_khau', ''))

                user_role = info_data.get('vai_tro', '')

                # Ẩn/hiện các trường theo vai trò
                if user_role == 'sinhvien':
                    # Hiển thị thông tin sinh viên
                    self.birth_widget.setVisible(True)
                    self.gender_widget.setVisible(True)
                    self.address_widget.setVisible(True)
                    self.degree_widget.setVisible(False)
                    self.department_widget.setVisible(False)

                    # Load dữ liệu sinh viên
                    ngay_sinh = info_data.get('ngay_sinh', '')
                    if ngay_sinh:
                        try:
                            date_obj = QDate.fromString(str(ngay_sinh), 'yyyy-MM-dd')
                            if date_obj.isValid():
                                self.ns_input.setDate(date_obj)
                        except:
                            pass

                    gioi_tinh = info_data.get('gioi_tinh', 'Nam')
                    if gioi_tinh:
                        index = self.gt_combo.findText(gioi_tinh)
                        if index >= 0:
                            self.gt_combo.setCurrentIndex(index)

                    self.dc_input.setText(info_data.get('dia_chi', ''))

                elif user_role == 'giangvien':
                    # Hiển thị thông tin giảng viên
                    self.birth_widget.setVisible(False)
                    self.gender_widget.setVisible(False)
                    self.address_widget.setVisible(False)
                    self.degree_widget.setVisible(True)
                    self.department_widget.setVisible(True)

                    # Load dữ liệu giảng viên
                    self.degree_input.setText(info_data.get('hoc_vi', ''))
                    self.department_label.setText(info_data.get('ten_khoa', ''))

                else:
                    # Ẩn tất cả thông tin chuyên biệt
                    self.birth_widget.setVisible(False)
                    self.gender_widget.setVisible(False)
                    self.address_widget.setVisible(False)
                    self.degree_widget.setVisible(False)
                    self.department_widget.setVisible(False)

            else:
                logger.warning(f"Không thể tải thông tin cá nhân: {info_data}")

        except Exception as e:
            logger.error(f"Lỗi load thông tin cá nhân: {e}")

    def save_info(self):
        """Lưu thông tin cá nhân"""
        try:
            info_data = {
                'ho_ten': self.ho_ten_input.text(),
                'email': self.email_input.text(),
                'so_dien_thoai': self.sdt_input.text()
            }

            # Thêm thông tin theo vai trò
            if self.birth_widget.isVisible():
                info_data.update({
                    'ngay_sinh': self.ns_input.date().toString('yyyy-MM-dd'),
                    'gioi_tinh': self.gt_combo.currentText(),
                    'dia_chi': self.dc_input.toPlainText()
                })

            if self.degree_widget.isVisible():
                info_data['hoc_vi'] = self.degree_input.text()

            success, message = self.api_client.update_personal_info(self.ma_nguoi_dung, info_data)

            if success:
                QMessageBox.information(self, "Thành công", "Cập nhật thông tin thành công!")
                self.accept()
            else:
                QMessageBox.warning(self, "Lỗi", f"Cập nhật thất bại: {message}")

        except Exception as e:
            logger.error(f"Lỗi lưu thông tin cá nhân: {e}")
            QMessageBox.critical(self, "Lỗi", f"Lỗi: {str(e)}")
