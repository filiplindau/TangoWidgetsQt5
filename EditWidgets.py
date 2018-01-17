# -*- coding:utf-8 -*-
"""
Created on Dec 18, 2017

@author: Filip
"""
from PyQt5 import QtWidgets, QtCore, QtGui
import PyTango as pt
import numpy as np
import re
from BaseWidgets import QTangoAttributeBase
from ColorDefinitions import QTangoColors, QTangoSizes
from Utils import format_float, FloatValidator
import logging

logger = logging.getLogger(__name__)

# Regular expression to find floats. Match groups are the whole string, the
# whole coefficient, the decimal part of the coefficient, and the exponent
# part.
_float_re = re.compile(r'(([+-]?\d+(\.\d*)?|\.\d+)([eE][+-]?\d+)?)')


# noinspection PyAttributeOutsideInit
class QTangoReadAttributeSpinBox(QTangoAttributeBase, QtWidgets.QDoubleSpinBox):
    def __init__(self, sizes=None, colors=None, parent=None):
        QtWidgets.QDoubleSpinBox.__init__(self, parent)
        QTangoAttributeBase.__init__(self, sizes, colors, parent)
        self.attrColors = colors
        self.sizes = sizes
        self.state = 'UNKNOWN'
        self.quality = 'UNKNOWN'
        self.current_attr_color = self.attrColors.secondaryColor0
        self.current_attr_color = self.attrColors.unknownColor

        logger.debug("QTangoReadAttributeSpinBox: init")
        self.setupLayout()
        logger.debug("QTangoReadAttributeSpinBox: init done")

    def setupLayout(self):
        self.setLocale(QtCore.QLocale(QtCore.QLocale.English))
        s = ''.join(('QDoubleSpinBox { \n',
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
                     'qproperty-buttonSymbols: NoButtons; \n',
                     'min-width: ', str(int(self.sizes.barHeight) * 1), 'px; \n',
                     'max-width: ', str(int(self.sizes.barHeight) * 4), 'px; \n',
                     'min-height: ', str(int(self.sizes.barHeight * 1.3)), 'px; \n',
                     'max-height: ', str(int(self.sizes.barHeight * 1.3)), 'px; \n',
                     'qproperty-readOnly: 1; \n',
                     ';} \n'))

        logger.debug("QTangoReadAttributeSpinBox: stylesheet")

        font = self.font()
        font.setFamily(self.sizes.fontType)
        font.setStretch(self.sizes.fontStretch)
        font.setWeight(self.sizes.fontWeight)
        font.setPointSize(int(self.sizes.barHeight * 0.7))
        font.setStyleStrategy(QtGui.QFont.PreferAntialias)
        self.setFont(font)
        self.setStyleSheet(s)
        self.setSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)
        logger.debug("QTangoReadAttributeSpinBox: font")

        # self.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignBottom)
        # self.setMaximum(np.inf)
        # self.setMinimum(-np.inf)



        # self.validator = FloatValidator()

        logger.debug("QTangoReadAttributeSpinBox: validator")

    def setValue(self, value):
        if type(value) == pt.DeviceAttribute:
            self.setQuality(value.quality)
            val = value.value
        else:
            val = value
        if val is not None:
            QtWidgets.QDoubleSpinBox.setValue(self, val)
        else:
            QtWidgets.QDoubleSpinBox.setValue(self, 0.0)

    def validate(self, text, position):
        return self.validator.validate(text, position)

    def fixup(self, text):
        return self.validator.fixup(text)

    def valueFromText(self, text):
        return float(text)

    def textFromValue(self, value):
        return format_float(value)

    def stepBy(self, steps):
        text = self.cleanText()
        groups = _float_re.search(text).groups()
        decimal = float(groups[1])
        decimal += steps
        new_string = "{:g}".format(decimal) + (groups[3] if groups[3] else "")
        self.lineEdit().setText(new_string)


