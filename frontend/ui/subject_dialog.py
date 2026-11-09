"""Dialog thêm/sửa môn học, sử dụng API service"""
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

from services.subject_service import SubjectService
from services.department_service import DepartmentService
import logging

logger = logging.getLogger(__name__)


class SubjectDialog(QDialog):
    """Dialog để thêm hoặc chỉnh sửa môn học qua API"""

    def __init__(self, parent=None, subject_code=None):
        super().__init__(parent)
        self.subject_code = subject_code
        self.subject_service = SubjectService()
        self.department_service = DepartmentService()

        self.setWindowTitle("Thêm môn học" if subject_code is None else "Chỉnh sửa môn học")
        self.setModal(True)
        self.setMinimumWidth(500)

        self.init_ui()

        if subject_code:
            self.load_subject(subject_code)

    def init_ui(self):
        """Khởi tạo giao diện"""
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)

        form_layout = QFormLayout()
        form_layout.setSpacing(15)
        form_layout.setLabelAlignment(Qt.AlignRight)

        self.subject_code_edit = QLineEdit()
        self.subject_code_edit.setPlaceholderText("Ví dụ: CNTT101")
        form_layout.addRow("<b>Mã môn học:</b>", self.subject_code_edit)

        self.subject_name_edit = QLineEdit()
        self.subject_name_edit.setPlaceholderText("Ví dụ: Lập trình Python")
        form_layout.addRow("<b>Tên môn học:</b>", self.subject_name_edit)

        self.credits_spin = QSpinBox()
        self.credits_spin.setRange(1, 10)
        self.credits_spin.setValue(3)
        form_layout.addRow("<b>Số tín chỉ:</b>", self.credits_spin)

        self.department_combo = QComboBox()
        self.load_departments()
        form_layout.addRow("<b>Khoa:</b>", self.department_combo)

        layout.addLayout(form_layout)
        layout.addSpacing(20)

        button_layout = QHBoxLayout()
        save_btn = QPushButton("Lưu")
        save_btn.clicked.connect(self.save_subject)
        cancel_btn = QPushButton("Hủy")
        cancel_btn.clicked.connect(self.reject)

        button_layout.addStretch()
        button_layout.addWidget(save_btn)
        button_layout.addWidget(cancel_btn)

        layout.addLayout(button_layout)
        self.setLayout(layout)

    def load_departments(self):
        """Load danh sách khoa từ API"""
        departments = self.department_service.get_all_departments()
        self.department_combo.clear()
        self.departments_map = {}
        for dept in departments:
            display_name = f"{dept.get('ma_khoa')} - {dept.get('ten_khoa')}"
            self.department_combo.addItem(display_name, userData=dept.get('ma_khoa'))
            self.departments_map[dept.get('ma_khoa')] = display_name

    def load_subject(self, subject_code):
        """Load thông tin môn học từ API"""
        subject = self.subject_service.get_subject_by_code(subject_code)
        if subject is not None:
            self.subject_code_edit.setText(subject.get('ma_mon_hoc', ''))
            self.subject_code_edit.setEnabled(False)
            self.subject_name_edit.setText(subject.get('ten_mon_hoc', ''))
            self.credits_spin.setValue(subject.get('so_tin_chi', 3))
            ma_khoa = subject.get('ma_khoa', '')
            index = self.department_combo.findData(ma_khoa)
            if index >= 0:
                self.department_combo.setCurrentIndex(index)
        else:
            QMessageBox.critical(self, "Lỗi", f"Không tìm thấy môn học với mã {subject_code}.")
            self.reject()

    def save_subject(self):
        """Lưu thông tin môn học qua API"""
        try:
            subject_code = self.subject_code_edit.text().strip()
            subject_name = self.subject_name_edit.text().strip()
            credits = self.credits_spin.value()
            ma_khoa = self.department_combo.currentData()
            
            if not subject_code or not subject_name:
                QMessageBox.warning(self, "Thiếu thông tin", "Mã môn học và Tên môn học là bắt buộc.")
                return

            if not ma_khoa:
                QMessageBox.warning(self, "Thiếu thông tin", "Phải chọn một khoa.")
                return

            subject_data = {
                "ma_mon_hoc": subject_code,
                "ten_mon_hoc": subject_name,
                "so_tin_chi": credits,
                "ma_khoa": ma_khoa
            }

            if self.subject_code:
                success, message = self.subject_service.update_subject(self.subject_code, subject_data)
            else:
                success, message = self.subject_service.create_subject(subject_data)

            if success:
                QMessageBox.information(self, "Thành công", message)
                self.accept()
            else:
                QMessageBox.critical(self, "Lỗi", f"Không thể lưu: {message}")

        except Exception as e:
            logger.error(f"Lỗi khi lưu môn học: {e}")
            QMessageBox.critical(self, "Lỗi hệ thống", f"Đã xảy ra lỗi không mong muốn: {e}")
