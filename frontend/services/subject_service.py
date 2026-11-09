import requests
from services.api_service import get_api_client

class SubjectService:
    def __init__(self):
        self.api_client = get_api_client()

    def get_all_subjects(self):
        success, response = self.api_client.get_all_monhoc()
        if success:
            if isinstance(response, dict):
                return response.get("data", [])
            elif isinstance(response, list):
                return response
            else:
                return []
        return []

    def get_subject_by_code(self, subject_code):
        success, response = self.api_client.get_monhoc_detail(subject_code)
        if not success:
            return None
        return response

    def create_subject(self, subject_data):
        success, message = self.api_client.create_monhoc(subject_data)
        return success, message

    def update_subject(self, subject_code, subject_data):
        success, message = self.api_client.update_monhoc(subject_code, subject_data)
        return success, message

    def delete_subject(self, subject_code):
        success, message = self.api_client.delete_monhoc(subject_code)
        return success, message
