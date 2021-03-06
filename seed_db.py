from wth import auth, app, School, SchoolClass, HomeworkAssignment, StudentClass
from pytz import utc
import datetime
import os


def init_school():
    school = School(name='School for Troubled Treats', abbreviation='STT')
    school.save()


def init_admin():
    user = auth.User(username='admin',
                     real_name='Randall Ma',
                     is_admin=True,
                     active=True,
                     email='example@example.com',
                     school=School.get(id=1))
    user.set_password('password')
    user.save()


def init_school_class():
    school_class = SchoolClass(title='Crumpets 2013-2014 AP Tastiness',
                               school=School.get(id=1))
    school_class.save()


def init_student_class():
    student_class = StudentClass(student=auth.User.get(id=1),
                                 school_class=SchoolClass.get(id=1))
    student_class.save()


def add_more_assignments(assignments=20):
    for i in xrange(0, assignments):
        time_offset = datetime.timedelta(minutes=i * 2)
        now = datetime.datetime.utcnow().replace(tzinfo=utc)
        fake_now = now + time_offset

        hw_assignment = HomeworkAssignment(school_class=SchoolClass.get(id=1),
                                           poster=auth.User.get(id=1),
                                           date_posted=fake_now,
                                           date_due=fake_now + datetime.timedelta(days=1),
                                           description="Lorum ipsum dolor python; ruby c lua javascript cubone pikachu charmander bicycle races are coming your way! When u were young u were the King of Carrot Flowers. :)",
                                           thumbnail=os.path.join(app.config['MEDIA_ROOT'], 't1.jpg'))
        hw_assignment.save()


if __name__ == '__main__':
    auth.User.create_table(fail_silently=True)
    School.create_table(fail_silently=True)
    SchoolClass.create_table(fail_silently=True)
    HomeworkAssignment.create_table(fail_silently=True)
    StudentClass.create_table(fail_silently=True)

    init_school()
    init_admin()
    init_school_class()
    init_student_class()
    add_more_assignments()
