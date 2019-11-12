# -*- coding:utf-8 -*-
"""
Created on Dec 18, 2017

@author: Filip
"""
from PyQt5 import QtWidgets, QtCore, QtGui, Qt
import numpy as np
import sys
import PyTango as pt
import pyqtgraph as pg
from ColorDefinitions import QTangoColors, QTangoSizes
import logging
from Utils import to_precision2

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class QTangoAttributeBase(QtWidgets.QWidget):
    """ Base class for all qtango these style widgets.

    Contains variables storing the colors, the state, and the quality (that is, if the attribute is valid, alarm,
    or warning).
    """
    def __init__(self, sizes=None, colors=None, parent=None):
        QtWidgets.QWidget.__init__(self, parent)
        if colors is None:
            self.attrColors = QTangoColors()
        else:
            self.attrColors = colors
        if sizes is None:
            self.sizes = QTangoSizes()
        else:
            self.sizes = sizes

        self.state = 'UNKNOWN'
        self.quality = 'UNKNOWN'
        self.current_attr_color = self.attrColors.secondaryColor0
        self.current_attr_color = self.attrColors.unknownColor

        self.attrInfo = None

        self.prefixDict = {'k': 1e-3, 'M': 1e-6, 'G': 1e-9, 'T': 1e-12, 'P': 1e-15,
                           'm': 1e3, '\u00b5': 1e6, 'n': 1e9, 'p': 1e12, 'f': 1e15, 'c': 1e2}
        self.prefix = None
        self.prefixFactor = 1.0

    def setState(self, state, use_background_color=False):
        if type(state) == pt.DeviceAttribute:
            state_str = str(state.value)
        else:
            state_str = str(state)

        if state_str == str(pt.DevState.OFF):
            color = self.attrColors.offColor
            state_string = 'OFF'
        elif state_str == str(pt.DevState.ON):
            color = self.attrColors.onColor
            state_string = 'ON'
        elif state_str == str(pt.DevState.FAULT):
            color = self.attrColors.faultColor
            state_string = 'FAULT'
        elif state_str == str(pt.DevState.ALARM):
            color = self.attrColors.alarmColor
            state_string = 'ALARM'
        elif state_str == str(pt.DevState.STANDBY):
            color = self.attrColors.standbyColor
            state_string = 'STANDBY'
        elif state_str == str(pt.DevState.UNKNOWN):
            color = self.attrColors.unknownColor
            state_string = 'UNKNOWN'
        elif state_str == str(pt.DevState.DISABLE):
            color = self.attrColors.disableColor
            state_string = 'DISABLE'
        elif state_str == str(pt.DevState.MOVING):
            color = self.attrColors.movingColor
            state_string = 'MOVING'
        elif state_str == str(pt.DevState.RUNNING):
            color = self.attrColors.runningColor
            state_string = 'RUNNING'
        elif state_str == str(pt.AttrQuality.ATTR_WARNING):
            color = self.attrColors.warnColor
            state_string = 'WARNING'
        elif state_str == str(pt.AttrQuality.ATTR_CHANGING):
            color = self.attrColors.changingColor
            state_string = 'CHANGING'
        elif state_str == str(pt.AttrQuality.ATTR_ALARM):
            color = self.attrColors.alarmColor2
            state_string = 'ALARM'
        elif state_str == str(pt.AttrQuality.ATTR_INVALID):
            color = self.attrColors.invalidColor
            state_string = 'INVALID'
        elif state_str == str(pt.AttrQuality.ATTR_VALID):
            color = self.attrColors.validColor
            state_string = 'VALID'
        else:
            color = self.attrColors.unknownColor
            state_string = 'UNKNOWN'

        self.state = state_string
        self.current_attr_color = color

        s = str(self.styleSheet())
        if s != '':
            if use_background_color is True:
                i0 = s.find('\nbackground-color')
            else:
                i0 = s.find('\ncolor')
            i1 = s[i0:].find(':')
            i2 = s[i0:].find(';')
            s_new = ''.join((s[0:i0 + i1 + 1], ' ', color, s[i0 + i2:]))
            self.setStyleSheet(s_new)

        self.update()

    def setQuality(self, quality, use_background_color=False):
        if type(quality) == pt.DeviceAttribute:
            state_str = str(quality.value)
        else:
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
            color = self.attrColors.warnColor2
            state_string = 'WARNING'
        elif state_str == str(pt.AttrQuality.ATTR_CHANGING):
            color = self.attrColors.changingColor
            state_string = 'CHANGING'
        else:
            color = self.attrColors.unknownColor
            state_string = 'UNKNOWN'

        self.quality = state_string
        self.current_attr_color = color

        s = str(self.styleSheet())
        if s != '':
            if use_background_color is True:
                i0 = s.find('\nbackground-color')
            else:
                i0 = s.find('\ncolor')
            i1 = s[i0:].find(':')
            i2 = s[i0:].find(';')
            s_new = ''.join((s[0:i0 + i1 + 1], ' ', color, s[i0 + i2:]))
            self.setStyleSheet(s_new)

        self.update()

    def setupLayout(self):
        pass

    def configureAttribute(self, attr_info):
        self.attrInfo = attr_info

    def setPrefix(self, prefix):
        try:
            self.prefixFactor = self.prefixDict[prefix]
            self.prefix = prefix
        except KeyError:
            self.prefix = None
            self.prefixFactor = 1.0
        logger.info("Setting prefix {0}, factor {1}".format(prefix, self.prefixFactor))


