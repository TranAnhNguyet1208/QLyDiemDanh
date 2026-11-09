"""Dialog thêm/sửa lớp học phần, sử dụng API service"""
from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt, QDate
from services.class_service import ClassService
from services.api_service import get_api_client
import logging

logger = logging.getLogger(__name__)


class ClassDialog(QDialog):
    """Dialog để thêm hoặc chỉnh sửa lớp học phần qua API"""

    def __init__(self, parent=None, class_id=None):
        super().__init__(parent)
        self.class_id = class_id  # Đây là MaLopHocPhan
        self.class_service = ClassService()
        self.api_client = get_api_client()

        self.setWindowTitle("Thêm Lớp học phần" if class_id is None else "Chỉnh sửa Lớp học phần")
        self.setModal(True)
        self.setMinimumWidth(650)
        self.setMinimumHeight(450)

        self.init_ui()

        if class_id is not None:
            self.load_class_data()

    def init_ui(self):
        """Khởi tạo giao diện"""
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)

        form_layout = QFormLayout()
        form_layout.setSpacing(15)
        form_layout.setLabelAlignment(Qt.AlignRight)

        self.class_code_edit = QLineEdit()
        self.class_code_edit.setPlaceholderText("VD: DHP_CNTT18A")
        form_layout.addRow("<b>Mã lớp học phần:</b>", self.class_code_edit)
        
        self.subject_combo = QComboBox()
        self.load_subjects()
        form_layout.addRow("<b>Môn học:</b>", self.subject_combo)

        self.teacher_combo = QComboBox()
        self.load_teachers()
        form_layout.addRow("<b>Giảng viên phụ trách:</b>", self.teacher_combo)

        self.course_year_spin = QSpinBox()
        self.course_year_spin.setRange(2020, 2030)
        self.course_year_spin.setValue(QDate.currentDate().year())
        form_layout.addRow("<b>Năm học:</b>", self.course_year_spin)
        
        self.semester_spin = QSpinBox()
        self.semester_spin.setRange(1, 3)
        self.semester_spin.setValue(1)
        form_layout.addRow("<b>Học kỳ:</b>", self.semester_spin)
        
        # Thêm ghi chú nếu cần thiết (Backend hỗ trợ, nhưng UI cũ không có, ta thêm vào cho đầy đủ)
        self.note_edit = QLineEdit()
        self.note_edit.setPlaceholderText("Ghi chú (tùy chọn)")
        form_layout.addRow("<b>Ghi chú:</b>", self.note_edit)

        layout.addLayout(form_layout)
        layout.addSpacing(20)

        button_layout = QHBoxLayout()
        save_btn = QPushButton("Lưu")
        save_btn.clicked.connect(self.save_class)
        cancel_btn = QPushButton("Hủy")
        cancel_btn.clicked.connect(self.reject)

        button_layout.addStretch()
        button_layout.addWidget(save_btn)
        button_layout.addWidget(cancel_btn)

        layout.addLayout(button_layout)
        self.setLayout(layout)

    def load_subjects(self):
        """Load danh sách môn học từ API"""
        success, subjects = self.api_client.get_all_subjects()
        if success:
            self.subject_combo.addItem("-- Chọn môn học --", None)
            for sub in subjects:
                # Backend trả về MaMonHoc/TenMonHoc hoặc ma_mon_hoc/ten_mon_hoc tùy endpoint
                s_id = sub.get('ma_mon_hoc') or sub.get('ma_mon_hoc')
                s_name = sub.get('ten_mon_hoc') or sub.get('ten_mon_hoc')
                if s_id:
                    self.subject_combo.addItem(f"{s_id} - {s_name}", s_id)
        else:
            logger.error(f"Lỗi load môn học từ API: {subjects}")

    def load_teachers(self):
        """Load danh sách giảng viên từ API"""
        success, teachers = self.api_client.get_all_teachers()
        if success:
            self.teacher_combo.addItem("-- Chọn giảng viên --", None)
            for teacher in teachers:
                t_id = teacher.get('ma_giang_vien') or teacher.get('ma_giang_vien')
                t_name = teacher.get('ho_ten') or teacher.get('ho_ten')
                if t_id:
                    self.teacher_combo.addItem(f"{t_name} ({t_id})", t_id)
        else:
            logger.error(f"Lỗi load giảng viên từ API: {teachers}")

    def load_class_data(self):
        """Load thông tin lớp học từ API (GET chi tiết trả về PascalCase)"""
        cls = self.class_service.get_class_by_id(self.class_id)
        if cls:
            self.class_code_edit.setText(cls.get('ma_lop_hoc_phan', ''))
            self.class_code_edit.setEnabled(False) # Không cho sửa mã
            
            # Xử lý năm học (có thể là int hoặc str)
            nam_hoc = cls.get('nam_hoc')
            if nam_hoc:
                try:
                    self.course_year_spin.setValue(int(nam_hoc))
                except ValueError:
                    pass
            
            self.semester_spin.setValue(int(cls.get('hoc_ky', 1)))
            self.note_edit.setText(cls.get('ghi_chu', ''))

            subject_id = cls.get('ma_mon_hoc')
            index = self.subject_combo.findData(subject_id)
            if index >= 0:
                self.subject_combo.setCurrentIndex(index)
                
            teacher_id = cls.get('ma_giang_vien')
            index = self.teacher_combo.findData(teacher_id)
            if index >= 0:
                self.teacher_combo.setCurrentIndex(index)

        else:
            QMessageBox.critical(self, "Lỗi", f"Không tìm thấy lớp học phần với mã {self.class_id}.")
            self.reject()

    def save_class(self):
        """Lưu thông tin lớp học phần qua API (Gửi snake_case)"""
        try:
            class_code = self.class_code_edit.text().strip()
            subject_id = self.subject_combo.currentData()
            teacher_id = self.teacher_combo.currentData()

            if not class_code or not subject_id:
                QMessageBox.warning(self, "Thiếu thông tin", "Mã lớp và Môn học là bắt buộc.")
                return

            class_data = {
                "ma_lhp": class_code,
                "ma_mon_hoc": subject_id,
                "ma_giang_vien": teacher_id,
                "nam_hoc": str(self.course_year_spin.value()), 
                "hoc_ky": self.semester_spin.value(),
                "ghi_chu": self.note_edit.text().strip()
            }

            if self.class_id:
                # === CẬP NHẬT ===
                success, message = self.class_service.update_class(self.class_id, class_data)
            else:
                # === TẠO MỚI ===
                success, message = self.class_service.create_class(class_data)

            if success:
                QMessageBox.information(self, "Thành công", message)
                self.accept()
            else:
                QMessageBox.critical(self, "Lỗi", f"Không thể lưu: {message}")

        except Exception as e:
            logger.error(f"Lỗi khi lưu lớp học phần: {e}")
            QMessageBox.critical(self, "Lỗi hệ thống", f"Đã xảy ra lỗi không mong muốn: {e}")