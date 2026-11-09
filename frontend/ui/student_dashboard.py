
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from services.student_api_helper import StudentAPIHelper
from services.api_service import get_api_client
from ui.personal_info_dialog import PersonalInfoDialog
from ui.calendar_view import CalendarView
import logging

logger = logging.getLogger(__name__)


class ReportWorker(QThread):
    """Worker thread để tải dữ liệu báo cáo dưới nền"""
    finished = pyqtSignal(bool, object)

    def __init__(self, api_func, *args, **kwargs):
        super().__init__()
        self.api_func = api_func
        self.args = args
        self.kwargs = kwargs

    def run(self):
        try:
            # api_func được kỳ vọng trả về (success, data)
            result = self.api_func(*self.args, **self.kwargs)
            if isinstance(result, tuple) and len(result) >= 2:
                self.finished.emit(result[0], result[1])
            else:
                self.finished.emit(False, "Invalid response format")
        except Exception as e:
            logger.error(f"Worker error: {e}")
            self.finished.emit(False, str(e))



class StudentDashboard(QMainWindow):
    """Dashboard cho sinh viên"""
    
    logout_requested = pyqtSignal()
    
    def __init__(self, user_data):
        super().__init__()
        self.user_data = user_data
        self.student_code = user_data.get('ma_sinh_vien') or user_data.get('student_code', '')
        self.ma_sv = self.student_code  # API sử dụng MaSinhVien
        
        logger.info(f"StudentDashboard initialized with user_data: {user_data}")
        logger.info(f"Extracted student_code (ma_sv): '{self.ma_sv}'")
        
        if not self.ma_sv:
            QMessageBox.warning(None, "Cảnh báo", "Không tìm thấy mã sinh viên trong dữ liệu đăng nhập!")
        
        self.api_helper = StudentAPIHelper()
        self.api_client = get_api_client()
        
        self.current_session_id = None
        
        self.init_ui()
        self.load_data()
    
    def format_date_vn(self, date_str):
        """Chuyển đổi định dạng ngày từ yyyy-MM-dd sang dd/MM/yyyy"""
        if not date_str: return ""
        try:
            # Nếu là datetime object
            if hasattr(date_str, 'toString'):
                return date_str.toString("dd/MM/yyyy")
            
            # Nếu là string
            qdate = QDate.fromString(str(date_str), "yyyy-MM-dd")
            if qdate.isValid():
                return qdate.toString("dd/MM/yyyy")
            return str(date_str)
        except:
            return str(date_str)

    def init_ui(self):
        """Khởi tạo giao diện"""
        self.setWindowTitle(f"Sinh viên - {self.user_data.get('ho_ten', '')}")
        self.showMaximized()
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QVBoxLayout()
        
        header = self.create_header()
        main_layout.addWidget(header)
        
        self.warning_frame = QFrame()
        self.warning_frame.setVisible(False)
        main_layout.addWidget(self.warning_frame)
        
        tabs = QTabWidget()
        tabs.addTab(self.create_attendance_tab(), "Điểm danh")
        tabs.addTab(self.create_schedule_tab(), "Lịch học")
        tabs.addTab(self.create_registration_tab(), "Đăng ký học phần")
        
        main_layout.addWidget(tabs)
        
        central_widget.setLayout(main_layout)
    
    def create_header(self):
        """Tạo header"""
        header_frame = QFrame()
        header_frame.setStyleSheet("""
            QFrame {
                background-color: #2c3e50;
                color: white;
                padding: 15px;
            }
        """)
        
        layout = QHBoxLayout(header_frame)
        
        info_label = QLabel(f"Sinh viên: {self.user_data.get('ho_ten', '')} - {self.student_code}")
        info_label.setFont(QFont('Segoe UI', 14, QFont.Bold))
        
        history_btn = QPushButton("📋 Lịch sử điểm danh")
        history_btn.setStyleSheet("""
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
        history_btn.clicked.connect(self.show_attendance_history_dialog)
        
        stats_btn = QPushButton("📊 Thống kê chuyên cần")
        stats_btn.setStyleSheet("""
            QPushButton {
                background-color: #9b59b6;
                color: white;
                padding: 8px 15px;
                border: none;
                border-radius: 3px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #8e44ad;
            }
        """)
        stats_btn.clicked.connect(self.show_attendance_stats_dialog)
        
        personal_btn = QPushButton("👤 Thông tin cá nhân")
        personal_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: white;
                padding: 8px 15px;
                border: 2px solid white;
                border-radius: 3px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 0.1);
            }
        """)
        personal_btn.clicked.connect(self.show_personal_info)
        
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
        layout.addWidget(history_btn)
        layout.addWidget(stats_btn)
        layout.addWidget(personal_btn)
        layout.addWidget(logout_btn)
        
        return header_frame

    def create_attendance_tab(self):
        """Tab điểm danh bằng mã"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        session_group = QGroupBox("📚 Chọn buổi học")
        session_layout = QVBoxLayout()
        
        # Dropdown chọn session
        session_select_layout = QHBoxLayout()
        session_select_layout.addWidget(QLabel("Buổi học hôm nay:"))
        
        self.session_combo = QComboBox()
        self.session_combo.setStyleSheet("""
            QComboBox {
                padding: 10px;
                font-size: 12pt;
                border: 2px solid #bdc3c7;
                border-radius: 5px;
                background: white;
            }
            QComboBox:hover {
                border: 2px solid #3498db;
            }
        """)
        self.session_combo.currentIndexChanged.connect(self.on_session_changed)
        session_select_layout.addWidget(self.session_combo, 1)
        
        refresh_btn = QPushButton("🔄")
        refresh_btn.setToolTip("Tải lại danh sách buổi học")
        refresh_btn.clicked.connect(self.load_sessions)
        session_select_layout.addWidget(refresh_btn)
        
        session_layout.addLayout(session_select_layout)
        
        # Thông tin session đã chọn
        self.session_info_label = QLabel("Vui lòng chọn buổi học để điểm danh")
        self.session_info_label.setStyleSheet("""
            padding: 15px;
            background: #f8f9fa;
            border-left: 4px solid #3498db;
            border-radius: 5px;
            font-size: 11pt;
        """)
        self.session_info_label.setWordWrap(True)
        session_layout.addWidget(self.session_info_label)
        
        session_group.setLayout(session_layout)
        layout.addWidget(session_group)
        
        # Form nhập mã
        form_group = QGroupBox("Điểm danh bằng mã")
        form_layout = QFormLayout()
        
        self.code_input = QLineEdit()
        self.code_input.setPlaceholderText("Nhập mã điểm danh (ví dụ: ABC123)")
        self.code_input.setStyleSheet("""
            QLineEdit {
                padding: 15px;
                font-size: 14pt;
                border: 2px solid #bdc3c7;
                border-radius: 5px;
            }
            QLineEdit:focus {
                border: 3px solid #2ecc71;
            }
        """)
        self.code_input.returnPressed.connect(self.attend_by_code)
        
        attend_btn = QPushButton("✓ Điểm danh ngay")
        attend_btn.setCursor(Qt.PointingHandCursor)
        attend_btn.setStyleSheet("""
            QPushButton {
                background-color: #2ecc71;
                color: white;
                padding: 15px 30px;
                border: none;
                border-radius: 5px;
                font-weight: bold;
                font-size: 12pt;
            }
            QPushButton:hover {
                background-color: #27ae60;
            }
            QPushButton:pressed {
                background-color: #219150;
            }
        """)
        attend_btn.clicked.connect(self.attend_by_code)
        
        form_layout.addRow("Mã điểm danh:", self.code_input)
        form_layout.addRow("", attend_btn)
        
        form_group.setLayout(form_layout)
        layout.addWidget(form_group)
        
        # Hướng dẫn
        guide_label = QLabel()
        guide_label.setText(
            "💡 <b>Hướng dẫn điểm danh:</b><br><br>"
            "<b>Bước 1:</b> Chọn buổi học từ dropdown phía trên<br>"
            "<b>Bước 2:</b> Nhận mã điểm danh từ giảng viên<br>"
            "<b>Bước 3:</b> Nhập mã vào ô trên (không phân biệt hoa thường)<br>"
            "<b>Bước 4:</b> Nhấn nút 'Điểm danh ngay' hoặc Enter<br><br>"
            "<b style='color: #f44336;'>⚠️ Lưu ý:</b> Mã có hiệu lực đến khi kết thúc buổi học!"
        )
        guide_label.setStyleSheet("""
            padding: 20px;
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                        stop:0 #fff9c4, stop:1 #fff59d);
            border-left: 5px solid #fbc02d;
            border-radius: 5px;
            font-size: 11pt;
        """)
        guide_label.setWordWrap(True)
        layout.addWidget(guide_label)
        
        layout.addStretch()
        
        widget.setLayout(layout)
        return widget

    def create_schedule_tab(self):
        """Tab lịch học sử dụng CalendarView"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        header_layout = QHBoxLayout()
        
        title = QLabel("📅 Lịch học")
        title.setFont(QFont('Segoe UI', 14, QFont.Bold))
        header_layout.addWidget(title)
        
        header_layout.addStretch()
        
        # CalendarView không cần date picker vì nó có navigation riêng
        load_btn = QPushButton("🔄 Tải lại lịch")
        load_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                padding: 8px 16px;
                border: none;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        load_btn.clicked.connect(self.load_schedule)
        
        header_layout.addWidget(load_btn)
        
        layout.addLayout(header_layout)
        
        # Thay thế QTableWidget bằng CalendarView
        self.calendar_view = CalendarView()
        layout.addWidget(self.calendar_view)
        
        widget.setLayout(layout)
        return widget

    def create_registration_tab(self):
        """Tab đăng ký học phần"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        title_label = QLabel("Đăng ký học phần")
        title_label.setFont(QFont('Segoe UI', 14, QFont.Bold))
        
        refresh_btn = QPushButton("🔄 Tải danh sách lớp")
        refresh_btn.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                padding: 12px 25px;
                border: none;
                border-radius: 5px;
                font-weight: bold;
                font-size: 11pt;
            }
            QPushButton:hover {
                background-color: #219150;
            }
        """)
        refresh_btn.clicked.connect(self.load_registration_data)
        
        header_layout = QHBoxLayout()
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        header_layout.addWidget(refresh_btn)
        
        layout.addLayout(header_layout)
        
        self.registration_table = QTableWidget()
        self.registration_table.setColumnCount(7)
        self.registration_table.setHorizontalHeaderLabels([
            "Mã LHP", "Môn học", "Giảng viên", "Học kỳ", "Năm học", "Sĩ số", "Hành động"
        ])
        self.registration_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        
        layout.addWidget(self.registration_table)
        
        widget.setLayout(layout)
        return widget

    def load_registration_data(self):
        """Load danh sách lớp học phần để đăng ký"""
        try:
            success, classes = self.api_helper.get_available_classes(self.ma_sv)
            
            if not success:
                QMessageBox.warning(self, "Lỗi", "Không thể tải danh sách lớp học phần")
                return
            
            self.registration_table.setRowCount(len(classes))
            
            for i, cls in enumerate(classes):
                ma_lhp = cls.get('ma_lhp', '')
                self.registration_table.setItem(i, 0, QTableWidgetItem(ma_lhp))
                self.registration_table.setItem(i, 1, QTableWidgetItem(cls.get('ten_mon_hoc', '')))
                self.registration_table.setItem(i, 2, QTableWidgetItem(cls.get('ten_giang_vien', '')))
                self.registration_table.setItem(i, 3, QTableWidgetItem(str(cls.get('hoc_ky', ''))))
                self.registration_table.setItem(i, 4, QTableWidgetItem(str(cls.get('nam_hoc', ''))))
                self.registration_table.setItem(i, 5, QTableWidgetItem(str(cls.get('si_so', 0))))
                
                is_registered = cls.get('da_dang_ky', False)
                
                btn_widget = QWidget()
                btn_layout = QHBoxLayout(btn_widget)
                btn_layout.setContentsMargins(0, 0, 0, 0)
                btn_layout.setAlignment(Qt.AlignCenter)
                
                if is_registered:
                    action_btn = QPushButton("Hủy đăng ký")
                    action_btn.setStyleSheet("background-color: #f44336; color: white; border: none; padding: 5px 10px; border-radius: 3px;")
                    action_btn.clicked.connect(lambda _, c=ma_lhp: self.cancel_registration(c))
                else:
                    action_btn = QPushButton("Đăng ký")
                    action_btn.setStyleSheet("background-color: #4CAF50; color: white; border: none; padding: 5px 10px; border-radius: 3px;")
                    action_btn.clicked.connect(lambda _, c=ma_lhp: self.register_class(c))
                
                btn_layout.addWidget(action_btn)
                self.registration_table.setCellWidget(i, 6, btn_widget)
                
        except Exception as e:
            logger.error(f"Lỗi load danh sách đăng ký: {e}")
            QMessageBox.warning(self, "Lỗi", f"Có lỗi xảy ra: {str(e)}")

    def register_class(self, ma_lhp):
        """Xử lý đăng ký lớp"""
        reply = QMessageBox.question(self, 'Xác nhận', f'Bạn có chắc muốn đăng ký lớp {ma_lhp}?',
                                      QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            success, msg = self.api_helper.register_class(self.ma_sv, ma_lhp)
            if success:
                QMessageBox.information(self, "Thành công", msg)
                self.load_registration_data()
            else:
                QMessageBox.warning(self, "Thất bại", msg)

    def cancel_registration(self, ma_lhp):
        """Xử lý hủy đăng ký lớp"""
        reply = QMessageBox.question(self, 'Xác nhận', f'Bạn có chắc muốn hủy đăng ký lớp {ma_lhp}?',
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            success, msg = self.api_helper.cancel_registration(self.ma_sv, ma_lhp)
            if success:
                QMessageBox.information(self, "Thành công", msg)
                self.load_registration_data()
            else:
                QMessageBox.warning(self, "Thất bại", msg)

    def load_data(self):
        """Load dữ liệu ban đầu từ API"""
        self.load_detailed_warning()
        self.load_sessions()
        self.load_registration_data()
        # Load lịch học sau khi UI đã sẵn sàng
        QTimer.singleShot(100, self.load_schedule)
    
    def load_sessions(self):
        """Load danh sách buổi học cho sinh viên"""
        try:
            today = QDate.currentDate()
            # Lấy buổi học từ hôm nay đến 30 ngày sau
            start_date = today.toString('yyyy-MM-dd')
            end_date = today.addDays(30).toString('yyyy-MM-dd')
            
            logger.info(f"Loading sessions for {self.ma_sv} from {start_date} to {end_date}")
            
            success, sessions = self.api_helper.get_student_sessions(self.ma_sv, start_date, end_date)
            
            if not success or not sessions:
                logger.warning(f"Không thể tải danh sách buổi học cho {self.ma_sv}")
                self.session_combo.addItem("Không có buổi học", None)
                return
            
            # Xóa các item cũ
            self.session_combo.clear()
            
            # Thêm item "Chọn buổi học" mặc định
            self.session_combo.addItem("-- Chọn buổi học --", None)
            
            # Thêm các buổi học vào combo
            for session in sessions:
                ma_buoi = session.get('ma_buoi_hoc')
                ngay_hoc = session.get('ngay_hoc', '')
                thoi_gian_bat_dau = session.get('thoi_gian_bat_dau', '')
                ten_mon_hoc = session.get('ten_mon_hoc', '')
                ma_lhp = session.get('ma_lhp', '')
                phong_hoc = session.get('phong_hoc', '')
                ten_giang_vien = session.get('ten_giang_vien', 'Chưa phân công')
                
                # Định dạng thời gian
                try:
                    if thoi_gian_bat_dau:
                        thoi_gian = str(thoi_gian_bat_dau)[:5]
                    else:
                        thoi_gian = "N/A"
                except:
                    thoi_gian = "N/A"
                
                # Format ngày hiển thị
                ngay_hien_thi = self.format_date_vn(ngay_hoc)
                
                # Tạo text hiển thị
                display_text = f"{ngay_hien_thi} {thoi_gian} - {ten_mon_hoc} ({ma_lhp})"
                
                # Lưu session data đầy đủ
                session_data = {
                    'ma_buoi_hoc': ma_buoi,
                    'ngay_hoc': ngay_hoc, # Giữ nguyên format gốc cho logic
                    'ngay_hien_thi': ngay_hien_thi, # Thêm ngày hiển thị
                    'thoi_gian_bat_dau': thoi_gian_bat_dau,
                    'thoi_gian_ket_thuc': session.get('thoi_gian_ket_thuc'),
                    'ten_mon_hoc': ten_mon_hoc,
                    'ma_lhp': ma_lhp,
                    'phong_hoc': phong_hoc,
                    'ten_giang_vien': ten_giang_vien,
                    'trang_thai': session.get('trang_thai', 'Chưa diễn ra')
                }
                
                self.session_combo.addItem(display_text, session_data)
            
            logger.info(f"Loaded {len(sessions)} sessions into combo")
        
        except Exception as e:
            logger.error(f"Lỗi load danh sách buổi học: {e}")
            self.session_combo.addItem("Lỗi tải buổi học", None)
    
    def on_session_changed(self):
        """Xử lý khi chọn session khác"""
        session_data = self.session_combo.currentData()
        
        if session_data:
            self.current_session_id = session_data.get('ma_buoi_hoc')
            
            # Hiển thị thông tin chi tiết session
            ngay_hoc = session_data.get('ngay_hien_thi') or self.format_date_vn(session_data.get('ngay_hoc', 'N/A'))
            thoi_gian_bat_dau = session_data.get('thoi_gian_bat_dau', 'N/A')
            thoi_gian_ket_thuc = session_data.get('thoi_gian_ket_thuc', 'N/A')
            ten_mon_hoc = session_data.get('ten_mon_hoc', 'N/A')
            ma_lhp = session_data.get('ma_lhp', 'N/A')
            phong_hoc = session_data.get('phong_hoc', 'N/A')
            ten_giang_vien = session_data.get('ten_giang_vien', 'Chưa phân công')
            trang_thai = session_data.get('trang_thai', 'N/A')
            
            session_info = f"""
            <b>Buổi học đã chọn:</b><br>
            <b>Ngày:</b> {ngay_hoc}<br>
            <b>Giờ:</b> {thoi_gian_bat_dau} - {thoi_gian_ket_thuc}<br>
            <b>Môn học:</b> {ten_mon_hoc} ({ma_lhp})<br>
            <b>Phòng:</b> {phong_hoc}<br>
            <b>Giảng viên:</b> {ten_giang_vien}<br>
            <b>Trạng thái:</b> {trang_thai}<br>
            <b>Bạn có thể điểm danh bằng mã được cung cấp.</b>
            """
            self.session_info_label.setText(session_info)
            self.session_info_label.setStyleSheet("""
                padding: 15px;
                background: #e3f2fd;
                border-left: 4px solid #2196f3;
                border-radius: 5px;
                font-size: 11pt;
            """)
        else:
            self.current_session_id = None
            self.session_info_label.setText("Vui lòng chọn buổi học để điểm danh")
            self.session_info_label.setStyleSheet("""
                padding: 15px;
                background: #f8f9fa;
                border-left: 4px solid #3498db;
                border-radius: 5px;
                font-size: 11pt;
            """)
    
    def load_schedule(self):
        """Load lịch học"""
        try:
            # Lấy lịch cho 30 ngày (hoặc có thể lấy theo tháng hiện tại của CalendarView)
            # Hiện tại lấy 30 ngày tới và 30 ngày trước để cover
            today = QDate.currentDate()
            from_date = today.addDays(-30).toString("yyyy-MM-dd")
            to_date = today.addDays(30).toString("yyyy-MM-dd")
            
            logger.info(f"Loading schedule from {from_date} to {to_date} for student {self.ma_sv}")
            
            success, sessions = self.api_helper.get_student_sessions(self.ma_sv, from_date, to_date)
            
            if not success:
                logger.error("Failed to load student sessions")
                sessions = []
            
            logger.info(f"Retrieved {len(sessions) if sessions else 0} sessions")
            
            # Format data cho CalendarView
            formatted_sessions = []
            if sessions:
                for session in sessions:
                    try:
                        # Map API data to CalendarView format
                        formatted_session = {
                            'SessionID': session.get('ma_buoi_hoc'),
                            'Date': session.get('ngay_hoc'),
                            'StartTime': str(session.get('thoi_gian_bat_dau', ''))[:5],
                            'EndTime': str(session.get('thoi_gian_ket_thuc', ''))[:5],
                            'SubjectName': session.get('ten_mon_hoc', 'N/A'),
                            'Room': session.get('phong_hoc', 'TBA'),
                            'Status': session.get('trang_thai_diem_danh', 'N/A')
                        }
                        formatted_sessions.append(formatted_session)
                    except Exception as e:
                        logger.error(f"Error formatting session: {e}")
            
            # Update CalendarView
            if hasattr(self, 'calendar_view'):
                self.calendar_view.set_sessions(formatted_sessions)
            
        except Exception as e:
            logger.error(f"Lỗi load lịch: {e}")
            import traceback
            logger.error(traceback.format_exc())
            QMessageBox.warning(self, "Lỗi", f"Không thể tải lịch học: {str(e)}")
    
    def load_detailed_warning(self):
        """Load chi tiết cảnh báo chuyên cần (Report 17)"""
        try:
            success, response = self.api_helper.get_detailed_attendance_warning(self.ma_sv)
            
            if not success or not response:
                self.warning_frame.setVisible(False)
                return
            
            co_canh_bao_do = response.get('co_canh_bao_do', False)
            co_canh_bao_vang = response.get('co_canh_bao_vang', False)
            data = response.get('data', [])
            
            if not co_canh_bao_do and not co_canh_bao_vang:
                self.warning_frame.setVisible(False)
                return
            
            if self.warning_frame.layout():
                QWidget().setLayout(self.warning_frame.layout())
            
            layout = QVBoxLayout()
            self.warning_frame.setLayout(layout)
            
            if co_canh_bao_do:
                bg_color = "#FFEBEE"
                border_color = "#f44336"
                text_color = "#c62828"
                icon = "🔴"
                title = "CẢNH BÁO NGUY CẤP"
            else:
                bg_color = "#FFF3E0"
                border_color = "#FF9800"
                text_color = "#E65100"
                icon = "🟡"
                title = "CẢNH BÁO CHUYÊN CẦN"
            
            self.warning_frame.setStyleSheet(f"""
                QFrame {{
                    background-color: {bg_color};
                    border-left: 5px solid {border_color};
                    border-radius: 5px;
                }}
            """)
            
            title_label = QLabel(f"{icon} <b>{title}</b>")
            title_label.setStyleSheet(f"color: {text_color}; font-size: 12pt;")
            layout.addWidget(title_label)
            
            for item in data:
                mon = item.get('ten_mon_hoc', '')
                thong_bao = item.get('thong_bao', '')
                muc_do = item.get('muc_do_canh_bao', 0)
                
                if muc_do == 3:
                    # Mức 3: Đỏ - Nguy cơ cấm thi
                    color = "#d32f2f"
                    icon_str = "⛔"
                else:
                    # Mức 2: Vàng - Cảnh báo
                    color = "#f57c00"
                    icon_str = "⚠️"
                    
                msg = f"{icon_str} <b>{mon}</b>: {thong_bao}"
                    
                lbl = QLabel(msg)
                lbl.setStyleSheet(f"color: {color}; margin-left: 20px;")
                layout.addWidget(lbl)
                
            self.warning_frame.setVisible(True)
            
        except Exception as e:
            logger.error(f"Lỗi load chi tiết cảnh báo: {e}")

    def attend_by_code(self):
        """Điểm danh bằng mã"""
        if not self.current_session_id:
            QMessageBox.warning(self, "Cảnh báo", "Vui lòng chọn buổi học trước khi điểm danh!")
            return
        
        code = self.code_input.text().strip().upper()
        
        if not code:
            QMessageBox.warning(self, "Lỗi", "Vui lòng nhập mã điểm danh")
            return
        
        try:
            success, response_data = self.api_client.attend_by_code(self.ma_sv, code)
            message = response_data.get('message', 'Không có phản hồi')
            
            if success:
                QMessageBox.information(self, "Thành công", "✅ " + message)
                self.code_input.clear()
                self.load_detailed_warning()
                self.load_schedule()
            else:
                QMessageBox.warning(self, "Lỗi", "❌ " + message)
            
        except Exception as e:
            logger.error(f"Lỗi điểm danh: {e}")
            QMessageBox.critical(self, "Lỗi", f"Không thể điểm danh: {str(e)}")
    
    def show_attendance_history_dialog(self):
        """Hiển thị dialog lịch sử điểm danh cá nhân"""
        try:
            dialog = QDialog(self)
            dialog.setWindowTitle("Lịch sử điểm danh cá nhân")
            dialog.setGeometry(100, 100, 1000, 600)
            
            layout = QVBoxLayout()
            
            header = QLabel("📋 Lịch sử điểm danh theo từng buổi học")
            header.setFont(QFont('Segoe UI', 12, QFont.Bold))
            layout.addWidget(header)
            
            # Loading indicator
            loading_label = QLabel("⏳ Đang tải dữ liệu...", dialog)
            loading_label.setAlignment(Qt.AlignCenter)
            loading_label.setStyleSheet("font-size: 14pt; color: #7f8c8d;")
            layout.addWidget(loading_label)
            
            table = QTableWidget()
            table.setColumnCount(6)
            table.setHorizontalHeaderLabels([
                "Ngày học", "Môn học", "Lớp", "Trạng thái", "Thời gian", "Phương thức"
            ])
            table.horizontalHeader().setStretchLastSection(True)
            table.setColumnWidth(0, 150)  # Ngày học
            table.setColumnWidth(1, 300)  # Môn học
            table.setColumnWidth(2, 150)  # Lớp
            table.setColumnWidth(3, 150)  # Trạng thái
            table.setColumnWidth(4, 150)  # Thời gian
            table.setEditTriggers(QAbstractItemView.NoEditTriggers)
            table.setAlternatingRowColors(True)
            table.setVisible(False) # Hide initially
            
            layout.addWidget(table)
            
            btn_layout = QHBoxLayout()
            export_btn = QPushButton("📥 Xuất Excel")
            export_btn.setStyleSheet("""
                QPushButton {
                    background-color: #27ae60;
                    color: white;
                    padding: 10px 20px;
                    border: none;
                    border-radius: 3px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #219150;
                }
            """)
            
            close_btn = QPushButton("Đóng")
            close_btn.setStyleSheet("""
                QPushButton {
                    background-color: #95a5a6;
                    color: white;
                    padding: 10px 20px;
                    border: none;
                    border-radius: 3px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #7f8c8d;
                }
            """)
            close_btn.clicked.connect(dialog.close)
            
            btn_layout.addWidget(export_btn)
            btn_layout.addStretch()
            btn_layout.addWidget(close_btn)
            layout.addLayout(btn_layout)
            
            dialog.setLayout(layout)
            
            # Callback function for worker
            def on_history_loaded(success, history_data):
                loading_label.setVisible(False)
                
                if not success or not history_data:
                    QMessageBox.warning(dialog, "Thông báo", "Không có dữ liệu lịch sử điểm danh")
                    return
                
                table.setVisible(True)
                table.setRowCount(len(history_data))
                
                for i, record in enumerate(history_data):
                    ngay_hoc = self.format_date_vn(record.get('ngay_hoc', ''))
                    table.setItem(i, 0, QTableWidgetItem(ngay_hoc))
                    table.setItem(i, 1, QTableWidgetItem(record.get('ten_mon_hoc', 'N/A')))
                    table.setItem(i, 2, QTableWidgetItem(record.get('ma_lop_hoc_phan', 'N/A')))
                    
                    status = record.get('trang_thai_diem_danh', 'N/A')
                    status_item = QTableWidgetItem(status)
                    
                    if status == 'Có mặt':
                        status_item.setBackground(QColor('#E8F5E9'))
                        status_item.setForeground(QColor('#2E7D32'))
                    elif 'Vắng' in status:
                        status_item.setBackground(QColor('#FFEBEE'))
                        status_item.setForeground(QColor('#C62828'))
                    elif status == 'Muộn':
                        status_item.setBackground(QColor('#FFF3E0'))
                        status_item.setForeground(QColor('#E65100'))
                    
                    table.setItem(i, 3, status_item)
                    table.setItem(i, 4, QTableWidgetItem(record.get('thoi_gian_diem_danh', '')))
                    table.setItem(i, 5, QTableWidgetItem(record.get('phuong_thuc', '')))
            
            # Start worker
            self.history_worker = ReportWorker(self.api_helper.get_attendance_history, self.ma_sv)
            self.history_worker.finished.connect(on_history_loaded)
            self.history_worker.start()
            
            dialog.exec_()
            
        except Exception as e:
            logger.error(f"Lỗi hiển thị lịch sử: {e}")
            QMessageBox.critical(self, "Lỗi", f"Không thể tải lịch sử điểm danh: {str(e)}")

    def show_attendance_stats_dialog(self):
        """Hiển thị dialog thống kê chuyên cần theo học kỳ"""
        try:
            dialog = QDialog(self)
            dialog.setWindowTitle("Thống kê chuyên cần")
            dialog.setGeometry(100, 100, 1000, 600)
            
            layout = QVBoxLayout()
            
            header = QLabel("📊 Thống kê tỷ lệ chuyên cần (%) trong học kỳ")
            header.setFont(QFont('Segoe UI', 12, QFont.Bold))
            layout.addWidget(header)
            
            # Loading indicator
            loading_label = QLabel("⏳ Đang tải dữ liệu...", dialog)
            loading_label.setAlignment(Qt.AlignCenter)
            loading_label.setStyleSheet("font-size: 14pt; color: #7f8c8d;")
            layout.addWidget(loading_label)
            
            table = QTableWidget()
            table.setColumnCount(8)
            table.setHorizontalHeaderLabels([
                "Môn học", "Lớp", "Học kỳ", "Năm", "Tổng buổi", "Có mặt", "Vắng", "Tỉ lệ %"
            ])
            table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch) # Môn học
            table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents) # Lớp
            table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents) # Học kỳ
            table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents) # Năm
            table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeToContents) # Tổng buổi
            table.horizontalHeader().setSectionResizeMode(5, QHeaderView.ResizeToContents) # Có mặt
            table.horizontalHeader().setSectionResizeMode(6, QHeaderView.ResizeToContents) # Vắng
            table.horizontalHeader().setSectionResizeMode(7, QHeaderView.ResizeToContents) # Tỉ lệ
            table.setEditTriggers(QAbstractItemView.NoEditTriggers)
            table.setAlternatingRowColors(True)
            table.setVisible(False) # Hide initially
            
            layout.addWidget(table)
            
            close_btn = QPushButton("Đóng")
            close_btn.clicked.connect(dialog.close)
            layout.addWidget(close_btn, 0, Qt.AlignRight)
            
            dialog.setLayout(layout)
            
            # Callback function
            def on_stats_loaded(success, stats_data):
                loading_label.setVisible(False)
                
                if not success or not stats_data:
                    QMessageBox.warning(dialog, "Thông báo", "Không có dữ liệu thống kê")
                    return
                
                table.setVisible(True)
                table.setRowCount(len(stats_data))
                
                for i, stat in enumerate(stats_data):
                    table.setItem(i, 0, QTableWidgetItem(stat.get('ten_mon_hoc', 'N/A')))
                    table.setItem(i, 1, QTableWidgetItem(stat.get('ma_lop_hoc_phan', 'N/A')))
                    table.setItem(i, 2, QTableWidgetItem(str(stat.get('hoc_ky', ''))))
                    table.setItem(i, 3, QTableWidgetItem(str(stat.get('nam_hoc', ''))))
                    table.setItem(i, 4, QTableWidgetItem(str(stat.get('tong_buoi_hoc', 0))))
                    table.setItem(i, 5, QTableWidgetItem(str(stat.get('so_buoi_co_mat', 0))))
                    table.setItem(i, 6, QTableWidgetItem(str(stat.get('so_buoi_vang', 0))))
                    
                    percentage = f"{stat.get('ty_le_chuyen_can', 0):.1f}%"
                    perc_item = QTableWidgetItem(percentage)
                    
                    # Color coding based on percentage
                    val = stat.get('ty_le_chuyen_can', 0)
                    if val < 80:
                        perc_item.setForeground(QColor('red'))
                        perc_item.setFont(QFont('Segoe UI', 9, QFont.Bold))
                    elif val < 90:
                        perc_item.setForeground(QColor('#f57c00')) # Orange
                    else:
                        perc_item.setForeground(QColor('green'))
                        
                    table.setItem(i, 7, perc_item)
            
            # Start worker
            self.stats_worker = ReportWorker(self.api_helper.get_attendance_stats, self.ma_sv)
            self.stats_worker.finished.connect(on_stats_loaded)
            self.stats_worker.start()
            
            dialog.exec_()
            
        except Exception as e:
            logger.error(f"Lỗi hiển thị thống kê: {e}")
            QMessageBox.critical(self, "Lỗi", f"Không thể tải thống kê: {str(e)}")


    def show_personal_info(self):
        """Hiển thị thông tin cá nhân"""
        dialog = PersonalInfoDialog(self, self.user_data)
        dialog.exec_()