# noinspection PyAttributeOutsideInit
class QTangoWriteAttributeLineEdit(QtWidgets.QLineEdit, QTangoAttributeBase):
    """ A line edit for input of values to a tango attribute. Will emit a signal newValueSignal
    when enter is pressed.
    """
    newValueSignal = QtCore.pyqtSignal()

    def __init__(self, sizes=None, colors=None, parent=None):
        QTangoAttributeBase.__init__(self, sizes, colors, parent)
        QtWidgets.QLineEdit.__init__(self, parent)

        self.storedCursorPos = 0
        self.lastKey = QtCore.Qt.Key_0

        self.dataValue = 1.0
        self.dataFormat = "{:.4g}"
        self.dataFormat = "%.4g"

        self.setupLayout()

    def setupLayout(self):
        s = ''.join(('QLineEdit { \n',
                     'background-color: ', self.attrColors.backgroundColor, '; \n',
                     'selection-background-color: ', self.attrColors.secondaryColor1, '; \n',
                     'selection-color: ', self.attrColors.backgroundColor, '; \n',
                     #            'border-width: ', str(int(self.sizes.barHeight/10)), 'px; \n',
                     'border-width: ', str(int(1)), 'px; \n',
                     'border-color: ', self.attrColors.secondaryColor0, '; \n',
                     'border-top-style: solid; \n',
                     'border-bottom-style: solid; \n',
                     'border-left-style: double; \n',
                     'border-right-style: solid; \n',
                     'border-radius: 0px; \n',
                     'padding-top: 0px; \n',
                     'padding-bottom: 0px; \n',
                     'padding-left: 0px; \n',
                     'padding-right: ', str(int(self.sizes.barHeight/5)), 'px; \n',
                     'margin: 0px; \n',
                     'min-width: ', str(int(self.sizes.barHeight) * 1), 'px; \n',
                     'max-width: ', str(int(self.sizes.barHeight) * 4), 'px; \n',
                     'min-height: ', str(int(self.sizes.barHeight * 1.3)), 'px; \n',
                     'max-height: ', str(int(self.sizes.barHeight * 1.3)), 'px; \n',
                     'qproperty-readOnly: 0; \n',
                     'color: ', self.attrColors.secondaryColor0, ';} \n'))
        font = self.font()
        font.setFamily(self.sizes.fontType)
        font.setStretch(self.sizes.fontStretch)
        font.setWeight(self.sizes.fontWeight)
        font.setPointSize(int(self.sizes.barHeight * 0.7))
        font.setStyleStrategy(QtGui.QFont.PreferAntialias)
        self.setFont(font)

        self.setStyleSheet(s)
        # self.setColors(self.attrColors.secondaryColor1, self.attrColors.backgroundColor)
        self.setSizePolicy(QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Minimum)
        self.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)

        self.validatorObject = QtGui.QDoubleValidator()
        self.validatorObject.setNotation(QtGui.QDoubleValidator.ScientificNotation)

    def setColors(self, attr_color_name, background_color_name):
        background_color = self.attrColors.__getattribute__(background_color_name)
        main_color = self.attrColors.__getattribute__(attr_color_name)
        s = ''.join(('QLineEdit { \n',
                     'background-color: ', background_color, '; \n',
                     'selection-background-color: ', main_color, '; \n',
                     'selection-color: ', background_color, '; \n',
                     'border-width: ', str(int(1)), 'px; \n',
                     'border-color: ', main_color, '; \n',
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
                     'qproperty-readOnly: 0; \n',
                     'color: ', main_color, ';} \n'))

        self.setStyleSheet(s)

    def value(self):
        if self.validatorObject.validate(self.text(), 0)[0] == QtGui.QValidator.Acceptable:
            return np.double(self.text())
        else:
            return self.dataValue

    def setValue(self, value):
        self.dataValue = value
        # s_val = self.dataFormat.format(value)
        s_val = "".join(("{0:", self.dataFormat[1:], "}")).format(value)
        self.setText(s_val)

    def keyPressEvent(self, event):
        # Record keypress to check if it was return in changeStep
        if type(event) == QtGui.QKeyEvent:
            self.lastKey = event.key()
            if event.key() == QtCore.Qt.Key_Up or event.key() == QtCore.Qt.Key_Down:
                txt = str(self.text()).lower()
                if self.validatorObject.validate(self.text(), 0)[0] == QtGui.QValidator.Acceptable:
                    self.dataValue = np.double(self.text())

                comma_pos = txt.find('.')
                exp_pos = txt.find('e')
                if comma_pos < 0:
                    # Compensate if there is no comma
                    if exp_pos < 0:
                        # No exponent
                        comma_pos = txt.__len__()
                    else:
                        comma_pos = exp_pos
                cursor_pos = self.cursorPosition()
                cursor_decimal_pos = comma_pos - cursor_pos
                logger.debug("In keyPressEvent: decimal pos {0}".format(cursor_decimal_pos))
                logger.debug("In keyPressEvent: comma pos {0}".format(comma_pos))
                logger.debug("In keyPressEvent: cursor pos {0}".format(cursor_pos))
                logger.debug("In keyPressEvent: exp pos {0}".format(exp_pos))
                logger.debug("In keyPressEvent: old dataValue {0}".format(self.dataValue))

                # Compensate for the length of the comma character if we are to left of the comma
                if cursor_decimal_pos < 0:
                    logger.debug("In keyPressEvent: New decimal pos {0}".format(cursor_decimal_pos))
                    new_decimal_pos = cursor_decimal_pos + 1
                else:
                    new_decimal_pos = cursor_decimal_pos

                if cursor_pos <= exp_pos or exp_pos < 0:
                    # We are adjusting decimal value
                    # 				print txt, pos
                    # Find exponent value:
                    if exp_pos > 0:
                        exp_value = float(txt[exp_pos + 1:])
                    else:
                        exp_value = 0
                    if event.key() == QtCore.Qt.Key_Up:
                        step_dir = 1
                    else:
                        step_dir = -1
                    self.dataValue += step_dir * 10 ** (exp_value + new_decimal_pos)
                    logger.debug("In keyPressEvent: New decimal pos {0}".format(new_decimal_pos))
                    logger.debug("In keyPressEvent: Step {0}".format(step_dir * 10 ** new_decimal_pos))
                    logger.debug("In keyPressEvent: New decimal dataValue {0}".format(self.dataValue))

                    # txt = self.dataFormat.format(self.dataValue)
                    txt = "".join(("{0:", self.dataFormat[1:], "}")).format(self.dataValue)
                    new_comma_pos = txt.find('.')
                    if new_comma_pos < 0:
                        # There is no comma (integer)
                        new_comma_pos = txt.__len__()
                        txt += '.'
                    if cursor_decimal_pos < 0:
                        new_cursor_pos = new_comma_pos - cursor_decimal_pos
                    else:
                        new_cursor_pos = new_comma_pos - cursor_decimal_pos
                    logger.debug("In keyPressEvent: New cursor pos {0}".format(new_cursor_pos))
                    # Check if the new number was truncated due to trailing zeros being removed
                    if new_cursor_pos > txt.__len__() - 1:
                        logger.debug("In keyPressEvent: Adding {0} zeros".format(new_cursor_pos - txt.__len__()))
                        txt += '0' * (new_cursor_pos - txt.__len__())
                    self.clear()
                    self.insert(txt)
                    self.setCursorPosition(new_cursor_pos)

                else:
                    # We are adjusting exponent value
                    logger.debug("In keyPressEvent: Adjusting exponent")
                    cursor_exp_pos = txt.__len__() - cursor_pos
                    logger.debug("In keyPressEvent: New cursor exp pos {0}".format(cursor_exp_pos))
                    if event.key() == QtCore.Qt.Key_Up:
                        self.dataValue *= 10 ** (cursor_exp_pos + 1)
                    else:
                        self.dataValue /= 10 ** (cursor_exp_pos + 1)

                        logger.debug("In keyPressEvent: New decimal dataValue {0}".format(self.dataValue))
                    # txt = self.dataFormat.format(self.dataValue)
                    txt = "".join(("{0:", self.dataFormat[1:], "}")).format(self.dataValue)
                    self.clear()
                    self.insert(txt)

            elif event.key() in [QtCore.Qt.Key_Enter, QtCore.Qt.Key_Return]:
                logger.debug("In keyPressEvent: Enter pressed")
                if self.validatorObject.validate(self.text(), 0)[0] == QtGui.QValidator.Acceptable:
                    self.dataValue = np.double(self.text())
                logger.debug("In keyPressEvent: validated")
                self.newValueSignal.emit()
                logger.debug("In keyPressEvent: signal emitted")
                # This fires an editingFinished event
                super(QTangoWriteAttributeLineEdit, self).keyPressEvent(event)
                logger.debug("In keyPressEvent: editing finished")

            elif event.key() in [QtCore.Qt.Key_Right]:
                # This is to add another zero if we press right while at the right edge of the field
                cursor_pos = self.cursorPosition()
                txt = str(self.text()).lower()
                if self.validatorObject.validate(self.text(), 0)[0] == QtGui.QValidator.Acceptable:
                    self.dataValue = np.double(self.text())
                logger.debug("In keyPressEvent: Cursor pos {0}".format(cursor_pos))
                if cursor_pos == txt.__len__():
                    # We are at the right edge so add a zero if it is a decimal number
                    comma_pos = txt.find('.')
                    exp_pos = txt.find('e')
                    if exp_pos < 0:
                        # There is no exponent, so ok to add zero
                        if comma_pos < 0:
                            # Compensate if there is no comma
                            txt += '.'
                            comma_pos = txt.__len__()
                        txt += '0'
                        self.clear()
                        self.insert(txt)
                else:
                    # We were not at the right edge, so process normally
                    super(QTangoWriteAttributeLineEdit, self).keyPressEvent(event)

            else:
                super(QTangoWriteAttributeLineEdit, self).keyPressEvent(event)


