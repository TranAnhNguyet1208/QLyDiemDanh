from services.api_service import get_api_client
import logging

logger = logging.getLogger(__name__)


class AdminAPIHelper:
    
    @staticmethod
    def load_students():
        """Tải danh sách sinh viên từ API"""
        try:
            api = get_api_client()
            success, students = api.get_all_students()
            
            if not success:
                logger.error(f"Lỗi tải sinh viên: {students}")
                return []
            
            return students  # Trả trực tiếp snake_case
        
        except Exception as e:
            logger.error(f"Exception tải sinh viên: {e}")
            return []
    
    @staticmethod
    def load_teachers():
        """Tải danh sách giảng viên từ API"""
        try:
            api = get_api_client()
            success, teachers = api.get_all_teachers()
            
            if not success:
                logger.error(f"Lỗi tải giảng viên: {teachers}")
                return []
            
            return teachers
        
        except Exception as e:
            logger.error(f"Exception tải giảng viên: {e}")
            return []
    
    @staticmethod
    def load_classes():
        """Tải danh sách lớp học phần từ API"""
        try:
            api = get_api_client()
            success, classes = api.get_all_classes()
            
            if not success:
                logger.error(f"Lỗi tải lớp học: {classes}")
                return []
            
            return classes  # Trả trực tiếp snake_case
        
        except Exception as e:
            logger.error(f"Exception tải lớp học: {e}")
            return []
    
    @staticmethod
    def create_student(student_data):
        """Tạo sinh viên mới"""
        try:
            api = get_api_client()
            success, message = api.create_student(student_data)
            return success, message
        except Exception as e:
            logger.error(f"Exception tạo sinh viên: {e}")
            return False, str(e)
    
    @staticmethod
    def update_student(ma_nguoi_dung, student_data):
        """Cập nhật sinh viên"""
        try:
            api = get_api_client()
            success, message = api.update_student(ma_nguoi_dung, student_data)
            return success, message
        except Exception as e:
            logger.error(f"Exception cập nhật sinh viên: {e}")
            return False, str(e)
    
    @staticmethod
    def delete_student(ma_sv):
        """Xóa sinh viên"""
        try:
            api = get_api_client()
            success, message = api.delete_student(ma_sv)
            return success, message
        except Exception as e:
            logger.error(f"Exception xóa sinh viên: {e}")
            return False, str(e)
    
    @staticmethod
    def create_teacher(teacher_data):
        """Tạo giảng viên mới"""
        try:
            api = get_api_client()
            success, message = api.create_teacher(teacher_data)
            return success, message
        except Exception as e:
            logger.error(f"Exception tạo giảng viên: {e}")
            return False, str(e)
    
    @staticmethod
    def update_teacher(ma_nguoi_dung, teacher_data):
        """Cập nhật giảng viên"""
        try:
            api = get_api_client()
            success, message = api.update_teacher(ma_nguoi_dung, teacher_data)
            return success, message
        except Exception as e:
            logger.error(f"Exception cập nhật giảng viên: {e}")
            return False, str(e)
    
    @staticmethod
    def delete_teacher(ma_gv):
        """Xóa giảng viên"""
        try:
            api = get_api_client()
            success, message = api.delete_teacher(ma_gv)
            return success, message
        except Exception as e:
            logger.error(f"Exception xóa giảng viên: {e}")
            return False, str(e)
    
    @staticmethod
    def create_class(class_data):
        """Tạo lớp học phần mới"""
        try:
            api = get_api_client()
            success, message = api.create_class(class_data)
            return success, message
        except Exception as e:
            logger.error(f"Exception tạo lớp học: {e}")
            return False, str(e)
    
    @staticmethod
    def update_class(ma_lhp, class_data):
        """Cập nhật lớp học phần"""
        try:
            api = get_api_client()
            success, message = api.update_class(ma_lhp, class_data)
            return success, message
        except Exception as e:
            logger.error(f"Exception cập nhật lớp học: {e}")
            return False, str(e)
    
    @staticmethod
    def delete_class(ma_lhp):
        """Xóa lớp học phần"""
        try:
            api = get_api_client()
            success, message = api.delete_class(ma_lhp)
            return success, message
        except Exception as e:
            logger.error(f"Exception xóa lớp học: {e}")
            return False, str(e)
    
    @staticmethod
    def get_admin_reports():
        """Lấy dữ liệu các báo cáo admin"""
        try:
            api = get_api_client()
            reports = {}
            
            success, data = api.get_admin_report_overall_attendance()
            reports['overall_attendance'] = data if success else {}
            
            success, teachers = api.get_admin_report_teacher_attendance()
            reports['teacher_attendance'] = teachers if success else []
            
            success, students = api.get_admin_report_absent_students()
            reports['absent_students'] = students if success else []
            
            success, stats = api.get_admin_report_session_stats()
            reports['session_stats'] = stats if success else {}
            
            success, chart = api.get_admin_report_pie_chart()
            reports['pie_chart'] = chart if success else {}
            

            
            success, eligible = api.get_admin_report_exam_eligible()
            reports['exam_eligibility'] = eligible if success else []
            
            success, compare = api.get_admin_report_compare_departments()
            reports['compare_departments'] = compare if success else []
            
            success, audit = api.get_admin_report_audit_log()
            reports['audit_log'] = audit if success else []
            
            return reports
        
        except Exception as e:
            logger.error(f"Exception tải báo cáo: {e}")
            return {}
