# #!/usr/bin/env python
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
version = '0.1'

import re
import simplejson

from httplib2 import Http
from inspect import ismethod

LOGIN_URL = 'https://github.com/login/oauth/authorize'
TOKENSTORE_KEY = 'github_token'


class TokenStore(object):
    def get(self, key):
        raise NotImplementedError(
            'github.TokenStore must be subclassed and the method ' \
            'get must be implemented',
        )

    def set(self, key, value):
        raise NotImplementedError(
            'github.TokenStore must be subclassed and the method ' \
            'set must be implemented',
        )


class GithubResponse(dict):
    def __init__(self, headers, body, store):
        self.raw = body
        self.headers = dict(headers)
        self.status_code = int(self.headers['status'])
        self.store = store

        if self.status_code in (200, 401):
            try:
                self.update(simplejson.loads(unicode(body, 'utf-8')))
            except simplejson.JSONDecodeError:
                pass

        if 'access_token' in self:
            token = self['access_token']
            if self.store:
                self.store.set(TOKENSTORE_KEY, token)

        elif store and store.get(TOKENSTORE_KEY):
            token = store.get(TOKENSTORE_KEY)

        else:
            token = None

        if token:
            store.set(TOKENSTORE_KEY, token)

    @property
    def was_authorized(self):
        if self.status_code == 401:
            return False

        elif self.message_matches(r'bad\s*credentials'):
            return False

        return True

    def message_matches(self, pattern):
        if not 'message' in self.headers:
            return False

        regex = re.compile(pattern, re.I | re.U)
        return regex.search(regex, self['message'])


class API(object):
    def __init__(
        self,
        client_id=None,
        client_secret=None,
        store=None,
        **kwargs):

        if not isinstance(client_id, basestring):
            raise TypeError(
               'github.API requires the first argument to be a ' \
               'string holding the client_id',
            )
        elif not isinstance(client_secret, basestring):
            raise TypeError(
               'github.API requires the second argument to be a ' \
               'string holding the client_secret',
            )

        self.client_id = client_id
        self.client_secret = client_secret
        self.store = self.validate_token_store(store)
        self.http = Http(**kwargs)
        self.is_authenticated = False
        self.__cache = dict(
            user=None,
        )

    def request(self, url, data=None, method='GET', headers=None):
        # always JSON
        h = {'Content-Type': 'application/json'}

        if not isinstance(data, dict):
            data = {}

        token = self.store and self.store.get(TOKENSTORE_KEY)

        if isinstance(token, basestring) and len(token) > 0:
            h['Authorization'] = "token %s" % unicode(token)

        if isinstance(headers, dict):
            h.update(headers)

        headers, body = self.http.request(
            url,
            headers=h,
            body=simplejson.dumps(data),
            method=method,
        )

        response = GithubResponse(headers, body, self.store)
        self.is_authenticated = response.was_authorized

        return response

    @property
    def user(self):
        token = self.store and self.store.get(TOKENSTORE_KEY)

        u = self.__cache.get('user', None)
        if u:
            return u

        if not token:
            return None

        response = self.request('https://api.github.com/user')
        self.__cache['user'] = response
        return self.__cache['user']

    def authenticate(self, code=None):
        url = '%s?client_id=%s' % (LOGIN_URL, self.client_id)

        token = self.store and self.store.get(TOKENSTORE_KEY)
        if token:
            return self

        if self.user:
            return self

        elif isinstance(code, basestring) and len(code) > 0:
            response = self.request(
                'https://github.com/login/oauth/access_token',
                data={
                    'code': code,
                    'client_id': self.client_id,
                    'client_secret': self.client_secret,
                },
                method='POST',
            )
            self.is_authenticated = response.was_authorized
            if response.was_authorized:
                return self
            else:
                return url

        else:
            return url

    def __repr__(self):
        return u'github.API("{0}", "{1}", store={2})'.format(
            self.client_id,
            self.client_secret,
            self.store,
        )

    def validate_token_store(self, store):
        if type(store) == TokenStore:
            raise TypeError(
                'github.API argument "store" requires a implementation ' \
                'of github.TokenStore',
            )
        elif isinstance(store, TokenStore):
            cls = store.__class__
            explanation = 'the provided TokenStore: %s, does not implement ' \
                'the method "%%s"' % cls.__name__

            if not ismethod(store.get) or cls.get == TokenStore.get:
                raise TypeError(explanation % "get")

            elif not ismethod(store.set) or cls.set == TokenStore.set:
                raise TypeError(explanation % "set")

        return store
