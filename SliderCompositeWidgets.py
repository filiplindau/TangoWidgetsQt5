# -*- coding:utf-8 -*-
"""
Created on Dec 18, 2017

@author: Filip
"""
from PyQt5 import QtWidgets, QtCore, QtGui
import PyTango as pt
import numpy as np
import copy
from BaseWidgets import QTangoAttributeBase, QTangoVSliderBase2, QTangoHSliderBase, QTangoHSliderBase2
from BaseWidgets import QTangoHSliderBaseCompact
from LabelWidgets import QTangoStartLabel, QTangoEndLabel, QTangoAttributeNameLabel, QTangoAttributeUnitLabel
from LabelWidgets import QTangoReadAttributeLabel
from EditWidgets import QTangoWriteAttributeLineEdit, QTangoReadAttributeSpinBox, QTangoWriteAttributeSpinBox
import logging

logger = logging.getLogger(__name__)


# noinspection PyAttributeOutsideInit
class QTangoReadAttributeSlider(QTangoAttributeBase):
    """ Class for a composite read_attribute_slider.

    It consists of a start and end label with color coded state. The current value is shown and a slider
    with configurable limits.

    The slider style can be selected with the slider_style:
    1: QTangoHSliderBase
    2: QTangoHSliderBase2
    3: QTangoHSliderCompact

    If a unit is supplied with setAttributeName or configureAttribute it is displayed with the current value.

    The current write value is shown if show_write_value == True (not implemented)

    """
    def __init__(self, sizes=None, colors=None, parent=None,
                 slider_style=2, show_write_label=False):
        QTangoAttributeBase.__init__(self, sizes, colors, parent)
        self.setupLayout(slider_style, show_write_label)

    def setupLayout(self, slider_style=2, show_write_label=False):
        self.startLabel = QTangoStartLabel(self.sizes, self.attrColors)
        self.endLabel = QTangoEndLabel(self.sizes, self.attrColors)
        self.nameLabel = QTangoAttributeNameLabel(self.sizes, self.attrColors)

        # Create read_attribute_spinbox and modify max_width
        sizes_value = copy.copy(self.sizes)
        sizes_value.barHeight *= 1.25
        self.valueSpinbox = QTangoReadAttributeLabel(sizes_value, self.attrColors)
        s = str(self.valueSpinbox.styleSheet())
        # if s != '':
        #     i0 = s.find('\nmax-width')
        #     i1 = s[i0:].find(':')
        #     i2 = s[i0:].find(';')
        #     s_new = ''.join((s[0:i0 + i1 + 1], ' ', str(self.sizes.readAttributeWidth), s[i0 + i2:]))
        #     self.valueSpinbox.setStyleSheet(s_new)
        self.valueSpinbox.setSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding, QtWidgets.QSizePolicy.Minimum)

        # Select slider style:
        if slider_style == 1:
            self.valueSlider = QTangoHSliderBase(self.sizes, self.attrColors)
        elif slider_style == 3:
            self.valueSlider = QTangoHSliderBaseCompact(self.sizes, self.attrColors)
        else:
            self.valueSlider = QTangoHSliderBase2(self.sizes, self.attrColors)

        # Create write_label if needed
        if show_write_label is True:
            self.writeLabel = QTangoStartLabel(self.sizes, self.attrColors)
            self.writeLabel.current_attr_color = self.attrColors.backgroundColor
            self.writeLabel.setupLayout()

        self.layout = QtWidgets.QHBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(self.sizes.barWidth / 3)

        self.layoutGrid = QtWidgets.QGridLayout()
        self.layoutGrid.setContentsMargins(0, 0, 0, 0)
        self.layoutGrid.addWidget(self.nameLabel, 0, 0)
        self.layoutGrid.addWidget(self.valueSlider, 1, 0, 1, 2)
        self.layoutGrid.addWidget(self.valueSpinbox, 0, 3)
        if show_write_label is True:
            self.layoutGrid.addWidget(self.writeLabel, 1, 2)

        self.layoutGrid.addWidget(self.nameLabel, 0, 0, 1, 2)
        self.layoutGrid.addWidget(self.valueSpinbox, 1, 1)
