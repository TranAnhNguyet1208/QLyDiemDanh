
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from services.student_service import StudentService
from services.api_service import get_api_client
from services.department_service import DepartmentService
import logging

logger = logging.getLogger(__name__)


class StudentDialog(QDialog):
    """Dialog để thêm hoặc chỉnh sửa sinh viên qua API"""

    def __init__(self, parent=None, student_code=None):
        super().__init__(parent)
        self.student_code = student_code
        self.student_service = StudentService()
        self.api_client = get_api_client()
        self.department_service = DepartmentService()

        self.setWindowTitle("Thêm sinh viên" if student_code is None else "Chỉnh sửa sinh viên")
        self.setModal(True)
        self.setMinimumWidth(500)

        self.init_ui()

        if student_code:
            self.load_student_data()

    def init_ui(self):
        """Khởi tạo giao diện"""
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)

        form_layout = QFormLayout()
        form_layout.setSpacing(15)
        form_layout.setLabelAlignment(Qt.AlignRight)

        self.student_code_edit = QLineEdit()
        self.student_code_edit.setPlaceholderText("Mã sinh viên (ví dụ: 21T1020001)")
        form_layout.addRow("<b>Mã sinh viên:</b>", self.student_code_edit)

        self.fullname_edit = QLineEdit()
        self.fullname_edit.setPlaceholderText("Họ và tên đầy đủ")
        form_layout.addRow("<b>Họ tên:</b>", self.fullname_edit)

        if self.student_code:
            self.email_edit = QLineEdit()
            self.email_edit.setPlaceholderText("email@example.com")
            form_layout.addRow("<b>Email:</b>", self.email_edit)

            self.phone_edit = QLineEdit()
            self.phone_edit.setPlaceholderText("0123456789")
            form_layout.addRow("<b>Số điện thoại:</b>", self.phone_edit)

            self.status_combo = QComboBox()
            self.status_combo.addItems(["Hoạt động", "Ngừng hoạt động"])
            form_layout.addRow("<b>Trạng thái:</b>", self.status_combo)

        self.dob_edit = QDateEdit()
        self.dob_edit.setCalendarPopup(True)
        self.dob_edit.setDisplayFormat("dd/MM/yyyy")
        form_layout.addRow("<b>Ngày sinh:</b>", self.dob_edit)

        self.address_edit = QLineEdit()
        self.address_edit.setPlaceholderText("Địa chỉ hiện tại")
        form_layout.addRow("<b>Địa chỉ:</b>", self.address_edit)

        self.gender_combo = QComboBox()
        self.gender_combo.addItems(["Nam", "Nữ", "Khác"])
        form_layout.addRow("<b>Giới tính:</b>", self.gender_combo)

        if not self.student_code:
            self.department_combo = QComboBox()
            self.load_departments()
            form_layout.addRow("<b>Khoa:</b>", self.department_combo)

        self.class_combo = QComboBox()
        self.load_classes()
        form_layout.addRow("<b>Lớp hành chính:</b>", self.class_combo)

        layout.addLayout(form_layout)
        layout.addSpacing(20)

        button_layout = QHBoxLayout()
        save_btn = QPushButton("Lưu")
        save_btn.clicked.connect(self.save_student)
        cancel_btn = QPushButton("Hủy")
        cancel_btn.clicked.connect(self.reject)

        button_layout.addStretch()
        button_layout.addWidget(save_btn)
        button_layout.addWidget(cancel_btn)

        layout.addLayout(button_layout)
        self.setLayout(layout)

    def load_departments(self):
        """Load danh sách khoa từ API"""
        depts = self.department_service.get_all_departments()
        if depts:
            for dept in depts:
                self.department_combo.addItem(dept['ten_khoa'], dept['ma_khoa'])
        else:
            logger.error("Lỗi load khoa từ API")
            QMessageBox.warning(self, "Lỗi", "Không thể tải danh sách khoa.")

    def load_classes(self):
        """Load danh sách lớp hành chính từ API"""
        success, classes = self.api_client.get_all_admin_classes()
        if success:
            self.class_combo.addItem("Không có", None)
            for cls in classes:
                self.class_combo.addItem(cls['ten_lop_hanh_chinh'], cls['ma_lop_hanh_chinh'])
        else:
            logger.error(f"Lỗi load lớp hành chính từ API: {classes}")
            QMessageBox.warning(self, "Lỗi", "Không thể tải danh sách lớp hành chính.")

    def load_student_data(self):
        """Load thông tin sinh viên từ API để chỉnh sửa"""
        student = self.student_service.get_student_by_code(self.student_code)
        if student:
            self.student_code_edit.setText(student.get('ma_sinh_vien', ''))
            self.student_code_edit.setEnabled(False)
            self.fullname_edit.setText(student.get('ho_ten', ''))
            self.email_edit.setText(student.get('email', '') or '')
            self.phone_edit.setText(student.get('so_dien_thoai', '') or '')

            ngay_sinh_str = student.get('ngay_sinh')
            if ngay_sinh_str:
                self.dob_edit.setDate(QDate.fromString(ngay_sinh_str, "yyyy-MM-dd"))
            else:
                self.dob_edit.setDate(QDate.currentDate())

            self.address_edit.setText(student.get('dia_chi', '') or '')

            gender = student.get('gioi_tinh', 'Nam')
            gender_index = self.gender_combo.findText(gender, Qt.MatchFixedString)
            if gender_index >= 0:
                self.gender_combo.setCurrentIndex(gender_index)

            trang_thai = student.get('trang_thai', 'Hoạt động')
            status_index = self.status_combo.findText(trang_thai, Qt.MatchFixedString)
            if status_index >= 0:
                self.status_combo.setCurrentIndex(status_index)

            class_id = student.get('ma_lop_hanh_chinh')
            class_index = self.class_combo.findData(class_id)
            if class_index >= 0:
                self.class_combo.setCurrentIndex(class_index)
        else:
            QMessageBox.critical(self, "Lỗi", f"Không tìm thấy sinh viên với mã {self.student_code}.")
            self.reject()

    def save_student(self):
        """Lưu thông tin sinh viên qua API"""
        try:
            student_code = self.student_code_edit.text().strip()
            fullname = self.fullname_edit.text().strip()
            if not student_code or not fullname:
                QMessageBox.warning(self, "Thiếu thông tin", "Mã sinh viên và Họ tên là bắt buộc.")
                return

            if self.student_code:
                current_student_data = self.student_service.get_student_by_code(self.student_code)
                if not current_student_data or 'ma_nguoi_dung' not in current_student_data:
                    QMessageBox.critical(self, "Lỗi", "Không thể lấy mã người dùng để cập nhật.")
                    return

                student_data = {
                    "ma_sinh_vien": student_code,
                    "ho_ten": fullname,
                    "email": self.email_edit.text().strip() or None,
                    "so_dien_thoai": self.phone_edit.text().strip() or None,
                    "trang_thai": self.status_combo.currentText(),
                    "ngay_sinh": self.dob_edit.date().toString("yyyy-MM-dd"),
                    "dia_chi": self.address_edit.text().strip() or None,
                    "gioi_tinh": self.gender_combo.currentText(),
                    "ma_lop_hanh_chinh": self.class_combo.currentData()
                }

                user_id = current_student_data['ma_nguoi_dung']
                success, message = self.student_service.update_student(user_id, student_data)
            else:
                department_code = self.department_combo.currentData()
                if not department_code:
                    QMessageBox.warning(self, "Thiếu thông tin", "Khoa là bắt buộc.")
                    return

                student_data = {
                    "ma_khoa": department_code,
                    "ho_ten": fullname,
                    "ma_sv": student_code,
                    "ma_lop_hc": self.class_combo.currentData(),
                    "ngay_sinh": self.dob_edit.date().toString("yyyy-MM-dd")
                }

                success, message = self.student_service.create_student(student_data)

            if success:
                QMessageBox.information(self, "Thành công", message)
                self.accept()
            else:
                QMessageBox.critical(self, "Lỗi", f"Không thể lưu thông tin: {message}")

        except Exception as e:
            logger.error(f"Lỗi khi lưu sinh viên: {e}")
            QMessageBox.critical(self, "Lỗi hệ thống", f"Đã xảy ra lỗi không mong muốn: {e}")