# services/academic_service.py
from config import USE_DUMMY_DATA
from data.dummy_academic_provider import DummyAcademicProvider
from data.real_academic_provider import RealAcademicProvider

class AcademicService:
    """Service layer routing requests to either Dummy or Real Academic Provider."""

    def __init__(self):
        if USE_DUMMY_DATA:
            self.provider = DummyAcademicProvider()
        else:
            self.provider = RealAcademicProvider()

    # Routine
    def get_routines(self, user_id):
        return self.provider.get_routines(user_id)

    def add_routine(self, user_id, course_title, day_of_week, start_time, end_time):
        return self.provider.add_routine(user_id, course_title, day_of_week, start_time, end_time)

    def delete_routine(self, routine_id):
        return self.provider.delete_routine(routine_id)

    # Assignments
    def get_assignments(self, user_id):
        return self.provider.get_assignments(user_id)

    def add_assignment(self, user_id, title, deadline):
        return self.provider.add_assignment(user_id, title, deadline)

    def mark_assignment_completed(self, assignment_id):
        return self.provider.mark_assignment_completed(assignment_id)

    def delete_assignment(self, index_or_id):
        return self.provider.delete_assignment(index_or_id)

    # Class Tests
    def get_class_tests(self, user_id):
        return self.provider.get_class_tests(user_id)

    def add_class_test(self, user_id, exam_title, exam_date):
        return self.provider.add_class_test(user_id, exam_title, exam_date)

    def delete_class_test(self, index_or_id):
        return self.provider.delete_class_test(index_or_id)


