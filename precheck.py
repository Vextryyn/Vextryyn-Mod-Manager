import sys
import os
import subprocess
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QPushButton, QVBoxLayout, QMessageBox
from PyQt5.QtCore import Qt

def check_archetype(parent=None):
    """Check if Archetype exists. If not, show dialog and optionally install."""
    if os.path.exists("Archetype"):
        return True  # Folder exists, continue normally

    # Show a blocking window/dialog
    msg_box = QMessageBox(parent)
    msg_box.setWindowTitle("Archetype Missing")
    msg_box.setText("The Archetype folder is missing.\nDo you want to install it now?")
    msg_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
    msg_box.setDefaultButton(QMessageBox.Yes)
    choice = msg_box.exec()

    if choice == QMessageBox.No:
        sys.exit(0)  # Exit app if user cancels

    # User wants to install
    status_win = QWidget()
    status_win.setWindowTitle("Installing Archetype")
    status_win.setFixedSize(300, 100)
    layout = QVBoxLayout()
    status_label = QLabel("Downloading Archetype...")
    status_label.setAlignment(Qt.AlignCenter)
    layout.addWidget(status_label)
    status_win.setLayout(layout)
    status_win.show()
    QApplication.processEvents()  # Force GUI to update

    # Run clone/pull
    repo_url = "https://github.com/ssjshields/archetype"
    target_dir = "Archetype"

    if os.path.exists(target_dir):
        subprocess.run(["git", "-C", target_dir, "pull"])
    else:
        subprocess.run(["git", "clone", repo_url, target_dir])

    status_label.setText("Download complete!")
    QApplication.processEvents()
    status_win.close()
    return True
