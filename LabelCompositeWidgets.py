# -*- coding:utf-8 -*-
"""
Created on Dec 18, 2017

@author: Filip
"""
from PyQt5 import QtWidgets, QtCore, QtGui
import PyTango as pt
from BaseWidgets import QTangoAttributeBase
from LabelWidgets import QTangoStartLabel, QTangoEndLabel, QTangoAttributeNameLabel, QTangoStateLabel
from LabelWidgets import QTangoBooleanLabel, QTangoReadAttributeLabel, QTangoAttributeUnitLabel
import logging

logger = logging.getLogger(__name__)


class QTangoDeviceStatus(QTangoAttributeBase):
    def __init__(self, sizes=None, colors=None, parent=None):
        QTangoAttributeBase.__init__(self, sizes, colors, parent)
        self.startLabel = None
        self.endLabel = None
        self.nameLabel = None
        self.stateLabel = None
        self.statusLabel = None
        self.setupLayout()

    def setupLayout(self):
        self.startLabel = QTangoStartLabel(self.sizes, self.attrColors)
        self.startLabel.setSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding, QtWidgets.QSizePolicy.Expanding)
        self.endLabel = QTangoEndLabel(self.sizes, self.attrColors)
        self.endLabel.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        self.nameLabel = QTangoAttributeNameLabel(self.sizes, self.attrColors)
        self.nameLabel.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignBottom)
        self.nameLabel.setSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding, QtWidgets.QSizePolicy.Fixed)
        self.nameLabel.setText("Status")
        self.stateLabel = QTangoStateLabel(self.sizes, self.attrColors)
        self.stateLabel.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignBottom)
        self.stateLabel.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        self.statusLabel = QTangoAttributeNameLabel(self.sizes, self.attrColors)
        self.statusLabel.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignBottom)
        self.statusLabel.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        self.statusLabel.setWordWrap(True)

        s = ''.join(('QLabel {min-height: ', str(self.sizes.barHeight), 'px; \n',
                     'background-color: ', self.attrColors.backgroundColor, '; \n',
                     'color: ', self.current_attr_color, ';}'))
        self.statusLabel.setStyleSheet(s)
        font = self.font()
        font.setPointSize(int(self.sizes.barHeight * 0.3))
        font.setStyleStrategy(QtGui.QFont.PreferAntialias)
        self.statusLabel.setFont(font)

        spacer_item = QtWidgets.QSpacerItem(0, 0, QtWidgets.QSizePolicy.MinimumExpanding,
                                            QtWidgets.QSizePolicy.MinimumExpanding)

        layout = QtWidgets.QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout_top = QtWidgets.QHBoxLayout()
        layout_top.setContentsMargins(0, 0, 0, 0)
        layout2 = QtWidgets.QVBoxLayout()
        layout2.setContentsMargins(0, 0, 0, 0)
        layout2.setSpacing(0)
        layout2.setContentsMargins(0, 0, 0, 3)

        layout.addWidget(self.startLabel)
        layout.addLayout(layout2)
        layout2.addLayout(layout_top)
        layout_top.addWidget(self.nameLabel)
        layout_top.addWidget(self.stateLabel)
        layout2.addSpacerItem(spacer_item)
        layout2.addWidget(self.statusLabel)
        layout.addWidget(self.endLabel)

        self.setMaximumWidth(self.sizes.readAttributeWidth)
        self.setMinimumWidth(self.sizes.readAttributeWidth)
        self.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)

    def statusText(self):
        return str(self.statusLabel.text())

    # @QtCore.pyqtSignature('setAttributeName(QString)')
    def setStatusText(self, a_name):
        self.statusLabel.setText(a_name)
        self.update()

    def setState(self, state):
        self.endLabel.setState(state)
        self.startLabel.setState(state)
        self.nameLabel.setState(state)
        self.stateLabel.setState(state)
        self.statusLabel.setState(state)

    def setStatus(self, state, status):
        self.setState(state)
        self.statusLabel.setText(status)
        self.update()


# noinspection PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit
class QTangoDeviceNameStatus(QTangoAttributeBase):
    def __init__(self, sizes=None, colors=None, parent=None):
        QTangoAttributeBase.__init__(self, sizes, colors, parent)
        self.setupLayout()

    def setupLayout(self):

        self.startLabel = QTangoStartLabel(self.sizes, self.attrColors)
        self.startLabel.setSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding, QtWidgets.QSizePolicy.Fixed)
        self.endLabel = QTangoEndLabel(self.sizes, self.attrColors)
        self.endLabel.setSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding, QtWidgets.QSizePolicy.Fixed)
        self.nameLabel = QTangoAttributeNameLabel(self.sizes, self.attrColors)
        self.nameLabel.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignBottom)
        self.nameLabel.setSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding, QtWidgets.QSizePolicy.Fixed)

        layout = QtWidgets.QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.startLabel)
        layout.addWidget(self.nameLabel)
        layout.addWidget(self.endLabel)

        self.setMaximumWidth(self.sizes.readAttributeWidth)
        self.setMinimumWidth(self.sizes.readAttributeWidth)
        self.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)

    def attributeName(self):
        return str(self.nameLabel.text())

    # @QtCore.pyqtSignature('setAttributeName(QString)')
    def setAttributeName(self, a_name):
        self.nameLabel.setText(a_name)
        self.update()

    def setState(self, state):
        self.endLabel.setState(state)
        self.startLabel.setState(state)
        self.nameLabel.setState(state)