# noinspection PyAttributeOutsideInit
class QTangoHSliderBase(QtWidgets.QSlider, QTangoAttributeBase):
    """ Base class for a horizontal slider widget.

    The slider is a line with a valid section (colored in secondaryColor) and warning sections on either side
    (colored in warnColor). An up pointing arrow points at the read value. Text for current value, min limit,
    and max limit are drawn. If the write value is set, it is drawn as an arrow outline.

    """
    def __init__(self, sizes=None, colors=None, parent=None):
        QTangoAttributeBase.__init__(self, sizes, colors, parent)
        QtWidgets.QSlider.__init__(self, parent)
        self.setupLayout()

    def setupLayout(self):
        self.setMaximum(100)
        self.setMinimum(0)
        self.attrMaximum = 1
        self.attrMinimum = 0
        self.attrValue = 0.5
        self.attrWriteValue = None
        self.warnHigh = 0.9
        self.warnLow = 0.1

        self.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.setMaximumHeight(self.sizes.barHeight)
        self.setMinimumHeight(self.sizes.barHeight)

    def paintEvent(self, e):
        qp = QtGui.QPainter()
        qp.begin(self)
        self.drawWidget(qp)
        qp.end()

    def drawWidget(self, qp):
        size = self.size()
        w = size.width()
        h = size.height()

        start_h = h / 6.0  # Position of horizontal line
        line_w = h / 4.0  # Width of horizontal line
        arrow_w = h / 2.5  # Width of arrow
        write_w = h / 8.0

        # Vertical position of scale text
        text_vert_pos = h
        # Pixel coordinate of current value:
        x_val = w * (self.attrValue - self.attrMinimum) / (self.attrMaximum - self.attrMinimum)

        # Setup font
        font = QtGui.QFont(self.sizes.fontType, self.sizes.barHeight * 0.5, self.sizes.fontWeight)
        font.setStretch(self.sizes.fontStretch)

        # Strings to draw
        s_val = "{:.2f}".format(self.attrValue)
        s_min = "{:.2f}".format(self.attrMinimum)
        s_max = "{:.2f}".format(self.attrMaximum)
        s_val_width = QtGui.QFontMetricsF(font).width(s_val)
        s_min_width = QtGui.QFontMetricsF(font).width(s_min)
        s_max_width = QtGui.QFontMetricsF(font).width(s_max)

        # Position to draw text of current value
        text_point = QtCore.QPointF(x_val + line_w / 2 + h / 5.0, text_vert_pos)
        if x_val < 0:
            text_point.setX(h / 3.0 + h / 16.0)
        if x_val + s_val_width > w:
            text_point.setX(w - s_val_width - h / 3.0 - h / 16.0)
        if x_val < 0:
            # Draw left pointing arrow if the pixel position is < 0
            poly = QtGui.QPolygonF([QtCore.QPointF(0, (start_h + line_w / 2 + h) / 2),
                                    QtCore.QPointF(h / 3.0, h),
                                    QtCore.QPointF(h / 3.0, start_h + line_w / 2)])
        elif x_val > w:
            # Draw right pointing arrow if the pixel position is > w
            poly = QtGui.QPolygonF([QtCore.QPointF(w, (start_h + line_w / 2 + h) / 2),
                                    QtCore.QPointF(w - h / 3.0, h),
                                    QtCore.QPointF(w - h / 3.0, start_h + line_w / 2)])
        else:
            # Draw up pointing arrow otherwise
            poly = QtGui.QPolygonF([QtCore.QPointF(x_val, start_h + line_w / 2.0),
                                    QtCore.QPointF(x_val - arrow_w / 2.0, h),
                                    QtCore.QPointF(x_val + arrow_w / 2.0, h)])

        color_attr = QtGui.QColor(self.attrColors.secondaryColor0)
        color_write_attr = QtGui.QColor(self.attrColors.secondaryColor2)
        color_line = QtGui.QColor(self.attrColors.secondaryColor0)
        pen_attr = QtGui.QPen(color_line)
        pen_attr.setWidthF(line_w)
        brush_attr = QtGui.QBrush(color_line)
        qp.setFont(font)

        color_warn = QtGui.QColor(self.attrColors.warnColor)
        pen_warn = QtGui.QPen(color_warn)
        pen_warn.setWidthF(line_w)
        brush_warn = QtGui.QBrush(color_warn)

        qp.setRenderHint(QtGui.QPainter.Antialiasing, False)  # No antialiasing when drawing horizontal/vertical lines
        qp.setRenderHint(QtGui.QPainter.TextAntialiasing, True)
        qp.setRenderHint(QtGui.QPainter.SmoothPixmapTransform, True)
        # Draw warning line
        qp.setPen(pen_warn)
        qp.setBrush(brush_warn)
        qp.drawLine(0, start_h, w, start_h)
        # Draw line
        qp.setPen(pen_attr)
        qp.setBrush(brush_attr)
        qp.drawLine(w * (self.warnLow - self.attrMinimum) / (self.attrMaximum - self.attrMinimum), start_h,
                    w * (self.warnHigh - self.attrMinimum) / (self.attrMaximum - self.attrMinimum), start_h)

        # Draw arrow
        qp.setRenderHint(QtGui.QPainter.Antialiasing, True)

        # Change color of arrow when in warning range
        # 		if self.attrValue < self.warnLow or self.attrValue > self.warnHigh:
        # 			pen = pen_warn
        # 			brush = brush_warn
        # 			qp.setBrush(brush)
        # 		else:
        # 			pen = pen_attr
        # 			brush = brush_attr
        pen = pen_attr
        pen.setColor(color_attr)
        pen.setWidthF(0)
        qp.setPen(pen)
        qp.drawPolygon(poly)
        if self.attrWriteValue is not None:
            pen.setWidthF(write_w)
            pen.setColor(color_write_attr)
            qp.setPen(pen)
            x_val_w = w * (self.attrWriteValue - self.attrMinimum) / (self.attrMaximum - self.attrMinimum)
            qp.drawLine(x_val_w, h, x_val_w, 0)
        # Draw texts
        # Don't draw the limit texts if the value text is overlapping
        pen.setColor(color_attr)
        qp.setPen(pen)
        if x_val - arrow_w / 2 > s_min_width:
            qp.drawText(QtCore.QPointF(0, text_vert_pos), s_min)
        if text_point.x() < w - s_max_width:
            qp.drawText(QtCore.QPointF(w - s_max_width, text_vert_pos), s_max)

    def setValue(self, value):
        if type(value) == pt.DeviceAttribute:
            self.setQuality(value.quality)
            if value.value is not None:
                val = 0.0
            else:
                val = value.value
        else:
            val = value
        self.attrValue = val
        self.update()

    def setWriteValue(self, value):
        self.attrWriteValue = value
        self.update()

    def setWarningLimits(self, limits):
        if type(limits) == pt.AttributeInfoListEx:
            warn_high = limits[0].alarms.max_warning
            warn_low = limits[0].alarms.min_warning
        else:
            warn_low = limits[0]
            warn_high = limits[1]
        self.warnHigh = warn_high
        self.warnLow = warn_low
        self.update()

    def setSliderLimits(self, attr_min, attr_max):
        self.attrMinimum = attr_min
        self.attrMaximum = attr_max
        self.update()


