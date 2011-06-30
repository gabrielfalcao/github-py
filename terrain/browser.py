# -*- coding: utf-8 -*-
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
import urllib
from httplib2 import Http
from lxml import html
from os.path import dirname, abspath, join, exists
from lettuce import before, world

local_file = lambda *path: join(abspath(dirname(__file__)), *path)
secret_file = local_file('..', '.github-secret')

err = 'please create the file "%s" containing ' \
       '"your_github_username:your_password" ' \
       '(without the quotes)' % secret_file

assert exists(secret_file), err

world.django_app_id = 'de9fc92a367df56978fa'
world.django_app_secret = 'e4b59886c6b2c5c32ee1661112288e75ec85fa63'


@before.all
def get_passwords():
    try:
        login, password = open(secret_file).read().strip().split(":")
    except ValueError:
        raise AssertionError(err)

    world.github_credentials = dict(login=login,
                                    password=password)


class SimpleHeadlessBrowser(Http):
    def __init__(self, *args, **kw):
        self.last_headers = {}
        self.last_body = ''
        super(SimpleHeadlessBrowser, self).__init__(*args, **kw)

    def get(self, url, body=None, headers=None):
        return self.request(url, 'GET', body=body, headers=headers)

    def post(self, url, body=None, headers=None):
        body = urllib.urlencode(isinstance(body, dict) and body or {})
        return self.request(url, 'POST', body=body, headers=headers)

    def request(self, url, method, body=None, headers=None):
        h = self.last_headers.copy()
        if 'set-cookie' in h:
            h['cookie'] = h['set-cookie']

        h.update(isinstance(headers, dict) and headers or {})

        response = super(SimpleHeadlessBrowser, self).request(
            url,
            method,
            body,
            headers=h,
        )
        self.last_headers, self.last_body = response

        return response

    @property
    def dom(self):
        return self.last_body and html.fromstring(self.last_body)

    def cssselect(self, selector):
        ret = self.dom is not None and self.dom.cssselect(selector) or []
        if len(ret) is 1:
            return ret[0]

        return ret

    def xpath(self, selector):
        ret = self.dom is not None and self.dom.xpath(selector) or []
        if len(ret) is 1:
            return ret[0]

        return ret


@before.each_scenario
def prepare_client(scenario):
    world.browser = SimpleHeadlessBrowser()
    world.browser.get('https://github.com/login')

    data = {}

    for e in world.browser.cssselect('form input[name]'):
        data[e.attrib['name']] = unicode(e.attrib.get('value', ''))

    data.update(world.github_credentials)
    import debug

    response = world.browser.post('https://github.com/session', body=data)
    import debug
