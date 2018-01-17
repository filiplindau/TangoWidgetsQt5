# -*- coding:utf-8 -*-
"""
Created on Dec 18, 2017

@author: Filip
"""
from PyQt5 import QtWidgets
import PyTango as pt
import numpy as np
import time
from BaseWidgets import QTangoAttributeBase
from LabelWidgets import QTangoStartLabel, QTangoEndLabel, QTangoAttributeNameLabel
from LabelWidgets import QTangoReadAttributeLabel
from BaseWidgets import QTangoTrendBase, QTangoVSliderBase2, QTangoSpectrumBase
import logging

logger = logging.getLogger(__name__)


# noinspection PyAttributeOutsideInit
class QTangoReadAttributeTrend(QTangoAttributeBase):
    def __init__(self, name=None, sizes=None, colors=None, parent=None):
        QTangoAttributeBase.__init__(self, sizes, colors, parent)
        self.unit = None
        self.prefixDict = {'k': 1e3, 'M': 1e6, 'G': 1e9, 'T': 1e12, 'P': 1e15,
                           'm': 1e-3, 'u': 1e-6, 'n': 1e-9, 'p': 1e-12, 'f': 1e-15, 'c': 1e-2}
        self.prefix = None
        self.prefixFactor = 1.0

        self.curve_focus = 0
        self.setupLayout(name)

    def setupLayout(self, name=None):
        self.startLabel = QTangoStartLabel(self.sizes, self.attrColors)
        self.endLabel = QTangoEndLabel(self.sizes, self.attrColors)
        self.nameLabel = QTangoAttributeNameLabel(self.sizes, self.attrColors)
        self.unitLabel = QTangoAttributeNameLabel(self.sizes, self.attrColors)
        self.curveNameLabel = QTangoAttributeNameLabel(self.sizes, self.attrColors)
        if name is not None:
            self.curveNameLabel.setText(name)
        else:
            self.curveNameLabel.setText("curve 0")
        self.valueSpinbox = QTangoReadAttributeLabel(self.sizes, self.attrColors)
        self.nameLabel.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        self.valueSlider = QTangoVSliderBase2(self.sizes, self.attrColors)

        self.valueTrend = QTangoTrendBase(name=name, sizes=self.sizes, colors=self.attrColors)
        self.valueTrend.valueTrendCurves[-1].sigClicked.connect(self.setCurveFocus)

        self.layout = QtWidgets.QHBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(self.sizes.barWidth / 3)

        layout2 = QtWidgets.QVBoxLayout()
        layout3 = QtWidgets.QHBoxLayout()
        layout2.addLayout(layout3)
        layout2.addWidget(self.valueTrend)
        layout3.addWidget(self.nameLabel)
        layout3.addWidget(self.curveNameLabel)
        layout3.addWidget(self.valueSpinbox)
        layout3.addWidget(self.unitLabel)

        self.layout.addWidget(self.startLabel)
        self.layout.addLayout(layout2)
        self.layout.addWidget(self.endLabel)

        self.setMaximumWidth(self.sizes.readAttributeWidth)
        self.setMinimumWidth(self.sizes.readAttributeWidth)
        self.setMaximumHeight(self.sizes.barHeight * 4)
        self.setMinimumHeight(self.sizes.barHeight * 4)
        self.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)

    def attributeName(self):
        return str(self.nameLabel.text())

    # @QtCore.pyqtSignature('setAttributeName(QString)')
    def setAttributeName(self, a_name, a_unit=None):
        self.nameLabel.setText(a_name)
        if a_unit is not None:
            self.valueSlider.setUnit(a_unit)
            self.setUnit(a_unit)
        self.update()

    def setAttributeValue(self, value, curve=0):
        if type(value) == pt.DeviceAttribute:
            if value.value is not None:
                if curve == 0:
                    self.valueSlider.setValue(value)
                    self.valueSpinbox.setValue(value)
                self.valueTrend.addPoint(value, curve)
                self.nameLabel.setQuality(value.quality)
                self.unitLabel.setQuality(value.quality)
        else:
            t = time.time()
            self.valueTrend.addPoint([t, value], curve)
            if curve == 0:
                self.valueSlider.setValue(value)
                self.valueSpinbox.setValue(value)

        self.update()

    def addPoint(self, value, curve=0):
        if type(value) == pt.DeviceAttribute:
            if value.value is not None:
                value.value /= self.prefixFactor
                self.valueSlider.setValue(value)
                self.valueTrend.addPoint(value, curve)
                self.nameLabel.setQuality(value.quality)
                self.curveNameLabel.setQuality(value.quality)
                self.unitLabel.setQuality(value.quality)
                self.startLabel.setQuality(value.quality)
                self.endLabel.setQuality(value.quality)
                self.unitLabel.setQuality(value.quality)
                self.valueSpinbox.setQuality(value.quality)
        else:
            value /= self.prefixFactor
            self.valueSlider.setValue(value)
            t = time.time()
            self.valueTrend.addPoint([t, value], curve)
        if curve == self.curve_focus:
            self.valueSlider.setValue(value)
            self.valueSpinbox.setValue(value)
        self.update()

    def setUnit(self, unit):
        self.unit = unit
        if self.unit is not None:
            unit_str = self.unit
            if self.prefix is not None:
                unit_str = ''.join((self.prefix, unit_str))

            self.unitLabel.setText(unit_str)

    def setPrefix(self, prefix):
        try:
            self.prefixFactor = self.prefixDict[prefix]
            self.prefix = prefix
            self.setUnit(self.unit)
        except KeyError:
            self.prefix = None
            self.prefixFactor = 1.0

    def setAttributeWarningLimits(self, limits):
        self.valueSlider.setWarningLimits(limits)
        self.valueTrend.setWarningLimits(limits)

    def setSliderLimits(self, attr_min, attr_max):
        self.valueSlider.setSliderLimits(attr_min, attr_max)

    def setSliderRangeAnchor(self, anchor, slider_range, anchor_pos=0.75):
        """Set the slider total range. The anchor value is set at
        relative position anchorPos (0-1)
        """
        val_min = anchor - slider_range * anchor_pos
        val_max = anchor + slider_range * (1 - anchor_pos)
        self.valueSlider.setSliderLimits(val_min, val_max)

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
        self.setAttributeWarningLimits((min_warning, max_warning))
        self.valueSlider.setUnit(self.attrInfo.unit)
        self.setUnit(self.attrInfo.unit)

    def setTrendLimits(self, low, high):
        self.valueTrend.setYRange(low, high, padding=0.05)

    def addCurve(self, name=None):
        self.valueTrend.addCurve(name)
        self.valueTrend.valueTrendCurves[-1].sigClicked.connect(self.setCurveFocus)

    def setCurveFocus(self, curve):
        name = curve.opts.get('name', None)
        if name is not None:
            self.curve_focus = self.valueTrend.curve_name_list.index(name)
            self.curveNameLabel.setText(name)

    def setCurveName(self, curve, name):
        self.valueTrend.setCurveName(curve, name)

    def showLegend(self, show_legend=True):
        self.valueTrend.showLegend(show_legend)

    def setDuration(self, duration):
        self.valueTrend.setDuration(duration)


