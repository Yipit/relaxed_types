# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import re


class custom_type(object):
    def __init__(self, name, checker):
        self.name = name
        self.checker = checker

    def __call__(self, arg):
        return self.checker(arg)

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.__str__()


def MinLength(l):
    return custom_type('MinLength[{}]'.format(l), lambda data: len(data) > l)


def Range(lo, hi):
    return custom_type('Range[{},{}]'.format(lo, hi), lambda data: lo <= len(data) <= hi)


def Contains(c):
    return custom_type('Contains[{}]'.format(c), lambda data: c in data)


def RegExpPattern(r):
    return custom_type('RegExpPattern[{}]'.format(r),
                       lambda data: re.search(r, data) is not None)
