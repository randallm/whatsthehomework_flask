from wth import app, auth
from wth.models import StudentClass
from flask import request


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


@app.route('/motd/')
@auth.login_required
def motd():
    if auth.get_logged_in_user():
        return auth.get_logged_in_user().username
    else:
        return 'False'


@app.route('/hw/news/', methods=['POST'])
@auth.login_required
def view_assignments():
    return [c for c in StudentClass.select().where(
                StudentClass == auth.User.get(request.form['username']))]
