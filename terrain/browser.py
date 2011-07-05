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
from splinter.browser import Browser
from lxml import html
from os.path import dirname, abspath, join, exists
from lettuce import before, world

local_file = lambda *path: abspath(join(abspath(dirname(__file__)), *path))
secret_file = local_file('..', '.github-secret')

err = 'please create the file "%s" containing ' \
       '"your_github_username:your_password" ' \
       '(without the quotes)' % secret_file

assert exists(secret_file), err

world.django_app_id = 'de9fc92a367df56978fa'
world.django_app_secret = 'e4b59886c6b2c5c32ee1661112288e75ec85fa63'
world.tornado_app_id = 'b2ae1ce0e63e9cbd7f9d'
world.tornado_app_secret = '881244b5010a80960432536ab6a2b4a6d5cb49b9'


@before.all
def get_passwords():
    try:
        login, password = open(secret_file).read().strip().split(":")
    except ValueError:
        raise AssertionError(err)

    world.github_credentials = dict(login=login,
                                    password=password)


@before.each_scenario
def prepare_client(scenario):
    world.browser = Browser()
    world.browser.visit('https://github.com/login')

    for field, value in world.github_credentials.items():
        world.browser.find_by_name(field).first.value = value

    world.browser.find_by_name("commit").first.click()