# noinspection PyAttributeOutsideInit
class QTangoReadAttributeDouble(QTangoAttributeBase):
    def __init__(self, sizes=None, colors=None, parent=None):
        QTangoAttributeBase.__init__(self, sizes, colors, parent)
        self.unit = None
        self.prefixDict = {'k': 1e-3, 'M': 1e-6, 'G': 1e-9, 'T': 1e-12, 'P': 1e-15,
                           'm': 1e3, 'u': 1e6, 'n': 1e9, 'p': 1e12, 'f': 1e15, 'c': 1e2}
        self.prefix = None
        self.prefixFactor = 1.0
        self.setupLayout()

    def setupLayout(self):
        self.startLabel = QTangoStartLabel(self.sizes, self.attrColors)
        self.endLabel = QTangoEndLabel(self.sizes, self.attrColors)
        self.nameLabel = QTangoAttributeNameLabel(self.sizes, self.attrColors)
        self.nameLabel.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.unitLabel = QTangoAttributeUnitLabel(self.sizes, self.attrColors)
        self.valueSpinbox = QTangoReadAttributeLabel(self.sizes, self.attrColors)
        self.unitLabel.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignBottom)

        layout = QtWidgets.QHBoxLayout(self)
        margin = int(self.sizes.barHeight / 10)
        layout.setContentsMargins(margin, margin, margin, margin)

        layout.addWidget(self.startLabel)
        layout.addWidget(self.nameLabel)
        layout.addWidget(self.valueSpinbox)
        layout.addWidget(self.unitLabel)
        layout.addWidget(self.endLabel)

        self.setMaximumWidth(self.sizes.readAttributeWidth)
        self.setMinimumWidth(self.sizes.readAttributeWidth)
        self.setSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)

    def attributeName(self):
        return str(self.nameLabel.text())

    # @QtCore.pyqtSignature('setAttributeName(QString)')
    def setAttributeName(self, a_name, a_unit=None):
        self.nameLabel.setText(a_name)
        if a_unit is not None:
            self.setUnit(a_unit)
        self.update()

    def setAttributeValue(self, value):
        if type(value) == pt.DeviceAttribute:
            self.startLabel.setQuality(value.quality)
            self.endLabel.setQuality(value.quality)
            self.unitLabel.setQuality(value.quality)
            self.valueSpinbox.setQuality(value.quality)
            self.nameLabel.setQuality(value.quality)
            val = value.value
        else:
            val = value
        self.valueSpinbox.setValue(val * self.prefixFactor)
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


# noinspection PyAttributeOutsideInit
class QTangoReadAttributeBoolean(QTangoAttributeBase):
    def __init__(self, sizes=None, colors=None, parent=None):
        QTangoAttributeBase.__init__(self, sizes, colors, parent)
        self.setupLayout()

    def setupLayout(self):
        self.startLabel = QTangoStartLabel(self.sizes, self.attrColors)
        self.endLabel = QTangoEndLabel(self.sizes, self.attrColors)
        self.nameLabel = QTangoAttributeNameLabel(self.sizes, self.attrColors)
        self.valueBoolean = QTangoBooleanLabel(self.sizes, self.attrColors)

        self.layout = QtWidgets.QHBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(self.sizes.barWidth / 3)

        self.layoutGrid = QtWidgets.QGridLayout()
        self.layoutGrid.setContentsMargins(0, 0, 0, 0)
        self.layoutGrid.addWidget(self.nameLabel, 0, 0, )
        self.layoutGrid.addWidget(self.valueBoolean, 0, 1)
        self.layoutGrid.setHorizontalSpacing(self.sizes.barWidth / 4)
        self.layoutGrid.setVerticalSpacing(0)

        self.layout.addWidget(self.startLabel)
        self.layout.addLayout(self.layoutGrid)
        self.layout.addWidget(self.endLabel)

        self.setMaximumWidth(self.sizes.readAttributeWidth)
        self.setMinimumWidth(self.sizes.readAttributeWidth)
        self.setMaximumHeight(self.sizes.barHeight)
        self.setMinimumHeight(self.sizes.barHeight)
        self.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)

    def attributeName(self):
        return str(self.nameLabel.text())

    # @QtCore.pyqtSignature('setAttributeName(QString)')
    def setAttributeName(self, a_name):
        self.nameLabel.setText(a_name)
        self.update()

    def setAttributeValue(self, value):
        if type(value) == pt.DeviceAttribute:
            self.startLabel.setQuality(value.quality)
            self.endLabel.setQuality(value.quality)
            if value.dim_x > 1:
                val = value.value[0]
            else:
                val = value.value
        else:
            val = value

        self.valueBoolean.setBooleanState(val)
        self.update()
