from services.api_service import get_api_client
import logging

logger = logging.getLogger(__name__)


class TeacherAPIHelper:
    
    @staticmethod
    def load_classes_by_teacher(ma_gv: str):
        """Tải danh sách lớp học của giảng viên"""
        try:
            api = get_api_client()
            success, classes = api._request('GET', f'/giangvien/lophocphan/{ma_gv}')
            
            if not success:
                logger.error(f"Lỗi tải lớp học: {classes}")
                return []
            
            return classes.get('data', [])  # Trả trực tiếp snake_case
        
        except Exception as e:
            logger.error(f"Exception tải lớp học: {e}")
            return []
    
    @staticmethod
    def load_students_in_class(ma_lhp: str):
        """Tải danh sách sinh viên trong lớp"""
        try:
            api = get_api_client()
            success, students = api._request('GET', f'/lophocphan/{ma_lhp}/sinhvien')
            
            if not success:
                logger.error(f"Lỗi tải sinh viên lớp: {students}")
                return []
            
            return students.get('data', [])  # Trả trực tiếp snake_case
        
        except Exception as e:
            logger.error(f"Exception tải sinh viên: {e}")
            return []
    
    @staticmethod
    def create_manual_attendance(ma_buoi_hoc: int, ma_code: str):
        """Tạo phiên điểm danh thủ công (nhập mã)"""
        try:
            api = get_api_client()
            success, data = api.create_manual_attendance_session(ma_buoi_hoc, ma_code)
            
            if success:
                return True, data
            else:
                return False, data
        
        except Exception as e:
            logger.error(f"Exception tạo phiên điểm danh: {e}")
            return False, {"message": str(e)}
    
    @staticmethod
    def create_qr_attendance(ma_buoi_hoc: int):
        """Tạo phiên điểm danh QR"""
        try:
            api = get_api_client()
            success, data = api.create_qr_attendance_session(ma_buoi_hoc)
            
            if success:
                return True, data
            else:
                return False, data
        
        except Exception as e:
            logger.error(f"Exception tạo mã QR: {e}")
            return False, {"message": str(e)}
    
    @staticmethod
    def get_teacher_reports(ma_gv: str, ma_lhp: str = None):
        """Lấy dữ liệu báo cáo giảng viên"""
        try:
            api = get_api_client()
            reports = {}
            
            if ma_lhp:
                success, students = api.get_teacher_report_student_attendance(ma_lhp)
                reports['student_attendance'] = students if success else []
                
                success, sessions = api.get_teacher_report_session_attendance(ma_lhp)
                reports['session_attendance'] = sessions if success else []
                
                success, trend = api.get_teacher_report_attendance_trend(ma_lhp)
                reports['attendance_trend'] = trend if success else {}
                
                success, special = api.get_teacher_report_special_students(ma_lhp)
                reports['special_students'] = special if success else []
                
                success, warning = api.get_teacher_report_exam_warning(ma_lhp)
                reports['exam_warning'] = warning if success else []
            
            success, overall = api.get_teacher_report_overall_attendance(ma_gv)
            reports['overall_attendance'] = overall if success else []
            
            return reports
        
        except Exception as e:
            logger.error(f"Exception tải báo cáo: {e}")
            return {}
