# data/real_academic_provider.py
from database.database import (
    get_class_routines, add_class_routine, update_class_routine, delete_class_routine,
    get_assignments_with_courses, add_assignment, complete_assignment, delete_assignment,
    get_exams_with_courses, add_exam, delete_exam,
    get_courses, add_course
)

class RealAcademicProvider:
    """Interacts with Sifat's database.py functions for Class Routine, Assignments, and Class Tests."""

    def _get_course_id_by_code(self, user_id, course_code):
        """Find existing course_id by course_code for this specific user. Creates one if not found."""
        courses = get_courses()
        for c in courses:
            # c = (course_id, user_id, course_code, course_title, difficulty, credit_hours)
            if c[1] == user_id and c[2] == course_code:
                return c[0]
        
        # If course_code not found for user_id, create it under user_id
        add_course(user_id, course_code, course_code, "Medium", 3)
        courses = get_courses()
        for c in courses:
            if c[1] == user_id and c[2] == course_code:
                return c[0]
        return None

    # --- CLASS ROUTINE ---
    def get_routines(self, user_id):
        routines = get_class_routines(user_id)
        return [
            {
                "routine_id": r[0],
                "course_title": r[1],
                "day_of_week": r[2],
                "start_time": r[3],
                "end_time": r[4]
            }
            for r in routines
        ]

    def add_routine(self, user_id, course_title, day_of_week, start_time, end_time):
        course_code = course_title.split(" - ")[0].split(" (")[0].strip()
        course_id = self._get_course_id_by_code(user_id, course_code)
        if course_id:
            add_class_routine(user_id, course_id, day_of_week, start_time, end_time)
        return True

    def delete_routine(self, routine_id):
        delete_class_routine(routine_id)
        return True

    # --- ASSIGNMENTS ---
    def get_assignments(self, user_id):
        all_assignments = get_assignments_with_courses(user_id)
        # Returns list of dicts: (course_code, title, deadline, completed, assignment_id)
        return [
            {
                "assignment_id": a[4],
                "course_title": a[0],
                "title": a[1],
                "deadline": a[2],
                "completed": bool(a[3])
            }
            for a in all_assignments
        ]

    def add_assignment(self, user_id, title, deadline):
        course_code = title.split(" - ")[0].strip() if " - " in title else title
        course_id = self._get_course_id_by_code(user_id, course_code)
        if course_id:
            add_assignment(course_id, title, deadline)
        return True

    def mark_assignment_completed(self, assignment_id):
        complete_assignment(assignment_id)
        return True

    def delete_assignment(self, assignment_id):
        delete_assignment(assignment_id)
        return True

    # --- CLASS TESTS / EXAMS ---
    def get_class_tests(self, user_id):
        all_exams = get_exams_with_courses(user_id)
        # Returns list of dicts: (course_code, exam_title, exam_date, exam_id)
        return [
            {
                "exam_id": e[3],
                "course_title": e[0],
                "exam_title": e[1],
                "exam_date": e[2]
            }
            for e in all_exams
        ]

    def add_class_test(self, user_id, exam_title, exam_date):
        course_code = exam_title.split(" - ")[0].strip() if " - " in exam_title else exam_title
        course_id = self._get_course_id_by_code(user_id, course_code)
        if course_id:
            add_exam(course_id, exam_title, exam_date)
        return True

    def delete_class_test(self, exam_id):
        delete_exam(exam_id)
        return True
