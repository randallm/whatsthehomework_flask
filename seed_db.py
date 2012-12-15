from app import auth, School

school = School(name='Albany High School', abbreviation='AHS')
school.save()

user = auth.User(username='admin',
                 real_name='Randall Ma',
                 is_admin=True,
                 active=True,
                 email='example@example.com',
                 school=School.get(id=1))
user.set_password('password')
user.save()