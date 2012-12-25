from flask import Flask
from flask_peewee.db import Database
from peewee import *
from flask_peewee.admin import Admin

MEDIA_ROOT = ''
DATABASE = {
    'name': 'wth.db',
    'engine': 'peewee.SqliteDatabase',
}
DEBUG = True
SECRET_KEY = 'tr(*xbvnzx)bq07&+z^-s()+qad-1zl$4*&!oh%_eloyb@_=dk'

app = Flask(__name__)
app.config.from_object(__name__)

db = Database(app)

from wth.models import *

auth = CustomAuth(app, db)
admin = Admin(app, auth)
admin.register(School)
admin.register(SchoolClass)
admin.register(Teacher)
admin.register(User, UserAdmin)
admin.register(HomeworkAssignment)
admin.setup()

import wth.views
