"""
Created on 14 aug 2014

@author: Filip
"""
# -*- coding:utf-8 -*-

from PyQt5 import QtCore

import time
import sys
import threading
import PyTango as pt
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.CRITICAL)


# noinspection PyAttributeOutsideInit
class AttributeClass(QtCore.QObject):
    """ Class that starts a thread for reading a tango attribute.

    The read interval can be set and a signal is emitted after a read.
    Optionally the attribute info can be read asynchronously and signal emitted.

    Callback method can be supplied for these two methods.

    The attribute write value can be set through the attr_write method.

    The thread is killed be calling the stop_read method.

    :param name: Tango name of the attribute
    :param device: Tango device name (e.g. gunlaser/oscillator/finesse)
    :param interval: Time interval for reading the attribute in seconds
    :param slot: Optional method to connect to the attrSignal
    :param get_info: Boolean if the attribute configuration info should also be read
    :param attr_info_slot: Optional method to connect to the attrInfoSignal
    """
    attrSignal = QtCore.pyqtSignal(pt.device_attribute.DeviceAttribute)
    attrInfoSignal = QtCore.pyqtSignal(pt.AttributeInfoEx)

    def __init__(self, name, device, interval, slot=None, get_info=False, attr_info_slot=None):
        super(AttributeClass, self).__init__()
        self.name = name
        self.device = device
        self.interval = interval
        self.get_info = get_info
        self.get_info_flag = get_info
        self.pause_read_flag = False
        self.callback = slot
        self.info_callback = attr_info_slot

        if slot is not None:
            self.attrSignal.connect(slot)

        if attr_info_slot is not None:
            self.attrInfoSignal.connect(attr_info_slot)

        self.last_read_time = time.time()
        self.attr = None
        self.attr_info = None
        self.read_thread = threading.Thread(name=self.name, target=self.attr_read)
        self.stop_thread_flag = False

        self.start_read()

    def attr_read(self):
        logger.debug("Entering attr_read for \"{0}\"".format(self.name))
        reply_ready = True
        while self.stop_thread_flag is False:
            if self.pause_read_flag is True:
                time.sleep(0.1)
            else:
                if self.get_info_flag is True:
                    self.get_info_flag = False
                    try:
                        self.attr_info = self.device.get_attribute_config(self.name)
                        self.attrInfoSignal.emit(self.attr_info)

                    except pt.DevFailed as e:
                        if e.args[0].reason == 'API_DeviceTimeOut':
                            logger.debug('AttrInfo Timeout')
                        else:
                            logger.debug("{0} attrinfo error: {1}".format(self.name, e.args[0].reason))
                        self.attr_info = pt.AttributeInfoEx()
                        self.attrInfoSignal.emit(self.attr_info)
                    except Exception as e:
                        logger.debug("{0} recovering from attrInfo error {1}".format(self.name, str(e)))
                        self.attr_info = pt.AttributeInfoEx()
                        self.attrInfoSignal.emit(self.attr_info)

                t = time.time()

                if self.interval is None:
                    dt = 0
                else:
                    dt = self.interval
                if t-self.last_read_time > dt:
                    self.last_read_time = t
                    try:
                        reply_id = self.device.read_attribute_asynch(self.name)

                        reply_ready = False
                    except pt.DevFailed as e:
                        if e.args[0].reason == 'API_DeviceTimeOut':
                            logger.debug("Timeout")
                        else:
                            logger.debug("{0} read_attribute_asynch error: {1}".format(self.name, e.args[0].reason))
                        self.attr = pt.DeviceAttribute()
                        self.attr.quality = pt.AttrQuality.ATTR_INVALID
                        self.attr.value = None
                        self.attr.w_value = None
                        self.attrSignal.emit(self.attr)

                    except Exception as e:
                        logger.error("{0} recovering from {1}".format(self.name, str(e)))
                        self.attr = pt.DeviceAttribute()
                        self.attr.quality = pt.AttrQuality.ATTR_INVALID
                        self.attr.value = None
                        self.attrSignal.emit(self.attr)

                    while reply_ready is False and self.stop_thread_flag is False:
                        try:
                            self.attr = self.device.read_attribute_reply(reply_id)
                            reply_ready = True
                            # logger.debug("{0} Reply: {1}".format(self.name, self.attr))
                            self.attrSignal.emit(self.attr)
                            # Read only once if interval = None:
                            if self.interval is None:
                                self.stop_thread_flag = True
                                self.interval = 0.0
                        except pt.DevFailed as e:
                            logger.info("Exception e: {0}".format(e))
                            if isinstance(e, pt.AsynReplyNotArrived):
                                time.sleep(0.1)
                            else:
                                reply_ready = True
                                logger.debug("Error reply {0}: {1}".format(self.name, str(e)))
                                self.attr = pt.DeviceAttribute()
                                self.attr.quality = pt.AttrQuality.ATTR_INVALID
                                self.attr.value = None
                                self.attr.w_value = None
                                self.attrSignal.emit(self.attr)

                if self.interval is not None:
                    time.sleep(self.interval)
                else:
                    time.sleep(0.2)
        logger.debug("{0} waiting for final reply".format(self.name))
        final_timeout = 1.0  # Wait max 1 s
        final_start_time = time.time()
        final_timeout_flag = False
        while reply_ready is False and final_timeout_flag is False:
            try:
                self.attr = self.device.read_attribute_reply(reply_id)
                reply_ready = True
                self.attrSignal.emit(self.attr)
            except Exception as e:
                if e.args[0].reason == 'API_AsynReplyNotArrived':
                    time.sleep(0.1)
                else:
                    reply_ready = True
                    logger.debug("Error reply {0}: {1}".format(self.name, str(e)))
                    self.attr = pt.DeviceAttribute()
                    self.attr.quality = pt.AttrQuality.ATTR_INVALID
                    self.attr.value = None
                    self.attr.w_value = None
                    self.attrSignal.emit(self.attr)
            if time.time()-final_start_time > final_timeout:
                final_timeout_flag = True
        if final_timeout_flag is False:
            logger.debug("{0}... Thread stopped".format(self.name))
        else:
            logger.debug("{0}... Thread timed out".format(self.name))

    def attr_write(self, wvalue):
        logger.debug("{0} attr_write: {1}".format(self.name, wvalue))
        self.device.write_attribute(self.name, wvalue)

    def stop_read(self):
        """
        Stop the tango attribute reading thread
        :return:
        """
        self.stop_thread_flag = True

    def stopRead(self):
        # For compatiblity
        self.stop_thread_flag = True

    def start_read(self):
        """
        Start the tango attribute reading thread. First stop the old thread if it was running.
        :return:
        """
        self.stop_read()
        if self.read_thread.is_alive() is True:
            self.read_thread.join(3.0)
        self.stop_thread_flag = False
        self.pause_read_flag = False
        self.read_thread = threading.Thread(name=self.name, target=self.attr_read)
        self.read_thread.start()

    def pause_read(self):
        """
        Signal that the read thread should pause. The thread is still running, but tango
        calls are paused.
        :return:
        """
        self.pause_read_flag = True

    def unpause_read(self):
        """
        Signal that the read thread should unpause.
        :return:
        """
        self.pause_read_flag = False

    def init_retrieve_attribute_info(self):
        """
        Init retrieval of attribute info from the tango attribute object
        :return:
        """
        self.get_info_flag = True

    def get_attr_info(self):
        """
        Get the tango attribute info.
        :return: Tango attribute info AttributeInfoEx if retrieved, otherwise return False
        """
        if self.attr_info is not None:
            return self.attr_info
        else:
            return False
