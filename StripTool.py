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
from collections import OrderedDict
from BaseWidgets import QTangoAttributeBase
from Utils import to_precision2
import logging

logger = logging.getLogger(__name__)
while len(logger.handlers):
    logger.removeHandler(logger.handlers[0])

f = logging.Formatter("%(asctime)s - %(module)s.   %(funcName)s - %(levelname)s - %(message)s")
fh = logging.StreamHandler()
fh.setFormatter(f)
logger.addHandler(fh)
logger.setLevel(logging.DEBUG)


class QTangoStripTool(QTangoAttributeBase):
    def __init__(self, name=None, legend_pos="bottom", sizes=None, colors=None, chronological=True, parent=None):
        QTangoAttributeBase.__init__(self, sizes, colors, parent)
        self.setObjectName(self.__class__.__name__)
        self.colors = colors    # type: QTangoColors
        self.sizes = sizes
        self.name = name

        self.plot_widget = QTangoStripToolPlotWidget(name, sizes, colors, chronological)
        self.plot_widget.get_curve(0).sigClicked.connect(self.set_curve_focus)
        logger.debug("Plot widget created")
        self.legend_widget = QTangoStripToolLegendWidget(legend_pos, sizes, colors)
        legend_item = QTangoStripToolLegendItem(name, unit="m", sizes=self.sizes, colors=self.colors)
        legend_item.clicked.connect(self.set_curve_focus)
        self.legend_widget.addItem(legend_item)
        logger.debug("Legend widget created")

        self.set_legend_position(legend_pos)

        s = str(self.styleSheet())
        use_background_color = True
        color = self.attrColors.backgroundColor
        st = """QTangoStripTool {{
                      border-width: 0px;
                      border-color: {0};
                      border-style: solid;
                      border-radius: 0px;
                      adding: 2px;
                      margin: 1px;
                      color: {0};
                      background-color: {1};
                      }}""".format(self.attrColors.secondaryColor0, self.attrColors.backgroundColor)
        self.setStyleSheet(st)
        legend_item.clicked.emit()

    def add_curve(self, name):
        curve_new = self.plot_widget.addCurve(name)
        curve_new.sigClicked.connect(self.set_curve_focus)
        plot_color = curve_new.opts["pen"].color().name()
        logger.debug("Adding curve {0} with color {1}".format(name, plot_color))
        legend_item = QTangoStripToolLegendItem(name, unit="m", color=plot_color, sizes=self.sizes, colors=self.colors)
        legend_item.clicked.connect(self.set_curve_focus)
        self.legend_widget.addItem(legend_item)

    def set_data(self, x_data, y_data, curve_index=0, auto_range=True):
        logger.debug("{0}: curve_index {1}".format(self.__class__, curve_index))
        self.plot_widget.setData(x_data, y_data, curve_index, auto_range)
        legend_item = self.legend_widget.get_item(curve_index)
        axis_range = self.plot_widget.get_curve_range(curve_index)
        legend_item.set_range(axis_range[1])

    def set_curve_focus(self):
        s = self.sender()
        if isinstance(s, QTangoStripToolLegendItem):
            logger.debug("{0}: Signal from {1}".format(self.__class__, s.name))
            ind = self.legend_widget.get_item_index(s)
            logger.debug("Legend item index {0}".format(ind))
            self.plot_widget.setCurveFocus(ind)
            self.legend_widget.set_focus_item(ind)
        else:
            ind = self.plot_widget.get_curve_focus_ind()
            self.plot_widget.get_curve_color(ind)
            self.legend_widget.set_focus_item(ind)

    def set_legend_position(self, position):
        try:
            for w in range(2):
                self.layout().takeAt(0)
        except AttributeError:
            pass
        if position == "top":
            lay = QtWidgets.QVBoxLayout()
            lay.addWidget(self.legend_widget)
            lay.addWidget(self.plot_widget)
        elif position == "bottom":
            lay = QtWidgets.QVBoxLayout()
            lay.addWidget(self.plot_widget)
            lay.addWidget(self.legend_widget)
        elif position == "right":
            lay = QtWidgets.QHBoxLayout()
            lay.addWidget(self.plot_widget)
            lay.addWidget(self.legend_widget)
        else:
            lay = QtWidgets.QHBoxLayout()
            lay.addWidget(self.legend_widget)
            lay.addWidget(self.plot_widget)

        self.setLayout(lay)
        self.legend_widget.set_position(position)


