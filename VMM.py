import os
import sys
import subprocess
import shutil
import json
import zipfile
import tempfile
from pathlib import Path
import xml.etree.ElementTree as ET
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import QTimer, QDir
from PyQt5.QtGui import QColor, QFont, QGuiApplication
from PyQt5.QtWidgets import QFileDialog, QMessageBox, QApplication
from xmlpreview import XmlAnimationPreview 
from theme_manager import ThemeManager
from counterpreview import CounterPreview
from completeBuild import CompleteBuild
from otherWidget import OtherWidget
from PokeGen import PokeGen
from cursorEdit import CursorEdit
from qttheme import system_theme
from functools import partial
from typing import Dict
from PIL import Image
from messagebox import AboutWindow
from modOrganizer import ModListWidget, MOD_FILENAME_SUFFIXES
from otherWidget import OtherWidget
from colorButton import ColorButton
from precheck import check_archetype, check_git_installed



class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1118, 788)

        base_path = self.get_base_path()
        print("Base path:", base_path)
        self.archetype_root= os.path.join(base_path,"Archetype")
        if not self.ensure_archetype(MainWindow):
            sys.exit(0) 
        self.assets_dir = os.path.join(self.archetype_root,"archetype-theme/theme")
        self.login_dir = os.path.join(self.assets_dir, "backgrounds")
        self.counter_dir = os.path.join(self.assets_dir, "counters")
        self.speech_dir = os.path.join(self.assets_dir,"speech-bubbles")
        self.shape_dir = os.path.join(self.assets_dir,"shapes")
        
        ##custom Content Stuff
        self.customContent = os.path.join(base_path,"CustomContent")
        self.custom_counter = os.path.join(self.customContent,"CustomCounters")
        self.custom_login = os.path.join(self.customContent,"CustomThemes") 
        self.custom_cursor = os.path.join(self.customContent,"CustomCursors")
        self.config_root = self.get_config_base_folder("VexModMan")
        os.makedirs(self.config_root, exist_ok=True)
        self.config_dir = self.config_root

       
       
        self.defaultConfig = os.path.join(base_path, "default.json")
        self.configSelector = os.path.join(self.config_dir, "config_selector.json")
        self.configPath= os.path.join(self.config_dir,"config.json")
        if not hasattr(self, "configPath") or not self.configPath:
            self.configPath = os.path.join(self.config_dir, "config.json")

        self.previewimages = self.resource_path("Preview")
        self.pokeballIcon = os.path.join(self.assets_dir, "res/custom/counter")
        self.gamePath = ""
        self.cursorDir = os.path.join(self.assets_dir,"res/custom/cursors")
        self.cursorXmlDir = os.path.join(self.assets_dir,"cursors")
        self.themeFolder = os.path.join(self.archetype_root,"archetype-theme/theme")
        self.modsLocation = self.get_current_path("mods_path", self.configPath)
        if os.path.exists(self.configPath):
            self.modsLocation = self.get_current_path("mods_path", self.configPath)
        else:
            self.modsLocation = self.get_current_path("mods_path", self.defaultConfig)

        if not self.modsLocation:
            self.modsLocation = self.resource_path("Mods") 

        self.mod_order_file = os.path.join(self.modsLocation, "mod_order.txt")

        self.flipped_cache = {}
        self.mod_order_file = os.path.join(self.modsLocation, "mod_order.txt")
        self.theme_manager = ThemeManager()

        self.centralwidget = QtWidgets.QWidget(MainWindow)
        central_layout = QtWidgets.QVBoxLayout(self.centralwidget)
        self.centralwidget.setObjectName("centralwidget")
        self.tabWidget = QtWidgets.QTabWidget(self.centralwidget)
        self.tabWidget.setGeometry(QtCore.QRect(0, 0, 1116, 721))
        self.tabWidget.setObjectName("tabWidget")

        self._setup_login_tab()
        self._setup_counter_tab()
        self._setup_window_tab()
        self._setup_other_tab()
        self._setup_mods_tab()
        self._setup_archetype_tab()

        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1118, 22))
        self.menubar.setObjectName("menubar")
        self.menuFile = QtWidgets.QMenu(self.menubar)
        self.menuFile.setObjectName("menuFile")
        self.menuHelp = QtWidgets.QMenu(self.menubar)
        self.menuHelp.setObjectName("menuHelp")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.actionSave = QtWidgets.QAction(MainWindow)
        self.actionSave.setObjectName("actionSave")
        self.actionSaveAs = QtWidgets.QAction(MainWindow)
        self.actionSaveAs.setObjectName("actionSaveAs")
        self.actionExit = QtWidgets.QAction(MainWindow)
        self.actionExit.setObjectName("actionExit")
        self.actionLoad = QtWidgets.QAction(MainWindow)
        self.actionLoad.setObjectName("actionLoad")
        self.actionAbout = QtWidgets.QAction(MainWindow)
        self.actionAbout.setObjectName("actionAbout")
        self.actionLoadDefault = QtWidgets.QAction(MainWindow)
        self.actionLoadDefault.setObjectName("actionLoadDefault")

        for action in [self.actionSave, self.actionSaveAs, self.actionLoad, self.actionLoadDefault]:
            self.menuFile.addAction(action)
        self.menuHelp.addAction(self.actionAbout)
        self.menuFile.addSeparator()
        self.menuFile.addAction(self.actionExit)
        self.menubar.addAction(self.menuFile.menuAction())
        self.menubar.addAction(self.menuHelp.menuAction())

        self.status_label_archetype = QtWidgets.QLabel(self.GetArchtype)
        self.status_label_archetype.setGeometry(QtCore.QRect(4, 610, 795, 35))
        self.status_label_archetype.setStyleSheet("color: green; font-size: 18pt;")

        self.status_label_custom_counter = QtWidgets.QLabel(self.counterPreview)
        self.status_label_custom_counter.setGeometry(QtCore.QRect(277, 10, 383, 17))
        self.status_label_custom_counter.setStyleSheet("color: green; font-size: 8pt;")

        self.status_label_mods = QtWidgets.QLabel(self.modButtonsFrame)
        self.status_label_mods.setGeometry(QtCore.QRect(0, 0, 255, 30))
        self.status_label_mods.setStyleSheet("color: green; font-size: 12pt;")

        self.screenFrame = self.create_frame(self.GetArchtype,784,492,305,91,"screenFrame")
        self.screenDrop = QtWidgets.QComboBox(self.screenFrame)
        self.screenDrop.setGeometry(QtCore.QRect(14, 54, 280, 25))
        self.screenDrop.setObjectName("screenDrop")
        self.screenDrop.addItems(["PokeMMO Default", "PokeMMO Default + VKCapture","Gamescope Fullscreen Wayland","Gamescope Fullscreen X11"])
        self.screenDrop.setCurrentIndex(0)
        self.label_29 = self.make_label(self.screenFrame,"label_29",14,True,(10,10,61,29),None)
        self.label_31 = self.make_label(self.screenFrame,"label_31",14,True,(158,10,69,29),None)

        self.screenResW = QtWidgets.QTextEdit(self.screenFrame)
        self.screenResW.setGeometry(QtCore.QRect(76,10,61,29))
        self.screenResW.setText("1920")
        self.screenResW.setObjectName("res_w")
        self.screenResH = QtWidgets.QTextEdit(self.screenFrame)
        self.screenResH.setGeometry(QtCore.QRect(232,10,61,29))
        self.screenResH.setText("1080")
        self.screenResH.setObjectName("res_h")

        self.configFrame = self.create_frame(self.GetArchtype,784,402,305,91,"configFrame")
        self.configDrop = QtWidgets.QComboBox(self.configFrame)
        self.configDrop.setGeometry(QtCore.QRect(14, 54, 280, 25))
        self.configDrop.setObjectName("configDrop")
        self.configLabel = self.make_label(self.configFrame,"configLabel",20,True,(48,8,223,38),None)

        self.retranslateUi(MainWindow)
        self.tabWidget.setCurrentIndex(5)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

        default_colors = {
            self.mainColorW: "#42b9ff",
            self.subColorW: "#1c2328",
            self.buttonColorW: "#263238",
            self.accentColorW: "#2d3b40",
            self.hpHighW: "#82e026",
            self.hpLowW: "#dc2222",
            self.hpMidW: "#ecd031",
            self.xpColorW: "#2eb2f8",
            self.friendshipColorW: "#b61ae8",
            self.fontBorder:"#233031",
            self.fontMainW: "#ffffff",
            self.fontSubW: "#acb7b9",
            self.fontButtonW: "#84959b",
            self.fontDisabledColorW: "#9984959b",
            self.waterbg: "#D91c2328",
            self.waterW: "#dc2222",
            self.berryProgress: "#42b9ff",
            self.berryWarning: "#42b9ff",
            self.iconColorW: "#ffffff",
            self.ballColor: "#42b9ff",
            self.mainColor: "#1c2328",
            self.subColor:"#42b9ff",
            self.minMaxButtonColor:"#ffffff",
            self.berryDisabled:"#ffffff",
            self.reshiramColor:"#1b2526",
            self.reshiramAura:"#cb4e03",
            self.zekromColor:"#070b0b",
            self.zekromAura:"#00a5c9",
            self.ballOutline:"#ffffff",
            self.fontColor:"#ffffff",
        }
        for widget, color in default_colors.items():
            widget.setColor(color)
        self.reshiramAura.setColor(QColor("#cb4e03"))
        self.reshiramColor.setColor(QColor("#1b2526"))
        self.zekromAura.setColor(QColor("#00a5c9"))
        self.zekromColor.setColor(QColor("#070b0b"))

        self.setup_color_hooks() 
        self.update_login_drop()
        self.update_counter_drop()
        self.update_vartiou_drop()
        self.update_counter_preview()   
        self.update_login_preview()
        self.update_window_preview()
        self.update_hp_preview()
        self.update_bubbles_drop()
        self.update_icon_drop()
        self.update_cursor_drop()
        self.update_cursor_preview()

        self.loginDrop.currentIndexChanged.connect(self.update_login_preview)
        self.counterDrop.currentIndexChanged.connect(self.update_counter_preview)
        self.customDrop.currentIndexChanged.connect(self.update_vartiou_drop)
        self.cursorDrop.currentIndexChanged.connect(self.update_cursor_preview)
        self.configDrop.currentIndexChanged.connect(self.on_config_changed)

        for btn, idx in [(self.mainColor, 0), (self.subColor, 1), (self.minMaxButtonColor, 2),
                          (self.ballOutline, 8), (self.ballColor, 7)]:
            btn.colorChanged.connect(lambda c, i=idx: self.counterPreview.set_layer_tint(i, QColor(c)))

        for btn, idx in [(self.buttonColorW, 0), (self.iconColorW, 1), (self.subColorW, 3),
                          (self.accentColorW, 4), (self.mainColorW, 5)]:
            btn.colorChanged.connect(lambda c, i=idx: self.windowPreview.set_layer_tint(i, QColor(c)))

        for btn, idx in [(self.subColorW, 1), (self.hpHighW, 3), (self.hpMidW, 4),
                          (self.hpLowW, 5), (self.xpColorW, 6)]:
            btn.colorChanged.connect(lambda c, i=idx: self.hpBar.set_layer_tint(i, QColor(c)))

        self.downloadArch.clicked.connect(self.downloadLatestArch)
        self.setGamePath.clicked.connect(self.select_game_path)
        self.actionSave.triggered.connect(self.save_config)
        self.actionSaveAs.triggered.connect(self.save_config_as)
        self.actionLoad.triggered.connect(self.load_config)
        self.actionLoadDefault.triggered.connect(self.load_default_config)
        self.actionExit.triggered.connect(MainWindow.close)
        self.actionAbout.triggered.connect(self.show_about_window)
        self.cursorBrowse.clicked.connect(self.handle_cursor_browse)
        self.completeMod.clicked.connect(self.complete_build)
        self.playPokemmo.clicked.connect(self.poke_start)
        self.cursorEditButton.clicked.connect(self.edit_cursor_data)
        self.setModFolder.clicked.connect(self.select_mods_path)


        self.colorLinkedLabels = [
        self.counterText,
        self.windowTextFontMain,
        self.windowTextFontMain2,
        self.windowTextFontSub,
        self.windowTextFontButton1,
        self.windowTextFontButton2,
        self.windowTextFontButton3,
        ]
        
        self.load_last_config()

        self.status_label_archetype2 = self.make_label(
            self.GetArchtype,
            f"<b>Pokemmo Location:</b> {self.get_current_path("game_path",self.configPath)}<br>"
            f"<b>Archetype Status:</b> {self.get_Archstatus()}<br>"
            f"<b>Mod Folder:</b>{os.path.abspath(self.modsLocation)}<br>"
            f"<b>Mod Count:</b> {self.mod_count(self.modsLocation)}",
            16,
            False,
            (5,446,793,143),
            None
        )
        self.status_label_archetype2.setTextFormat(QtCore.Qt.RichText)
        self.update_archetype_summary()
        self.create_shortcut()

    def update_counter_xml(self):
        if self.counterDrop.currentText() != "Counter-Vartiou.xml":
            return

        xml_path = os.path.join(self.assets_dir, "gfx.xml")
        
        if not os.path.exists(xml_path):
            print(f"[Error] XML file not found: {xml_path}")
            return

        tree = ET.parse(xml_path)
        root = tree.getroot()

        for images in root.findall("images"):
            if images.attrib.get("file") == "res/counter/vartiou/counter-theme.png":
                for area in images.findall("area"):
                    if area.attrib.get("name") == "counter-theme":
                        images.set("file", "res/counter/vartiou/counter-theme-compact.png")
                        area.set("xywh", "*")
                        tree.write(xml_path, encoding="utf-8", xml_declaration=True)
                        print(f"[Success] Updated {xml_path} successfully")
                        return

        print("[Info] No matching <images> block found")

    def populate_dropdown(
        self,
        combo, 
        base_folder, 
        custom_folder=None, 
        file_ext=None, 
        include_subfolders=True, 
        file_filter=None, 
        exclude_names=None):

        combo.blockSignals(True)
        combo.clear()

        folders = [base_folder]
        if custom_folder and os.path.exists(custom_folder):
            if include_subfolders:
                for subfolder in sorted(os.listdir(custom_folder)):
                    full_path = os.path.join(custom_folder, subfolder)
                    if os.path.isdir(full_path):
                        folders.append(full_path)
            folders.append(custom_folder)

        for folder in folders:
            if not os.path.exists(folder):
                continue

            for file_name in sorted(os.listdir(folder)):
                full_path = os.path.join(folder, file_name)

                if not file_ext and os.path.isdir(full_path):
                    combo.addItem(file_name, full_path)
                    continue

                if file_ext and not file_name.lower().endswith(file_ext.lower()):
                    continue

                if exclude_names and file_name in exclude_names:
                    continue

                if file_filter and not file_filter(file_name):
                    continue

                display_name = file_name
                if custom_folder and folder.startswith(custom_folder):
                    display_name = file_name

                combo.addItem(display_name, full_path)

        combo.blockSignals(False)

    def update_login_drop(self):
        self.populate_dropdown(
        combo=self.loginDrop,
        base_folder=self.login_dir,
        custom_folder=self.custom_login,
        file_ext=".xml",
        file_filter=lambda f: not (
            f.startswith(("Counter-", "Cursors-", "Default")) or
            f in ["Round.xml", "Sharp.xml", "Archetype.xml"]
        ),)

    def mod_count(self,path: str)->int:
        if not os.path.isdir(path):
            return 0
        file_count = sum(1 for f in os.listdir(path) if os.path.isfile(os.path.join(path, f)))
        return file_count

    def update_counter_drop(self):
        self.populate_dropdown(
            combo=self.counterDrop,
            base_folder=self.counter_dir,
            custom_folder=self.custom_counter,
            file_ext=".xml",
            file_filter=lambda f: f.startswith("Counter-"),
        )

    def update_vartiou_drop(self):

        self.populate_dropdown(
            combo=self.customDrop,
            base_folder=self.custom_counter,
            file_ext=None, 
            include_subfolders=False
        ) 

    def update_cursor_drop(self):

        self.populate_dropdown(
            combo=self.cursorDrop,
            base_folder=self.cursorXmlDir,
            custom_folder=self.custom_cursor,
            file_ext=".xml", 
            include_subfolders=False,
            file_filter=lambda f: f.startswith("Cursors-"),
        )  

    def update_bubbles_drop(self):

        self.populate_dropdown(
            combo=self.speechDrop,
            base_folder=self.speech_dir,
            file_ext=".xml",
            include_subfolders=False,
            file_filter=lambda f: f.startswith("Default-"),
        )

    def refresh_config_dropdown(self):
        self.configDrop.blockSignals(True)
        self.configDrop.clear()

        for file in sorted(os.listdir(self.config_dir)):
            if not file.endswith(".json"):
                continue

            if file == "config_selector.json":
                continue

            full_path = os.path.join(self.config_dir, file)
            self.configDrop.addItem(file, full_path)
        # set current active
        active = self.get_active_config_path()

        index = self.configDrop.findData(active)
        if index >= 0:
            self.configDrop.setCurrentIndex(index)

        self.configDrop.blockSignals(False)

    def on_config_changed(self, index):
        path = self.configDrop.itemData(index)
        if not path:
            return
        self.set_active_config_path(path)
        self._load_config_from_path(path)
    
    def poke_start(self, *args):

        self.save_config()
        try:
            with open(self.configPath, "r") as f:
                config = json.load(f)
        except Exception:
            self.status_label_archetype.setText("Error: The Game Path is not set")
            return

        gamepath = config.get("paths", {}).get("game_path")

        if not gamepath:
            self.status_label_archetype.setText("Error: No game path set.")
            return

        if not os.path.isdir(gamepath):
            self.status_label_archetype.setText(
                f"Error: Game path does not exist:\n{gamepath}"
            )
            return


        script_name = "PokeMMO"
        if sys.platform.startswith("win"):
            script_path = os.path.join(gamepath, script_name + ".exe")
            base_cmd = [script_path]
        else:
            script_path = os.path.join(gamepath, script_name + ".sh")
            if not os.access(script_path, os.X_OK):
                os.chmod(script_path, 0o755)
            base_cmd = ["bash", script_path]

        if not os.path.exists(script_path):
            self.status_label_archetype.setText(
                f"Error: Launch script not found:\n{script_path}"
            )
            return

        mods_path = config.get("paths", {}).get("mods_path")
        if mods_path and os.path.isdir(mods_path):
            self.sync_user_mod_symlinks(gamepath, mods_path)
            PokeGen.update_poke(
                os.path.join(gamepath, "config", "main.properties"),
                mods_path,
            )

        selection = self.screenDrop.currentText()
        width = int(self.screenResW.toPlainText())
        height = int(self.screenResH.toPlainText())

        if selection == "Gamescope Fullscreen Wayland":
            gamescope_args = [
                "gamescope",
                "-w", str(width),
                "-h", str(height),
                "-W", str(width),
                "-H", str(height),
                "-f",
                "--expose-wayland"
            ]
            cmd = gamescope_args + base_cmd
        elif selection == "Gamescope Fullscreen X11":
            gamescope_args = [
                "gamescope",
                "-w", str(width),
                "-h", str(height),
                "-W", str(width),
                "-H", str(height),
                "-f",
            ]
            cmd = gamescope_args + base_cmd
        elif selection == "PokeMMO Default + VKCapture":
            cmd = ["obs-gamecapture"] + base_cmd
        
        else:
            cmd = base_cmd

        try:
            subprocess.run(cmd, cwd=gamepath, check=True)
            self.status_label_archetype.setText("PokeMMO launched successfully.")
        except subprocess.CalledProcessError as e:
            self.status_label_archetype.setText(
                f"Error running PokeMMO:\n{e}"
            )

    def update_icon_drop(self):

        self.populate_dropdown(
            combo=self.iconDrop,
            base_folder=self.shape_dir,
            file_ext=".xml", 
            include_subfolders=False,
            file_filter=lambda f: f.startswith("Sharp") or f.startswith("Round"),
        )  

    def update_login_preview(self):
        xml_path = self.loginDrop.currentData()
        if xml_path and os.path.exists(xml_path):
            self.loginPreview.set_xml_path(xml_path)

    def update_single_preview(self, preview_widget, base_path, xml_filename):
        import xml.etree.ElementTree as ET

        xml_path = os.path.join(base_path, xml_filename)
        if not os.path.exists(xml_path):
            print(f"XML file not found: {xml_path}")
            return

        try:
            tree = ET.parse(xml_path)
            root = tree.getroot()

            image_attr = root.find(".//images")
            if image_attr is None or "file" not in image_attr.attrib:
                print(f"No <images> tag or 'file' attribute found in {xml_filename}")
                return

            image_path = os.path.join(base_path, image_attr.attrib["file"])

            preview_widget.set_image(image_path, xml_path=xml_path)

        except ET.ParseError as e:
            print(f"Failed to parse XML {xml_filename}: {e}")

    def update_cursor_preview(self):
        current_index = self.cursorDrop.currentIndex()

        if current_index < 0 or current_index >= self.cursorDrop.count():
            if self.cursorDrop.count() > 0:
                current_index = 0
                self.cursorDrop.setCurrentIndex(0)
            else:
                print("cursorDrop has no items to select.")
                return

        selected_name = self.cursorDrop.itemText(current_index)

        if selected_name not in os.listdir(self.cursorXmlDir):
            self.update_single_preview(
                self.cursorPreview,
                self.custom_cursor,
                selected_name
            )            
        else:
            self.update_single_preview(
                self.cursorPreview,
                self.cursorXmlDir,
                selected_name
            )

    def update_preview_layers(self, preview_widget, base_path, image_list, color_map, combine_map=None):
        if not base_path or not os.path.exists(base_path):
            print(f"[MainWindow] Invalid base path: {base_path}")
            return

        layer_paths = [os.path.join(base_path, img) for img in image_list]
        preview_widget.layer_paths = [p if os.path.exists(p) else None for p in layer_paths]

        while len(preview_widget.layer_tints) < len(layer_paths):
            preview_widget.layer_tints.append(QColor(255, 255, 255, 255))

        for idx, color_btn in color_map.items():
            preview_widget.layer_tints[idx] = color_btn.color()

        if combine_map:
            for idx, (c1, c2) in combine_map.items():
                preview_widget.layer_tints[idx] = self.combine_colors(c1.color(), c2.color())

        preview_widget.update_preview()

    def update_counter_preview(self):
        text = self.counterDrop.currentText()

        layer = [
            "maincolorR.png",
            "sidecolorR.png",
            "MinMax.png",
            "Blank1.png", "Blank1.png", "Blank1.png", "Blank1.png",
            os.path.relpath(os.path.join(self.pokeballIcon, "Pokeball-Icon2.png"), self.previewimages),
            os.path.relpath(os.path.join(self.pokeballIcon, "Pokeball-Icon.png"), self.previewimages),
        ]

        layer_map = {
            "maincolor": 0,
            "sidecolor": 1,
            "minmax": 2,
            "icon2": 7,
            "icon": 8,
        }

        if "Icon" not in text:
            for name in ["icon", "icon2"]:
                idx = layer_map.get(name)
                if idx is not None and idx < len(layer):
                    layer[idx] = "Blank1.png"

        if "Left" in text:
            flipped_paths = self.flip_layers_y(layer, [0, 1])
            layer = [os.path.relpath(p, self.previewimages) for p in flipped_paths]

        self.update_preview_layers(
            self.counterPreview,
            self.previewimages,
            layer,
            {
                0: self.mainColor,
                1: self.subColor,
                2: self.minMaxButtonColor,
                6: self.minMaxButtonColor,
                7: self.ballColor,
                8: self.ballOutline,
            },
        )


        if "Vartiou" in text:
            layer = [*["Blank1.png"] * 3,os.path.relpath(os.path.join(self.custom_counter,self.customDrop.currentText(),"data/themes/default/res/counter-theme.png"), self.previewimages)]
            self.update_preview_layers(
            self.counterPreview,
            self.previewimages,
            layer,
            {
                0: self.mainColor,
                1: self.subColor,
                2: self.minMaxButtonColor,
                6: self.minMaxButtonColor,
                7: self.ballColor,
                8: self.ballOutline,
            },    
        )

    def flip_layers_y(self, image_paths: list, layers_to_flip: list = None):
        flipped_paths = []

        flipped_dir = os.path.join(tempfile.gettempdir(), "VMM", "Flipped")
        os.makedirs(flipped_dir, exist_ok=True)

        for idx, path in enumerate(image_paths):
            try:
                full_path = (
                    path
                    if os.path.isabs(path) or path.startswith(self.previewimages)
                    else os.path.join(self.previewimages, path)
                )

                if layers_to_flip and idx in layers_to_flip:
                    if full_path in self.flipped_cache:
                        flipped_path = self.flipped_cache[full_path]
                    else:
                        img = Image.open(full_path).convert("RGBA")
                        img = img.transpose(Image.FLIP_LEFT_RIGHT)

                        flipped_path = os.path.join(flipped_dir, os.path.basename(full_path))
                        img.save(flipped_path)
                        self.flipped_cache[full_path] = flipped_path
                        print(f"Flipped and cached: {flipped_path}")

                    full_path = flipped_path

                flipped_paths.append(full_path)

            except Exception as e:
                print(f"⚠ Failed to process image {path}: {e}")
                flipped_paths.append(path)

        return flipped_paths

    def update_window_preview(self):
        self.update_preview_layers(
            self.windowPreview,
            self.previewimages,
            ["ButtonColor.png", "IconColor.png", "OtherColor.png",
            "SubColor.png", "AccentColor.png", "MainColor.png"],
            {
                0: self.buttonColorW,
                1: self.iconColorW,
                3: self.subColorW,
                4: self.accentColorW,
                5: self.mainColorW,
            },
            combine_map={2: (self.buttonColorW, self.subColorW)}
        )

    def update_hp_preview(self):
        self.update_preview_layers(
            self.hpBar,
            self.previewimages,
            ["HPBarBaseLayer.png", "HPBarSubColor.png", "HPBarText.png",
            "HPBarMax.png", "HPBarMid.png", "HPBarMin.png", "XPBar.png"],
            {
                1: self.subColorW,
                3: self.hpHighW,
                4: self.hpMidW,
                5: self.hpLowW,
                6: self.xpColorW,
            },
            combine_map={0: (self.buttonColorW, self.subColorW)}
        )

    def setup_color_hooks_for_preview(self, color_map, target_preview, by_name=False):
        for key, button in color_map.items():
            if by_name:
                button.colorChanged.connect(lambda c, name=key: target_preview.set_layer_color(name, QColor(c)))
            else:
                button.colorChanged.connect(lambda c, idx=key: target_preview.set_layer_tint(idx, QColor(c)))

    def setup_color_hooks(self):
        self.setup_color_hooks_for_preview({
            "reshiram-color": self.reshiramColor,
            "zekrom-color": self.zekromColor,
            "reshiram-aura": self.reshiramAura,
            "zekrom-aura": self.zekromAura,
        }, self.loginPreview, by_name=True)

        self.setup_color_hooks_for_preview({
            0: self.mainColor,
            1: self.subColor,
            2: self.minMaxButtonColor,
            7: self.ballColor,
            8: self.ballOutline,
        }, self.counterPreview)

        self.setup_color_hooks_for_preview({
            0: self.buttonColorW,
            1: self.iconColorW,
            3: self.subColorW,
            4: self.accentColorW,
            5: self.mainColorW,
        }, self.windowPreview)

        self.setup_color_hooks_for_preview({
            1: self.subColorW,
            3: self.hpHighW,
            4: self.hpMidW,
            5: self.hpLowW,
            6: self.xpColorW,
        }, self.hpBar)

    def combine_colors(self, color1: QColor, color2: QColor) -> QColor:
        r = (color1.red() + color2.red()) // 2
        g = (color1.green() + color2.green()) // 2
        b = (color1.blue() + color2.blue()) // 2
        a = (color1.alpha() + color2.alpha()) // 2
        return QColor(r, g, b, a)

    def updateFontColor(self, color, label):
        label.setStyleSheet(f"color: {color.name()};")

    def get_config_base_folder(self, app_name="VexModMan"):
        return os.path.join(
            os.environ.get("XDG_CONFIG_HOME", os.path.expanduser("~/.config")),
            app_name
        )

    def handle_zip_import(self, update_func, label_widget):
        file_path, _ = QFileDialog.getOpenFileName(None, "Select a Theme ZIP", "", "Zip Files (*.zip);;All Files (*)")
        if not file_path:
            return
        new_theme = self.theme_manager.add_theme_from_zip(file_path,self.custom_login, parent_widget=self)
        if new_theme:
            update_func()
            label_widget.setText(f"✔ Imported: {os.path.basename(new_theme)}")
            label_widget.setStyleSheet("color: green; font-size: 9pt;")
        else:
            label_widget.setText("✖ Import failed. Please try again.")
            label_widget.setStyleSheet("color: red; font-size: 9pt;")

        QTimer.singleShot(30000, lambda: label_widget.setText(""))

    def handle_mod_import(self):
        file_path, _ = QFileDialog.getOpenFileName(None, "Select a Mod", "", "Zip Files (*.zip);;Mod Files (*.mod);;All Files (*)")
        if not file_path:
            return
        shutil.copy2(file_path, self.modsLocation)
        if hasattr(self, "mods_widget"):
            cfg = self.safe_load_json(self.get_active_config_path())
            pm = cfg.get("mods")
            self.mods_widget.load_mods(
                profile_mods=pm if isinstance(pm, dict) else None
            )

    def handle_basic_import(self, update_func,target_dir, label_widget):
        file_path, _ = QFileDialog.getOpenFileName(None, "Select a Theme ZIP", "", "Zip Files (*.zip);;All Files (*)")
        if not file_path:
            return
        new_theme = self.theme_manager.unzip_file(file_path,target_dir, parent_widget=self)
        if new_theme:
            update_func()
            label_widget.setText(f"✔ Imported: {os.path.basename(new_theme)}")
            label_widget.setStyleSheet("color: green; font-size: 9pt;")
        else:
            label_widget.setText("✖ Import failed. Please try again.")
            label_widget.setStyleSheet("color: red; font-size: 9pt;")

        QTimer.singleShot(30000, lambda: label_widget.setText(""))    

    def handle_login_browse(self):
        self.handle_zip_import(self.update_login_drop, self.label_2_status)

    def handle_vartiou_browse(self):
        self.handle_basic_import(self.update_vartiou_drop,self.custom_counter, self.status_label_custom_counter)      

    def update_archetype_summary(self):
        try:
            self._update_archetype_summary_label("")
        except Exception:
            archetype_status = '<span style="color:#ff3b3b;">Could not check status.</span>'
            self.status_label_archetype2.setText(
                f"<b>Pokemmo Location:</b> {self.get_current_path('game_path', self.configPath)}<br>"
                f"<b>Archetype Status:</b> {archetype_status}<br>"
                f"<b>Mod Folder:</b>{os.path.abspath(self.modsLocation)}<br>"
                f"<b>Mod Count:</b> {self.mod_count(self.modsLocation)}"
            )

    def check_remote_version(self, repo_url, destination):
        try:
            remote_refs = subprocess.run(
                ["git", "ls-remote", "--symref", repo_url, "HEAD"],
                check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
            )

            for line in remote_refs.stdout.splitlines():
                if line.startswith("ref:"):
                    default_branch = line.split()[1].split("/")[-1]
                    break
            else:
                default_branch = "main"

            remote_hash = subprocess.run(
                ["git", "ls-remote", repo_url, f"refs/heads/{default_branch}"],
                check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
            ).stdout.split()[0].strip()

            local_hash = None
            if os.path.exists(destination) and os.path.exists(os.path.join(destination, ".git")):
                local_hash_output = subprocess.run(
                    ["git", "-C", destination, "rev-parse", default_branch],
                    stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
                )
                if local_hash_output.returncode == 0:
                    local_hash = local_hash_output.stdout.strip()

            return local_hash == remote_hash

        except:
            return False

    def git_clone_or_pull(self, repo_url, destination, status_label):

        try:
            subprocess.run(["git", "--version"], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        except (subprocess.CalledProcessError, FileNotFoundError):
            status_label.setText("Git not found. Install Git and try again.")
            status_label.setStyleSheet("color: red; font-size: 18pt;")
            QTimer.singleShot(10000, lambda: status_label.setText(""))
            return

        try:
            remote_refs = subprocess.run(
                ["git", "ls-remote", "--symref", repo_url, "HEAD"],
                check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
            )

            default_branch = "main"
            for line in remote_refs.stdout.splitlines():
                if line.startswith("ref:"):
                    default_branch = line.split()[1].split("/")[-1]
                    break

            if os.path.exists(os.path.join(destination, ".git")):
                subprocess.run(["git", "-C", destination, "fetch", "--all"], check=True)
                subprocess.run(["git", "-C", destination, "reset", "--hard", f"origin/{default_branch}"], check=True)
                subprocess.run(["git", "-C", destination, "clean", "-fd"], check=True)
                msg = "Updated Successfully, Please run Complete Build Again"

            else:
                if os.path.exists(destination):
                    shutil.rmtree(destination)

                subprocess.run(["git", "clone", repo_url, destination], check=True)
                msg = "Downloaded"

            status_label.setText(f"Archetype {msg}")
            status_label.setStyleSheet("color: green; font-size: 18pt;")

        except subprocess.CalledProcessError as e:
            status_label.setText(f"Git operation failed: {e}")
            status_label.setStyleSheet("color: red; font-size: 18pt;")

        QTimer.singleShot(30000, lambda: status_label.setText(""))

    def create_button(self,parent, x, y, w, h, font_size, bold, name):
        btn = QtWidgets.QPushButton(parent)
        btn.setGeometry(QtCore.QRect(x, y, w, h))

        font = QtGui.QFont()
        font.setPointSize(font_size)
        font.setBold(bold)
        btn.setFont(font)

        if name:
            btn.setObjectName(name)

        return btn

    def create_frame(self, parent, x, y, w, h, name):
        frame = QtWidgets.QFrame(parent)
        frame.setGeometry(QtCore.QRect(x, y, w, h))
        frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        frame.setFrameShadow(QtWidgets.QFrame.Raised)

        if name:
            frame.setObjectName(name)

        return frame

    def downloadLatestArch(self):
        self.git_clone_or_pull("https://github.com/ssjshields/archetype", self.archetype_root, self.status_label_archetype)
        self.update_archetype_summary()

    def make_label(self, parent, text="", font_size=12, bold=False, geometry=None, align=None,color=None):
        label = QtWidgets.QLabel(parent)
        if geometry:
            label.setGeometry(QtCore.QRect(*geometry))
        font = QtGui.QFont()
        font.setPointSize(font_size)
        font.setBold(bold)
        label.setFont(font)
        if align:
            label.setAlignment(align)
        label.setText(text)
        if color is not None:
            label.setStyleSheet(f"color: {color};")
        return label

    def make_color_button(self,parent, name, x, y, width=48, height=23):
        btn = ColorButton(parent)
        btn.setGeometry(QtCore.QRect(x, y, width, height))
        btn.setObjectName(name)
        return btn

    def make_font_label(self, parent, geometry, size=8, bold=False):
        lbl = QtWidgets.QLabel(parent)
        lbl.setGeometry(QtCore.QRect(*geometry))
        font = QFont("Noto Sans", size)
        font.setBold(bold)
        lbl.setFont(font)
        return lbl
    #Save Section 
    #_______________________________#
    def col(self, widget):
        return widget.color().name()

    def safe_load_json(self, path):
        if not os.path.exists(path):
            return {}
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}

    def asset_paths(self):
        login = self.loginDrop.currentText()

        if login not in ("Unova.xml", "Allstars.xml"):
            folder = login.removesuffix(".xml")
            login_path = os.path.join("CustomThemes", folder)
        else:
            login_path = "backgrounds/"

        cursor_name = self.cursorDrop.currentText()
        cursor_path = (
            "CustomCursors"
            if cursor_name not in os.listdir(self.cursorXmlDir)
            else "cursors"
        )

        return login_path, cursor_path

    def build_config(self, existing_game_path=None, existing_mods_path=None):
        login_path, cursor_path = self.asset_paths()

        c = self.col

        return {
            "colors": {
                "main-color": c(self.mainColorW),
                "sub-color": c(self.subColorW),
                "button-color": c(self.buttonColorW),
                "accent-color": c(self.accentColorW),
                "font-main-color": c(self.fontMainW),
                "font-sub-color": c(self.fontSubW),
                "font-button-color": c(self.fontButtonW),
                "font-disabled-color": c(self.fontDisabledColorW),
                "hp-high-color": c(self.hpHighW),
                "hp-mid-color": c(self.hpMidW),
                "hp-low-color": c(self.hpLowW),
                "xp-color": c(self.xpColorW),
                "friendship-color": c(self.friendshipColorW),
                "icon-color": c(self.iconColorW),
                "water-background": c(self.waterbg),
                "water-warning": c(self.waterW),
                "berry-progress": c(self.berryProgress),
                "berry-progress-warning": c(self.berryWarning),
                "berry-progress-disabled": c(self.berryDisabled),
                "reshiram-color": c(self.reshiramColor),
                "reshiram-aura": c(self.reshiramAura),
                "zekrom-color": c(self.zekromColor),
                "zekrom-aura": c(self.zekromAura),
                "counter-ball-color": c(self.ballColor),
                "counter-ball-outline": c(self.ballOutline),
                "counter-min-max-button-color": c(self.minMaxButtonColor),
                "counter-main-color": c(self.mainColor),
                "counter-sub-color":c(self.subColor),
                "counter-font":c(self.fontColor),
                "counter-font-border":c(self.fontBorder)
            },

            "paths": {
                "login_screen": self.loginDrop.currentText(),
                "encounter_counter": self.counterDrop.currentText(),
                "custom_counter_current": self.customDrop.currentText(),
                "game_path": self.gamePath or existing_game_path,
                "mods_path": self.modsLocation or existing_mods_path,
            },

            "look": {
                "login_screen": os.path.join(login_path, self.loginDrop.currentText()),
                "arch_cursor": os.path.join(cursor_path, self.cursorDrop.currentText()),
                "arch_shape": os.path.join("shapes", self.iconDrop.currentText()),
                "speech_bubbles": os.path.join("speech-bubbles", self.speechDrop.currentText()),
            },

            "counter": {
                "encounter_counter": os.path.join("counters", self.counterDrop.currentText()),
            },

            "state": {
                "current_tab": self.tabWidget.currentIndex(),
                "loginDrop": self.loginDrop.currentIndex(),
                "counterDrop": self.counterDrop.currentIndex(),
                "customDrop": self.customDrop.currentIndex(),
                "bubblesDrop": self.speechDrop.currentIndex(),
                "icon_drop": self.iconDrop.currentIndex(),
                "cursor_drop": self.cursorDrop.currentIndex(),
                "screenDrop": self.screenDrop.currentIndex(),
            },

            "mods": (
                self.mods_widget.get_mod_profile_state()
                if hasattr(self, "mods_widget")
                else {"order": [], "disabled": []}
            ),
        }

    def save_config(self):
        path = self.get_active_config_path()

        existing = self.safe_load_json(path)

        config = self.build_config(
            existing.get("paths", {}).get("game_path"),
            existing.get("paths", {}).get("mods_path"),
        )

        with open(path, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=4)

        print(f"Config saved: {path}")

    def save_config_as(self):
        name, ok = QtWidgets.QInputDialog.getText(
            None,
            "Save Config",
            "Enter config name:"
        )

        if not ok or not name.strip():
            return

        name = name.strip()
        if not name.endswith(".json"):
            name += ".json"

        new_path = os.path.join(self.config_dir, name)

        existing = self.safe_load_json(self.get_active_config_path())

        config = self.build_config(
            existing.get("paths", {}).get("game_path"),
            existing.get("paths", {}).get("mods_path"),
        )

        with open(new_path, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=4)

        self.set_active_config_path(new_path)
        self.configPath = new_path

        print(f"Saved and activated config: {new_path}")

        if hasattr(self, "configDrop"):
            self.refresh_config_dropdown()

    #EndSaveSection
    #___________________________________________

    def get_Archstatus(self):
        repo_path = self.archetype_root
        if not os.path.isdir(repo_path):
            return '<span style="color: gray;">Path does not exist</span>'

        git_dir = os.path.join(repo_path, ".git")
        if not os.path.isdir(git_dir):
            return '<span style="color: orange;">Not a git repository</span>'

        try:
            subprocess.run(
                ["git", "fetch"],
                cwd=repo_path,
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )

            result = subprocess.run(
                ["git", "status", "-uno"],
                cwd=repo_path,
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )

            output = result.stdout.lower()
            if "up to date" in output or "ahead of" in output:
                return '<span style="color: green;">Up to date</span>'
            elif "behind" in output:
                return '<span style="color: red;">Updates available</span>'
            else:
                return '<span style="color: blue;">Status unclear</span>'
        except subprocess.CalledProcessError as e:
            print(f"Git command failed: {e}")
            return '<span style="color: red;">Git error</span>'
    #Load Section
    #_______________________________________
    def ensure_config_selector(self):
        if not os.path.exists(self.configSelector):
            with open(self.configSelector, "w", encoding="utf-8") as f:
                json.dump({
                    "active_config": self.defaultConfig
                }, f, indent=4)

    def get_active_config_path(self):
        self.ensure_config_selector()

        try:
            with open(self.configSelector, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception:
            return self.defaultConfig

        path = data.get("active_config", self.defaultConfig)

        if not os.path.exists(path):
            print(f"[Warn] Missing config: {path}, falling back to default")
            return self.defaultConfig

        return path

    def set_active_config_path(self, path):
        with open(self.configSelector, "w", encoding="utf-8") as f:
            json.dump({"active_config": path}, f, indent=4)

    def _load_config_from_path(self, path):
        if not os.path.exists(path):
            print(f"No config file found at {path}, using defaults.")
            return

        with open(path, "r", encoding="utf-8") as f:
            config = json.load(f)

        self.configPath = path

        color_map = {
            "main-color": "mainColorW",
            "sub-color": "subColorW",
            "button-color": "buttonColorW",
            "accent-color": "accentColorW",
            "hp-high-color": "hpHighW",
            "hp-mid-color": "hpMidW",
            "hp-low-color": "hpLowW",
            "xp-color": "xpColorW",
            "friendship-color": "friendshipColorW",
            "icon-color": "iconColorW",
            "counter-main-color": "mainColor",
            "counter-sub-color": "subColor",
            "counter-ball-color": "ballColor",
            "counter-ball-outline": "ballOutline",
            "counter-min-max-button-color": "minMaxButtonColor",
        }

        for json_key, widget_attr in color_map.items():
            widget = getattr(self, widget_attr, None)
            if widget:
                value = config["colors"].get(json_key, "#000000")
                color = QtGui.QColor(value)
                widget.setColor(color)
                if hasattr(widget, "colorChanged"):
                    widget.colorChanged.emit(color)
            else:
                print(f"[Warning] No widget found for '{widget_attr}'")

        state = config.get("state", {})

        if hasattr(self, "tabWidget") and isinstance(self.tabWidget, QtWidgets.QTabWidget):
            self.tabWidget.setCurrentIndex(state.get("current_tab", 0))

        combo_keys = [
            ("loginDrop", "loginDrop"),
            ("counterDrop", "counterDrop"),
            ("customDrop", "customDrop"),
            ("speechDrop", "speechDrop"),
            ("bubblesDrop", "bubblesDrop"),
            ("iconDrop", "icon_drop"),
            ("cursorDrop", "cursor_drop"),
            ("screenDrop", "screenDrop")
        ]

        for attr, state_key in combo_keys:
            combo = getattr(self, attr, None)
            if combo and isinstance(combo, QtWidgets.QComboBox):
                index = state.get(state_key, 0)
                if 0 <= index < combo.count():
                    combo.setCurrentIndex(index)
                else:
                    print(f"[Warning] Index {index} out of range for {attr}")

        self.modsLocation = self.get_current_path("mods_path", path)
        if hasattr(self, "mods_widget"):
            self.mods_widget.set_mods_folder(self.modsLocation, profile_mods=config.get("mods"))

    def load_last_config(self):
        path = self.get_active_config_path()

        self.configPath = path
        self._load_config_from_path(path)

        if hasattr(self, "configDrop"):
            self.refresh_config_dropdown()

            index = self.configDrop.findData(path)
            if index >= 0:
                self.configDrop.blockSignals(True)
                self.configDrop.setCurrentIndex(index)
                self.configDrop.blockSignals(False)

    def load_default_config(self):
        self._load_config_from_path(self.defaultConfig)

    def load_config(self):
        file_path, _ = QtWidgets.QFileDialog.getOpenFileName(
            None,
            "Select Config File",
            self.config_dir,
            "JSON Files (*.json);;All Files (*)"
        )

        if not file_path:
            print("No config file selected.")
            return

        if not os.path.exists(file_path):
            print(f"Selected file does not exist: {file_path}")
            return

        self._load_config_from_path(file_path)
        self.set_active_config_path(file_path)
        self.configPath = file_path

        if hasattr(self, "configDrop"):
            self.refresh_config_dropdown()

        print(f"Loaded and activated config: {file_path}")


    def get_current_path(self, path_type=None, config_file=None):
            config_file = config_file or getattr(self, "configPath", None)
            if not config_file or not os.path.isfile(config_file):
                print("Config file not found.")
                return None

            try:
                with open(config_file, "r", encoding="utf-8") as f:
                    config = json.load(f)
                paths = config.get("paths", {})
                return paths.get(path_type, None)
            except Exception as e:
                print(f"Failed to read config: {e}")
                return None

    def _update_archetype_summary_label(self, success_msg):
        up_to_date = self.check_remote_version(
            "https://github.com/ssjshields/archetype",
            self.archetype_root
        )
        archetype_status = '<span style="color:#28a745;">Up to date.</span>' if up_to_date else '<span style="color:#ff9800;">Update available!</span>'
        self.status_label_archetype2.setText(
            f"<b>Pokemmo Location:</b> {self.get_current_path('game_path', self.configPath)}<br>"
            f"<b>Archetype Status:</b> {archetype_status}<br>"
            f"<b>Mod Folder:</b>{os.path.abspath(self.modsLocation)}<br>"
            f"<b>Mod Count:</b> {self.mod_count(self.modsLocation)}"
        )

    def select_mods_path(self):
        dialog = QtWidgets.QFileDialog()
        dialog.setWindowTitle("Select Mods Location")
        dialog.setFileMode(QtWidgets.QFileDialog.Directory)
        dialog.setFilter(QDir.AllEntries | QDir.Hidden) 
        dialog.setOption(QtWidgets.QFileDialog.ShowDirsOnly, False)

        if dialog.exec_():
            selected_files = dialog.selectedFiles()
            if selected_files:
                self.modsLocation = selected_files[0]
                self.status_label_archetype.setText(f"Mods path set to {self.modsLocation}")
                self.status_label_archetype.setStyleSheet("color: green; font-size: 18pt;")

                cfg = self.safe_load_json(self.get_active_config_path())
                if hasattr(self, "mods_widget"):
                    self.mods_widget.set_mods_folder(
                        self.modsLocation, profile_mods=cfg.get("mods")
                    )
                self.save_config()
                self._update_archetype_summary_label("")

    def select_game_path(self):
        dialog = QtWidgets.QFileDialog()
        dialog.setWindowTitle("Select Pokemmo Installation Location")
        dialog.setFileMode(QtWidgets.QFileDialog.Directory)
        dialog.setFilter(QDir.AllEntries | QDir.Hidden) 
        dialog.setOption(QtWidgets.QFileDialog.ShowDirsOnly, False)

        if dialog.exec_():
            selected_files = dialog.selectedFiles()
            if selected_files:
                self.gamePath = selected_files[0]
                self.status_label_archetype.setText(f"Game path set to {self.gamePath}")
                self.status_label_archetype.setStyleSheet("color: green; font-size: 18pt;")

                self.save_config()
                self._update_archetype_summary_label("")

    def complete_build(self):
        self.save_config()
        colors = CompleteBuild(self.configPath, os.path.join(self.themeFolder, "CHOOSE_YOUR_COLORS.xml"), category="colors")
        counter = CompleteBuild(self.configPath, os.path.join(self.themeFolder, "CHOOSE_YOUR_COUNTER.xml"), category="counter")
        look = CompleteBuild(self.configPath, os.path.join(self.themeFolder, "CHOOSE_YOUR_LOOK.xml"), category="look")
        
        self.copy_files(self.customContent,self.themeFolder)

        print(self.counterDrop.currentText())
        colors.generate_xml()
        counter.generate_xml()
        look.generate_xml()
        if self.counterDrop.currentText() == "Counter-Vartiou.xml":
            self.copy_files(os.path.join(self.custom_counter,self.customDrop.currentText(),"data/themes/default/res"),os.path.join(self.assets_dir,"res/counter/vartiou"))
            self.update_counter_xml()

        self.gamePath = self.get_current_path("game_path",self.configPath)

        print(f"current path is: {self.gamePath}")
        if os.path.exists(os.path.join(self.gamePath,"data/mods/Archetype")):
            shutil.rmtree(os.path.join(self.gamePath,"data/mods/Archetype"))
        self.symlink_create(os.path.join(self.archetype_root,"archetype-theme"), os.path.join(self.gamePath,"data/mods/archetype-theme"))
        self.symlink_create(os.path.join(self.archetype_root,"archetype-rounded-icons"), os.path.join(self.gamePath,"data/mods/archetype-rounded-icons"))
        self.sync_user_mod_symlinks(self.gamePath, self.modsLocation)
        PokeGen.update_poke(os.path.join(self.gamePath,"config/main.properties"),self.modsLocation)
        self.status_label_archetype.setText(f"All Mods Installed Successfully!!")
        self.status_label_archetype.setStyleSheet("color: green; font-size: 18pt;")

    def copy_files(self,src_folder, dst_folder):
        if not os.path.exists(src_folder):
            print(f"Source folder does not exist: {src_folder}")
            return

        if not os.path.exists(dst_folder):
            os.makedirs(dst_folder)
        
        for item in os.listdir(src_folder):
            src_path = os.path.join(src_folder, item)
            dst_path = os.path.join(dst_folder, item)
            
            if os.path.isdir(src_path):
                shutil.copytree(src_path, dst_path, dirs_exist_ok=True)
            else:
                shutil.copy2(src_path, dst_path)
        
        print(f"Contents copied from '{src_folder}' to '{dst_folder}'")

    def symlink_create(self, src_folder, dst_folder):
        if not os.path.exists(src_folder):
            print(f"Source folder does not exist: {src_folder}")
            return

        if not os.path.exists(dst_folder):
            os.makedirs(dst_folder)

        for item in os.listdir(src_folder):
            src_path = os.path.join(src_folder, item)
            dst_path = os.path.join(dst_folder, item)

            try:
                if os.path.lexists(dst_path):
                    if os.path.islink(dst_path) or os.path.isfile(dst_path):
                        os.remove(dst_path)
                    elif os.path.isdir(dst_path):
                        shutil.rmtree(dst_path)

                abs_src = os.path.abspath(src_path)
                abs_dst = os.path.abspath(dst_path)

                if os.path.isdir(src_path):
                    print(f"Creating FOLDER symlink: {abs_src} -> {abs_dst}")
                    os.symlink(abs_src, abs_dst)
                else:
                    print(f"Creating FILE symlink: {abs_src} -> {abs_dst}")
                    os.symlink(abs_src, abs_dst)

            except Exception as e:
                print(f"Failed to symlink {src_path} -> {dst_path}: {e}")

        print(f"Symlinks created from '{src_folder}' to '{dst_folder}'")

    def sync_user_mod_symlinks(self, game_path, mods_folder):
        """Symlink only enabled mod files into the game; remove symlinks for disabled mods."""
        if not mods_folder or not os.path.isdir(mods_folder):
            print(f"sync_user_mod_symlinks: mods folder missing: {mods_folder}")
            return

        data_mods = os.path.join(game_path, "data", "mods")
        if not os.path.exists(data_mods):
            os.makedirs(data_mods)

        _, disabled = PokeGen.read_mod_lists(mods_folder)
        abs_mods = os.path.abspath(mods_folder)

        for name in os.listdir(mods_folder):
            if not name.lower().endswith(MOD_FILENAME_SUFFIXES):
                continue
            src_path = os.path.join(mods_folder, name)
            if not (os.path.isfile(src_path) or os.path.isdir(src_path)):
                continue

            dst_path = os.path.join(data_mods, name)

            if name in disabled:
                try:
                    if os.path.islink(dst_path):
                        os.remove(dst_path)
                except Exception as e:
                    print(f"Failed to remove disabled mod symlink {dst_path}: {e}")
                continue

            try:
                if os.path.lexists(dst_path):
                    if os.path.islink(dst_path):
                        cur = os.readlink(dst_path)
                        if os.path.abspath(cur) == os.path.abspath(src_path):
                            continue
                        os.remove(dst_path)
                    elif os.path.isdir(dst_path):
                        shutil.rmtree(dst_path)
                    else:
                        os.remove(dst_path)

                abs_src = os.path.abspath(src_path)
                abs_dst = os.path.abspath(dst_path)
                try:
                    os.symlink(
                        abs_src,
                        abs_dst,
                        target_is_directory=os.path.isdir(src_path),
                    )
                except TypeError:
                    os.symlink(abs_src, abs_dst)
                print(f"Creating symlink: {abs_src} -> {abs_dst}")
            except Exception as e:
                print(f"Failed to symlink mod {src_path} -> {dst_path}: {e}")

        try:
            for name in os.listdir(data_mods):
                dst_path = os.path.join(data_mods, name)
                if not os.path.islink(dst_path):
                    continue
                target = os.path.abspath(os.path.join(os.path.dirname(dst_path), os.readlink(dst_path)))
                if not target.startswith(abs_mods + os.sep) and target != abs_mods:
                    continue
                base = os.path.basename(target)
                if not os.path.exists(target) or base not in os.listdir(mods_folder):
                    os.remove(dst_path)
                    print(f"Removed stale mod symlink: {dst_path}")
        except Exception as e:
            print(f"Stale symlink cleanup skipped: {e}")

    def handle_cursor_browse(self):
        file_path, _ = QtWidgets.QFileDialog.getOpenFileName(
            None,
            "Select New Cursor",
            os.path.dirname(self.configPath) if hasattr(self, "configPath") else "",
            "PNG Files (*.png);;All Files (*)"
        )

        if not file_path:
            return None

        image = QtGui.QImage(file_path)
        if image.isNull():
            QtWidgets.QMessageBox.warning(None, "Invalid Image", "The selected file is not a valid image.")
            return None


        base_name = os.path.splitext(os.path.basename(file_path))[0]
        cursor_name = base_name

        counter = 1
        target_png = os.path.join(self.custom_cursor, f"Cursors-{cursor_name}.png")
        target_xml = os.path.join(self.custom_cursor, f"Cursors-{cursor_name}.xml")
        extra_png = f"Cursors-{cursor_name}.png"

        while os.path.exists(target_png) or os.path.exists(target_xml):
            cursor_name = f"{base_name}_{counter}"
            target_png = os.path.join(self.custom_cursor, f"Cursors-{cursor_name}.png")
            target_xml = os.path.join(self.custom_cursor, f"Cursors-{cursor_name}.xml")
            counter += 1


        os.makedirs(os.path.dirname(target_png), exist_ok=True)
        shutil.copy(file_path, target_png)

        source_xml = os.path.join(self.cursorXmlDir, "Cursors-Black.xml")
        if os.path.exists(source_xml):
            shutil.copy(source_xml, target_xml)

        if os.path.exists(target_xml):
            try:
                with open(target_xml, "r", encoding="utf-8") as f:
                    xml_data = f.read()

                import re
                xml_data = re.sub(
                    r'(<images[^>]*file=")([^"]*)(")',
                    r'\1' + extra_png.replace("\\", "/") + r'\3',
                    xml_data
                )

                with open(target_xml, "w", encoding="utf-8") as f:
                    f.write(xml_data)

            except Exception as e:
                print("Error updating XML:", e)
        self.update_cursor_drop()
        return target_png

    def edit_cursor_data(self):
        cursor_name = self.cursorDrop.currentText()

        if not cursor_name.lower().endswith(".xml"):
            cursor_name = f"{cursor_name}.xml"

        selected_name = self.cursorDrop.itemText(self.cursorDrop.currentIndex())
        if selected_name not in os.listdir(self.cursorXmlDir):
            xml_path = os.path.join(self.custom_cursor, cursor_name)
        else:
            xml_path = os.path.join(self.cursorXmlDir, cursor_name)
            
        dialog = CursorEdit(
            xml_path,
            on_save=self.update_cursor_preview
        )

        dialog.exec_()


    def create_shortcut(self, parent=None):
        base_path = self.get_base_path()

        exec_path = Path(os.environ.get("APPIMAGE", sys.argv[0])).resolve()

        local_apps_dir = Path.home() / ".local/share/applications"
        local_apps_dir.mkdir(parents=True, exist_ok=True)
        desktop_file = local_apps_dir / "VexModMan.desktop"

        desktop_entry = (
            "[Desktop Entry]\n"
            "Type=Application\n"
            "Name=VexModMan\n"
            "Comment=Pokemmo Mod Manager\n"
            f"Exec={exec_path}\n"
            f"Icon={base_path}/VMM.png\n"
            "Terminal=false\n"
            "Categories=Game;\n"
        )

        needs_update = False
        if desktop_file.exists():
            content = desktop_file.read_text()
            if f"Exec={exec_path}" not in content or f"Icon={base_path}/VMM.png" not in content:
                needs_update = True
        else:
            needs_update = True

        if not needs_update:
            return

        try:
            with open(self.configSelector, "r", encoding="utf-8") as f:
                config_data = json.load(f)
        except Exception:
            config_data = {}

        if config_data.get("ignored", False):
            return

        dialog = QtWidgets.QDialog(parent)
        dialog.setWindowTitle("Create Desktop Shortcut")
        dialog.setMinimumWidth(350)
        layout = QtWidgets.QVBoxLayout(dialog)

        label = QtWidgets.QLabel("Would you like to create shortcuts for VexModMan?\n(This will create a desktop entry and a menu shortcut.)")
        layout.addWidget(label)

        checkbox = QtWidgets.QCheckBox("Ignore (don't ask again)")
        layout.addWidget(checkbox)

        button_box = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Yes | QtWidgets.QDialogButtonBox.No)
        layout.addWidget(button_box)

        button_box.accepted.connect(dialog.accept)
        button_box.rejected.connect(dialog.reject)

        reply = dialog.exec_()

        if checkbox.isChecked():
            try:
                with open(self.configSelector, "r", encoding="utf-8") as f:
                    config_data = json.load(f)
            except Exception:
                config_data = {}
            config_data["ignored"] = True
            with open(self.configSelector, "w", encoding="utf-8") as f:
                json.dump(config_data, f, indent=4)

        if reply != QtWidgets.QDialog.Accepted:
            return

        desktop_file.write_text(desktop_entry)
        desktop_file.chmod(0o755)

        os.system(f'gio set "{desktop_file}" metadata::trusted true')
        os.system("update-desktop-database ~/.local/share/applications 2>/dev/null")

        desktop_dir = Path.home() / "Desktop"
        if desktop_dir.exists():
            desktop_file_desktop = desktop_dir / "VexModMan.desktop"

            desktop_needs_update = False
            if desktop_file_desktop.exists():
                content = desktop_file_desktop.read_text()
                if f"Exec={exec_path}" not in content or f"Icon={base_path}/VMM.png" not in content:
                    desktop_needs_update = True
            else:
                desktop_needs_update = True

            if desktop_needs_update:
                desktop_file_desktop.write_text(desktop_entry)
                desktop_file_desktop.chmod(0o755)
                os.system(f'gio set "{desktop_file_desktop}" metadata::trusted true')


    def get_base_path(self):
        appimage_path = os.environ.get("APPIMAGE")
        if appimage_path:
            return os.path.dirname(os.path.abspath(appimage_path))       
        if getattr(sys, "frozen", False) and sys.executable:
            return os.path.dirname(os.path.abspath(sys.executable))        
        if '__file__' in globals():
            return os.path.dirname(os.path.abspath(__file__))        
        return os.getcwd()

    def resource_path(self, relative_path):
        try:
            base_path = sys._MEIPASS
        except AttributeError:
            base_path = os.path.abspath(".")

        return os.path.join(base_path, relative_path)

    def ensure_archetype(self, parent=None):
        if os.path.exists(self.archetype_root):
            return True

        choice = QMessageBox.question(
            parent,
            "Archetype Missing",
            "Archetype is required in order to use Vextryyn's Mod Manager.\n"
            "There are 2 ways to do this:\n\n"
            "Option 1: Go to https://github.com/ssjshields/archetype download and extract into the VMM folder\n\n"
            "Option 2: press Yes and this will download all the files for you",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.Yes
        )

        if choice == QMessageBox.No:
            return False 

        status_win = QtWidgets.QWidget(parent)
        status_win.setWindowTitle("Installing Archetype")
        status_win.setFixedSize(300, 100)
        from PyQt5.QtWidgets import QVBoxLayout, QLabel
        layout = QVBoxLayout()
        status_label = QLabel("Downloading Archetype...")
        layout.addWidget(status_label)
        status_win.setLayout(layout)
        status_win.show()
        QApplication.processEvents()  

        repo_url = "https://github.com/ssjshields/archetype"
        try:
            if os.path.exists(self.archetype_root):
                subprocess.run(["git", "-C", self.archetype_root, "pull"], check=True)
            else:
                subprocess.run(["git", "clone", repo_url, self.archetype_root], check=True)
        except subprocess.CalledProcessError as e:
            QMessageBox.critical(parent, "Error", f"Failed to download Archetype:\n{e}")
            status_win.close()
            return False

        status_label.setText("Download complete!")
        QApplication.processEvents()
        status_win.close()
        return True


    def show_about_window(self):
        dlg = AboutWindow()
        dlg.exec_() 

    def _setup_login_tab(self):
        self.LoginScreen = QtWidgets.QWidget()
        self.LoginScreen.setObjectName("LoginScreen")

        self.unovaLoginOptions = self.create_frame(self.LoginScreen, 5, 415, 340, 261, "unovaLoginOptions")
        self.label_8 = self.make_label(self.unovaLoginOptions, "label_8", 12, False, (20, 65, 181, 201), None)
        self.label_9 = self.make_label(self.unovaLoginOptions, "label_9", 16, True, (15, 15, 311, 41), None)

        for attr, name, y in [
            ("zekromColor", "zekrom-color", 175),
            ("reshiramColor", "reshiram-color", 90),
            ("zekromAura", "zekrom-aura", 220),
            ("reshiramAura", "reshiram-aura", 130),
        ]:
            setattr(self, attr, self.make_color_button(self.unovaLoginOptions, name, 150, y))

        self.addOwnLogin = self.create_frame(self.LoginScreen, 5, 15, 340, 66, "addOwnLogin")
        self.label_2 = self.make_label(self.addOwnLogin, "label_2", 12, True, (5, 15, 241, 30), None)
        self.label_2_status = self.make_label(self.LoginScreen, "", 9, True, (386, 20, 685, 117), None, "green")
        self.loginBrowse = self.create_button(self.addOwnLogin, 235, 20, 80, 25, 10, False, "loginBrowse")
        self.loginBrowse.clicked.connect(self.handle_login_browse)

        self.chooseLogin = self.create_frame(self.LoginScreen, 5, 90, 340, 320, "chooseLogin")
        self.loginDrop = QtWidgets.QComboBox(self.chooseLogin)
        self.loginDrop.setGeometry(QtCore.QRect(15, 35, 301, 25))
        self.loginDrop.setObjectName("loginDrop")
        self.label = self.make_label(self.chooseLogin, "label", 16, True, (60, -10, 226, 51), None)

        self.loginPreviewFrame = self.create_frame(self.LoginScreen, 360, 170, 731, 506, "loginPreviewFrame")
        default_xml = os.path.join(self.assets_dir, "backgrounds/Allstars.xml")
        self.loginPreview = XmlAnimationPreview(default_xml, parent=self.loginPreviewFrame)
        self.loginPreview.setGeometry(QtCore.QRect(5, 5, 721, 496))
        self.loginPreview.setObjectName("loginPreview")

        self.tabWidget.addTab(self.LoginScreen, "")

    def _setup_counter_tab(self):
        self.EncounterCounter = QtWidgets.QWidget()
        self.EncounterCounter.setObjectName("EncounterCounter")

        self.counterColorFrame = self.create_frame(self.EncounterCounter, 15, 105, 306, 391, "counterColorFrame")
        self.label_6 = self.make_label(self.counterColorFrame, "label_6", 16, True, (15, 15, 311, 41), None)
        self.label_7 = self.make_label(self.counterColorFrame, "label_7", 12, False, (20, 35, 181, 361), None)

        for attr, name, y in [
            ("ballColor", "counter-ball-color", 75),
            ("mainColor", "counter-main-color", 205),
            ("fontColor", "counter-font", 290),
            ("minMaxButtonColor", "counter-min-max-button-color", 160),
            ("ballOutline", "ballOutline", 115),
            ("subColor", "counter-sub-color", 250),
            ("fontBorder", "counter-font-border", 335),
        ]:
            setattr(self, attr, self.make_color_button(self.counterColorFrame, name, 220, y))

        self.counterSelectorFrame = self.create_frame(self.EncounterCounter, 15, 20, 531, 80, "counterSelectorFrame")
        self.counterDrop = QtWidgets.QComboBox(self.counterSelectorFrame)
        self.counterDrop.setGeometry(QtCore.QRect(225, 25, 301, 25))
        self.counterDrop.setObjectName("counterDrop")
        self.counterDrop.setCurrentIndex(1)
        self.label_5 = self.make_label(self.counterSelectorFrame, "label_5", 16, True, (5, 5, 211, 61), None)

        self.counterPreviewFrame = self.create_frame(self.EncounterCounter, 345, 125, 731, 506, "counterPreviewFrame")
        default_xml = os.path.join(self.assets_dir, "Counter-Right.xml")
        self.counterPreview = CounterPreview(parent=self.counterPreviewFrame)
        self.counterPreview.setGeometry(QtCore.QRect(5, 5, 721, 496))
        self.counterPreview.setObjectName("counterPreview")

        self.counterText = self.make_font_label(self.counterPreviewFrame, (300, 170, 211, 200), 14, True)
        self.counterText.setObjectName("counterText")
        self.fontColor.colorChanged.connect(lambda c, lbl=self.counterText: self.updateFontColor(c, lbl))

        self.addOwnVaritou = self.create_frame(self.EncounterCounter, 565, 20, 456, 86, "addOwnVaritou")
        self.label_3 = self.make_label(self.addOwnVaritou, "label_3", 12, True, (25, 0, 211, 30), None)
        self.varitouBrowse = self.create_button(self.addOwnVaritou, 235, 5, 80, 25, 9, False, "varitouBrowse")
        self.varitouBrowse.clicked.connect(self.handle_vartiou_browse)
        self.label_16 = self.make_label(self.addOwnVaritou, "label_16", 9, False, (25, 35, 386, 17), None)
        self.customDrop = QtWidgets.QComboBox(self.addOwnVaritou)
        self.customDrop.setGeometry(QtCore.QRect(150, 55, 301, 25))
        self.customDrop.setObjectName("customDrop")
        self.label_18 = self.make_label(self.addOwnVaritou, "label_18", 12, True, (5, 50, 141, 30), None)

        self.tabWidget.addTab(self.EncounterCounter, "")

    def _setup_window_tab(self):
        self.WindowColors = QtWidgets.QWidget()
        self.WindowColors.setObjectName("WindowColors")

        self.windowPreviewFrame = self.create_frame(self.WindowColors, 15, 25, 829, 653, "windowPreviewFrame")
        self.windowPreview = CounterPreview(parent=self.windowPreviewFrame)
        self.windowPreview.setGeometry(QtCore.QRect(5, 5, 805, 577))
        self.windowPreview.setObjectName("windowPreview")

        self.hpBar = CounterPreview(parent=self.windowPreviewFrame)
        self.hpBar.setGeometry(QtCore.QRect(7, 592, 297, 63))
        self.hpBar.setObjectName("hpBar")
        self.BerryPreview = QtWidgets.QWidget(self.windowPreviewFrame)
        self.BerryPreview.setGeometry(QtCore.QRect(347, 592, 307, 57))
        self.BerryPreview.setObjectName("BerryPreview")

        self.MainWindowFrame = self.create_frame(self.WindowColors, 868, 10, 233, 656, "MainWindowFrame")

        for attr, geo, bold in [
            ("label_4", (8, 319, 146, 137), False),
            ("label_10", (8, 56, 81, 121), False),
            ("label_11", (8, 171, 101, 146), False),
            ("label_12", (8, 515, 143, 139), False),
            ("label_13", (46, 1, 155, 61), True),
            ("label_14", (-2, 464, 230, 61), True),
        ]:
            setattr(self, attr, self.make_label(self.MainWindowFrame, attr, 16, bold, geo, None))

        for attr, name, y in [
            ("accentColorW", "accent-color", 152),
            ("subColorW", "sub-color", 94),
            ("mainColorW", "main-color", 66),
            ("fontButtonW", "font-button-color", 378),
            ("buttonColorW", "button-color", 124),
            ("fontSubW", "font-sub-color", 348),
            ("fontDisabledColorW", "font-disabled-color", 406),
            ("xpColorW", "xp-color", 264),
            ("friendshipColorW", "friendship-color", 292),
            ("fontMainW", "font-main-color", 320),
            ("hpHighW", "hp-high-color", 179),
            ("hpLowW", "hp-low-color", 234),
            ("hpMidW", "hp-mid-color", 206),
            ("waterW", "water-warning", 546),
            ("waterbg", "water-background", 518),
            ("berryProgress", "berry-progress", 576),
            ("berryWarning", "berry-progress-warning", 604),
            ("berryDisabled", "berry-progress-disabled", 632),
            ("iconColorW", "icon-color", 434),
        ]:
            setattr(self, attr, self.make_color_button(self.MainWindowFrame, name, 158, y))

        for attr, geo, size, bold in [
            ("windowTextFontMain", (40, -50, 211, 200), 8, True),
            ("windowTextFontMain2", (47, -27, 211, 200), 7, False),
            ("windowTextFontSub", (232, 147, 717, 61), 8, False),
            ("windowTextFontSub2", (110, 115, 717, 61), 8, False),
            ("windowTextFontMinIV", (428, 147, 61, 61), 8, False),
            ("windowTextFontMaxIV", (317, 147, 61, 61), 8, False),
            ("windowTextFontButton1", (160, 45, 717, 61), 8, False),
            ("windowTextFontButton2", (100, 80, 717, 61), 8, False),
            ("windowTextFontButton3", (130, 147, 717, 61), 8, False),
            ("windowTextFontButton4", (225, 493, 717, 61), 8, False),
            ("windowTextFontDisabled1", (602, 80, 61, 61), 8, False),
            ("windowTextFontDisabled2", (160, 493, 100, 61), 8, False),
        ]:
            setattr(self, attr, self.make_font_label(self.windowPreviewFrame, geo, size, bold))
            label = getattr(self, attr)
            label.setObjectName(attr)

        self.windowTextFontMinIV.setStyleSheet("color: #f46263;")
        self.windowTextFontMaxIV.setStyleSheet("color: #6eb66e;")

        for btn, labels in [
            (self.fontMainW, [self.windowTextFontMain, self.windowTextFontMain2]),
            (self.fontSubW, [self.windowTextFontSub, self.windowTextFontSub2]),
            (self.fontButtonW, [self.windowTextFontButton1, self.windowTextFontButton2,
                                self.windowTextFontButton3, self.windowTextFontButton4]),
            (self.fontDisabledColorW, [self.windowTextFontDisabled1, self.windowTextFontDisabled2]),
        ]:
            for lbl in labels:
                btn.colorChanged.connect(lambda c, lbl=lbl: self.updateFontColor(c, lbl))

        for widget in [self.label_12, self.label_11, self.label_4, self.label_10, self.accentColorW,
            self.subColorW, self.mainColorW, self.fontButtonW, self.buttonColorW, self.fontSubW,
            self.fontDisabledColorW, self.xpColorW, self.friendshipColorW, self.fontMainW,
            self.hpHighW, self.hpLowW, self.hpMidW, self.label_13, self.waterW, self.label_14,
            self.waterbg, self.berryProgress, self.berryWarning]:
            widget.raise_()

        self.tabWidget.addTab(self.WindowColors, "")

    def _setup_other_tab(self):
        self.OtherScreen = QtWidgets.QWidget()
        self.OtherScreen.setObjectName("OtherScreen")

        self.cursoFrame = self.create_frame(self.OtherScreen, 10, 30, 561, 141, "cursoFrame")
        self.cursorDrop = QtWidgets.QComboBox(self.cursoFrame)
        self.cursorDrop.setGeometry(QtCore.QRect(225, 25, 301, 25))
        self.cursorDrop.setObjectName("cursorDrop")
        self.label_15 = self.make_label(self.cursoFrame, "label_15", 16, True, (5, 5, 211, 61), None)
        self.cursorBrowse = self.create_button(self.cursoFrame, 435, 70, 80, 25, 9, False, "cursorBrowse")
        self.label_17 = self.make_label(self.cursoFrame, "label_17", 12, True, (195, 65, 241, 30), None)
        self.label_30 = self.make_label(self.cursoFrame, "label_30", 12, True, (195, 96, 241, 30), None)
        self.cursorEditButton = self.create_button(self.cursoFrame, 435, 101, 80, 25, 9, False, "cursorEdit")
        self.cursorPreviewFrame = self.create_frame(self.OtherScreen, 680, 10, 321, 166, "cursorPreviewFrame")

        self.cursorPreview = OtherWidget(self.cursorPreviewFrame)
        self.cursorPreview.setGeometry(QtCore.QRect(5, 5, 310, 155))
        self.cursorPreview.setObjectName("cursorPreview")

        self.iconFrame = self.create_frame(self.OtherScreen, 10, 225, 561, 80, "iconFrame")
        self.iconDrop = QtWidgets.QComboBox(self.iconFrame)
        self.iconDrop.setGeometry(QtCore.QRect(225, 25, 301, 25))
        self.iconDrop.setObjectName("iconDrop")
        self.iconDrop.addItem("")
        self.iconDrop.addItem("")
        self.label_20 = self.make_label(self.iconFrame, "label_20", 16, True, (5, 5, 211, 61), None)

        self.speechBubblesFrame = self.create_frame(self.OtherScreen, 10, 385, 561, 121, "speechBubblesFrame")
        self.speechDrop = QtWidgets.QComboBox(self.speechBubblesFrame)
        self.speechDrop.setGeometry(QtCore.QRect(225, 25, 301, 25))
        self.speechDrop.setObjectName("speechDrop")
        self.label_23 = self.make_label(self.speechBubblesFrame, "label_23", 16, True, (5, 5, 211, 61), None)
        self.speechBrowse = self.create_button(self.speechBubblesFrame, 435, 70, 80, 25, 9, False, "speechBrowse")
        self.label_24 = self.make_label(self.speechBubblesFrame, "label_24", 12, True, (195, 65, 241, 30), None)
        self.speechBubblePreviewFrame = self.create_frame(self.OtherScreen, 680, 365, 321, 166, "speechBubblePreviewFrame")

        self.speechBubblePreview = QtWidgets.QWidget(self.speechBubblePreviewFrame)
        self.speechBubblePreview.setGeometry(QtCore.QRect(5, 5, 310, 155))
        self.speechBubblePreview.setObjectName("speechBubblePreview")

        self.tabWidget.addTab(self.OtherScreen, "")

    def _setup_archetype_tab(self):
        self.Archetype = QtWidgets.QWidget()
        self.Archetype.setObjectName("Archetype")

        self.GetArchtype = self.create_frame(self.Archetype, 12, 19, 1089, 657, "GetArchtype")
        self.label_25 = self.make_label(self.GetArchtype, "label_25", 16, True, (5, 5, 236, 61), None)
        self.downloadArch = self.create_button(self.GetArchtype, 245, 15, 281, 46, 16, True, "downloadArch")
        self.label_27 = self.make_label(self.GetArchtype, "label_27", 16, True, (5, 134, 210, 61), None)
        self.setModFolder = self.create_button(self.GetArchtype, 245, 144, 281, 46, 16, True, "setModFolder")
        self.labelBrowse = self.make_label(self.GetArchtype, "Set Game Path", 16, True, (5, 70, 210, 61), None)
        self.setGamePath = self.create_button(self.GetArchtype, 245, 80, 281, 46, 16, True, "setGamePath")
        self.completeMod = self.create_button(self.GetArchtype, 595, 70, 281, 46, 16, True, "completeMod")
        self.playPokemmo = self.create_button(self.GetArchtype, 806, 606, 280, 46, 16, True, "playPokemmo")
        self.label_28 = self.make_label(self.GetArchtype, "label_28", 16, True, (590, 0, 306, 61), None)

        self.tabWidget.addTab(self.Archetype, "")

    def _setup_mods_tab(self):
        self.Mods = QtWidgets.QWidget()
        self.Mods.setObjectName("Mods")

        self.modOrderFrame = self.create_frame(self.Mods, 12, 136, 1087, 543, "modOrderFrame")
        self.modButtonsFrame = self.create_frame(self.Mods, 238, 20, 585, 97, "modButtonsFrame")
        self.modButtonLabel = self.make_label(self.modButtonsFrame, "modButtonLabel", 12, True, (260, 12, 79, 30), None)

        self.mods_widget = ModListWidget(
            mods_folder=self.modsLocation,
            parent=self.modOrderFrame,
            on_order_saved=self.save_config,
        )
        layout = QtWidgets.QVBoxLayout(self.modOrderFrame)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.mods_widget)

        self.tabWidget.addTab(self.Mods, "")

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "Vextryyn's Mod Manager"))

        for widget, text in [
            (self.label_8, "reshiram color\n\nreshiram aura\n\nzekrom color\n\nzekrom aura"),
            (self.label_9, "Unova Login Screen Options"),
            (self.label_2, "Add Your Own Login Screen"),
            (self.loginBrowse, "Browse..."),
            (self.label, "Choose Login Screen"),
            (self.label_6, "Encounter Counter Colors"),
            (self.label_7, " ball color\n\n ball outline\n\n min max button color\n\n main color\n\n sub color\n\n font\n\n font border"),
            (self.label_5, "Encounter Counter"),
            (self.label_3, " Add Vartiou here"),
            (self.varitouBrowse, "Browse..."),
            (self.label_16, "This will do the work getting what is needed, just choose the zip file"),
            (self.label_18, "Choose Custom"),
            (self.label_11, "hp high \nhp mid\nhp low\nxp\nfriendship"),
            (self.label_10, "main\nsub\nbutton\naccent"),
            (self.label_4, "font main\nfont sub\nfont button\nfont disabled\nIcon"),
            (self.label_13, "Main Window"),
            (self.counterText, "Pokemon        1\n\n\nPokemon        2\n\n\nPokemon        3"),
            (self.windowTextFontMain, "           Global Trade Link"),
            (self.windowTextFontMain2, "Pokemon Listings"),
            (self.windowTextFontSub, " Modest     20               11     16     23               $5,000                   Just now            28 days                      Buy"),
            (self.windowTextFontSub2, "Pokemon\t           Nature\t\tIVs\t\t            Price\t     Start Date          End Date\tBuy"),
            (self.windowTextFontMinIV, "0"),
            (self.windowTextFontMaxIV, "31"),
            (self.windowTextFontButton1, "Item Market       Item Listings       Your Listings       Create Listing       Trade Log"),
            (self.windowTextFontButton2, "Select Template\t\t\t\t\t\t\t          Advanced Search             ↻               Newest"),
            (self.windowTextFontButton3, "Lv. 36 Evee"),
            (self.windowTextFontButton4, "2         3         4         5         6         7         8         9        10       11       12      13       14       >>"),
            (self.windowTextFontDisabled1, "☒"),
            (self.windowTextFontDisabled2, "<<      1"),
            (self.label_14, "Berry Watering Colors"),
            (self.label_12, "waterBG\nwaterwarning\nberryprogress\nberrywarning\nberrydisabled"),
            (self.label_15, "Cursor Type"),
            (self.cursorBrowse, "Browse..."),
            (self.cursorEditButton, "Edit"),
            (self.label_17, "Add Custom Cursor"),
            (self.label_30, "Edit Cursor Data"),
            (self.label_20, "Icon Type"),
            (self.label_23, "Speech Bubbles"),
            (self.speechBrowse, "Browse..."),
            (self.label_24, "Add Custom Speech Bubbles"),
            (self.label_25, "Get/Update Archetype"),
            (self.label_27, "Set Mods Folder"),
            (self.label_29, "Width"),
            (self.label_31, "Height"),
            (self.configLabel, "Config Selection"),
            (self.downloadArch, "Download"),
            (self.setModFolder, "Browse..."),
            (self.playPokemmo, "Play Pokemmo"),
            (self.modButtonLabel, "Mod List"),
            (self.setGamePath, "Browse..."),
            (self.completeMod, "Complete"),
            (self.label_28, "Finish and add to Pokemmo"),
        ]:
            widget.setText(_translate("MainWindow", text))

        for tab, name in [
            (self.LoginScreen, "Login Screen"),
            (self.EncounterCounter, "Encounter Counter"),
            (self.WindowColors, "Window Colors"),
            (self.OtherScreen, "Other"),
            (self.Archetype, "Archetype"),
            (self.Mods, "Mods"),
        ]:
            self.tabWidget.setTabText(self.tabWidget.indexOf(tab), _translate("MainWindow", name))

        for widget, text in [
            (self.menuFile, "File"),
            (self.menuHelp, "Help"),
            (self.actionSave, "Save"),
            (self.actionExit, "Exit"),
            (self.actionLoad, "Load"),
            (self.actionSaveAs, "Save As..."),
            (self.actionLoadDefault, "Load Defaults"),
            (self.actionAbout, "About"),
        ]:
            widget.setTitle(_translate("MainWindow", text)) if hasattr(widget, 'setTitle') else widget.setText(_translate("MainWindow", text))



if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    system_theme(app)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())
