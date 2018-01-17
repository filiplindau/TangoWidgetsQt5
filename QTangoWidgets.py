# -*- coding:utf-8 -*-
"""
Created on Feb 14, 2013

@author: Filip
"""
from PyQt5 import QtWidgets, QtCore, QtGui
import sys
from TangoDeviceClient import TangoDeviceClient
from SliderCompositeWidgets import QTangoAttributeSlider
from SpectrumCompositeWidgets import QTangoReadAttributeSpectrum
from ButtonWidgets import QTangoCommandSelection
from LabelWidgets import QTangoStartLabel, QTangoAttributeUnitLabel, QTangoReadAttributeLabel
from LabelCompositeWidgets import QTangoDeviceNameStatus
from EditWidgets import QTangoReadAttributeSpinBox, QTangoWriteAttributeSpinBox
import logging

root = logging.getLogger()

while len(root.handlers):
    root.removeHandler(root.handlers[0])

f = logging.Formatter("%(asctime)s - %(module)s.   %(funcName)s - %(levelname)s - %(message)s")
fh = logging.StreamHandler()
fh.setFormatter(f)
root.addHandler(fh)
root.setLevel(logging.DEBUG)


class TestDeviceClient(TangoDeviceClient):
    """ Example device client using the test laser finesse and redpitaya5.

    """
    def __init__(self):
        TangoDeviceClient.__init__(self, "Finesse", use_sidebar=False, use_bottombar=True)
        self.power_slider = QTangoAttributeSlider(self.attr_sizes, self.colors, show_write_widget=True)
        self.power_slider.setSliderLimits(0, 6)
        self.power_slider.setAttributeName("Power")
        self.power_slider.newValueSignal.connect(self.write_power)
        self.add_widget(self.power_slider, defer_update=True)

        self.add_device("finesse", "testlaser/oscillator/finesse")
        self.add_attribute("power", "finesse", self.read_power, update_interval=0.3, single_shot=False,
                           get_info=True, attr_info_slot=self.power_slider.configureAttribute)

        self.temperature_slider = QTangoAttributeSlider(self.attr_sizes, self.colors, show_write_widget=False,
                                                        slider_style=3)
        self.temperature_slider.setSliderLimits(20, 30)
        self.temperature_slider.setAttributeName("Temperature")
        self.add_widget(self.temperature_slider, defer_update=True)

        self.add_attribute("lasertemperature", "finesse", self.read_temperature, update_interval=0.5, single_shot=False,
                           get_info=True, attr_info_slot=self.temperature_slider.configureAttribute)

        self.error_trace = QTangoReadAttributeSpectrum(self.attr_sizes, self.colors)
        self.error_trace.setAttributeName("Error trace")
        self.error_trace.setMaximumHeight(60)
        self.add_widget(self.error_trace, defer_update=False)

        self.add_device("redpitaya5", "testlaser/devices/redpitaya5")
        self.add_attribute("waveform1", "redpitaya5", self.read_errortrace, update_interval=0.3, single_shot=False,
                           get_info=True, attr_info_slot=self.error_trace.configureAttribute)
        self.add_attribute("timevector", "redpitaya5", self.read_timevector, update_interval=0.3, single_shot=True)
        self.error_timevector = []

        self.finesse_commands = QTangoCommandSelection("Laser operation", self.attr_sizes, self.colors)
        self.finesse_commands.addCmdButton("On", self.finesse_on)
        self.finesse_commands.addCmdButton("Off", self.finesse_off)
        self.add_widget(self.finesse_commands)

        self.add_attribute("status", "finesse", self.finesse_status, update_interval=0.3, single_shot=False)

    def read_power(self, data):
        root.debug("In read_power: {0}".format(data.value))
        self.power_slider.setAttributeValue(data)

    def read_temperature(self, data):
        root.debug("In read_temperature: {0}".format(data.value))
        self.temperature_slider.setAttributeValue(data)

    def write_power(self):
        new_power = self.power_slider.getWriteValue()
        root.debug("In write_power: new value {0}".format(new_power))
        self.attributes["power_finesse"].attr_write(new_power)

    def read_timevector(self, data):
        self.error_timevector = data.value

    def read_errortrace(self, data):
        if len(self.error_timevector) == len(data.value):
            self.error_trace.setSpectrum(self.error_timevector, data)

    def finesse_on(self):
        self.devices["finesse"].command_inout_asynch("on", forget=True)

    def finesse_off(self):
        self.devices["finesse"].command_inout_asynch("off", forget=True)

    def finesse_status(self, data):
        self.finesse_commands.setStatus(data)

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)

    splash_pix = QtGui.QPixmap('splash_tangoloading.png')
    splash = QtWidgets.QSplashScreen(splash_pix, QtCore.Qt.WindowStaysOnTopHint)
    splash.setMask(splash_pix.mask())
    splash.show()
    splash.showMessage('         Importing modules', alignment=QtCore.Qt.AlignBottom | QtCore.Qt.AlignLeft,
                       color=QtGui.QColor('#66cbff'))
    app.processEvents()

    splash.showMessage('         Starting GUI', alignment=QtCore.Qt.AlignBottom | QtCore.Qt.AlignLeft,
                       color=QtGui.QColor('#66cbff'))
    app.processEvents()
    myapp = TestDeviceClient()
    myapp.show()
    splash.finish(myapp)
    sys.exit(app.exec_())


