"""Dialog thêm/sửa khoa, sử dụng API service"""
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from services.department_service import DepartmentService
import logging

logger = logging.getLogger(__name__)


class DepartmentDialog(QDialog):
    """Dialog để thêm hoặc chỉnh sửa khoa qua API"""

    def __init__(self, parent=None, department_id=None):
        super().__init__(parent)
        self.department_id = department_id
        self.department_service = DepartmentService()

        self.setWindowTitle("Thêm khoa" if department_id is None else "Chỉnh sửa khoa")
        self.setModal(True)
        self.setMinimumWidth(500)

        self.init_ui()

        if department_id:
            self.load_department_data()

    def init_ui(self):
        """Khởi tạo giao diện"""
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)

        form_layout = QFormLayout()
        form_layout.setSpacing(15)
        form_layout.setLabelAlignment(Qt.AlignRight)

        self.dept_code_edit = QLineEdit()
        self.dept_code_edit.setPlaceholderText("Ví dụ: CNTT")
        form_layout.addRow("<b>Mã khoa:</b>", self.dept_code_edit)

        self.dept_name_edit = QLineEdit()
        self.dept_name_edit.setPlaceholderText("Ví dụ: Công nghệ Thông tin")
        form_layout.addRow("<b>Tên khoa:</b>", self.dept_name_edit)

        self.dept_phone_edit = QLineEdit()
        self.dept_phone_edit.setPlaceholderText("Số điện thoại")
        form_layout.addRow("<b>Số điện thoại:</b>", self.dept_phone_edit)

        self.dept_email_edit = QLineEdit()
        self.dept_email_edit.setPlaceholderText("email")
        form_layout.addRow("<b>Email:</b>", self.dept_email_edit)

        self.dept_office_edit = QLineEdit()
        self.dept_office_edit.setPlaceholderText("Phòng làm việc")
        form_layout.addRow("<b>Phòng làm việc:</b>", self.dept_office_edit)

        layout.addLayout(form_layout)
        layout.addSpacing(20)

        button_layout = QHBoxLayout()
        save_btn = QPushButton("Lưu")
        save_btn.clicked.connect(self.save_department)
        cancel_btn = QPushButton("Hủy")
        cancel_btn.clicked.connect(self.reject)

        button_layout.addStretch()
        button_layout.addWidget(save_btn)
        button_layout.addWidget(cancel_btn)

        layout.addLayout(button_layout)
        self.setLayout(layout)

    def load_department_data(self):
        """Load thông tin khoa từ API"""
        department = self.department_service.get_department_by_id(self.department_id)
        if department:
            self.dept_code_edit.setText(department.get('ma_khoa', ''))
            self.dept_code_edit.setEnabled(False)  # Không cho sửa mã khoa
            self.dept_name_edit.setText(department.get('ten_khoa', ''))
            self.dept_phone_edit.setText(department.get('so_dien_thoai', '') or '')
            self.dept_email_edit.setText(department.get('email', '') or '')
            self.dept_office_edit.setText(department.get('phong_lam_viec', '') or '')
        else:
            QMessageBox.critical(self, "Lỗi", f"Không tìm thấy khoa với mã {self.department_id}.")
            self.reject()

    def save_department(self):
        """Lưu thông tin khoa qua API"""
        try:
            dept_code = self.dept_code_edit.text().strip()
            dept_name = self.dept_name_edit.text().strip()
            dept_phone = self.dept_phone_edit.text().strip()
            dept_email = self.dept_email_edit.text().strip()
            dept_office = self.dept_office_edit.text().strip()

            if not dept_code or not dept_name:
                QMessageBox.warning(self, "Thiếu thông tin", "Mã khoa và Tên khoa là bắt buộc.")
                return

            department_data = {
                "ma_khoa": dept_code,
                "ten_khoa": dept_name,
                "so_dien_thoai": dept_phone if dept_phone else None,
                "email": dept_email if dept_email else None,
                "phong_lam_viec": dept_office if dept_office else None
            }

            if self.department_id:
                # === CẬP NHẬT ===
                success, message = self.department_service.update_department(self.department_id, department_data)
            else:
                # === TẠO MỚI ===
                success, message = self.department_service.create_department(department_data)

            if success:
                QMessageBox.information(self, "Thành công", message)
                self.accept()
            else:
                QMessageBox.critical(self, "Lỗi", f"Không thể lưu: {message}")

        except Exception as e:
            logger.error(f"Lỗi khi lưu khoa: {e}")
            QMessageBox.critical(self, "Lỗi hệ thống", f"Đã xảy ra lỗi không mong muốn: {e}")
