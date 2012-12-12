from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.core.exceptions import ValidationError
from django.utils.timezone import utc
import datetime


class School(models.Model):
    name = models.CharField(max_length=100)
    abbreviation = models.CharField(max_length=10)

    def __unicode__(self):
        return u'%s (%s)' % (self.name, self.abbreviation)


class Teacher(models.Model):
    last_name = models.CharField(max_length=100)


class SchoolClass(models.Model):
    title = models.CharField(max_length=150)
    class_name = models.CharField(max_length=50)

    school = models.ForeignKey(School)
    teacher = models.ForeignKey(Teacher)
    starting_year = models.IntegerField(
        default=datetime.datetime.utcnow().year)
    ending_year = models.IntegerField(
        default=datetime.datetime.utcnow().year + 1)

    def clean(self):
        # validate ending year
        if self.ending_year < self.starting_year:
            raise ValidationError('Ending year cannot be before starting year')

    def save(self, *args, **kwargs):
        verbose_year = '(%i - %i)' % (self.starting_year, self.ending_year)

        class_details = [self.school.abbreviation,
                         self.teacher.last_name,
                         self.class_name,
                         verbose_year]
        self.title = ' '.join(class_details)

        super(SchoolClass, self).save(*args, **kwargs)


class HomeworkAssignment(models.Model):
    school_class = models.ForeignKey(SchoolClass)
    poster = models.ForeignKey(User)
    # photo = models.ImageField(upload_to='hwphotos/')

    date_posted = models.DateTimeField()
    date_assigned = models.DateTimeField()

    description = models.TextField(max_length=1000)  # space to transcribe dates or info from photo

    def save(self, *args, **kwargs):
        self.date_posted = datetime.datetime.utcnow().replace(tzinfo=utc)
        super(HomeworkAssignment, self).save(*args, **kwargs)


class UserProfile(models.Model):
    user = models.OneToOneField(User)
    school = models.ForeignKey(School)

    def __unicode__(self):
        return self.user.username


def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)
post_save.connect(create_user_profile, sender=User)