class QTangoWriteAttributeSpinBox(QtWidgets.QDoubleSpinBox):
    def __init__(self, sizes=None, colors=None, parent=None):
        QtWidgets.QDoubleSpinBox.__init__(self, parent)
        self.setLocale(QtCore.QLocale(QtCore.QLocale.English))

        # 		Setting up event handling:
        self.lineEdit().cursorPositionChanged.connect(self.changeStep)
        self.lineEdit().updateWriteValue.connect(self.editReady)
        self.lineEdit().returnPressed.connect(self.editReady)
        self.setKeyboardTracking(False)
        self.valueChanged.connect(self.valueReady)
        self.editingFinished.connect(self.editReady)

        self.storedCursorPos = 0
        self.lastKey = QtCore.Qt.Key_0
        if colors is None:
            self.attrColors = QTangoColors()
        else:
            self.attrColors = colors
        if sizes is None:
            self.sizes = QTangoSizes()
        else:
            self.sizes = sizes
        s = ''.join(('QDoubleSpinBox { \n',
                     'background-color: ', self.attrColors.backgroundColor, '; \n',
                     'selection-background-color: ', self.attrColors.secondaryColor0, '; \n',
                     'selection-color: ', self.attrColors.backgroundColor, '; \n',
                     'border-width: ', str(int(self.sizes.barHeight / 10)), 'px; \n',
                     'border-color: ', self.attrColors.secondaryColor0, '; \n',
                     'border-top-style: none; \n',
                     'border-bottom-style: none; \n',
                     'border-left-style: double; \n',
                     'border-right-style: solid; \n',
                     'border-radius: 0px; \n',
                     'padding: 0px; \n',
                     'margin: 0px; \n',
                     'qproperty-buttonSymbols: NoButtons; \n',
                     'min-width: ', str(int(self.sizes.barHeight) * 2.5), 'px; \n',
                     'max-width: ', str(int(self.sizes.barHeight) * 2.5), 'px; \n',
                     'min-height: ', str(int(self.sizes.barHeight)), 'px; \n',
                     'max-height: ', str(int(self.sizes.barHeight)), 'px; \n',
                     'qproperty-readOnly: 0; \n',
                     'color: ', self.attrColors.secondaryColor0, ';} \n'))
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
        self.setMaximum(1e9)
        self.setMinimum(-1e9)

    def valueReady(self, value):
        logger.debug("Value ready:: {0}".format(value))
        self.lineEdit().setCursorPosition(self.storedCursorPos)

    def editReady(self):
        logger.debug("Edit ready::")
        logger.debug("Cursor pos set to {0}".format(self.storedCursorPos))
        self.lineEdit().setCursorPosition(self.storedCursorPos)

    def stepBy(self, steps):
        logger.debug("Step: {0}".format(steps))
        logger.debug("Value: {0}".format(self.value()))
        logger.debug("Text: {0}".format(self.valueFromText(self.text())))
        txt = self.text()
        current_value = self.valueFromText(txt)
        comma_pos = str(txt).find('.')
        self.storedCursorPos = self.lineEdit().cursorPosition()
        pos = comma_pos - self.storedCursorPos + 1
        if pos + self.decimals() < 0:
            pos = -self.decimals()
        elif pos > 0:
            pos -= 1
        self.setValue(current_value + 10 ** pos * steps)

    def changeStep(self, old, new):
        logger.debug("In changeStep::")

    def keyPressEvent(self, event):
        # Record keypress to check if it was return in changeStep
        if type(event) == QtGui.QKeyEvent:
            self.lastKey = event.key()
        super(QTangoWriteAttributeSpinBox, self).keyPressEvent(event)

    def setColors(self, attr_color_name, background_color_name):
        background_color = self.attrColors.__getattribute__(background_color_name)
        main_color = self.attrColors.__getattribute__(attr_color_name)
        s = ''.join(('QDoubleSpinBox { \n',
                     'background-color: ', background_color, '; \n',
                     'selection-background-color: ', main_color, '; \n',
                     'selection-color: ', background_color, '; \n',
                     'border-width: 1px; \n',
                     'border-color: ', main_color, '; \n',
                     'border-style: solid; \n',
                     'border-radius: 0px; \n',
                     'padding: 0px; \n',
                     'margin: 0px; \n',
                     'qproperty-buttonSymbols: NoButtons; \n',
                     'min-width: ', str(self.sizes.barWidth), 'px; \n',
                     'max-width: ', str(self.sizes.barWidth), 'px; \n',
                     'min-height: ', str(int(self.sizes.barHeight - 2)), 'px; \n',
                     'max-height: ', str(int(self.sizes.barHeight - 2)), 'px; \n',
                     'qproperty-readOnly: 0; \n',
                     'color: ', main_color, ';} \n'))

        self.setStyleSheet(s)