# noinspection PyAttributeOutsideInit
class QTangoHSliderBase2(QtWidgets.QSlider, QTangoAttributeBase):
    """ Second version base class for a horizontal slider widget.

        The slider is a line with a valid section (colored in secondaryColor) and warning sections on either side
        (colored in warnColor). An up pointing arrow points at the read value. Text for current value, min limit,
        and max limit are drawn. If the write value is set, it is drawn as an arrow outline.

        """
    def __init__(self, sizes=None, colors=None, parent=None):
        QTangoAttributeBase.__init__(self, sizes, colors, parent)
        QtWidgets.QSlider.__init__(self, parent)
        self.setupLayout()

    def setupLayout(self):
        self.setMaximum(100)
        self.setMinimum(0)
        self.attr_maximum = 1
        self.attr_minimum = 0
        self.attr_value = 0.5
        self.attr_write_value = None
        self.warnHigh = 0.9
        self.warnLow = 0.1
        self.unit = "a.u."

        self.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.setMaximumHeight(self.sizes.barHeight * 1.0)
        self.setMinimumHeight(self.sizes.barHeight * 1.0)

    def paintEvent(self, e):
        qp = QtGui.QPainter()
        qp.begin(self)
        self.drawWidget(qp)
        qp.end()

    def drawWidget(self, qp):
        size = self.size()
        w = size.width()
        h = size.height()

        start_h = h / 6.0  # Position of horizontal line
        line_w = h / 4.0  # Width of horizontal line
        arrow_w = h / 2.5  # Width of arrow

        # Vertical position of scale text
        text_vert_pos = start_h + self.sizes.barHeight * 0.5 + line_w / 2 + 1

        # Pixel coordinate of current value:
        x_val = w * (self.attr_value - self.attr_minimum) / (self.attr_maximum - self.attr_minimum)

        # Setup font
        font = QtGui.QFont('Calibri', self.sizes.barHeight * 0.5, self.sizes.fontWeight)

        # Strings to draw
        s_val = "{:.2f}".format(self.attr_value)
        s_min = "{:.2f}".format(self.attr_minimum)
        s_max = "{:.2f}".format(self.attr_maximum)
        s_val_width = QtGui.QFontMetricsF(font).width(s_val)
        s_min_width = QtGui.QFontMetricsF(font).width(s_min)
        s_max_width = QtGui.QFontMetricsF(font).width(s_max)

        # Position to draw text of current value
        text_point = QtCore.QPointF(x_val + line_w / 2 + h / 5.0, text_vert_pos)
        if x_val < 0:
            text_point.setX(h / 3.0 + h / 16.0)
        if x_val + s_val_width > w:
            text_point.setX(w - s_val_width - h / 3.0 - h / 16.0)
        if x_val < 0:
            # Draw left pointing arrow if the pixel position is < 0
            poly = QtGui.QPolygonF([QtCore.QPointF(0, (start_h + line_w / 2 + h) / 2),
                                    QtCore.QPointF(h / 3.0, h),
                                    QtCore.QPointF(h / 3.0, start_h + line_w / 2)])
        elif x_val > w:
            # Draw right pointing arrow if the pixel position is > w
            poly = QtGui.QPolygonF([QtCore.QPointF(w, (start_h + line_w / 2 + h) / 2),
                                    QtCore.QPointF(w - h / 3.0, h),
                                    QtCore.QPointF(w - h / 3.0, start_h + line_w / 2)])
        else:
            # Draw up pointing arrow otherwise
            poly = QtGui.QPolygonF([QtCore.QPointF(x_val, start_h + line_w / 2.0),
                                    QtCore.QPointF(x_val - arrow_w / 2.0, h),
                                    QtCore.QPointF(x_val + arrow_w / 2.0, h)])

        color_attr = QtGui.QColor(self.attrColors.secondaryColor0)
        color_write_attr = QtGui.QColor(self.attrColors.secondaryColor2)
        color_line = QtGui.QColor(self.attrColors.secondaryColor0)
        pen_attr = QtGui.QPen(color_line)
        pen_attr.setWidthF(line_w)
        brush_attr = QtGui.QBrush(color_line)
        qp.setFont(font)

        color_warn = QtGui.QColor(self.attrColors.warnColor)
        pen_warn = QtGui.QPen(color_warn)
        brush_warn = QtGui.QBrush(color_warn)

        # Draw write value arrow
        qp.setRenderHint(QtGui.QPainter.Antialiasing, True)

        pen = pen_attr
        pen.setColor(color_attr)
        pen.setWidthF(0)
        qp.setPen(pen)
        qp.setBrush(brush_attr)
        qp.drawPolygon(poly)
        if self.attr_write_value is not None:
            pen.setWidthF(2)
            pen.setColor(color_write_attr)
            qp.setPen(pen)
            x_val_w = w * (self.attr_write_value - self.attr_minimum) / (self.attr_maximum - self.attr_minimum)

            poly_w = QtGui.QPolygonF([QtCore.QPointF(x_val_w - arrow_w / 2.0 - 4, h),
                                     QtCore.QPointF(x_val_w - 4, start_h + line_w / 2.0 - 1),
                                     QtCore.QPointF(x_val_w + 4, start_h + line_w / 2.0 - 1),
                                     QtCore.QPointF(x_val_w + arrow_w / 2.0 + 4, h)])

            qp.drawPolyline(poly_w)

        pen.setColor(color_attr)
        pen.setWidthF(2)
        qp.setPen(pen)
        qp.drawPolygon(poly)

        # Draw texts
        # Don't draw the limit texts if the value text is overlapping
        pen.setColor(color_attr)
        qp.setPen(pen)
        if x_val - arrow_w / 2 > s_min_width:
            qp.drawText(QtCore.QPointF(2, text_vert_pos), s_min)
        if text_point.x() < w - s_max_width:
            qp.drawText(QtCore.QPointF(w - s_max_width - 2, text_vert_pos), s_max)

        qp.setRenderHint(QtGui.QPainter.Antialiasing, False)  # No antialiasing when drawing horizontal/vertical lines
        qp.setRenderHint(QtGui.QPainter.TextAntialiasing, True)
        qp.setRenderHint(QtGui.QPainter.SmoothPixmapTransform, True)

        # Draw warning line
        pen_warn.setWidthF(line_w)
        qp.setPen(pen_warn)
        qp.setBrush(brush_warn)
        qp.drawLine(0, start_h, w, start_h)
        # Draw line
        pen_attr = QtGui.QPen(color_line)
        pen_attr.setWidthF(line_w)
        brush_attr = QtGui.QBrush(color_line)
        qp.setPen(pen_attr)
        qp.setBrush(brush_attr)
        qp.drawLine(
            QtCore.QPointF(w * (self.warnLow - self.attr_minimum) / (self.attr_maximum - self.attr_minimum), start_h),
            QtCore.QPointF(w * (self.warnHigh - self.attr_minimum) / (self.attr_maximum - self.attr_minimum), start_h))
        # Draw start and end point lines
        pen_attr.setWidthF(1)
        if self.warnLow > self.attr_minimum:
            pen_attr.setColor(color_warn)
        qp.setPen(pen_attr)
        qp.drawLine(0, start_h, 0, start_h + line_w * 2)
        if self.warnHigh > self.attr_maximum:
            pen_attr.setColor(color_line)
            qp.setPen(pen_attr)
        qp.drawLine(w - 1, start_h, w - 1, start_h + line_w * 2)

    def setValue(self, value):
        if type(value) == pt.DeviceAttribute:
            self.setQuality(value.quality)
            if value.value is not None:
                val = value.value
            else:
                val = 0.0
        else:
            val = value
        self.attr_value = val
        self.update()

    def setWriteValue(self, value):
        self.attr_write_value = value
        self.update()

    def setWarningLimits(self, limits):
        if type(limits) == pt.AttributeInfoListEx:
            warn_high = limits[0].alarms.max_warning
            warn_low = limits[0].alarms.min_warning
        else:
            warn_low = limits[0]
            warn_high = limits[1]
        self.warnHigh = warn_high
        self.warnLow = warn_low
        self.update()

    def setSliderLimits(self, attr_min, attr_max):
        self.attr_minimum = attr_min
        self.attr_maximum = attr_max
        self.update()

    def setUnit(self, a_unit):
        self.unit = a_unit
        self.update()


