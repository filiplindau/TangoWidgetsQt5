# -*- coding:utf-8 -*-
"""
Created on Dec 18, 2017

@author: Filip
"""
from PyQt5 import QtWidgets, QtCore, QtGui
import numpy as np
import PyTango as pt
from ColorDefinitions import QTangoColors, QTangoSizes
from BaseWidgets import QTangoAttributeBase
from Utils import to_precision, FloatValidator, IntValidator
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.WARN)


class QTangoStartLabel(QtWidgets.QLabel, QTangoAttributeBase):
    def __init__(self, sizes=None, colors=None, parent=None):
        QTangoAttributeBase.__init__(self, sizes, colors, parent)
        QtWidgets.QLabel.__init__(self, parent)
        self.setupLayout()

    def setQuality(self, quality):
        QTangoAttributeBase.setQuality(self, quality, use_background_color=True)

    def setState(self, state):
        QTangoAttributeBase.setState(self, state, use_background_color=True)

    def setupLayout(self):
        self.setText('')
        st = ''.join(('QLabel {min-height: ', str(self.sizes.barHeight), 'px; \n',
                      'min-width: ', str(int(self.sizes.barWidth / 3)), 'px; \n',
                      'max-width: ', str(int(self.sizes.barWidth / 3)), 'px; \n',
                      'background-color: ', self.current_attr_color, ';}'))
        self.setStyleSheet(st)


class QTangoBooleanLabel(QtWidgets.QLabel):
    def __init__(self, sizes=None, colors=None, parent=None):
        QtWidgets.QLabel.__init__(self, parent)
        if colors is None:
            self.attrColors = QTangoColors()
        else:
            self.attrColors = colors
        if sizes is None:
            self.sizes = QTangoSizes()
        else:
            self.sizes = sizes
        self.setText('')
        st = ''.join(('QLabel {min-height: ', str(self.sizes.barHeight / 2), 'px; \n',
                      'max-height: ', str(int(self.sizes.barHeight / 2)), 'px; \n',
                      'min-width: ', str(int(self.sizes.barHeight / 2)), 'px; \n',
                      'max-width: ', str(int(self.sizes.barHeight / 2)), 'px; \n',
                      'border-width: 1px; \n',
                      'border-color: ', self.attrColors.secondaryColor0, '; \n',
                      'border-style: solid; \n',
                      'border-radius: 0px; \n',
                      'padding: 0px; \n',
                      'margin: 0px; \n',
                      'background-color: ', self.attrColors.backgroundColor, ';}'))
        self.setStyleSheet(st)

    def setBooleanState(self, bool_state):
        if bool_state is False:
            st = ''.join(('QLabel {min-height: ', str(self.sizes.barHeight / 2), 'px; \n',
                          'max-height: ', str(int(self.sizes.barHeight / 2)), 'px; \n',
                          'min-width: ', str(int(self.sizes.barHeight / 2)), 'px; \n',
                          'max-width: ', str(int(self.sizes.barHeight / 2)), 'px; \n',
                          'border-width: 1px; \n',
                          'border-color: ', self.attrColors.secondaryColor0, '; \n',
                          'border-style: solid; \n',
                          'border-radius: 0px; \n',
                          'padding: 0px; \n',
                          'margin: 0px; \n',
                          'background-color: ', self.attrColors.backgroundColor, ';}'))
        else:
            st = ''.join(('QLabel {min-height: ', str(self.sizes.barHeight / 2), 'px; \n',
                          'max-height: ', str(int(self.sizes.barHeight / 2)), 'px; \n',
                          'min-width: ', str(int(self.sizes.barHeight / 2)), 'px; \n',
                          'max-width: ', str(int(self.sizes.barHeight / 2)), 'px; \n',
                          'border-width: 1px; \n',
                          'border-color: ', self.attrColors.secondaryColor0, '; \n',
                          'border-style: solid; \n',
                          'border-radius: 0px; \n',
                          'padding: 0px; \n',
                          'margin: 0px; \n',
                          'background-color: ', self.attrColors.secondaryColor0, ';}'))
        self.setStyleSheet(st)


class QTangoEndLabel(QtWidgets.QLabel, QTangoAttributeBase):
    def __init__(self, sizes=None, colors=None, parent=None):
        QTangoAttributeBase.__init__(self, sizes, colors, parent)
        QtWidgets.QLabel.__init__(self, parent)
        self.setupLayout()

    def setQuality(self, quality):
        QTangoAttributeBase.setQuality(self, quality, use_background_color=True)

    def setState(self, state):
        QTangoAttributeBase.setState(self, state, use_background_color=True)

    def setupLayout(self):
        st = ''.join(('QLabel {min-height: ', str(self.sizes.barHeight), 'px; \n',
                      'min-width: ', str(int(self.sizes.barWidth)), 'px; \n',
                      'max-width: ', str(int(self.sizes.barWidth)), 'px; \n',
                      'background-color: ', self.current_attr_color, ';}'))
        self.setStyleSheet(st)


