# services/study_material_service.py
"""
===============================================================================
COLLABORATION CONTRACT WITH SIFAT (Database Layer Developer)
===============================================================================

Sifat will implement the database layer and data providers for Study Materials separately.
The UI and StudyMaterialService layer expect the following database operations and data structures:

1. Expected Database Table Structure (in study_pilot.db):
   CREATE TABLE IF NOT EXISTS study_materials (
       material_id INTEGER PRIMARY KEY AUTOINCREMENT,
       user_id INTEGER NOT NULL,
       course_id INTEGER NOT NULL,
       file_name TEXT NOT NULL,
       file_path TEXT NOT NULL,
       uploaded_at TEXT NOT NULL,
       FOREIGN KEY (user_id) REFERENCES users(user_id),
       FOREIGN KEY (course_id) REFERENCES courses(course_id)
   );

2. Expected Provider / Database Functions to be implemented by Sifat in database.py:
   - get_study_materials(user_id) -> returns list of tuples / dicts
   - add_study_material(user_id, course_id, file_name, file_path) -> inserts record
   - delete_study_material(material_id) -> deletes record

3. Expected Data Structure returned for each material:
   {
       "material_id": int,
       "user_id": int,
       "course_id": int,
       "course_code": str,     # e.g., "CSE 2100"
       "file_name": str,       # e.g., "Lecture 01.pdf"
       "file_path": str,       # Absolute local path to PDF file
       "uploaded_at": str      # e.g., "2026-09-22 22:00:00"
   }

===============================================================================
"""

import os
import json
import shutil
from datetime import datetime
from services.profile_service import ProfileService

BASE_MATERIALS_DIR = os.path.join(os.getcwd(), "study_materials")
MANIFEST_PATH = os.path.join(BASE_MATERIALS_DIR, "materials_manifest.json")


class StudyMaterialService:
    """
    Service layer for Study Materials.
    Communicates with ProfileService for courses, copies uploaded PDFs to
    the dedicated `study_materials/user_<user_id>/course_<course_id>/` directory,
    and maintains local JSON persistence until Sifat implements the real DB provider.
    """

    def __init__(self):
        self.profile_service = ProfileService()
        self._ensure_storage_dir()

    def _ensure_storage_dir(self):
        os.makedirs(BASE_MATERIALS_DIR, exist_ok=True)
        if not os.path.exists(MANIFEST_PATH):
            self._save_manifest({})

    def _load_manifest(self):
        if not os.path.exists(MANIFEST_PATH):
            return {}
        try:
            with open(MANIFEST_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}

    def _save_manifest(self, data):
        try:
            with open(MANIFEST_PATH, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4)
        except Exception as e:
            print(f"[StudyMaterialService] Failed to save manifest: {e}")

    def get_user_courses(self, user_id):
        """Retrieves user's profile courses via ProfileService."""
        return self.profile_service.get_courses(user_id)

    def get_course_labels(self, user_id):
        """Retrieves course labels (e.g. 'CSE 2100 - Data Structures') for dropdowns."""
        return self.profile_service.get_course_labels(user_id)

    def get_materials(self, user_id):
        """
        Retrieves all study materials for a specific user from manifest.
        Returns a list of dictionaries.
        """
        key = str(user_id) if user_id is not None else "guest"
        manifest = self._load_manifest()
        return manifest.get(key, [])

    def upload_material(self, user_id, course_id, source_file_path, course_code=""):
        """
        Copies the source PDF into study_materials/user_<user_id>/course_<course_id>/
        and records its metadata in the manifest.
        """
        if not source_file_path or not os.path.exists(source_file_path):
            raise FileNotFoundError("Selected PDF file does not exist.")

        user_key = str(user_id) if user_id is not None else "guest"
        course_key = str(course_id) if course_id is not None else "general"

        # 1. Create dedicated user & course directory: study_materials/user_<id>/course_<id>/
        target_dir = os.path.join(BASE_MATERIALS_DIR, f"user_{user_key}", f"course_{course_key}")
        os.makedirs(target_dir, exist_ok=True)

        # 2. Copy PDF file to dedicated directory
        file_name = os.path.basename(source_file_path)
        target_file_path = os.path.join(target_dir, file_name)
        shutil.copy2(source_file_path, target_file_path)

        # 3. Update manifest persistence
        manifest = self._load_manifest()
        if user_key not in manifest:
            manifest[user_key] = []

        existing_user_materials = manifest[user_key]
        next_id = len(existing_user_materials) + 1

        material = {
            "material_id": next_id,
            "user_id": user_id,
            "course_id": course_id,
            "course_code": course_code,
            "file_name": file_name,
            "file_path": os.path.abspath(target_file_path),
            "uploaded_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

        existing_user_materials.append(material)
        self._save_manifest(manifest)

        return {"success": True, "material": material}


