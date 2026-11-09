from PyQt5.QtWidgets import *
from services.admin_class_service import AdminClassService
import logging

logger = logging.getLogger(__name__)

class AdminClassDialog(QDialog):
    """Dialog để thêm hoặc chỉnh sửa Lớp Hành chính (Admin Class)."""
    def __init__(self, parent=None, class_code=None):
        super().__init__(parent)
        self.class_code = class_code
        self.admin_class_service = AdminClassService()

        self.setWindowTitle("Lớp Hành chính")
        self.setMinimumWidth(400)

        self.init_ui()
        if self.class_code:
            self.load_data()

    def init_ui(self):
        layout = QVBoxLayout(self)
        form_layout = QFormLayout()

        self.ma_lop_input = QLineEdit()
        self.ten_lop_input = QLineEdit()
        
        # Nếu là chỉnh sửa, không cho sửa mã
        if self.class_code:
            self.ma_lop_input.setReadOnly(True)

        form_layout.addRow("Mã lớp (*):", self.ma_lop_input)
        form_layout.addRow("Tên lớp (*):", self.ten_lop_input)

        layout.addLayout(form_layout)

        self.buttons = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel, self)
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)
        layout.addWidget(self.buttons)

    def load_data(self):
        """Tải dữ liệu của lớp để chỉnh sửa."""
        # Hiện tại service chưa có get_one, ta sẽ giả định dữ liệu được truyền vào
        # hoặc có thể lấy từ một nguồn khác nếu cần. Trong ví dụ này, ta sẽ
        # dựa vào việc service có thể được mở rộng.
        # Giả sử admin_class_service có hàm get_admin_class(code)
        success, data = self.admin_class_service.get_admin_class(self.class_code)
        if success and data:
            self.ma_lop_input.setText(data.get('ma_lop'))
            self.ten_lop_input.setText(data.get('ten_lop'))
        else:
            logger.error(f"Could not load data for admin class {self.class_code}")
            self.buttons.button(QDialogButtonBox.Save).setEnabled(False)

    def accept(self):
        """Lưu dữ liệu khi nhấn Save."""
        ma_lop = self.ma_lop_input.text().strip()
        ten_lop = self.ten_lop_input.text().strip()

        if not ma_lop or not ten_lop:
            QMessageBox.warning(self, "Thiếu thông tin", "Mã lớp và Tên lớp không được để trống.")
            return

        data = {'ma_lop': ma_lop, 'ten_lop': ten_lop}

        if self.class_code:
            success, message = self.admin_class_service.update_admin_class(self.class_code, data)
        else:
            success, message = self.admin_class_service.create_admin_class(data)

        if success:
            QMessageBox.information(self, "Thành công", message)
            super().accept()
        else:
            QMessageBox.critical(self, "Lỗi", f"Thao tác thất bại: {message}")
