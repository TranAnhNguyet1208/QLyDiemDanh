import os
from dotenv import load_dotenv

# Tải các biến môi trường từ file .env
load_dotenv()

# Cài đặt kết nối cơ sở dữ liệu
DB_DRIVER = os.getenv('DB_DRIVER', 'ODBC Driver 17 for SQL Server')
DB_SERVER = os.getenv('DB_SERVER', 'localhost')
DB_DATABASE = os.getenv('DB_DATABASE', 'qlsv')
DB_USERNAME = os.getenv('DB_USERNAME', os.getenv('DB_USER', ''))
DB_PASSWORD = os.getenv('DB_PASSWORD', '')
DB_TRUSTED_CONNECTION = os.getenv('DB_TRUSTED_CONNECTION', 'no')
DB_ENCRYPT = os.getenv('DB_ENCRYPT', 'yes')
DB_TRUST_SERVER_CERTIFICATE = os.getenv('DB_TRUST_SERVER_CERTIFICATE', 'yes')

DB_MAX_RETRIES = int(os.getenv('DB_MAX_RETRIES', '3'))
DB_RETRY_BACKOFF = float(os.getenv('DB_RETRY_BACKOFF', '0.5'))
DB_MAX_CONNECTIONS = int(os.getenv('DB_MAX_CONNECTIONS', '5'))

# Flask cấu hình
FLASK_ENV = os.getenv('FLASK_ENV', 'development')
DEBUG = os.getenv('DEBUG', 'True').lower() == 'true'

