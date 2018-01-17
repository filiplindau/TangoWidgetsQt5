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
from LabelWidgets import QTangoStartLabel, QTangoEndLabel, QTangoAttributeNameLabel
from EditWidgets import QTangoWriteAttributeLineEdit, QTangoReadAttributeSpinBox
from SliderCompositeWidgets import QTangoAttributeSlider


# noinspection PyAttributeOutsideInit
class QTangoReadAttributeSlider(QTangoAttributeBase):
    def __init__(self, sizes=None, colors=None, parent=None):
        QTangoAttributeBase.__init__(self, sizes, colors, parent)
        self.setupLayout()

    def setupLayout(self):
        read_value_width = self.sizes.barWidth
        read_width = self.sizes.readAttributeWidth - self.sizes.barHeight / 6 - self.sizes.barHeight / 2

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

    def attributeName(self):
        return str(self.nameLabel.text())

    #@QtCore.pyqtSignature('setAttributeName(QString)')
    def setAttributeName(self, aName):
        self.nameLabel.setText(aName)
        self.update()

    def setAttributeValue(self, value):
        if type(value) == pt.DeviceAttribute:
            self.startLabel.setQuality(value.quality)
            self.endLabel.setQuality(value.quality)
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


# noinspection PyAttributeOutsideInit
class QTangoWriteAttributeSlider4(QTangoAttributeSlider):
    def __init__(self, sizes=None, colors=None, parent=None):
        QTangoAttributeSlider.__init__(self, sizes, colors, parent)

    def setupLayout(self):
        self.startLabel = QTangoStartLabel(self.sizes, self.attrColors)
        self.endLabel = QTangoEndLabel(self.sizes, self.attrColors)
        self.nameLabel = QTangoAttributeNameLabel(self.sizes, self.attrColors)
        self.unitLabel = QTangoAttributeUnitLabel(self.sizes, self.attrColors)
        sizesValue = copy.copy(self.sizes)
        sizesValue.barHeight *= 1.0
        self.valueSpinbox = QTangoReadAttributeSpinBox(sizesValue, self.attrColors)
        s = str(self.valueSpinbox.styleSheet())
        if s != '':
            i0 = s.find('\nmax-width')
            i1 = s[i0:].find(':')
            i2 = s[i0:].find(';')
            sNew = ''.join((s[0:i0 + i1 + 1], ' ', str(self.sizes.readAttributeWidth), s[i0 + i2:]))
            self.valueSpinbox.setStyleSheet(sNew)
        self.valueSpinbox.setSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding, QtWidgets.QSizePolicy.Minimum)

        self.valueSlider = QTangoHSliderBase2(self.sizes, self.attrColors)
        # 		self.writeValueSpinbox = QTangoWriteAttributeSpinBox2(sizesValue, self.attrColors)
        # 		self.writeValueSpinbox.editingFinished.connect(self.editingFinished)
        self.writeValueLineEdit = QTangoWriteAttributeLineEdit(self.sizes, self.attrColors)
        self.writeValueLineEdit.editingFinished.connect(self.updateWriteValue)
        self.writeValueLineEdit.setLayoutDirection(QtCore.Qt.RightToLeft)

        self.writeLabel = QTangoStartLabel(self.sizes, self.attrColors)
        self.writeLabel.current_attr_color = self.attrColors.backgroundColor
        self.writeLabel.setupLayout()

        self.vSpacer = QtWidgets.QSpacerItem(20, self.sizes.barHeight, QtWidgets.QSizePolicy.Minimum,
                                         QtWidgets.QSizePolicy.MinimumExpanding)

        self.layout = QtWidgets.QHBoxLayout(self)
        margin = int(self.sizes.barHeight / 10)
        self.layout.setContentsMargins(margin, margin, margin, margin)
        self.layout.setSpacing(self.sizes.barHeight / 3)

        layoutV = QtWidgets.QVBoxLayout()
        layoutH1 = QtWidgets.QHBoxLayout()
        layoutH1.addWidget(self.nameLabel)
        layoutH1.addWidget(self.valueSpinbox)
        layoutH2 = QtWidgets.QHBoxLayout()
        spacerItemH = QtWidgets.QSpacerItem(5, 5, QtWidgets.QSizePolicy.MinimumExpanding, QtWidgets.QSizePolicy.Minimum)
        layoutH2.addSpacerItem(spacerItemH)
        layoutH2.addWidget(self.writeLabel)
        layoutH2.addWidget(self.writeValueLineEdit)
        layoutV.addLayout(layoutH1)
        layoutV.addLayout(layoutH2)
        layoutV.addWidget(self.valueSlider)

        self.layout.addWidget(self.startLabel)
        self.layout.addLayout(layoutV)
        self.layout.addWidget(self.endLabel)

        self.setMaximumWidth(self.sizes.readAttributeWidth)
        self.setMinimumWidth(self.sizes.readAttributeWidth)
        self.setMaximumHeight(self.sizes.barHeight * 4)
        self.setMinimumHeight(self.sizes.barHeight * 4)
        self.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)

    def configureAttribute(self, attrInfo):
        QTangoReadAttributeSlider2.configureAttribute(self, attrInfo)
        self.valueSpinbox.setSuffix(''.join((' ', self.attrInfo.unit)))

    def setAttributeName(self, aName, aUnit=None):
        self.nameLabel.setText(aName)
        if aUnit is not None:
            self.valueSpinbox.setSuffix(QtCore.QString.fromUtf8(''.join((' ', aUnit))))
        self.update()

    def setAttributeValue(self, data):
        if type(data) == pt.DeviceAttribute:
            self.startLabel.setQuality(data.quality)
            self.endLabel.setQuality(data.quality)
            if data.value is not None:
                self.valueSlider.setValue(data.value)
                self.valueSpinbox.setValue(data.value)
                if self.writeValueInitialized is False:
                    print 'Initializing write value'
                    self.writeValueInitialized = True
                    self.setAttributeWriteValue(data.w_value)

                if data.w_value != self.writeValueLineEdit.value():
                    if self.writeLabel.current_attr_color != self.attrColors.secondaryColor0:
                        self.writeLabel.current_attr_color = self.attrColors.secondaryColor0
                        self.writeLabel.setupLayout()
                else:
                    if self.writeLabel.current_attr_color != self.attrColors.backgroundColor:
                        self.writeLabel.current_attr_color = self.attrColors.backgroundColor
                        self.writeLabel.setupLayout()
        else:
            self.valueSlider.setValue(data)
            self.valueSpinbox.setValue(data)
        self.update()

    def setAttributeWriteValue(self, value):
        self.writeValueLineEdit.setValue(value)
        self.valueSlider.setWriteValue(value)
        self.update()

    def setSliderLimits(self, min_limit, max_limit):
        self.valueSlider.setSliderLimits(min_limit, max_limit)

    def updateWriteValue(self):
        if self.writeValueLineEdit.validatorObject.validate(self.writeValueLineEdit.text(), 0)[
            0] == QtGui.QValidator.Acceptable:
            self.valueSlider.setWriteValue(np.double(self.writeValueLineEdit.text()))
        self.update()
        print 'updating slider to ', self.writeValueLineEdit.text()

    def getWriteValue(self):
        return self.writeValueLineEdit.value()