class QTangoAttributeNameLabel(QtWidgets.QLabel, QTangoAttributeBase):
    def __init__(self, sizes=None, colors=None, parent=None):
        QTangoAttributeBase.__init__(self, sizes, colors, parent)
        QtWidgets.QLabel.__init__(self, parent)
        self.name_text = ''
        self.currentAttrColor = self.attrColors.secondaryColor0
        self.setupLayout()

    def setupLayout(self):
        self.setText('')
        s = ''.join(('QLabel {min-height: ', str(self.sizes.barHeight), 'px; \n',
                     'max-height: ', str(self.sizes.barHeight), 'px; \n',
                     # 					'min-width: ', str(int(readWidth)), 'px; \n',
                     # 					'max-width: ', str(int(readWidth)), 'px; \n',
                     'background-color: ', self.attrColors.backgroundColor, '; \n',
                     'color: ', self.currentAttrColor, ';}'))
        self.setStyleSheet(s)

        font = self.font()
        font.setFamily(self.sizes.fontType)
        font.setStretch(self.sizes.fontStretch)
        font.setWeight(self.sizes.fontWeight)
        font.setPointSize(int(self.sizes.barHeight * 0.7))
        font.setStyleStrategy(QtGui.QFont.PreferAntialias)
        self.setFont(font)
        self.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignBottom)
        self.setSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)

    def setQuality(self, quality):
        state_str = str(quality)
        if state_str == str(pt.AttrQuality.ATTR_VALID):
            color = self.attrColors.validColor
            state_string = 'VALID'
        elif state_str == str(pt.AttrQuality.ATTR_INVALID):
            color = self.attrColors.invalidColor
            state_string = 'INVALID'
        elif state_str == str(pt.AttrQuality.ATTR_ALARM):
            color = self.attrColors.alarmColor
            state_string = 'ALARM'
        elif state_str == str(pt.AttrQuality.ATTR_WARNING):
            color = self.attrColors.warnColor
            state_string = 'WARNING'
        elif state_str == str(pt.AttrQuality.ATTR_CHANGING):
            color = self.attrColors.changingColor
            state_string = 'CHANGING'
        else:
            color = self.attrColors.unknownColor
            state_string = 'UNKNOWN'

        self.quality = state_string
        self.currentAttrColor = color
        s = ''.join(('QLabel {min-height: ', str(self.sizes.barHeight), 'px; \n',
                     'max-height: ', str(self.sizes.barHeight), 'px; \n',
                     'background-color: ', self.attrColors.backgroundColor, '; \n',
                     'color: ', self.currentAttrColor, ';}'))
        self.setStyleSheet(s)
        self.update()


class QTangoStateLabel(QtWidgets.QLabel, QTangoAttributeBase):
    def __init__(self, sizes=None, colors=None, parent=None):
        QTangoAttributeBase.__init__(self, sizes, colors, parent)
        QtWidgets.QLabel.__init__(self, parent)
        self.currentAttrColor = self.attrColors.secondaryColor0
        self.setupLayout()

    def setupLayout(self):
        self.setText('')
        s = ''.join(('QLabel {min-height: ', str(self.sizes.barHeight), 'px; \n',
                     'max-height: ', str(self.sizes.barHeight), 'px; \n',
                     'background-color: ', self.attrColors.backgroundColor, '; \n',
                     'color: ', self.currentAttrColor, ';}'))
        self.setStyleSheet(s)

        font = self.font()
        font.setFamily(self.sizes.fontType)
        font.setStretch(self.sizes.fontStretch)
        font.setWeight(self.sizes.fontWeight)
        font.setPointSize(int(self.sizes.barHeight * 0.7))
        font.setStyleStrategy(QtGui.QFont.PreferAntialias)
        self.setFont(font)
        self.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignBottom)
        self.setSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)

    def setQuality(self, quality):
        state_str = str(quality)
        if state_str == str(pt.AttrQuality.ATTR_VALID):
            color = self.attrColors.validColor
            state_string = 'VALID'
        elif state_str == str(pt.AttrQuality.ATTR_INVALID):
            color = self.attrColors.invalidColor
            state_string = 'INVALID'
        elif state_str == str(pt.AttrQuality.ATTR_ALARM):
            color = self.attrColors.alarmColor
            state_string = 'ALARM'
        elif state_str == str(pt.AttrQuality.ATTR_WARNING):
            color = self.attrColors.warnColor
            state_string = 'WARNING'
        elif state_str == str(pt.AttrQuality.ATTR_CHANGING):
            color = self.attrColors.changingColor
            state_string = 'CHANGING'
        else:
            color = self.attrColors.unknownColor
            state_string = 'UNKNOWN'

        self.quality = state_string
        self.currentAttrColor = color
        s = ''.join(('QLabel {min-height: ', str(self.sizes.barHeight), 'px; \n',
                     'max-height: ', str(self.sizes.barHeight), 'px; \n',
                     'background-color: ', self.attrColors.backgroundColor, '; \n',
                     'color: ', self.currentAttrColor, ';}'))
        self.setStyleSheet(s)
        self.update()

    def setState(self, state):
        QTangoAttributeBase.setState(self, state)
        self.setText(self.state)


