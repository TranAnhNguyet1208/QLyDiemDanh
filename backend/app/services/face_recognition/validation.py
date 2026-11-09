import re


def validate_name(name: str) -> tuple[bool, str]:
    if not name or not name.strip():
        return False, "Tên không được để trống"
    
    words = name.strip().split()
    
    if len(words) < 2:
        return False, "Họ tên phải có ít nhất 2 từ"
    
    for word in words:
        if not word.isalpha():
            return False, "Họ tên chỉ được chứa chữ cái"
    
    return True, ""


def validate_student_id(student_id: str) -> tuple[bool, str]:
    if not student_id or not student_id.strip():
        return False, "Mã sinh viên không được để trống"
    
    student_id = student_id.strip()
    
    if not re.match(r'^[a-zA-Z0-9]+$', student_id):
        return False, "Mã sinh viên chỉ được chứa chữ cái và số, không có ký tự đặc biệt"
    
    return True, ""


def validate_input(name: str, student_id: str) -> tuple[bool, str]:
    is_valid, error = validate_name(name)
    if not is_valid:
        return False, error
    
    is_valid, error = validate_student_id(student_id)
    if not is_valid:
        return False, error
    
    return True, ""
