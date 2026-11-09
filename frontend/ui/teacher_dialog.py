from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from services.teacher_service import TeacherService
from services.api_service import get_api_client
import logging

logger = logging.getLogger(__name__)


class TeacherDialog(QDialog):
    """Dialog để thêm hoặc chỉnh sửa giảng viên qua API"""

    def __init__(self, parent=None, teacher_code=None):
        super().__init__(parent)
        self.teacher_code = teacher_code
        self.teacher_service = TeacherService()
        self.api_client = get_api_client()

        self.setWindowTitle("Thêm giảng viên" if teacher_code is None else "Chỉnh sửa giảng viên")
        self.setModal(True)
        self.setMinimumWidth(550)

        self.init_ui()

        if teacher_code:
            self.load_teacher_data()

    def init_ui(self):
        """Khởi tạo giao diện"""
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        
        form_layout = QFormLayout()
        form_layout.setSpacing(15)
        form_layout.setLabelAlignment(Qt.AlignRight)

        self.teacher_code_edit = QLineEdit()
        self.teacher_code_edit.setPlaceholderText("GV001")
        form_layout.addRow("<b>Mã giảng viên:</b>", self.teacher_code_edit)

        self.fullname_edit = QLineEdit()
        self.fullname_edit.setPlaceholderText("Họ và tên đầy đủ")
        form_layout.addRow("<b>Họ tên:</b>", self.fullname_edit)

        if self.teacher_code:
            self.email_edit = QLineEdit()
            self.email_edit.setPlaceholderText("email@example.com")
            form_layout.addRow("<b>Email:</b>", self.email_edit)

            self.phone_edit = QLineEdit()
            self.phone_edit.setPlaceholderText("0123456789")
            form_layout.addRow("<b>Số điện thoại:</b>", self.phone_edit)

            self.status_combo = QComboBox()
            self.status_combo.addItems(["Hoạt động", "Ngừng hoạt động"])
            form_layout.addRow("<b>Trạng thái:</b>", self.status_combo)

        self.department_combo = QComboBox()
        self.department_combo.setMinimumWidth(200)
        self.load_departments()
        form_layout.addRow("<b>Khoa:</b>", self.department_combo)

        self.degree_combo = QComboBox()
        self.degree_combo.addItems(["Thạc sĩ", "Tiến sĩ", "Giáo sư", "Phó Giáo sư", "Cử nhân"])
        form_layout.addRow("<b>Học vị:</b>", self.degree_combo)

        layout.addLayout(form_layout)
        layout.addSpacing(20)
        
        button_layout = QHBoxLayout()
        save_btn = QPushButton("Lưu")
        save_btn.clicked.connect(self.save_teacher)
        cancel_btn = QPushButton("Hủy")
        cancel_btn.clicked.connect(self.reject)

        button_layout.addStretch()
        button_layout.addWidget(save_btn)
        button_layout.addWidget(cancel_btn)

        layout.addLayout(button_layout)
        self.setLayout(layout)

    def load_departments(self):
        """Load danh sách khoa từ API"""
        success, departments = self.api_client.get_all_departments()
        if success:
            self.department_combo.addItem("-- Chọn khoa --", None)
            for dept in departments:
                self.department_combo.addItem(dept['ten_khoa'], dept['ma_khoa'])
        else:
            logger.error(f"Lỗi load khoa từ API: {departments}")
            QMessageBox.warning(self, "Lỗi", "Không thể tải danh sách khoa.")

    def load_teacher_data(self):
        """Load thông tin giảng viên từ API"""
        teacher = self.teacher_service.get_teacher_by_code(self.teacher_code)
        if teacher:
            self.teacher_code_edit.setText(teacher.get('ma_giang_vien', ''))
            self.teacher_code_edit.setEnabled(False)
            self.fullname_edit.setText(teacher.get('ho_ten', ''))
            self.email_edit.setText(teacher.get('email', '') or '')
            self.phone_edit.setText(teacher.get('so_dien_thoai', '') or '')

            trang_thai = teacher.get('trang_thai', 'Hoạt động')
            status_index = self.status_combo.findText(trang_thai, Qt.MatchFixedString)
            if status_index >= 0:
                self.status_combo.setCurrentIndex(status_index)

            degree = teacher.get('hoc_vi', 'Thạc sĩ')
            degree_index = self.degree_combo.findText(degree, Qt.MatchFixedString)
            if degree_index >= 0:
                self.degree_combo.setCurrentIndex(degree_index)

            dept_id = teacher.get('ma_khoa')
            dept_index = self.department_combo.findData(dept_id)
            if dept_index >= 0:
                self.department_combo.setCurrentIndex(dept_index)
        else:
            QMessageBox.critical(self, "Lỗi", f"Không tìm thấy giảng viên với mã {self.teacher_code}.")
            self.reject()

    def save_teacher(self):
        """Lưu thông tin giảng viên qua API"""
        try:
            teacher_code = self.teacher_code_edit.text().strip()
            fullname = self.fullname_edit.text().strip()
            if not teacher_code or not fullname:
                QMessageBox.warning(self, "Thiếu thông tin", "Mã giảng viên và Họ tên là bắt buộc.")
                return

            if self.teacher_code:
                current_teacher_data = self.teacher_service.get_teacher_by_code(self.teacher_code)
                if not current_teacher_data or 'ma_nguoi_dung' not in current_teacher_data:
                    QMessageBox.critical(self, "Lỗi", "Không thể lấy mã người dùng để cập nhật.")
                    return

                teacher_data = {
                    "ma_giang_vien": teacher_code,
                    "ho_ten": fullname,
                    "email": self.email_edit.text().strip() or None,
                    "so_dien_thoai": self.phone_edit.text().strip() or None,
                    "trang_thai": self.status_combo.currentText(),
                    "ma_khoa": self.department_combo.currentData(),
                    "hoc_vi": self.degree_combo.currentText()
                }

                user_id = current_teacher_data['ma_nguoi_dung']
                success, message = self.teacher_service.update_teacher(user_id, teacher_data)
            else:
                dept_id = self.department_combo.currentData()
                if not dept_id:
                    QMessageBox.warning(self, "Thiếu thông tin", "Khoa là bắt buộc.")
                    return

                teacher_data = {
                    "ma_gv": teacher_code,
                    "ho_ten": fullname,
                    "ma_khoa": dept_id,
                    "hoc_vi": self.degree_combo.currentText()
                }

                success, message = self.teacher_service.create_teacher(teacher_data)

            if success:
                QMessageBox.information(self, "Thành công", message)
                self.accept()
            else:
                QMessageBox.critical(self, "Lỗi", f"Không thể lưu thông tin: {message}")

        except Exception as e:
            logger.error(f"Lỗi khi lưu giảng viên: {e}")
            QMessageBox.critical(self, "Lỗi hệ thống", f"Đã xảy ra lỗi không mong muốn: {e}")