# noinspection PyAttributeOutsideInit
class QTangoHSliderBaseCompact(QtWidgets.QSlider, QTangoAttributeBase):
    """ Base class for a compact horizontal slider widget.

        The widget is made as vertically compact as possible.
        The slider is a line with a valid section (colored in secondaryColor) and warning sections on either side
        (colored in warnColor). A line marks the read value. No text is drawn. The write value is not drawn.

        """
    def __init__(self, sizes=None, colors=None, parent=None):
        QTangoAttributeBase.__init__(self, sizes, colors, parent)
        QtWidgets.QSlider.__init__(self, parent)
        self.setupLayout()

    def setupLayout(self):
        self.setMaximum(100)
        self.setMinimum(0)
        self.attrMaximum = 1
        self.attrMinimum = 0
        self.attrValue = 0.5
        self.attrWriteValue = None
        self.warnHigh = 0.9
        self.warnLow = 0.1

        self.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.setMaximumHeight(self.sizes.barHeight * 0.3)
        self.setMinimumHeight(self.sizes.barHeight * 0.3)

    def paintEvent(self, e):
        qp = QtGui.QPainter()
        qp.begin(self)
        self.drawWidget(qp)
        qp.end()

    def drawWidget(self, qp):
        size = self.size()
        w = size.width()
        h = size.height()

        start_h = h / 2.0  # Position of horizontal line
        line_w = h * 0.6  # Width of horizontal line
        arrow_w = h * 0.5  # Width of indicator

        # Pixel coordinate of current value:
        x_val = w * (self.attrValue - self.attrMinimum) / (self.attrMaximum - self.attrMinimum)

        # color_attr = QtGui.QColor(self.attrColors.secondaryColor0)
        color_line = QtGui.QColor(self.attrColors.secondaryColor0)
        pen_attr = QtGui.QPen(color_line)
        pen_attr.setWidthF(line_w)
        # brush_attr = QtGui.QBrush(color_line)

        color_warn = QtGui.QColor(self.attrColors.warnColor)
        pen_warn = QtGui.QPen(color_warn)
        brush_warn = QtGui.QBrush(color_warn)

        qp.setRenderHint(QtGui.QPainter.Antialiasing, False)  # No antialiasing when drawing horizontal/vertical lines

        # Draw warning line
        pen_warn.setWidthF(line_w)
        qp.setPen(pen_warn)
        qp.setBrush(brush_warn)
        qp.drawLine(0, int(start_h), w, int(start_h))
        # Draw line
        pen_attr = QtGui.QPen(color_line)
        pen_attr.setWidthF(line_w)
        brush_attr = QtGui.QBrush(color_line)
        qp.setPen(pen_attr)
        qp.setBrush(brush_attr)
        qp.drawLine(
            QtCore.QPointF(w * (self.warnLow - self.attrMinimum) / (self.attrMaximum - self.attrMinimum),
                           int(start_h)),
            QtCore.QPointF(w * (self.warnHigh - self.attrMinimum) / (self.attrMaximum - self.attrMinimum),
                           int(start_h)))
        # Draw indicator
        pen_ind = QtGui.QPen(QtCore.Qt.black)
        pen_ind.setWidthF(3 * arrow_w)
        brush_ind = QtGui.QBrush(QtCore.Qt.white)
        qp.setPen(pen_ind)
        qp.setBrush(brush_ind)
        qp.drawLine(QtCore.QPointF(x_val, start_h - line_w / 2.0 - 1),
                    QtCore.QPointF(x_val, start_h + line_w / 2.0 + 1))
        pen_ind.setWidthF(arrow_w)
        pen_ind.setColor(QtCore.Qt.white)
        qp.setPen(pen_ind)
        qp.setBrush(brush_ind)
        qp.drawLine(QtCore.QPointF(x_val, start_h - line_w / 2.0 - 1),
                    QtCore.QPointF(x_val, start_h + line_w / 2.0 + 1))

    def setValue(self, value):
        if type(value) == pt.DeviceAttribute:
            self.setQuality(value.quality)
            if value.value is not None:
                val = value.value
            else:
                val = 0.0
        else:
            val = value
        self.attrValue = val
        self.update()

    def setWriteValue(self, value):
        self.attrWriteValue = value
        self.update()

    def setWarningLimits(self, limits):
        if type(limits) == pt.AttributeInfoListEx:
            warn_high = limits[0].alarms.max_warning
            warn_low = limits[0].alarms.min_warning
        else:
            warn_low = limits[0]
            warn_high = limits[1]
        self.warnHigh = warn_high
        self.warnLow = warn_low
        self.update()

    def setSliderLimits(self, attr_min, attr_max):
        self.attrMinimum = attr_min
        self.attrMaximum = attr_max
        self.update()


