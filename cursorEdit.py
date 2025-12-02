from PyQt5 import QtWidgets, QtCore
import xml.etree.ElementTree as ET
import os

class CursorEdit(QtWidgets.QDialog):
    def __init__(self, xml_path, on_save=None, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Edit Cursor Definitions")
        self.resize(600, 500)

        self.xml_path = xml_path
        self.on_save = on_save

        layout = QtWidgets.QVBoxLayout(self)
        scroll = QtWidgets.QScrollArea()
        scroll.setWidgetResizable(True)
        layout.addWidget(scroll)

        container = QtWidgets.QWidget()
        self.form_layout = QtWidgets.QFormLayout(container)
        scroll.setWidget(container)

        self.tree = ET.parse(self.xml_path)
        self.root = self.tree.getroot()

        self.fields = {}

        for elem in self.root.findall(".//cursor"):
            name = elem.get("name")

            row_widget = QtWidgets.QWidget()
            row_layout = QtWidgets.QHBoxLayout(row_widget)

            fields = {}

            if elem.get("ref"):
                ref_edit = QtWidgets.QLineEdit(elem.get("ref"))
                fields["ref"] = ref_edit
                row_layout.addWidget(QtWidgets.QLabel(name + " ref →"))
                row_layout.addWidget(ref_edit)

            else:
                hotX = QtWidgets.QLineEdit(elem.get("hotSpotX", ""))
                hotY = QtWidgets.QLineEdit(elem.get("hotSpotY", ""))
                xywh = QtWidgets.QLineEdit(elem.get("xywh", ""))

                fields["hotSpotX"] = hotX
                fields["hotSpotY"] = hotY
                fields["xywh"] = xywh

                row_layout.addWidget(QtWidgets.QLabel(name))
                row_layout.addWidget(QtWidgets.QLabel("hotSpotX"))
                row_layout.addWidget(hotX)
                row_layout.addWidget(QtWidgets.QLabel("hotSpotY"))
                row_layout.addWidget(hotY)
                row_layout.addWidget(QtWidgets.QLabel("xywh"))
                row_layout.addWidget(xywh)

            self.fields[name] = fields
            self.form_layout.addRow(row_widget)

        button_row = QtWidgets.QHBoxLayout()
        save_btn = QtWidgets.QPushButton("Save")
        cancel_btn = QtWidgets.QPushButton("Close")

        save_btn.clicked.connect(self.save_changes)
        cancel_btn.clicked.connect(self.reject)

        button_row.addWidget(save_btn)
        button_row.addWidget(cancel_btn)
        layout.addLayout(button_row)

    def save_changes(self):
        for elem in self.root.findall(".//cursor"):
            name = elem.get("name")
            fields = self.fields[name]

            if elem.get("ref"):
                elem.set("ref", fields["ref"].text())
            else:
                elem.set("hotSpotX", fields["hotSpotX"].text())
                elem.set("hotSpotY", fields["hotSpotY"].text())
                elem.set("xywh", fields["xywh"].text())

        self.tree.write(self.xml_path, encoding="utf-8", xml_declaration=True)

        if self.on_save:
            self.on_save()

        QtWidgets.QMessageBox.information(self, "Saved", "Cursor settings updated!")

