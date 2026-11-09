"""Helper functions để tích hợp API vào student dashboard"""
from services.api_service import get_api_client
import logging

logger = logging.getLogger(__name__)


class StudentAPIHelper:
    
    @staticmethod
    def get_attendance_history(ma_sv: str):
        """Lấy lịch sử điểm danh cá nhân"""
        if not ma_sv:
            logger.error("get_attendance_history: ma_sv is empty")
            return False, []
        try:
            api = get_api_client()
            endpoint = f"/sinhvien/lich-su-diem-danh/{ma_sv}"
            response = api.make_request(endpoint, "GET")
            
            if not response or not response.get('success'):
                logger.error(f"Lỗi tải lịch sử điểm danh: {response}")
                return False, []
            
            history = response.get('data', [])
            return True, history
        
        except Exception as e:
            logger.error(f"Exception tải lịch sử: {e}")
    def get_attendance_warning(ma_sv: str):
        """Lấy cảnh báo nếu tỷ lệ chuyên cần dưới mức"""
        if not ma_sv:
            return None
        try:
            api = get_api_client()
            success, warning = api.get_student_attendance_warning(ma_sv)
            
            if not success:
                return None
            
            return {
                'has_warning': warning.get('co_canh_bao', False),
                'message': warning.get('thong_bao', ''),
                'attendance_percentage': warning.get('ty_le_co_mat', 0),
                'required_percentage': warning.get('ty_le_toi_thieu', 0)
            }
        
        except Exception as e:
            logger.error(f"Exception tải cảnh báo: {e}")
            return None
    
    @staticmethod
    def get_overall_warning_status(ma_sv: str):
        """Lấy trạng thái cảnh báo tổng hợp cho tất cả các lớp"""
        if not ma_sv:
            return {
                'muc_do': 0,
                'so_lop_canh_bao': 0,
                'so_lop_do': 0,
                'so_lop_vang': 0,
                'danh_sach_lop': '',
                'message': '',
                'status': 'ok'
            }
        try:
            api = get_api_client()
            endpoint = f"/sinhvien/trang-thai-canh-bao/{ma_sv}"
            response = api.make_request(endpoint, "GET")
            
            if not response or not response.get('success'):
                logger.error(f"Lỗi tải trạng thái cảnh báo: {response}")
                return {
                    'muc_do': 0,
                    'so_lop_canh_bao': 0,
                    'so_lop_do': 0,
                    'so_lop_vang': 0,
                    'danh_sach_lop': '',
                    'message': '',
                    'status': 'ok'
                }
            
            muc_do = response.get('muc_do', 0)
            status = 'ok'
            if muc_do == 3:
                status = 'danger'
            elif muc_do == 2:
                status = 'warning'
            
            return {
                'muc_do': muc_do,
                'so_lop_canh_bao': response.get('so_lop_canh_bao', 0),
                'so_lop_do': response.get('so_lop_do', 0),
                'so_lop_vang': response.get('so_lop_vang', 0),
                'danh_sach_lop': response.get('danh_sach_lop', ''),
                'message': response.get('message', ''),
                'status': status
            }
        
        except Exception as e:
            logger.error(f"Exception tải trạng thái cảnh báo: {e}")
            return {
                'muc_do': 0,
                'so_lop_canh_bao': 0,
                'so_lop_do': 0,
                'so_lop_vang': 0,
                'danh_sach_lop': '',
                'message': '',
                'status': 'ok'
            }

    @staticmethod
    def get_detailed_attendance_warning(ma_sv: str):
        """Lấy chi tiết cảnh báo chuyên cần (Report 17)"""
        if not ma_sv:
            return False, {}
        try:
            api = get_api_client()
            endpoint = f"/sinhvien/canh-bao-chuyen-can/{ma_sv}"
            response = api.make_request(endpoint, "GET")
            
            if not response or not response.get('success'):
                logger.error(f"Lỗi tải chi tiết cảnh báo: {response}")
                return False, {}
            
            return True, response
        except Exception as e:
            logger.error(f"Exception tải chi tiết cảnh báo: {e}")
            return False, {}
    
    @staticmethod
    def get_attendance_stats(ma_sv: str):
        """Lấy thống kê chuyên cần (Report 16)"""
        if not ma_sv:
            return False, []
        try:
            api = get_api_client()
            endpoint = f"/sinhvien/thong-ke-chuyen-can/{ma_sv}"
            response = api.make_request(endpoint, "GET")
            
            if not response or not response.get('success'):
                logger.error(f"Lỗi tải thống kê chuyên cần: {response}")
                return False, []
            
            return True, response.get('data', [])
        except Exception as e:
            logger.error(f"Exception tải thống kê chuyên cần: {e}")
            return False, []

    @staticmethod
    def get_student_sessions(ma_sv: str, start_date: str = None, end_date: str = None):
        """Lấy danh sách buổi học cho sinh viên"""
        if not ma_sv:
            logger.error("get_student_sessions: ma_sv is empty")
            return False, []
        try:
            api = get_api_client()
            endpoint = f"/sinhvien/buoi-hoc/{ma_sv}"
            
            params = {}
            if start_date:
                params['start_date'] = start_date
            if end_date:
                params['end_date'] = end_date
            
            response = api.make_request(endpoint, "GET", params=params)
            
            if not response or not response.get('success'):
                logger.error(f"Lỗi tải danh sách buổi học: {response}")
                return False, []
            
            sessions = response.get('data', [])
            return True, sessions
        
        except Exception as e:
            logger.error(f"Exception tải danh sách buổi học: {e}")
            return False, []

    @staticmethod
    def get_available_classes(ma_sv: str):
        """Lấy danh sách lớp học phần có thể đăng ký"""
        if not ma_sv:
            return False, []
        try:
            api = get_api_client()
            endpoint = "/dangky/ds-lop"
            params = {'ma_sinh_vien': ma_sv}
            response = api.make_request(endpoint, "GET", params=params)
            
            if not response or not response.get('success'):
                logger.error(f"Lỗi tải danh sách lớp: {response}")
                return False, []
            
            return True, response.get('data', [])
        except Exception as e:
            logger.error(f"Exception tải danh sách lớp: {e}")
            return False, []

    @staticmethod
    def register_class(ma_sv: str, ma_lhp: str):
        """Đăng ký lớp học phần"""
        try:
            api = get_api_client()
            endpoint = "/dangky"
            data = {'ma_sinh_vien': ma_sv, 'ma_lhp': ma_lhp}
            response = api.make_request(endpoint, "POST", json=data)
            
            if response and response.get('success'):
                return True, response.get('message', 'Đăng ký thành công')
            return False, response.get('message', 'Đăng ký thất bại')
        except Exception as e:
            return False, str(e)

    @staticmethod
    def cancel_registration(ma_sv: str, ma_lhp: str):
        """Hủy đăng ký lớp học phần"""
        try:
            api = get_api_client()
            endpoint = "/dangky"
            data = {'ma_sinh_vien': ma_sv, 'ma_lhp': ma_lhp}
            response = api.make_request(endpoint, "DELETE", json=data)
            
            if response and response.get('success'):
                return True, response.get('message', 'Hủy đăng ký thành công')
            return False, response.get('message', 'Hủy đăng ký thất bại')
        except Exception as e:
            return False, str(e)