class QTangoAttributeUnitLabel(QtWidgets.QLabel, QTangoAttributeBase):
    def __init__(self, sizes=None, colors=None, parent=None):
        QTangoAttributeBase.__init__(self, sizes, colors, parent)
        QtWidgets.QLabel.__init__(self, parent)
        self.unit_text = ''
        self.currentAttrColor = self.attrColors.secondaryColor0
        self.setupLayout()

    def setupLayout(self):
        self.setText('')

        font = self.font()
        font.setFamily(self.sizes.fontType)
        font.setStretch(self.sizes.fontStretch)
        font.setWeight(self.sizes.fontWeight)
        font.setPointSize(int(self.sizes.barHeight * 0.7))
        font.setStyleStrategy(QtGui.QFont.PreferAntialias)
        self.setFont(font)
        self.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignBottom)
        self.setSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)

        # unit_width = QtGui.QFontMetricsF(font).width('mmmm')
        s = ''.join(('QLabel {min-height: ', str(self.sizes.barHeight), 'px; \n',
                     'max-height: ', str(self.sizes.barHeight), 'px; \n',
                     'background-color: ', self.attrColors.backgroundColor, '; \n',
                     'color: ', self.currentAttrColor, ';}'))
        self.setStyleSheet(s)

    def setText(self, unit_text):
        if unit_text == '':
            txt = 'a.u.'
        else:
            txt = ''.join(('', unit_text, ''))
        self.unit_text = txt
        QtWidgets.QLabel.setText(self, txt)

    def setQuality(self, quality):
        state_str = str(quality)
        if state_str == str(pt.AttrQuality.ATTR_VALID):
            color = self.attrColors.validColor
            state_string = 'VALID'
        elif state_str == str(pt.AttrQuality.ATTR_INVALID):
            color = self.attrColors.invalidColor
            state_string = 'INVALID'
        elif state_str == str(pt.AttrQuality.ATTR_ALARM):
            color = self.attrColors.alarmColor
            state_string = 'ALARM'
        elif state_str == str(pt.AttrQuality.ATTR_WARNING):
            color = self.attrColors.warnColor
            state_string = 'WARNING'
        elif state_str == str(pt.AttrQuality.ATTR_CHANGING):
            color = self.attrColors.changingColor
            state_string = 'CHANGING'
        else:
            color = self.attrColors.unknownColor
            state_string = 'UNKNOWN'

        self.quality = state_string
        self.currentAttrColor = color

        s = ''.join(('QLabel {min-height: ', str(self.sizes.barHeight), 'px; \n',
                     'max-height: ', str(self.sizes.barHeight), 'px; \n',
                     'background-color: ', self.attrColors.backgroundColor, '; \n',
                     'color: ', self.currentAttrColor, ';}'))
        self.setStyleSheet(s)

        self.update()


