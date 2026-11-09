from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import openpyxl
from openpyxl.styles import Font, PatternFill
from openpyxl.utils import get_column_letter
import io
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Qt5Agg')
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure


class TeacherReportDialog(QDialog):
    
    def __init__(self, parent=None, title="Báo cáo", data=None, class_name=""):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setMinimumSize(1600, 800)
        self.setWindowState(Qt.WindowMaximized)
        self.data = data or {}
        self.class_name = class_name
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout(self)
        self.main_widget = QWidget()
        self.main_layout = QVBoxLayout(self.main_widget)
        layout.addWidget(self.main_widget)
        
        button_layout = QHBoxLayout()
        export_btn = QPushButton("📥 Xuất Excel")
        export_btn.clicked.connect(self.export_to_excel)
        close_btn = QPushButton("Đóng")
        close_btn.clicked.connect(self.accept)
        
        button_layout.addWidget(export_btn)
        button_layout.addStretch()
        button_layout.addWidget(close_btn)
        layout.addLayout(button_layout)
    
    def create_table(self, data_list, column_names=None, keys=None):
        table = QTableWidget()
        
        if not data_list:
            table.setColumnCount(1)
            table.setRowCount(1)
            table.setItem(0, 0, QTableWidgetItem("Không có dữ liệu"))
            return table
        
        if column_names is None:
            column_names = list(data_list[0].keys())
            
        if keys is None:
            keys = column_names
        
        table.setColumnCount(len(column_names))
        table.setHorizontalHeaderLabels(column_names)
        table.setRowCount(len(data_list))
        
        header = table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)
        
        for row_idx, row_data in enumerate(data_list):
            for col_idx, key in enumerate(keys):
                value = row_data.get(key, '')
                if isinstance(value, float):
                    item = QTableWidgetItem(f"{value:.2f}")
                else:
                    item = QTableWidgetItem(str(value) if value is not None else "")
                item.setFlags(item.flags() & ~Qt.ItemIsEditable)
                table.setItem(row_idx, col_idx, item)
        
        return table
    
    def export_to_excel(self):
        pass


class TeacherReport1Dialog(TeacherReportDialog):
    """Thống kê tỷ lệ chuyên cần của từng sinh viên trong lớp"""
    
    def __init__(self, parent=None, data=None, class_name=""):
        super().__init__(parent, "Tỷ lệ chuyên cần từng sinh viên", data, class_name)
    
    def init_ui(self):
        super().init_ui()
        
        if self.data and isinstance(self.data, list) and len(self.data) > 0:
            column_names = ["Mã SV", "Họ tên", "Tổng buổi", "Có mặt", "Vắng", "Tỷ lệ (%)"]
            keys = ["ma_sinh_vien", "ho_ten", "tong_buoi_hoc", "so_buoi_co_mat", "so_buoi_vang", "ty_le_chuyen_can"]
            table = self.create_table(self.data, column_names, keys)
            self.main_layout.addWidget(table)
    
    def export_to_excel(self):
        if not self.data:
            QMessageBox.warning(self, "Cảnh báo", "Không có dữ liệu để xuất")
            return
        
        file_path, _ = QFileDialog.getSaveFileName(self, "Lưu file", "", "Excel Files (*.xlsx)")
        if not file_path:
            return
        
        try:
            wb = openpyxl.Workbook()
            ws = wb.active
            ws.title = "Chuyên cần SV"
            
            headers = ["Mã SV", "Họ tên", "Tổng buổi học", "Có mặt", "Vắng", "Tỷ lệ chuyên cần (%)"]
            ws.append(headers)
            
            for cell in ws[1]:
                cell.font = Font(bold=True, color="FFFFFF")
                cell.fill = PatternFill(start_color="366092", end_color="366092", fill_type="solid")
            
            for row in self.data:
                ws.append([
                    row.get("ma_sinh_vien", ""),
                    row.get("ho_ten", ""),
                    row.get("tong_buoi_hoc", ""),
                    row.get("so_buoi_co_mat", ""),
                    row.get("so_buoi_vang", ""),
                    round(row.get("ty_le_chuyen_can", 0), 2)
                ])
            
            for col in ws.columns:
                ws.column_dimensions[get_column_letter(col[0].column)].width = 18
            
            wb.save(file_path)
            QMessageBox.information(self, "Thành công", "Đã xuất báo cáo thành công!")
        except Exception as e:
            QMessageBox.critical(self, "Lỗi", f"Không thể xuất báo cáo: {str(e)}")


