from wth import auth, School, SchoolClass, Teacher, HomeworkAssignment, StudentClass
import datetime
from pytz import utc

auth.User.create_table()
School.create_table()
SchoolClass.create_table()
Teacher.create_table()
HomeworkAssignment.create_table()
StudentClass.create_table()

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

for i in xrange(0, 50):
    time_offset = datetime.timedelta(minutes=i * 2)
    now = datetime.datetime.utcnow().replace(tzinfo=utc)
    fake_now = now + time_offset

    hw_assignment = HomeworkAssignment(school_class=SchoolClass.get(id=1),
                                       poster=auth.User.get(id=1),
                                       date_posted=fake_now,
                                       date_due=fake_now + datetime.timedelta(days=1))
    hw_assignment.save()

student_class = StudentClass(student=auth.User.get(id=1),
                             school_class=SchoolClass.get(id=1))
student_class.save()
