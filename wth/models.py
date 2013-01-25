from wth import app, db
from peewee import CharField, ForeignKeyField, BooleanField, TextField, DateTimeField
from flask_peewee.auth import Auth, BaseUser
from flask_peewee.admin import ModelAdmin
from pytz import utc
import lepl.apps.rfc3696
import datetime
import subprocess
import os
import re


class School(db.Model):
    name = CharField(max_length=100)
    abbreviation = CharField(max_length=10)

    def __unicode__(self):
        return u'%s (%s)' % (self.name, self.abbreviation)


class Teacher(db.Model):
    last_name = CharField(max_length=30)

    def __unicode__(self):
        return u'%s' % (self.last_name)


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

    def __unicode__(self):
        return u'%s' % (self.title)


class User(db.Model, BaseUser):
    username = CharField()
    password = CharField()
    email = CharField(max_length=254)

    admin = BooleanField(default=False)
    active = BooleanField(default=True)

    school = ForeignKeyField(School)

    def validate_username(u):
        # lowercase alphanumeric, hyphens/underscores, 3-20 chars
        if not re.match(r'^[a-z0-9_-]{3,20}$', u):
            return 'bad_username'

    def validate_password(p):
        # wildcard 6-30 chars
        if not re.match(r'^.{6,30}$', p):
            return 'bad_password'

    def validate_email(e):
        email_validator = lepl.apps.rfc3696.Email()
        if not email_validator(e):
            return 'bad_email'


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
    photo = CharField(default='')
    thumbnail = CharField(default='')

    date_assigned = DateTimeField(default=datetime.datetime.utcnow() \
                                        .replace(tzinfo=utc))
    date_due = DateTimeField(default=datetime.datetime.utcnow() \
                                          .replace(tzinfo=utc) \
                                          + datetime.timedelta(days=3))

    description = TextField(max_length=1000,
                            default='')

    def save_photo(self, file_obj):
        self.photo = os.path.join(app.config['MEDIA_ROOT'], self.id + '.jpg')
        self.thumbnail = os.path.join(app.config['MEDIA_ROOT'], 't' + self.id + '.jpg')
        self.save()

    def delete_photo(self):
        # Popen() is called because proc.wait() time is too long
        subprocess.Popen(['rm', self.photo])  # DANGEROUS, untested

    def __unicode__(self):
        return u'%s - %s' % (self.poster.username, self.school_class.title)


class StudentClass(db.Model):
    student = ForeignKeyField(User)
    school_class = ForeignKeyField(SchoolClass)