class QTangoWriteAttributeSpinBox2(QtWidgets.QDoubleSpinBox):
    def __init__(self, sizes=None, colors=None, parent=None):
        QtWidgets.QDoubleSpinBox.__init__(self, parent)
        self.setLocale(QtCore.QLocale(QtCore.QLocale.English))

        # 		Setting up event handling:
        self.lineEdit().cursorPositionChanged.connect(self.changeStep)
        self.lineEdit().updateWriteValue.connect(self.editReady)
        self.lineEdit().returnPressed.connect(self.editReady)
        self.setKeyboardTracking(False)
        self.valueChanged.connect(self.valueReady)
        self.editingFinished.connect(self.editReady)

        self.storedCursorPos = 0
        self.lastKey = QtCore.Qt.Key_0
        if colors is None:
            self.attrColors = QTangoColors()
        else:
            self.attrColors = colors
        if sizes is None:
            self.sizes = QTangoSizes()
        else:
            self.sizes = sizes
        s = ''.join(('QDoubleSpinBox { \n',
                     'background-color: ', self.attrColors.backgroundColor, '; \n',
                     'selection-background-color: ', self.attrColors.secondaryColor1, '; \n',
                     'selection-color: ', self.attrColors.backgroundColor, '; \n',
                     'border-width: ', str(int(1)), 'px; \n',
                     'border-color: ', self.attrColors.secondaryColor0, '; \n',
                     'border-top-style: solid; \n',
                     'border-bottom-style: solid; \n',
                     'border-left-style: double; \n',
                     'border-right-style: solid; \n',
                     'border-radius: 0px; \n',
                     'padding: 0px; \n',
                     'margin: 0px; \n',
                     'qproperty-buttonSymbols: UpDownArrows; \n',
                     'min-width: ', str(int(self.sizes.barHeight) * 1), 'px; \n',
                     'max-width: ', str(int(self.sizes.barHeight) * 4), 'px; \n',
                     'min-height: ', str(int(self.sizes.barHeight * 1.2)), 'px; \n',
                     'max-height: ', str(int(self.sizes.barHeight * 1.2)), 'px; \n',
                     'qproperty-readOnly: 0; \n',
                     'color: ', self.attrColors.secondaryColor0, ';} \n'))
        font = self.font()
        font.setFamily(self.sizes.fontType)
        font.setStretch(self.sizes.fontStretch)
        font.setWeight(self.sizes.fontWeight)
        font.setPointSize(int(self.sizes.barHeight * 0.7))
        font.setStyleStrategy(QtGui.QFont.PreferAntialias)
        self.setFont(font)

        self.setStyleSheet(s)
        self.setSizePolicy(QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Minimum)
        self.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        self.setMaximum(1e9)
        self.setMinimum(-1e9)

    def valueReady(self, value):
        logger.debug("Value ready:: {0}".format(value))
        self.lineEdit().setCursorPosition(self.storedCursorPos)

    def editReady(self):
        logger.debug("Edit ready::")
        logger.debug("Cursor pos set to {0}".format(self.storedCursorPos))
        self.lineEdit().setCursorPosition(self.storedCursorPos)

    def stepBy(self, steps):
        logger.debug("In QTangoWriteAttributeSpinBox2.stepBy")
        logger.debug("Step: {0}".format(steps))
        logger.debug("Value: {0}".format(self.value()))
        logger.debug("Text: {0}".format(self.valueFromText(self.text())))
        txt = self.text()
        current_value = self.valueFromText(txt)
        comma_pos = str(txt).find('.')
        self.storedCursorPos = self.lineEdit().cursorPosition()
        pos = comma_pos - self.storedCursorPos + 1
        logger.debug("stepBy::comma pos: {0}".format(comma_pos))
        logger.debug("stepBy::stored pos: {0}".format(self.storedCursorPos))
        logger.debug("stepBy::cursor pos: {0}".format(self.lineEdit().cursorPosition()))
        if pos + self.decimals() < 0:
            pos = -self.decimals()
        elif pos > 0:
            pos -= 1
        self.setValue(current_value + 10 ** pos * steps)

    def changeStep(self):
        logging.debug("In QTangoWriteAttributeSpinBox2.changeStep")
        # Check if the last key was return, then the cursor
        # shouldn't change
        if self.lastKey != QtCore.Qt.Key_Return:
            txt = str(self.text())
            comma_pos = txt.find('.')
            pos = comma_pos - self.storedCursorPos + 1
            logger.debug("stepBy::pos: {0}".format(pos))
            logger.debug("stepBy::comma pos: {0}".format(comma_pos))
            logger.debug("stepBy::stored pos: {0}".format(self.storedCursorPos))
            if pos + self.decimals() < 0:
                pos = -self.decimals()
            elif pos > 0:
                pos -= 1

    def keyPressEvent(self, event):
        # Record keypress to check if it was return in changeStep
        if type(event) == QtGui.QKeyEvent:
            self.lastKey = event.key()
        super(QTangoWriteAttributeSpinBox2, self).keyPressEvent(event)

    def setColors(self, attr_color_name, background_color_name):
        main_color = self.attrColors.__getattribute__(background_color_name)
        background_color = self.attrColors.__getattribute__(attr_color_name)
        s = ''.join(('QDoubleSpinBox { \n',
                     'background-color: ', background_color, '; \n',
                     'selection-background-color: ', main_color, '; \n',
                     'selection-color: ', background_color, '; \n',
                     'border-width: 1px; \n',
                     'border-color: ', main_color, '; \n',
                     'border-style: solid; \n',
                     'border-radius: 0px; \n',
                     'padding: 0px; \n',
                     'margin: 0px; \n',
                     'qproperty-buttonSymbols: NoButtons; \n',
                     'min-width: ', str(self.sizes.barWidth), 'px; \n',
                     'max-width: ', str(self.sizes.barWidth), 'px; \n',
                     'min-height: ', str(int(self.sizes.barHeight - 2)), 'px; \n',
                     'max-height: ', str(int(self.sizes.barHeight - 2)), 'px; \n',
                     'qproperty-readOnly: 0; \n',
                     'color: ', main_color, ';} \n'))

        self.setStyleSheet(s)
