# data/dummy_academic_provider.py

class DummyAcademicProvider:
    """In-memory data store for testing Class Routine, Assignments, and Class Tests UI."""

    routines = [
        {"routine_id": 1, "course_title": "CSE 2100", "day_of_week": "Monday", "start_time": "08:00 AM", "end_time": "09:30 AM"},
        {"routine_id": 2, "course_title": "CSE 2101", "day_of_week": "Wednesday", "start_time": "10:00 AM", "end_time": "11:30 AM"},
    ]

    assignments = [
        {"course_title": "CSE 2100", "title": "Database Project Schema", "deadline": "2026-09-15", "completed": False},
        {"course_title": "CSE 2101", "title": "Data Structures Lab 3", "deadline": "2026-09-20", "completed": False},
    ]

    class_tests = [
        {"course_title": "CSE 2100", "exam_title": "CT-1 Systems", "exam_date": "2026-09-25"},
        {"course_title": "CSE 2101", "exam_title": "Midterm Exam", "exam_date": "2026-10-05"},
    ]

    # --- CLASS ROUTINE ---
    def get_routines(self, user_id):
        return self.routines

    def add_routine(self, user_id, course_title, day_of_week, start_time, end_time):
        new_id = len(self.routines) + 1
        self.routines.append({
            "routine_id": new_id,
            "course_title": course_title,
            "day_of_week": day_of_week,
            "start_time": start_time,
            "end_time": end_time
        })
        return True

    def delete_routine(self, routine_id):
        self.routines = [r for r in self.routines if r["routine_id"] != routine_id]
        return True

    # --- ASSIGNMENTS ---
    def get_assignments(self, user_id):
        return self.assignments

    def add_assignment(self, user_id, title, deadline):
        course_code = title.split(" - ")[0].strip() if " - " in title else "CSE 2100"
        self.assignments.append({
            "course_title": course_code,
            "title": title,
            "deadline": deadline,
            "completed": False
        })
        return True

    def mark_assignment_completed(self, assignment_id):
        return True

    def delete_assignment(self, index):
        if isinstance(index, int) and 0 <= index < len(self.assignments):
            self.assignments.pop(index)
        return True

    # --- CLASS TESTS ---
    def get_class_tests(self, user_id):
        return self.class_tests

    def add_class_test(self, user_id, exam_title, exam_date):
        course_code = exam_title.split(" - ")[0].strip() if " - " in exam_title else "CSE 2100"
        self.class_tests.append({
            "course_title": course_code,
            "exam_title": exam_title,
            "exam_date": exam_date
        })
        return True

    def delete_class_test(self, index):
        if isinstance(index, int) and 0 <= index < len(self.class_tests):
            self.class_tests.pop(index)
        return True


