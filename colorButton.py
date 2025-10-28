from PyQt5.QtWidgets import QPushButton, QColorDialog
from PyQt5.QtGui import QColor
from PyQt5.QtCore import pyqtSignal

class ColorButton(QPushButton):
    colorChanged = pyqtSignal(QColor)

    def __init__(self, parent=None, initial_color=QColor("white"), *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self._color = QColor(initial_color)  # clone
        self.update_style()
        self.clicked.connect(self.choose_color)

    def choose_color(self):
        color = QColorDialog.getColor(self._color, self, "Select Color")
        if color.isValid():
            self._color = QColor(color)               # clone
            self.update_style()
            self.colorChanged.emit(QColor(self._color))  # emit clone

    def update_style(self):
        self.setStyleSheet(f"background-color: {self._color.name()};")

    def color(self):
        return QColor(self._color)  # always return a clone

    def setColor(self, color):
        if not isinstance(color, QColor):
            color = QColor(color)
        self._color = QColor(color)                     # clone
        self.update_style()
        self.colorChanged.emit(QColor(self._color))     # emit clone
