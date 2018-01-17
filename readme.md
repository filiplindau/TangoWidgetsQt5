# TangoWidgetsQt5

Qt widgets for GUIs showing Tango control system devices. CSS skinned for dark background and flat look. Threaded attribute reading.

### Prerequisites

PyQt5 and pyqtgraph. PyTango.


### Example usage

```
class TestlaserOscillatorControl(TangoDeviceClient):
    """ Example device client using the test laser finesse and redpitaya5.

    """

    def __init__(self):
        TangoDeviceClient.__init__(self, "Finesse", use_sidebar=False, use_bottombar=True)
        layout_attr_0 = QtWidgets.QVBoxLayout()
        self.layout_data.addLayout(layout_attr_0)

        self.finesse_commands = QTangoCommandSelection("Laser operation", self.attr_sizes, self.colors)
        self.finesse_commands.addCmdButton("On", self.finesse_on)
        self.finesse_commands.addCmdButton("Off", self.finesse_off)
        layout_attr_0.addWidget(self.finesse_commands)
        self.add_device("finesse", "testlaser/oscillator/finesse")
        self.add_attribute("status", "finesse", self.finesse_status, update_interval=0.3, single_shot=False)

        self.power_slider = QTangoAttributeSlider(self.attr_sizes, self.colors, show_write_widget=True)
        self.power_slider.setSliderLimits(0, 6)
        self.power_slider.setAttributeName("Power")
        self.power_slider.newValueSignal.connect(self.write_power)
        layout_attr_0.addWidget(self.power_slider)
        self.add_attribute("power", "finesse", self.read_power, update_interval=0.3, single_shot=False,
                           get_info=True, attr_info_slot=self.power_slider.configureAttribute)
```