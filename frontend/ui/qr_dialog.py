
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton, QMessageBox
from PyQt5.QtGui import QPixmap, QFont
from PyQt5.QtCore import Qt, QSize
import base64
import io
from PIL import Image
import logging

logger = logging.getLogger(__name__)


class QRDialog(QDialog):
    """Dialog hiển thị mã QR lớn để sinh viên quét"""
    
    def __init__(self, qr_image_base64: str, ma_buoi_hoc: str = "", parent=None, qr_link: str = ""):
        """
        qr_image_base64: Ảnh QR encoded base64 từ API
        ma_buoi_hoc: Mã buổi học (hiển thị tham khảo)
        qr_link: Link điểm danh (để hiển thị)
        """
        super().__init__(parent)
        self.qr_image_base64 = qr_image_base64
        self.ma_buoi_hoc = ma_buoi_hoc
        self.qr_link = qr_link
        self.init_ui()
        self.setModal(True)
    
    def init_ui(self):
        """Khởi tạo giao diện"""
        self.setWindowTitle("Mã QR Điểm Danh")
        self.setFixedSize(1000, 950)
        self.setStyleSheet("""
            QDialog {
                background-color: #f5f6fa;
            }
            QLabel {
                color: #2c3e50;
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(40, 40, 40, 40)
        
        # Title
        title = QLabel("Mã QR Điểm Danh")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 40px; font-weight: bold; margin-bottom: 15px;")
        layout.addWidget(title)
        
        # Info
        if self.ma_buoi_hoc:
            info_label = QLabel(f"Buổi học: {self.ma_buoi_hoc}")
            info_label.setAlignment(Qt.AlignCenter)
            info_label.setStyleSheet("font-size: 28px; font-weight: bold; color: #3498db;")
            layout.addWidget(info_label)
            
        instruction_label = QLabel("Vui lòng yêu cầu sinh viên quét mã QR bên dưới\nđể thực hiện điểm danh")
        instruction_label.setAlignment(Qt.AlignCenter)
        instruction_label.setStyleSheet("font-size: 20px; color: #7f8c8d;")
        layout.addWidget(instruction_label)
        
        # QR Code Image
        qr_label = QLabel()
        qr_label.setAlignment(Qt.AlignCenter)
        qr_label.setFixedSize(600, 600)
        qr_label.setStyleSheet("""
            background-color: white;
            border: 3px solid #bdc3c7;
            border-radius: 15px;
        """)
        
        try:
            # Giải mã base64 image
            if "," in self.qr_image_base64:
                self.qr_image_base64 = self.qr_image_base64.split(",")[1]
                
            image_data = base64.b64decode(self.qr_image_base64)
            image = Image.open(io.BytesIO(image_data))
            
            # Convert to QPixmap
            byte_array = io.BytesIO()
            image.save(byte_array, format="PNG")
            q_image = QPixmap()
            q_image.loadFromData(byte_array.getvalue())
            
            # Scale ảnh QR
            qr_label.setPixmap(q_image.scaled(580, 580, Qt.KeepAspectRatio, Qt.SmoothTransformation))
            
        except Exception as e:
            logger.error(f"Lỗi tải QR image: {e}")
            qr_label.setText("Lỗi tải mã QR")
            qr_label.setStyleSheet("font-size: 20px; color: red; background: white;")
            
        layout.addWidget(qr_label, 0, Qt.AlignCenter)
        
        # Static expiration message
        expiration_label = QLabel("Mã QR sẽ hết hạn khi buổi học kết thúc")
        expiration_label.setAlignment(Qt.AlignCenter)
        # Tăng font size
        expiration_label.setStyleSheet("font-size: 24px; font-weight: bold; color: #e74c3c; margin-top: 15px;")
        layout.addWidget(expiration_label)
        
        # Close button
        close_btn = QPushButton("Đóng")
        close_btn.setCursor(Qt.PointingHandCursor)
        close_btn.setStyleSheet("""
            QPushButton {
                background-color: #95a5a6;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 15px 40px;
                font-weight: bold;
                font-size: 18px;
            }
            QPushButton:hover {
                background-color: #7f8c8d;
            }
        """)
        close_btn.clicked.connect(self.close)
        layout.addWidget(close_btn, 0, Qt.AlignCenter)
