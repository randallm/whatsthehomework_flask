What's the Homework
===================

What's the Homework (WTH) is an Android collaborative homework manager app. Students can share and upload homework assignments and view them in Facebook-esque news feeds.

Future Plans
------------

I originally started this project with the intent of reimplementing many of the features available in social networking sites. However, I recently realized getting my peers to switch all switch from our existing homework sharing mediums to a service that I built is unpragmatic at best. As a result, this server client is being put on the backburner as I migrate [the Android app](https://github.com/randallm/whatsthehomework_android) to take advantage of a local database and existing sharing platforms, like NFC and existing social networks.

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

Licensing
---------

Copyright (c) 2012-2013, Randall Ma
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:
* Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.
* Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.
* Neither the name of What's the Homework nor the names of its contributors may be used to endorse or promote products derived from this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL <COPYRIGHT HOLDER> BE LIABLE FOR ANY
DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
(INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
