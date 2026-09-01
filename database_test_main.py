from database.database import (
    create_tables,
    add_user,
    add_course,
    add_assignment,
    add_exam,
    add_study_session,
    add_study_plan,
    add_class_routine,
    delete_class_routine,
    update_class_routine,
    complete_assignment,
    complete_study_session,
    complete_study_plan,
    get_users,
    get_courses,
    get_assignments,
    get_exams,
    get_assignments_with_courses,
    get_exams_with_courses,
    get_study_sessions,
    get_total_study_time,
    get_study_plans,
    get_study_plans_with_courses,
    get_course_study_time,
    get_completed_assignment_count,
    get_completed_study_plan_count,
    get_upcoming_assignments,
    get_upcoming_exams,
    add_availability,
    get_availability,
    get_class_routines,
)


# Create database tables
create_tables()


# # # =========================
# # # TEST USER
# # # =========================

# # add_user(
# #     "Sifat",
# #     "sifat@example.com"
# # )


# # =========================
# # TEST COURSES
# # =========================

# add_course(
#     1,
#     "CSE 2201",
#     "Object Oriented Programming",
#     "Hard",
#     3
# )

# add_course(
#     1,
#     "CSE 2103",
#     "Digital Logic Design",
#     "Hard",
#     3
# )


# # =========================
# # TEST ASSIGNMENTS
# # =========================

# add_assignment(
#     1,
#     "OOP Assignment 1",
#     "2026-09-05"
# )

# add_assignment(
#     2,
#     "DLD Assignment 1",
#     "2026-09-08"
# )


# # =========================
# # TEST EXAMS
# # =========================

# add_exam(
#     1,
#     "OOP Final Exam",
#     "2026-10-15"
# )

# add_exam(
#     2,
#     "DLD Final Exam",
#     "2026-10-20"
# )


# # =========================
# # DISPLAY USERS
# # =========================

# print("\nUSERS:")

# users = get_users()

# for user in users:
#     print(user)


# # =========================
# # DISPLAY COURSES
# # =========================

# print("\nCOURSES:")

# courses = get_courses()

# for course in courses:
#     print(course)


# # =========================
# # DISPLAY ASSIGNMENTS
# # =========================

# print("\nASSIGNMENTS:")

# assignments = get_assignments()

# for assignment in assignments:
#     print(assignment)


# # =========================
# # DISPLAY EXAMS
# # =========================

# print("\nEXAMS:")

# exams = get_exams()

# for exam in exams:
#     print(exam)


# # =========================
# # ASSIGNMENTS + COURSES
# # =========================

# print("\nASSIGNMENTS WITH COURSES:")

# assignments = get_assignments_with_courses()

# for assignment in assignments:
#     print(assignment)


# # =========================
# # EXAMS + COURSES
# # =========================

# print("\nEXAMS WITH COURSES:")

# exams = get_exams_with_courses()

# for exam in exams:
#     print(exam)


# add_study_session(
#     2,
#     "2026-08-31",
#     120
# )

# print("Study session added")



# sessions = get_study_sessions()

# for session in sessions:
#     print(session)

# complete_study_session(1)
# complete_study_session(2)
# complete_study_session(3)

# total=get_total_study_time()

# print(total)

# add_study_plan(2,"31-8-26",120,"DSA Practise")

# plans=get_study_plans_with_courses()

# for plan in plans :
#     print(plan)

# print("after")

# complete_study_plan(3)

# for plan in plans :
#     print(plan)

# total=get_course_study_time(2)

# print(total)

# complete_assignment(1)
# complete_assignment(2)
# count=get_completed_assignment_count()

# print(count)


# print(get_completed_study_plan_count())

# print(get_upcoming_assignments())

# exams = get_upcoming_exams()

# for exam in exams :
#     print(exam)


# add_availability(
#     1,
#     "Monday",
#     "18:00",
#     "22:00"
# )

# add_availability(
#     1,
#     "Tuesday",
#     "19:00",
#     "22:00"
# )

# availability = get_availability(1)

# for item in availability:
#     print(item)


# add_class_routine(
#     1,2,"Saturday","8.50am","10.30am"
# )

# add_class_routine(
#     2,1,"sunday","2.30pm","5.00pm"
# )

# delete_class_routine(2)

# update_class_routine(
#     3,1,"Saturday","2.30pm", "5.00pm"
# )

# routines= get_class_routines(1)

# for routine in routines:
#     print(routine)