# noinspection PyAttributeOutsideInit
class QTangoVSliderBase2(QtWidgets.QSlider, QTangoAttributeBase):
    """ Base class for a vertical slider widget.

        The slider is a line with a valid section (colored in secondaryColor) and warning sections on either side
        (colored in warnColor). A left pointing arrow points at the read value. Text for current value, min limit,
        and max limit are drawn. If the write value is set, it is drawn as an arrow outline.

    """
    def __init__(self, sizes=None, colors=None, parent=None):
        QTangoAttributeBase.__init__(self, sizes, colors, parent)
        QtWidgets.QSlider.__init__(self, parent)
        self.unit = ""
        self.setupLayout()

    def setupLayout(self):
        self.setMaximum(100)
        self.setMinimum(0)
        self.attrMaximum = 1
        self.attrMinimum = 0
        self.attrValue = 0.5
        self.attrWriteValue = None
        self.warnHigh = 0.9
        self.warnLow = 0.1

        self.setSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.setMaximumWidth(self.sizes.barWidth * 5.0 - 2)
        self.setMinimumWidth(self.sizes.barWidth * 5.0 - 2)

    def paintEvent(self, e):
        qp = QtGui.QPainter()
        qp.begin(self)
        self.drawWidget(qp)
        qp.end()

    def drawWidget(self, qp):
        size = self.size()
        w = size.width()
        h = size.height()

        # Setup font
        font = QtGui.QFont(self.sizes.fontType, self.sizes.barHeight * 0.75, self.sizes.fontWeight)
        font.setStretch(self.sizes.fontStretch)
        font.setStyleStrategy(QtGui.QFont.PreferAntialias)

        # Strings to draw
        # s_val = ''.join(("{:.4g}".format(self.attrValue), " ", self.unit))
        # s_val = "{0:.4g} {1}{2}".format(self.attrValue, self.prefix, self.unit)
        # s_min = "{:.4g}".format(self.attrMinimum)
        # s_max = "{:.4g}".format(self.attrMaximum)
        s_val = u"{0}{1}".format(to_precision2(self.attrValue, p=2, w=5, neg_compensation=False), self.unit)
        s_min = "{0}".format(to_precision2(self.attrMinimum, p=0, w=4, neg_compensation=False, return_prefix_string=True))
        s_max = "{0}".format(to_precision2(self.attrMaximum, p=0, w=4, neg_compensation=False, return_prefix_string=True))

        # Width of value text:
        # s_val_width = QtGui.QFontMetricsF(font).width(s_val)
        # Height of the text:
        s_val_height = QtGui.QFontMetricsF(font).height()
        # Width of the min scale text:
        # s_min_width = QtGui.QFontMetricsF(font).width(s_min)
        # Width of the max scale text:
        # s_max_width = QtGui.QFontMetricsF(font).width(s_max)

        start_x = 0.0  # Position of vertical line
        line_w = w / 8.0  # Width of vertical line
        # arrow_w = s_val_height / 2.0
        arrow_w = 1.25 * s_val_height / 2.0
        write_w = 6.0

        # Vertical position of scale text
        # text_vert_pos = start_x + self.sizes.barHeight * 0.5 + line_w / 2 + 1

        # Pixel coordinate of current value:
        y_val = h - h * (self.attrValue - self.attrMinimum) / (self.attrMaximum - self.attrMinimum)

        # Position to draw text of current value
        text_point = QtCore.QPointF(start_x + line_w / 2 + arrow_w, y_val + s_val_height * 0.3)
        # Check if text is outside the bounds of the slider
        if y_val - arrow_w < 0:
            text_point.setY(0.8 * s_val_height)
        if y_val + arrow_w > h:
            text_point.setY(h - s_val_height * 0.2)

        if self.quality == "ALARM":
            color_attr = QtGui.QColor(self.attrColors.alarmColor)
            color_write_attr = QtGui.QColor(self.attrColors.alarmColor)
            color_line = QtGui.QColor(self.attrColors.alarmColor2)
            pen = QtGui.QPen(color_line)
            pen_attr = QtGui.QPen(color_attr)
            pen_attr.setWidthF(line_w)
            brush_attr = QtGui.QBrush(color_attr, QtCore.Qt.NoBrush)
            qp.setFont(font)

            color_warn = QtGui.QColor(self.attrColors.alarmColor)
            pen_warn = QtGui.QPen(color_warn)
            brush_warn = QtGui.QBrush(color_warn, QtCore.Qt.NoBrush)

        elif self.quality == "WARNING":
            color_attr = QtGui.QColor(self.attrColors.warnColor2)
            color_write_attr = QtGui.QColor(self.attrColors.secondaryColor2)
            color_line = QtGui.QColor(self.attrColors.secondaryColor0)
            pen = QtGui.QPen(color_line)
            pen_attr = QtGui.QPen(color_attr)
            pen_attr.setWidthF(line_w)
            brush_attr = QtGui.QBrush(color_attr, QtCore.Qt.NoBrush)
            qp.setFont(font)

            color_warn = QtGui.QColor(self.attrColors.warnColor)
            pen_warn = QtGui.QPen(color_warn)
            brush_warn = QtGui.QBrush(color_warn)
        else:
            color_attr = QtGui.QColor(self.attrColors.secondaryColor0)
            color_write_attr = QtGui.QColor(self.attrColors.secondaryColor2)
            color_line = QtGui.QColor(self.attrColors.secondaryColor0)
            pen = QtGui.QPen(color_line)
            pen_attr = QtGui.QPen(color_line)
            pen_attr.setWidthF(line_w)
            brush_attr = QtGui.QBrush(color_line, QtCore.Qt.NoBrush)
            qp.setFont(font)

            color_warn = QtGui.QColor(self.attrColors.warnColor)
            pen_warn = QtGui.QPen(color_warn)
            brush_warn = QtGui.QBrush(color_warn)

        # Draw anti-aliased
        qp.setRenderHint(QtGui.QPainter.Antialiasing, True)
        qp.setRenderHint(QtGui.QPainter.TextAntialiasing, True)

        pen_attr.setWidthF(1.5)
        qp.setPen(pen_attr)
        qp.setBrush(brush_attr)

        # Check if the arrow is outside the bounds of the slider
        if y_val < 0:
            # Draw up pointing arrow if the pixel position is < 0
            arrow_poly = QtGui.QPolygonF([QtCore.QPointF(start_x + line_w / 2 + arrow_w / 2.0, arrow_w / 4.0),
                                         QtCore.QPointF(start_x + line_w / 2.0, 0.0),
                                         QtCore.QPointF(start_x + line_w / 2.0 + arrow_w, 2 * arrow_w),
                                         QtCore.QPointF(w - 1.0, 2 * arrow_w)])
            qp.drawPolyline(arrow_poly)
        elif y_val - arrow_w < 0:
            # Intermediate position, draw modified arrow
            arrow_poly = QtGui.QPolygonF([QtCore.QPointF(start_x + line_w / 2.0, y_val),
                                         QtCore.QPointF(start_x + line_w / 2.0 + arrow_w, 2 * arrow_w),
                                         QtCore.QPointF(w - 1.0, 2 * arrow_w),
                                         QtCore.QPointF(w - 1.0, 0.0),
                                         QtCore.QPointF(start_x + line_w / 2.0 + arrow_w, 0.0)])
            qp.drawPolygon(arrow_poly)
        elif y_val > h:
            # Draw down pointing arrow if the pixel position is > h
            arrow_poly = QtGui.QPolygonF([QtCore.QPointF(start_x + line_w / 2 + arrow_w / 2.0, h - arrow_w / 4.0),
                                         QtCore.QPointF(start_x + line_w / 2.0, h),
                                         QtCore.QPointF(start_x + line_w / 2.0 + arrow_w, h - 2 * arrow_w),
                                         QtCore.QPointF(w - 1.0, h - 2 * arrow_w)])
            qp.drawPolyline(arrow_poly)
        elif y_val + arrow_w > h:
            # Intermediate position, draw modified arrow
            arrow_poly = QtGui.QPolygonF([QtCore.QPointF(start_x + line_w / 2.0, y_val),
                                         QtCore.QPointF(start_x + line_w / 2.0 + arrow_w, h),
                                         QtCore.QPointF(w - 1.0, h),
                                         QtCore.QPointF(w - 1.0, h - 2 * arrow_w),
                                         QtCore.QPointF(start_x + line_w / 2.0 + arrow_w, h - 2 * arrow_w)])
            qp.drawPolygon(arrow_poly)
        else:
            # Draw left pointing arrow otherwise
            arrow_poly = QtGui.QPolygonF([QtCore.QPointF(start_x + line_w / 2.0, y_val),
                                         QtCore.QPointF(start_x + line_w / 2.0 + arrow_w, y_val + arrow_w),
                                         QtCore.QPointF(w - 1.0, y_val + arrow_w),
                                         QtCore.QPointF(w - 1.0, y_val - arrow_w),
                                         QtCore.QPointF(start_x + line_w / 2.0 + arrow_w, y_val - arrow_w)])
            qp.drawPolygon(arrow_poly)

        # Write value arrow
        if self.attrWriteValue is not None:
            pen.setWidthF(2.5)
            pen.setColor(color_write_attr)
            qp.setPen(pen)
            write_y_val = h - h * (self.attrWriteValue - self.attrMinimum) / (self.attrMaximum - self.attrMinimum)

            poly_w = QtGui.QPolygonF([QtCore.QPointF(start_x + line_w / 2.0 + arrow_w, write_y_val + arrow_w + write_w),
                                     QtCore.QPointF(start_x + line_w / 2.0, write_y_val + write_w),
                                     QtCore.QPointF(start_x + line_w / 2.0, write_y_val - write_w),
                                     QtCore.QPointF(start_x + line_w / 2.0 + arrow_w, write_y_val - arrow_w - write_w)])

            qp.drawPolyline(poly_w)

        #
        # Draw texts
        #

        # Draw value text
        pen.setColor(color_attr)
        qp.setPen(pen)
        qp.drawText(text_point, s_val)

        # Draw slider scale texts
        # Don't draw the limit texts if the value text is overlapping
        font.setPointSizeF(self.sizes.barHeight * 0.5)

        qp.setRenderHint(QtGui.QPainter.TextAntialiasing, True)
        qp.setFont(font)
        pen.setColor(color_line)
        qp.setPen(pen)
        if y_val + arrow_w / 2 < h - s_val_height:
            qp.drawText(QtCore.QPointF(start_x + line_w, h - s_val_height * 0.2), s_min)
        if y_val - arrow_w / 2 > s_val_height:
            qp.drawText(QtCore.QPointF(start_x + line_w, s_val_height * 0.6), s_max)

        qp.setRenderHint(QtGui.QPainter.Antialiasing, False)  # No antialiasing when drawing horizontal/vertical lines
        qp.setRenderHint(QtGui.QPainter.TextAntialiasing, True)
        qp.setRenderHint(QtGui.QPainter.SmoothPixmapTransform, True)

        # Draw warning line
        pen_warn.setWidthF(line_w)
        qp.setPen(pen_warn)
        qp.setBrush(brush_warn)
        qp.drawLine(start_x, 0, start_x, h)
        # Draw line
        pen_attr = QtGui.QPen(color_line)
        pen_attr.setWidthF(line_w)
        brush_attr = QtGui.QBrush(color_line)
        qp.setPen(pen_attr)
        qp.setBrush(brush_attr)
        qp.drawLine(
            QtCore.QPointF(start_x, h - h * (self.warnLow - self.attrMinimum) / (self.attrMaximum - self.attrMinimum)),
            QtCore.QPointF(start_x, h - h * (self.warnHigh - self.attrMinimum) / (self.attrMaximum - self.attrMinimum)))
        # Draw start and end point lines
        pen_attr.setWidthF(1)
        if self.warnLow > self.attrMinimum:
            pen_attr.setColor(color_warn)
        qp.setPen(pen_attr)
        qp.drawLine(start_x, h - 1, start_x + line_w * 2, h - 1)
        if self.warnHigh > self.attrMaximum:
            pen_attr.setColor(color_line)
            qp.setPen(pen_attr)
        qp.drawLine(start_x, 0, start_x + line_w * 2, 0)

    def setValue(self, value):
        if type(value) == pt.DeviceAttribute:
            self.setQuality(value.quality)
            if value.value is not None:
                val = value.value
            else:
                val = 0.0
        else:
            val = value
        # self.attrValue = val * self.prefixFactor
        self.attrValue = val
        self.update()

    def setWriteValue(self, value):
        self.attrWriteValue = value
        self.update()

    def setWarningLimits(self, limits):
        if type(limits) == pt.AttributeInfoListEx:
            warn_high = limits[0].alarms.max_warning
            warn_low = limits[0].alarms.min_warning
        else:
            warn_low = limits[0]
            warn_high = limits[1]
        self.warnHigh = warn_high
        self.warnLow = warn_low
        self.update()

    def setSliderLimits(self, min_limit, max_limit):
        self.attrMinimum = min_limit
        self.attrMaximum = max_limit
        self.update()

    def setUnit(self, a_unit):
        self.unit = a_unit
        self.update()


