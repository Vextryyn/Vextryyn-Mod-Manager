import sys
import os
import subprocess
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout, QMessageBox
from PyQt5.QtCore import Qt

def check_git_installed(parent=None):
    """Check if Git is installed."""
    try:
        subprocess.run(["git", "--version"], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        msg_box = QMessageBox(parent)
        msg_box.setWindowTitle("Git Not Found")
        msg_box.setText("Git is not installed or not in your PATH.\nPlease install Git to continue.")
        msg_box.setIcon(QMessageBox.Critical)
        msg_box.exec()
        return False

def check_archetype(parent=None):
    """Check if Archetype exists. If not, show dialog and optionally install."""
    if not check_git_installed(parent):
        sys.exit(1)

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
