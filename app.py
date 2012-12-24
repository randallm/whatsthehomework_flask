# TODO:
# * migrate to github issues tracker
# * set limits on charfields
# * move to postgres
# * grab secret key from environment variable
# * fragment app.py into multiple files (be wary of constants like MEDIA_ROOT)

from flask import Flask, request
from flask_peewee.db import Database
from flask_peewee.auth import Auth, BaseUser
from flask_peewee.admin import Admin, ModelAdmin
from flask_peewee.rest import RestAPI, UserAuthentication, RestResource, RestrictOwnerResource
from peewee import *
from pytz import utc
import datetime
import subprocess


DATABASE = {
    'name': 'wth.db',
    'engine': 'peewee.SqliteDatabase',
}
DEBUG = True
SECRET_KEY = 'tr(*xbvnzx)bq07&+z^-s()+qad-1zl$4*&!oh%_eloyb@_=dk'

app = Flask(__name__)
app.config.from_object(__name__)

db = Database(app)


@app.route('/login/', methods=['POST'])
def login():
    user = auth.authenticate(request.form['username'],
                             request.form['password'])
    if user:
        auth.login_user(user)
        print 'hello', user.username
        return "hello"
    else:
        print 'invalidlogin'
        return "wrong"


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


class User(db.Model, BaseUser):
    username = CharField()  # need limits
    password = CharField()
    email = CharField()  # need validation

    admin = BooleanField(default=True)  # DANGEROUS
    active = BooleanField(default=True)

    school = ForeignKeyField(School)


class UserAdmin(ModelAdmin):
    columns = ('username', 'email', 'admin')


class CustomAuth(Auth):
    def get_user_model(self):
        return User

    def get_model_admin(self):
        return UserAdmin


class HomeworkAssignment(db.Model):
    school_class = ForeignKeyField(SchoolClass)
    poster = ForeignKeyField(User)
    photo = CharField(default='None')

    date_posted = DateTimeField(default=datetime.datetime.utcnow() \
                                        .replace(tzinfo=utc))
    date_assigned = DateTimeField(default=datetime.datetime.utcnow() \
                                          .replace(tzinfo=utc))

    description = TextField(max_length=1000)

    def save_photo(self, file_obj):
        self.photo = os.path.join(MEDIA_ROOT, self.id + '.jpg')
        self.save()

    def delete_photo(self):
        # Popen() is called because proc.wait() time is too long
        subprocess.Popen(['rm', self.photo])  # DANGEROUS, untested

auth = CustomAuth(app, db)
admin = Admin(app, auth)
admin.register(School)
admin.register(SchoolClass)
admin.register(Teacher)
admin.register(User, UserAdmin)
admin.register(HomeworkAssignment)
admin.setup()

@app.route('/testperms/')
@auth.login_required
def private():
    # import ipdb;ipdb.set_trace()
    return auth.get_logged_in_user().username
    # return auth.get_logged_in_user().username, auth.get_logged_in_user().password
    # print auth.get_logged_in_user().username, auth.get_logged_in_user().password

if __name__ == '__main__':
    auth.User.create_table(fail_silently=True)
    School.create_table(fail_silently=True)
    SchoolClass.create_table(fail_silently=True)
    Teacher.create_table(fail_silently=True)
    HomeworkAssignment.create_table(fail_silently=True)
    app.run(host='0.0.0.0')