# noinspection PyAttributeOutsideInit,PyAttributeOutsideInit
class QTangoTrendBase(pg.PlotWidget, QTangoAttributeBase):
    """ Base class for a trend widget.

        The widget stores trend curves that are trended. The duration is set with setDuration (seconds).
        Curves are added with addCurve. New points are added with addPoint.

        If curves are named with setCurveName they can be shown with showLegend.

    """
    def __init__(self, name=None, sizes=None, colors=None, chronological=True, parent=None):
        QTangoAttributeBase.__init__(self, sizes, colors, parent)
        pg.PlotWidget.__init__(self, useOpenGL=True)
        self.valuesSize = 200000
        self.duration = 600.0
        self.xValues = []
        self.yValues = []

        self.legend = None
        self.curve_focus = 0
        self.curve_name_list = []

        self.chronological = chronological

        self.setupLayout(name)
        self.setupData()

    def setupLayout(self, name=None):
        self.setXRange(-self.duration, 0)
        self.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        pi = self.getPlotItem()
        ax_left = pi.getAxis('left')
        ax_left.setPen(self.attrColors.secondaryColor0)
        pi.hideAxis('left')
        ax_bottom = pi.getAxis('bottom')
        ax_bottom.setPen(self.attrColors.secondaryColor0)

        ax_right = pi.getAxis('right')
        ax_right.setPen(self.attrColors.secondaryColor0)
        # 		ax_right.setWidth(0)
        # 		ax_right.setTicks([])
        # 		ax_right.showLabel(False)
        pi.showAxis('right')

        color_warn = QtGui.QColor(self.attrColors.warnColor)
        color_warn.setAlphaF(0.75)
        color_good = QtGui.QColor(self.attrColors.secondaryColor0)
        color_good.setAlphaF(0.33)
        # brushWarn = QtGui.QBrush(color_warn, style=QtCore.Qt.SolidPattern)
        # brushGood = QtGui.QBrush(color_good, style=QtCore.Qt.SolidPattern)
        # penLines = QtGui.QPen(QtGui.QColor('#55555500'))

        # high_lim = 1e9

        # 		self.warningRegionUpper = pg.LinearRegionItem(values=[high_lim, high_lim],
        #                                                   orientation = pg.LinearRegionItem.Horizontal,
        # 													brush = brushWarn, movable = False)
        # 		self.warningRegionUpper.lines[0].setPen(penLines)
        # 		self.warningRegionUpper.lines[1].setPen(penLines)
        # 		self.warningRegionLower = pg.LinearRegionItem(values=[-high_lim, -high_lim],
        #                                                   orientation = pg.LinearRegionItem.Horizontal,
        # 													brush = brushWarn, movable = False)
        # 		self.warningRegionLower.lines[0].setPen(penLines)
        # 		self.warningRegionLower.lines[1].setPen(penLines)
        # 		self.goodRegion = pg.LinearRegionItem(values=[-high_lim, high_lim],
        #                                                   orientation = pg.LinearRegionItem.Horizontal,
        # 													brush = brushGood, movable = False)
        # 		self.goodRegion.lines[0].setPen(penLines)
        # 		self.goodRegion.lines[1].setPen(penLines)
        # 		self.addItem(self.warningRegionUpper)
        # 		self.addItem(self.warningRegionLower)
        # 		self.addItem(self.goodRegion)
        self.valueTrendCurves = []
        self.currentDataIndex = []

        self.trendMenu = QtWidgets.QMenu()
        self.trendMenu.setTitle("Trend options")
        duration_action = QtWidgets.QWidgetAction(self)
        duration_widget = QtWidgets.QWidget()
        duration_layout = QtWidgets.QHBoxLayout()
        duration_label = QtWidgets.QLabel("Duration / s")
        duration_spinbox = QtWidgets.QDoubleSpinBox()
        duration_spinbox.setMaximum(3e7)
        duration_spinbox.setValue(self.duration)
        duration_spinbox.setMinimumWidth(40)
        duration_spinbox.editingFinished.connect(self.setDurationContext)

        duration_layout.addWidget(duration_label)
        duration_layout.addWidget(duration_spinbox)
        duration_widget.setLayout(duration_layout)
        duration_action.setDefaultWidget(duration_widget)
        self.trendMenu.addAction(duration_action)
        pi.ctrlMenu = [self.trendMenu, pi.ctrlMenu]

        self.addCurve(name)

    def setupData(self, curve=0):
        """ Pre-allocate data arrays
        """
        if len(self.xValues) > curve + 1:
            # Curve already exists
            self.xValues[curve] = -np.ones(self.valuesSize) * np.inf
            self.yValues[curve] = np.zeros(self.valuesSize)
            self.currentDataIndex[curve] = 0
            self.valueTrendCurves[curve].setData(self.xValues[curve], self.yValues[curve], antialias=True)
        else:
            # Need to create new arrays
            self.xValues.append(-np.ones(self.valuesSize) * np.inf)
            self.yValues.append(np.zeros(self.valuesSize))
            self.currentDataIndex.append(0)
            if len(self.valueTrendCurves) < curve + 1:
                self.addCurve()
            # self.valueTrendCurves[curve].setData(self.xValues[curve], self.yValues[curve], antialias = True)

    def setWarningLimits(self, limits):
        if type(limits) == pt.AttributeInfoListEx:
            warn_high = limits[0].alarms.max_warning
            warn_low = limits[0].alarms.min_warning
        else:
            warn_low = limits[0]
            warn_high = limits[1]
        self.warningRegionUpper.setRegion([warn_high, 1e6])
        self.warningRegionLower.setRegion([-1e6, warn_low])
        self.goodRegion.setRegion([warn_low, warn_high])

    def configureAttribute(self, attr_info):
        QTangoAttributeBase.configureAttribute(self, attr_info)
        try:
            min_warning = float(self.attrInfo.alarms.min_warning)
        except ValueError:
            min_warning = -np.inf
        try:
            max_warning = float(self.attrInfo.alarms.max_warning)
        except ValueError:
            max_warning = np.inf
        self.setWarningLimits((min_warning, max_warning))
        self.setUnit(self.attrInfo.unit)

    def setDuration(self, duration):
        """ Set the duration of the trend graph in x axis units
        (e.g. samples, seconds...)
        """
        self.duration = duration
        self.setXRange(-self.duration, 0)

    def setDurationContext(self):
        """ Set the duration of the trend graph in x axis units
        (e.g. samples, seconds...) from the context menu
        """
        w = self.sender()
        duration = w.value()
        self.duration = duration
        self.setXRange(-self.duration, 0)

    def addCurve(self, name=None):
        curve_index = len(self.valueTrendCurves)
        if name is not None:
            new_curve = self.plot(name=name)
            self.curve_name_list.append(name)
        else:
            new_curve = self.plot(name=str(curve_index))
            self.curve_name_list.append(str(curve_index))
        curve_color = self.attrColors.legend_color_list[curve_index % len(self.attrColors.legend_color_list)]
        new_curve.setPen(curve_color, width=2.0)
        new_curve.curve.setClickable(True)
        self.valueTrendCurves.append(new_curve)

        self.setupData(len(self.valueTrendCurves) - 1)

        new_curve.sigClicked.connect(self.setCurveFocus)

    def setCurveFocus(self, curve):
        name = curve.opts.get('name', None)

    def showLegend(self, show_legend=True):
        if show_legend is True:
            if self.legend is None:
                self.legend = self.addLegend(offset=(5, 5))
                for it in self.valueTrendCurves:
                    self.legend.addItem(it, it.opts.get('name', None))
        else:
            if self.legend is not None:
                self.legend.scene().removeItem(self.legend)
                self.legend = None

    def setCurveName(self, curve, name):
        self.valueTrendCurves[curve].opts['name'] = name

    def addPoint(self, data, curve=0):
        if type(data) == pt.DeviceAttribute:
            x_new = data.time.totime()
            y_new = data.value
        else:
            x_new = data[0]
            y_new = data[1]
        # Check x_new against last x to see if it is increasing.
        # Sometimes there is a bug with wrong time values that are very much lower
        # than the old value (probably 0)
        if self.currentDataIndex[curve] == 0:
            x_old = 0.0
        else:
            x_old = self.xValues[curve][self.currentDataIndex[curve]]
        if (self.chronological is False) or (x_new > x_old):
            # Rescaling if the number of sample is too high
            if self.currentDataIndex[curve] + 1 >= self.valuesSize:
                self.currentDataIndex[curve] = int(self.valuesSize * 0.75)
                self.xValues[curve][0:self.currentDataIndex[curve]] = self.xValues[curve][
                                                                      self.valuesSize - self.currentDataIndex[
                                                                          curve]:self.valuesSize]
                self.yValues[curve][0:self.currentDataIndex[curve]] = self.yValues[curve][
                                                                      self.valuesSize - self.currentDataIndex[
                                                                          curve]:self.valuesSize]
            elif self.currentDataIndex[curve] == 0:
                self.xValues[curve][0] = x_new
                self.yValues[curve][0] = y_new
            self.currentDataIndex[curve] += 1
            self.xValues[curve][self.currentDataIndex[curve]] = x_new
            start_index = np.argmax((self.xValues[curve] - x_new) > -self.duration)
            self.yValues[curve][self.currentDataIndex[curve]] = y_new
            self.valueTrendCurves[curve].setData(self.xValues[curve][start_index:self.currentDataIndex[curve]] - x_new,
                                                 self.yValues[curve][start_index:self.currentDataIndex[curve]],
                                                 antialias=True)
            self.update()


