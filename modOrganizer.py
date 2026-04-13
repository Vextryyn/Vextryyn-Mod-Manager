import os
import shutil
from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QListWidgetItem

MOD_FILENAME_SUFFIXES = (".pak", ".zip", ".mod", ".json")


class ModListWidget(QtWidgets.QWidget):
    @staticmethod
    def is_mod_filename(name):
        return name.lower().endswith(MOD_FILENAME_SUFFIXES)

    def __init__(self, mods_folder="mods", parent=None, on_order_saved=None):
        super(ModListWidget, self).__init__(parent)

        self.mods_folder = mods_folder
        self.mod_order_file = os.path.join(self.mods_folder, "mod_order.txt")
        self.mod_disabled_file = os.path.join(self.mods_folder, "mod_disabled.txt")
        self.on_order_saved = on_order_saved

        layout = QtWidgets.QVBoxLayout(self)

        label = QtWidgets.QLabel(
            "Drag mods to change load order. Uncheck a mod to disable it (excluded from the game). "
            "Click Save Order to write mod_order.txt and mod_disabled.txt and update the active profile."
        )
        label.setWordWrap(True)
        layout.addWidget(label)

        self.mod_list = QtWidgets.QListWidget()
        self.mod_list.setDragDropMode(QtWidgets.QAbstractItemView.InternalMove)
        layout.addWidget(self.mod_list)

        self.mod_list.itemChanged.connect(self._on_item_changed)

        button_layout = QtWidgets.QHBoxLayout()
        layout.addLayout(button_layout)

        self.up_button = QtWidgets.QPushButton("↑ Move Up")
        self.up_button.clicked.connect(self.move_up)
        button_layout.addWidget(self.up_button)

        self.down_button = QtWidgets.QPushButton("↓ Move Down")
        self.down_button.clicked.connect(self.move_down)
        button_layout.addWidget(self.down_button)

        refresh_button = QtWidgets.QPushButton("🔄 Refresh Mods")
        refresh_button.clicked.connect(self.load_mods)
        button_layout.addWidget(refresh_button)

        delete_button = QtWidgets.QPushButton("🗑️ Delete Selected")
        delete_button.clicked.connect(self.delete_selected_mod)
        button_layout.addWidget(delete_button)

        save_button = QtWidgets.QPushButton("💾 Save Order")
        save_button.clicked.connect(self.save_mod_order)
        button_layout.addWidget(save_button)

        self.status_label = QtWidgets.QLabel("")
        layout.addWidget(self.status_label)

        self.load_mods()

    def set_mods_folder(self, folder, profile_mods=None):
        self.mods_folder = folder
        self.mod_order_file = os.path.join(self.mods_folder, "mod_order.txt")
        self.mod_disabled_file = os.path.join(self.mods_folder, "mod_disabled.txt")
        self.load_mods(profile_mods=profile_mods)

    def get_mod_profile_state(self):
        order = []
        disabled = []
        for i in range(self.mod_list.count()):
            item = self.mod_list.item(i)
            name = item.text()
            order.append(name)
            if item.checkState() == Qt.Unchecked:
                disabled.append(name)
        return {"order": order, "disabled": disabled}

    def _read_disabled(self):
        if not os.path.exists(self.mod_disabled_file):
            return set()
        with open(self.mod_disabled_file, "r", encoding="utf-8") as f:
            return {line.strip() for line in f if line.strip()}

    def _on_item_changed(self, item):
        if self.mod_list.signalsBlocked():
            return
        n = self.mod_list.count()
        enabled = sum(
            1
            for i in range(n)
            if self.mod_list.item(i).checkState() == Qt.Checked
        )
        self.status_label.setText(
            f"{enabled} enabled / {n - enabled} disabled — click Save Order to apply to the game."
        )

    def load_mods(self, profile_mods=None):
        self.mod_list.blockSignals(True)
        self.mod_list.clear()

        if not os.path.exists(self.mods_folder):
            os.makedirs(self.mods_folder)

        disk_mods = sorted(
            f
            for f in os.listdir(self.mods_folder)
            if self.is_mod_filename(f)
        )

        saved_order = []
        disabled = set()

        if profile_mods and isinstance(profile_mods, dict):
            saved_order = [
                x for x in (profile_mods.get("order") or []) if isinstance(x, str) and x
            ]
            for x in profile_mods.get("disabled") or []:
                if isinstance(x, str) and x:
                    disabled.add(x)
        else:
            if os.path.exists(self.mod_order_file):
                with open(self.mod_order_file, "r", encoding="utf-8") as f:
                    saved_order = [line.strip() for line in f if line.strip()]
            disabled = self._read_disabled()

        if saved_order:
            ordered = [m for m in saved_order if m in disk_mods]
            seen = set(ordered)
            for m in disk_mods:
                if m not in seen:
                    ordered.append(m)
                    seen.add(m)
            mods = ordered
        else:
            mods = disk_mods

        for mod in mods:
            item = QListWidgetItem(mod)
            item.setFlags(item.flags() | Qt.ItemIsUserCheckable | Qt.ItemIsDragEnabled)
            item.setCheckState(Qt.Unchecked if mod in disabled else Qt.Checked)
            self.mod_list.addItem(item)

        self.mod_list.blockSignals(False)

        if profile_mods is not None and isinstance(profile_mods, dict):
            self._write_disk_meta_from_list()

        n = len(mods)
        en = sum(1 for i in range(n) if self.mod_list.item(i).checkState() == Qt.Checked)
        self.status_label.setText(
            f"Loaded {n} mod(s) from '{self.mods_folder}' ({en} enabled, {n - en} disabled)."
        )

    def delete_selected_mod(self):
        selected_items = self.mod_list.selectedItems()
        if not selected_items:
            self.status_label.setText("No mod selected to delete!")
            return

        for item in selected_items:
            mod_name = item.text()
            mod_path = os.path.join(self.mods_folder, mod_name)

            if os.path.exists(mod_path):
                try:
                    os.remove(mod_path)
                except Exception as e:
                    print(f"Error deleting {mod_name}: {e}")

            self.mod_list.takeItem(self.mod_list.row(item))

        self.save_mod_order()

        self.status_label.setText(f"Deleted {len(selected_items)} mod(s).")

    def move_up(self):
        current_row = self.mod_list.currentRow()
        if current_row > 0:
            item = self.mod_list.item(current_row)
            item_prev = self.mod_list.item(current_row - 1)
            text_curr = item.text()
            text_prev = item_prev.text()
            check_curr = item.checkState()
            check_prev = item_prev.checkState()
            item.setText(text_prev)
            item_prev.setText(text_curr)
            item.setCheckState(check_prev)
            item_prev.setCheckState(check_curr)
            self.mod_list.setCurrentRow(current_row - 1)

    def move_down(self):
        current_row = self.mod_list.currentRow()
        if current_row >= 0 and current_row < self.mod_list.count() - 1:
            item = self.mod_list.item(current_row)
            item_next = self.mod_list.item(current_row + 1)
            text_curr = item.text()
            text_next = item_next.text()
            check_curr = item.checkState()
            check_next = item_next.checkState()
            item.setText(text_next)
            item_next.setText(text_curr)
            item.setCheckState(check_next)
            item_next.setCheckState(check_curr)
            self.mod_list.setCurrentRow(current_row + 1)

    def _write_disabled(self, disabled_set):
        with open(self.mod_disabled_file, "w", encoding="utf-8") as f:
            f.write("\n".join(sorted(disabled_set)))
            if disabled_set:
                f.write("\n")

    def save_mod_order(self):
        self._write_disk_meta_from_list()

        if self.on_order_saved:
            self.on_order_saved()

        n = self.mod_list.count()
        disabled_n = sum(
            1
            for i in range(n)
            if self.mod_list.item(i).checkState() == Qt.Unchecked
        )
        self.status_label.setText(
            f"Saved {n} mod(s) in order; {disabled_n} disabled (written to mod_disabled.txt)."
        )

    def _write_disk_meta_from_list(self):
        """Write mod_order.txt / mod_disabled.txt from the current list (no profile callback)."""
        order = []
        disabled = []
        for i in range(self.mod_list.count()):
            item = self.mod_list.item(i)
            name = item.text()
            order.append(name)
            if item.checkState() == Qt.Unchecked:
                disabled.append(name)

        with open(self.mod_order_file, "w", encoding="utf-8") as f:
            f.write("\n".join(order))
            if order:
                f.write("\n")

        self._write_disabled(set(disabled))