# noinspection PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit
class QTangoReadAttributeSlider3(QTangoReadAttributeSlider2):
    def __init__(self, sizes=None, colors=None, parent=None):
        QTangoReadAttributeSlider2.__init__(self, sizes, colors, parent)

    def setupLayout(self):
        #		QTangoReadAttributeSlider2.setupLayout(self)
        self.startLabel = QTangoStartLabel(self.sizes, self.attrColors)
        self.endLabel = QTangoEndLabel(self.sizes, self.attrColors)
        self.nameLabel = QTangoAttributeNameLabel(self.sizes, self.attrColors)
        self.unitLabel = QTangoAttributeUnitLabel(self.sizes, self.attrColors)
        self.valueSpinbox = QTangoReadAttributeSpinBox(self.sizes, self.attrColors)
        self.valueSlider = QTangoHSliderBase2(self.sizes, self.attrColors)
        self.writeLabel = QTangoStartLabel(self.sizes, self.attrColors)
        self.writeLabel.current_attr_color = self.attrColors.backgroundColor
        self.writeLabel.setupLayout()

        self.layout = QtWidgets.QHBoxLayout(self)
        margin = int(self.sizes.barHeight / 10)
        self.layout.setContentsMargins(margin, margin, margin, margin)
        self.layout.setSpacing(self.sizes.barHeight / 3)

        self.layoutGrid = QtWidgets.QGridLayout()
        self.layoutGrid.setContentsMargins(0, 0, 0, 0)
        self.layoutGrid.addWidget(self.nameLabel, 0, 0)
        self.layoutGrid.addWidget(self.unitLabel, 0, 1)
        self.layoutGrid.addWidget(self.valueSlider, 1, 0, 1, 2)
        # 		self.layoutGrid.addWidget(self.valueSpinbox, 0, 3)
        # 		self.layoutGrid.addWidget(self.writeLabel, 1, 2)

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
        # 		self.layoutGrid.removeWidget(self.valueSpinbox)
        # 		self.valueSpinbox = None
        # 		self.layoutGrid.removeWidget(self.writeLabel)
        self.valueLabel = QTangoAttributeNameLabel(self.sizes, self.attrColors)
        self.layoutGrid.addWidget(self.valueLabel, 0, 3)

    def setAttributeValue(self, value):
        if type(value) == pt.DeviceAttribute:
            self.startLabel.setQuality(value.quality)
            self.endLabel.setQuality(value.quality)
            if value.value is not None:
                val = value.value
                self.valueLabel.setText(str(val))
                self.valueSlider.setValue(val)
        else:
            val = value
            self.valueLabel.setText(str(val))
            self.valueSlider.setValue(val)
        self.update()


