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
import functools
from github import API, TokenStore


class TornadoSessionStore(TokenStore):
    def __init__(self, handler):
        self.handler = handler

    def get(self, key):
        return self.handler.get_secure_cookie(key)

    def set(self, key, value):
        self.handler.set_secure_cookie(key, value)
        assert self.get(key) == value, '%r != %r' % (self.get(key), value)


class InvalidGithubTornadoConfiguration(Exception):
    pass


class AuthenticationManager(object):
    """holds the logic behind the @authenticated decorator"""

    def __init__(self, callback):
        self.callback = callback

    def validate_application(self):
        e = 'missing the parameter "%s" in your tornado application settings'
        settings = self.handler.application.settings
        params = [
            'github_client_id',
            'github_client_secret',
            'cookie_secret',
        ]

        for param in params:
            if param not in settings:
                raise InvalidGithubTornadoConfiguration(e % param)

    def process(self, handler, args, kwargs):
        self.handler = handler

        self.validate_application()
        github = API(
            self.handler.application.settings['github_client_id'],
            self.handler.application.settings['github_client_secret'],
            store=TornadoSessionStore(self.handler),
        )
        self.handler.github = github
        code = self.handler.get_argument('code', None)

        api = github.authenticate(code)

        if isinstance(api, basestring):
            return self.handler.redirect(api, True)

        return self.callback(self.handler, api, *args, **kwargs)


def authenticated(method):
    controller = AuthenticationManager(method)

    @functools.wraps(method)
    def wrapper(handler, *args, **kw):
        return controller.process(handler, args, kw)

    return wrapper
