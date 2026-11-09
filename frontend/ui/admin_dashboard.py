from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from datetime import datetime
import logging
import os
import cv2
import time

from services.student_service import StudentService
from services.teacher_service import TeacherService
from services.class_service import ClassService
from services.department_service import DepartmentService
from services.admin_class_service import AdminClassService
from services.session_service import SessionService
from services.face_recognition_service import FaceRecognitionService
from services.api_service import get_api_client
from services.subject_service import SubjectService

from ui.session_dialog import SessionDialog
from ui.student_dialog import StudentDialog
from ui.teacher_dialog import TeacherDialog
from ui.class_dialog import ClassDialog
from ui.class_students_dialog import ClassStudentsDialog
from ui.department_dialog import DepartmentDialog
from ui.admin_class_dialog import AdminClassDialog
from ui.subject_dialog import SubjectDialog
from ui.report_dialogs import (
    Report1Dialog, Report2Dialog, Report3Dialog, Report4Dialog,
    Report5Dialog, Report6Dialog, Report7Dialog, Report8Dialog
)
from ui.personal_info_dialog import PersonalInfoDialog

logger = logging.getLogger(__name__)

class AdminDashboard(QMainWindow):
    """Dashboard cho admin, đã được tái cấu trúc để dùng API"""
    
    logout_requested = pyqtSignal()
    
    def __init__(self, user_data):
        super().__init__()
        self.user_data = user_data
        
        self.student_service = StudentService()
        self.teacher_service = TeacherService()
        self.class_service = ClassService()
        self.department_service = DepartmentService()
        self.admin_class_service = AdminClassService()
        self.session_service = SessionService()
        self.face_service = FaceRecognitionService()
        self.subject_service = SubjectService()
        self.api_client = get_api_client()

        self.setWindowTitle(f"Quản trị - {self.user_data.get('ho_ten', '')}")
        self.showMaximized()
        self.init_ui()

    def init_ui(self):
        """Khởi tạo giao diện"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout(central_widget)
        
        header = self.create_header()
        layout.addWidget(header)
        
        tabs = QTabWidget()
        tabs.addTab(self.create_overview_tab(), "📊 Tổng quan")
        tabs.addTab(self.create_students_tab(), "🎓 Sinh viên")
        tabs.addTab(self.create_teachers_tab(), "👨‍🏫 Giảng viên")
        tabs.addTab(self.create_departments_tab(), "🏛️ Khoa")
        tabs.addTab(self.create_admin_classes_tab(), "🏷️ Lớp hành chính")
        tabs.addTab(self.create_reports_tab(), "📑 Báo cáo")
        tabs.addTab(self.create_classes_tab(), "🏫 Lớp học phần")
        tabs.addTab(self.create_sessions_tab(), "📅 Buổi học")
        tabs.addTab(self.create_subjects_tab(), "📚 Môn học")
        
        layout.addWidget(tabs)

    def create_header(self):
        """Tạo header"""
        header_frame = QFrame()
        header_frame.setStyleSheet("background-color: #333; color: white; padding: 15px;")
        layout = QHBoxLayout(header_frame)
        info_label = QLabel(f"👑 Quản trị viên: {self.user_data.get('ho_ten', 'Admin')}")
        info_label.setFont(QFont('Segoe UI', 16, QFont.Bold))
        
        personal_btn = QPushButton("👤 Thông tin cá nhân")
        personal_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                padding: 8px 15px;
                border: none;
                border-radius: 3px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        
        logout_btn = QPushButton("Đăng xuất")
        logout_btn.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                padding: 8px 15px;
                border: none;
                border-radius: 3px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """)
        
        logout_btn.clicked.connect(self.logout_requested.emit)
        personal_btn.clicked.connect(self.show_personal_info_dialog)
        
        layout.addWidget(info_label)
        layout.addStretch()
        layout.addWidget(personal_btn)
        layout.addWidget(logout_btn)
        
        return header_frame

    def create_overview_tab(self):
        """Tab tổng quan - Phiên bản SIÊU TO KHỔNG LỒ"""
        widget = QWidget()
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(widget)
        
        main_layout = QVBoxLayout(widget)
        main_layout.setSpacing(40) # Khoảng cách giữa các phần lớn hơn
        main_layout.setContentsMargins(40, 40, 40, 40) # Lề tổng thể dày hơn
        
        # --- 1. WELCOME SECTION ---
        welcome_frame = QFrame()
        welcome_frame.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #2c3e50, stop:1 #3498db);
                border-radius: 20px;
            }
            QLabel {
                color: white;
                background: transparent;
            }
        """)
        welcome_layout = QVBoxLayout(welcome_frame)
        welcome_layout.setContentsMargins(50, 50, 50, 50) 
        welcome_layout.setSpacing(15)

        icon_label = QLabel("📊")
        icon_label.setStyleSheet("font-size: 60px; margin-bottom: 10px;")
        
        welcome_title = QLabel("TỔNG QUAN HỆ THỐNG")
        welcome_title.setStyleSheet("font-size: 55px; font-weight: 900; letter-spacing: 2px;")
        
        welcome_subtitle = QLabel("Thống kê dữ liệu thời gian thực về sinh viên, giảng viên và lớp học")

        welcome_subtitle.setStyleSheet("font-size: 28px; opacity: 0.9; font-weight: 500;")
        
        welcome_layout.addWidget(icon_label)
        welcome_layout.addWidget(welcome_title)
        welcome_layout.addWidget(welcome_subtitle)
        
        main_layout.addWidget(welcome_frame)
        
        self.stats_layout = QGridLayout()
        self.stats_layout.setSpacing(40)
        main_layout.addLayout(self.stats_layout)
        
        self.load_overview_stats()
        main_layout.addStretch()
        
        return scroll

    def load_overview_stats(self):
        """Tải dữ liệu thống kê từ API"""
        while self.stats_layout.count():
            item = self.stats_layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()
        
        success, stats = self.api_client.get_admin_overview_stats()
        if not success:
            logger.error("Không thể tải dữ liệu tổng quan từ API")
            error_label = QLabel("Không thể tải dữ liệu thống kê. Vui lòng thử lại.")
            error_label.setAlignment(Qt.AlignCenter)
            self.stats_layout.addWidget(error_label, 0, 0, 2, 2)
            return

        cards_data = [
            ("👨‍🎓 Sinh viên", stats.get('total_students', 0), "#1abc9c", "#16a085"),
            ("👨‍🏫 Giảng viên", stats.get('total_teachers', 0), "#3498db", "#2980b9"),
            ("📚 Lớp học phần", stats.get('total_classes', 0), "#9b59b6", "#8e44ad"),
            ("📅 Buổi học hôm nay", stats.get('today_sessions', 0), "#e67e22", "#d35400"),
        ]

        for i, (title, value, color, hover_color) in enumerate(cards_data):
            row = i // 2
            col = i % 2
            card = self.create_stat_card(title, value, color, hover_color)
            self.stats_layout.addWidget(card, row, col)

    def create_stat_card(self, title, value, color, hover_color):
        """Tạo card thống kê - Phiên bản Big Size"""
        card = QFrame()

        card.setMinimumHeight(320)
        
        card.setStyleSheet(f"""
            QFrame {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 {color}, stop:1 {hover_color});
                border-radius: 25px; /* Bo góc tròn hơn */
                border: none;
            }}
            QFrame:hover {{
                background: {hover_color};
            }}
        """)
        
        layout = QVBoxLayout(card)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(20)
        
        layout.addStretch() 
        
        title_label = QLabel(title)
        title_label.setWordWrap(True)
        title_label.setStyleSheet("""
            color: rgba(255, 255, 255, 0.9);
            font-size: 30px; 
            font-weight: bold;
            text-transform: uppercase;
            background: transparent;
        """)
        
        value_label = QLabel(str(value))
        value_label.setStyleSheet("""
            color: white;
            font-size: 85px; 
            font-weight: 900;
            background: transparent;
        """)
        
        layout.addWidget(title_label)
        layout.addWidget(value_label)
        
        layout.addStretch()
        
        return card

    def create_students_tab(self):
        self.students_table = QTableWidget(columnCount=7)
        self.students_table.setHorizontalHeaderLabels(["Mã SV", "Họ tên", "Lớp", "Email", "SĐT", "Khuôn mặt", "Hành động"])
        header = self.students_table.horizontalHeader()
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        header.setSectionResizeMode(3, QHeaderView.Stretch)
        
        self.student_class_filter = QComboBox()
        self.student_class_filter.addItem("Tất cả", None)
        self.student_class_filter.currentIndexChanged.connect(self.load_students)
        
        filter_layout = QHBoxLayout()
        filter_layout.addWidget(QLabel("Lọc theo lớp:"))
        filter_layout.addWidget(self.student_class_filter)
        filter_layout.addStretch()
        
        return self._create_tab_with_table("student", self.students_table, self.load_students, [
            ("➕ Thêm SV", self.add_student),
            ("📥 Nhập Excel/CSV", self.import_students_from_file),
            ("📷 Đăng ký Khuôn mặt", self.register_student_face)
        ], extra_toolbar_widgets=[self.student_class_filter])

    def create_subjects_tab(self):
        self.subjects_table = QTableWidget(columnCount=5)
        self.subjects_table.setHorizontalHeaderLabels(["Mã môn", "Tên môn", "Số tín chỉ", "Khoa", "Hành động"])
        header = self.subjects_table.horizontalHeader()
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        return self._create_tab_with_table("subject", self.subjects_table, self.load_subjects, [
            ("➕ Thêm môn học", self.add_subject)
        ])

    def create_teachers_tab(self):
        self.teachers_table = QTableWidget(columnCount=8)
        self.teachers_table.setHorizontalHeaderLabels(["Mã GV", "Họ tên", "Khoa", "Email", "SĐT", "Học vị", "Trạng thái", "Hành động"])
        header = self.teachers_table.horizontalHeader()
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        return self._create_tab_with_table("teacher", self.teachers_table, self.load_teachers, [("➕ Thêm GV", self.add_teacher)])

    def create_departments_tab(self):
        self.departments_table = QTableWidget(columnCount=6)
        self.departments_table.setHorizontalHeaderLabels(["Mã khoa", "Tên khoa", "Số điện thoại", "Email", "Phòng làm việc", "Hành động"])
        header = self.departments_table.horizontalHeader()
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        return self._create_tab_with_table("department", self.departments_table, self.load_departments, [("➕ Thêm Khoa", self.add_department)])

    def create_admin_classes_tab(self):
        self.admin_classes_table = QTableWidget(columnCount=3)
        self.admin_classes_table.setHorizontalHeaderLabels(["Mã Lớp", "Tên Lớp hành chính", "Hành động"])
        header = self.admin_classes_table.horizontalHeader()
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        return self._create_tab_with_table("admin_class", self.admin_classes_table, self.load_admin_classes, [("➕ Thêm Lớp HC", self.add_admin_class)])

    def create_reports_tab(self):
        """Tạo tab hiển thị danh sách báo cáo cố định cho Admin"""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        self.reports_table = QTableWidget(columnCount=2)
        self.reports_table.setHorizontalHeaderLabels(["Báo cáo", "Hành động"])
        self.reports_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)

        layout.addWidget(self.reports_table)
        self.load_reports_list()
        return widget

    def create_classes_tab(self):
        self.classes_table = QTableWidget(columnCount=7)
        self.classes_table.setHorizontalHeaderLabels(["Mã LHP", "Tên Môn học", "Giảng viên", "Năm học", "Học kỳ", "Sĩ số", "Hành động"])
        header = self.classes_table.horizontalHeader()
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        header.setSectionResizeMode(2, QHeaderView.Stretch)
        self.classes_table.setColumnWidth(0, 150)
        self.classes_table.setColumnWidth(3, 150)
        self.classes_table.setColumnWidth(4, 150)
        return self._create_tab_with_table("class", self.classes_table, self.load_classes, [
            ("➕ Thêm LHP", self.add_class),
            ("👥 Quản lý SV", self.manage_class_students)
        ])
    
    def create_sessions_tab(self):
        self.sessions_table = QTableWidget(columnCount=9)
        self.sessions_table.setHorizontalHeaderLabels(["Ngày", "Giờ", "Lớp", "Phòng", "Môn học", "Giảng viên", "Trạng thái", "Ghi chú", "Hành động"])
        header = self.sessions_table.horizontalHeader()
        header.setSectionResizeMode(2, QHeaderView.Stretch)
        header.setSectionResizeMode(4, QHeaderView.Stretch)
        header.setSectionResizeMode(5, QHeaderView.Stretch)
        self.sessions_table.setColumnWidth(0, 160) 
        self.sessions_table.setColumnWidth(1, 240) 
        self.sessions_table.setColumnWidth(3, 160) 
        
        self.session_from_date = QDateEdit(calendarPopup=True, date=QDate.currentDate().addDays(-30))
        self.session_from_date.setDisplayFormat("dd/MM/yyyy")
        self.session_to_date = QDateEdit(calendarPopup=True, date=QDate.currentDate().addDays(30))
        self.session_to_date.setDisplayFormat("dd/MM/yyyy")
        date_filter_widgets = [QLabel("Từ:"), self.session_from_date, QLabel("Đến:"), self.session_to_date]

        return self._create_tab_with_table("session", self.sessions_table, self.load_sessions, [("➕ Thêm Buổi học", self.add_session)], extra_toolbar_widgets=date_filter_widgets)

    def _create_tab_with_table(self, item_type, table, load_func, actions, extra_toolbar_widgets=None):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        toolbar = QHBoxLayout()
        for text, handler in actions:
            btn = QPushButton(text)
            btn.clicked.connect(handler)
            toolbar.addWidget(btn)
        
        refresh_btn = QPushButton("🔄 Làm mới")
        refresh_btn.clicked.connect(load_func)
        toolbar.addWidget(refresh_btn)
        toolbar.addStretch()

        if extra_toolbar_widgets:
            for w in extra_toolbar_widgets:
                toolbar.addWidget(w)
        
        layout.addLayout(toolbar)
        layout.addWidget(table)
        load_func()
        return widget

    def load_students(self):
        class_id = self.student_class_filter.currentData()
        students = self.student_service.get_all_students(class_id=class_id)
        self.students_table.setRowCount(len(students))
        for i, s in enumerate(students):
            self.students_table.setItem(i, 0, QTableWidgetItem(s.get('ma_sinh_vien', '')))
            self.students_table.setItem(i, 1, QTableWidgetItem(s.get('ho_ten', '')))
            self.students_table.setItem(i, 2, QTableWidgetItem(s.get('ten_lop_hanh_chinh', '')))
            self.students_table.setItem(i, 3, QTableWidgetItem(s.get('email', '')))
            self.students_table.setItem(i, 4, QTableWidgetItem(s.get('so_dien_thoai', '')))
            
            face_status = "Đã đăng ký" if s.get('du_lieu_khuon_mat') else "Chưa đăng ký"
            self.students_table.setItem(i, 5, QTableWidgetItem(face_status))
            
            self.students_table.setCellWidget(i, 6, self.create_action_buttons("student", s.get('ma_sinh_vien', '')))

    def load_subjects(self):
        subjects = self.subject_service.get_all_subjects()
        self.subjects_table.setRowCount(len(subjects))
        for i, sub in enumerate(subjects):
            self.subjects_table.setItem(i, 0, QTableWidgetItem(sub.get('ma_mon_hoc', '')))
            self.subjects_table.setItem(i, 1, QTableWidgetItem(sub.get('ten_mon_hoc', '')))
            self.subjects_table.setItem(i, 2, QTableWidgetItem(str(sub.get('so_tin_chi', ''))))
            self.subjects_table.setItem(i, 3, QTableWidgetItem(sub.get('ten_khoa', '')))
            self.subjects_table.setCellWidget(i, 4, self.create_action_buttons("subject", sub.get('ma_mon_hoc', '')))

    def load_teachers(self):
        teachers = self.teacher_service.get_all_teachers()
        self.teachers_table.setRowCount(len(teachers))
        for i, t in enumerate(teachers):
            self.teachers_table.setItem(i, 0, QTableWidgetItem(t.get('ma_giang_vien', '')))
            self.teachers_table.setItem(i, 1, QTableWidgetItem(t.get('ho_ten', '')))
            self.teachers_table.setItem(i, 2, QTableWidgetItem(t.get('ten_khoa', '')))
            self.teachers_table.setItem(i, 3, QTableWidgetItem(t.get('email', '')))
            self.teachers_table.setItem(i, 4, QTableWidgetItem(t.get('so_dien_thoai', '')))
            self.teachers_table.setItem(i, 5, QTableWidgetItem(t.get('hoc_vi', '')))
            self.teachers_table.setItem(i, 6, QTableWidgetItem(t.get('trang_thai', '')))
            self.teachers_table.setCellWidget(i, 7, self.create_action_buttons("teacher", t.get('ma_giang_vien', '')))

    def load_departments(self):
        depts = self.department_service.get_all_departments()
        self.departments_table.setRowCount(len(depts))
        for i, d in enumerate(depts):
            self.departments_table.setItem(i, 0, QTableWidgetItem(d.get('ma_khoa')))
            self.departments_table.setItem(i, 1, QTableWidgetItem(d.get('ten_khoa')))
            self.departments_table.setItem(i, 2, QTableWidgetItem(d.get('so_dien_thoai') or ''))
            self.departments_table.setItem(i, 3, QTableWidgetItem(d.get('email') or ''))
            self.departments_table.setItem(i, 4, QTableWidgetItem(d.get('phong_lam_viec') or ''))
            self.departments_table.setCellWidget(i, 5, self.create_action_buttons("department", d.get('ma_khoa')))

    def load_classes(self):
        classes = self.class_service.get_all_classes()
        self.classes_table.setRowCount(len(classes))
        for i, c in enumerate(classes):
            self.classes_table.setItem(i, 0, QTableWidgetItem(c.get('ma_lop_hoc_phan')))
            self.classes_table.setItem(i, 1, QTableWidgetItem(c.get('ten_mon_hoc')))
            self.classes_table.setItem(i, 2, QTableWidgetItem(c.get('ten_giang_vien')))
            self.classes_table.setItem(i, 3, QTableWidgetItem(str(c.get('nam_hoc'))))
            self.classes_table.setItem(i, 4, QTableWidgetItem(str(c.get('hoc_ky'))))
            self.classes_table.setItem(i, 5, QTableWidgetItem(str(c.get('si_so', 0))))
            self.classes_table.setCellWidget(i, 6, self.create_action_buttons("class", c.get('ma_lop_hoc_phan')))

    def load_admin_classes(self):
        classes = self.admin_class_service.get_all_admin_classes()
        
        current_filter = self.student_class_filter.currentData()
        self.student_class_filter.blockSignals(True)
        self.student_class_filter.clear()
        self.student_class_filter.addItem("Tất cả", None)
        for c in classes:
            self.student_class_filter.addItem(c.get('ten_lop', ''), c.get('ma_lop'))
        
        if current_filter:
            index = self.student_class_filter.findData(current_filter)
            if index >= 0:
                self.student_class_filter.setCurrentIndex(index)
        self.student_class_filter.blockSignals(False)

        self.admin_classes_table.setRowCount(len(classes))
        for i, cls in enumerate(classes):
            self.admin_classes_table.setItem(i, 0, QTableWidgetItem(cls.get('ma_lop')))
            self.admin_classes_table.setItem(i, 1, QTableWidgetItem(cls.get('ten_lop')))
            self.admin_classes_table.setCellWidget(i, 2, self.create_action_buttons('admin_class', cls.get('ma_lop')))

    def load_reports_list(self):
        reports = [
            ("overall_attendance", "Tổng hợp chuyên cần (học kỳ)", False),
            ("teacher_attendance", "Tỷ lệ chuyên cần theo giảng viên", False),
            ("absent_students", "Sinh viên vắng trên 20%", False),
            ("session_stats", "Thống kê buổi học & điểm danh", False),
            ("pie_chart", "Biểu đồ tỉ lệ có mặt/vắng", True),
            ("exam_eligibility", "Danh sách đủ/không đủ dự thi", False),
            ("compare_departments", "So sánh chuyên cần giữa khoa", False),
            ("audit_log", "Lịch sử chỉnh sửa điểm danh", False),
        ]

        self.reports_table.setRowCount(len(reports))
        for i, (rid, title, is_chart) in enumerate(reports):
            self.reports_table.setItem(i, 0, QTableWidgetItem(title))
            widget = QWidget()
            hl = QHBoxLayout(widget)
            hl.setContentsMargins(0,0,0,0)
            
            view_btn = QPushButton("Xem")
            view_btn.clicked.connect(lambda _, r=rid: self.view_report(r))
            hl.addWidget(view_btn)
            
            if not is_chart:
                export_btn = QPushButton("Xuất")
                export_btn.clicked.connect(lambda _, r=rid: self.export_report(r))
                hl.addWidget(export_btn)
            
            hl.addStretch()
            self.reports_table.setCellWidget(i, 1, widget)

    def load_sessions(self):
        from_date = self.session_from_date.date().toString('yyyy-MM-dd')
        to_date = self.session_to_date.date().toString('yyyy-MM-dd')
        sessions = self.session_service.get_sessions_by_filter(start_date=from_date, end_date=to_date)
        self.sessions_table.setRowCount(len(sessions))
        for i, s in enumerate(sessions):
            date_str = s.get('ngay_hoc', '')
            if date_str:
                try:
                    date_obj = QDate.fromString(date_str, "yyyy-MM-dd")
                    date_str = date_obj.toString("dd/MM/yyyy")
                except:
                    pass
            self.sessions_table.setItem(i, 0, QTableWidgetItem(date_str))
            time_range = f"{s.get('thoi_gian_bat_dau', '')} - {s.get('thoi_gian_ket_thuc', '')}" if s.get('thoi_gian_bat_dau') else ""
            self.sessions_table.setItem(i, 1, QTableWidgetItem(time_range))
            self.sessions_table.setItem(i, 2, QTableWidgetItem(s.get('ma_lhp', '')))
            self.sessions_table.setItem(i, 3, QTableWidgetItem(s.get('phong_hoc', '')))
            self.sessions_table.setItem(i, 4, QTableWidgetItem(s.get('ten_mon_hoc', '')))
            self.sessions_table.setItem(i, 5, QTableWidgetItem(s.get('ten_giang_vien', '')))
            self.sessions_table.setItem(i, 6, QTableWidgetItem(s.get('trang_thai', '')))
            self.sessions_table.setItem(i, 7, QTableWidgetItem(s.get('ghi_chu', '')))
            self.sessions_table.setCellWidget(i, 8, self.create_action_buttons("session", s.get('ma_buoi_hoc')))

    def create_action_buttons(self, item_type, item_id):
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(5, 2, 5, 2)
        edit_btn = QPushButton("Sửa")
        edit_btn.clicked.connect(lambda: self.edit_item(item_type, item_id))
        delete_btn = QPushButton("Xóa")
        delete_btn.clicked.connect(lambda: self.delete_item(item_type, item_id))
        layout.addWidget(edit_btn)
        layout.addWidget(delete_btn)
        return widget

    def reload_table(self, item_type):
        loaders = {
            "student": self.load_students, "teacher": self.load_teachers,
            "department": self.load_departments, "class": self.load_classes,
            "session": self.load_sessions,
            "admin_class": self.load_admin_classes,
            "subject": self.load_subjects,
        }
        if item_type in loaders:
            loaders[item_type]()

    def add_student(self):
        dialog = StudentDialog(self)
        if dialog.exec_() == QDialog.Accepted: self.load_students()

    def edit_student(self, student_code):
        dialog = StudentDialog(self, student_code=student_code)
        if dialog.exec_() == QDialog.Accepted: self.load_students()

    def import_students_from_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Chọn file danh sách sinh viên", "", "Excel Files (*.xlsx);;CSV Files (*.csv)"
        )
        if not file_path:
            return

        QApplication.setOverrideCursor(Qt.WaitCursor)
        try:
            success, message = self.student_service.import_students(file_path)
            QApplication.restoreOverrideCursor()
            
            if success:
                QMessageBox.information(self, "Thành công", message)
                self.load_students()
            else:
                QMessageBox.critical(self, "Lỗi", f"Không thể nhập dữ liệu: {message}")
        except Exception as e:
            QApplication.restoreOverrideCursor()
            QMessageBox.critical(self, "Lỗi", f"Đã xảy ra lỗi: {str(e)}")

    def add_teacher(self):
        dialog = TeacherDialog(self)
        if dialog.exec_() == QDialog.Accepted: self.load_teachers()

    def edit_teacher(self, teacher_code):
        dialog = TeacherDialog(self, teacher_code=teacher_code)
        if dialog.exec_() == QDialog.Accepted: self.load_teachers()

    def add_subject(self):
        dialog = SubjectDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            self.load_subjects()

    def edit_subject(self, subject_code):
        dialog = SubjectDialog(self, subject_code=subject_code)
        if dialog.exec_() == QDialog.Accepted:
            self.load_subjects()
    
    def add_department(self):
        dialog = DepartmentDialog(self)
        if dialog.exec_() == QDialog.Accepted: self.load_departments()

    def edit_department(self, department_id):
        dialog = DepartmentDialog(self, department_id=department_id)
        if dialog.exec_() == QDialog.Accepted: self.load_departments()

    def add_class(self):
        dialog = ClassDialog(self)
        if dialog.exec_() == QDialog.Accepted: self.load_classes()

    def edit_class(self, class_id):
        dialog = ClassDialog(self, class_id=class_id)
        if dialog.exec_() == QDialog.Accepted: self.load_classes()

    def add_session(self):
        dialog = SessionDialog(self)
        if dialog.exec_() == QDialog.Accepted: self.load_sessions()

    def edit_session(self, session_id):
        dialog = SessionDialog(self, session_id=session_id)
        if dialog.exec_() == QDialog.Accepted: self.load_sessions()

    def add_admin_class(self):
        dialog = AdminClassDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            self.load_admin_classes()

    def edit_admin_class(self, class_code):
        dialog = AdminClassDialog(self, class_code=class_code)
        if dialog.exec_() == QDialog.Accepted:
            self.load_admin_classes()

    def edit_item(self, item_type, item_id):
        handlers = {
            "student": self.edit_student, "teacher": self.edit_teacher,
            "department": self.edit_department, "class": self.edit_class,
            "session": self.edit_session,
            "admin_class": self.edit_admin_class,
            "subject": self.edit_subject,
        }
        if item_type in handlers:
            handlers[item_type](item_id)

    def delete_item(self, item_type, item_id):
        reply = QMessageBox.question(self, "Xác nhận xóa", f"Bạn có chắc muốn xóa {item_type} có mã '{item_id}' không?", QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.No:
            return

        service_map = {
            "student": self.student_service.delete_student,
            "teacher": self.teacher_service.delete_teacher,
            "department": self.department_service.delete_department,
            "class": self.class_service.delete_class,
            "session": self.session_service.delete_session,
            "admin_class": self.admin_class_service.delete_admin_class,
            "subject": self.subject_service.delete_subject,
        }
        
        if item_type not in service_map:
            QMessageBox.warning(self, "Lỗi", f"Hành động xóa không được hỗ trợ cho '{item_type}'.")
            return

        success, message = service_map[item_type](item_id)

        if success:
            QMessageBox.information(self, "Thành công", f"Đã xóa {item_type} thành công!")
            self.reload_table(item_type)
        else:
            QMessageBox.critical(self, "Lỗi", f"Không thể xóa: {message}")

    def _prepare_report_dialog(self, report_id):
        try:
            if report_id == 'overall_attendance':
                dlg_params = self._get_overall_attendance_params()
                if dlg_params is None:
                    return None
                hocky, namhoc = dlg_params
                success, data = self.api_client.get_admin_report_overall_attendance({'hocky': hocky, 'namhoc': namhoc})
                if success:
                    return Report1Dialog(self, data.get('data', []))
            
            elif report_id == 'teacher_attendance':
                success, data = self.api_client.get_admin_report_teacher_attendance()
                if success:
                    return Report2Dialog(self, data)
            
            elif report_id == 'absent_students':
                success, data = self.api_client.get_admin_report_absent_students()
                if success:
                    return Report3Dialog(self, data)
            
            elif report_id == 'session_stats':
                success, data = self.api_client.get_admin_report_session_stats()
                if success:
                    return Report4Dialog(self, data.get('data', {}))
            
            elif report_id == 'pie_chart':
                success, data = self.api_client.get_admin_report_pie_chart()
                if success:
                    return Report5Dialog(self, data.get('data', {}))
            
            elif report_id == 'exam_eligibility':
                success, data = self.api_client.get_admin_report_exam_eligible()
                if success:
                    return Report6Dialog(self, data)
            
            elif report_id == 'compare_departments':
                success, data = self.api_client.get_admin_report_compare_departments()
                if success:
                    return Report7Dialog(self, data)
            
            elif report_id == 'audit_log':
                success, data = self.api_client.get_admin_report_audit_log()
                if success:
                    return Report8Dialog(self, data)
            
            return None
        except Exception as e:
            logger.error(f"Error preparing report {report_id}: {e}")
            return None

    def view_report(self, report_id):
        QApplication.setOverrideCursor(Qt.WaitCursor)
        try:
            dlg = self._prepare_report_dialog(report_id)
            QApplication.restoreOverrideCursor()
            
            if dlg:
                dlg.exec_()
            else:
                QMessageBox.warning(self, "Thông báo", "Không thể tải dữ liệu báo cáo hoặc người dùng đã hủy.")
        except Exception as e:
            QApplication.restoreOverrideCursor()
            QMessageBox.critical(self, "Lỗi", f"Có lỗi khi tải báo cáo: {str(e)}")

    def export_report(self, report_id):
        if report_id == 'pie_chart':
            QMessageBox.information(self, "Thông báo", "Biểu đồ không hỗ trợ xuất Excel.")
            return

        QApplication.setOverrideCursor(Qt.WaitCursor)
        try:
            dlg = self._prepare_report_dialog(report_id)
            QApplication.restoreOverrideCursor()
            
            if dlg:
                dlg.export_to_excel()
            else:
                QMessageBox.warning(self, "Thông báo", "Không thể tải dữ liệu báo cáo hoặc người dùng đã hủy.")
        except Exception as e:
            QApplication.restoreOverrideCursor()
            QMessageBox.critical(self, "Lỗi", f"Có lỗi khi xuất báo cáo: {str(e)}")
    
    def _get_overall_attendance_params(self):
        dlg = QDialog(self)
        dlg.setWindowTitle("Chọn học kỳ và năm học")
        dlg.setMinimumSize(300, 150)
        layout = QVBoxLayout(dlg)
        
        form = QFormLayout()
        hocky_spin = QSpinBox()
        hocky_spin.setRange(1, 2)
        hocky_spin.setValue(1)
        
        namhoc_edit = QLineEdit()
        namhoc_edit.setText(str(datetime.now().year))
        
        form.addRow("Học kỳ:", hocky_spin)
        form.addRow("Năm học:", namhoc_edit)
        layout.addLayout(form)
        
        btn_layout = QHBoxLayout()
        ok_btn = QPushButton("OK")
        cancel_btn = QPushButton("Hủy")
        ok_btn.clicked.connect(dlg.accept)
        cancel_btn.clicked.connect(dlg.reject)
        btn_layout.addWidget(ok_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addLayout(btn_layout)
        
        if dlg.exec_() == QDialog.Accepted:
            return hocky_spin.value(), namhoc_edit.text()
        return None

    def manage_class_students(self):
        """Mở dialog quản lý sinh viên trong lớp học phần."""
        selected_items = self.classes_table.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Cảnh báo", "Vui lòng chọn một lớp học phần để quản lý.")
            return
        
        row = selected_items[0].row()
        class_id = self.classes_table.item(row, 0).text()
        class_name = self.classes_table.item(row, 1).text()
        
        dialog = ClassStudentsDialog(self, class_id=class_id, class_name=class_name)
        dialog.exec_()
        self.load_classes()

    def register_student_face(self):
        """Đăng ký khuôn mặt cho sinh viên - Chụp ảnh trực tiếp từ camera"""
        # Lấy sinh viên được chọn
        selected_items = self.students_table.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Cảnh báo", "Vui lòng chọn sinh viên cần đăng ký khuôn mặt!")
            return
        
        row = selected_items[0].row()
        student_code = self.students_table.item(row, 0).text()
        student_name = self.students_table.item(row, 1).text()
        
        # Kiểm tra xem đã đăng ký chưa
        face_status = self.students_table.item(row, 5).text()
        if face_status == "Đã đăng ký":
            reply = QMessageBox.question(
                self, "Xác nhận", 
                f"{student_name} đã đăng ký khuôn mặt.\nBạn có muốn đăng ký lại không?",
                QMessageBox.Yes | QMessageBox.No
            )
            if reply == QMessageBox.No:
                return
        
        # Tạo thư mục tự động theo mã sinh viên
        folder_path = os.path.join("face_data", student_code)
        os.makedirs(folder_path, exist_ok=True)
        
        # Mở camera để chụp ảnh
        try:
            # Khởi tạo camera
            cap = cv2.VideoCapture(0)
            if not cap.isOpened():
                QMessageBox.critical(self, "Lỗi", "Không thể mở camera!")
                return
            
            face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
            
            # Hướng dẫn
            QMessageBox.information(
                self, "Hướng dẫn",
                f"Chuẩn bị chụp ảnh khuôn mặt cho {student_name}\n\n"
                "- Nhìn thẳng vào camera\n"
                "- Giữ khuôn mặt trong khung hình\n"
                "- Hệ thống sẽ tự động chụp 30 ảnh (0.5s/ảnh)\n"
                "- Nhấn ESC để hủy"
            )
            
            count = 0
            target_count = 30
            last_capture_time = 0
            capture_delay = 0.5  # 0.5 giây giữa mỗi lần chụp
            
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                
                frame = cv2.flip(frame, 1)
                
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                faces = face_cascade.detectMultiScale(gray, 1.3, 5)
                
                # Vẽ khung và hiển thị
                for (x, y, w, h) in faces:
                    cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
                
                # Hiển thị số ảnh đã chụp
                status_color = (0, 255, 0) if len(faces) > 0 else (0, 0, 255)
                status_text = "Phat hien khuan mat" if len(faces) > 0 else "Khong tim thay khuan mat"
                
                cv2.putText(frame, f"Da chup: {count}/{target_count}", (10, 30),
                            cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                cv2.putText(frame, status_text, (10, 70),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, status_color, 2)
                cv2.putText(frame, "ESC: Huy", (10, 110),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
                
                cv2.imshow(f"Dang ky khuan mat - {student_name}", frame)
                
                # Tự động chụp ảnh khi phát hiện khuôn mặt và đủ delay
                current_time = time.time()
                if len(faces) > 0 and (current_time - last_capture_time) >= capture_delay and count < target_count:
                    count += 1
                    img_name = os.path.join(folder_path, f"{student_code}_{count}.jpg")
                    cv2.imwrite(img_name, frame)
                    print(f"Đã chụp: {img_name}")
                    last_capture_time = current_time
                    
                    if count >= target_count:
                        cap.release()
                        cv2.destroyAllWindows()
                        break
                
                key = cv2.waitKey(1)
                
                # ESC để thoát
                if key == 27:
                    cap.release()
                    cv2.destroyAllWindows()
                    if count > 0:
                        reply = QMessageBox.question(
                            self, "Xác nhận",
                            f"Bạn đã chụp {count} ảnh. Có muốn lưu không?",
                            QMessageBox.Yes | QMessageBox.No
                        )
                        if reply == QMessageBox.No:
                            return
                    else:
                        return
            
            # Đăng ký khuôn mặt
            # Training ngầm không cần hiện dialog
            QApplication.setOverrideCursor(Qt.WaitCursor)
            try:
                face_service = FaceRecognitionService()
                success, message = face_service.register_person(student_name, student_code, folder_path)
            finally:
                QApplication.restoreOverrideCursor()
            
            if success:
                QMessageBox.information(self, "Thành công", message)
                # Reload để cập nhật status
                self.load_students()
            else:
                QMessageBox.warning(self, "Lỗi", message)
                
        except Exception as e:
            if 'cap' in locals(): cap.release()
            cv2.destroyAllWindows()
            logger.error(f"Lỗi đăng ký khuôn mặt: {e}")
            QMessageBox.critical(self, "Lỗi", f"Không thể đăng ký khuôn mặt:\n{str(e)}")
    
    def show_personal_info_dialog(self):
        """Hiển thị dialog thông tin cá nhân"""
        try:
            dialog = PersonalInfoDialog(self, self.user_data)
            dialog.exec_()
        except Exception as e:
            logger.error(f"Lỗi hiển thị dialog thông tin cá nhân: {e}")
            QMessageBox.critical(self, "Lỗi", f"Không thể mở dialog thông tin cá nhân: {str(e)}")