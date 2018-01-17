# -*- coding:utf-8 -*-
"""
Created on Dec 18, 2017

@author: Filip
"""
from PyQt5 import QtWidgets, QtCore, QtGui
import PyTango as pt
from BaseWidgets import QTangoAttributeBase
from LabelWidgets import QTangoStartLabel, QTangoEndLabel, QTangoAttributeNameLabel, QTangoAttributeUnitLabel
from LabelWidgets import QTangoReadAttributeLabel
from EditWidgets import QTangoWriteAttributeLineEdit
import logging

logger = logging.getLogger(__name__)


# noinspection PyAttributeOutsideInit
class QTangoWriteAttributeDouble(QtWidgets.QWidget, QTangoAttributeBase):
    def __init__(self, sizes=None, colors=None, precision=4, parent=None):
        QTangoAttributeBase.__init__(self, sizes, colors, parent)

        self.writeValueInitialized = False
        self.unit = None
        self.precision = precision
        self.prefix = None

        self.setupLayout()

    def setupLayout(self):
        self.startLabel = QTangoStartLabel(self.sizes, self.attrColors)
        self.endLabel = QTangoEndLabel(self.sizes, self.attrColors)
        self.nameLabel = QTangoAttributeNameLabel(self.sizes, self.attrColors)
        self.nameLabel.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.unitLabel = QTangoAttributeUnitLabel(self.sizes, self.attrColors)
        self.valueSpinbox = QTangoReadAttributeLabel(self.sizes, self.attrColors)
        self.writeValueLineEdit = QTangoWriteAttributeLineEdit(self.sizes, self.attrColors)
        self.writeValueLineEdit.setLayoutDirection(QtCore.Qt.RightToLeft)
        self.writeLabel = QTangoStartLabel(self.sizes, self.attrColors)
        self.writeLabel.current_attr_color = self.attrColors.backgroundColor
        self.writeLabel.setupLayout()

        layout = QtWidgets.QHBoxLayout(self)
        margin = int(self.sizes.barHeight / 10)
        layout.setContentsMargins(margin, margin, margin, margin)

        layout_grid = QtWidgets.QGridLayout()
        margin = int(self.sizes.barHeight / 10)
        layout_grid.setContentsMargins(margin, margin, margin, margin)
        layout_grid.addWidget(self.nameLabel, 0, 0)
        layout_grid.addWidget(self.valueSpinbox, 0, 2)
        layout_grid.addWidget(self.unitLabel, 0, 3)
        layout_grid.addWidget(self.writeLabel, 1, 1)
        layout_grid.addWidget(self.writeValueLineEdit, 1, 2)

        layout.addWidget(self.startLabel)
        layout.addLayout(layout_grid)
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

    def setUnit(self, unit):
        self.unit = unit
        if self.unit is not None:
            unit_str = self.unit
            if self.prefix is not None:
                unit_str = ''.join((self.prefix, unit_str))
            self.unitLabel.setText(unit_str)

    def setAttributeValue(self, value):
        if type(value) == pt.DeviceAttribute:
            if value.value is not None:
                if self.writeValueInitialized is False:
                    print 'Initializing write value'
                    self.writeValueInitialized = True
                    self.setAttributeWriteValue(value.w_value)

                if value.w_value != self.writeValueLineEdit.value():
                    if self.writeLabel.current_attr_color != self.attrColors.secondaryColor0:
                        self.writeLabel.current_attr_color = self.attrColors.secondaryColor0
                        self.writeLabel.setupLayout()
                else:
                    if self.writeLabel.current_attr_color != self.attrColors.backgroundColor:
                        self.writeLabel.current_attr_color = self.attrColors.backgroundColor
                        self.writeLabel.setupLayout()
            self.startLabel.setQuality(value.quality)
            self.endLabel.setQuality(value.quality)
            self.unitLabel.setQuality(value.quality)
            self.valueSpinbox.setQuality(value.quality)
            self.nameLabel.setQuality(value.quality)

            val = value.value
        else:
            val = value

        self.valueSpinbox.setValue(val)
        self.update()

    def setAttributeWriteValue(self, value):
        self.writeValueLineEdit.setValue(value)
        self.update()

    def getWriteValue(self):
        return self.writeValueLineEdit.value()
