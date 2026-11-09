"""Dialog thêm/sửa buổi học, sử dụng API service"""
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from services.session_service import SessionService
from services.api_service import get_api_client
import logging

logger = logging.getLogger(__name__)


class SessionDialog(QDialog):
    """Dialog thêm/sửa buổi học qua API"""

    def __init__(self, parent=None, session_id=None):
        super().__init__(parent)
        self.session_id = session_id
        self.session_service = SessionService()
        self.api_client = get_api_client()

        self.setWindowTitle("Sửa buổi học" if session_id else "Thêm buổi học mới")
        self.setModal(True)
        self.setMinimumWidth(600)
        
        self.init_ui()

        if session_id:
            self.load_session_data()
        else:
            self.class_combo.setEnabled(True)

    def init_ui(self):
        """Khởi tạo giao diện"""
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        
        form_layout = QFormLayout()
        form_layout.setSpacing(15)
        form_layout.setLabelAlignment(Qt.AlignRight)

        # Lớp học phần
        self.class_combo = QComboBox()
        self.load_classes()
        form_layout.addRow("<b>Lớp học phần:</b>", self.class_combo)

        # Ngày học
        self.date_edit = QDateEdit(calendarPopup=True)
        self.date_edit.setDate(QDate.currentDate())
        self.date_edit.setDisplayFormat("dd/MM/yyyy")
        form_layout.addRow("<b>Ngày học:</b>", self.date_edit)

        # Giờ bắt đầu
        self.start_time_edit = QTimeEdit(displayFormat="HH:mm")
        self.start_time_edit.setTime(QTime(7, 0))
        form_layout.addRow("<b>Giờ bắt đầu:</b>", self.start_time_edit)

        # Giờ kết thúc
        self.end_time_edit = QTimeEdit(displayFormat="HH:mm")
        self.end_time_edit.setTime(QTime(9, 0))
        form_layout.addRow("<b>Giờ kết thúc:</b>", self.end_time_edit)

        # Phòng học
        self.room_edit = QLineEdit(placeholderText="VD: A101, B205...")
        form_layout.addRow("<b>Phòng học:</b>", self.room_edit)

        # Trạng thái (chỉ hiển thị khi sửa)
        self.status_combo = QComboBox()
        self.status_combo.addItems(["Chưa diễn ra", "Đang diễn ra", "Đã kết thúc", "Đã hủy"])
        self.status_label = QLabel("<b>Trạng thái:</b>")
        form_layout.addRow(self.status_label, self.status_combo)
        # Ẩn trạng thái nếu đang thêm mới
        if not self.session_id:
            self.status_label.hide()
            self.status_combo.hide()

        # Ghi chú
        self.note_edit = QLineEdit(placeholderText="Ghi chú về buổi học...")
        form_layout.addRow("<b>Ghi chú:</b>", self.note_edit)

        layout.addLayout(form_layout)
        layout.addSpacing(20)

        button_layout = QHBoxLayout()
        save_btn = QPushButton("Lưu")
        save_btn.clicked.connect(self.save_session)
        cancel_btn = QPushButton("Hủy")
        cancel_btn.clicked.connect(self.reject)
        
        button_layout.addStretch()
        button_layout.addWidget(save_btn)
        button_layout.addWidget(cancel_btn)

        layout.addLayout(button_layout)
        self.setLayout(layout)

    def load_classes(self):
        """Load danh sách lớp học phần từ API"""
        success, classes = self.api_client.get_all_classes()
        if success:
            self.class_combo.addItem("-- Chọn lớp --", None)
            for cls in classes:
                # Backend trả về PascalCase keys: MaLopHocPhan, TenMonHoc
                ma_lhp = cls.get('ma_lop_hoc_phan') or cls.get('ma_lhp')
                ten_mon = cls.get('ten_mon_hoc') or cls.get('ten_mon_hoc')
                if ma_lhp and ten_mon:
                    self.class_combo.addItem(f"{ma_lhp} - {ten_mon}", ma_lhp)
        else:
            logger.error(f"Lỗi load lớp học phần từ API: {classes}")

    def load_session_data(self):
        """Load dữ liệu buổi học cần sửa từ API"""
        session = self.session_service.get_session_detail(self.session_id)
        if session:
            class_id = session.get('ma_lhp')
            class_index = self.class_combo.findData(class_id)
            if class_index >= 0:
                self.class_combo.setCurrentIndex(class_index)
            self.class_combo.setEnabled(False)

            session_date_str = session.get('ngay_hoc')
            if session_date_str:
                self.date_edit.setDate(QDate.fromString(session_date_str, "yyyy-MM-dd"))

            start_time_str = session.get('thoi_gian_bat_dau')
            if start_time_str:
                self.start_time_edit.setTime(QTime.fromString(start_time_str, "HH:mm:ss"))
            
            end_time_str = session.get('thoi_gian_ket_thuc')
            if end_time_str:
                self.end_time_edit.setTime(QTime.fromString(end_time_str, "HH:mm:ss"))

            self.room_edit.setText(session.get('phong_hoc', ''))

            session_status = session.get('trang_thai', 'Chưa diễn ra')
            status_index = self.status_combo.findText(session_status, Qt.MatchFixedString)
            if status_index >= 0:
                self.status_combo.setCurrentIndex(status_index)

            self.note_edit.setText(session.get('ghi_chu', ''))
        else:
             QMessageBox.critical(self, "Lỗi", f"Không thể tải dữ liệu cho buổi học ID: {self.session_id}")
             self.reject()


    def save_session(self):
        """Lưu buổi học qua API"""
        class_id = self.class_combo.currentData()
        if not class_id:
            QMessageBox.warning(self, "Thiếu thông tin", "Vui lòng chọn một lớp học phần.")
            return

        session_data = {
            "ngay_hoc": self.date_edit.date().toString("yyyy-MM-dd"),
            "thoi_gian_bat_dau": self.start_time_edit.time().toString("HH:mm:ss"),
            "thoi_gian_ket_thuc": self.end_time_edit.time().toString("HH:mm:ss"),
            "phong_hoc": self.room_edit.text().strip(),
            "ghi_chu": self.note_edit.text().strip()
        }

        try:
            if self.session_id:
                # === CẬP NHẬT ===
                session_data["trang_thai"] = self.status_combo.currentText()
                success, message = self.session_service.update_session(self.session_id, session_data)
            else:
                # === TẠO MỚI ===
                session_data["ma_lhp"] = class_id
                success, message = self.session_service.create_session(session_data)

            if success:
                QMessageBox.information(self, "Thành công", message)
                self.accept()
            else:
                QMessageBox.critical(self, "Lỗi", f"Không thể lưu: {message}")

        except Exception as e:
            logger.error(f"Lỗi khi lưu buổi học: {e}")
            QMessageBox.critical(self, "Lỗi hệ thống", f"Đã xảy ra lỗi không mong muốn: {e}")