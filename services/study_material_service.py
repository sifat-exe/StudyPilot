import os
import shutil
from services.profile_service import ProfileService
from Database.database import (
    get_study_materials_by_user,
    add_study_material,
    delete_study_material
)

BASE_MATERIALS_DIR = os.path.join(os.getcwd(), "study_materials")


class StudyMaterialService:

    def __init__(self):
        self.profile_service = ProfileService()
        self._ensure_storage_dir()

    def _ensure_storage_dir(self):
        os.makedirs(BASE_MATERIALS_DIR, exist_ok=True)

    def get_user_courses(self, user_id):
        return self.profile_service.get_courses(user_id)

    def get_course_labels(self, user_id):
        return self.profile_service.get_course_labels(user_id)

    def get_materials(self, user_id):
        return get_study_materials_by_user(user_id)

    def upload_material(self, user_id, course_id, source_file_path, course_code=""):
        if not source_file_path or not os.path.exists(source_file_path):
            raise FileNotFoundError("Selected PDF file does not exist.")

        user_key = str(user_id) if user_id is not None else "guest"
        course_key = str(course_id) if course_id is not None else "general"

        target_dir = os.path.join(
            BASE_MATERIALS_DIR,
            f"user_{user_key}",
            f"course_{course_key}"
        )

        os.makedirs(target_dir, exist_ok=True)

        file_name = os.path.basename(source_file_path)
        target_file_path = os.path.join(target_dir, file_name)

        shutil.copy2(source_file_path, target_file_path)

        material_id = add_study_material(
            user_id,
            course_id,
            file_name,
            os.path.abspath(target_file_path)
        )

        material = {
            "material_id": material_id,
            "user_id": user_id,
            "course_id": course_id,
            "course_code": course_code,
            "file_name": file_name,
            "file_path": os.path.abspath(target_file_path)
        }

        return {
            "success": True,
            "material": material
        }

    def delete_material(self, material_id):
        return delete_study_material(material_id)