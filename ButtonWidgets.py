# -*- coding:utf-8 -*-
"""
Created on Dec 18, 2017

@author: Filip
"""
from PyQt5 import QtWidgets, QtCore, QtGui
import PyTango as pt
from collections import OrderedDict
from BaseWidgets import QTangoAttributeBase
from LabelWidgets import QTangoStartLabel, QTangoEndLabel, QTangoAttributeNameLabel


class QTangoComboBoxBase(QtWidgets.QComboBox, QTangoAttributeBase):
    def __init__(self, sizes=None, colors=None, parent=None):
        QTangoAttributeBase.__init__(self, sizes, colors, parent)
        QtWidgets.QComboBox.__init__(self, parent)
        self.setupLayout()

    def setupLayout(self):
        self.setLocale(QtCore.QLocale(QtCore.QLocale.English))
        s = ''.join(('QComboBox { \n',
                     'background-color: ', self.attrColors.secondaryColor0, '; \n',
                     'selection-background-color: ', self.attrColors.secondaryColor1, '; \n',
                     'selection-color: ', self.attrColors.backgroundColor, '; \n',
                     'border-width: ', str(int(1)), 'px; \n',
                     'border-color: ', self.attrColors.backgroundColor, '; \n',
                     'border-top-style: solid; \n',
                     'border-bottom-style: solid; \n',
                     'border-left-style: double; \n',
                     'border-right-style: solid; \n',
                     'border-radius: 0px; \n',
                     'padding: 1px 0px 1px 3px; \n',
                     'margin: 0px; \n',
                     'min-width: ', str(int(self.sizes.readAttributeWidth / 3)), 'px; \n',
                     'max-width: ', str(int(self.sizes.readAttributeWidth)), 'px; \n',
                     'min-height: ', str(int(self.sizes.barHeight * 1.3)), 'px; \n',
                     'max-height: ', str(int(self.sizes.barHeight * 1.3)), 'px; \n',
                     'color: ', self.attrColors.backgroundColor, ';} \n',

                     'QComboBox:on { \n',
                     'background-color: ', self.attrColors.secondaryColor0, '; \n',
                     'color: ', self.attrColors.backgroundColor, '; \n',
                     '} \n',

                     'QComboBox QAbstractItemView { \n',
                     'background-color: ', self.attrColors.backgroundColor, '; \n',
                     'color: ', self.attrColors.secondaryColor0, '; \n',
                     'border-color: ', self.attrColors.backgroundColor, '; \n',
                     'selection-background-color: ', self.attrColors.secondaryColor1, '; \n',
                     'selection-color: ', self.attrColors.backgroundColor, '; \n',
                     '} \n',

                     'QComboBox::drop-down { \n',
                     'background-color: ', self.attrColors.secondaryColor0, '; \n',
                     'color: ', self.attrColors.backgroundColor, '; \n',
                     '} \n',

                     'QComboBox::down-arrow { \n',
                     'image: url(blackarrowdown.png); \n',
                     '} \n'
                     ))

        font = self.font()
        font.setFamily(self.sizes.fontType)
        font.setStretch(self.sizes.fontStretch)
        font.setWeight(self.sizes.fontWeight)
        font.setPointSize(int(self.sizes.barHeight * 0.7))
        font.setStyleStrategy(QtGui.QFont.PreferAntialias)
        self.setFont(font)
        self.setStyleSheet(s)
        self.setSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)
        item_delegate = QtWidgets.QStyledItemDelegate()
        self.setItemDelegate(item_delegate)

    def setValue(self, value):
        if type(value) == pt.DeviceAttribute:
            self.setQuality(value.quality)
            val = value.value
        else:
            val = value
        if val is not None:
            ind = self.findText(val)
            self.setCurrentIndex(ind)
        else:
            self.setCurrentIndex(0)

    def setWidth(self, width):
        s = str(self.styleSheet())
        ind0 = s.find('min-width') + 11
        ind1 = s[ind0:].find('px') + ind0
        s2 = s[0:ind0] + str(width) + s[ind1:]
        self.setStyleSheet(s2)


