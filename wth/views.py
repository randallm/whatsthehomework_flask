from wth import app, auth
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
    # import ipdb;ipdb.set_trace()
    return auth.get_logged_in_user().username
    # return app.auth.get_logged_in_user().username, app.auth.get_logged_in_user().password
    # print app.auth.get_logged_in_user().username, app.auth.get_logged_in_user().password

# @app.route('/login/', methods=['POST'])
# @app.route('/hw/news, methods=['POST'])
# @app.auth.login_required
# def post_assignment():
