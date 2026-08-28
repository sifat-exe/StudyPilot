from database.database import create_tables, add_user, get_users ,add_course,get_courses


create_tables()


#add_user("Sifat", "sifat@example.com")


# add_course(
#     1,
#     "CSE 2201",
#     "Object Oriented Programming",
#     "Hard",
#     3
# )

# users = get_users()

for user in users:
    print(user)

courses = get_courses()

for course in courses:
    print(course)