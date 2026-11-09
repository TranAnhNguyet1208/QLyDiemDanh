from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

from services.teacher_service import TeacherService
from services.session_service import SessionService
from services.class_service import ClassService
from services.attendance_service import AttendanceService
from services.face_recognition_service import FaceRecognitionService
from services.api_service import get_api_client

from ui.qr_dialog import QRDialog
from ui.teacher_report_dialogs import (
    TeacherReport1Dialog, TeacherReport2Dialog, TeacherReport3Dialog,
    TeacherReport4Dialog, TeacherReport5Dialog, TeacherReport6Dialog
)
from ui.personal_info_dialog import PersonalInfoDialog
import logging
import cv2

logger = logging.getLogger(__name__)


class TeacherDashboard(QMainWindow):
    """Dashboard cho giảng viên, đã được tái cấu trúc để dùng API"""

    logout_requested = pyqtSignal()

    def __init__(self, user_data):
        super().__init__()
        self.user_data = user_data
        self.teacher_code = user_data.get('ma_giang_vien') or user_data.get('user_id') # API trả về user_id, dùng nó làm mã GV

        self.teacher_service = TeacherService()
        self.session_service = SessionService()
        self.class_service = ClassService()
        self.attendance_service = AttendanceService()
        self.face_service = FaceRecognitionService()
        self.api_client = get_api_client()

        self.current_session_id = None
        self.attendance_data = {}
        self.initial_attendance_data = {}
        self.last_attendance_data = {} 
        self.is_bulk_updating = False
        
        self.attendance_poll_timer = QTimer()
        self.attendance_poll_timer.timeout.connect(self.poll_attendance_updates)

        self.setWindowTitle(f"Giảng viên - {self.user_data.get('ho_ten', '')}")
        self.showMaximized()
        self.init_ui()
        self.load_initial_data()

    def init_ui(self):
        """Khởi tạo giao diện"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        header = self.create_header()
        main_layout.addWidget(header)

        tabs = QTabWidget()
        tabs.addTab(self.create_schedule_tab(), "📅 Lịch dạy")
        tabs.addTab(self.create_attendance_tab(), "✓ Điểm danh")
        tabs.addTab(self.create_students_tab(), "👥 Sinh viên")
        tabs.addTab(self.create_report_tab(), "📊 Báo cáo")
        main_layout.addWidget(tabs)
    
    def create_header(self):
        """Tạo header"""
        header_frame = QFrame()
        header_frame.setStyleSheet("background-color: #00796B; color: white; padding: 15px;")
        layout = QHBoxLayout(header_frame)
        
        info_label = QLabel(f"👨‍🏫 Giảng viên: {self.user_data.get('ho_ten', '')} ({self.teacher_code})")
        info_label.setFont(QFont('Segoe UI', 14, QFont.Bold))
        
        personal_btn = QPushButton("👤 Thông tin cá nhân")
        personal_btn.setStyleSheet("""
            QPushButton {
                background-color: #009688;
                color: white;
                padding: 8px 15px;
                border: none;
                border-radius: 3px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #00897B;
            }
        """)
        personal_btn.clicked.connect(self.show_personal_info_dialog)
        
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
        
        layout.addWidget(info_label)
        layout.addStretch()
        layout.addWidget(personal_btn)
        layout.addWidget(logout_btn)
        
        return header_frame

    def create_schedule_tab(self):
        """Tab lịch dạy"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        filter_layout = QHBoxLayout()
        filter_layout.addWidget(QLabel("Từ:"))
        self.from_date = QDateEdit(calendarPopup=True, date=QDate.currentDate())
        self.from_date.setDisplayFormat("dd/MM/yyyy")
        filter_layout.addWidget(self.from_date)
        filter_layout.addWidget(QLabel("Đến:"))
        self.to_date = QDateEdit(calendarPopup=True, date=QDate.currentDate().addDays(30))
        self.to_date.setDisplayFormat("dd/MM/yyyy")
        filter_layout.addWidget(self.to_date)
        load_btn = QPushButton("Tải lịch")
        load_btn.clicked.connect(self.load_schedule)
        filter_layout.addWidget(load_btn)
        filter_layout.addStretch()
        
        self.schedule_table = QTableWidget(columnCount=6)
        self.schedule_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.schedule_table.setHorizontalHeaderLabels(["Ngày", "Giờ", "Môn học", "Lớp", "Phòng", "Loại"])
        self.schedule_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        
        layout.addLayout(filter_layout)
        layout.addWidget(self.schedule_table)
        return widget

    def create_attendance_tab(self):
        """Tab điểm danh"""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        session_layout = QHBoxLayout()
        session_layout.addWidget(QLabel("Chọn buổi học:"))
        self.session_combo = QComboBox()
        self.session_combo.currentIndexChanged.connect(self.on_session_selected)
        session_layout.addWidget(self.session_combo, 1)
        layout.addLayout(session_layout)

        actions_layout = QHBoxLayout()
        self.gen_code_btn = QPushButton("🔑 Tạo mã")
        self.gen_code_btn.clicked.connect(self.generate_code)
        self.gen_qr_btn = QPushButton("📱 Tạo QR")
        self.gen_qr_btn.clicked.connect(self.generate_qr)
        self.face_btn = QPushButton("📷 Điểm danh khuôn mặt")
        self.face_btn.clicked.connect(self.face_attendance)
        actions_layout.addWidget(self.gen_code_btn)
        actions_layout.addWidget(self.gen_qr_btn)
        actions_layout.addWidget(self.face_btn)
        layout.addLayout(actions_layout)
        
        self.code_label = QLabel()
        self.code_label.setAlignment(Qt.AlignCenter)
        self.code_label.setStyleSheet("font-size: 20pt; font-weight: bold; color: blue;")
        layout.addWidget(self.code_label)

        bulk_layout = QHBoxLayout()
        bulk_layout.addWidget(QLabel("Chọn nhanh:"), 0)
        
        self.chk_all_present = QCheckBox("Tất cả Có mặt")
        self.chk_all_present.stateChanged.connect(lambda state: self.toggle_all_status("Có mặt", state))
        
        self.chk_all_absent_cp = QCheckBox("Tất cả Vắng CP")
        self.chk_all_absent_cp.stateChanged.connect(lambda state: self.toggle_all_status("Vắng có phép", state))
        
        self.chk_all_absent_kp = QCheckBox("Tất cả Vắng KP")
        self.chk_all_absent_kp.stateChanged.connect(lambda state: self.toggle_all_status("Vắng không phép", state))
        
        bulk_layout.addWidget(self.chk_all_present)
        bulk_layout.addWidget(self.chk_all_absent_cp)
        bulk_layout.addWidget(self.chk_all_absent_kp)
        bulk_layout.addStretch(1)
        layout.addLayout(bulk_layout)

        self.attendance_table = QTableWidget(columnCount=6)
        self.attendance_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.attendance_table.setHorizontalHeaderLabels(["Mã SV", "Họ tên", "IP", "Có mặt", "Vắng CP", "Vắng KP"])
        self.attendance_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        layout.addWidget(self.attendance_table)

        self.save_attendance_btn = QPushButton("💾 Lưu điểm danh thủ công")
        self.save_attendance_btn.clicked.connect(self.save_manual_attendance)
        layout.addWidget(self.save_attendance_btn, 0, Qt.AlignCenter)
        
        return widget
    
    def create_students_tab(self):
        """Tab sinh viên"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        class_layout = QHBoxLayout()
        class_layout.addWidget(QLabel("Chọn lớp:"))
        self.student_class_combo = QComboBox()
        self.student_class_combo.currentIndexChanged.connect(self.load_class_students)
        class_layout.addWidget(self.student_class_combo, 1)
        layout.addLayout(class_layout)
        
        self.students_table = QTableWidget(columnCount=4)
        self.students_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.students_table.setHorizontalHeaderLabels(["Mã SV", "Họ tên", "email", "SĐT"])
        self.students_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        layout.addWidget(self.students_table)
        return widget

    def create_report_tab(self):
        """Tab báo cáo"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        class_layout = QHBoxLayout()
        class_layout.addWidget(QLabel("Lớp:"))
        self.report_class_combo = QComboBox()
        self.report_class_combo.currentIndexChanged.connect(self.on_report_class_changed)
        class_layout.addWidget(self.report_class_combo, 1)
        
        consolidated_btn = QPushButton("📊 Báo cáo tổng hợp")
        consolidated_btn.clicked.connect(self.load_consolidated_report)
        class_layout.addWidget(consolidated_btn)
        layout.addLayout(class_layout)
        
        self.reports_table = QTableWidget(columnCount=2)
        self.reports_table.setHorizontalHeaderLabels(["Báo cáo", "Hành động"])
        self.reports_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        layout.addWidget(self.reports_table)
        
        return widget
    
    def on_report_class_changed(self):
        if self.report_class_combo.currentIndex() > 0:
            self.load_report_list()
    
    def load_report_list(self):
        reports = [
            ("student_attendance", "Tỷ lệ chuyên cần từng sinh viên", False),
            ("attendance_list", "Danh sách điểm danh theo buổi học", False),
            ("trend_chart", "Xu hướng chuyên cần theo tuần/tháng", True),
            ("top_students", "Top 10 sinh viên chuyên cần cao nhất", False),
            ("bottom_students", "Top 10 sinh viên chuyên cần thấp nhất", False),
            ("warning_list", "Cảnh báo sinh viên nguy cơ cấm thi", False),
        ]
        
        self.reports_table.setRowCount(len(reports))
        for i, (rid, title, is_chart) in enumerate(reports):
            self.reports_table.setItem(i, 0, QTableWidgetItem(title))
            
            widget = QWidget()
            hl = QHBoxLayout(widget)
            hl.setContentsMargins(0, 0, 0, 0)
            
            view_btn = QPushButton("Xem")
            view_btn.clicked.connect(lambda _, r=rid: self.view_teacher_report(r))
            hl.addWidget(view_btn)
            
            if not is_chart:
                export_btn = QPushButton("Xuất")
                export_btn.clicked.connect(lambda _, r=rid: self.export_teacher_report(r))
                hl.addWidget(export_btn)
            
            hl.addStretch()
            self.reports_table.setCellWidget(i, 1, widget)

    def load_initial_data(self):
        self.load_schedule()
        self.load_sessions_for_combos()
        self.load_teacher_classes_for_combos()

    def load_schedule(self):
        from_date = self.from_date.date().toString('yyyy-MM-dd')
        to_date = self.to_date.date().toString('yyyy-MM-dd')
        schedule = self.teacher_service.get_teacher_schedule(self.teacher_code, from_date, to_date)
        self.schedule_table.setRowCount(len(schedule))
        for i, item in enumerate(schedule):
            self.schedule_table.setItem(i, 0, QTableWidgetItem(item.get('ngay_hoc')))
            self.schedule_table.setItem(i, 1, QTableWidgetItem(f"{item.get('thoi_gian_bat_dau')} - {item.get('thoi_gian_ket_thuc')}"))
            self.schedule_table.setItem(i, 2, QTableWidgetItem(item.get('ten_mon_hoc')))
            self.schedule_table.setItem(i, 3, QTableWidgetItem(item.get('ma_lhp')))
            self.schedule_table.setItem(i, 4, QTableWidgetItem(item.get('phong_hoc')))
            self.schedule_table.setItem(i, 5, QTableWidgetItem(item.get('loai_buoi_hoc')))

    def load_sessions_for_combos(self):
        """Tải các buổi học hôm nay và ngày mai cho combo box điểm danh"""
        today = QDate.currentDate().toString('yyyy-MM-dd')
        tomorrow = QDate.currentDate().addDays(1).toString('yyyy-MM-dd')
        sessions = self.session_service.get_sessions_by_filter(start_date=today, end_date=tomorrow, teacher_id=self.teacher_code)
        self.session_combo.clear()
        self.session_combo.addItem("-- Chọn buổi học --", None)
        for s in sessions:
            self.session_combo.addItem(f"{s.get('ngay_hoc')} - {s.get('ten_mon_hoc')} ({s.get('ma_lhp')})", s.get('ma_buoi_hoc'))

    def load_teacher_classes_for_combos(self):
        classes = self.teacher_service.get_teacher_classes(self.teacher_code)
        self.student_class_combo.clear()
        self.report_class_combo.clear()
        self.student_class_combo.addItem("-- Chọn lớp --", None)
        self.report_class_combo.addItem("-- Chọn lớp --", None)
        for c in classes:
            text = f"{c.get('ma_lop_hoc_phan')} - {c.get('ten_mon_hoc')}"
            self.student_class_combo.addItem(text, c.get('ma_lop_hoc_phan'))
            self.report_class_combo.addItem(text, c.get('ma_lop_hoc_phan'))
    
    def on_session_selected(self):
        self.attendance_poll_timer.stop()
        if self.session_combo.currentIndex() > 0:
            self.current_session_id = self.session_combo.currentData()
            self.load_attendance_for_session()
            self.attendance_poll_timer.start(3000)
        else:
            self.current_session_id = None
            self.attendance_table.clearContents()
            self.attendance_table.setRowCount(0)
            self.last_attendance_data.clear()
    
    def load_attendance_for_session(self):
        """Tải danh sách điểm danh của một buổi học"""
        if not self.current_session_id: return
        
        
        attendance_list = self.attendance_service.get_session_attendance(self.current_session_id)
        
        if self.attendance_table.rowCount() != len(attendance_list):
            self.attendance_table.setRowCount(len(attendance_list))
        
        for i, s in enumerate(attendance_list):
            student_id = s.get('ma_sinh_vien')
            server_status = s.get('trang_thai')
            
            if student_id not in self.attendance_data:
                self.attendance_data[student_id] = {'status': server_status, 'note': '', 'dirty': False}
                self.initial_attendance_data[student_id] = server_status
            else:
                self.initial_attendance_data[student_id] = server_status
                if not self.attendance_data[student_id].get('dirty'):
                    self.attendance_data[student_id]['status'] = server_status

            self.attendance_table.setItem(i, 0, QTableWidgetItem(student_id))
            self.attendance_table.setItem(i, 1, QTableWidgetItem(s.get('ho_ten')))
            self.attendance_table.setItem(i, 2, QTableWidgetItem(s.get('ip', '')))
            
            current_display_status = self.attendance_data[student_id]['status']

            for j, status in enumerate(['Có mặt', 'Vắng có phép', 'Vắng không phép']):
                checkbox = self.attendance_table.cellWidget(i, j + 3)
                if not checkbox:
                    checkbox = QCheckBox()
                    self.attendance_table.setCellWidget(i, j + 3, checkbox)
                    checkbox.stateChanged.connect(lambda state, sid=student_id, st=status: self.on_status_changed(sid, st, state))
                
                checkbox.blockSignals(True)
                checkbox.setChecked(current_display_status == status)
                checkbox.blockSignals(False)

    def on_status_changed(self, student_id, status, state):
        if state == Qt.Checked:
            initial_status = self.initial_attendance_data.get(student_id)
            current_saved_status = self.attendance_data[student_id].get('status')
            
            # 2. There was an initial status from DB (not None/Empty/"Chưa điểm danh")
            
            note = ""
            is_saved_data = initial_status and initial_status != "Chưa điểm danh"
            
            if not self.is_bulk_updating and is_saved_data and initial_status != status:
                 text, ok = QInputDialog.getText(self, "Ghi chú thay đổi", 
                                               f"Bạn đang thay đổi trạng thái của SV {student_id}\n"
                                               f"Từ '{initial_status}' sang '{status}'.\n"
                                               f"Vui lòng nhập lý do:", QLineEdit.Normal, "")
                 if ok:
                     note = text
            
            self.attendance_data[student_id]['status'] = status
            self.attendance_data[student_id]['note'] = note
            self.attendance_data[student_id]['dirty'] = True
            
            row = self.find_student_row(student_id)
            if row != -1:
                for i, st in enumerate(['Có mặt', 'Vắng có phép', 'Vắng không phép']):
                    if st != status:
                        self.attendance_table.cellWidget(row, i + 3).setChecked(False)

    def toggle_all_status(self, status, state):
        if state != Qt.Checked:
            return
            
        self.is_bulk_updating = True
        try:
            if status == "Có mặt":
                self.chk_all_absent_cp.setChecked(False)
                self.chk_all_absent_kp.setChecked(False)
            elif status == "Vắng có phép":
                self.chk_all_present.setChecked(False)
                self.chk_all_absent_kp.setChecked(False)
            elif status == "Vắng không phép":
                self.chk_all_present.setChecked(False)
                self.chk_all_absent_cp.setChecked(False)

            for i in range(self.attendance_table.rowCount()):
                col_idx = 3
                if status == 'Vắng có phép': col_idx = 4
                elif status == 'Vắng không phép': col_idx = 5
                
                checkbox = self.attendance_table.cellWidget(i, col_idx)
                if checkbox:
                    checkbox.setChecked(True)
        finally:
            self.is_bulk_updating = False
    
    def find_student_row(self, student_id):
        for i in range(self.attendance_table.rowCount()):
            if self.attendance_table.item(i, 0).text() == student_id:
                return i
        return -1

    def load_class_students(self):
        """Tải sinh viên của một lớp"""
        class_id = self.student_class_combo.currentData()
        if not class_id: return
        students = self.teacher_service.get_class_students(class_id)
        self.students_table.setRowCount(len(students))
        for i, s in enumerate(students):
            self.students_table.setItem(i, 0, QTableWidgetItem(s.get('ma_sinh_vien')))
            self.students_table.setItem(i, 1, QTableWidgetItem(s.get('ho_ten')))
            self.students_table.setItem(i, 2, QTableWidgetItem(s.get('email')))
            self.students_table.setItem(i, 3, QTableWidgetItem(s.get('so_dien_thoai')))

    def _prepare_report_dialog(self, report_id):
        class_id = self.report_class_combo.currentData()
        class_name = self.report_class_combo.currentText()
        
        if not class_id and report_id != 'consolidated':
            QMessageBox.warning(self, "Cảnh báo", "Vui lòng chọn lớp học phần")
            return None
            
        try:
            if report_id == 'student_attendance':
                success, data = self.api_client.get_teacher_report_student_attendance(class_id)
                if success:
                    return TeacherReport1Dialog(self, data, class_name)
            
            elif report_id == 'attendance_list':
                success, data = self.api_client.get_teacher_report_attendance_list(class_id)
                if success:
                    return TeacherReport2Dialog(self, data, class_name)
            
            elif report_id == 'trend_chart':
                success, chart_data = self.api_client.get_teacher_report_trend(class_id)
                if success and chart_data:
                    return TeacherReport3Dialog(self, chart_data, class_name)
            
            elif report_id == 'top_students':
                success, data = self.api_client.get_teacher_report_special_students(class_id, 'cao')
                if success:
                    return TeacherReport4Dialog(self, data, class_name, 'cao')
            
            elif report_id == 'bottom_students':
                success, data = self.api_client.get_teacher_report_special_students(class_id, 'thap')
                if success:
                    return TeacherReport4Dialog(self, data, class_name, 'thap')
            
            elif report_id == 'warning_list':
                success, data = self.api_client.get_teacher_report_warning(class_id)
                if success:
                    return TeacherReport6Dialog(self, data, class_name)
            
            return None
        except Exception as e:
            logger.error(f"Error preparing report {report_id}: {e}")
            return None

    def view_teacher_report(self, report_id):
        QApplication.setOverrideCursor(Qt.WaitCursor)
        try:
            dlg = self._prepare_report_dialog(report_id)
            QApplication.restoreOverrideCursor()
            
            if dlg:
                dlg.exec_()
            else:
                if self.report_class_combo.currentData(): 
                    QMessageBox.warning(self, "Thông báo", "Không thể tải dữ liệu báo cáo.")
        except Exception as e:
            QApplication.restoreOverrideCursor()
            QMessageBox.critical(self, "Lỗi", f"Có lỗi khi tải báo cáo: {str(e)}")
    
    def export_teacher_report(self, report_id):
        QApplication.setOverrideCursor(Qt.WaitCursor)
        try:
            dlg = self._prepare_report_dialog(report_id)
            QApplication.restoreOverrideCursor()
            
            if dlg:
                dlg.export_to_excel()
            else:
                if self.report_class_combo.currentData():
                    QMessageBox.warning(self, "Thông báo", "Không thể tải dữ liệu báo cáo.")
        except Exception as e:
            QApplication.restoreOverrideCursor()
            QMessageBox.critical(self, "Lỗi", f"Có lỗi khi xuất báo cáo: {str(e)}")
    
    def load_consolidated_report(self):
        """Tải báo cáo tổng hợp cho giảng viên"""
        QApplication.setOverrideCursor(Qt.WaitCursor)
        try:
            success, data = self.api_client.get_teacher_report_consolidated(self.teacher_code)
            if success:
                dlg = TeacherReport5Dialog(self, data, self.user_data.get('ho_ten', ''))
                QApplication.restoreOverrideCursor()
                dlg.exec_()
            else:
                QApplication.restoreOverrideCursor()
                QMessageBox.critical(self, "Lỗi", "Không thể tải báo cáo tổng hợp.")
        except Exception as e:
            QApplication.restoreOverrideCursor()
            QMessageBox.critical(self, "Lỗi", f"Có lỗi: {str(e)}")

    def poll_attendance_updates(self):
        """Polling để cập nhật danh sách điểm danh (được gọi mỗi 3 giây)"""
        if not self.current_session_id:
            return
        
        try:
            attendance_list = self.attendance_service.get_session_attendance(self.current_session_id)
            if attendance_list:
                self.update_attendance_from_api(attendance_list)
        except Exception as e:
            logger.error(f"Lỗi polling điểm danh: {e}")
    
    def update_attendance_from_api(self, attendance_list: list):
        """Cập nhật bảng điểm danh từ API response"""
        try:
            new_attendance_data = {}
            
            for s in attendance_list:
                ma_sv = s.get('ma_sinh_vien', '')
                trang_thai = s.get('trang_thai', 'Chưa điểm danh')
                
                self.initial_attendance_data[ma_sv] = trang_thai
                
                if ma_sv not in self.attendance_data:
                     self.attendance_data[ma_sv] = {'status': trang_thai, 'note': '', 'dirty': False}
                
                if not self.attendance_data[ma_sv].get('dirty'):
                    self.attendance_data[ma_sv]['status'] = trang_thai
                    
                    row = self.find_student_row(ma_sv)
                    if row != -1:
                        self.attendance_table.item(row, 1).setText(s.get('ho_ten', ''))
                        self.attendance_table.item(row, 2).setText(s.get('ip', ''))

                        for j, status in enumerate(['Có mặt', 'Vắng có phép', 'Vắng không phép']):
                            checkbox = self.attendance_table.cellWidget(row, j + 3)
                            if checkbox:
                                checkbox.blockSignals(True)
                                checkbox.setChecked(trang_thai == status)
                                checkbox.blockSignals(False)
            
        
        except Exception as e:
            logger.error(f"Lỗi cập nhật bảng điểm danh: {e}")
    
    def generate_code(self):
        """Tạo mã điểm danh bằng chữ"""
        if not self.current_session_id: return
        import random, string
        code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
        success, message = self.attendance_service.generate_attendance_code(self.current_session_id, code)
        if success:
            self.code_label.setText(f"Mã điểm danh: {code}")
            QMessageBox.information(self, "Thành công", f"Mã điểm danh là: {code}")
        else:
            QMessageBox.critical(self, "Lỗi", message)

    def generate_qr(self):
        """Tạo và hiển thị mã QR"""
        if not self.current_session_id: return
        success, message, qr_base64, qr_link = self.attendance_service.generate_qr_code_session(self.current_session_id)
        if success:
            dialog = QRDialog(qr_base64, str(self.current_session_id), self, qr_link=qr_link)
            dialog.exec_()
        else:
            QMessageBox.critical(self, "Lỗi", message)

    def save_manual_attendance(self):
        """Lưu điểm danh thủ công cho các sinh viên đã được tick"""
        if not self.current_session_id: return
        saved_count = 0
        for student_id, data in self.attendance_data.items():
            status = data.get('status')
            note = data.get('note', '')
            if status:
                success, msg = self.attendance_service.attend_manual(self.current_session_id, student_id, status, note)
                if success: 
                    saved_count += 1
                    if student_id in self.attendance_data:
                        self.attendance_data[student_id]['dirty'] = False
                else: logger.error(f"Lỗi lưu điểm danh cho SV {student_id}: {msg}")
        QMessageBox.information(self, "Hoàn tất", f"Đã lưu điểm danh cho {saved_count} sinh viên.")
        self.load_attendance_for_session()

    def face_attendance(self):
        """Điểm danh bằng khuôn mặt - Mở camera để nhận diện"""
        if not self.current_session_id:
            QMessageBox.warning(self, "Cảnh báo", "Vui lòng chọn buổi học!")
            return
        
        # Sync model from backend before starting
        try:
            self.statusBar().showMessage("Đang đồng bộ dữ liệu khuôn mặt từ máy chủ...")
            QApplication.processEvents() # Update UI
            success, msg = self.face_service.sync_model_from_server()
            if success:
                logger.info("Synced face model from server.")
            else:
                logger.warning(f"Could not sync model: {msg}")
            self.statusBar().clearMessage()
        except Exception as e:
            logger.error(f"Error syncing model: {e}")

        try:
            # Kiểm tra model đã được train chưa
            if not self.face_service.is_trained:
                 QMessageBox.warning(
                    self, "Cảnh báo", 
                    "Chưa có dữ liệu khuôn mặt nào được đăng ký (hoặc chưa đồng bộ được)!\nVui lòng đăng ký khuôn mặt cho sinh viên trước."
                )
                 return

            # Hướng dẫn
            QMessageBox.information(
                self, "Hướng dẫn",
                "Điểm danh bằng khuôn mặt:\n\n"
                "- Sinh viên lần lượt đứng trước camera\n"
                "- Hệ thống sẽ tự động nhận diện và điểm danh\n"
                "- Nhấn ESC để kết thúc\n"
                "- Mỗi sinh viên chỉ được điểm danh 1 lần"
            )
            
            # Mở camera
            cap = cv2.VideoCapture(0)
            if not cap.isOpened():
                QMessageBox.critical(self, "Lỗi", "Không thể mở camera!")
                return
            
            # Load danh sách sinh viên đã điểm danh (theo face recognition trong session này)
            attended_students = set()
            
            import time
            last_recognition_time = 0
            recognition_cooldown = 2.0  # 2 giây cooldown giữa các lần nhận diện
            
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                
                # Mirror (flip) để dễ nhìn
                frame = cv2.flip(frame, 1)
                
                current_time = time.time()
                
                # Nhận diện khuôn mặt
                success, result = self.face_service.recognize_face(frame)
                
                # Hiển thị thông tin
                if success and result:
                    student_code = result.get('student_id', '')
                    student_name = result.get('name', '')
                    confidence = result.get('confidence', 0)
                    
                    # Vẽ khung xanh và thông tin
                    cv2.putText(frame, f"Ma: {student_code}", (10, 70),
                               cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                    
                    # Kiểm tra đã điểm danh chưa (trong lần quét này)
                    if student_code in attended_students:
                        cv2.putText(frame, "DA DIEM DANH ROI!", (10, 150),
                                   cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 165, 255), 2)
                    else:
                        cv2.putText(frame, "Dang diem danh...", (10, 150),
                                   cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 0), 2)
                        
                        # Điểm danh tự động (với cooldown)
                        if (current_time - last_recognition_time) >= recognition_cooldown:
                            try:
                                # Gọi API điểm danh thủ công (giống legacy logic)
                                success_save, message = self.attendance_service.attend_manual(
                                    self.current_session_id,
                                    student_code,
                                    'Có mặt',
                                    f"Điểm danh khuôn mặt ({confidence*100:.0f}%)"
                                )
                                
                                if success_save:
                                    # Cập nhật attendance_data
                                    if student_code in self.attendance_data:
                                         self.attendance_data[student_code]['status'] = 'Có mặt'
                                         self.attendance_data[student_code]['dirty'] = False # Đã lưu lên server
                                    
                                    # Update checkbox trong table ngay lập tức
                                    row = self.find_student_row(student_code)
                                    if row >= 0:
                                        # Bỏ check tất cả các checkbox khác
                                        for col in range(2, 5):
                                            checkbox_widget = self.attendance_table.cellWidget(row, col)
                                            if checkbox_widget:
                                                checkbox = checkbox_widget.findChild(QCheckBox)
                                                if checkbox:
                                                    checkbox.blockSignals(True)
                                                    checkbox.setChecked(col == 3)  # Chỉ check cột "Có mặt" (index 3)
                                                    checkbox.blockSignals(False)
                                    
                                    attended_students.add(student_code)
                                    logger.info(f"Đã điểm danh: {student_name} ({student_code})")
                                else:
                                     # Nếu lỗi (ví dụ đã điểm danh rồi), vẫn coi là đã xử lý để không spam API
                                     if "đã điểm danh" in str(message).lower():
                                         attended_students.add(student_code)
                                     logger.warning(f"API trả về: {message}")

                                last_recognition_time = current_time
                            
                            except Exception as e:
                                logger.error(f"Lỗi điểm danh: {e}")
                else:
                    # Hiển thị thông báo lỗi nếu có
                    msg = result.get('message', 'Khong nhan dien duoc') if result else 'Khong nhan dien duoc'
                    cv2.putText(frame, msg, (10, 30),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                
                cv2.putText(frame, "ESC: Ket thuc", (10, frame.shape[0] - 20),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
                
                cv2.imshow("Diem danh khuon mat", frame)
                
                # ESC để thoát
                if cv2.waitKey(1) == 27:
                    break
            
            cap.release()
            cv2.destroyAllWindows()
            
            self.load_attendance_for_session()
            
            QMessageBox.information(
                self, "Hoàn tất",
                f"Đã đánh dấu {len(attended_students)} sinh viên!\n\n"
                "Vui lòng kiểm tra và bấm 'Lưu điểm danh' để hoàn tất."
            )
        
        except Exception as e:
            logger.error(f"Lỗi điểm danh khuôn mặt: {e}")
            QMessageBox.critical(self, "Lỗi", f"Không thể điểm danh:\n{str(e)}")

    def show_personal_info_dialog(self):
        """Hiển thị dialog thông tin cá nhân"""
        try:
            dialog = PersonalInfoDialog(self, self.user_data)
            dialog.exec_()
        except Exception as e:
            logger.error(f"Lỗi hiển thị dialog thông tin cá nhân: {e}")
            QMessageBox.critical(self, "Lỗi", f"Không thể mở dialog thông tin cá nhân: {str(e)}")
    
    def closeEvent(self, event):
        """Dừng timer khi đóng window"""
        self.attendance_poll_timer.stop()
        super().closeEvent(event)