class QTangoCommandButton(QtWidgets.QPushButton, QTangoAttributeBase):
    def __init__(self, title, slot=None, sizes=None, colors=None, parent=None):
        QTangoAttributeBase.__init__(self, sizes, colors, parent)
        QtWidgets.QPushButton.__init__(self, parent)
        self.name = title

        if slot is not None:
            self.clicked.connect(slot)

        self.setupLayout()

    def setupLayout(self):
        button_height = self.sizes.barHeight * 1.75
        s = ''.join(('QPushButton {	background-color: ', self.attrColors.secondaryColor0, '; \n',
                     'color: ', self.attrColors.backgroundColor, '; \n',
                     'min-height: ', str(int(button_height)), 'px; \n',
                     'max-height: ', str(int(button_height)), 'px; \n',
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
                     'QPushButton:hover{ background-color: ', self.attrColors.secondaryColor1, ';} \n',
                     'QPushButton:hover:pressed{ background-color: ', self.attrColors.secondaryColor2, ';} \n'))
        self.setStyleSheet(s)

        self.setText(''.join((self.name, ' ')))
        font = self.font()
        font.setFamily(self.sizes.fontType)
        font.setStretch(self.sizes.fontStretch)  # QtGui.QFont.Condensed)
        font.setPointSize(int(self.sizes.barHeight * 0.7))
        font.setStyleStrategy(QtGui.QFont.PreferAntialias)
        self.setFont(font)

    def setQuality(self, quality):
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
            color = self.attrColors.warnColor
            state_string = 'WARNING'
        elif state_str == str(pt.AttrQuality.ATTR_CHANGING):
            color = self.attrColors.changingColor
            state_string = 'CHANGING'
        else:
            color = self.attrColors.unknownColor
            state_string = 'UNKNOWN'

        self.quality = state_string
        self.current_attr_color = color

        button_height = self.sizes.barHeight * 1.75
        s = ''.join(('QPushButton {	background-color: ', self.current_attr_color, '; \n',
                     'color: ', self.attrColors.backgroundColor, '; \n',
                     'min-height: ', str(int(button_height)), 'px; \n',
                     'max-height: ', str(int(button_height)), 'px; \n',
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
                     'QPushButton:hover{ background-color: ', self.attrColors.secondaryColor1, ';} \n',
                     'QPushButton:hover:pressed{ background-color: ', self.attrColors.secondaryColor2, ';} \n'))
        self.setStyleSheet(s)
        self.update()


# noinspection PyAttributeOutsideInit
class QTangoCommandSelection(QTangoAttributeBase):
    def __init__(self, title, sizes=None, colors=None, parent=None):
        QTangoAttributeBase.__init__(self, sizes, colors, parent)
        self.cmdButtons = OrderedDict()
        self.title = title
        self.layout = None
        self.setupLayout()

    def setupLayout(self):
        # Init layouts once
        if self.layout is None:
            self.startLabel = QTangoStartLabel(self.sizes, self.attrColors)
            self.endLabel = QTangoEndLabel(self.sizes, self.attrColors)
            self.nameLabel = QTangoAttributeNameLabel(self.sizes, self.attrColors)
            self.nameLabel.setText(self.title)
            self.nameLabel.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
            self.nameLabel.setMinimumWidth(0)
            self.statusLabel = QTangoAttributeNameLabel(self.sizes, self.attrColors)
            self.statusLabel.setSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding, QtWidgets.QSizePolicy.Fixed)
            self.statusLabel.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
            self.statusLabel.setText('')

            self.layout = QtWidgets.QHBoxLayout(self)
            self.layout.setContentsMargins(0, 0, 0, 0)
            self.layout.setContentsMargins(0, 0, 0, 0)
            self.layout.setSpacing(self.sizes.barWidth / 3)

            self.layout2 = QtWidgets.QVBoxLayout()
            self.layout2.setContentsMargins(0, 0, 0, 0)
            self.layout2.setContentsMargins(0, 0, 0, 0)

            self.layoutInfo = QtWidgets.QHBoxLayout()
            self.layoutInfo.setContentsMargins(0, 0, 0, 0)
            self.layoutInfo.setContentsMargins(0, 0, 0, 0)
            self.layoutInfo.setSpacing(int(self.sizes.barWidth / 6))
            self.layoutInfo.addWidget(self.nameLabel)
            self.layoutInfo.addWidget(self.statusLabel)
            self.layoutButtons = QtWidgets.QHBoxLayout()
            self.layoutButtons.setContentsMargins(0, 0, 0, 0)
            self.layoutButtons.setContentsMargins(0, 0, 0, 0)
            self.layoutButtons.setSpacing(int(self.sizes.barHeight / 3))
            self.layout2.addLayout(self.layoutInfo)
            self.layout2.addLayout(self.layoutButtons)

            self.layout.addWidget(self.startLabel)
            self.layout.addLayout(self.layout2)
            self.layout.addWidget(self.endLabel)

        # Clear out old layout
        if self.cmdButtons.keys().__len__() > 0:
            for i in reversed(range(self.layoutButtons.count())):
                self.layoutButtons.itemAt(i).widget().setParent(None)

            # Add buttons
        for cmdButton in self.cmdButtons.itervalues():
            self.layoutButtons.addWidget(cmdButton)

        self.setMaximumWidth(self.sizes.readAttributeWidth)
        self.setMinimumWidth(self.sizes.readAttributeWidth)
        self.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)

        self.update()

    def setStatus(self, status, state=None):
        if type(status) == pt.DeviceAttribute:
            self.startLabel.setQuality(status.quality)
            self.endLabel.setQuality(status.quality)
            self.nameLabel.setQuality(status.quality)
            self.statusLabel.setQuality(status.quality)
            for cmdButton in self.cmdButtons.itervalues():
                cmdButton.setQuality(status.quality)
            status_text = str(status.value)
        else:
            status_text = status
        if status_text is not None:
            self.statusLabel.setText(status_text)
        else:
            self.statusLabel.setText('--')
        self.statusLabel.repaint()

    def addCmdButton(self, name, slot):
        cmd_button = QTangoCommandButton(name, slot, self.sizes, self.attrColors)
        self.cmdButtons[name] = cmd_button

        self.setupLayout()


