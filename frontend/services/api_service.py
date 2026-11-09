import requests
import logging
from typing import Dict, List, Any, Optional, Tuple

logger = logging.getLogger(__name__)

API_BASE_URL = "http://127.0.0.1:5000/api"
TIMEOUT = 10


class APIClient:
    """Client wrapper cho tất cả API calls"""
    
    def __init__(self, base_url: str = API_BASE_URL):
        self.base_url = base_url
        self.session = requests.Session()
        self.auth_token = None

    def set_auth_token(self, token: str):
        """Thiết lập token xác thực"""
        self.auth_token = token
        if token:
            self.session.headers.update({"Authorization": f"Bearer {token}"})
    
    def _request(self, method: str, endpoint: str, **kwargs) -> Tuple[bool, Dict[str, Any]]:
        """Thực hiện HTTP request"""
        url = f"{self.base_url}{endpoint}"
        kwargs.setdefault('timeout', TIMEOUT)
        
        try:
            if method == 'GET':
                response = self.session.get(url, **kwargs)
            elif method == 'POST':
                response = self.session.post(url, **kwargs)
            elif method == 'PUT':
                response = self.session.put(url, **kwargs)
            elif method == 'DELETE':
                response = self.session.delete(url, **kwargs)
            else:
                return False, {"message": f"Phương thức {method} không hỗ trợ"}
            
            if response.ok:
                return True, response.json() if response.text else {}
            else:
                logger.error(f"API error {response.status_code}: {response.text}")
                return False, {"message": f"Lỗi {response.status_code}: {response.text}"}
        
        except requests.exceptions.Timeout:
            logger.error(f"API timeout: {url}")
            return False, {"message": "Hết thời gian chờ máy chủ"}
        except requests.exceptions.ConnectionError:
            logger.error(f"API connection error: {url}")
            return False, {"message": "Không thể kết nối tới máy chủ"}
        except Exception as e:
            logger.error(f"API error: {e}")
            return False, {"message": str(e)}

    def login(self, username, password) -> Tuple[bool, Dict[str, Any]]:
        """POST /dangnhap - Đăng nhập người dùng"""
        payload = {'username': username, 'password': password}
        return self._request('POST', '/dangnhap', json=payload)
    
    # ============= SINH VIÊN =============
    
    def get_all_students(self, class_id: str = None) -> Tuple[bool, List[Dict]]:
        """GET /sinhvien - Lấy danh sách tất cả sinh viên (có thể lọc theo lớp)"""
        params = {'class_id': class_id} if class_id else {}
        success, data = self._request('GET', '/sinhvien', params=params)
        return success, data.get('data', []) if success else []
    
    def get_student(self, ma_sv: str) -> Tuple[bool, Dict]:
        """GET /sinhvien/<ma_sv> - Lấy thông tin một sinh viên"""
        success, data = self._request('GET', f'/sinhvien/{ma_sv}')
        return success, data.get('data', {}) if success else {}
    
    def create_student(self, student_data: Dict) -> Tuple[bool, str]:
        """POST /sinhvien - Tạo sinh viên mới"""
        success, data = self._request('POST', '/sinhvien', json=student_data)
        return success, data.get('message', 'Thành công') if success else data.get('message', 'Lỗi')
    
    def update_student(self, ma_nguoi_dung: str, student_data: Dict) -> Tuple[bool, str]:
        """PUT /admin/sinhvien/<ma_nguoi_dung> - Cập nhật thông tin sinh viên"""
        success, data = self._request('PUT', f'/admin/sinhvien/{ma_nguoi_dung}', json=student_data)
        return success, data.get('message', 'Thành công') if success else data.get('message', 'Lỗi')
    
    def delete_student(self, ma_sv: str) -> Tuple[bool, str]:
        """DELETE /sinhvien/<ma_sv> - Xóa sinh viên"""
        success, data = self._request('DELETE', f'/sinhvien/{ma_sv}')
        return success, data.get('message', 'Thành công') if success else data.get('message', 'Lỗi')

    def import_students(self, file_path: str) -> Tuple[bool, Dict]:
        """POST /admin/sinhvien/import - Nhập sinh viên từ file Excel/CSV"""
        try:
            with open(file_path, 'rb') as f:
                files = {'file': (file_path.split('/')[-1], f)}
                url = f"{self.base_url}/admin/sinhvien/import"
                response = self.session.post(url, files=files, timeout=TIMEOUT)
                
                if response.ok:
                    return True, response.json()
                else:
                    return False, {"message": f"Lỗi {response.status_code}: {response.text}"}
        except Exception as e:
            return False, {"message": str(e)}
    
    # ============= GIẢNG VIÊN =============
    
    def get_all_teachers(self) -> Tuple[bool, List[Dict]]:
        """GET /giangvien - Lấy danh sách tất cả giảng viên"""
        success, data = self._request('GET', '/giangvien')
        return success, data.get('data', []) if success else []
    
    def get_teacher(self, ma_gv: str) -> Tuple[bool, Dict]:
        """GET /giangvien/<ma_gv> - Lấy thông tin một giảng viên"""
        success, data = self._request('GET', f'/giangvien/{ma_gv}')
        return success, data.get('data', {}) if success else {}
    
    def create_teacher(self, teacher_data: Dict) -> Tuple[bool, str]:
        """POST /giangvien - Tạo giảng viên mới"""
        success, data = self._request('POST', '/giangvien', json=teacher_data)
        return success, data.get('message', 'Thành công') if success else data.get('message', 'Lỗi')
    
    def update_teacher(self, ma_nguoi_dung: str, teacher_data: Dict) -> Tuple[bool, str]:
        """PUT /admin/giangvien/<ma_nguoi_dung> - Cập nhật thông tin giảng viên"""
        success, data = self._request('PUT', f'/admin/giangvien/{ma_nguoi_dung}', json=teacher_data)
        return success, data.get('message', 'Thành công') if success else data.get('message', 'Lỗi')
    
    def delete_teacher(self, ma_gv: str) -> Tuple[bool, str]:
        """DELETE /giangvien/<ma_gv> - Xóa giảng viên"""
        success, data = self._request('DELETE', f'/giangvien/{ma_gv}')
        return success, data.get('message', 'Thành công') if success else data.get('message', 'Lỗi')

    def get_teacher_schedule(self, teacher_id: str, from_date: str = None, to_date: str = None) -> Tuple[bool, List[Dict]]:
        """GET /giangvien/<teacher_id>/lichday - Lấy lịch dạy của giảng viên"""
        params = {}
        if from_date:
            params['from_date'] = from_date
        if to_date:
            params['to_date'] = to_date
        success, data = self._request('GET', f'/giangvien/{teacher_id}/lichday', params=params)
        return success, data.get('data', []) if success else []

    def get_teacher_classes(self, teacher_id: str) -> Tuple[bool, List[Dict]]:
        """GET /giangvien/lophocphan/<teacher_id> - Lấy các lớp học của giảng viên"""
        success, data = self._request('GET', f'/giangvien/lophocphan/{teacher_id}')
        return success, data.get('data', []) if success else []

    def get_teacher_class_students(self, class_id: str) -> Tuple[bool, List[Dict]]:
        """GET /giangvien/lophocphan/<class_id>/sinhvien - Lấy danh sách sinh viên của lớp học phần (cho giảng viên)"""
        success, data = self._request('GET', f'/giangvien/lophocphan/{class_id}/sinhvien')
        return success, data.get('data', []) if success else []
    
    # ============= THÔNG TIN CÁ NHÂN =============
    
    def get_personal_info(self, ma_nguoi_dung: str) -> Tuple[bool, Dict]:
        """GET /taikhoan/<ma_nguoi_dung> - Lấy thông tin cá nhân"""
        success, data = self._request('GET', f'/taikhoan/{ma_nguoi_dung}')
        return success, data.get('data', {}) if success else {}
    
    def update_personal_info(self, ma_nguoi_dung: str, info_data: Dict) -> Tuple[bool, str]:
        """PUT /taikhoan/<ma_nguoi_dung> - Cập nhật thông tin cá nhân"""
        success, data = self._request('PUT', f'/taikhoan/{ma_nguoi_dung}', json=info_data)
        return success, data.get('message', 'Thành công') if success else data.get('message', 'Lỗi')

    def change_password(self, ma_nguoi_dung: str, mat_khau_cu: str, mat_khau_moi: str) -> Tuple[bool, str]:
        """PUT /doimatkhau - Đổi mật khẩu"""
        payload = {
            'ma_nguoi_dung': ma_nguoi_dung,
            'mat_khau_cu': mat_khau_cu,
            'mat_khau_moi': mat_khau_moi
        }
        success, data = self._request('PUT', '/doimatkhau', json=payload)
        return success, data.get('message', 'Thành công') if success else data.get('message', 'Lỗi')
    
    # ============= LỚP HỌC PHẦN =============
    
    def get_all_classes(self) -> Tuple[bool, List[Dict]]:
        """GET /lophocphan - Lấy danh sách tất cả lớp học phần"""
        success, data = self._request('GET', '/lophocphan')
        return success, data.get('data', []) if success else []
    
    def get_class(self, ma_lhp: str) -> Tuple[bool, Dict]:
        """GET /lophocphan/<ma_lhp> - Lấy thông tin một lớp học phần"""
        success, data = self._request('GET', f'/lophocphan/{ma_lhp}')
        return success, data.get('data', {}) if success else {}
    
    def create_class(self, class_data: Dict) -> Tuple[bool, str]:
        """POST /lophocphan - Tạo lớp học phần mới"""
        success, data = self._request('POST', '/lophocphan', json=class_data)
        return success, data.get('message', 'Thành công') if success else data.get('message', 'Lỗi')
    
    def update_class(self, ma_lhp: str, class_data: Dict) -> Tuple[bool, str]:
        """PUT /lophocphan/<ma_lhp> - Cập nhật lớp học phần"""
        success, data = self._request('PUT', f'/lophocphan/{ma_lhp}', json=class_data)
        return success, data.get('message', 'Thành công') if success else data.get('message', 'Lỗi')
    
    def delete_class(self, ma_lhp: str) -> Tuple[bool, str]:
        """DELETE /lophocphan/<ma_lhp> - Xóa lớp học phần"""
        success, data = self._request('DELETE', f'/lophocphan/{ma_lhp}')
        return success, data.get('message', 'Thành công') if success else data.get('message', 'Lỗi')
    
    def get_all_admin_classes(self) -> Tuple[bool, List[Dict]]:
        """GET /lophanhchinh - Lấy danh sách tất cả lớp hành chính"""
        success, data = self._request('GET', '/lophanhchinh')
        return success, data.get('data', []) if success else []

    def get_admin_class(self, ma_lop: str) -> Tuple[bool, Dict]:
        """GET /lophanhchinh/<ma_lop> - Lấy thông tin một lớp hành chính"""
        success, data = self._request('GET', f'/lophanhchinh/{ma_lop}')
        return success, data.get('data', {}) if success else {}

    def create_admin_class(self, class_data: Dict) -> Tuple[bool, str]:
        """POST /lophanhchinh - Tạo lớp hành chính mới"""
        success, data = self._request('POST', '/lophanhchinh', json=class_data)
        return success, data.get('message', 'Thành công') if success else data.get('message', 'Lỗi')

    def update_admin_class(self, ma_lop: str, class_data: Dict) -> Tuple[bool, str]:
        """PUT /lophanhchinh/<ma_lop> - Cập nhật lớp hành chính"""
        success, data = self._request('PUT', f'/lophanhchinh/{ma_lop}', json=class_data)
        return success, data.get('message', 'Thành công') if success else data.get('message', 'Lỗi')

    def delete_admin_class(self, ma_lop: str) -> Tuple[bool, str]:
        """DELETE /lophanhchinh/<ma_lop> - Xóa lớp hành chính"""
        success, data = self._request('DELETE', f'/lophanhchinh/{ma_lop}')
        return success, data.get('message', 'Thành công') if success else data.get('message', 'Lỗi')

    def get_all_departments(self) -> Tuple[bool, List[Dict]]:
        """GET /khoa - Lấy danh sách tất cả các khoa"""
        success, data = self._request('GET', '/khoa')
        return success, data.get('data', []) if success else []

    # ============= MÔN HỌC =============

    def get_all_monhoc(self) -> Tuple[bool, List[Dict]]:
        """GET /monhoc - Lấy danh sách tất cả các môn học"""
        success, data = self._request('GET', '/monhoc')
        return success, data.get('data', []) if success else []

    def get_monhoc_detail(self, ma_mon_hoc: str) -> Tuple[bool, Dict]:
        """GET /monhoc/<ma_mon_hoc> - Lấy thông tin một môn học"""
        success, data = self._request('GET', f'/monhoc/{ma_mon_hoc}')
        return success, data.get('data', {}) if success else {}

    def create_monhoc(self, monhoc_data: Dict) -> Tuple[bool, str]:
        """POST /monhoc - Tạo môn học mới"""
        success, data = self._request('POST', '/monhoc', json=monhoc_data)
        return success, data.get('message', 'Thành công') if success else data.get('message', 'Lỗi')

    def update_monhoc(self, ma_mon_hoc: str, monhoc_data: Dict) -> Tuple[bool, str]:
        """PUT /monhoc/<ma_mon_hoc> - Cập nhật môn học"""
        success, data = self._request('PUT', f'/monhoc/{ma_mon_hoc}', json=monhoc_data)
        return success, data.get('message', 'Thành công') if success else data.get('message', 'Lỗi')

    def delete_monhoc(self, ma_mon_hoc: str) -> Tuple[bool, str]:
        """DELETE /monhoc/<ma_mon_hoc> - Xóa môn học"""
        success, data = self._request('DELETE', f'/monhoc/{ma_mon_hoc}')
        return success, data.get('message', 'Thành công') if success else data.get('message', 'Lỗi')


    def get_all_subjects(self) -> Tuple[bool, List[Dict]]:
        """GET /monhoc - Lấy danh sách tất cả các môn học"""
        success, data = self._request('GET', '/monhoc')
        return success, data.get('data', []) if success else []


    def get_department(self, department_id: str) -> Tuple[bool, Dict]:
        """GET /khoa/<id> - Lấy thông tin một khoa"""
        success, data = self._request('GET', f'/khoa/{department_id}')
        return success, data.get('data', {}) if success else {}

    def create_department(self, department_data: Dict) -> Tuple[bool, str]:
        """POST /khoa - Tạo khoa mới"""
        success, data = self._request('POST', '/khoa', json=department_data)
        return success, data.get('message', 'Thành công') if success else data.get('message', 'Lỗi')

    def update_department(self, department_id: str, department_data: Dict) -> Tuple[bool, str]:
        """PUT /khoa/<id> - Cập nhật thông tin khoa"""
        success, data = self._request('PUT', f'/khoa/{department_id}', json=department_data)
        return success, data.get('message', 'Thành công') if success else data.get('message', 'Lỗi')

    def delete_department(self, department_id: str) -> Tuple[bool, str]:
        """DELETE /khoa/<id> - Xóa một khoa"""
        success, data = self._request('DELETE', f'/khoa/{department_id}')
        return success, data.get('message', 'Thành công') if success else data.get('message', 'Lỗi')
    
    def assign_teacher_to_class(self, ma_lhp: str, ma_gv: str) -> Tuple[bool, str]:
        """PUT /lophocphan/gan-giangvien - Gán giảng viên cho lớp học phần"""
        success, data = self._request('PUT', '/lophocphan/gan-giangvien', 
                                      json={'ma_lhp': ma_lhp, 'ma_gv': ma_gv})
        return success, data.get('message', 'Thành công') if success else data.get('message', 'Lỗi')

    # ============= LỚP HỌC PHẦN - SINH VIÊN =============

    def get_students_in_class(self, class_id: str) -> Tuple[bool, List[Dict]]:
        """GET /lophocphan/<id>/sinhvien - Lấy danh sách sinh viên trong lớp"""
        success, data = self._request('GET', f'/lophocphan/{class_id}/sinhvien')
        return success, data.get('data', []) if success else []

    def add_student_to_class(self, class_id: str, student_id: str) -> Tuple[bool, str]:
        """POST /lophocphan/<id>/sinhvien - Thêm sinh viên vào lớp"""
        payload = {'ma_sinh_vien': student_id}
        success, data = self._request('POST', f'/lophocphan/{class_id}/sinhvien', json=payload)
        return success, data.get('message', 'Thành công') if success else data.get('message', 'Lỗi')

    def remove_student_from_class(self, class_id: str, student_id: str) -> Tuple[bool, str]:
        """DELETE /lophocphan/<id>/sinhvien/<student_id> - Xóa sinh viên khỏi lớp"""
        success, data = self._request('DELETE', f'/lophocphan/{class_id}/sinhvien/{student_id}')
        return success, data.get('message', 'Thành công') if success else data.get('message', 'Lỗi')

    def add_students_from_admin_class(self, class_id: str, admin_class_id: str) -> Tuple[bool, Dict]:
        """POST /dangky-hangloat - Thêm SV từ lớp hành chính."""
        payload = {
            'ma_lhp': class_id,
            'ma_lop_hc': admin_class_id
        }
        return self._request('POST', '/dangky-hangloat', json=payload)

    
    # ============= BUỔI HỌC =============
    
    def create_session(self, session_data: Dict) -> Tuple[bool, str]:
        """POST /buoihoc - Tạo buổi học mới"""
        success, data = self._request('POST', '/buoihoc', json=session_data)
        return success, data.get('message', 'Thành công') if success else data.get('message', 'Lỗi')
    
    def update_session(self, ma_buoi_hoc: int, session_data: Dict) -> Tuple[bool, str]:
        """PUT /buoihoc/<ma_buoi_hoc> - Cập nhật buổi học"""
        success, data = self._request('PUT', f'/buoihoc/{ma_buoi_hoc}', json=session_data)
        return success, data.get('message', 'Thành công') if success else data.get('message', 'Lỗi')

    def get_sessions(self, params: Dict = None) -> Tuple[bool, List[Dict]]:
        """GET /buoihoc - Lấy danh sách buổi học với các tham số lọc"""
        success, data = self._request('GET', '/buoihoc', params=params)
        return success, data.get('data', []) if success else []

    def get_session(self, ma_buoi_hoc: int) -> Tuple[bool, Dict]:
        """GET /buoihoc/<ma_buoi_hoc> - Lấy thông tin chi tiết một buổi học"""
        success, data = self._request('GET', f'/buoihoc/{ma_buoi_hoc}')
        return success, data.get('data', {}) if success else {}

    def delete_session(self, ma_buoi_hoc: int) -> Tuple[bool, str]:
        """DELETE /buoihoc/<ma_buoi_hoc> - Xóa một buổi học"""
        success, data = self._request('DELETE', f'/buoihoc/{ma_buoi_hoc}')
        return success, data.get('message', 'Thành công') if success else data.get('message', 'Lỗi')
    
    # ============= ĐIỂM DANH - PHIÊN =============
    
    def create_manual_attendance_session(self, ma_buoi_hoc: int, ma_code: str) -> Tuple[bool, Dict]:
        """POST /phien/tao-thu-cong - Tạo phiên điểm danh thủ công"""
        success, data = self._request('POST', '/phien/tao-thu-cong', 
                                      json={'ma_buoi_hoc': ma_buoi_hoc, 'ma_code': ma_code})
        return success, data if success else {}
    
    def create_qr_attendance_session(self, ma_buoi_hoc: int) -> Tuple[bool, Dict]:
        """POST /phien/tao-qr - Tạo phiên điểm danh QR, trả về QR image base64"""
        success, data = self._request('POST', '/phien/tao-qr', 
                                      json={'ma_buoi_hoc': ma_buoi_hoc})
        return success, data if success else {}

    # ============= ĐIỂM DANH - THỰC HIỆN =============

    def attend_by_code(self, student_code: str, attendance_code: str) -> Tuple[bool, Dict]:
        """POST /diemdanh/ma - Sinh viên điểm danh bằng mã"""
        payload = {'student_code': student_code, 'attendance_code': attendance_code}
        success, data = self._request('POST', '/diemdanh/ma', json=payload)
        return success, data if success else {}

    def attend_by_face(self, student_code: str, session_id: int, confidence: float) -> Tuple[bool, Dict]:
        """POST /diemdanh/khuonmat - Sinh viên điểm danh bằng nhận diện khuôn mặt"""
        payload = {'student_code': student_code, 'session_id': session_id, 'confidence': confidence}
        success, data = self._request('POST', '/diemdanh/khuonmat', json=payload)
        return success, data if success else {}

    def attend_manual(self, session_id: int, student_id: int, status: str, note: str = None) -> Tuple[bool, Dict]:
        """POST /diemdanh/thucong - Giảng viên điểm danh thủ công cho sinh viên"""
        payload = {'session_id': session_id, 'student_id': student_id, 'status': status, 'note': note}
        success, data = self._request('POST', '/diemdanh/thucong', json=payload)
        return success, data if success else {}

    def get_session_attendance(self, session_id: int) -> Tuple[bool, List[Dict]]:
        """GET /phien/<session_id>/danh-sach - Lấy danh sách điểm danh của buổi học"""
        success, data = self._request('GET', f'/phien/{session_id}/danh-sach')
        return success, data.get('data', []) if success else []

    def get_attendance_stats(self, session_id: int) -> Tuple[bool, Dict]:
        """GET /buoihoc/<session_id>/thongke - Lấy thống kê điểm danh của buổi học"""
        success, data = self._request('GET', f'/buoihoc/{session_id}/thongke')
        return success, data if success else {}
    
    # ============= NHẬN DIỆN KHUÔN MẶT =============
    
    def recognize_face(self, image_base64: str) -> Tuple[bool, Dict]:
        """POST /khuon-mat/nhan-dien - Nhận diện khuôn mặt từ image base64"""
        success, data = self._request('POST', '/khuon-mat/nhan-dien', 
                                      json={'image': image_base64})
        return success, data if success else {}
    
    def register_face(self, student_code: str, images: List[bytes]) -> Tuple[bool, str]:
        """POST /khuon-mat/upload-anh - Đăng ký khuôn mặt (multipart upload)"""
        files = [('files', (f'image_{i}.jpg', img, 'image/jpeg')) for i, img in enumerate(images)]
        data = {'student_code': student_code}
        success, response_data = self._request('POST', '/khuon-mat/upload-anh', 
                                               data=data, files=files)
        return success, response_data.get('message', 'Thành công') if success else response_data.get('message', 'Lỗi')
    
    def get_registered_faces(self) -> Tuple[bool, List[Dict]]:
        """GET /khuon-mat/danh-sach - Lấy danh sách sinh viên đã đăng ký khuôn mặt"""
        success, data = self._request('GET', '/khuon-mat/danh-sach')
        return success, data.get('data', []) if success else []
    
    def delete_face(self, student_code: str) -> Tuple[bool, str]:
        """DELETE /khuon-mat/<student_code> - Xóa khuôn mặt"""
        success, data = self._request('DELETE', f'/khuon-mat/{student_code}')
        return success, data.get('message', 'Thành công') if success else data.get('message', 'Lỗi')
    
    def get_face_status(self) -> Tuple[bool, Dict]:
        """GET /khuon-mat/trang-thai - Kiểm tra trạng thái hệ thống nhận diện"""
        success, data = self._request('GET', '/khuon-mat/trang-thai')
        return success, data if success else {}
    
    # ============= BÁOCAO - ADMIN =============
    
    def get_admin_report_overall_attendance(self, filters: Optional[Dict] = None) -> Tuple[bool, Dict]:
        """GET /baocao/tonghop-chuyen-can - Báo cáo tổng hợp chuyên cần toàn bộ lớp"""
        params = filters or {}
        success, data = self._request('GET', '/baocao/tonghop-chuyen-can', params=params)
        if success:
            return success, {'data': data.get('data', [])}
        return success, {}
    
    def get_admin_report_teacher_attendance(self) -> Tuple[bool, List[Dict]]:
        """GET /baocao/chuyencan-giangvien - Báo cáo tỷ lệ chuyên cần trung bình của giảng viên"""
        success, data = self._request('GET', '/baocao/chuyencan-giangvien')
        return success, data.get('data', []) if success else []
    
    def get_admin_report_absent_students(self, threshold: int = 3) -> Tuple[bool, List[Dict]]:
        """GET /baocao/sinhvien-vang-qua-muc - Danh sách sinh viên vượt quá số buổi vắng cho phép"""
        success, data = self._request('GET', '/baocao/sinhvien-vang-qua-muc', 
                                      params={'threshold': threshold})
        return success, data.get('data', []) if success else []
    
    def get_admin_report_session_stats(self) -> Tuple[bool, Dict]:
        """GET /baocao/thong-ke-buoi-hoc-diem-danh - Thống kê số buổi học và điểm danh"""
        success, data = self._request('GET', '/baocao/thong-ke-buoi-hoc-diem-danh')
        if success:
            return success, {'data': data.get('data', {})}
        return success, {}
    
    def get_admin_report_pie_chart(self) -> Tuple[bool, Dict]:
        """GET /baocao/bieu-do-tron-ty-le-chuyen-can - Biểu đồ tròn tỷ lệ chuyên cần"""
        success, data = self._request('GET', '/baocao/bieu-do-tron-ty-le-chuyen-can')
        if success:
            return success, {'data': data.get('data', {})}
        return success, {}
    
    def get_admin_report_exam_eligible(self) -> Tuple[bool, List[Dict]]:
        """GET /baocao/danh-sach-du-kien-du-thi - Danh sách sinh viên đủ điều kiện dự thi"""
        success, data = self._request('GET', '/baocao/danh-sach-du-kien-du-thi')
        return success, data.get('data', []) if success else []
    
    def get_admin_report_compare_departments(self) -> Tuple[bool, List[Dict]]:
        """GET /baocao/so-sanh-ty-le-chuyen-can-khoa - So sánh tỷ lệ chuyên cần giữa các khoa"""
        success, data = self._request('GET', '/baocao/so-sanh-ty-le-chuyen-can-khoa')
        return success, data.get('data', []) if success else []
    
    def get_admin_report_audit_log(self) -> Tuple[bool, List[Dict]]:
        """GET /baocao/lich-su-chinh-sua - Lịch sử chỉnh sửa dữ liệu điểm danh"""
        success, data = self._request('GET', '/baocao/lich-su-chinh-sua')
        return success, data.get('data', []) if success else []

    def get_admin_overview_stats(self) -> Tuple[bool, Dict]:
        """GET /baocao/tongquan - Lấy thống kê tổng quan cho admin"""
        success, data = self._request('GET', '/baocao/tongquan')
        return success, data.get('data', {}) if success else {}


    
    # ============= BÁOCAO - GIẢNG VIÊN =============
    
    def get_teacher_report_student_attendance(self, ma_lhp: str) -> Tuple[bool, List[Dict]]:
        """GET /giangvien/baocao/chuyen-can-sinh-vien/<ma_lhp> - Thống kê tỷ lệ chuyên cần từng sinh viên"""
        success, data = self._request('GET', f'/giangvien/baocao/chuyen-can-sinh-vien/{ma_lhp}')
        return success, data.get('data', []) if success else []
    
    def get_teacher_report_attendance_list(self, ma_lhp: str) -> Tuple[bool, List[Dict]]:
        """GET /giangvien/baocao/danh-sach-diem-danh-buoi-hoc/<ma_lhp> - Danh sách điểm danh theo buổi học"""
        success, data = self._request('GET', f'/giangvien/baocao/danh-sach-diem-danh-buoi-hoc/{ma_lhp}')
        return success, data.get('data', []) if success else []
    
    def get_teacher_report_trend(self, ma_lhp: str) -> Tuple[bool, Dict]:
        """GET /giangvien/baocao/xu-huong-chuyen-can/<ma_lhp> - Xu hướng chuyên cần theo tuần/tháng"""
        success, data = self._request('GET', f'/giangvien/baocao/xu-huong-chuyen-can/{ma_lhp}')
        return success, data.get('data', {}) if success else {}
    
    def get_teacher_report_special_students(self, ma_lhp: str, loai: str = 'cao') -> Tuple[bool, List[Dict]]:
        """GET /giangvien/baocao/sinh-vien-dac-biet/<ma_lhp> - Sinh viên cao nhất/thấp nhất"""
        success, data = self._request('GET', f'/giangvien/baocao/sinh-vien-dac-biet/{ma_lhp}', params={'loai': loai})
        return success, data.get('data', []) if success else []
    
    def get_teacher_report_consolidated(self, ma_gv: str) -> Tuple[bool, List[Dict]]:
        """GET /giangvien/baocao/tong-hop-chuyen-can/<ma_gv> - Báo cáo tổng hợp chuyên cần"""
        success, data = self._request('GET', f'/giangvien/baocao/tong-hop-chuyen-can/{ma_gv}')
        return success, data.get('data', []) if success else []
    
    def get_teacher_report_warning(self, ma_lhp: str) -> Tuple[bool, List[Dict]]:
        """GET /giangvien/baocao/canh-bao-cam-thi/<ma_lhp> - Cảnh báo cấm thi"""
        success, data = self._request('GET', f'/giangvien/baocao/canh-bao-cam-thi/{ma_lhp}')
        return success, data.get('data', []) if success else []

    
    # ============= BÁOCAO - SINH VIÊN =============
    
    def get_student_attendance_history(self, ma_sv: str) -> Tuple[bool, List[Dict]]:
        """GET /sinhvien/lich-su-diem-danh/<ma_sv> - Lịch sử điểm danh cá nhân"""
        success, data = self._request('GET', f'/sinhvien/lich-su-diem-danh/{ma_sv}')
        return success, data.get('data', []) if success else []
    
    def get_student_attendance_stats(self, ma_sv: str) -> Tuple[bool, Dict]:
        """GET /sinhvien/thong-ke-chuyen-can/<ma_sv> - Thống kê tỷ lệ chuyên cần (%)"""
        success, data = self._request('GET', f'/sinhvien/thong-ke-chuyen-can/{ma_sv}')
        return success, data if success else {}
    
    def get_student_attendance_warning(self, ma_sv: str) -> Tuple[bool, Dict]:
        """GET /sinhvien/canh-bao-chuyen-can/<ma_sv> - Cảnh báo nếu tỷ lệ dưới mức quy định"""
        success, data = self._request('GET', f'/sinhvien/canh-bao-chuyen-can/{ma_sv}')
        return success, data if success else {}

    # ============= ĐIỂM DANH - GIẢNG VIÊN =============
    
    def create_manual_attendance_session(self, ma_buoi_hoc: int, ma_code: str) -> Tuple[bool, Dict]:
        """POST /phien/tao-thu-cong - Tạo phiên điểm danh bằng mã"""
        payload = {'ma_buoi_hoc': ma_buoi_hoc, 'ma_code': ma_code}
        success, data = self._request('POST', '/phien/tao-thu-cong', json=payload)
        return success, data if success else {}
    
    def create_qr_attendance_session(self, ma_buoi_hoc: int) -> Tuple[bool, Dict]:
        """POST /phien/tao-qr - Tạo phiên điểm danh QR và trả về ảnh QR"""
        payload = {'ma_buoi_hoc': ma_buoi_hoc}
        success, data = self._request('POST', '/phien/tao-qr', json=payload)
        if success:
            return success, {'message': data.get('message', 'Tạo QR thành công'), 'qr_image': data.get('qr_image_url'), 'ma_phien': data.get('ma_phien'), 'qr_link': data.get('qr_link')}
        return success, data
    
    def attend_by_code(self, student_code: str, attendance_code: str) -> Tuple[bool, Dict]:
        """POST /diemdanh/nhap-ma - Điểm danh bằng mã"""
        payload = {'ma_code': attendance_code, 'ma_sv': student_code}
        success, data = self._request('POST', '/diemdanh/nhap-ma', json=payload)
        return success, data if success else {}
    
    def attend_by_face(self, student_code: str, ma_buoi_hoc: int, confidence: float) -> Tuple[bool, Dict]:
        """POST /diemdanh/khuon-mat - Điểm danh bằng khuôn mặt"""
        payload = {'ma_sv': student_code, 'ma_buoi_hoc': ma_buoi_hoc, 'do_tin_cay': confidence}
        success, data = self._request('POST', '/diemdanh/khuon-mat', json=payload)
        return success, data if success else {}
    
    def attend_manual(self, ma_buoi_hoc: int, student_id: str, status: str, note: str = None) -> Tuple[bool, Dict]:
        """POST /diemdanh/thu-cong - Điểm danh thủ công"""
        payload = {'ma_buoi_hoc': ma_buoi_hoc, 'ma_sv': student_id, 'trang_thai': status}
        if note:
            payload['ghi_chu'] = note
        success, data = self._request('POST', '/diemdanh/thu-cong', json=payload)
        return success, data if success else {}
    
    def end_attendance_session(self, ma_phien: int) -> Tuple[bool, Dict]:
        """POST /phien/<ma_phien>/ket-thuc - Kết thúc phiên điểm danh"""
        success, data = self._request('POST', f'/phien/{ma_phien}/ket-thuc')
        return success, data if success else {}
    
    def make_request(self, endpoint: str, method: str = 'GET', **kwargs) -> Dict:
        """Thực hiện HTTP request generic (tương thích với legacy code)"""
        success, data = self._request(method, endpoint, **kwargs)
        return data if success else {}
    
    def download_file(self, endpoint: str, filename: str) -> Tuple[bool, str]:
        """Tải file từ API"""
        try:
            url = f"{self.base_url}{endpoint}"
            response = self.session.get(url, timeout=TIMEOUT, stream=True)
            
            if response.ok:
                from pathlib import Path
                downloads_dir = Path.home() / "Downloads"
                downloads_dir.mkdir(parents=True, exist_ok=True)
                
                file_path = downloads_dir / filename
                with open(file_path, 'wb') as f:
                    f.write(response.content)
                
                return True, str(file_path)
            else:
                logger.error(f"Download error {response.status_code}: {response.text}")
                return False, f"Lỗi {response.status_code}"
        except Exception as e:
            logger.error(f"Download error: {e}")
            return False, str(e)


_api_client = None


def get_api_client() -> APIClient:
    """Lấy instance singleton của APIClient"""
    global _api_client
    if _api_client is None:
        _api_client = APIClient()
    return _api_client
