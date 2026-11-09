import pyodbc
import time
import logging
from app.core.config import (
    DB_DRIVER,
    DB_SERVER,
    DB_DATABASE,
    DB_USERNAME,
    DB_PASSWORD,
    DB_TRUSTED_CONNECTION,
    DB_ENCRYPT,
    DB_TRUST_SERVER_CERTIFICATE,
    DB_MAX_RETRIES,
    DB_RETRY_BACKOFF,
    DB_MAX_CONNECTIONS,
)

logger = logging.getLogger(__name__)

try:
    pyodbc.pooling = True
except Exception:
    pass

import threading

_db_semaphore = threading.BoundedSemaphore(DB_MAX_CONNECTIONS)


def _build_connection_string():
    """Xây dựng connection string dựa trên cấu hình"""
    if DB_TRUSTED_CONNECTION.lower() == 'yes':
        return (
            f'Driver={{{DB_DRIVER}}};'
            f'Server={DB_SERVER};'
            f'Database={DB_DATABASE};'
            f'Trusted_Connection=yes;'
        )
    else:
        conn_str = (
            f'Driver={{{DB_DRIVER}}};'
            f'Server={DB_SERVER};'
            f'Database={DB_DATABASE};'
            f'UID={DB_USERNAME};'
            f'PWD={DB_PASSWORD};'
        )
        
        if DB_ENCRYPT.lower() == 'yes':
            conn_str += 'Encrypt=yes;'
        
        if DB_TRUST_SERVER_CERTIFICATE.lower() == 'yes':
            conn_str += 'TrustServerCertificate=yes;'
        
        return conn_str


def get_db_connection():
    connection_string = _build_connection_string()
    attempt = 0
    while attempt < max(1, DB_MAX_RETRIES):
        acquired = _db_semaphore.acquire(timeout=10)
        if not acquired:
            logger.warning("Không thể lấy DB semaphore (timeout)")
            attempt += 1
            time.sleep(DB_RETRY_BACKOFF * (2 ** (attempt - 1)))
            continue

        try:
            conn = pyodbc.connect(connection_string)

            class _ConnProxy:
                def __init__(self, real_conn, semaphore):
                    self._real = real_conn
                    self._sem = semaphore

                def close(self):
                    try:
                        self._real.close()
                    finally:
                        try:
                            self._sem.release()
                        except Exception:
                            pass

                def __getattr__(self, item):
                    return getattr(self._real, item)

            return _ConnProxy(conn, _db_semaphore)

        except pyodbc.Error as ex:
            try:
                _db_semaphore.release()
            except Exception:
                pass

            sqlstate = None
            try:
                sqlstate = ex.args[0]
            except Exception:
                pass
            logger.warning(
                "Lỗi kết nối cơ sở dữ liệu lần %d (SQLSTATE=%s): %s",
                attempt + 1,
                sqlstate,
                ex,
            )
            attempt += 1
            if attempt >= DB_MAX_RETRIES:
                print(f"\nLỗi kết nối database (SQLSTATE: {sqlstate}): {ex}")
                if sqlstate == '28000':
                    print("Sai tên đăng nhập hoặc mật khẩu.")
                elif sqlstate == '08001':
                    print("Lỗi kết nối mạng hoặc tường lửa.")
                return None

            backoff = DB_RETRY_BACKOFF * (2 ** (attempt - 1))
            time.sleep(backoff)

    return None