# noinspection PyAttributeOutsideInit,PyAttributeOutsideInit
class QTangoSpectrumBase(pg.PlotWidget, QTangoAttributeBase):
    """ Base class for a spectrum (line plot) widget.

        At creation one curve is added. Additional curves can be added using addCurve. Curves can be named
        with names displayed using showLegend.

    """
    def __init__(self, sizes=None, colors=None, parent=None):
        QTangoAttributeBase.__init__(self, sizes, colors, parent)
        pg.PlotWidget.__init__(self, useOpenGL=True)

        self.legend = None
        self.warnHigh = np.inf
        self.warnLow = -np.inf
        self.setupLayout()

    def setupLayout(self):
        self.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        pi = self.getPlotItem()
        pi.hideAxis('left')
        pi.showAxis('right', True)
        pi.showGrid(True, True, 0.2)
        ax_left = pi.getAxis('right')
        ax_left.setPen(self.attrColors.secondaryColor0)
        ax_bottom = pi.getAxis('bottom')
        ax_bottom.setPen(self.attrColors.secondaryColor0)

        self.spectrumCurves = [self.plot()]
        self.spectrumNames = ['']
        self.spectrumCurves[0].setPen(self.attrColors.secondaryColor0, width=2.0)

        self.useOpenGL(True)
        self.setAntialiasing(True)
        br = pg.mkBrush(self.attrColors.backgroundColor)
        self.setBackgroundBrush(br)

    def setSpectrum(self, x_data, y_data, index=0):
        self.spectrumCurves[index].setData(y=y_data, x=x_data, antialias=False)
        self.update()

    def showLegend(self, state):
        pi = self.getPlotItem()
        if state is True:
            if self.legend is None:
                self.legend = pi.addLegend()
                for ind, cur in enumerate(self.spectrumCurves):
                    self.legend.addItem(cur, self.spectrumNames[ind])
        else:
            if self.legend is not None:
                self.legend.scene().removeItem(self.legend)
                self.legend = None

    def setCurveName(self, index, name):
        self.spectrumNames[index] = name
        if self.legend is not None:
            self.legend.removeItem(name)
            self.legend.addItem(self.spectrumCurves[index], self.spectrumNames[index])

    def addPlot(self, color, name='', ignore_bounds=False):
        p = self.plot(ignoreBounds=ignore_bounds)
        p.setPen(color, width=2.0)
        self.spectrumCurves.append(p)
        self.spectrumNames.append(name)

    def setWarningLimits(self, limits):
        if type(limits) == pt.AttributeInfoListEx:
            warn_high = limits[0].alarms.max_warning
            warn_low = limits[0].alarms.min_warning
        else:
            warn_low = limits[0]
            warn_high = limits[1]
        self.warnHigh = warn_high
        self.warnLow = warn_low
        self.update()


