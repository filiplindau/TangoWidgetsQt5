from PyQt5 import QtWidgets, QtGui
import sys
from LabelWidgets import QTangoAttributeNameLabel
from SliderCompositeWidgets import QTangoAttributeSlider
from EditCompositeWidgets import QTangoWriteAttributeDouble
from TangoDeviceClient import TangoDeviceClient
from ColorDefinitions import QTangoSizes, QTangoColors
import logging

logger = logging.getLogger()

while len(logger.handlers):
    logger.removeHandler(logger.handlers[0])

f = logging.Formatter("%(asctime)s - %(module)s.   %(funcName)s - %(levelname)s - %(message)s")
fh = logging.StreamHandler()
fh.setFormatter(f)
logger.addHandler(fh)
logger.setLevel(logging.INFO)


class TestDeviceClient(TangoDeviceClient):
    """ Example device client using the test laser finesse and redpitaya5.

    """
    def __init__(self):
        TangoDeviceClient.__init__(self, "Astrella Overview", use_sidebar=False, use_bottombar=False, call_setup_layout=False)

        self.fund_enabled_data = False
        self.harm_enabled_data = False

        self.title_sizes = QTangoSizes()
        self.title_sizes.barHeight = 30
        self.top_spacing = 20
        self.setup_layout(False, False)
        self.attr_sizes.barHeight = 15
        self.attr_sizes.readAttributeHeight = 170
        self.attr_sizes.fontStretch = 100

        # Slider setup
        #

        self.slider = QTangoAttributeSlider("Power", self.attr_sizes, self.colors, show_write_widget=True, slider_style=4)
        self.slider.setSliderLimits(-10, 200)
        self.slider.newWriteValueSignal.connect(self.write_power)

        self.slider2 = QTangoAttributeSlider("Pos", self.attr_sizes, self.colors, show_write_widget=True, slider_style=4)
        self.slider2.setSliderLimits(-10, 200)
        self.slider2.newWriteValueSignal.connect(self.write_pos)
        self.slider2.writeValueEdit.setDataFormat("%d")
        self.slider2.valueSlider.data_format = "d"
        self.add_widget(self.slider)
        self.add_widget(self.slider2)

    def write_power(self):
        new_value = self.slider.getWriteValue()
        logger.info("New slider value: {0}".format(new_value))
        self.slider.setAttributeValue(new_value)

    def write_pos(self):
        new_value = self.slider2.getWriteValue()
        logger.info("New slider2 value: {0}".format(new_value))
        self.slider2.setAttributeValue(new_value)


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)

    # s = 'QWidget{background-color: #000000; }'
    #
    # myapp = QTangoAttributeSlider()
    # myapp.setStyleSheet(s)
    # myapp.setAttributeName("apa")
    # myapp.show()
    # print("{0}".format(myapp.nameLabel.text()))
    # sys.exit(app.exec_())

    myapp = TestDeviceClient()
    myapp.show()
    sys.exit(app.exec_())
