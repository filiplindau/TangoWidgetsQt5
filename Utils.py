# -*- coding:utf-8 -*-
"""
Created on Dec 18, 2017

@author: Filip
"""
import re
from PyQt5 import QtGui
import logging
import numpy as np

logger = logging.getLogger(__name__)

# Regular expression to find floats. Match groups are the whole string, the
# whole coefficient, the decimal part of the coefficient, and the exponent
# part.
_float_re = re.compile(r'(([+-]?\d+(\.\d*)?|\.\d+)([eE][+-]?\d+)?)')


def valid_float_string(string):
    match = _float_re.search(string)
    return match.groups()[0] == string if match else False


class FloatValidator(QtGui.QValidator):
    def validate(self, string, position):
        string = str(string)
        if valid_float_string(string):
            return self.Acceptable
        if string == "" or string[position - 1] in 'e.-+':
            return self.Intermediate
        return self.Invalid

    def fixup(self, text):
        match = _float_re.search(text)
        return match.groups()[0] if match else ""


def format_float(value):
    """Modified form of the 'g' format specifier."""
    string = "{:.4g}".format(value).replace("e+", "e")
    string = re.sub("e(-?)0*(\d+)", r"e\1\2", string)
    return string


def to_precision(x, p):
    """
    returns a string representation of x formatted with a precision of p

    Based on the webkit javascript implementation taken from here:
    https://code.google.com/p/webkit-mirror/source/browse/JavaScriptCore/kjs/number_object.cpp
    """
    x = float(x)
    if x == 0.:
        return "0." + "0" * (p - 1)

    out = []

    if x < 0:
        out.append("-")
        x = -x

    e = int(np.log10(x))
    tens = 10 ** (e - p + 1)
    n = np.floor(x / tens)

    if n < 10 ** (p - 1):
        e -= 1
        tens = 10 ** (e - p + 1)
        n = np.floor(x / tens)

    if abs((n + 1.) * tens - x) <= abs(n * tens - x):
        n += 1

    if n >= 10 ** p:
        n /= 10.
        e += 1

    m = "%.*g" % (p, n)

    if e < -2 or e >= p:
        out.append(m[0])
        if p > 1:
            out.append(".")
            out.extend(m[1:p])
        out.append('e')
        if e > 0:
            out.append("+")
        out.append(str(e))
    elif e == (p - 1):
        out.append(m)
    elif e >= 0:
        out.append(m[:e + 1])
        if e + 1 < len(m):
            out.append(".")
            out.extend(m[e + 1:])
    else:
        out.append("0.")
        out.extend(["0"] * -(e + 1))
        out.append(m)

    return "".join(out)