class DummyLabel(QtWidgets.QFrame, QTangoAttributeBase):
    def __init__(self):
        QtWidgets.QFrame.__init__(self)
        QTangoAttributeBase.__init__(self)
        self.setObjectName(self.__class__.__name__)
        self.l1 = QtWidgets.QLabel("test")
        self.l2 = QtWidgets.QLabel("apa")
        self.setLayout(QtWidgets.QHBoxLayout())
        self.layout().addWidget(self.l1)
        self.layout().addWidget(self.l2)
        self.attrColors = QTangoColors()
        st = ''.join(("DummyLabel {\n",
                      'border-width: 2px; \n',
                      'border-color: ', self.attrColors.secondaryColor0, '; \n',
                      'border-style: solid; \n',
                      'border-radius: 0px; \n',
                      'padding: 2px; \n',
                      'margin: 1px; \n',
                      'color: ', self.attrColors.secondaryColor0, "; \n",
                      'background-color: ', self.attrColors.backgroundColor, ';}\n',
                      "QLabel {\n",
                      'border-width: 0px; \n',
                      'border-color: ', self.attrColors.secondaryColor0, '; \n',
                      'border-style: solid; \n',
                      'border-radius: 0px; \n',
                      'padding: 2px; \n',
                      'margin: 1px; \n',
                      'color: ', self.attrColors.secondaryColor0, "; \n",
                      'background-color: ', self.attrColors.backgroundColor, ';}'
                      ))
        self.setStyleSheet(st)


class QTangoStripToolLegendItem(QtWidgets.QFrame, QTangoAttributeBase):
    clicked = QtCore.pyqtSignal()

    def __init__(self, name, range=[0, 1], color=None, unit=None, sizes=None, colors=None, parent=None):
        QtWidgets.QFrame.__init__(self)
        QTangoAttributeBase.__init__(self, sizes, colors, parent)
        self.setObjectName(self.__class__.__name__)
        logger.debug("New legend item: {0}, {1}".format(name, self.objectName()))
        self.name = name
        self.range = range
        self.unit = unit
        if color is None:
            self.color = self.attrColors.secondaryColor0
        else:
            self.color = color
        self.border_width = 1
        lay = QtWidgets.QHBoxLayout()
        self.name_label = QtWidgets.QLabel(name)
        self.range_label = QtWidgets.QLabel("[{0}-{1}] ".format(to_precision2(range[0], 2, 4, True),
                                                                to_precision2(range[1], 2, 4, True)))
        self.unit_label = QtWidgets.QLabel(unit)
        lay.addWidget(self.name_label)
        lay.addSpacerItem(QtWidgets.QSpacerItem(3, 0, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed))
        lay.addWidget(self.range_label)
        lay.addWidget(self.unit_label)
        self.setLayout(lay)
        self.update_stylesheet()

    def update_stylesheet(self, new_color=None, new_width=None):
        if new_color is not None:
            self.color = new_color
        if new_width is not None:
            self.border_width = new_width
        st = """QTangoStripToolLegendItem {{
                      border-top-width: {2}px;
                      border-bottom-width: {2}px;
                      border-left-width: {3}px;
                      border-right-width: {3}px;
                      border-color: {0};
                      border-style: solid;
                      border-radius: 0px;
                      padding: 2px;
                      margin: 1px;
                      color: {0};
                      background-color: {1};
                      }}
                QLabel {{
                      border-width: 0px;
                      border-color: {0};
                      border-style: solid;
                      border-radius: 0px;
                      padding: 0px;
                      margin: 0px;
                      color: {0};
                      background-color: {1};
                      }}
                QLabel:hover {{
                      border-color: {0};
                      }}
                      """.format(self.color, self.attrColors.backgroundColor, 1, self.border_width*4)
        self.setStyleSheet(st)
        self.update()

    def set_name(self, name):
        self.name = name
        self.name_label.setText(name)

    def set_range(self, range):
        self.range = range
        self.range_label.setText("[{0}-{1}] ".format(to_precision2(range[0], 2, 4, True),
                                                     to_precision2(range[1], 2, 4, True)))

    def set_unit(self, unit):
        self.unit = unit
        self.unit_label.setText(unit)

    def mousePressEvent(self, a0: QtGui.QMouseEvent) -> None:
        if a0.button() == QtCore.Qt.LeftButton:
            logger.debug("{0}: Emitting clicked signal".format(self.name))
            self.clicked.emit()