# noinspection PyAttributeOutsideInit
class QTangoWriteAttributeComboBox(QtWidgets.QWidget):
    def __init__(self, sizes=None, colors=None, parent=None):
        QtWidgets.QWidget.__init__(self, parent)
        self.attrColors = QTangoColors()
        if colors is None:
            self.attrColors = QTangoColors()
        else:
            self.attrColors = colors
        if sizes is None:
            self.sizes = QTangoSizes()
        else:
            self.sizes = sizes

        self.writeValueInitialized = False
        self.unit = None

        self.setupLayout()

    def setupLayout(self):
        read_value_width = self.sizes.barWidth

        self.startLabel = QTangoStartLabel(self.sizes, self.attrColors)
        self.endLabel = QTangoEndLabel(self.sizes, self.attrColors)
        self.nameLabel = QTangoAttributeNameLabel(self.sizes, self.attrColors)
        self.writeValueComboBox = QTangoComboBoxBase(self.sizes, self.attrColors)

        layout = QtWidgets.QHBoxLayout(self)
        margin = int(self.sizes.barHeight / 10)
        layout.setContentsMargins(margin, margin, margin, margin)

        layout_grid = QtWidgets.QHBoxLayout()
        layout_grid.setContentsMargins(0, 0, 0, 0)
        margin = int(self.sizes.barHeight / 10)
        layout_grid.setContentsMargins(margin, margin, margin, margin)
        layout_grid.addWidget(self.nameLabel)
        layout_grid.addWidget(self.writeValueComboBox)

        layout.addWidget(self.startLabel)
        layout.addLayout(layout_grid)
        layout.addWidget(self.endLabel)

        self.setMaximumWidth(self.sizes.readAttributeWidth)
        self.setMinimumWidth(self.sizes.readAttributeWidth)
        self.setSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)

        self.writeValueComboBox.activated[str].connect(self.onActivated)

    def attributeName(self):
        return str(self.nameLabel.text())

    # @QtCore.pyqtSignature('setAttributeName(QString)')
    def setAttributeName(self, a_name, a_unit=None):
        self.nameLabel.setText(a_name)
        if a_unit is not None:
            self.unit = a_unit
        self.update()

    def setAttributeValue(self, value):
        if type(value) == pt.DeviceAttribute:
            if value.value is not None:
                if self.writeValueInitialized is False:
                    print 'Initializing write value'
                    self.writeValueInitialized = True
                    self.setAttributeWriteValue(value.w_value)

            self.startLabel.setQuality(value.quality)
            self.endLabel.setQuality(value.quality)
        self.update()

    def setAttributeWriteValue(self, value):
        self.writeValueComboBox.setValue(value)
        self.update()

    def getWriteValue(self):
        return self.writeValueComboBox.value()

    def addItem(self, item_text):
        self.writeValueComboBox.addItem(item_text)

    def setActivatedMethod(self, method):
        self.writeValueComboBox.activated[str].connect(method)

    def onActivated(self, text):
        print text
