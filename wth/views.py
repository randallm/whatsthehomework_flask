from wth import app, auth
from wth.models import StudentClass, HomeworkAssignment, SchoolClass
from flask import request, jsonify
import datetime
from pytz import utc
import itertools


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


def process_assignment_metadata(assignments):
    data = {}
    for assignment in assignments:
        data[str(assignment.date_posted)] = {
            'photo': assignment.get_photo_uri(),
            'date_due': str(assignment.date_due),
            'description': assignment.description
        }

    return data


@app.route('/hw/news/all/<page>/', methods=['GET', 'POST'])
@auth.login_required
def view_news_feed(page):

    def tomorrow():
        now = datetime.datetime.utcnow().replace(tzinfo=utc)
        day = datetime.timedelta(days=1)
        return now + day

    def paginate(iterable, page_size):
        while True:
            i1, i2 = itertools.tee(iterable)
            iterable, page = (itertools.islice(i1, page_size, None),
                    list(itertools.islice(i2, page_size)))
            if len(page) == 0:
                break
            yield page

    classes = [c for c in StudentClass.select().where(
        StudentClass.student.id == auth.get_logged_in_user().id)]

    assignments = []

    for c in classes:
        assignments.append(HomeworkAssignment.select().where(
            HomeworkAssignment.school_class == c and \
            HomeworkAssignment.date_due > tomorrow()))

    assignments.sort(key=lambda a: a.date_posted)

    assignments = list(paginate(assignments, 10))
    assignments = assignments[page]

    resp = jsonify(process_assignment_metadata(assignments))
    resp.status_code = 200
    return resp


@app.route('/hw/news/<class_id>/<page>/', methods=['POST'])
@auth.login_required
def view_class_assignments(class_id, page):
    school_class = SchoolClass.get(id=class_id)

    if StudentClass.get(student=auth.get_logged_in_user,
                        school_class=school_class):

        assignments = [a for a in HomeworkAssignment.select().where(HomeworkAssignment.school_class == school_class).order_by(HomeworkAssignment.date_posted).paginate(page, 10)]

        resp = jsonify(process_assignment_metadata(assignments))
        resp.status_code = 200
        return resp


@app.route('/hw/news/news/dummy/all/', methods=['POST'])
def view_dummy_news_feed():
    now = str(datetime.datetime.utcnow().replace(tzinfo=utc))

    data = {
        now: {
            'photo': 'http://lorempixel.com/g/400/200/',
            'date_due': now,
            'description': 'Lorem ipsum dolor sit amet, consectetur adipisicing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.'
        }
    }

    resp = jsonify(data)
    resp.status_code = 200
    return resp