class TeacherReport2Dialog(TeacherReportDialog):
    """Danh sách sinh viên có mặt, vắng mặt trong từng buổi học"""
    
    def __init__(self, parent=None, data=None, class_name=""):
        super().__init__(parent, "Danh sách điểm danh theo buổi học", data, class_name)
        self.setMinimumSize(1700, 800)
    
    def init_ui(self):
        super().init_ui()
        
        if self.data and isinstance(self.data, list) and len(self.data) > 0:
            column_names = ["Buổi học", "Ngày", "Phòng", "Mã SV", "Họ tên", "Trạng thái", "Thời gian", "Phương thức"]
            keys = ["ma_buoi_hoc", "ngay_hoc", "phong_hoc", "ma_sinh_vien", "ho_ten", "trang_thai_diem_danh", "thoi_gian_diem_danh", "phuong_thuc"]
            table = self.create_table(self.data, column_names, keys)
            self.main_layout.addWidget(table)
    
    def export_to_excel(self):
        if not self.data:
            QMessageBox.warning(self, "Cảnh báo", "Không có dữ liệu để xuất")
            return
        
        file_path, _ = QFileDialog.getSaveFileName(self, "Lưu file", "", "Excel Files (*.xlsx)")
        if not file_path:
            return
        
        try:
            wb = openpyxl.Workbook()
            ws = wb.active
            ws.title = "DS Điểm danh"
            
            headers = ["Buổi học", "Ngày", "Phòng", "Mã SV", "Họ tên", "Trạng thái", "Thời gian", "Phương thức"]
            ws.append(headers)
            
            for cell in ws[1]:
                cell.font = Font(bold=True, color="FFFFFF")
                cell.fill = PatternFill(start_color="4472C4", end_color="4472C4", fill_type="solid")
            
            for row in self.data:
                ws.append([
                    row.get("ma_buoi_hoc", ""),
                    row.get("ngay_hoc", ""),
                    row.get("phong_hoc", ""),
                    row.get("ma_sinh_vien", ""),
                    row.get("ho_ten", ""),
                    row.get("trang_thai_diem_danh", ""),
                    row.get("thoi_gian_diem_danh", ""),
                    row.get("phuong_thuc", "")
                ])
            
            for col in ws.columns:
                ws.column_dimensions[get_column_letter(col[0].column)].width = 15
            
            wb.save(file_path)
            QMessageBox.information(self, "Thành công", "Đã xuất báo cáo thành công!")
        except Exception as e:
            QMessageBox.critical(self, "Lỗi", f"Không thể xuất báo cáo: {str(e)}")


