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
from inspect import ismethod


class TokenStore(object):
    def get(self, key):
        raise NotImplementedError(
            'github.TokenStore must be subclassed and the method ' \
            'get must be implemented',
        )

    def set(self, key):
        raise NotImplementedError(
            'github.TokenStore must be subclassed and the method ' \
            'set must be implemented',
        )


class API(object):
    _cookie_token_name = '_ght_at'

    def __init__(
        self,
        client_id=None,
        client_secret=None,
        store=None):

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

    @property
    def is_authenticated(self):
        return False

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