# noinspection PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit
class QTangoReadAttributeSlider4(QTangoReadAttributeSlider2):
    def __init__(self, sizes=None, colors=None, parent=None):
        QTangoReadAttributeSlider2.__init__(self, sizes, colors, parent)

    def setupLayout(self):
        self.startLabel = QTangoStartLabel(self.sizes, self.attrColors)
        self.endLabel = QTangoEndLabel(self.sizes, self.attrColors)
        self.nameLabel = QTangoAttributeNameLabel(self.sizes, self.attrColors)
        self.unitLabel = QTangoAttributeUnitLabel(self.sizes, self.attrColors)
        sizesValue = copy.copy(self.sizes)
        sizesValue.barHeight *= 1.25
        self.valueSpinbox = QTangoReadAttributeSpinBox(sizesValue, self.attrColors)
        s = str(self.valueSpinbox.styleSheet())
        if s != '':
            i0 = s.find('\nmax-width')
            i1 = s[i0:].find(':')
            i2 = s[i0:].find(';')
            sNew = ''.join((s[0:i0 + i1 + 1], ' ', str(self.sizes.readAttributeWidth), s[i0 + i2:]))
            self.valueSpinbox.setStyleSheet(sNew)
        self.valueSpinbox.setSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding, QtWidgets.QSizePolicy.Minimum)

        self.valueSlider = QTangoHSliderBase2(self.sizes, self.attrColors)
        self.writeLabel = QTangoStartLabel(self.sizes, self.attrColors)
        self.writeLabel.current_attr_color = self.attrColors.backgroundColor
        self.writeLabel.setupLayout()

        self.vSpacer = QtWidgets.QSpacerItem(20, self.sizes.barHeight, QtWidgets.QSizePolicy.Minimum,
                                         QtWidgets.QSizePolicy.MinimumExpanding)

        self.layout = QtWidgets.QHBoxLayout(self)
        margin = int(self.sizes.barHeight / 10)
        self.layout.setContentsMargins(margin, margin, margin, margin)
        self.layout.setSpacing(self.sizes.barHeight / 3)

        self.layoutGrid = QtWidgets.QGridLayout()
        self.layoutGrid.setContentsMargins(0, 0, 0, 0)
        self.layoutGrid.addWidget(self.nameLabel, 0, 0, 1, 2)
        self.layoutGrid.addWidget(self.valueSpinbox, 1, 1)
        self.layoutGrid.addItem(self.vSpacer, 2, 0)
        self.layoutGrid.addWidget(self.valueSlider, 2, 0, 1, 2)

        self.layoutGrid.setHorizontalSpacing(self.sizes.barHeight / 4)
        self.layoutGrid.setVerticalSpacing(self.sizes.barHeight / 10)

        self.layout.addWidget(self.startLabel)
        self.layout.addLayout(self.layoutGrid)
        self.layout.addWidget(self.endLabel)

        self.setMaximumWidth(self.sizes.readAttributeWidth)
        self.setMinimumWidth(self.sizes.readAttributeWidth)
        self.setMaximumHeight(self.sizes.barHeight * 4)
        self.setMinimumHeight(self.sizes.barHeight * 4)
        self.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)

    def configureAttribute(self, attrInfo):
        QTangoReadAttributeSlider2.configureAttribute(self, attrInfo)
        self.valueSpinbox.setSuffix(''.join((' ', self.attrInfo.unit)))

    def setAttributeName(self, aName, aUnit=None):
        self.nameLabel.setText(aName)
        if aUnit is not None:
            self.valueSpinbox.setSuffix(QtCore.QString.fromUtf8(''.join((' ', aUnit))))
        self.update()