class TeacherReport3Dialog(TeacherReportDialog):
    """Biểu đồ xu hướng chuyên cần theo tuần/tháng"""
    
    def __init__(self, parent=None, data=None, class_name=""):
        super().__init__(parent, "Xu hướng chuyên cần theo tuần", data, class_name)
        self.setMinimumSize(1400, 800)
        self.raw_data = []
    
    def init_ui(self):
        super().init_ui()
        
        if self.data and isinstance(self.data, dict) and self.data.get('labels'):
            self.create_trend_chart()
    
    def create_trend_chart(self):
        labels = self.data.get('labels', [])
        datasets = self.data.get('datasets', [])
        
        ty_le_data = []
        co_mat_data = []
        
        for dataset in datasets:
            if dataset.get('label') == 'Ty le chuyen can (%)':
                ty_le_data = dataset.get('data', [])
            elif dataset.get('label') == 'So luot co mat':
                co_mat_data = dataset.get('data', [])
        
        fig = Figure(figsize=(12, 6), dpi=100)
        ax1 = fig.add_subplot(111)
        
        color_line = '#2196F3'
        color_bar = '#4CAF50'
        
        # Line chart (Tỷ lệ)
        ax1.plot(range(len(labels)), ty_le_data, marker='o', linewidth=2.5, markersize=8, 
                 color=color_line, label='Tỷ lệ chuyên cần (%)')
        
        ax1.set_xlabel('Thời gian', fontsize=14, weight='bold', labelpad=10)
        ax1.set_ylabel('Tỷ lệ chuyên cần (%)', fontsize=14, weight='bold', color=color_line, labelpad=10)
        ax1.tick_params(axis='y', labelcolor=color_line, labelsize=12)
        ax1.tick_params(axis='x', labelsize=12)
        ax1.grid(True, alpha=0.3)
        ax1.set_ylim(0, 105)
        
        ax1.set_xticks(range(len(labels)))
        ax1.set_xticklabels(labels, rotation=45, ha='right', fontsize=11)
        
        # Bar chart (Số lượt có mặt)
        ax2 = ax1.twinx()
        bars = ax2.bar(range(len(labels)), co_mat_data, alpha=0.3, color=color_bar, 
                      label='Số lượt có mặt', width=0.6)
        
        ax2.set_ylabel('Số lượt có mặt', fontsize=14, weight='bold', color=color_bar, labelpad=10)
        ax2.tick_params(axis='y', labelcolor=color_bar, labelsize=12)
        
        fig.suptitle(f'Xu hướng chuyên cần - {self.class_name}', fontsize=18, weight='bold', y=0.98)
        
        lines, labels1 = ax1.get_legend_handles_labels()
        bars, labels2 = ax2.get_legend_handles_labels()
        ax1.legend(lines + bars, labels1 + labels2, loc='upper left', fontsize=12, frameon=True, shadow=True)
        
        fig.tight_layout()
        
        canvas = FigureCanvas(fig)
        self.main_layout.addWidget(canvas)
    
    def export_to_excel(self):
        if not self.data:
            QMessageBox.warning(self, "Cảnh báo", "Không có dữ liệu để xuất")
            return
        
        file_path, _ = QFileDialog.getSaveFileName(self, "Lưu file", "", "Excel Files (*.xlsx)")
        if not file_path:
            return
        
        try:
            wb = openpyxl.Workbook()
            ws = wb.active
            ws.title = "Xu hướng"
            
            headers = ["Tuần/Tháng", "Tỷ lệ (%)"]
            ws.append(headers)
            
            for cell in ws[1]:
                cell.font = Font(bold=True, color="FFFFFF")
                cell.fill = PatternFill(start_color="70AD47", end_color="70AD47", fill_type="solid")
            
            labels = self.data.get('labels', [])
            datasets = self.data.get('datasets', [])
            
            ty_le_data = []
            for dataset in datasets:
                if dataset.get('label') == 'Ty le chuyen can (%)':
                    ty_le_data = dataset.get('data', [])
                    break
            
            for i, label in enumerate(labels):
                ty_le = ty_le_data[i] if i < len(ty_le_data) else 0
                ws.append([label, round(ty_le, 2)])
            
            for col in ws.columns:
                ws.column_dimensions[get_column_letter(col[0].column)].width = 20
            
            wb.save(file_path)
            QMessageBox.information(self, "Thành công", "Đã xuất báo cáo thành công!")
        except Exception as e:
            QMessageBox.critical(self, "Lỗi", f"Không thể xuất báo cáo: {str(e)}")


