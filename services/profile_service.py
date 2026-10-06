# services/profile_service.py
from config import USE_DUMMY_DATA
from data.dummy_profile_provider import DummyProfileProvider
from data.real_profile_provider import RealProfileProvider


class ProfileService:
    """UI-facing profile/course API. Database work stays in providers."""

    def __init__(self):
        if USE_DUMMY_DATA:
            self.provider = DummyProfileProvider()
        else:
            self.provider = RealProfileProvider()

    def get_profile(self, user_id):
        return self.provider.get_profile(user_id)

    def save_profile(self, user_id, profile):
        return self.provider.save_profile(user_id, profile)

    def get_courses(self, user_id):
        return self.provider.get_courses(user_id)

    def get_course_labels(self, user_id):
        """Labels for CT / Assignments / Routine dropdowns: 'CODE - Name'."""
        courses = self.get_courses(user_id)
        labels = []
        for course in courses:
            code = (course.get("course_code") or "").strip()
            title = (course.get("course_title") or "").strip()
            if not code:
                continue
            labels.append(f"{code} - {title}" if title else code)
        return labels
