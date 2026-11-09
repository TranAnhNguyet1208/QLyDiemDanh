from services.api_service import get_api_client
import logging
from typing import List, Dict

logger = logging.getLogger(__name__)

class AdminClassService:
    """Service for managing administrative classes (Lớp hành chính)."""
    
    def __init__(self):
        self.api_client = get_api_client()

    def get_all_admin_classes(self) -> List[Dict]:
        success, classes = self.api_client.get_all_admin_classes()
        if not success:
            logger.error("Failed to fetch administrative classes from API.")
            return []

        if isinstance(classes, dict):
            classes = classes.get("data", [])
        
        processed = []
        for row in classes:
            ma_lop = row.get('ma_lop_hanh_chinh')
            ten_lop = row.get('ten_lop_hanh_chinh')
            if ma_lop and ten_lop:
                processed.append({'ma_lop': ma_lop, 'ten_lop': ten_lop})
            else:
                logger.warning(f"Skipping malformed admin class data: {row}")
        
        return processed

    def get_admin_class(self, class_code: str) -> tuple[bool, Dict]:
        return self.api_client.get_admin_class(class_code)

    def create_admin_class(self, class_data: Dict) -> tuple[bool, str]:
        return self.api_client.create_admin_class(class_data)

    def update_admin_class(self, class_code: str, class_data: Dict) -> tuple[bool, str]:
        return self.api_client.update_admin_class(class_code, class_data)

    def delete_admin_class(self, class_code: str) -> tuple[bool, str]:
        return self.api_client.delete_admin_class(class_code)
