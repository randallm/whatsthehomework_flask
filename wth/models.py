from wth import app, db
from peewee import CharField, ForeignKeyField, BooleanField, TextField, DateTimeField
from flask_peewee.auth import Auth, BaseUser
from flask_peewee.admin import ModelAdmin
from pytz import utc
import datetime
import subprocess
import os
import base64


class School(db.Model):
    name = CharField(max_length=100)
    abbreviation = CharField(max_length=10)

    def __unicode__(self):
        return u'%s (%s)' % (self.name, self.abbreviation)


class SchoolClass(db.Model):
    title = CharField(max_length=150)
    # class_name = CharField(max_length=50)

    school = ForeignKeyField(School)

    # starting_year = IntegerField()
    # ending_year = IntegerField()

    # http://flask-peewee.readthedocs.org/en/latest/api.html?highlight=save#Mod
    # Ask about behavior of save_model() in IRC
    # def save_model(self, instance, form, adding=False):
    #     verbose_year = '(%i - %i)' % (form.starting_year,
    #                                   form.ending_year)

    #     class_details = [instance.school.abbreviation,
    #                      instance.class_name,
    #                      verbose_year]
    #     instance.title = ' '.join(class_details)

    #     super(SchoolClass, self).save(*args, **kwargs)

    def __unicode__(self):
        return u'%s' % (self.title)


class User(db.Model, BaseUser):
    username = CharField(unique=True)
    password = CharField()
    email = CharField(max_length=254, unique=True)

    admin = BooleanField(default=False)
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
    photo = CharField(default='')
    thumbnail = CharField(default='')

    date_assigned = DateTimeField(default=datetime.datetime.utcnow() \
                                        .replace(tzinfo=utc))
    date_due = DateTimeField(default=datetime.datetime.utcnow() \
                                          .replace(tzinfo=utc) \
                                          + datetime.timedelta(days=3))

    description = TextField(max_length=1000,
                            default='')

    def save_photo(self, b64_photo):
        with open(os.path.join(app.config['MEDIA_ROOT'], str(self.id) + '.jpg'), 'w') as f:
            ## TODO: PIL compress image
            f.write(base64.b64decode(b64_photo))

        with open(os.path.join(app.config['MEDIA_ROOT'], 't' + str(self.id) + '.jpg'), 'w') as f:
            ## TODO: PIL compress and resize image
            f.write(base64.b64decode(b64_photo))

        self.photo = os.path.join(app.config['MEDIA_ROOT'], self.id + '.jpg')
        self.thumbnail = os.path.join(app.config['MEDIA_ROOT'], 't' + self.id + '.jpg')
        self.save()

    def delete_photo(self):
        # Popen() is called because proc.wait() time is too long
        subprocess.Popen(['rm', self.photo])  # DANGEROUS, untested
        subprocess.Popen(['rm', self.thumbnail])

    def __unicode__(self):
        return u'%s - %s' % (self.poster.username, self.school_class.title)


class StudentClass(db.Model):
    student = ForeignKeyField(User)
    school_class = ForeignKeyField(SchoolClass)
