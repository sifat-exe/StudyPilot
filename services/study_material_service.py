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

    def delete_material(self, material_or_id):
        """
        Deletes a study material:
          1. Removes AI analysis records from DB (pdf_analyses & topic_summaries).
          2. Removes study_materials DB record.
          3. Removes the physical PDF file from disk.
        """
        if isinstance(material_or_id, dict):
            material_id = material_or_id.get("material_id")
            file_path = material_or_id.get("file_path")
        else:
            material_id = material_or_id
            file_path = None

        if material_id:
            try:
                from Database.database import delete_pdf_analysis
                delete_pdf_analysis(material_id)
            except Exception as e:
                print(f"[StudyMaterialService] Error deleting PDF analysis: {e}")

            delete_study_material(material_id)

        if file_path and os.path.exists(file_path):
            try:
                os.remove(file_path)
            except Exception as e:
                print(f"[StudyMaterialService] Error removing PDF file: {e}")

        return True


    def get_analysis(self, material_id: int):
        from Database.database import get_pdf_analysis
        return get_pdf_analysis(material_id)

    def save_analysis(self, material_id: int, result):
        from Database.database import save_pdf_analysis
        from services.ai_provider import is_valid_summary_text

        if not result or not getattr(result, "success", False) or not getattr(result, "topics", None):
            return None

        valid_topics = []
        for t in result.topics:
            title = getattr(t, "title", "") or (t.get("title") if isinstance(t, dict) else "")
            summary = getattr(t, "summary", "") or (t.get("summary") if isinstance(t, dict) else "")
            key_points = getattr(t, "key_points", []) if hasattr(t, "key_points") else (t.get("key_points", []) if isinstance(t, dict) else [])
            order_index = getattr(t, "order_index", 1) if hasattr(t, "order_index") else (t.get("order_index", 1) if isinstance(t, dict) else 1)

            if is_valid_summary_text(summary):
                valid_topics.append({
                    "title": title,
                    "summary": summary,
                    "key_points": key_points,
                    "order_index": order_index
                })

        if not valid_topics:
            print("[StudyMaterialService] No valid topic summaries to save; skipping DB save.")
            return None

        analysis_data = {
            "page_count": result.page_count,
            "extraction_method": result.extraction_method,
            "extracted_text": result.extracted_text,
            "meaningful_pages": result.meaningful_pages,
            "meaningful_ratio": result.meaningful_ratio,
            "topics": valid_topics
        }
        return save_pdf_analysis(material_id, analysis_data)