class TeacherReport4Dialog(TeacherReportDialog):
    """Sinh viên có tỷ lệ cao nhất/thấp nhất"""
    
    def __init__(self, parent=None, data=None, class_name="", loai="cao"):
        super().__init__(parent, f"Sinh viên chuyên cần {'cao nhất' if loai == 'cao' else 'thấp nhất'}", data, class_name)
        self.loai = loai
    
    def init_ui(self):
        super().init_ui()
        
        if self.data and isinstance(self.data, list) and len(self.data) > 0:
            column_names = ["Xếp hạng", "Mã SV", "Họ tên", "Tổng buổi", "Có mặt", "Vắng", "Tỷ lệ (%)"]
            keys = ["xep_hang", "ma_sinh_vien", "ho_ten", "tong_buoi_hoc", "so_buoi_co_mat", "so_buoi_vang", "ty_le_chuyen_can"]
            table = self.create_table(self.data, column_names, keys)
            self.main_layout.addWidget(table)
    
    def export_to_excel(self):
        if not self.data:
            QMessageBox.warning(self, "Cảnh báo", "Không có dữ liệu để xuất")
            return
        
        file_path, _ = QFileDialog.getSaveFileName(self, "Lưu file", "", "Excel Files (*.xlsx)")
        if not file_path:
            return
        
        try:
            wb = openpyxl.Workbook()
            ws = wb.active
            
            title = "SV Chuyên cần cao nhất" if self.loai == "cao" else "SV Chuyên cần thấp nhất"
            ws.title = title
            ws.append([title])
            ws.append([])
            
            headers = ["Xếp hạng", "Mã SV", "Họ tên", "Tổng buổi", "Có mặt", "Vắng", "Tỷ lệ (%)"]
            ws.append(headers)
            
            for cell in ws[3]:
                cell.font = Font(bold=True, color="FFFFFF")
                cell.fill = PatternFill(start_color="FF6B6B", end_color="FF6B6B", fill_type="solid")
            
            for row in self.data:
                ws.append([
                    row.get("xep_hang", ""),
                    row.get("ma_sinh_vien", ""),
                    row.get("ho_ten", ""),
                    row.get("tong_buoi_hoc", ""),
                    row.get("so_buoi_co_mat", ""),
                    row.get("so_buoi_vang", ""),
                    round(row.get("ty_le_chuyen_can", 0), 2)
                ])
            
            for col in ws.columns:
                ws.column_dimensions[get_column_letter(col[0].column)].width = 15
            
            wb.save(file_path)
            QMessageBox.information(self, "Thành công", "Đã xuất báo cáo thành công!")
        except Exception as e:
            QMessageBox.critical(self, "Lỗi", f"Không thể xuất báo cáo: {str(e)}")


class TeacherReport5Dialog(TeacherReportDialog):
    """Báo cáo tổng hợp chuyên cần của các lớp do giảng viên phụ trách"""
    
    def __init__(self, parent=None, data=None, teacher_name=""):
        super().__init__(parent, f"Báo cáo tổng hợp chuyên cần - GV: {teacher_name}", data, teacher_name)
    
    def init_ui(self):
        super().init_ui()
        
        if self.data and isinstance(self.data, list) and len(self.data) > 0:
            column_names = ["Lớp HP", "Môn học", "Học kỳ", "Năm", "Tổng SV", "Buổi học", "Lượt DD", "Có mặt", "Tỷ lệ (%)"]
            keys = ["ma_lop_hoc_phan", "ten_mon_hoc", "hoc_ky", "nam_hoc", "tong_sinh_vien", "tong_buoi_hoc", "tong_luot_diem_danh", "tong_luot_co_mat", "ty_le_chuyen_can"]
            table = self.create_table(self.data, column_names, keys)
            self.main_layout.addWidget(table)
    
    def export_to_excel(self):
        if not self.data:
            QMessageBox.warning(self, "Cảnh báo", "Không có dữ liệu để xuất")
            return
        
        file_path, _ = QFileDialog.getSaveFileName(self, "Lưu file", "", "Excel Files (*.xlsx)")
        if not file_path:
            return
        
        try:
            wb = openpyxl.Workbook()
            ws = wb.active
            ws.title = "Tổng hợp"
            
            headers = ["Lớp HP", "Môn học", "Học kỳ", "Năm", "Tổng SV", "Buổi học", "Lượt DD", "Có mặt", "Tỷ lệ (%)"]
            ws.append(headers)
            
            for cell in ws[1]:
                cell.font = Font(bold=True, color="FFFFFF")
                cell.fill = PatternFill(start_color="1F4788", end_color="1F4788", fill_type="solid")
            
            for row in self.data:
                ws.append([
                    row.get("ma_lop_hoc_phan", ""),
                    row.get("ten_mon_hoc", ""),
                    row.get("hoc_ky", ""),
                    row.get("nam_hoc", ""),
                    row.get("tong_sinh_vien", ""),
                    row.get("tong_buoi_hoc", ""),
                    row.get("tong_luot_diem_danh", ""),
                    row.get("tong_luot_co_mat", ""),
                    round(row.get("ty_le_chuyen_can", 0), 2)
                ])
            
            for col in ws.columns:
                ws.column_dimensions[get_column_letter(col[0].column)].width = 16
            
            wb.save(file_path)
            QMessageBox.information(self, "Thành công", "Đã xuất báo cáo thành công!")
        except Exception as e:
            QMessageBox.critical(self, "Lỗi", f"Không thể xuất báo cáo: {str(e)}")


