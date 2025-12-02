import os
from PyQt5.QtCore import Qt, QRect
from PyQt5.QtGui import QPixmap, QPainter, QPen, QColor
from PyQt5.QtWidgets import QLabel, QWidget, QVBoxLayout
import xml.etree.ElementTree as ET
from overlay import OverlayLabel

class OtherWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.label = OverlayLabel(self)
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setMinimumSize(50, 50)

        layout = QVBoxLayout(self)
        layout.addWidget(self.label)
        layout.setContentsMargins(0, 0, 0, 0)

        self.pixmap_original = None
        self.image_path = None
        self.cursors_data = []

    def set_image(self, path, xml_path=None):
        if not path or not os.path.exists(path):
            self.label.clear()
            self.pixmap_original = None
            self.cursors_data = []
            return

        self.pixmap_original = QPixmap(path)

        # Load XML
        cursors_data = []
        if xml_path and os.path.exists(xml_path):
            import xml.etree.ElementTree as ET
            try:
                tree = ET.parse(xml_path)
                root = tree.getroot()
                for elem in root.findall(".//cursor"):
                    data = {}
                    xywh = elem.get("xywh")
                    if xywh:
                        data["rect"] = tuple(map(int, xywh.split(",")))
                    if elem.get("hotSpotX") and elem.get("hotSpotY"):
                        data["hotspot"] = (int(elem.get("hotSpotX")), int(elem.get("hotSpotY")))
                    data["name"] = elem.get("name")
                    if elem.get("ref"):
                        data["ref"] = elem.get("ref")
                    cursors_data.append(data)
            except Exception as e:
                print("Error parsing XML:", e)

        self.cursors_data = cursors_data
        self.label.set_image(self.pixmap_original, cursors_data=self.cursors_data)