#        self.layoutGrid.addItem(self.vSpacer, 2, 0)
        self.layoutGrid.addWidget(self.valueSlider, 2, 0, 1, 2)

        self.layoutGrid.setHorizontalSpacing(self.sizes.barHeight / 4)
        # self.layoutGrid.setVerticalSpacing(0)

        self.layout.addWidget(self.startLabel)
        self.layout.addLayout(self.layoutGrid)
        self.layout.addWidget(self.endLabel)

        self.setMaximumWidth(self.sizes.readAttributeWidth)
        self.setMinimumWidth(self.sizes.readAttributeWidth)
        self.setMaximumHeight(self.sizes.barHeight * 2.2)
        self.setMinimumHeight(self.sizes.barHeight * 2.2)
        self.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)

    def attributeName(self):
        return str(self.nameLabel.text())

    # @QtCore.pyqtSignature('setAttributeName(QString)')
    def setAttributeName(self, a_name, a_unit=None):
        self.nameLabel.setText(a_name)
        if a_unit is not None:
            self.valueSpinbox.setSuffix(QtCore.QString.fromUtf8(''.join((' ', a_unit))))
        self.update()

    def setAttributeValue(self, value):
        if type(value) == pt.DeviceAttribute:
            self.startLabel.setQuality(value.quality)
            self.endLabel.setQuality(value.quality)
            self.nameLabel.setQuality(value.quality)
            if value.value is not None:
                val = value.value
                self.valueSpinbox.setValue(val)
                self.valueSlider.setValue(val)
        else:
            val = value
            self.valueSpinbox.setValue(val)
            self.valueSlider.setValue(val)
        self.update()

    def setAttributeWarningLimits(self, limits):
        self.valueSlider.setWarningLimits(limits)

    def setSliderLimits(self, min_limit, max_limit):
        self.valueSlider.setSliderLimits(min_limit, max_limit)

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
        self.valueSpinbox.setSuffix(''.join((' ', self.attrInfo.unit)))


