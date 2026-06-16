import sys

from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
)
import pyqtgraph as pg


class Dashboard(QMainWindow):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("VESC Dashboard")
        self.resize(1000, 700)

        # Central widget
        central = QWidget()
        self.setCentralWidget(central)

        # Main layout
        layout = QVBoxLayout()
        central.setLayout(layout)

        # TODO: add plots here
        self.voltage_plot = pg.PlotWidget(title="Voltage")
        self.current_plot = pg.PlotWidget(title="Current")
        layout.addWidget(self.voltage_plot)
        layout.addWidget(self.current_plot)
        self.voltage_plot.plot([], pen='r')
        self.current_plot.plot([], pen='b')

        self.show()