# noinspection PyAttributeOutsideInit
class QTangoReadAttributeLabel(QtWidgets.QLabel, QTangoAttributeBase):
    def __init__(self, sizes=None, colors=None, precision=4, parent=None):
        QTangoAttributeBase.__init__(self, sizes, colors, parent)
        QtWidgets.QLabel.__init__(self, parent)
        self.precision = precision
        self.data_format = "%6.3f"
        self.suffix = ""
        self.current_value = 0.0
        self.currentAttrColor = self.attrColors.secondaryColor0
        self.setupLayout()

    def setupLayout(self):
        self.setLocale(QtCore.QLocale(QtCore.QLocale.English))
        s = ''.join(('QLabel { \n',
                     'background-color: ', self.attrColors.backgroundColor, '; \n',
                     'selection-background-color: ', self.attrColors.secondaryColor1, '; \n',
                     'selection-color: ', self.attrColors.backgroundColor, '; \n',
                     'border-width: ', str(int(1)), 'px; \n',
                     'border-color: ', self.attrColors.backgroundColor, '; \n',
                     'border-top-style: solid; \n',
                     'border-bottom-style: solid; \n',
                     'border-left-style: double; \n',
                     'border-right-style: solid; \n',
                     'border-radius: 0px; \n',
                     'padding: 0px; \n',
                     'margin: 0px; \n',
                     'min-width: ', str(int(self.sizes.barHeight) * 1), 'px; \n',
                     'max-width: ', str(int(self.sizes.barHeight) * 4), 'px; \n',
                     'min-height: ', str(int(self.sizes.barHeight * 1.3)), 'px; \n',
                     'max-height: ', str(int(self.sizes.barHeight * 1.3)), 'px; \n',
                     'color: ', self.currentAttrColor, ';} \n'))

        font = self.font()
        font.setFamily(self.sizes.fontType)
        font.setStretch(self.sizes.fontStretch)
        font.setWeight(self.sizes.fontWeight)
        font.setPointSize(int(self.sizes.barHeight * 0.7))
        font.setStyleStrategy(QtGui.QFont.PreferAntialias)
        self.setFont(font)
        self.setStyleSheet(s)
        self.setSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)
        self.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignBottom)

        self.validator = FloatValidator()
        self.setDataFormat(self.data_format)

    def setDataFormat(self, data_format):
        if data_format == "int":
            self.data_format = "%d"
            self.validator = IntValidator()
        elif data_format in ["double", "float"]:
            self.data_format = "%6.3f"
            self.validator = FloatValidator()
        else:
            self.data_format = data_format
            if "f" in data_format or "e" in data_format or "g" in data_format:
                self.validator = FloatValidator()
            else:
                self.validator = IntValidator()

    def setValue(self, value):
        if type(value) == pt.DeviceAttribute:
            logger.debug("QTangoReadAttributeLabel::setValue: value {0}, quality {1}".format(value.value, value.quality))
            self.setQuality(value.quality)
            val = value.value

        else:
            val = value
        if val is not None:
            text = self.textFromValue(val * self.prefixFactor)
            QtWidgets.QLabel.setText(self, text)
        else:
            QtWidgets.QLabel.setText(self, "0.0")
        self.current_value = val

    def validate(self, text, position):
        return self.validator.validate(text, position)

    def fixup(self, text):
        return self.validator.fixup(text)

    def valueFromText(self, text):
        return float(text)

    def textFromValue(self, value):
        logger.debug("QTangoReadAttributeLabel::textFromValue: value {0}".format(value))
        # text = "".join((to_precision(value, self.precision), " ", self.suffix))
        if self.data_format[1:] == "d":
            value = int(value)
        text = "".join(("{0:", self.data_format[1:], "} {1}")).format(value, self.suffix)
        return text

    def setSuffix(self, suffix):
        self.suffix = suffix
        self.setValue(self.current_value)

    def setQuality(self, quality):
        state_str = str(quality)
        if state_str == str(pt.AttrQuality.ATTR_VALID):
            color = self.attrColors.validColor
            state_string = 'VALID'
        elif state_str == str(pt.AttrQuality.ATTR_INVALID):
            color = self.attrColors.invalidColor
            state_string = 'INVALID'
        elif state_str == str(pt.AttrQuality.ATTR_ALARM):
            color = self.attrColors.alarmColor
            state_string = 'ALARM'
        elif state_str == str(pt.AttrQuality.ATTR_WARNING):
            color = self.attrColors.warnColor
            state_string = 'WARNING'
        elif state_str == str(pt.AttrQuality.ATTR_CHANGING):
            color = self.attrColors.changingColor
            state_string = 'CHANGING'
        else:
            color = self.attrColors.unknownColor
            state_string = 'UNKNOWN'

        self.quality = state_string
        self.currentAttrColor = color

        s = ''.join(('QLabel { \n',
                     'background-color: ', self.attrColors.backgroundColor, '; \n',
                     'selection-background-color: ', self.attrColors.secondaryColor1, '; \n',
                     'selection-color: ', self.attrColors.backgroundColor, '; \n',
                     'border-width: ', str(int(1)), 'px; \n',
                     'border-color: ', self.attrColors.backgroundColor, '; \n',
                     'border-top-style: solid; \n',
                     'border-bottom-style: solid; \n',
                     'border-left-style: double; \n',
                     'border-right-style: solid; \n',
                     'border-radius: 0px; \n',
                     'padding: 0px; \n',
                     'margin: 0px; \n',
                     'min-width: ', str(int(self.sizes.barHeight) * 1), 'px; \n',
                     'max-width: ', str(int(self.sizes.barHeight) * 4), 'px; \n',
                     'min-height: ', str(int(self.sizes.barHeight * 1.3)), 'px; \n',
                     'max-height: ', str(int(self.sizes.barHeight * 1.3)), 'px; \n',
                     'color: ', self.currentAttrColor, ';} \n'))
        self.setStyleSheet(s)

        self.update()