# noinspection PyAttributeOutsideInit
class QTangoAttributeSlider(QTangoAttributeBase):
    def __init__(self, sizes=None, colors=None, parent=None,
                 slider_style=2, show_write_widget=False):
        logger.debug("QTangoAttributeSlider.__init__")
        QTangoAttributeBase.__init__(self, sizes, colors, parent)
        self.newValueSignal = None

        self.setupLayout(slider_style, show_write_widget)

        self.writeValueInitialized = False
        self.is_write_widget = show_write_widget

    def setupLayout(self, slider_style=2, show_write_widget=False):
        logger.debug("QTangoAttributeSlider.setupLayout")
        self.startLabel = QTangoStartLabel(self.sizes, self.attrColors)
        self.endLabel = QTangoEndLabel(self.sizes, self.attrColors)
        self.nameLabel = QTangoAttributeNameLabel(self.sizes, self.attrColors)
        self.unitLabel = QTangoAttributeUnitLabel(self.sizes, self.attrColors)
        self.valueLabel = QTangoReadAttributeLabel(self.sizes, self.attrColors)
        if show_write_widget is True:
            logger.debug("Adding write widgets")
            self.writeValueEdit = QTangoWriteAttributeLineEdit(self.sizes, self.attrColors)
            self.writeValueEdit.newValueSignal.connect(self.updateWriteValue)
            self.writeLabel = QTangoStartLabel(self.sizes, self.attrColors)
            self.writeLabel.current_attr_color = self.attrColors.backgroundColor
            self.writeLabel.setupLayout()
            self.newValueSignal = self.writeValueEdit.newValueSignal

        # Select slider style:
        if slider_style == 1:
            self.valueSlider = QTangoHSliderBase(self.sizes, self.attrColors)
        elif slider_style == 3:
            self.valueSlider = QTangoHSliderBaseCompact(self.sizes, self.attrColors)
        else:
            self.valueSlider = QTangoHSliderBase2(self.sizes, self.attrColors)

        logger.debug("QTangoAttributeSlider.setupLayout widget")

        self.layout = QtWidgets.QHBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(self.sizes.barWidth / 3)

        self.layoutGrid = QtWidgets.QGridLayout()
        self.layoutGrid.setContentsMargins(0, 0, 0, 0)
        self.layoutGrid.setHorizontalSpacing(self.sizes.barWidth / 4)
        self.layoutGrid.setVerticalSpacing(0)
        self.layoutGrid.addWidget(self.nameLabel, 0, 0)
        self.layoutGrid.addWidget(self.unitLabel, 0, 1)
        self.layoutGrid.addWidget(self.valueSlider, 1, 0, 1, 2)
        self.layoutGrid.addWidget(self.valueLabel, 0, 3, QtCore.Qt.AlignRight)
        if show_write_widget is True:
            self.layoutGrid.addWidget(self.writeLabel, 1, 2)
            self.layoutGrid.addWidget(self.writeValueEdit, 1, 3, QtCore.Qt.AlignRight)

        logger.debug("QTangoAttributeSlider.setupLayout: layoutGrid")

        self.layout.addWidget(self.startLabel)
        self.layout.addLayout(self.layoutGrid)
        self.layout.addWidget(self.endLabel)

        self.setMaximumWidth(self.sizes.readAttributeWidth)
        self.setMinimumWidth(self.sizes.readAttributeWidth)
        self.setMaximumHeight(self.sizes.barHeight * 2.2)
        self.setMaximumHeight(self.sizes.barHeight * 3.0)
        self.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)

        logger.debug("QTangoAttributeSlider.setupLayout: exit")

    def attributeName(self):
        return str(self.nameLabel.text())

    # @QtCore.pyqtSignature('setAttributeName(QString)')
    def setAttributeName(self, a_name, a_unit=None):
        self.nameLabel.setText(a_name)
        if a_unit is not None:
            self.unitLabel.setText(a_unit)
        self.update()

    def setAttributeValue(self, data):
        if type(data) == pt.DeviceAttribute:
            logger.debug("QTangoAttributeSlider::setAttributeValue: quality {0}".format(data.quality))
            self.startLabel.setQuality(data.quality)
            self.endLabel.setQuality(data.quality)
            self.nameLabel.setQuality(data.quality)
            self.unitLabel.setQuality(data.quality)
            if data.value is not None:
                logger.debug("QTangoAttributeSlider::setAttributeValue: setValue spinbox")
                self.valueLabel.setValue(data)
                logger.debug("QTangoAttributeSlider::setAttributeValue: setValue slider")
                self.valueSlider.setValue(data)
                if self.is_write_widget is True:
                    if self.writeValueInitialized is False:
                        logger.info("QTangoAttributeSlider::setAttributeValue: Initializing write value")
                        self.writeValueInitialized = True
                        self.setAttributeWriteValue(data.w_value)

                    if data.w_value != self.writeValueEdit.value():
                        if self.writeLabel.current_attr_color != self.attrColors.secondaryColor0:
                            self.writeLabel.current_attr_color = self.attrColors.secondaryColor0
                            self.writeLabel.setupLayout()
                    else:
                        if self.writeLabel.current_attr_color != self.attrColors.backgroundColor:
                            self.writeLabel.current_attr_color = self.attrColors.backgroundColor
                            self.writeLabel.setupLayout()
        else:
            self.valueLabel.setValue(data)
            self.valueSlider.setValue(data)
        self.update()

    def setAttributeWriteValue(self, value):
        if self.is_write_widget is True:
            self.writeValueEdit.setValue(value)
            self.valueSlider.setWriteValue(value)
            self.update()

    def setAttributeWarningLimits(self, limits):
        self.valueSlider.setWarningLimits(limits)

    def setSliderLimits(self, min_limit, max_limit):
        self.valueSlider.setSliderLimits(min_limit, max_limit)

    def updateWriteValue(self):
        logging.debug("In QTangoAttributeSlider.updateWriteValue: "
                      "updating slider to {0}".format(self.writeValueEdit.value()))
        self.valueSlider.setWriteValue(self.writeValueEdit.value())
        self.update()

    def getWriteValue(self):
        retval = None
        if self.is_write_widget:
            retval = self.writeValueEdit.value()
        return retval

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
        logger.debug("unit {0}".format(self.attrInfo.unit))
        try:
            self.valueSlider.setUnit(self.attrInfo.unit)
        except AttributeError:
            # Slider had no unit
            pass

        self.unit = self.attrInfo.unit
        self.unitLabel.setText(self.unit)

        self.valueLabel.data_format = attr_info.format
        if self.is_write_widget is True:
            self.writeValueEdit.dataFormat = attr_info.format


