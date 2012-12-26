from wth import auth, School, SchoolClass, Teacher, HomeworkAssignment

auth.User.create_table(fail_silently=True)
School.create_table(fail_silently=True)
SchoolClass.create_table(fail_silently=True)
Teacher.create_table(fail_silently=True)
HomeworkAssignment.create_table(fail_silently=True)

school = School(name='School for Troubled Treats', abbreviation='STT')
school.save()

user = auth.User(username='admin',
                 real_name='Randall Ma',
                 is_admin=True,
                 active=True,
                 email='example@example.com',
                 school=School.get(id=1))
user.set_password('password')
user.save()

teacher = Teacher(last_name='Crumpets')
teacher.save()

school_class = SchoolClass(title='Crumpets 2013-2014 AP Tastiness',
                           school=School.get(id=1),
                           teacher=Teacher.get(id=1))
school_class.save()

hw_assignment = HomeworkAssignment(school_class=SchoolClass.get(id=1),
                                   poster=auth.User.get(id=1))
hw_assignment.save()
