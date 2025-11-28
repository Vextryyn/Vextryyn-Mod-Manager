import platform
from PyQt5 import QtWidgets, QtGui
import subprocess

def system_theme(app: QtWidgets.QApplication):

    current_os = platform.system()

    if current_os == "Windows":
        app.setStyle("windows")
        try:
            import winreg
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize"
            )
            apps_use_light_theme, _ = winreg.QueryValueEx(key, "AppsUseLightTheme")
            winreg.CloseKey(key)
        except Exception:
            apps_use_light_theme = 1

        if apps_use_light_theme:
            app.setPalette(app.style().standardPalette())
        else:
            dark_palette = QtGui.QPalette()
            dark_color = QtGui.QColor(53, 53, 53)
            disabled_color = QtGui.QColor(127, 127, 127)

            dark_palette.setColor(QtGui.QPalette.Window, dark_color)
            dark_palette.setColor(QtGui.QPalette.WindowText, QtGui.QColor("white"))
            dark_palette.setColor(QtGui.QPalette.Base, QtGui.QColor(42, 42, 42))
            dark_palette.setColor(QtGui.QPalette.AlternateBase, dark_color)
            dark_palette.setColor(QtGui.QPalette.ToolTipBase, QtGui.QColor("white"))
            dark_palette.setColor(QtGui.QPalette.ToolTipText, QtGui.QColor("white"))
            dark_palette.setColor(QtGui.QPalette.Text, QtGui.QColor("white"))
            dark_palette.setColor(QtGui.QPalette.Disabled, QtGui.QPalette.Text, disabled_color)
            dark_palette.setColor(QtGui.QPalette.Button, dark_color)
            dark_palette.setColor(QtGui.QPalette.ButtonText, QtGui.QColor("white"))
            dark_palette.setColor(QtGui.QPalette.Disabled, QtGui.QPalette.ButtonText, disabled_color)
            dark_palette.setColor(QtGui.QPalette.BrightText, QtGui.QColor("red"))
            dark_palette.setColor(QtGui.QPalette.Link, QtGui.QColor(42, 130, 218))
            dark_palette.setColor(QtGui.QPalette.Highlight, QtGui.QColor(42, 130, 218))
            dark_palette.setColor(QtGui.QPalette.Disabled, QtGui.QPalette.Highlight, QtGui.QColor(80, 80, 80))
            dark_palette.setColor(QtGui.QPalette.HighlightedText, QtGui.QColor("white"))
            dark_palette.setColor(QtGui.QPalette.Disabled, QtGui.QPalette.HighlightedText, disabled_color)

            app.setPalette(dark_palette)

    elif current_os == "Darwin":
        app.setStyle(QtWidgets.QStyleFactory.create("macintosh"))
        app.setPalette(app.style().standardPalette())

    elif current_os == "Linux":
        dark_mode = is_linux_dark_mode()
        app.setPalette(linux_palette(dark_mode))



def is_linux_dark_mode() -> bool:
    try:
        out = subprocess.check_output(
            ["gsettings", "get", "org.gnome.desktop.interface", "gtk-theme"]
        ).decode().strip().strip("'")  # remove quotes
        return "dark" in out.lower()
    except Exception:
        return False

def linux_palette(dark: bool):
    if dark:
        dark_palette = QtGui.QPalette()
        dark_color = QtGui.QColor(53, 53, 53)
        disabled_color = QtGui.QColor(127, 127, 127)
        dark_palette.setColor(QtGui.QPalette.Window, dark_color)
        dark_palette.setColor(QtGui.QPalette.WindowText, QtGui.QColor("white"))
        dark_palette.setColor(QtGui.QPalette.Base, QtGui.QColor(42, 42, 42))
        dark_palette.setColor(QtGui.QPalette.AlternateBase, dark_color)
        dark_palette.setColor(QtGui.QPalette.ToolTipBase, QtGui.QColor("white"))
        dark_palette.setColor(QtGui.QPalette.ToolTipText, QtGui.QColor("white"))
        dark_palette.setColor(QtGui.QPalette.Text, QtGui.QColor("white"))
        dark_palette.setColor(QtGui.QPalette.Disabled, QtGui.QPalette.Text, disabled_color)
        dark_palette.setColor(QtGui.QPalette.Button, dark_color)
        dark_palette.setColor(QtGui.QPalette.ButtonText, QtGui.QColor("white"))
        dark_palette.setColor(QtGui.QPalette.Disabled, QtGui.QPalette.ButtonText, disabled_color)
        dark_palette.setColor(QtGui.QPalette.BrightText, QtGui.QColor("red"))
        dark_palette.setColor(QtGui.QPalette.Link, QtGui.QColor(42, 130, 218))
        dark_palette.setColor(QtGui.QPalette.Highlight, QtGui.QColor(42, 130, 218))
        dark_palette.setColor(QtGui.QPalette.Disabled, QtGui.QPalette.Highlight, QtGui.QColor(80, 80, 80))
        dark_palette.setColor(QtGui.QPalette.HighlightedText, QtGui.QColor("white"))
        dark_palette.setColor(QtGui.QPalette.Disabled, QtGui.QPalette.HighlightedText, disabled_color)
        return dark_palette
    else:
        return QtWidgets.QApplication.palette()
