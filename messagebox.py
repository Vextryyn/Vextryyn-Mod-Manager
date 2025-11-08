from PyQt5.QtWidgets import QDialog, QLabel, QVBoxLayout, QPushButton, QHBoxLayout
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt, QT_VERSION_STR
import PyQt5
import platform
import sys

class AboutWindow(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("About Archetype Manager")
        self.setFixedSize(400, 440)
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()

        # App name + version
        title = QLabel("Archetype Manager v0.0.1a")
        title.setFont(QFont("Arial", 16, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)

        # Description
        desc = QLabel(
            "<p>This manager is made for easy customization of the Archetype Theme by ssjshields.</p>"
            '<p>Archetype Theme by: <b>ssjshields</b><br>'
            'Donate to ssjshields: <a href="https://ko-fi.com/ssjshields">ko-fi.com/ssjshields</a></p>'
            '<p>Archetype Manager by <b>Vextryyn</b><br>'
            'Donate to Vextryyn:<br>'
            'BTC: 1PRVhoBaeP5zhKRjzXMYh9hpGJut4QeEDn</p>'
            "<p>If you want to donate any other cryptos, I am a coin collector so I am more than happy to make a new wallet for anything</p>"
            "<p>© 2025 GNU General Public License version 3 (GPLv3)</p>"
        )
        desc.setWordWrap(True)
        desc.setAlignment(Qt.AlignLeft)
        desc.setOpenExternalLinks(True)
        desc.setTextInteractionFlags(Qt.TextSelectableByMouse | Qt.LinksAccessibleByMouse)
        pyqt_version = PyQt5.QtCore.PYQT_VERSION_STR
        qt_version = QT_VERSION_STR
        python_version = platform.python_version()

        version_info = QLabel(
            f"<hr><p><b>Python:</b> {python_version}<br>"
            f"<b>PyQt:</b> {pyqt_version}<br>"
            f"<b>Qt:</b> {qt_version}</p>"
        )
        version_info.setAlignment(Qt.AlignCenter)
        version_info.setWordWrap(True)

        # OK button
        ok_btn = QPushButton("OK")
        ok_btn.clicked.connect(self.accept)
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        btn_layout.addWidget(ok_btn)
        btn_layout.addStretch()

        layout.addWidget(title)
        layout.addWidget(desc)
        layout.addWidget(version_info)
        layout.addLayout(btn_layout)

        self.setLayout(layout)
