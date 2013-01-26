from wth import app, auth
from flask import request, jsonify, make_response
import base64

# for queries being eval()'d:
from wth import db
from wth.models import StudentClass, HomeworkAssignment
from pytz import utc
import datetime
import itertools


@app.route('/user/login/', methods=['POST'])
def login():
    user = auth.authenticate(request.form['username'],
                             request.form['password'])
    if user:
        auth.login_user(user)
        resp = make_response()
        resp.status_code = 200
        return resp
    else:
        resp = make_response("bad_user_or_pass", 200)
        return resp


@app.route('/user/logout/')
def logout():
    if auth.get_logged_in_user():
        auth.logout_user()

    resp = make_response()
    resp.status_code = 200
    return resp


@app.route('/user/verify_logged_in/')
def verify_logged_in():
    if auth.get_logged_in_user():
        resp = make_response()
        resp.status_code = 200
        return resp
    else:
        resp = make_response()
        resp.status_code = 400
        return resp


@app.route('/user/motd/')
def motd():
    if auth.get_logged_in_user():
        return auth.get_logged_in_user().username
    else:
        resp = make_response()
        resp.status_code = 400
        return resp


@app.route('/user/classes/')
def user_classes():
    classes = [c for c in StudentClass.select().where(
        StudentClass.student == auth.get_logged_in_user().id)]
    data = {}
    for c in classes:
        data[c.school_class.id] = c.school_class.title
    resp = jsonify(data)
    resp.status_code = 200
    return resp


def process_assignments(assignments, reverse=False):
    # reverse should change the numbering of the counter to work backwards
    # because the assignments need to be prepended to an array in the app
    # ONLY for <latest_pk> methods

    data = {'assignments': [{}]}

    if len(assignments) > 15:
        data['assignments'][0][15] = 'true'
        resp = jsonify(data)
        resp.status_code = 200
        return resp

    if reverse:
        counter = 0
    else:
        counter = len(assignments) - 1

    for assignment in assignments:
        if assignment.thumbnail:
            with open(assignment.thumbnail, 'rb') as f:
                thumbnail = base64.b64encode(f.read())
        else:
            thumbnail = 'None'

        data['assignments'][0][counter] = {
            'pk': assignment.id,
            'poster': assignment.poster.username,
            'thumbnail': thumbnail,
            'date_assigned': str(assignment.date_assigned),
            'date_due': str(assignment.date_due),
            'description': assignment.description
        }
        if reverse:
            counter += 1
        else:
            counter -= 1

    resp = jsonify(data)
    resp.status_code = 200
    return resp


@app.route('/news/new/all/')
def news_feed():
    # get list of classes of logged in user
    classes = [c for c in StudentClass.select().where(
        StudentClass.student == auth.get_logged_in_user().id)]

    # builds query:
    # SELECT * FROM HomeworkAssignment
    # WHERE school_class = 1
    # OR school_class = 2...
    query = 'HomeworkAssignment.select().where('
    for i in xrange(0, len(classes)):
        query += '(HomeworkAssignment.school_class == ' + \
            'classes[' + str(i) + '])'
        if i != (len(classes) - 1):
            query += ' | '
        else:
            query += ')'

    assignments = [a for a in eval(query)]
    assignments.sort(key=lambda a: a.id)
    assignments = assignments[-15:]
    return process_assignments(assignments)


# UNTESTED for multiple studentclasses
@app.route('/news/new/all/<latest_pk>/')
def update_news_feed(latest_pk):
    classes = [c for c in StudentClass.select().where(
        StudentClass.student == auth.get_logged_in_user().id)]

    # SELECT * FROM HomeworkAssignment
    # WHERE school_class = 1 & id > 123
    # OR school_class = 2 & id > 123...
    query = 'HomeworkAssignment.select().where('
    for i in xrange(0, len(classes)):
        query += '(HomeworkAssignment.school_class == ' + \
            'classes[' + str(i) + ']) & (HomeworkAssignment.id > ' + str(latest_pk) + ')'
        if i != (len(classes) - 1):
            query += ' | '
        else:
            query += ')'

    assignments = [a for a in eval(query)]
    # if len(assignments) > 15:
    #     clear_feed_data = {'assignments': [{'clear_feed':0}]}
    #     resp = jsonify(clear_feed_data)
    #     return resp
    # else:
    assignments.sort(key=lambda a: a.id, reverse=True)
    return process_assignments(assignments)


@app.route('/news/old/all/<oldest_pk>/')
def older_news_feed(oldest_pk):

    classes = [c for c in StudentClass.select().where(
        StudentClass.student == auth.get_logged_in_user().id)]

    # SELECT * FROM HomeworkAssignment
    # WHERE school_class = 1 & id < 123
    # OR school_class = 2 & id < 123...
    query = 'HomeworkAssignment.select().where('
    for i in xrange(0, len(classes)):
        query += '(HomeworkAssignment.school_class == ' + \
            'classes[' + str(i) + ']) & (HomeworkAssignment.id < ' + str(oldest_pk) + ')'
        if i != (len(classes) - 1):
            query += ' | '
        else:
            query += ')'

    # import ipdb;ipdb.set_trace()

    assignments = [a for a in eval(query)]
    assignments.sort(key=lambda a: a.id)
    assignments = assignments[-15:]
    return process_assignments(assignments)


# @app.route('/news/new/id/<class_id>/')
# def class_feed(class_id):

#     assignments = [a for a in HomeworkAssignment.select().where(
#         HomeworkAssignment.school_class == class_id)]
#     assignments.sort(key=lambda a: a.id)
#     assignments = assignments[-15:]

#     return process_assignments(assignments)


# @app.route('/news/new/id/<class_id>/<latest_pk>/')
# def update_class_feed(class_id, latest_pk):

#     assignments = [a for a in HomeworkAssignment.select().where((HomeworkAssignment.school_class == class_id) & (HomeworkAssignment.id > latest_pk))]
#     assignments.sort(key=lambda a: a.id, reverse=True)
#     if len(assignments) > 15:
#         clear_feed_data = {'assignments': [{'0':{'clear_feed':'true'}}]}
#         resp = jsonify(clear_feed_data)
#         return resp
#     else:
#         assignments.sort(key=lambda a: a.id, reverse=True)
#         return process_assignments(assignments)


# @app.route('/news/old/id/<class_id>/<oldest_pk>/')
# def older_class_feed(class_id, oldest_pk):

#     assignments = [a for a in HomeworkAssignment.select().where((
#         HomeworkAssignment.school_class == class_id) & (HomeworkAssignment.id < oldest_pk))]
#     assignments.sort(key=lambda a: a.id, reverse=True)
#     assignments = assignments[-15:]
#     return process_assignments(assignments)
