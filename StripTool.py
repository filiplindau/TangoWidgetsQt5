# -*- coding:utf-8 -*-
"""
Created on Dec 18, 2017

@author: Filip
"""
from PyQt5 import QtWidgets, QtCore, QtGui, Qt
import PyTango as pt
import pyqtgraph as pg
from pyqtgraph.graphicsItems.LegendItem import ItemSample
from ColorDefinitions import QTangoColors, QTangoSizes
import numpy as np
import time
import sys
from BaseWidgets import QTangoAttributeBase
import logging

logger = logging.getLogger(__name__)
while len(logger.handlers):
    logger.removeHandler(logger.handlers[0])

f = logging.Formatter("%(asctime)s - %(module)s.   %(funcName)s - %(levelname)s - %(message)s")
fh = logging.StreamHandler()
fh.setFormatter(f)
logger.addHandler(fh)
logger.setLevel(logging.DEBUG)


class QTangoStripTool(pg.PlotWidget, QTangoAttributeBase):
    """ Base class for a trend widget.

        The widget stores trend curves that are trended. The duration is set with setDuration (seconds).
        Curves are added with addCurve. New points are added with addPoint.

        If curves are named with setCurveName they can be shown with showLegend.

    """
    def __init__(self, name=None, sizes=None, colors=None, chronological=True, parent=None):
        QTangoAttributeBase.__init__(self, sizes, colors, parent)
        pg.PlotWidget.__init__(self, useOpenGL=True)
        self.values_size = 200000
        self.duration = 600.0
        self.x_values = list()
        self.y_values = list()

        self.legend = None
        self.curve_focus = 0
        self.curve_name_list = list()
        self.curve_vb_list = list()
        self.curve_ax_list = list()
        self.value_trend_curves = list()
        self.current_data_index = list()

        self.trend_menu = None

        self.chronological = chronological

        self.setupLayout(name)
        self.setupTrendMenu()
        self.addCurve(name)
        self.setCurveFocus(0)
        # self.setupData()

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
        pi.sigYRangeChanged.connect(self.updateViews)
        pi.vb.sigResized.connect(self.updateViews)

        color_warn = QtGui.QColor(self.attrColors.warnColor)
        color_warn.setAlphaF(0.75)
        color_good = QtGui.QColor(self.attrColors.secondaryColor0)
        color_good.setAlphaF(0.33)

        self.legend = self.getPlotItem().addLegend()

    def setupData(self, curve=0):
        """ Pre-allocate data arrays
        """
        try:
            # Curve already exists
            self.x_values[curve] = -np.ones(self.values_size) * np.inf
            self.y_values[curve] = np.zeros(self.values_size)
            self.current_data_index[curve] = 0
            logger.debug("Setting up data for curve {0}".format(curve))
            self.value_trend_curves[curve].setData(self.x_values[curve], self.y_values[curve], antialias=True)
        except IndexError:
            # Need to create new arrays
            logger.debug("Adding new data arrays for curve {0}".format(curve))
            self.x_values.append(-np.ones(self.values_size) * np.inf)
            self.y_values.append(np.zeros(self.values_size))
            self.current_data_index.append(0)
            # if len(self.value_trend_curves) < curve + 1:
            #     self.addCurve()
            # self.valueTrendCurves[curve].setData(self.xValues[curve], self.yValues[curve], antialias = True)

    def setupTrendMenu(self):
        pi = self.getPlotItem()
        self.trend_menu = QtWidgets.QMenu()
        self.trend_menu.setTitle("Trend options")
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
        self.trend_menu.addAction(duration_action)
        pi.ctrlMenu = [self.trend_menu, pi.ctrlMenu]

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
        curve_index = len(self.value_trend_curves)
        if name is None:
            name = str(curve_index)
        logger.info("Adding curve {0}, name {1}".format(curve_index, name))
        vb = pg.ViewBox()
        ax = pg.AxisItem("right")
        ax.linkToView(vb)
        ax1 = pg.AxisItem("bottom")
        ax1.linkToView(vb)
        # vb.enableAutoRange("y")
        # vb.setRange(yRange=[-10, 10])
        pi_main = self.getPlotItem()
        pi_main.scene().addItem(vb)
        vb.setXLink(pi_main)
        # vb.setYLink(pi_main)

        curve_new = pg.PlotCurveItem(name=name)
        curve_color = self.attrColors.legend_color_list[curve_index % len(self.attrColors.legend_color_list)]
        curve_new.setPen(curve_color, width=2.0)
        curve_new.setClickable(True)
        vb.addItem(curve_new)

        logger.debug("New curve color: {0}".format(curve_new.opts["pen"].color().getRgb()))

        self.value_trend_curves.append(curve_new)
        self.curve_vb_list.append(vb)
        self.curve_ax_list.append(ax)
        self.curve_name_list.append(name)

        self.legend.addItem(curve_new, name)

        self.setupData(curve_index)

        curve_new.sigClicked.connect(self.setCurveFocus)
        # self.setCurveFocus(name)

        logger.debug("Calling updateViews")
        self.updateViews()

    def updateViews(self):
        logger.info("Updating view")
        pi = self.getPlotItem()
        for ind, vb in enumerate(self.curve_vb_list):
            vb.setGeometry(pi.vb.sceneBoundingRect())
            vb.linkedViewChanged(pi.vb, vb.XAxis)
            if ind == self.curve_focus:
                logger.info("Curve index {0} selected".format(ind))
                vb.linkedViewChanged(pi.vb, vb.YAxis)

    def setCurveFocus(self, curve):
        if isinstance(curve, int):
            name = self.curve_name_list[curve]
            self.curve_focus = curve
        elif isinstance(curve, str):
            name = curve
            self.curve_focus = self.curve_name_list.index(name)
        else:
            name = curve.opts.get('name', None)
            self.curve_focus = self.curve_name_list.index(name)
        logger.debug("Curve {0} selected, index {1}".format(name, self.curve_focus))
        pi = self.getPlotItem()
        axis_viewrange = self.curve_vb_list[self.curve_focus].viewRange()
        logger.debug("Setting view range {0}".format(axis_viewrange[1]))
        pi.vb.setRange(yRange=axis_viewrange[1], padding=0)
        pi_ax = pi.getAxis("right")
        curve_color = self.value_trend_curves[self.curve_focus].opts["pen"].color()
        logger.debug("Axis color: {0}".format(curve_color.getRgb()))
        pi_ax.setPen(curve_color)
        # self.updateViews()

    def showLegend(self, show_legend=True):
        if show_legend is True:
            if self.legend is None:
                self.legend = self.addLegend(offset=(5, 5))
                for it in self.value_trend_curves:
                    self.legend.addItem(it, it.opts.get('name', None))
        else:
            if self.legend is not None:
                self.legend.scene().removeItem(self.legend)
                self.legend = None

    def setCurveName(self, curve, name):
        self.value_trend_curves[curve].opts['name'] = name

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
        if self.current_data_index[curve] == 0:
            x_old = 0.0
        else:
            x_old = self.x_values[curve][self.current_data_index[curve]]
        if (self.chronological is False) or (x_new > x_old):
            # Rescaling if the number of sample is too high
            if self.current_data_index[curve] + 1 >= self.values_size:
                self.current_data_index[curve] = int(self.values_size * 0.75)
                self.x_values[curve][0:self.current_data_index[curve]] = self.x_values[curve][
                                                                         self.values_size - self.current_data_index[
                                                                          curve]:self.values_size]
                self.y_values[curve][0:self.current_data_index[curve]] = self.y_values[curve][
                                                                         self.values_size - self.current_data_index[
                                                                          curve]:self.values_size]
            elif self.current_data_index[curve] == 0:
                self.x_values[curve][0] = x_new
                self.y_values[curve][0] = y_new
            self.current_data_index[curve] += 1
            self.x_values[curve][self.current_data_index[curve]] = x_new
            start_index = np.argmax((self.x_values[curve] - x_new) > -self.duration)
            self.y_values[curve][self.current_data_index[curve]] = y_new
            self.value_trend_curves[curve].setData(self.x_values[curve][start_index:self.current_data_index[curve]] - x_new,
                                                   self.y_values[curve][start_index:self.current_data_index[curve]],
                                                   antialias=True)
            self.update()

    def setData(self, x_data, y_data, curve_index=0, auto_range=True):
        logger.debug("Setting data for curve {0}".format(curve_index))
        self.setupData(curve_index)
        n = x_data.shape[0]
        self.x_values[curve_index][-n:] = x_data
        self.y_values[curve_index][-n:] = y_data
        vb = self.curve_vb_list[curve_index]
        vb.enableAutoRange("y")
        self.value_trend_curves[curve_index].setData(x_data, y_data, antialias=True)
        if auto_range:
            vb.autoRange()
        if self.curve_focus == curve_index:
            pi = self.getPlotItem()
            axis_viewrange = self.curve_vb_list[curve_index].viewRange()
            logger.debug("Setting view range {0}".format(axis_viewrange))
            pi.vb.setRange(yRange=axis_viewrange[1], padding=0)
            pi.vb.setRange(xRange=axis_viewrange[0])
        self.updateViews()


class StripToolSample(QtWidgets.QWidget):


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)

    strip_tool = QTangoStripTool("Test")
    strip_tool.show()
    x_data = np.linspace(-600, 0, 1000)
    y_data = np.sin(2 * np.pi * x_data / 240.0)
    strip_tool.setData(x_data, y_data, 0)

    for c in range(1):
        x_data = np.linspace(-600, 0, 1000)
        y_data = np.sin(2*np.pi*x_data/240.0 * (c + 1)) + 10 * c
        strip_tool.addCurve("Curve {0}".format(c + 1))
        strip_tool.setData(x_data, y_data, c + 1)
        # strip_tool.curve_vb_list[c].setRange(yRange=[c-1, c+1])

    sys.exit(app.exec_())
