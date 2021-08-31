# -*- coding:utf-8 -*-
"""
Created on Dec 19, 2017

@author: Filip
"""
from PyQt5 import QtWidgets
import PyTango
from ColorDefinitions import QTangoColors, QTangoSizes
from LayoutWidgets import QTangoTitleBar, QTangoHorizontalBar, QTangoSideBar
from AttributeReadThreadClass import AttributeClass
import logging
import threading
from concurrent.futures import Future

# logger = logging.getLogger(__name__)
# logger.setLevel(logging.INFO)


class DummyDevice:
    def __init__(self, tango_name):
        self.name = tango_name
        self.logger = logging.getLogger("DummyDevice {0}".format(self.name))

    def get_state(self):
        return PyTango.DevState.UNKNOWN

    def command_inout_asynch(self, *args):
        self.logger.info("{0}: Dummy command {1}".format(self.name, args))

    def get_attribute_config(self, name):
        raise RuntimeError("No attribute info")

    def read_attribute_asynch(self, name):
        raise RuntimeError("No attribute")

    def read_attribute_reply(self, id):
        raise RuntimeError("No attribute id")

    def write_attribute(self, name, value):
        self.logger.info("{0}: Dummy write attribute {1}={2}".format(self.name, name, value))

    def dev_name(self):
        return self.name


class TangoDeviceClient(QtWidgets.QWidget):
    def __init__(self, name, use_sidebar=False, use_bottombar=False, call_setup_layout=True, parent=None):
        QtWidgets.QWidget.__init__(self, parent)

        self.name = name

        self.title_sizes: QTangoSizes = None
        self.attr_sizes: QTangoSizes = None
        self.frame_sizes: QTangoSizes = None
        self.colors = QTangoColors()
        self.top_spacing = 60

        self.titlebar = None
        self.bottombar = None
        self.sidebar = None
        self.layout_data = None
        self.attr_lock = threading.Lock()

        self.logger = logging.getLogger("TangoDeviceClient {0}".format(name))
        self.logger.setLevel(logging.INFO)

        if call_setup_layout:
            self.setup_layout(use_sidebar, use_bottombar)

        self.devices = dict()
        self.attributes = dict()
        self.dev_connect_thread_dict = dict()

    def setup_layout(self, use_sidebar=False, use_bottombar=False):
        s = 'QWidget{background-color: #000000; }'
        self.setStyleSheet(s)

        if self.title_sizes is None:
            self.title_sizes = QTangoSizes()
            self.title_sizes.barHeight = 40
            self.title_sizes.barWidth = 18
            self.title_sizes.readAttributeWidth = 300
            self.title_sizes.writeAttributeWidth = 150
            self.title_sizes.fontStretch = 80
            self.title_sizes.fontType = 'Arial'

        if self.frame_sizes is None:
            self.frame_sizes = QTangoSizes()
            self.frame_sizes.barHeight = 40
            self.frame_sizes.barWidth = 35
            self.frame_sizes.readAttributeWidth = 300
            self.frame_sizes.writeAttributeWidth = 150
            self.frame_sizes.fontStretch = 80
            self.frame_sizes.fontType = 'Arial'

        if self.attr_sizes is None:
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

    def add_spaceritem(self, spacer_item):
        self.layout_data.addSpacerItem(spacer_item)

    def add_attribute(self, attr_name, device_name, callback, update_interval=0.5, single_shot=False,
                      get_info=False, attr_info_slot=None):
        with self.attr_lock:
            attr_dict_name = "{0}_{1}".format(attr_name, device_name)
            if device_name not in self.devices:
                raise KeyError("Device not in dictionary")
            if single_shot is True:
                update_interval = None
            self.attributes[attr_dict_name] = AttributeClass(attr_name, self.devices[device_name], update_interval,
                                                             callback, get_info, attr_info_slot)

    def add_device(self, device_name, tango_name, dummy_fallback=True):
        self.devices[device_name] = DummyDevice(tango_name)
        if tango_name in self.dev_connect_thread_dict.keys():
            return
        self.logger.info("Adding device {0}".format(tango_name))
        f: Future = PyTango.futures.DeviceProxy(tango_name, green_mode=PyTango.GreenMode.Futures,
                                                wait=False, timeout=None)
        # f: Future = PyTango.DeviceProxy(tango_name, green_mode=PyTango.GreenMode.Futures,
        #                                 wait=True, timeout=None)
        f.add_done_callback(self._dev_connected)
        with self.attr_lock:
            self.dev_connect_thread_dict[tango_name] = (f, device_name)

    def closeEvent(self, event):
        with self.attr_lock:
            for a in self.attributes.values():
                self.logger.debug("In closeEvent: Stopping {0}".format(a.name))
                a.stop_read()
            for a in self.attributes.values():
                a.read_thread.join()
            event.accept()
            for f, device_name in self.dev_connect_thread_dict.values():
                f.cancel()

    def _dev_connected(self, future):
        dev_proxy = future.result()
        dev_name = dev_proxy.dev_name()
        self.logger.info("{0} connected!".format(dev_name))
        with self.attr_lock:
            f, device_name = self.dev_connect_thread_dict.pop(dev_name)
            self.devices[device_name] = dev_proxy
            for an in self.attributes.keys():
                dn = self.attributes[an].device.dev_name()
                if dn == dev_name:
                    self.logger.debug("Found attribute {0}, reconnecting".format(an))
                    a: AttributeClass = self.attributes[an]
                    attr_name = a.name
                    a.stop_read()
                    self.attributes[an] = AttributeClass(name=attr_name, device=dev_proxy, interval=a.interval,
                                                         slot=a.callback, get_info=a.get_info, attr_info_slot=a.info_callback)
