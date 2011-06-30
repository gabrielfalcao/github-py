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
import github
import simplejson

from sure import that
from httpretty import HTTPretty, httprettified


def test_it_should_require_the_client_id_in_first_place():
    "creating a github.API requires the client_id as first argument"
    assert that(github.API). \
        raises(TypeError,
               'github.API requires the first argument to be a ' \
               'string holding the client_id',
        )


def test_it_should_require_the_client_secret_in_second_place():
    "creating a github.API requires the client_secret as second argument"

    assert that(github.API, with_args=['client_id']). \
        raises(TypeError,
               'github.API requires the second argument to be a ' \
               'string holding the client_secret',
        )


def test_it_should_require_a_implementation_of_tokenstore():
    'creating a github.API passing a "raw" TokenStore is denied'
    unimplemented_storage = github.TokenStore()
    assert that(github.API, with_args=['client_id', 'client_secret'],
                and_kwargs={'store': unimplemented_storage}). \
        raises(TypeError,
               'github.API argument "store" requires a implementation ' \
               'of github.TokenStore',
        )


def test_it_complains_when_store_does_not_implement_get():
    'creating a github.API passing a storage that does not implement "get"'

    class QuarterImplementedTokenStore(github.TokenStore):
        pass

    quarter_implemented = QuarterImplementedTokenStore()
    assert that(github.API, with_args=['client_id', 'client_secret'],
                and_kwargs={'store': quarter_implemented}).raises(
        TypeError,
        'the provided TokenStore: %s, does not implement the method "get"' % \
        QuarterImplementedTokenStore.__name__,
    )


def test_it_complains_when_store_does_not_implement_set():
    'creating a github.API passing a storage that does not implement "set"'

    class HalfImplementedTokenStore(github.TokenStore):
        def get(self, k):
            pass

    half_implemented = HalfImplementedTokenStore()
    assert that(github.API, with_args=['client_id', 'client_secret'],
                and_kwargs={'store': half_implemented}).raises(
        TypeError,
        'the provided TokenStore: %s, does not implement the method "set"' % \
        HalfImplementedTokenStore.__name__,
    )


def test_does_not_complain_when_its_a_nice_implementation():
    'creating a github.API passing a storage that implements get/set methods'

    class FullyImplementedTokenStore(github.TokenStore):
        def get(self):
            pass

        def set(self):
            pass

    dummy = FullyImplementedTokenStore()
    api = github.API('client_id', 'client_secret', store=dummy)
    assert that(api).is_a(github.API)


@httprettified
def test_api_representation():
    "github.API object should be nicely repr()'ed"

    class MyStore(github.TokenStore):
        data = {}

        def set(self, k, v):
            self.data[k] = v

        def get(self, k):
            return self.data.get(k)

    simple = MyStore()
    api = github.API('app-id-here', 'app-secret-here', store=simple)

    assert that(repr(api)).equals(
        'github.API("app-id-here", "app-secret-here", store=%r)' % simple)


@httprettified
def test_it_should_not_be_authenticated_by_default():
    "github.API is not authenticated until requested"

    class MyStore(github.TokenStore):
        data = {}

        def set(self, k, v):
            self.data[k] = v

        def get(self, k):
            return self.data.get(k)

    simple = MyStore()
    api = github.API('app-id-here', 'app-secret-here', store=simple)

    assert not api.is_authenticated, '%s should not be authenticated' % api


@httprettified
def test_first_authentication_step_is_redirect():
    "github.API's first authentication step is a redirect"

    HTTPretty.register_uri(
        HTTPretty.POST,
        'https://github.com/login/oauth/access_token',
        status=401,
        body={'message': 'Bad credentials'},
    )

    class MyStore(github.TokenStore):
        data = {}

        def set(self, k, v):
            self.data[k] = v

        def get(self, k):
            return self.data.get(k)

    simple = MyStore()
    api = github.API('app-id-here', 'app-secret-here', store=simple)

    result = api.authenticate()

    assert that(result).is_a(basestring)

    assert that(result).equals(
        'https://github.com/login/oauth/authorize?client_id=app-id-here',
    )


@httprettified
def test_second_authentication_step_takes_code_and_makes_a_request():
    "github.API's second authentication step takes a code and requests a " \
    "access token"

    HTTPretty.register_uri(
        HTTPretty.POST,
        'https://github.com/login/oauth/access_token',
        body='{"access_token": "this-is-the-access-token"}',
        status=200,
    )

    class MyStore(github.TokenStore):
        data = {}

        def set(self, k, v):
            self.data[k] = v

        def get(self, k):
            return self.data.get(k)

    simple = MyStore()
    api = github.API('app-id-here', 'app-secret-here', store=simple)

    result = api.authenticate(code='visitor-code')

    try:
        last_body = simplejson.loads(HTTPretty.last_request.body)
    except:
        raise AssertionError(
            'the request body was not json serializable: %r' % \
            HTTPretty.last_request.body)

    assert that(last_body).at('client_secret').equals('app-secret-here')
    assert that(last_body).at('code').equals('visitor-code')
    assert that(last_body).at('client_id').equals('app-id-here')

    assert that(result).is_a(github.API)


@httprettified
def test_dont_authorize_401():
    "github.API's recognized it was not authorized (response 401)"

    HTTPretty.register_uri(
        HTTPretty.POST,
        'https://github.com/login/oauth/access_token',
        status=401,
    )
    HTTPretty.register_uri(
        HTTPretty.POST,
        'https://api.github.com/user',
        body='{"login": "gabrielfalcao"}',
    )

    api = github.API('app-id-here', 'app-secret-here')

    result = api.authenticate(code='bad-code')

    assert that(result).is_a(basestring)
    assert that(result).equals(
        'https://github.com/login/oauth/authorize?client_id=app-id-here',
    )


@httprettified
def test_dont_authorize_bad_credentials():
    "github.API's recognized it was not authorized (with message)"

    HTTPretty.register_uri(
        HTTPretty.POST,
        'https://github.com/login/oauth/access_token',
        body='{"message": "Bad credentials"}',
    )
    HTTPretty.register_uri(
        HTTPretty.POST,
        'https://api.github.com/user',
        body='{"message": "Bad credentials"}',
    )

    api = github.API('app-id-here', 'app-secret-here')

    result = api.authenticate(code='bad-code')

    assert that(result).is_a(basestring)
    assert that(result).equals(
        'https://github.com/login/oauth/authorize?client_id=app-id-here',
    )

# create a test that check when the token is expired, and raises an
# exception when any search on the API is issued, raise a
# GithubTokenExpired exception
