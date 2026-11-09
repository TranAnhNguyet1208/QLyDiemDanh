from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from datetime import datetime, timedelta

class CalendarView(QWidget):
    """Widget hiển thị lịch dạng tuần với timeline"""
    
    session_clicked = pyqtSignal(dict)  # Signal khi click vào buổi học
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_date = QDate.currentDate()
        self.sessions = []
        self.container = None
        self.start_of_week = None
        self.session_widgets = []
        self.init_ui()
    
    def init_ui(self):
        """Khởi tạo giao diện"""
        layout = QVBoxLayout()
        layout.setSpacing(10)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Header với tháng/năm và navigation
        header = self.create_header()
        layout.addWidget(header)
        
        self.calendar_widget = QWidget()
        self.calendar_layout = QVBoxLayout()
        self.calendar_layout.setSpacing(0)
        self.calendar_widget.setLayout(self.calendar_layout)
        
        scroll = QScrollArea()
        scroll.setWidget(self.calendar_widget)
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        
        layout.addWidget(scroll)
        self.setLayout(layout)
        
        self.render_calendar()
    
    def create_header(self):
        """Tạo header với navigation"""
        header_widget = QWidget()
        header_widget.setStyleSheet("""
            QWidget {
                background-color: #f5f5f5;
                color: #333;
                padding: 10px;
            }
            QPushButton {
                background-color: white;
                color: #333;
                border: 1px solid #ccc;
                border-radius: 3px;
                padding: 8px 15px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #e0e0e0;
            }
        """)
        
        layout = QHBoxLayout(header_widget)
        
        prev_btn = QPushButton("◀ Tuần trước")
        prev_btn.clicked.connect(self.previous_week)
        
        today_btn = QPushButton("📅 Hôm nay")
        today_btn.clicked.connect(self.go_to_today)
        
        next_btn = QPushButton("Tuần sau ▶")
        next_btn.clicked.connect(self.next_week)
        
        self.month_label = QLabel()
        self.month_label.setStyleSheet("font-size: 14pt; font-weight: bold; border: none;")
        self.month_label.setAlignment(Qt.AlignCenter)
        
        layout.addWidget(prev_btn)
        layout.addWidget(today_btn)
        layout.addWidget(next_btn)
        layout.addStretch()
        layout.addWidget(self.month_label)
        layout.addStretch()
        
        return header_widget

    def update_header(self):
        """Cập nhật header với tháng/năm hiện tại"""
        month_names = [
            "", "Tháng 1", "Tháng 2", "Tháng 3", "Tháng 4", "Tháng 5", "Tháng 6",
            "Tháng 7", "Tháng 8", "Tháng 9", "Tháng 10", "Tháng 11", "Tháng 12"
        ]
        month = month_names[self.current_date.month()]
        year = self.current_date.year()
        
        start_of_week = self.current_date.addDays(-self.current_date.dayOfWeek() + 1)
        end_of_week = start_of_week.addDays(6)
        
        self.month_label.setText(
            f"{month} {year} - Tuần {start_of_week.toString('dd/MM')} đến {end_of_week.toString('dd/MM')}"
        )
    
    def render_calendar(self):
        """Render lịch tuần với grid lines chính xác"""
        while self.calendar_layout.count():
            child = self.calendar_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        
        self.update_header()
        
        start_of_week = self.current_date.addDays(-self.current_date.dayOfWeek() + 1)
        self.start_of_week = start_of_week
        
        container = QWidget()
        self.container = container
        container.installEventFilter(self)
        
        container_layout = QHBoxLayout()
        container_layout.setSpacing(0)
        container_layout.setContentsMargins(0, 0, 0, 0)
        container.setLayout(container_layout)
        
        # Cột thời gian
        time_widget = QWidget()
        time_widget.setFixedWidth(80)
        time_widget.setStyleSheet("background-color: #f5f5f5; border-right: 1px solid #ddd;")
        time_layout = QVBoxLayout()
        time_layout.setSpacing(0)
        time_layout.setContentsMargins(0, 0, 0, 0)
        
        time_header = QLabel("GMT+7")
        time_header.setAlignment(Qt.AlignCenter)
        time_header.setFixedHeight(60)
        time_header.setStyleSheet("""
            background-color: #e0e0e0;
            border: 1px solid #ccc;
            font-weight: bold;
            font-size: 10pt;
        """)
        time_layout.addWidget(time_header)
        
        for hour in range(7, 13): # 7h đến 12h
            lbl = QLabel(f"{hour}:00")
            lbl.setAlignment(Qt.AlignTop | Qt.AlignHCenter)
            lbl.setFixedHeight(80) # 80px per hour
            lbl.setStyleSheet("""
                background-color: #f9f9f9;
                border-top: 1px solid #eee;
                font-size: 9pt;
                padding-top: 5px;
            """)
            time_layout.addWidget(lbl)
            
        time_layout.addStretch()
        time_widget.setLayout(time_layout)
        container_layout.addWidget(time_widget)
        
        # Các cột ngày
        day_names = ["Thứ 2", "Thứ 3", "Thứ 4", "Thứ 5", "Thứ 6", "Thứ 7", "Chủ nhật"]
        today = QDate.currentDate()
        
        for i in range(7):
            day_date = start_of_week.addDays(i)
            is_today = day_date == today
            
            day_column = QWidget()
            day_layout = QVBoxLayout()
            day_layout.setSpacing(0)
            day_layout.setContentsMargins(0, 0, 0, 0)
            day_column.setLayout(day_layout)
            
            # Header ngày
            header_text = f"{day_names[i]}\n{day_date.toString('dd/MM')}"
            header_lbl = QLabel(header_text)
            header_lbl.setAlignment(Qt.AlignCenter)
            header_lbl.setFixedHeight(60)
            
            if is_today:
                header_lbl.setStyleSheet("""
                    background-color: #2196F3;
                    color: white;
                    border: 1px solid #1976D2;
                    font-weight: bold;
                    font-size: 10pt;
                """)
            else:
                header_lbl.setStyleSheet("""
                    background-color: #e0e0e0;
                    border: 1px solid #ccc;
                    font-weight: bold;
                    font-size: 10pt;
                """)
            
            day_layout.addWidget(header_lbl)
            
            # Grid area cho các buổi học
            grid_area = QWidget()
            grid_area.setStyleSheet("""
                background-color: white;
                border: 1px solid #eee;
                border-top: none;
            """)
            # Grid area height = (13 - 7) * 80 = 6 * 80 = 480px
            grid_area.setFixedHeight(480) 
            
            day_layout.addWidget(grid_area)
            day_layout.addStretch()
            
            container_layout.addWidget(day_column)
            
        self.calendar_layout.addWidget(container)
        
        # Sau khi render xong khung, overlay các buổi học
        QTimer.singleShot(100, lambda: self.overlay_sessions(container, start_of_week))

    def overlay_sessions(self, container, start_of_week):
        """Overlay sessions với absolute positioning chính xác theo thời gian"""
        # Check if container is stale (replaced by a newer one)
        if container is not self.container:
            return

        try:
            if not container.layout():
                return
        except RuntimeError:
            # Container might be deleted
            return

        for item in self.session_widgets:
            try:
                if isinstance(item, dict):
                    if item.get('widget'):
                        item['widget'].deleteLater()
                else:
                    item.deleteLater()
            except RuntimeError:
                pass
            except Exception:
                pass
        self.session_widgets.clear()
        
        for session in self.sessions:
            try:
                session_date_str = session.get('Date', '') or session.get('SessionDate', '')
                if not session_date_str:
                    continue
                    
                if isinstance(session_date_str, str):
                    session_date = QDate.fromString(session_date_str, "yyyy-MM-dd")
                else:
                    session_date = session_date_str
                
                if not session_date.isValid():
                    continue
                
                if session_date < start_of_week or session_date > start_of_week.addDays(6):
                    continue
                
                day_of_week = session_date.dayOfWeek() - 1
                
                start_time_str = str(session.get('StartTime', ''))
                end_time_str = str(session.get('EndTime', ''))
                
                if ':' not in start_time_str or ':' not in end_time_str:
                    continue
                
                start_parts = start_time_str.split(':')
                end_parts = end_time_str.split(':')
                
                start_hour = int(start_parts[0])
                start_min = int(start_parts[1])
                end_hour = int(end_parts[0])
                end_min = int(end_parts[1])
                
                start_minutes_from_7am = (start_hour - 7) * 60 + start_min
                end_minutes_from_7am = (end_hour - 7) * 60 + end_min
                
                if start_minutes_from_7am < 0:
                    print(f"Skipping session starting before 7:00: {start_hour}:{start_min}")
                    continue
                
                if end_minutes_from_7am > 12 * 60: 
                    pass

                # Scale: 80px per hour => 80/60 px per minute
                top_position = int(start_minutes_from_7am * 80.0 / 60.0)
                duration_minutes = end_minutes_from_7am - start_minutes_from_7am
                height = int(duration_minutes * 80.0 / 60.0)
                
                # Tìm cột ngày tương ứng
                # container layout items: 0 is time_widget, 1..7 are day columns
                day_column = container.layout().itemAt(day_of_week + 1).widget()
                if not day_column:
                    continue
                    
                # Grid area là item thứ 2 trong day_column layout (index 1)
                grid_area = day_column.layout().itemAt(1).widget()
                if not grid_area:
                    continue
                
                session_widget = self.create_session_widget(session)
                session_widget.setParent(grid_area)
                
                self.session_widgets.append({
                    'widget': session_widget,
                    'grid_area': grid_area,
                    'top': top_position,
                    'height': height
                })
                
                left_margin = 6
                right_margin = 6
                top_margin = 3
                bottom_margin = 3
                
                widget_width = max(80, grid_area.width() - left_margin - right_margin)
                widget_height = max(20, height - top_margin - bottom_margin)
                
                session_widget.setGeometry(
                    left_margin, 
                    top_position + top_margin, 
                    widget_width, 
                    widget_height
                )
                session_widget.show()
                
            except Exception as e:
                import traceback
                print(f"Lỗi overlay session: {e}")
                print(traceback.format_exc())
                continue
    
    def create_session_widget(self, session):
        """Tạo widget hiển thị buổi học"""
        status = session.get('Status') or session.get('AttendanceStatus') or 'Chưa điểm danh'
        status = str(status).strip() if status else 'Chưa điểm danh'
        
        if 'Có mặt' in status or status == 'Có mặt':
            bg_color = "#E8F5E9"
            border_color = "#4CAF50"
            status_color = "#2E7D32"
        elif 'Vắng có phép' in status:
            bg_color = "#FFF3E0"
            border_color = "#FF9800"
            status_color = "#E65100"
        elif 'Vắng' in status or 'không phép' in status:
            bg_color = "#FFEBEE"
            border_color = "#f44336"
            status_color = "#C62828"
        else:
            bg_color = "#E3F2FD"
            border_color = "#2196F3"
            status_color = "#1976D2"
        
        widget = QFrame()
        widget.setFrameShape(QFrame.StyledPanel)
        widget.setStyleSheet(f"""
            QFrame {{
                background-color: {bg_color};
                border-left: 5px solid {border_color};
                border-radius: 4px;
                padding: 4px;
            }}
            QFrame:hover {{
                background-color: {border_color}33;
                border: 1px solid {border_color};
            }}
        """)
        
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(2, 2, 2, 2)
        layout.setSpacing(2)
        
        subject_label = QLabel(session.get('SubjectName', ''))
        subject_label.setStyleSheet("font-weight: bold; font-size: 9pt; border: none; background: transparent;")
        subject_label.setWordWrap(True)
        layout.addWidget(subject_label)
        
        time_str = f"{session.get('StartTime')} - {session.get('EndTime')}"
        time_label = QLabel(time_str)
        time_label.setStyleSheet("font-size: 8pt; color: #555; border: none; background: transparent;")
        layout.addWidget(time_label)
        
        room_label = QLabel(f"Phòng: {session.get('Room', '')}")
        room_label.setStyleSheet("font-size: 8pt; color: #555; border: none; background: transparent;")
        layout.addWidget(room_label)
        
        status_label = QLabel(status)
        status_label.setStyleSheet(f"font-size: 8pt; font-weight: bold; color: {status_color}; border: none; background: transparent;")
        layout.addWidget(status_label)
        
        layout.addStretch()
        
        # Click event
        widget.mousePressEvent = lambda event: self.session_clicked.emit(session)
        
        return widget

    def set_sessions(self, sessions):
        """Đặt danh sách buổi học"""
        seen = set()
        unique_sessions = []
        for s in sessions:
            session_id = s.get('SessionID')
            if session_id not in seen:
                seen.add(session_id)
                unique_sessions.append(s)
        
        self.sessions = unique_sessions
        
        if self.container and self.start_of_week:
            self.refresh()
        else:
            self.render_calendar()
    
    def previous_week(self):
        """Tuần trước"""
        self.current_date = self.current_date.addDays(-7)
        self.render_calendar()
    
    def next_week(self):
        """Tuần sau"""
        self.current_date = self.current_date.addDays(7)
        self.render_calendar()
    
    def go_to_today(self):
        """Về hôm nay"""
        self.current_date = QDate.currentDate()
        self.render_calendar()
    
    def eventFilter(self, obj, event):
        if obj == self.container and event.type() == event.Resize:
            if self.container and self.start_of_week and len(self.session_widgets) > 0:
                QTimer.singleShot(50, self._reposition_widgets)
        return super().eventFilter(obj, event)
    
    def _reposition_widgets(self):
        for item in self.session_widgets:
            if isinstance(item, dict):
                try:
                    widget = item['widget']
                    grid_area = item['grid_area']
                    
                    # Check if C++ objects are still valid
                    if not widget or not grid_area:
                        continue
                        
                    top = item['top']
                    height = item['height']
                    
                    left_margin = 6
                    right_margin = 6
                    top_margin = 3
                    bottom_margin = 3
                    
                    widget_width = max(80, grid_area.width() - left_margin - right_margin)
                    widget_height = max(20, height - top_margin - bottom_margin)
                    
                    widget.setGeometry(
                        left_margin,
                        top + top_margin,
                        widget_width,
                        widget_height
                    )
                except RuntimeError:
                    # Widget might be deleted
                    continue
                except Exception as e:
                    continue
    
    def refresh(self):
        if self.container and self.start_of_week:
            self.overlay_sessions(self.container, self.start_of_week)
