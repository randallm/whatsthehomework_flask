from flask import Flask
from flask_peewee.db import Database
# from peewee import *
from flask_peewee.admin import Admin
from datetime import timedelta
from wth.securecookie import ItsdangerousSessionInterface

app = Flask(__name__)
app.config.from_object('wth.config')

app.session_interface = ItsdangerousSessionInterface()
# session.permanent = True (already set in auth.py)
app.permanent_session_lifetime = timedelta(minutes=9999999)

db = Database(app)

from wth.models import *

auth = CustomAuth(app, db)
# admin = Admin(app, auth)
# admin.setup()

import wth.views
