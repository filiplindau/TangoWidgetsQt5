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
from collections import OrderedDict
from ColorDefinitions import QTangoColors, QTangoSizes


# noinspection PyAttributeOutsideInit
class QTangoTitleBar(QtWidgets.QWidget):
    """
    Solid colored title bar. The title is located in the right side of the bar.
    """
    def __init__(self, title='', sizes=None, colors=None, parent=None):
        QtWidgets.QWidget.__init__(self, parent)
        if title is None:
            self.title = ''
        else:
            self.title = title
        if sizes is None:
            self.sizes = QTangoSizes()
        else:
            self.sizes = sizes
        if colors is None:
            self.attrColors = QTangoColors()
        else:
            self.attrColors = colors

        self.setupLayout()

    def setupLayout(self):
        bar_height = self.sizes.barHeight
        self.startLabel = QtWidgets.QLabel('')
        s = ''.join(('QLabel {min-height: ', str(int(bar_height * 1.25)), 'px; \n',
                     'min-width: ', str(int(bar_height * 1.25 / 3)), 'px; \n',
                     'max-height: ', str(int(bar_height * 1.25)), 'px; \n',
                     'background-color: ', self.attrColors.primaryColor0, '; \n',
                     '}'))
        self.startLabel.setStyleSheet(s)

        self.startLabel.setSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding, QtWidgets.QSizePolicy.Fixed)

        self.endLabel = QtWidgets.QLabel('')
        s = ''.join(('QLabel {min-height: ', str(int(bar_height * 1.25)), 'px; \n',
                     'min-width: ', str(int(bar_height * 1.25)), 'px; \n',
                     'max-height: ', str(int(bar_height * 1.25)), 'px; \n',
                     'background-color: ', self.attrColors.primaryColor0, '; \n',
                     '}'))
        self.endLabel.setStyleSheet(s)

        self.nameLabel = QtWidgets.QLabel('')
        s = ''.join(('QLabel {min-height: ', str(int(bar_height * 1.25)), 'px; \n',
                     'max-height: ', str(int(bar_height * 1.25)), 'px; \n',
                     'background-color: ', self.attrColors.backgroundColor, '; \n',
                     'color: ', self.attrColors.primaryColor0, '; \n',
                     '}'))
        self.nameLabel.setStyleSheet(s)

        self.nameLabel.setText(self.title.upper())
        font = self.nameLabel.font()
        font.setFamily(self.sizes.fontType)
        font.setStretch(self.sizes.fontStretch)
        font.setWeight(self.sizes.fontWeight)
        font.setPointSize(int(bar_height * 1.15))
        font.setStyleStrategy(QtGui.QFont.PreferAntialias)
        self.nameLabel.setFont(font)
        self.nameLabel.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)

        self.layout = QtWidgets.QHBoxLayout(self)
        self.layout.setSpacing(int(bar_height / 5))
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.addWidget(self.startLabel)
        self.layout.addWidget(self.nameLabel)
        self.layout.addWidget(self.endLabel)

    def setName(self, name):
        self.nameLabel.setText(name)