class QTangoStripToolLegendWidget(QTangoAttributeBase):
    def __init__(self, position="bottom", sizes=None, colors=None, parent=None):
        QTangoAttributeBase.__init__(self, sizes, colors, parent)
        self.position = position
        self.items = OrderedDict()
        self.item_name_list = list()
        lay = QtWidgets.QGridLayout()
        self.setLayout(lay)
        self.max_col = None
        self.set_position(position)
        self.current_focus_item = None

    def addItem(self, legend_item):
        self.items[legend_item.name] = legend_item
        self.item_name_list.append(legend_item.name)
        n = len(self.items) - 1
        c = n % self.max_col
        r = n // self.max_col
        self.layout().addWidget(legend_item, r, c)

    def removeItem(self, item):
        if isinstance(item, QTangoStripToolLegendItem):
            self.items.pop(item.name)
        else:
            self.items.pop(item)

    def get_item(self, item_id) -> QTangoStripToolLegendItem:
        if isinstance(item_id, str):
            i = self.items[item_id]
        else:
            # Assume item is an index
            i = self.items[self.item_name_list[item_id]]
        return i

    def get_item_index(self, item):
        try:
            ind = self.item_name_list.index(item.name)
        except ValueError:
            ind = None
        return ind

    def set_focus_item(self, item):
        if isinstance(item, str):
            i = self.items[item]
        else:
            # Assume item is an index
            i = self.items[self.item_name_list[item]]
        if self.current_focus_item is not None:
            self.current_focus_item.update_stylesheet(new_width=1)
        i.update_stylesheet(new_width=3)
        self.current_focus_item = i
        logger.debug("Setting focus stylesheet to {0}".format(i.name))

    def set_position(self, position):
        for i in range(len(self.items)):
            self.layout().takeAt(0)
        self.position = position
        if position in ["bottom", "top"]:
            self.max_col = 4
            spacer = QtWidgets.QWidget()
            spacer.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        else:
            self.max_col = 1
            spacer = QtWidgets.QWidget()
            spacer.setSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        n = len(self.items) - 1
        c = n % self.max_col
        r = n // self.max_col

        for item in self.items.values():
            self.layout().addWidget(item, r, c)
        self.layout().addWidget(spacer)


