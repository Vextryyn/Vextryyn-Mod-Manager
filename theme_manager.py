import os
import shutil
import zipfile
import xml.etree.ElementTree as ET
from PyQt5.QtWidgets import QMessageBox, QWidget


class ThemeManager:
    def __init__(self, custom_dir=None):
        # Default to ./CustomThemes
        self.custom_dir = custom_dir or os.path.join(os.getcwd(), "CustomThemes")
        os.makedirs(self.custom_dir, exist_ok=True)

    def add_theme_from_zip(self, zip_path, parent_widget=None):
        if not os.path.exists(zip_path):
            self._show_message("Error", f"ZIP file does not exist:\n{zip_path}", parent_widget)
            return None

        zip_name = os.path.splitext(os.path.basename(zip_path))[0]
        extract_path = os.path.join(self.custom_dir, zip_name)

        try:
            # Check if login-animation.xml exists inside ZIP first
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                if "login-animation.xml" not in zip_ref.namelist():
                    self._show_message(
                        "Missing login-animation.xml",
                        "The ZIP does not contain a login-animation.xml file.",
                        parent_widget
                    )
                    return None

                # Now safe to extract
                if os.path.exists(extract_path):
                    shutil.rmtree(extract_path)
                os.makedirs(extract_path, exist_ok=True)
                zip_ref.extractall(extract_path)

            # Rename login-animation.xml
            old_xml_path = os.path.join(extract_path, "login-animation.xml")
            new_xml_path = os.path.join(extract_path, f"{zip_name}.xml")
            os.rename(old_xml_path, new_xml_path)

            # Remove unwanted <theme> entries
            tree = ET.parse(new_xml_path)
            root = tree.getroot()
            modified = False
            for theme_tag in root.findall("theme"):
                if theme_tag.attrib.get("name") in ["logingui", "characterselectgui"]:
                    root.remove(theme_tag)
                    modified = True
            if modified:
                tree.write(new_xml_path)

            self._show_message(
                "Theme Added",
                f"Successfully added theme:\n{zip_name}.xml in folder {zip_name}",
                parent_widget
            )
            return new_xml_path

        except Exception as e:
            self._show_message(
                "Error",
                f"Failed to extract file:\n{str(e)}",
                parent_widget
            )
            return None

    def scan_themes(self):
        """
        Returns a list of all XML themes in the CustomThemes folder
        (including subfolders)
        """
        themes = []
        for root, _, files in os.walk(self.custom_dir):
            for f in files:
                if f.lower().endswith(".xml"):
                    themes.append(os.path.join(root, f))
        return sorted(themes)

    def _show_message(self, title, message, parent_widget=None):
        """
        Safely show a message box if parent_widget is a QWidget,
        otherwise print to console.
        """
        if isinstance(parent_widget, QWidget):
            QMessageBox.information(parent_widget, title, message)
        else:
            print(f"[{title}] {message}")