# noinspection PyAttributeOutsideInit
class QTangoReadAttributeSpectrum(QTangoAttributeBase):
    def __init__(self, sizes=None, colors=None, parent=None):
        QTangoAttributeBase.__init__(self, sizes, colors, parent)
        self.setupLayout()

    def setupLayout(self):
        self.startLabel = QTangoStartLabel(self.sizes, self.attrColors)
        self.endLabel = QTangoEndLabel(self.sizes, self.attrColors)
        self.nameLabel = QTangoAttributeNameLabel(self.sizes, self.attrColors)
        self.spectrum = QTangoSpectrumBase(self.sizes, self.attrColors)

        self.layout = QtWidgets.QHBoxLayout(self)
        margin = int(self.sizes.barHeight / 10)
        self.layout.setContentsMargins(margin, margin, margin, margin)
        self.layout.setSpacing(self.sizes.barWidth / 3)

        self.layoutGrid = QtWidgets.QGridLayout()
        self.layoutGrid.setContentsMargins(0, 0, 0, 0)
        self.layoutGrid.addWidget(self.nameLabel, 0, 0)
        self.layoutGrid.addWidget(self.spectrum, 1, 0, 1, 2)
        self.layoutGrid.setHorizontalSpacing(self.sizes.barWidth / 4)
        self.layoutGrid.setVerticalSpacing(0)

        self.layout.addWidget(self.startLabel)
        self.layout.addLayout(self.layoutGrid)
        self.layout.addWidget(self.endLabel)

        self.setMinimumWidth(self.sizes.readAttributeWidth)
        self.setMinimumHeight(self.sizes.barHeight * 6)
        self.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)

    def attributeName(self):
        return str(self.nameLabel.text())

    # @QtCore.pyqtSignature('setAttributeName(QString)')
    def setAttributeName(self, a_name):
        self.nameLabel.setText(a_name)
        self.update()

    def setSpectrum(self, xData, yData, index=0):
        if type(xData) == pt.DeviceAttribute:
            xData = xData.value
        if type(yData) == pt.DeviceAttribute:
            self.startLabel.setQuality(yData.quality)
            self.endLabel.setQuality(yData.quality)
            self.nameLabel.setQuality(yData.quality)
            yData = yData.value
        self.spectrum.setSpectrum(xData, yData, index)

    def setXRange(self, low, high):
        self.spectrum.setXRange(low, high)

    def fixedSize(self, fixed=True):
        if fixed is True:
            self.spectrum.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
            self.setMaximumWidth(self.sizes.readAttributeWidth)
        else:
            self.spectrum.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)

    def configureAttribute(self, attr_info):
        logger.debug("Configuring attribute {0}".format(attr_info.name))
        QTangoAttributeBase.configureAttribute(self, attr_info)
        try:
            min_warning = float(self.attrInfo.alarms.min_warning)
        except ValueError:
            min_warning = -np.inf
        try:
            max_warning = float(self.attrInfo.alarms.max_warning)
        except ValueError:
            max_warning = np.inf
        logger.debug("min_warning {0}, max_warning {1}".format(min_warning, max_warning))
        self.setAttributeWarningLimits((min_warning, max_warning))

    def setAttributeWarningLimits(self, limits):
        self.spectrum.setWarningLimits(limits)
