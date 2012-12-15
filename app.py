from flask import Flask
from flask_peewee.db import Database
from flask_peewee.auth import Auth, BaseUser
from flask_peewee.admin import Admin, ModelAdmin
from flask_peewee.rest import RestAPI, UserAuthentication, RestResource, RestrictOwnerResource
from peewee import *
from pytz import utc
import datetime


DATABASE = {
    'name': 'wth.db',
    'engine': 'peewee.SqliteDatabase',
}
DEBUG = True
SECRET_KEY = 'tr(*xbvnzx)bq07&+z^-s()+qad-1zl$4*&!oh%_eloyb@_=dk'

app = Flask(__name__)
app.config.from_object(__name__)

db = Database(app)


class School(db.Model):
    name = CharField(max_length=100)
    abbreviation = CharField(max_length=10)

    def __unicode__(self):
        return u'%s (%s)' % (self.name, self.abbreviation)


class Teacher(db.Model):
    last_name = CharField(max_length=100)


class SchoolClass(db.Model):
    title = CharField(max_length=150)
    # class_name = CharField(max_length=50)

    school = ForeignKeyField(School)
    teacher = ForeignKeyField(Teacher)
    # starting_year = IntegerField()
    # ending_year = IntegerField()

    # http://flask-peewee.readthedocs.org/en/latest/api.html?highlight=save#Mod
    # Ask about behavior of save_model() in IRC
    # def save_model(self, instance, form, adding=False):
    #     verbose_year = '(%i - %i)' % (form.starting_year,
    #                                   form.ending_year)

    #     class_details = [instance.school.abbreviation,
    #                      instance.teacher.last_name,
    #                      instance.class_name,
    #                      verbose_year]
    #     instance.title = ' '.join(class_details)

    #     super(SchoolClass, self).save(*args, **kwargs)


# class HomeworkAssignment(db.Model):
#     school_class = ForeignKeyField(SchoolClass)
#     poster = ForeignKeyField(User)
#     # photo = ImageField(upload_to='hwphotos/')

#     date_posted = DateTimeField(default=datetime.datetime.utcnow() \
#                                         .replace(tzinfo=utc))
#     date_assigned = DateTimeField(default=datetime.datetime.utcnow() \
#                                           .replace(tzinfo=utc))

#     description = TextField(max_length=1000)

class User(db.Model, BaseUser):
    username = CharField(max_length=30)
    password = CharField(max_length=30)
    email = CharField()

    real_name = CharField()

    is_admin = BooleanField(default=False)
    active = BooleanField(default=True)

    school = ForeignKeyField(School)


class UserAdmin(ModelAdmin):
    columns = ('username', 'email', 'school')


# class UserResource(RestResource, RestrictOwnerResource):
#     exclude = ('password', 'email', 'username',)  # not all things excluded yet
#     owner_field = 'user'

class UserResource(RestResource):
    exclude = ('password', 'email', 'username',)  # not all things excluded yet


class CustomAuth(Auth):
    def get_user_model(self):
        return User

    def get_model_admin(self):
        return UserAdmin


class CustomAdmin(Admin):
    def check_user_permission(self, user):
        return user.is_admin

auth = CustomAuth(app, db)
admin = CustomAdmin(app, auth)
admin.register(School)
admin.register(SchoolClass)
admin.register(Teacher)
admin.register(User, UserAdmin)
admin.setup()

# user_auth = UserAuthentication(auth)
# api = RestAPI(app, default_auth=user_auth)
# api.register(School)
# api.register(SchoolClass)
# api.register(Teacher)
# api.register(User, UserResource)
# api.setup()

if __name__ == '__main__':
    auth.User.create_table(fail_silently=True)
    School.create_table(fail_silently=True)
    SchoolClass.create_table(fail_silently=True)
    Teacher.create_table(fail_silently=True)
    app.run(host='0.0.0.0')
