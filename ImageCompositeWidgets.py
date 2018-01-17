# -*- coding:utf-8 -*-
"""
Created on Dec 18, 2017

@author: Filip
"""
from PyQt5 import QtWidgets
import PyTango as pt
from BaseWidgets import QTangoAttributeBase, QTangoImageBase, QTangoImageWithHistBase
from LabelWidgets import QTangoStartLabel, QTangoEndLabel, QTangoAttributeNameLabel


# noinspection PyAttributeOutsideInit
class QTangoReadAttributeImage(QTangoAttributeBase):
    def __init__(self, sizes=None, colors=None, parent=None):
        QTangoAttributeBase.__init__(self, sizes, colors, parent)
        self.setupLayout()

    def setupLayout(self):
        self.startLabel = QTangoStartLabel(self.sizes, self.attrColors)
        self.endLabel = QTangoEndLabel(self.sizes, self.attrColors)
        self.nameLabel = QTangoAttributeNameLabel(self.sizes, self.attrColors)
        self.imageWidget = QTangoImageBase(self.sizes, self.attrColors)

        self.layout = QtWidgets.QHBoxLayout(self)
        margin = int(self.sizes.barHeight / 10)
        self.layout.setContentsMargins(margin, margin, margin, margin)
        self.layout.setSpacing(self.sizes.barWidth / 3)

        self.layoutGrid = QtWidgets.QGridLayout()
        self.layoutGrid.setContentsMargins(0, 0, 0, 0)
        self.layoutGrid.addWidget(self.nameLabel, 0, 0)
        self.layoutGrid.addWidget(self.imageWidget, 1, 0, 1, 2)
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

    def setImage(self, image, auto_levels=False):
        if type(image) == pt.DeviceAttribute:
            im = image.value
            self.startLabel.setQuality(image.quality)
            self.endLabel.setQuality(image.quality)
            self.nameLabel.setQuality(image.quality)
        self.imageWidget.setImage(im, auto_levels)

    def fixedSize(self, fixed=True):
        if fixed is True:
            self.imageWidget.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
            self.setMaximumWidth(self.sizes.readAttributeWidth)
        else:
            self.imageWidget.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)


# noinspection PyAttributeOutsideInit
class QTangoReadAttributeImageWithHist(QTangoAttributeBase):
    def __init__(self, sizes=None, colors=None, parent=None):
        QTangoAttributeBase.__init__(self, sizes, colors, parent)
        self.setupLayout()

    def setupLayout(self):
        self.startLabel = QTangoStartLabel(self.sizes, self.attrColors)
        self.endLabel = QTangoEndLabel(self.sizes, self.attrColors)
        self.nameLabel = QTangoAttributeNameLabel(self.sizes, self.attrColors)
        self.imageWidget = QTangoImageWithHistBase(self.sizes, self.attrColors)

        self.layout = QtWidgets.QHBoxLayout(self)
        margin = int(self.sizes.barHeight / 10)
        self.layout.setContentsMargins(margin, margin, margin, margin)
        self.layout.setSpacing(self.sizes.barWidth / 3)

        self.layoutGrid = QtWidgets.QGridLayout()
        self.layoutGrid.setContentsMargins(0, 0, 0, 0)
        self.layoutGrid.addWidget(self.nameLabel, 0, 0)
        self.layoutGrid.addWidget(self.imageWidget, 1, 0, 1, 2)
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

    def setImage(self, image):
        if type(image) == pt.DeviceAttribute:
            im = image.value
            self.startLabel.setQuality(image.quality)
            self.endLabel.setQuality(image.quality)
        self.imageWidget.setImage(im, autoRange=False, autoLevels=False)