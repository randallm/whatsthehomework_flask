from flask import Flask
from flask_peewee.db import Database
from peewee import *
from flask_peewee.admin import Admin

app = Flask(__name__)
app.config.from_object('wth.config')

db = Database(app)

from wth.models import *

auth = CustomAuth(app, db)
admin = Admin(app, auth)
admin.register(School)
admin.register(SchoolClass)
admin.register(Teacher)
admin.register(User, UserAdmin)
admin.register(HomeworkAssignment)
admin.register(StudentClass)
admin.setup()

import wth.views
