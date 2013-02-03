from wth import app, auth
from flask import request, jsonify, make_response
from wth.models import StudentClass, SchoolClass, School
from wth.humanize_date import humanize_date
import lepl.apps.rfc3696
import base64
import os
import re
import calendar

# for queries being eval()'d:
from wth import db
from wth.models import HomeworkAssignment
from pytz import utc
import datetime
import itertools


@app.route('/user/login/', methods=['POST'])
def login():
    required_fields = ['username', 'password']
    for field in required_fields:
        if not request.form[field]:
            resp = make_response('missing_' + field)
            resp.status_code = 400
            return resp

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


@app.route('/user/new_student/', methods=['POST'])
def user_new_student():
    required_fields = ['username', 'real_name', 'email', 'school_id', 'password']
    for field in required_fields:
        if not request.form[field]:
            resp = make_response('missing_' + field)
            resp.status_code = 501
            return resp

    username = request.form['username']
    if auth.User.get(username=username):
        resp = make_response('duplicate_username')
        resp.status_code = 501
        return resp
    if not re.match(r'^[a-z0-9_-]{3,20}$', username):
        # lowercase alphanumeric, hyphens/underscores, 3-20 chars
        resp = make_response('invalid_username')
        resp.status_code = 501
        return resp

    password = request.form['password']
    if not re.match(r'^.{6,30}$', password):
        # wildcard 6-30 chars
        resp = make_response('invalid_password')
        resp.status_code = 501
        return resp

    email = request.form['email']
    if auth.User.get(email=email):
        resp = make_response('duplicate_email')
        resp.status_code = 501
        return resp
    email_validator = lepl.apps.rfc3696.Email()
    if not email_validator(email):
        resp = make_response('invalid_email')
        resp.status_code = 501
        return resp

    real_name = request.form['username']
    school_id = int(request.form['school_id'])

    user = auth.User(username=username,
                     real_name=real_name,
                     is_admin=False,
                     active=True,
                     email=email,
                     school=School.get(id=school_id))
    user.set_password(password)
    user.save()

    resp = make_response()
    resp.status_code = 200
    return resp


@app.route('/user/add_class/', methods=['POST'])
def user_add_class():
    student_class = StudentClass(student=auth.get_logged_in_user(),
                                 school_class=SchoolClass.get(id=request.form['school_class']))
    student_class.save()

    resp = make_response()
    resp.status_code = 200
    return resp


@app.route('/user/new_class/', methods=['POST'])
def user_new_class():
    school_class = SchoolClass(title=request.form['title'],
                               school=School.get(id=request.form['school']))
    school_class.save()

    resp = make_response()
    resp.status_code = 200
    return resp


@app.route('/hw/new_assignment/', methods=['POST'])
def hw_new_assignment():
    # this probably isn't going to work: you should think it out before actually testing this
    # new_assignment = str([a for a in HomeworkAssignment.select()][-1].id + 1) + '.jpg'
    # with open(os.path.join(app.config['MEDIA_ROOT'], new_assignment), 'w') as f:
        # f.write(request.form['b64_photo'])

    hw = HomeworkAssignment(school_class=SchoolClass.get(id=request.form['class']),
                            poster=auth.get_logged_in_user())
    if request.form['b64_photo']:
        hw.save_photo(request.form['b64_photo'])
    hw.save()

    resp = make_response()
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

    def unicode_to_human_time(u):
        DATETIME_FORMAT = '%Y-%m-%d %H:%M:%S.%f'
        return datetime.datetime.strptime(u[:-6], DATETIME_FORMAT)  # strip tzinfo

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
            'date_posted': humanize_date(unicode_to_human_time(assignment.date_posted)),
            'date_due': humanize_date(unicode_to_human_time(assignment.date_posted)),
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
