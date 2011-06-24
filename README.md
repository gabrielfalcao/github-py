# github-py
> version 0.1

# What

A implementation of the [GitHub API](http://developer.github.com/) in
python, leveraging the job of fetching data through objects.

# concept and usage

Authenticating through [OAuth](http://oauth.net/2/) takes a few steps,
some steps are taken in the API side, and some in your code.

## if you're new to OAuth

there is a simple walkthrough the steps

1. Your application has a code, with that code you give your visitor a
url to visit

2. Once with that url, you add some parameters that will tell github
what kinds of data you're gonna deal with. That is the scope

3. Send the user to that url. That's a github page asking to the
visitor if he really wants to allow your application to access his/her
data.

4. User authorizes, then github send the user back to your website,
and a key that seals the trust between the visitor, the github API and
your server.

5. From now on you keep that key with you for the entire session you
keep with the visitor (yay, cookies! :)

6. Whenever you need an information regarding the user, you use the
token given to you on `4th step` to go to github api, and get it :)

## token store

This github module comes with a class that must be inherited in order
to store the user token in any storage of your preference.

It is not a obligatory thing, but will help you on decoupling the API
authentication from your controllers, believe me :)

### example

```python
import redis
from github import TokenStore, API

class RedisStore(TokenStore):
    def __init__(self):
        self.db = redis.Redis()

    def get(self, key):
        self.db.get(key)

    def set(self, key, value):
        self.db.set(key, value)

github = API(client_id='your app id here',
             client_secret='your app secret',
             store=RedisStore())
```

## web framework support

github-py currently supports

* [Django](http://djangoproject.com)
* [Tornado](http://tornadoweb.org)
 * As well as [TornadIO](https://github.com/MrJoes/tornadio)

### example with Django

```python
# settings.py

DATABASES = {
...
}

GITHUB_CLIENT_ID = 'your app client id'
GITHUB_CLIENT_SECRET = 'your app client secret'
```

```python
# yourapp/views.py
from github.django import authenticated
from django.shortcuts import render_to_response

@authenticated
def index(request, github):
    return render_to_response('index.html', {'user': github.user})
```

### example with Tornado

```python
# yourapp.py
import tornado.ioloop
import tornado.web
from github.tornado import authenticated

class MainHandler(tornado.web.RequestHandler):
    @authenticated
    def get(self):
        self.render('index.html', user=github.user)

application = tornado.web.Application([
    (r"/", MainHandler),
])

if __name__ == "__main__":
    application.listen(8888)
    tornado.ioloop.IOLoop.instance().start()
```


#### or even use a ready-to-go RequestHandler

```python
# yourapp.py
import tornado.ioloop
import tornado.web
from github.tornado import GitHubPowered

class MainHandler(GitHubPowered):
    def get(self):
        self.render('index.html', user=github.user)

application = tornado.web.Application(
    [
        (r"/", MainHandler),
    ],
    template_path='/path/to/yourapp/templates'),
    cookie_secret='some random hash or something...',
    github_client_id='your app client id',
    github_client_secret='your app client secret',
)

if __name__ == "__main__":
    application.listen(8888)
    tornado.ioloop.IOLoop.instance().start()
```

### for both cases above you could make use of this template:

```html
<!-- yourapp/templates/index.html -->
...
<h1>Hello {{ user.name }},</h1>
<p>I have to say your picture: <img src="{{ user.avatar_url }}" alt="{{ user.name }}'s avatar" /> is terrific!</p>
```

# contributing

Firstly, I recommend using a [virtualenv](http://pypi.python.org/pypi/virtualenv).

Secondly, install the requirements:

    pip install -Ur requirements.pip

## guidelines

1. fork and clone the project
2. install the dependencies above
3. run the tests with make:
    > make unit functional
4. hack at will
5. commit, push etc
6. send a pull request

# License

    # <github-py - python library that leverages the GitHub API>
    # Copyright (C) <2011>  Gabriel Falcão <gabriel@nacaolivre.org>
    #
    # This program is free software: you can redistribute it and/or modify
    # it under the terms of the GNU General Public License as published by
    # the Free Software Foundation, either version 3 of the License, or
    # (at your option) any later version.
    #
    # This program is distributed in the hope that it will be useful,
    # but WITHOUT ANY WARRANTY; without even the implied warranty of
    # MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    # GNU General Public License for more details.
    #
    # You should have received a copy of the GNU General Public License
    # along with this program.  If not, see <http://www.gnu.org/licenses/>.