class TeacherReport6Dialog(TeacherReportDialog):
    """Cảnh báo sinh viên có nguy cơ bị cấm thi"""
    
    def __init__(self, parent=None, data=None, class_name=""):
        super().__init__(parent, "Cảnh báo sinh viên có nguy cơ cấm thi", data, class_name)
    
    def init_ui(self):
        super().init_ui()
        
        if self.data and isinstance(self.data, list) and len(self.data) > 0:
            column_names = ["Mã SV", "Họ tên", "Tổng buổi", "Buổi vắng", "Tỷ lệ vắng (%)", "Cảnh báo"]
            keys = ["ma_sinh_vien", "ho_ten", "tong_buoi_hoc", "so_buoi_vang", "ty_le_vang", "muc_do_canh_bao"]
            table = self.create_table(self.data, column_names, keys)
            
            for i, row in enumerate(self.data):
                if row.get("muc_do_canh_bao") == "NGUY CƠ CẤM THI":
                    for col in range(table.columnCount()):
                        table.item(i, col).setBackground(QColor("#FFB6C1"))
            
            self.main_layout.addWidget(table)
    
    def export_to_excel(self):
        if not self.data:
            QMessageBox.warning(self, "Cảnh báo", "Không có dữ liệu để xuất")
            return
        
        file_path, _ = QFileDialog.getSaveFileName(self, "Lưu file", "", "Excel Files (*.xlsx)")
        if not file_path:
            return
        
        try:
            wb = openpyxl.Workbook()
            ws = wb.active
            ws.title = "Cảnh báo"
            
            ws.append(["DANH SÁCH CẢNH BÁO CẤM THI"])
            ws.append(["Lưu ý: Sinh viên có tỷ lệ vắng trên 20% có nguy cơ bị cấm thi"])
            ws.append([])
            
            headers = ["Mã SV", "Họ tên", "Tổng buổi", "Buổi vắng", "Tỷ lệ vắng (%)", "Mức độ cảnh báo"]
            ws.append(headers)
            
            for cell in ws[4]:
                cell.font = Font(bold=True, color="FFFFFF")
                cell.fill = PatternFill(start_color="C65911", end_color="C65911", fill_type="solid")
            
            for row_idx, row in enumerate(self.data, start=5):
                ws.append([
                    row.get("ma_sinh_vien", ""),
                    row.get("ho_ten", ""),
                    row.get("tong_buoi_hoc", ""),
                    row.get("so_buoi_vang", ""),
                    round(row.get("ty_le_vang", 0), 2),
                    row.get("muc_do_canh_bao", "")
                ])
                
                if row.get("muc_do_canh_bao") == "NGUY CƠ CẤM THI":
                    for col in range(1, 7):
                        ws.cell(row=row_idx, column=col).fill = PatternFill(
                            start_color="FFB6C1", end_color="FFB6C1", fill_type="solid"
                        )
            
            for col in ws.columns:
                ws.column_dimensions[get_column_letter(col[0].column)].width = 18
            
            wb.save(file_path)
            QMessageBox.information(self, "Thành công", "Đã xuất báo cáo thành công!")
        except Exception as e:
            QMessageBox.critical(self, "Lỗi", f"Không thể xuất báo cáo: {str(e)}")
