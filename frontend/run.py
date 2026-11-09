import subprocess
import sys
import os

# Lấy đường dẫn tới Python trong venv
venv_python = os.path.join(os.path.dirname(__file__), '.venv', 'Scripts', 'python.exe')

if os.path.exists(venv_python):
    print("Đang khởi động Hệ thống Quản lý Điểm danh...")
    subprocess.run([venv_python, 'app.py'])
else:
    print("Lỗi: Không tìm thấy virtual environment!")
    print("Vui lòng tạo virtual environment trước:")
    print("  python -m venv .venv")
    print("  .venv\\Scripts\\activate")
    print("  pip install -r requirements.txt")
    sys.exit(1)
