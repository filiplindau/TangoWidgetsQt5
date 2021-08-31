"""
Connect to devices and subscribe to events for attributes

:created: 2021-07-01

:author: Filip Lindau <filip.lindau@maxiv.lu.se>
"""
# -*- coding:utf-8 -*-

from PyQt5 import QtCore

import time
import sys
import threading
import PyTango as pt
import logging
from concurrent.futures import Future

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class Device(QtCore.QObject):
    attrSignal = QtCore.pyqtSignal(pt.device_attribute.DeviceAttribute)
    attrInfoSignal = QtCore.pyqtSignal(pt.AttributeInfoEx)

    def __init__(self, name):
        super(Device, self).__init__()
        self.name = name
        self.logger = logging.getLogger("{0} {1}".format(self.__class__.__name__, name))
        self.device_proxy: pt.DeviceProxy = None
        self.attribute_event_dict = dict()
        self._dev_connecting_future = None
        self._attr_pending_list = list()
        self.connect()

    def connect(self):
        self.disconnect()
        self._dev_connecting_future = None
        f: Future = pt.DeviceProxy(tango_name, green_mode=pt.GreenMode.Futures, wait=True, timeout=None)
        f.add_done_callback(self._dev_connected)
        self._dev_connecting_future = f

    def disconnect(self):
        # Unsuscribe all events
        for attr_ev in self.attribute_event_dict.values():
            self.device_proxy.unsubscribe_event(attr_ev)
        self.device_proxy = None
        self.attribute_event_dict = dict()
        self._attr_pending_list = list()

    def _dev_connected(self, f):
        self.device_proxy = f.result()
        for a in self._attr_pending_list:
            self.sub_attr(a)

    def add_attribute(self, attr_name):
        if self.device_proxy is None:
            self._attr_pending_list.append(attr_name)

    def sub_attr(self, attr_name):
        self.unsub_attr(attr_name)
        ev_id = self.device_proxy.subscribe_event(attr_name, pt.EventType.CHANGE_EVENT, self.event_callback, stateless=True)
        self.attribute_event_dict[attr_name] = ev_id

    def unsub_attr(self, attr_name):
        if attr_name in self.attribute_event_dict.values():
            self.device_proxy.unsubscribe_event(ev_id)

    def event_callback(self, ev):
        self.logger.debug("{0}: event {1}".format(self.name, ev))


class DeviceEvents(QtCore.QObject):
    attrSignal = QtCore.pyqtSignal(pt.device_attribute.DeviceAttribute)
    attrInfoSignal = QtCore.pyqtSignal(pt.AttributeInfoEx)

    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        super(DeviceEvents, self).__init__()
        self.device_dict = dict()
        self.attribute_event_dict = dict()
        self._dev_connecting_dict = dict()
        self._attr_sub_dict = dict()

    def add_device(self, name, tango_name):
        self.logger.info("Adding device {0} ({1})".format(name, tango_name))
        if tango_name in self._dev_connecting_dict.keys():
            self.logger.info("Already connecting to device {0}, skipping".format(tango_name))
            return
        f: Future = pt.DeviceProxy(tango_name, green_mode=pt.GreenMode.Futures, wait=True, timeout=None)
        f.add_done_callback(self._dev_connected)
        self._dev_connecting_dict[tango_name] = (f, name)

    def _dev_connected(self, f):
        dev_proxy: pt.DeviceProxy = f.result()
        dev_name = dev_proxy.dev_name()
        self.logger.info("{0} connected!".format(dev_name))
        f, name = self.dev_connect_thread_dict.pop(dev_name)
        self.devices[name] = dev_proxy

    def add_attribute(self, attribute_name, device_name):
        self.logger.info("Adding attribute {0} on {1}".format(attribute_name, device_name))
        attr_key = "{0}/{1}".format(device_name, attribute_name)
        if device_name not in self.device_dict.keys():
            self.logger.error("")
            self._attr_sub_dict
            self.add_device(device_name, device_name)


        if attr_key in self.attribute_event_dict.keys():
            return

        self.attribute_event_dict[attr_key]
