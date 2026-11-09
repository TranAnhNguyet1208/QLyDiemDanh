"""Dialog quản lý sinh viên trong lớp, sử dụng API service"""
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from services.class_service import ClassService
from services.student_service import StudentService
from services.admin_class_service import AdminClassService
import logging

logger = logging.getLogger(__name__)


class ClassStudentsDialog(QDialog):
    """Dialog để quản lý sinh viên trong lớp qua API"""

    def __init__(self, parent=None, class_id=None, class_name=None):
        super().__init__(parent)
        self.class_id = class_id
        self.class_name = class_name
        
        self.class_service = ClassService()
        self.student_service = StudentService()
        self.admin_class_service = AdminClassService()
        
        self.all_available = []

        self.setWindowTitle(f"Quản lý sinh viên - {self.class_name} ({self.class_id})")
        self.setModal(True)
        self.setMinimumSize(1300, 900)

        self.init_ui()
        self.load_data()

    def init_ui(self):
        """Khởi tạo giao diện"""
        layout = QVBoxLayout(self)
        
        title = QLabel(f"Lớp: {self.class_name}")
        title.setFont(QFont('Segoe UI', 14, QFont.Bold))
        layout.addWidget(title)
        
        splitter = QSplitter(Qt.Horizontal)
        
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.addWidget(QLabel("<b>Sinh viên trong lớp</b>"))
        self.enrolled_table = QTableWidget(columnCount=3, editTriggers=QAbstractItemView.NoEditTriggers)
        self.enrolled_table.setHorizontalHeaderLabels(["Mã SV", "Họ tên", "Hành động"])
        self.enrolled_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.enrolled_table.setColumnWidth(0, 150)
        self.enrolled_table.setColumnWidth(2, 200)
        left_layout.addWidget(self.enrolled_table)
        splitter.addWidget(left_widget)
        
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        
        bulk_add_group = QGroupBox("Thêm hàng loạt theo Lớp Hành chính")
        bulk_add_layout = QHBoxLayout(bulk_add_group)
        
        self.admin_class_combo = QComboBox()
        self.admin_class_combo.setMinimumWidth(300)
        bulk_add_layout.addWidget(self.admin_class_combo, 1)
        
        self.bulk_add_btn = QPushButton("Thêm toàn bộ lớp")
        self.bulk_add_btn.clicked.connect(self.bulk_add_students)
        bulk_add_layout.addWidget(self.bulk_add_btn)
        
        right_layout.addWidget(bulk_add_group)
        
        right_layout.addWidget(QLabel("<b>Hoặc thêm từng sinh viên</b>"))
        
        search_layout = QHBoxLayout()
        search_layout.addWidget(QLabel("Tìm:"))
        self.search_input = QLineEdit(placeholderText="Nhập mã hoặc tên...")
        self.search_input.textChanged.connect(self.filter_available_students)
        search_layout.addWidget(self.search_input)
        right_layout.addLayout(search_layout)
        
        self.available_table = QTableWidget(columnCount=3, editTriggers=QAbstractItemView.NoEditTriggers)
        self.available_table.setHorizontalHeaderLabels(["", "Mã SV", "Họ tên"])
        self.available_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        self.available_table.setColumnWidth(0, 40)
        self.available_table.setColumnWidth(1, 150)
        self.available_table.setSelectionMode(QAbstractItemView.NoSelection)
        right_layout.addWidget(self.available_table)

        btn_layout = QHBoxLayout()
        add_selected_btn = QPushButton("Thêm sinh viên đã chọn")
        add_selected_btn.clicked.connect(self.add_selected_students)
        btn_layout.addStretch()
        btn_layout.addWidget(add_selected_btn)
        right_layout.addLayout(btn_layout)
        
        splitter.addWidget(right_widget)
        splitter.setSizes([600, 400])
        
        layout.addWidget(splitter)
        
        bottom_button_layout = QHBoxLayout()
        bottom_button_layout.addStretch()
        refresh_btn = QPushButton("🔄 Tải lại dữ liệu")
        refresh_btn.clicked.connect(self.load_data)
        bottom_button_layout.addWidget(refresh_btn)
        close_btn = QPushButton("Đóng")
        close_btn.clicked.connect(self.accept)
        bottom_button_layout.addWidget(close_btn)
        bottom_button_layout.addStretch()
        layout.addLayout(bottom_button_layout)

    def load_data(self):
        """Load lại toàn bộ dữ liệu từ API"""
        self.load_enrolled_students()
        self.load_available_students()
        self.load_admin_classes_into_combo()

    def load_admin_classes_into_combo(self):
        self.admin_class_combo.clear()
        admin_classes = self.admin_class_service.get_all_admin_classes()
        if not admin_classes:
            self.admin_class_combo.addItem("Không có lớp hành chính nào")
            self.admin_class_combo.setEnabled(False)
            self.bulk_add_btn.setEnabled(False)
        else:
            self.admin_class_combo.addItem("-- Chọn Lớp Hành chính --", None)
            for admin_class in admin_classes:
                self.admin_class_combo.addItem(f"{admin_class['ten_lop']} ({admin_class['ma_lop']})", admin_class['ma_lop'])
            self.admin_class_combo.setEnabled(True)
            self.bulk_add_btn.setEnabled(True)

    def bulk_add_students(self):
        admin_class_id = self.admin_class_combo.currentData()
        admin_class_name = self.admin_class_combo.currentText()

        if not admin_class_id:
            QMessageBox.warning(self, "Chưa chọn lớp", "Vui lòng chọn một lớp hành chính từ danh sách.")
            return

        reply = QMessageBox.question(
            self, 
            "Xác nhận thêm hàng loạt", 
            f"Bạn có chắc muốn thêm TẤT CẢ sinh viên từ lớp '{admin_class_name}' vào lớp học phần này không?\n\n(Các sinh viên đã có trong lớp sẽ được bỏ qua.)",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if reply == QMessageBox.No:
            return

        success, message, count = self.class_service.add_students_from_admin_class(self.class_id, admin_class_id)
        
        if success:
            QMessageBox.information(self, "Thành công", f"Đã thêm thành công {count} sinh viên từ lớp {admin_class_name}.")
            self.load_data()
        else:
            QMessageBox.critical(self, "Lỗi", f"Thêm hàng loạt thất bại: {message}")

    def load_enrolled_students(self):
        """Load sinh viên đã trong lớp từ API"""
        enrolled = self.class_service.get_students_in_class(self.class_id)
        self.enrolled_table.setRowCount(len(enrolled))
        for i, student in enumerate(enrolled):
            self.enrolled_table.setItem(i, 0, QTableWidgetItem(student.get('ma_sinh_vien')))
            self.enrolled_table.setItem(i, 1, QTableWidgetItem(student.get('ho_ten')))
            
            remove_btn = QPushButton("Xóa")
            remove_btn.clicked.connect(lambda _, s=student.get('ma_sinh_vien'): self.remove_student(s))
            self.enrolled_table.setCellWidget(i, 2, remove_btn)

    def load_available_students(self):
        """Load sinh viên có thể thêm (chưa trong lớp) từ API"""
        enrolled_students = self.class_service.get_students_in_class(self.class_id)
        enrolled_ids = {s.get('ma_sinh_vien') for s in enrolled_students}
        
        all_students = self.student_service.get_all_students()
        
        self.all_available = [s for s in all_students if s.get('ma_sinh_vien') not in enrolled_ids]
        self.display_available_students(self.all_available)

    def display_available_students(self, students):
        """Hiển thị danh sách sinh viên có thể thêm"""
        self.available_table.setRowCount(len(students))
        for i, student in enumerate(students):
            checkbox = QCheckBox()
            checkbox_widget = QWidget()
            checkbox_layout = QHBoxLayout(checkbox_widget)
            checkbox_layout.addWidget(checkbox)
            checkbox_layout.setAlignment(Qt.AlignCenter)
            self.available_table.setCellWidget(i, 0, checkbox_widget)

            item_code = QTableWidgetItem(student.get('ma_sinh_vien'))
            item_code.setData(Qt.UserRole, student.get('ma_sinh_vien'))
            self.available_table.setItem(i, 1, item_code)
            self.available_table.setItem(i, 2, QTableWidgetItem(student.get('ho_ten')))

    def filter_available_students(self):
        """Filter sinh viên theo từ khóa tìm kiếm"""
        keyword = self.search_input.text().lower()
        if not keyword:
            self.display_available_students(self.all_available)
        else:
            filtered = [
                s for s in self.all_available
                if keyword in s.get('ma_sinh_vien', '').lower() or keyword in s.get('ho_ten', '').lower()
            ]
            self.display_available_students(filtered)

    def add_selected_students(self):
        """Thêm các sinh viên đã chọn vào lớp qua API"""
        selected_ids = []
        for i in range(self.available_table.rowCount()):
            if self.available_table.cellWidget(i, 0).findChild(QCheckBox).isChecked():
                item = self.available_table.item(i, 1)
                if item:
                    selected_ids.append(item.data(Qt.UserRole))
        
        if not selected_ids:
            QMessageBox.warning(self, "Thông báo", "Vui lòng chọn ít nhất một sinh viên.")
            return

        added_count = 0
        for student_id in selected_ids:
            success, message = self.class_service.add_student_to_class(self.class_id, student_id)
            if success:
                added_count += 1
            else:
                logger.error(f"Lỗi thêm sinh viên {student_id} vào lớp {self.class_id}: {message}")
        
        QMessageBox.information(self, "Hoàn tất", f"Đã thêm thành công {added_count}/{len(selected_ids)} sinh viên.")
        self.load_data()

    def remove_student(self, student_id):
        """Xóa sinh viên khỏi lớp qua API"""
        reply = QMessageBox.question(self, "Xác nhận", f"Bạn có chắc muốn xóa sinh viên {student_id} khỏi lớp này?", QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            success, message = self.class_service.remove_student_from_class(self.class_id, student_id)
            if success:
                QMessageBox.information(self, "Thành công", message)
                self.load_data()
            else:
                QMessageBox.critical(self, "Lỗi", f"Không thể xóa sinh viên: {message}")