# noinspection PyAttributeOutsideInit
class QTangoReadAttributeSliderCompact(QTangoAttributeBase):
    def __init__(self, sizes=None, colors=None, parent=None):
        QTangoAttributeBase.__init__(self, sizes, colors, parent)
        self.setupLayout()

    def setupLayout(self):
        self.startLabel = QTangoStartLabel(self.sizes, self.attrColors)
        self.endLabel = QTangoEndLabel(self.sizes, self.attrColors)
        self.nameLabel = QTangoAttributeNameLabel(self.sizes, self.attrColors)
        self.unitLabel = QTangoAttributeUnitLabel(self.sizes, self.attrColors)
        self.valueSpinbox = QTangoReadAttributeSpinBox(self.sizes, self.attrColors)
        self.valueSpinbox.setAlignment(QtCore.Qt.AlignRight)
        self.valueSlider = QTangoHSliderBaseCompact(self.sizes, self.attrColors)

        self.layout = QtWidgets.QHBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(self.sizes.barWidth / 3)

        self.layoutAttr = QtWidgets.QVBoxLayout()
        self.layoutAttr.setContentsMargins(0, 0, 0, 0)
        self.layoutAttr.setSpacing(0)
        self.layoutAttr.setContentsMargins(0, 0, 0, 0)
        self.layoutData = QtWidgets.QHBoxLayout()
        self.layoutData.setContentsMargins(0, 0, 0, 0)
        self.layoutData.setContentsMargins(0, 0, 0, 0)
        self.layoutData.addWidget(self.nameLabel)
        self.layoutData.addWidget(self.valueSpinbox)
        self.layoutAttr.addLayout(self.layoutData)
        self.layoutAttr.addWidget(self.valueSlider)

        self.layout.addWidget(self.startLabel)
        self.layout.addLayout(self.layoutAttr)
        self.layout.addWidget(self.endLabel)

        self.setMaximumWidth(self.sizes.readAttributeWidth)
        self.setMinimumWidth(self.sizes.readAttributeWidth)
        self.setMaximumHeight(self.sizes.barHeight * 1.6)
        self.setMinimumHeight(self.sizes.barHeight * 1.6)
        self.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)

    def attributeName(self):
        return str(self.nameLabel.text())

    #@QtCore.pyqtSignature('setAttributeName(QString)')
    def setAttributeName(self, aName, aUnit=None):
        self.nameLabel.setText(aName)
        if aUnit is not None:
            self.unitLabel.setText(aUnit)
            self.valueSpinbox.setSuffix(''.join((' ', aUnit)))
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

    def configureAttribute(self, attrInfo):
        QTangoAttributeBase.configureAttribute(self, attrInfo)
        try:
            min_warning = float(self.attrInfo.alarms.min_warning)
        except:
            min_warning = -np.inf
        try:
            max_warning = float(self.attrInfo.alarms.max_warning)
        except:
            max_warning = np.inf
        self.setAttributeWarningLimits((min_warning, max_warning))
        self.unitLabel.setText(self.attrInfo.unit)
        self.valueSpinbox.setSuffix(''.join((' ', self.attrInfo.unit)))