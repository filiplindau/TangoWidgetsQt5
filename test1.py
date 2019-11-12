from PyQt5 import QtWidgets, QtGui
import sys
from LabelWidgets import QTangoAttributeNameLabel
from SliderCompositeWidgets import QTangoAttributeSlider
from EditCompositeWidgets import QTangoWriteAttributeDouble
import logging

root = logging.getLogger()

while len(root.handlers):
    root.removeHandler(root.handlers[0])

f = logging.Formatter("%(asctime)s - %(module)s.   %(funcName)s - %(levelname)s - %(message)s")
fh = logging.StreamHandler()
fh.setFormatter(f)
root.addHandler(fh)
root.setLevel(logging.INFO)


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)

    s = 'QWidget{background-color: #000000; }'

    myapp = QTangoAttributeSlider()
    myapp.setStyleSheet(s)
    myapp.setAttributeName("apa")
    myapp.show()
    print("{0}".format(myapp.nameLabel.text()))
    sys.exit(app.exec_())
