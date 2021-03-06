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
from sure import that_with_context
from httpretty import HTTPretty


def prepare(context):
    HTTPretty.enable()


def and_clear(context):
    HTTPretty.disable()

httprettified = that_with_context(prepare, and_clear)