class QTangoStripToolPlotWidget(pg.PlotWidget, QTangoAttributeBase):
    """ Base class for a trend widget.

        The widget stores trend curves that are trended. The duration is set with setDuration (seconds).
        Curves are added with addCurve. New points are added with addPoint.

        If curves are named with setCurveName they can be shown with showLegend.

    """
    def __init__(self, name=None, sizes=None, colors=None, chronological=True, parent=None):
        QTangoAttributeBase.__init__(self, sizes, colors, parent)
        pg.PlotWidget.__init__(self, useOpenGL=True)

        self.unselected_pen_width = 1.5
        self.selected_pen_width = 3.0

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

        # self.legend = self.getPlotItem().addLegend()

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
        curve_new.setPen(curve_color + "f0", width=self.unselected_pen_width)
        curve_new.setClickable(True)
        curve_new.setZValue(-100)
        vb.addItem(curve_new)

        logger.debug("New curve color: {0}".format(curve_new.opts["pen"].color().getRgb()))

        self.value_trend_curves.append(curve_new)
        self.curve_vb_list.append(vb)
        self.curve_ax_list.append(ax)
        self.curve_name_list.append(name)

        # self.legend.addItem(curve_new, name)

        self.setupData(curve_index)

        curve_new.sigClicked.connect(self.setCurveFocus)
        # self.setCurveFocus(name)

        logger.debug("Calling updateViews")
        self.updateViews()
        return curve_new

    def updateViews(self):
        logger.info("Updating view")
        pi = self.getPlotItem()
        for ind, vb in enumerate(self.curve_vb_list):
            vb.setGeometry(pi.vb.sceneBoundingRect())
            vb.linkedViewChanged(pi.vb, vb.XAxis)
            if ind == self.curve_focus:
                logger.info("Curve index {0} selected".format(ind))
                vb.linkedViewChanged(pi.vb, vb.YAxis)

    def setCurveFocus(self, curve_id):
        curve_old = self.value_trend_curves[self.curve_focus]
        curve_old_color = curve_old.opts["pen"].color()
        curve_old.setZValue(-100)
        curve_old.setPen(curve_old_color, width=self.unselected_pen_width)
        if isinstance(curve_id, int):
            name = self.curve_name_list[curve_id]
            self.curve_focus = curve_id
        elif isinstance(curve_id, str):
            name = curve_id
            self.curve_focus = self.curve_name_list.index(name)
        else:
            self.curve_focus = self.value_trend_curves.index(curve_id)
            name = self.curve_name_list[self.curve_focus]
        logger.debug("Curve {0} selected, index {1}".format(name, self.curve_focus))
        pi = self.getPlotItem()
        axis_viewrange = self.curve_vb_list[self.curve_focus].viewRange()
        logger.debug("Setting view range {0}".format(axis_viewrange[1]))
        pi.vb.setRange(yRange=axis_viewrange[1], padding=0)
        pi_ax = pi.getAxis("right")
        curve_selected = self.value_trend_curves[self.curve_focus]
        curve_color = curve_selected.opts["pen"].color()
        curve_selected.setPen(curve_color, width=self.selected_pen_width)
        curve_selected.setZValue(0.0)
        logger.debug("Axis color: {0}".format(curve_color.getRgb()))
        pi_ax.setPen(curve_color)
        # self.updateViews()

    def get_curve_range(self, curve):
        if isinstance(curve, int):
            name = self.curve_name_list[curve]
            curve_index = curve
        elif isinstance(curve, str):
            name = curve
            curve_index = self.curve_name_list.index(name)
        else:
            name = curve.opts.get('name', None)
            curve_index = self.curve_name_list.index(name)
        axis_viewrange = self.curve_vb_list[curve_index].viewRange()
        return axis_viewrange

    def get_curve_color(self, curve_id) -> QtGui.QColor:
        if isinstance(curve_id, int):
            name = self.curve_name_list[curve_id]
            curve_index = curve_id
        elif isinstance(curve_id, str):
            name = curve_id
            curve_index = self.curve_name_list.index(name)
        else:
            name = curve_id.opts.get('name', None)
            curve_index = self.curve_name_list.index(name)
        curve_color = self.value_trend_curves[curve_index].opts["pen"].color()
        logger.debug("Curve color: {0}".format(curve_color))
        return curve_color

    def get_curve_focus_ind(self):
        return self.curve_focus

    def get_curve(self, curve_id):
        if isinstance(curve_id, int):
            name = self.curve_name_list[curve_id]
            curve_index = curve_id
        elif isinstance(curve_id, str):
            name = curve_id
            curve_index = self.curve_name_list.index(name)
        else:
            name = curve_id.opts.get('name', None)
            curve_index = self.curve_name_list.index(name)
        curve = self.value_trend_curves[curve_index]
        return curve

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


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)

    strip_tool = QTangoStripTool("Test", legend_pos="right")
    strip_tool.show()
    x_data = np.linspace(-600, 0, 1000)
    y_data = np.sin(2 * np.pi * x_data / 240.0)
    logger.debug("Strip tool created")
    strip_tool.set_data(x_data, y_data, 0)

    # strip_tool.add_curve("apa")
    # strip_tool.set_data(x_data, y_data * 2, 1)

    for c in range(3):
        x_data = np.linspace(-600, 0, 1000)
        y_data = np.sin(2*np.pi*x_data/240.0 * (c + 1)) + 10 * c
        strip_tool.add_curve("Curve {0}".format(c + 1))
        strip_tool.set_data(x_data, y_data, c + 1)
        # strip_tool.curve_vb_list[c].setRange(yRange=[c-1, c+1])

    sys.exit(app.exec_())
