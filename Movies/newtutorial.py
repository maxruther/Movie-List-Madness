from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

import sys

class MainWindow(QMainWindow):

    def __init__(self, *args, **kwargs):
        # We must always call the super constructor, or else these won't work.
        super(MainWindow, self).__init__(*args, **kwargs)

        self.setWindowTitle("My Awesome App")

        label = QLabel("THIS IS AWESOME!!!")
        label.setAlignment(Qt.AlignCenter)

        self.setCentralWidget(label)


app = QApplication(sys.argv)

window = MainWindow()
# Windows are invisible by default, so it's important to include the show method!
window.show()


# Starts the event loop
app.exec_()