# noinspection PyAttributeOutsideInit,PyAttributeOutsideInit
class QTangoSideBar(QtWidgets.QWidget):
    """
    Solid colored bar on the side to frame a composite widget. Can have buttons.
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
        self.cmdButtons = OrderedDict()
        self.layout = None
        self.setupLayout()

    def setupLayout(self):
        self.startLabel = QtWidgets.QLabel('')
        s = ''.join(('QLabel {min-height: ', str(int(self.sizes.barHeight * 2)), 'px; \n',
                     'min-width: ', str(int(self.sizes.barWidth)), 'px; \n',
                     'max-width: ', str(int(self.sizes.barWidth)), 'px; \n',
                     'max-height: ', str(int(self.sizes.barHeight * 2)), 'px; \n',
                     'background-color: ', self.attrColors.primaryColor0, '; \n',
                     '}'))
        self.startLabel.setStyleSheet(s)

        self.endLabel = QtWidgets.QLabel('')
        s = ''.join(('QLabel {min-height: ', str(int(self.sizes.barHeight * 2)), 'px; \n',
                     'min-width: ', str(int(self.sizes.barWidth)), 'px; \n',
                     'max-width: ', str(int(self.sizes.barWidth)), 'px; \n',
                     'background-color: ', self.attrColors.primaryColor0, '; \n',
                     '}'))
        self.endLabel.setStyleSheet(s)
        self.endLabel.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Expanding)

        if self.layout is not None:
            for i in reversed(range(self.layout.count())):
                self.layout.itemAt(i).widget().setParent(None)
        if self.layout is None:
            self.layout = QtWidgets.QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(int(self.sizes.barHeight / 10))
        self.layout.addWidget(self.startLabel)
        for cmdButton in self.cmdButtons.values():
            self.layout.addWidget(cmdButton)
        self.layout.addWidget(self.endLabel)

        self.update()

    def addCmdButton(self, title, slot=None):
        """
        Add a button on the sidebar with text "title". The method "slot" is connected to button pushed signal
        :param title:
        :param slot:
        :return:
        """
        cmd_button = QtWidgets.QPushButton('CMD ')
        s = ''.join(('QPushButton {	background-color: ', self.attrColors.primaryColor0, '; \n',
                     'color: ', self.attrColors.backgroundColor, '; \n',
                     'min-height: ', str(int(self.sizes.barHeight * 1.25)), 'px; \n',
                     'max-height: ', str(int(self.sizes.barHeight * 1.25)), 'px; \n',
                     'min-width: ', str(int(self.sizes.barWidth)), 'px; \n',
                     'max-width: ', str(int(self.sizes.barWidth)), 'px; \n',
                     'padding-left: 5px; \n',
                     'padding-right: 5px; \n',
                     'border-width: 0px; \n',
                     'border-style: solid; \n',
                     'border-color: #339; \n',
                     'border-radius: 0; \n',
                     'border: 0px; \n',
                     'text-align: right bottom;\n',
                     'padding: 0px; \n',
                     'margin: 0px; \n',
                     '} \n',
                     'QPushButton:hover{ background-color: ', self.attrColors.primaryColor1, ';} \n',
                     'QPushButton:hover:pressed{ background-color: ', self.attrColors.primaryColor2, ';} \n'))
        cmd_button.setStyleSheet(s)

        cmd_button.setText(''.join((title, ' ')))
        font = cmd_button.font()
        font.setFamily(self.sizes.fontType)
        font.setStretch(self.sizes.fontStretch)
        font.setPointSize(int(self.sizes.barHeight * 0.5))
        font.setStyleStrategy(QtGui.QFont.PreferAntialias)
        cmd_button.setFont(font)

        if slot is not None:
            cmd_button.clicked.connect(slot)

        self.cmdButtons[title] = cmd_button

        self.setupLayout()


class QTangoHorizontalBar(QtWidgets.QWidget):
    """
    Horizontal solid colored bar to frame composite widgets
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
        self.cmdButtons = OrderedDict()
        self.layout = None
        self.startLabel = None
        self.endLabel = None
        self.setupLayout()

    def setupLayout(self):
        self.startLabel = QtWidgets.QLabel('')
        s = ''.join(('QLabel {min-height: ', str(int(self.sizes.barHeight)), 'px; \n',
                     'min-width: ', str(int(self.sizes.barWidth)), 'px; \n',
                     'max-height: ', str(int(self.sizes.barHeight)), 'px; \n',
                     'background-color: ', self.attrColors.primaryColor0, '; \n',
                     '}'))
        self.startLabel.setStyleSheet(s)

        self.endLabel = QtWidgets.QLabel('')
        s = ''.join(('QLabel {min-height: ', str(int(self.sizes.barHeight)), 'px; \n',
                     'min-width: ', str(int(self.sizes.barWidth * 1.25)), 'px; \n',
                     'max-height: ', str(int(self.sizes.barHeight)), 'px; \n',
                     'background-color: ', self.attrColors.primaryColor0, '; \n',
                     '}'))
        self.endLabel.setStyleSheet(s)
        self.endLabel.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)

        self.layout = QtWidgets.QHBoxLayout(self)
        self.layout.setSpacing(0)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.addWidget(self.startLabel)
        self.layout.addWidget(self.endLabel)


class QTangoContentWidget(QtWidgets.QWidget):
    def __init__(self, name, horizontal=True, sizes=None, colors=None, parent=None):
        QtGui.QWidget.__init__(self, parent)
        if colors is None:
            self.attrColors = QTangoColors()
        else:
            self.attrColors = colors
        if sizes is None:
            self.sizes = QTangoSizes()
        else:
            self.sizes = sizes
        self.layout = None
        self.name = name
        self.title_bar = None
        self.side_bar = None
        self.layout_bar = None
        self.layout_content = None
        self.setupLayout(horizontal)

    def setupLayout(self, horizontal):
        colors = self.attrColors
        colors.primaryColor0 = colors.secondaryColor0
        self.title_bar = QTangoTitleBar(self.name, sizes=self.sizes, colors=colors)
        # self.title_bar.setSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Minimum)
        self.side_bar = QTangoSideBar(colors=self.attrColors, sizes=self.sizes)
        self.layout = QtGui.QVBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)
        self.setLayout(self.layout)
        self.setMinimumHeight(self.sizes.readAttributeHeight * 1.2)
        self.layout_bar = QtGui.QHBoxLayout()
        if horizontal:
            self.layout_content = QtGui.QHBoxLayout()
        else:
            self.layout_content = QtGui.QVBoxLayout()
        self.layout_content.setSpacing(self.sizes.barHeight * 2)
        self.layout_content.setContentsMargins(self.sizes.barHeight * 1.25,
                                               self.sizes.barHeight * 1.25,
                                               self.sizes.barHeight,
                                               self.sizes.barHeight)
        self.layout.addWidget(self.title_bar)
        self.layout.addLayout(self.layout_bar)
        self.layout_bar.addWidget(self.side_bar)
        self.layout_bar.addLayout(self.layout_content)

    def addLayout(self, layout):
        self.layout_content.addLayout(layout)

    def addWidget(self, widget):
        self.layout_content.addWidget(widget)

    def addSpacerItem(self, spaceritem):
        self.layout_content.addSpacerItem(spaceritem)
