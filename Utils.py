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
_int_re = re.compile(r'([+-]?\d*)')


def valid_float_string(string):
    match = _float_re.search(string)
    return match.groups()[0] == string if match else False


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


class IntValidator(QtGui.QValidator):
    def validate(self, string, position):
        string = str(string)
        try:
            int(string)
        except ValueError:
            return self.Invalid
        return self.Acceptable

    def fixup(self, text):
        match = _int_re.search(text)
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

    # m = "%.*g" % (p, n)
    m = "{0:.{p}g}".format(n, p=p)

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

    s = "".join(out)

    return s


def to_precision2(x, p=-1, w=-1, neg_compensation=False, return_prefix_string=True, floating_point=True):
    """
    returns a string representation of x formatted with a precision of p OR width w

    """
    prefix_dict = {12: "T", 9: "G", 6: "M", 3: "k", 0: "", -3: "m", -6: "\u00b5", -9: "n", -12: "p", -15: "f", -18: "a"}
    out = []
    if p > 0:
        if p > w - 3:
            p = w - 3
    elif w > 3:
        p = w - 4
    else:
        p = 0
        w = 4

    if np.isnan(x):
        return " " * (w-2) + "--"

    if floating_point:
        x = float(x)
    else:
        x = int(x)
        p = 0

    s_neg = ""
    if x < 0:
        s_neg = "-"
        x = -x
    else:
        if neg_compensation:
            s_neg = " "
        else:
            s_neg = ""

    if x == 0:
        prefix = 0
    elif x < 1:
        try:
            prefix = int((np.log10(x) - 0.5) // 3)
        except ValueError:
            prefix = 0
    else:
        try:
            prefix = int(np.log10(x) // 3)
        except ValueError:
            prefix = 0

    if prefix > 0:
        p0 = p
        try:
            p = w - int(np.log10(x) - 3 * prefix)
        except ValueError:
            p = 0

    s_val = "{0:.{p}f} ".format(x * 10 ** (-prefix * 3), p=p)
    out.append(s_val)
    if return_prefix_string:
        try:
            out.append(prefix_dict[prefix*3])
            # if prefix != 0:
            #     w -= 1
            s_prefix = prefix_dict[prefix*3]
        except KeyError:
            out.append("1e{0} x".format(prefix * 3))
            s_prefix = "1e{0} x".format(prefix * 3)
    else:
        s_prefix = ""

    s_len = len(s_val) + len(s_neg) + len(s_prefix)
    n_space = w - s_len
    if n_space < -1:        # Allow one extra since . is small
        s_val = s_val[:n_space+1]
        s = s_neg + s_val + s_prefix
    else:
        s = " " * n_space + s_neg + s_val + s_prefix

    # s = "".join(out)
    # n_space = w - len(s)
    # s = " " * n_space + s

    return s
