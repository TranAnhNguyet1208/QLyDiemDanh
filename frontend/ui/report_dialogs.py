from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import openpyxl
from openpyxl.styles import Font, PatternFill
from openpyxl.utils import get_column_letter
import io
from datetime import datetime
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Qt5Agg')
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure


class ReportDialog(QDialog):
    
    def __init__(self, parent=None, title="Báo cáo", data=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setMinimumSize(1600, 800)
        self.setWindowState(Qt.WindowMaximized)
        self.data = data or {}
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


class Report1Dialog(ReportDialog):
    """Báo cáo tổng hợp chuyên cần toàn bộ lớp học theo học kỳ"""
    
    def __init__(self, parent=None, data=None):
        super().__init__(parent, "Báo cáo tổng hợp chuyên cần (học kỳ)", data)
    
    def init_ui(self):
        super().init_ui()
        
        if self.data and isinstance(self.data, list) and len(self.data) > 0:
            column_names = ["Mã LHP", "Tên Môn", "Giảng viên", "Tổng SV", "Buổi đã tổ chức", "Tỷ lệ chuyên cần (%)"]
            keys = ["ma_lop_hoc_phan", "ten_mon_hoc", "ten_giang_vien", "tong_so_sinh_vien", "so_buoi_da_to_chuc", "ty_le_chuyen_can_trung_binh"]
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
            ws.title = "Báo cáo chuyên cần"
            
            headers = ["Mã LHP", "Tên Môn Học", "Giảng viên", "Tổng SV", "Buổi đã tổ chức", "Tỷ lệ (%)"]
            ws.append(headers)
            
            for cell in ws[1]:
                cell.font = Font(bold=True, color="FFFFFF")
                cell.fill = PatternFill(start_color="366092", end_color="366092", fill_type="solid")
            
            for row in self.data:
                ws.append([
                    row.get("ma_lop_hoc_phan", ""),
                    row.get("ten_mon_hoc", ""),
                    row.get("ten_giang_vien", ""),
                    row.get("tong_so_sinh_vien", ""),
                    row.get("so_buoi_da_to_chuc", ""),
                    round(row.get("ty_le_chuyen_can_trung_binh", 0), 2)
                ])
            
            for col in ws.columns:
                ws.column_dimensions[get_column_letter(col[0].column)].width = 20
            
            wb.save(file_path)
            QMessageBox.information(self, "Thành công", "Đã xuất báo cáo thành công!")
        except Exception as e:
            QMessageBox.critical(self, "Lỗi", f"Không thể xuất báo cáo: {str(e)}")


class Report2Dialog(ReportDialog):
    """Báo cáo tỷ lệ chuyên cần theo giảng viên"""
    
    def __init__(self, parent=None, data=None):
        super().__init__(parent, "Tỷ lệ chuyên cần theo giảng viên", data)
    
    def init_ui(self):
        super().init_ui()
        
        if self.data and isinstance(self.data, list) and len(self.data) > 0:
            column_names = ["Mã GV", "Tên Giảng viên", "Tỷ lệ chuyên cần TB (%)"]
            keys = ["ma_giang_vien", "ten_giang_vien", "ty_le_chuyen_can_trung_binh"]
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
            ws.title = "Báo cáo GV"
            
            headers = ["Mã Giảng viên", "Tên Giảng viên", "Tỷ lệ chuyên cần TB (%)"]
            ws.append(headers)
            
            for cell in ws[1]:
                cell.font = Font(bold=True, color="FFFFFF")
                cell.fill = PatternFill(start_color="366092", end_color="366092", fill_type="solid")
            
            for row in self.data:
                ws.append([
                    row.get("ma_giang_vien", ""),
                    row.get("ten_giang_vien", ""),
                    round(row.get("ty_le_chuyen_can_trung_binh", 0), 2)
                ])
            
            for col in ws.columns:
                ws.column_dimensions[get_column_letter(col[0].column)].width = 25
            
            wb.save(file_path)
            QMessageBox.information(self, "Thành công", "Đã xuất báo cáo thành công!")
        except Exception as e:
            QMessageBox.critical(self, "Lỗi", f"Không thể xuất báo cáo: {str(e)}")


class Report3Dialog(ReportDialog):
    """Danh sách sinh viên vượt quá số buổi vắng cho phép (>20%)"""
    
    def __init__(self, parent=None, data=None):
        super().__init__(parent, "Danh sách sinh viên vắng trên 20%", data)
    
    def init_ui(self):
        super().init_ui()
        
        if self.data and isinstance(self.data, list) and len(self.data) > 0:
            column_names = ["Mã SV", "Họ tên", "Lớp", "Môn học", "Buổi vắng", "Tỷ lệ (%)", "Trạng thái"]
            keys = ["ma_sinh_vien", "ho_ten", "ten_lop_hanh_chinh", "ten_mon_hoc", "so_buoi_vang", "ty_le_vang", "trang_thai"]
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
            ws.title = "SV vắng quá mức"
            
            headers = ["Mã SV", "Họ tên", "Lớp hành chính", "Môn học", "Buổi vắng", "Tỷ lệ (%)", "Trạng thái"]
            ws.append(headers)
            
            for cell in ws[1]:
                cell.font = Font(bold=True, color="FFFFFF")
                cell.fill = PatternFill(start_color="C65911", end_color="C65911", fill_type="solid")
            
            for row in self.data:
                ws.append([
                    row.get("ma_sinh_vien", ""),
                    row.get("ho_ten", ""),
                    row.get("ten_lop_hanh_chinh", ""),
                    row.get("ten_mon_hoc", ""),
                    row.get("so_buoi_vang", ""),
                    round(row.get("ty_le_vang", 0), 2),
                    row.get("trang_thai", "")
                ])
            
            for col in ws.columns:
                ws.column_dimensions[get_column_letter(col[0].column)].width = 20
            
            wb.save(file_path)
            QMessageBox.information(self, "Thành công", "Đã xuất báo cáo thành công!")
        except Exception as e:
            QMessageBox.critical(self, "Lỗi", f"Không thể xuất báo cáo: {str(e)}")


class Report4Dialog(ReportDialog):
    """Thống kê số buổi học và điểm danh"""
    
    def __init__(self, parent=None, data=None):
        super().__init__(parent, "Thống kê buổi học và điểm danh", data)
    
    def init_ui(self):
        super().init_ui()
        
        if self.data and isinstance(self.data, dict):
            form_layout = QFormLayout()
            
            stats = [
                ("Tổng số buổi học", "tong_so_buoi_hoc"),
                ("Tổng lượt điểm danh", "tong_luot_diem_danh"),
                ("Tổng lượt có mặt", "tong_luot_co_mat"),
                ("Tổng lượt vắng có phép", "tong_luot_vang_co_phep"),
                ("Tổng lượt vắng không phép", "tong_luot_vang_khong_phep"),
            ]
            
            for label, key in stats:
                value = self.data.get(key, 0)
                value_label = QLabel(str(value))
                value_label.setFont(QFont('Segoe UI', 12, QFont.Bold))
                form_layout.addRow(label + ":", value_label)
            
            self.main_layout.addLayout(form_layout)
            self.main_layout.addStretch()
    
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
            ws.title = "Thống kê"
            
            headers = ["Chỉ tiêu", "Số lượng"]
            ws.append(headers)
            
            for cell in ws[1]:
                cell.font = Font(bold=True, color="FFFFFF")
                cell.fill = PatternFill(start_color="70AD47", end_color="70AD47", fill_type="solid")
            
            stats = [
                ["Tổng số buổi học", self.data.get("tong_so_buoi_hoc", 0)],
                ["Tổng lượt điểm danh", self.data.get("tong_luot_diem_danh", 0)],
                ["Tổng lượt có mặt", self.data.get("tong_luot_co_mat", 0)],
                ["Tổng lượt vắng có phép", self.data.get("tong_luot_vang_co_phep", 0)],
                ["Tổng lượt vắng không phép", self.data.get("tong_luot_vang_khong_phep", 0)],
            ]
            
            for row in stats:
                ws.append(row)
            
            ws.column_dimensions['A'].width = 30
            ws.column_dimensions['B'].width = 15
            
            wb.save(file_path)
            QMessageBox.information(self, "Thành công", "Đã xuất báo cáo thành công!")
        except Exception as e:
            QMessageBox.critical(self, "Lỗi", f"Không thể xuất báo cáo: {str(e)}")


class Report5Dialog(QDialog):
    """Biểu đồ tròn thể hiện tỷ lệ có mặt - vắng mặt - CHỈ XEM, KHÔNG XUẤT EXCEL"""
    
    def __init__(self, parent=None, data=None):
        super().__init__(parent)
        self.setWindowTitle("Biểu đồ tỷ lệ có mặt/vắng mặt")
        self.setMinimumSize(1400, 800)
        self.setWindowState(Qt.WindowMaximized)
        self.data = data or {}
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout(self)
        self.main_widget = QWidget()
        self.main_layout = QVBoxLayout(self.main_widget)
        layout.addWidget(self.main_widget)
        
        button_layout = QHBoxLayout()
        close_btn = QPushButton("Đóng")
        close_btn.clicked.connect(self.accept)
        button_layout.addStretch()
        button_layout.addWidget(close_btn)
        layout.addLayout(button_layout)
        
        if self.data and isinstance(self.data, dict) and self.data.get('so_luong'):
            self.create_pie_chart()
    
    def create_pie_chart(self):
        so_luong = self.data.get('so_luong', {})
        ty_le = self.data.get('ty_le', {})
        
        labels = [
            f"Có mặt ({so_luong.get('co_mat', 0)}) - {ty_le.get('co_mat', 0):.1f}%",
            f"Vắng có phép ({so_luong.get('vang_co_phep', 0)}) - {ty_le.get('vang_co_phep', 0):.1f}%",
            f"Vắng không phép ({so_luong.get('vang_khong_phep', 0)}) - {ty_le.get('vang_khong_phep', 0):.1f}%"
        ]
        
        sizes = [
            so_luong.get('co_mat', 0),
            so_luong.get('vang_co_phep', 0),
            so_luong.get('vang_khong_phep', 0)
        ]
        
        colors = ['#4CAF50', '#FFC107', '#F44336']
        explode = (0.05, 0.05, 0.05)
        
        if sum(sizes) == 0:
            no_data_label = QLabel("Chưa có dữ liệu điểm danh để hiển thị biểu đồ")
            no_data_label.setAlignment(Qt.AlignCenter)
            no_data_label.setStyleSheet("font-size: 14pt; color: gray; font-style: italic;")
            self.main_layout.addWidget(no_data_label)
            return

        fig = Figure(figsize=(10, 6), dpi=100)
        ax = fig.add_subplot(111)
        
        colors = ['#4CAF50', '#FFC107', '#F44336']
        
        wedges, texts, autotexts = ax.pie(
            sizes,
            labels=labels,
            autopct='%1.1f%%',
            colors=colors,
            explode=explode,
            shadow=True,
            startangle=90,
            textprops={'fontsize': 12, 'weight': 'bold'}
        )
        
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontsize(14)
            autotext.set_weight('bold')
            
        for text in texts:
            text.set_fontsize(12)
        
        ax.set_title('Tỷ lệ Có mặt - Vắng mặt của toàn hệ thống', fontsize=18, weight='bold', pad=20)
        ax.axis('equal')
        
        canvas = FigureCanvas(fig)
        self.main_layout.addWidget(canvas)
    


class Report6Dialog(ReportDialog):
    """Danh sách sinh viên đủ/không đủ điều kiện dự thi"""
    
    def __init__(self, parent=None, data=None):
        super().__init__(parent, "Danh sách đủ/không đủ dự thi", data)
    
    def init_ui(self):
        super().init_ui()
        
        if self.data and isinstance(self.data, list) and len(self.data) > 0:
            column_names = ["Mã SV", "Họ tên", "Lớp", "Môn học", "Buổi học", "Buổi vắng", "Tỷ lệ (%)", "Dự thi"]
            keys = ["ma_sinh_vien", "ho_ten", "ten_lop_hanh_chinh", "ten_mon_hoc", "tong_so_buoi_hoc", "so_buoi_vang", "ty_le_vang", "du_kien_du_thi"]
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
            ws.title = "Dự thi"
            
            headers = ["Mã SV", "Họ tên", "Lớp hành chính", "Môn học", "Tổng buổi", "Buổi vắng", "Tỷ lệ (%)", "Dự kiến dự thi"]
            ws.append(headers)
            
            for cell in ws[1]:
                cell.font = Font(bold=True, color="FFFFFF")
                cell.fill = PatternFill(start_color="1F4788", end_color="1F4788", fill_type="solid")
            
            for row in self.data:
                ws.append([
                    row.get("ma_sinh_vien", ""),
                    row.get("ho_ten", ""),
                    row.get("ten_lop_hanh_chinh", ""),
                    row.get("ten_mon_hoc", ""),
                    row.get("tong_so_buoi_hoc", ""),
                    row.get("so_buoi_vang", ""),
                    round(row.get("ty_le_vang", 0), 2),
                    row.get("du_kien_du_thi", "")
                ])
            
            for col in ws.columns:
                ws.column_dimensions[get_column_letter(col[0].column)].width = 18
            
            wb.save(file_path)
            QMessageBox.information(self, "Thành công", "Đã xuất báo cáo thành công!")
        except Exception as e:
            QMessageBox.critical(self, "Lỗi", f"Không thể xuất báo cáo: {str(e)}")


class Report7Dialog(ReportDialog):
    """So sánh tỷ lệ chuyên cần giữa các khoa"""
    
    def __init__(self, parent=None, data=None):
        super().__init__(parent, "So sánh tỷ lệ chuyên cần giữa các khoa", data)
    
    def init_ui(self):
        super().init_ui()
        
        if self.data and isinstance(self.data, list) and len(self.data) > 0:
            column_names = ["Mã Khoa", "Tên Khoa", "Lớp HP", "Buổi học", "Lượt điểm danh", "Có mặt", "Tỷ lệ (%)"]
            keys = ["ma_khoa", "ten_khoa", "so_lop_hoc_phan", "tong_so_buoi_hoc", "tong_luot_diem_danh", "tong_luot_co_mat", "ty_le_chuyen_can"]
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
            ws.title = "So sánh Khoa"
            
            headers = ["Mã Khoa", "Tên Khoa", "Số lớp HP", "Tổng buổi học", "Tổng lượt điểm danh", "Có mặt", "Tỷ lệ (%)"]
            ws.append(headers)
            
            for cell in ws[1]:
                cell.font = Font(bold=True, color="FFFFFF")
                cell.fill = PatternFill(start_color="375623", end_color="375623", fill_type="solid")
            
            for row in self.data:
                ws.append([
                    row.get("ma_khoa", ""),
                    row.get("ten_khoa", ""),
                    row.get("so_lop_hoc_phan", ""),
                    row.get("tong_so_buoi_hoc", ""),
                    row.get("tong_luot_diem_danh", ""),
                    row.get("tong_luot_co_mat", ""),
                    round(row.get("ty_le_chuyen_can", 0), 2)
                ])
            
            for col in ws.columns:
                ws.column_dimensions[get_column_letter(col[0].column)].width = 18
            
            wb.save(file_path)
            QMessageBox.information(self, "Thành công", "Đã xuất báo cáo thành công!")
        except Exception as e:
            QMessageBox.critical(self, "Lỗi", f"Không thể xuất báo cáo: {str(e)}")


class Report8Dialog(ReportDialog):
    """Lịch sử chỉnh sửa dữ liệu điểm danh"""
    
    def __init__(self, parent=None, data=None):
        super().__init__(parent, "Lịch sử chỉnh sửa điểm danh", data)
    
    def init_ui(self):
        super().init_ui()
        
        if self.data and isinstance(self.data, list) and len(self.data) > 0:
            column_names = ["Thời gian", "Người thực hiện", "Hành động", "Đối tượng", "Ghi chú"]
            keys = ["thoi_gian", "nguoi_thuc_hien", "hanh_dong", "doi_tuong", "ghi_chu"]
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
            ws.title = "Lịch sử"
            
            headers = ["Thời gian", "Người thực hiện", "Hành động", "Đối tượng", "Ghi chú"]
            ws.append(headers)
            
            for cell in ws[1]:
                cell.font = Font(bold=True, color="FFFFFF")
                cell.fill = PatternFill(start_color="595959", end_color="595959", fill_type="solid")
            
            for row in self.data:
                ws.append([
                    row.get("thoi_gian", ""),
                    row.get("nguoi_thuc_hien", ""),
                    row.get("hanh_dong", ""),
                    row.get("doi_tuong", ""),
                    row.get("ghi_chu", "")
                ])
            
            ws.column_dimensions['A'].width = 20
            ws.column_dimensions['B'].width = 20
            ws.column_dimensions['C'].width = 20
            ws.column_dimensions['D'].width = 15
            ws.column_dimensions['E'].width = 30
            
            wb.save(file_path)
            QMessageBox.information(self, "Thành công", "Đã xuất báo cáo thành công!")
        except Exception as e:
            QMessageBox.critical(self, "Lỗi", f"Không thể xuất báo cáo: {str(e)}")
