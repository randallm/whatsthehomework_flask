What's the Homework
===================

What's the Homework (WTH) is an Android collaborative homework manager app. Students can share and upload homework assignments and view them in Facebook-esque news feeds.

API Calls
---------

At the moment, requests should be made with `application/x-www-form-encoded`. This is subject to change to `application/json` in the future.

Responses are returned as `application/json` when example JSON is given below. Otherwise, they are given as `text/html` (again, subject to change to `application/json` in the future)

API - User/Authentication
-------------------------

`POST /user/login/`

Required: 'username', 'password'
Returns session cookie.

`GET /user/verify_logged_in/`

If user logged in, returns 200. Else, returns 400.

`GET /user/motd/`

If user logged in, returns user's username. Else, returns 400.

`GET /user/classes/`

Returns SchoolClass.id and SchoolClass.title of classes student is in.

    {
        "1": "Crumpets 2013-2014 AP Tastiness"
    }

`POST /user/new_student/`

Required: 'username', 'real_name', 'email', 'school_id', 'password'
Attempts to create new user.

`POST /user/add_class/`

Required: 'school_class'
Adds a class to student's class roster.

`POST /user/new_class/`

Required: 'school'
Creates a new class linked to an existing school.

`POST /user/new_assignment/`

Required: 'class'
Optional: 'b64_photo'
Creates new homework assignment in class with optional photo encoded in base64 text.

API - News Feed
---------------

`GET /news/new/all/`

Returns newest 15 assignments associated with a user's classes.

    {
      "assignments": [
        {
          "0": {
            "date_due": "1359999568",
            "description": "",
            "poster": "admin",
            "pk": 20,
            "thumbnail": "/9j/4AAQSkZJRgABAQAAAQABAAD//",
            "date_posted": "1359913168"
          },
          "1": {
            "date_due": "1359999448",
            "description": "",
            "poster": "admin",
            "pk": 19,
            "thumbnail": "/9j/4AAQSkZJRgABAQAAAQABAAD//",
            "date_posted": "1359913048"
          }
        }
      ]
    }

`GET /news/new/all/<latest_pk>/`

Returns newest posts associated with a user's classes starting from <latest_pk> (refresh action in app).

Example JSON is in same format as `/news/new/all/` except `pk` is numerically in reverse order.

`GET /news/old/all/<oldest_pk>/`

Return next 15 older posts associated with a user's classes starting from <oldest_pk> (scroll down to bottom action in app).

Example JSON is in same format as `/news/new/all/`.