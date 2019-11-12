# -*- coding:utf-8 -*-
"""
Created on Dec 19, 2017

@author: Filip
"""
from PyQt5 import QtWidgets
import PyTango
from BaseWidgets import QTangoColors, QTangoSizes
from LayoutWidgets import QTangoTitleBar, QTangoHorizontalBar, QTangoSideBar
from AttributeReadThreadClass import AttributeClass
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.CRITICAL)


class TangoDeviceClient(QtWidgets.QWidget):
    def __init__(self, name, use_sidebar=False, use_bottombar=False, call_setup_layout=True, parent=None):
        QtWidgets.QWidget.__init__(self, parent)

        self.name = name

        self.title_sizes = None
        self.attr_sizes = None
        self.frame_sizes = None
        self.colors = QTangoColors()
        self.top_spacing = 60

        self.titlebar = None
        self.bottombar = None
        self.sidebar = None
        self.layout_data = None

        if call_setup_layout:
            self.setup_layout(use_sidebar, use_bottombar)

        self.devices = dict()
        self.attributes = dict()

    def setup_layout(self, use_sidebar=False, use_bottombar=False):
        s = 'QWidget{background-color: #000000; }'
        self.setStyleSheet(s)

        self.title_sizes = QTangoSizes()
        self.title_sizes.barHeight = 40
        self.title_sizes.barWidth = 18
        self.title_sizes.readAttributeWidth = 300
        self.title_sizes.writeAttributeWidth = 150
        self.title_sizes.fontStretch = 80
        self.title_sizes.fontType = 'Arial'

        self.frame_sizes = QTangoSizes()
        self.frame_sizes.barHeight = 40
        self.frame_sizes.barWidth = 35
        self.frame_sizes.readAttributeWidth = 300
        self.frame_sizes.writeAttributeWidth = 150
        self.frame_sizes.fontStretch = 80
        self.frame_sizes.fontType = 'Arial'

        self.attr_sizes = QTangoSizes()
        self.attr_sizes.barHeight = 20
        self.attr_sizes.barWidth = 20
        self.attr_sizes.readAttributeWidth = 300
        self.attr_sizes.readAttributeHeight = 250
        self.attr_sizes.writeAttributeWidth = 299
        self.attr_sizes.fontStretch = 80
        self.attr_sizes.fontType = 'Arial'

        self.titlebar = QTangoTitleBar(self.name, self.title_sizes)
        self.setWindowTitle(self.name)
        if use_sidebar is True:
            self.sidebar = QTangoSideBar(colors=self.colors, sizes=self.frame_sizes)
        if use_bottombar is True:
            self.bottombar = QTangoHorizontalBar()

        layout_top = QtWidgets.QVBoxLayout(self)
        layout_top.setSpacing(0)
        layout_top.setContentsMargins(9, 9, 9, 9)

        layout_sidebar = QtWidgets.QHBoxLayout()
        layout_sidebar.setSpacing(0)
        layout_sidebar.setContentsMargins(-1, 0, 0, 0)

        layout_content = QtWidgets.QVBoxLayout()
        layout_content.setSpacing(0)
        layout_content.setContentsMargins(-1, 0, 0, 0)

        self.layout_data = QtWidgets.QHBoxLayout()
        self.layout_data.setContentsMargins(self.attr_sizes.barHeight / 2, self.attr_sizes.barHeight / 2,
                                            self.attr_sizes.barHeight / 2, self.attr_sizes.barHeight / 2)
        self.layout_data.setSpacing(self.attr_sizes.barHeight * 2)

        layout_top.addLayout(layout_sidebar)
        layout_sidebar.addLayout(layout_content)
        layout_content.addWidget(self.titlebar)
        layout_content.addSpacerItem(QtWidgets.QSpacerItem(20, self.top_spacing, QtWidgets.QSizePolicy.Minimum,
                                                           QtWidgets.QSizePolicy.Minimum))
        layout_content.addLayout(self.layout_data)
        if use_sidebar is True:
            layout_sidebar.addWidget(self.sidebar)
        if use_bottombar is True:
            layout_top.addWidget(self.bottombar)

    def add_layout(self, layout):
        self.layout_data.addLayout(layout)

    def add_widget(self, widget, defer_update=False):
        self.layout_data.addWidget(widget)
        if defer_update is False:
            self.update()

    def add_attribute(self, attr_name, device_name, callback, update_interval=0.5, single_shot=False,
                      get_info=False, attr_info_slot=None):
        attr_dict_name = "{0}_{1}".format(attr_name, device_name)
        if device_name not in self.devices:
            raise KeyError("Device not in dictionary")
        if single_shot is True:
            update_interval = None
        self.attributes[attr_dict_name] = AttributeClass(attr_name, self.devices[device_name], update_interval,
                                                         callback, get_info, attr_info_slot)

    def add_device(self, device_name, tango_name):
        self.devices[device_name] = PyTango.DeviceProxy(tango_name)

    def closeEvent(self, event):
        for a in self.attributes.values():
            logger.debug("In closeEvent: Stopping {0}".format(a.name))
            a.stop_read()
        for a in self.attributes.values():
            a.read_thread.join()
        event.accept()


