# modOrganizer.py
import os
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtWidgets import QListWidgetItem

class ModListWidget(QtWidgets.QWidget):
    def __init__(self, mods_folder="mods", parent=None):
        super(ModListWidget, self).__init__(parent)

        self.mods_folder = mods_folder
        self.mod_order_file = os.path.join(self.mods_folder, "mod_order.txt")

        # Main layout
        layout = QtWidgets.QVBoxLayout(self)

        # Instruction label
        label = QtWidgets.QLabel("Drag mods to change their load order:")
        layout.addWidget(label)

        # List widget
        self.mod_list = QtWidgets.QListWidget()
        self.mod_list.setDragDropMode(QtWidgets.QAbstractItemView.InternalMove)  # PyQt5 enum
        layout.addWidget(self.mod_list)
        self.mod_list.setAcceptDrops(True)
        self.mod_list.dragEnterEvent = self.dragEnterEvent
        self.mod_list.dropEvent = self.dropEvent

        # Buttons layout
        button_layout = QtWidgets.QHBoxLayout()
        layout.addLayout(button_layout)

        refresh_button = QtWidgets.QPushButton("🔄 Refresh Mods")
        refresh_button.clicked.connect(self.load_mods)
        button_layout.addWidget(refresh_button)

        delete_button = QtWidgets.QPushButton("🗑️ Delete Selected")
        delete_button.clicked.connect(self.delete_selected_mod)
        button_layout.addWidget(delete_button)

        save_button = QtWidgets.QPushButton("💾 Save Order")
        save_button.clicked.connect(self.save_mod_order)
        button_layout.addWidget(save_button)

        # Status label
        self.status_label = QtWidgets.QLabel("")
        layout.addWidget(self.status_label)

        # Initial load
        self.load_mods()

    def load_mods(self):
        self.mod_list.clear()

        # Ensure folder exists
        if not os.path.exists(self.mods_folder):
            os.makedirs(self.mods_folder)

        # List all mods
        mods = sorted([
            f for f in os.listdir(self.mods_folder)
            if f.lower().endswith((".pak", ".zip", ".mod", ".json"))
        ])

        # Load saved order
        saved_order = []
        if os.path.exists(self.mod_order_file):
            with open(self.mod_order_file, "r") as f:
                saved_order = [line.strip() for line in f if line.strip()]

        if saved_order:
            mods = sorted(mods, key=lambda x: saved_order.index(x) if x in saved_order else len(saved_order))

        for mod in mods:
            self.mod_list.addItem(QListWidgetItem(mod))

        self.status_label.setText(f"Loaded {len(mods)} mods from '{self.mods_folder}'.")

    def delete_selected_mod(self):
        selected_items = self.mod_list.selectedItems()
        if not selected_items:
            self.status_label.setText("No mod selected to delete!")
            return

        for item in selected_items:
            mod_name = item.text()
            mod_path = os.path.join(self.mods_folder, mod_name)

            # Remove from disk if it exists
            if os.path.exists(mod_path):
                try:
                    os.remove(mod_path)
                except Exception as e:
                    print(f"Error deleting {mod_name}: {e}")

            # Remove from the list widget
            self.mod_list.takeItem(self.mod_list.row(item))

        self.status_label.setText(f"Deleted {len(selected_items)} mod(s).")

    def save_mod_order(self):
        order = [self.mod_list.item(i).text() for i in range(self.mod_list.count())]
        with open(self.mod_order_file, "w") as f:
            f.write("\n".join(order))
        self.status_label.setText("Saved mod order to mod_order.txt")

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            event.ignore()

    def dropEvent(self, event):
        for url in event.mimeData().urls():
            file_path = url.toLocalFile()
            if os.path.isfile(file_path) and file_path.lower().endswith((".pak", ".zip", ".mod", ".json")):
                # Copy file to mods folder
                dest_path = os.path.join(self.mods_folder, os.path.basename(file_path))
                try:
                    import shutil
                    shutil.copy(file_path, dest_path)
                except Exception as e:
                    print(f"Error copying file: {e}")
        self.load_mods()  # refresh the list after drop