# noinspection PyAttributeOutsideInit
class QTangoReadAttributeSliderV(QTangoReadAttributeSlider):
    def __init__(self, sizes=None, colors=None, parent=None):
        QTangoAttributeBase.__init__(self, sizes, colors, parent)
        self.unit = None
        self.prefixDict = {'k': 1e3, 'M': 1e6, 'G': 1e9, 'T': 1e12, 'P': 1e15,
                           'm': 1e-3, 'u': 1e-6, 'n': 1e-9, 'p': 1e-12, 'f': 1e-15, 'c': 1e-2}
        self.prefix = None
        self.prefixFactor = 1.0
        self.setupLayout()

    def setupLayout(self):
        self.nameLabel = QTangoAttributeNameLabel(self.sizes, self.attrColors)
        sizes_value = copy.copy(self.sizes)
        sizes_value.barHeight *= 1.25

        self.valueSlider = QTangoVSliderBase2(self.sizes, self.attrColors)
        self.writeLabel = QTangoStartLabel(self.sizes, self.attrColors)
        self.writeLabel.current_attr_color = self.attrColors.backgroundColor
        self.writeLabel.setupLayout()

        self.unitLabel = QTangoAttributeNameLabel(self.sizes, self.attrColors)

        self.vSpacer = QtWidgets.QSpacerItem(20, self.sizes.barHeight, QtWidgets.QSizePolicy.Minimum,
                                             QtWidgets.QSizePolicy.MinimumExpanding)

        self.layout = QtWidgets.QVBoxLayout(self)
        margin = int(self.sizes.barHeight / 10)
        self.layout.setContentsMargins(margin, margin, margin, margin)
        self.layout.setSpacing(self.sizes.barHeight / 10)

        self.layout.addWidget(self.valueSlider)
        self.layout.addWidget(self.nameLabel)
        self.layout.addWidget(self.unitLabel)

        self.setMaximumWidth(self.sizes.barWidth * 4)
        self.setMinimumWidth(self.sizes.barWidth * 4)
        self.setMaximumHeight(self.sizes.readAttributeHeight)
        self.setMinimumHeight(self.sizes.readAttributeHeight)
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

    def setAttributeValue(self, value):
        if type(value) == pt.DeviceAttribute:
            if value.value is not None:
                self.valueSlider.setValue(value)
                self.nameLabel.setQuality(value.quality)
                self.unitLabel.setQuality(value.quality)
        else:
            val = value
            self.valueSlider.setValue(val)
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

    def setSliderLimits(self, min_limit, max_limit):
        self.valueSlider.setSliderLimits(min_limit, max_limit)

    def setSliderRangeAnchor(self, anchor, slider_range, anchor_pos=0.75):
        """Set the slider total range. The anchor value is set at
        realtive position anchorPos (0-1)
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


# noinspection PyAttributeOutsideInit
class QTangoWriteAttributeSliderV(QTangoAttributeSlider):
    def __init__(self, sizes=None, colors=None, parent=None):
        QTangoAttributeSlider.__init__(self, sizes, colors, parent)
        self.unit = None

    def setupLayout(self):
        self.nameLabel = QTangoAttributeNameLabel(self.sizes, self.attrColors)
        sizes_value = copy.copy(self.sizes)
        sizes_value.barHeight *= 1.25

        self.valueSlider = QTangoVSliderBase2(self.sizes, self.attrColors)
        self.writeLabel = QTangoStartLabel(self.sizes, self.attrColors)
        self.writeLabel.current_attr_color = self.attrColors.backgroundColor
        self.writeLabel.setupLayout()
        self.writeValueLineEdit = QTangoWriteAttributeLineEdit(self.sizes, self.attrColors)
        self.writeValueLineEdit.editingFinished.connect(self.updateWriteValue)
        self.writeValueLineEdit.setLayoutDirection(QtCore.Qt.RightToLeft)

        self.vSpacer = QtWidgets.QSpacerItem(20, self.sizes.barHeight, QtWidgets.QSizePolicy.Minimum,
                                             QtWidgets.QSizePolicy.MinimumExpanding)

        self.layout = QtWidgets.QVBoxLayout(self)
        margin = int(self.sizes.barHeight / 10)
        self.layout.setContentsMargins(margin, margin, margin, margin)
        self.layout.setSpacing(self.sizes.barHeight / 6.0)

        layout2 = QtWidgets.QHBoxLayout()
        margin = int(self.sizes.barHeight / 10)
        layout2.setContentsMargins(margin, margin, margin, margin)
        layout2.setSpacing(self.sizes.barHeight / 6.0)
        layout2.addWidget(self.writeLabel)
        layout2.addWidget(self.writeValueLineEdit)

        self.layout.addWidget(self.valueSlider)
        self.layout.addLayout(layout2)
        self.layout.addWidget(self.nameLabel)

        self.setMaximumWidth(self.sizes.barWidth * 4)
        self.setMinimumWidth(self.sizes.barWidth * 4)
        self.setMaximumHeight(self.sizes.readAttributeHeight)
        self.setMinimumHeight(self.sizes.readAttributeHeight)
        self.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)

    def attributeName(self):
        return str(self.nameLabel.text())

    # @QtCore.pyqtSignature('setAttributeName(QString)')
    def setAttributeName(self, a_name, a_unit=None):
        self.nameLabel.setText(a_name)
        if a_unit is not None:
            self.valueSlider.setUnit(a_unit)
            self.unit = a_unit
        self.update()

    def setAttributeValue(self, data):
        if type(data) == pt.DeviceAttribute:
            if data.value is not None:
                self.valueSlider.setValue(data)
                if self.writeValueInitialized is False:
                    print 'Initializing write value'
                    self.writeValueInitialized = True
                    self.setAttributeWriteValue(data.w_value)

                if np.abs((data.w_value - self.writeValueLineEdit.value()) / data.w_value) > 0.0001:
                    if self.writeLabel.current_attr_color != self.attrColors.secondaryColor0:
                        self.writeLabel.current_attr_color = self.attrColors.secondaryColor0
                        self.writeLabel.setupLayout()
                else:
                    if self.writeLabel.current_attr_color != self.attrColors.backgroundColor:
                        self.writeLabel.current_attr_color = self.attrColors.backgroundColor
                        self.writeLabel.setupLayout()
        else:
            self.valueSlider.setValue(data)
            self.unitLabel.setQuality(data.quality)
            self.valueLabel.setQuality(data.quality)
            self.nameLabel.setQuality(data.quality)
        self.update()

    def setAttributeWriteValue(self, value):
        self.writeValueLineEdit.setValue(value)
        self.valueSlider.setWriteValue(value)
        self.update()

    def setAttributeWarningLimits(self, limits):
        self.valueSlider.setWarningLimits(limits)

    def setSliderLimits(self, min_limit, max_limit):
        self.valueSlider.setSliderLimits(min_limit, max_limit)

    def updateWriteValue(self):
        if self.writeValueLineEdit.validatorObject.validate(self.writeValueLineEdit.text(), 0)[0] \
                == QtGui.QValidator.Acceptable:
            self.valueSlider.setWriteValue(np.double(self.writeValueLineEdit.text()))
        self.update()
        print 'updating slider to ', self.writeValueLineEdit.text()

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
        self.unit = self.attrInfo.unit

    def getWriteValue(self):
        return self.writeValueLineEdit.value()


###################################################################
# noinspection PyAttributeOutsideInit
class QTangoReadAttributeSliderDeprecated(QTangoAttributeBase):
    def __init__(self, sizes=None, colors=None, parent=None):
        QTangoAttributeBase.__init__(self, sizes, colors, parent)
        self.setupLayout()

    def setupLayout(self):
        self.startLabel = QTangoStartLabel(self.sizes, self.attrColors)
        self.endLabel = QTangoEndLabel(self.sizes, self.attrColors)
        self.nameLabel = QTangoAttributeNameLabel(self.sizes, self.attrColors)
        self.valueSpinbox = QTangoReadAttributeSpinBox(self.sizes, self.attrColors)
        self.valueSlider = QTangoHSliderBase(self.sizes, self.attrColors)

        self.layout = QtWidgets.QHBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(self.sizes.barHeight / 3)

        self.layoutGrid = QtWidgets.QGridLayout()
        margin = int(self.sizes.barHeight / 10)
        self.layoutGrid.setContentsMargins(margin, margin, margin, margin)
        self.layoutGrid.setContentsMargins(0, 0, 0, 0)
        self.layoutGrid.addWidget(self.nameLabel, 0, 0, )
        self.layoutGrid.addWidget(self.valueSlider, 1, 0)
        self.layoutGrid.addWidget(self.valueSpinbox, 0, 1)
        self.layoutGrid.setHorizontalSpacing(self.sizes.barHeight / 4)
        self.layoutGrid.setVerticalSpacing(0)

        self.layout.addWidget(self.startLabel)
        self.layout.addLayout(self.layoutGrid)
        self.layout.addWidget(self.endLabel)

        self.setMaximumWidth(self.sizes.readAttributeWidth)
        self.setMinimumWidth(self.sizes.readAttributeWidth)
        self.setMaximumHeight(self.sizes.barHeight * 2.2)
        self.setMinimumHeight(self.sizes.barHeight * 2.2)
        self.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)