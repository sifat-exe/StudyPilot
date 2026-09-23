# data/dummy_profile_provider.py
import copy


class DummyProfileProvider:
    """In-memory student profile for USE_DUMMY_DATA=True.

    This does not write to study_pilot.db. Set USE_DUMMY_DATA=False
    to save profile and courses in the database.
    """

    _profiles = {}

    def _empty_profile(self):
        return {
            "name": "",
            "university": "",
            "roll": "",
            "year": "1st",
            "semester": "Odd",
            "courses": [],
        }

    def get_profile(self, user_id):
        key = user_id if user_id is not None else "guest"
        if key not in DummyProfileProvider._profiles:
            DummyProfileProvider._profiles[key] = self._empty_profile()
        return copy.deepcopy(DummyProfileProvider._profiles[key])

    def save_profile(self, user_id, profile):
        key = user_id if user_id is not None else "guest"
        saved_courses = []
        next_id = 1
        for course in profile.get("courses", []):
            code = (course.get("course_code") or "").strip()
            title = (course.get("course_title") or "").strip()
            if not code and not title:
                continue
            saved_courses.append({
                "course_id": course.get("course_id") or next_id,
                "course_code": code,
                "course_title": title,
            })
            next_id += 1

        DummyProfileProvider._profiles[key] = {
            "name": (profile.get("name") or "").strip(),
            "university": (profile.get("university") or "").strip(),
            "roll": (profile.get("roll") or "").strip(),
            "year": profile.get("year") or "1st",
            "semester": profile.get("semester") or "Odd",
            "courses": saved_courses,
        }
        return True

    def get_courses(self, user_id):
        return self.get_profile(user_id).get("courses", [])