class QTangoImageWithHistBase(pg.ImageView):
    """ Base class for a image widget.



        """
    def __init__(self, sizes=None, colors=None, parent=None):
        if colors is None:
            self.attrColors = QTangoColors()
        else:
            self.attrColors = colors
        if sizes is None:
            self.sizes = QTangoSizes()
        else:
            self.sizes = sizes

        pg.ImageView.__init__(self)

        self.setupLayout()

    def setupLayout(self):
        self.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)


class QTangoImageBase(pg.GraphicsView):
    def __init__(self, sizes=None, colors=None, parent=None):
        if colors is None:
            self.attrColors = QTangoColors()
        else:
            self.attrColors = colors
        if sizes is None:
            self.sizes = QTangoSizes()
        else:
            self.sizes = sizes

        pg.GraphicsView.__init__(self)

        self.vb = pg.ViewBox(lockAspect=1.0, invertY=True)
        self.setCentralItem(self.vb)
        self.image = pg.ImageItem()
        self.vb.addItem(self.image)

        grad_editor = pg.GradientEditorItem()
        # 		for t in list(grad_editor.ticks.keys()):
        # 			grad_editor.removeTick(t, finish = False)
        # 		grad_editor.addTick(0.0, QtGui.QColor(0, 0, 0), movable = False, finish = False)
        # 		grad_editor.addTick(0.3333, QtGui.QColor(0, 80, 255), movable = False, finish = False)
        # 		grad_editor.addTick(0.6667, QtGui.QColor(102, 203, 255), movable = False, finish = False)
        # 		grad_editor.addTick(1.0, QtGui.QColor(255, 255, 255), movable = False, finish = False)
        grad_editor.loadPreset('flame')
        self.lut = grad_editor.getLookupTable(256)

        self.setupLayout()

    def setupLayout(self):
        self.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)

    def setImage(self, image, auto_levels=False):
        if image is not None:
            if type(image) == pt.DeviceAttribute:
                data = image.value
                if image.quality == pt.AttrQuality.ATTR_VALID:
                    grad_editor = pg.GradientEditorItem()
                    grad_editor.loadPreset('flame')
                    self.lut = grad_editor.getLookupTable(256)
                else:
                    grad_editor = pg.GradientEditorItem()
                    grad_editor.loadPreset('gray')
                    self.lut = grad_editor.getLookupTable(8)
            else:
                data = image
            self.image.setImage(np.transpose(data), autoLevels=auto_levels, lut=self.lut, autoDownSample=True)
            self.update()
