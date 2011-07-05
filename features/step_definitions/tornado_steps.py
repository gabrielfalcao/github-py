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

from lettuce import step, world


@step(u'Given I go to "(.*)"')
def given_i_go_to_group1(step, url):
    world.browser.visit(url)


@step(u'When I get redirected to "(.*)"')
def when_i_get_redirected_to_group1(step, url):
    import ipdb;ipdb.set_trace()


@step(u'And authorize the app "(.*)"')
def and_authorize_the_app_group1(step, name):
    import ipdb;ipdb.set_trace()


@step(u'Then I should be redirected back to "(.*)"')
def then_i_should_be_redirected_back_to_group1(step, group1):
    import ipdb;ipdb.set_trace()


@step(u'And the response should match these values:')
def and_the_response_should_match_these_values(step):
    import ipdb;ipdb.set_trace()
