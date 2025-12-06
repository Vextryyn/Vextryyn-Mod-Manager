import os
import sys
import subprocess
import shutil
import json
import zipfile
import tempfile
import xml.etree.ElementTree as ET
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import QTimer, QDir
from PyQt5.QtGui import QColor, QFont
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
from modOrganizer import ModListWidget
from otherWidget import OtherWidget



class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1118, 788)
        self.assets_dir = "./Archetype/theme/assets"
        self.archetype_root="./Archetype"
        self.custom_login = "./CustomThemes"
        self.custom_counter = "./CustomCounters"
        self.custom_cursor = "./CustomCursors"    
        if getattr(sys, "frozen", False):
            base_path = os.path.dirname(sys.executable)
        else:
            base_path = os.path.dirname(os.path.abspath(__file__))

        self.defaultConfig = os.path.join(base_path, "default.json")
        self.previewimages = os.path.join(base_path, "Preview")

        self.pokeballIcon = "./Archetype/theme/assets/jaejGI7pIp/res/custom/counter"
        self.gamePath = ""
        self.cursorDir = "./Archetype/theme/assets/jaejGI7pIp/res/custom/45pYZKcs0t" 
        self.themeFolder = "./Archetype/theme"
        self.configPath="./config.json"
        # self.defaultConfig="./default.json"
        if os.path.exists(self.configPath):
            self.modsLocation=self.get_current_path("mods_path",self.configPath)
        else:
            self.modsLocation=self.get_current_path("mods_path",self.defaultConfig)
        self.flipped_cache = {}
        self.mod_order_file = os.path.join(self.modsLocation, "mod_order.txt")
        self.theme_manager = ThemeManager()

        self.centralwidget = QtWidgets.QWidget(MainWindow)
        central_layout = QtWidgets.QVBoxLayout(self.centralwidget)
        self.centralwidget.setObjectName("centralwidget")
        self.tabWidget = QtWidgets.QTabWidget(self.centralwidget)
        self.tabWidget.setGeometry(QtCore.QRect(0, 0, 1116, 721))
        self.tabWidget.setObjectName("tabWidget")
        self.LoginScreen = QtWidgets.QWidget()
        self.LoginScreen.setObjectName("LoginScreen")
        self.unovaLoginOptions = QtWidgets.QFrame(self.LoginScreen)
        self.unovaLoginOptions.setGeometry(QtCore.QRect(5, 415, 340, 261))
        self.unovaLoginOptions.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.unovaLoginOptions.setObjectName("unovaLoginOptions")
       
        self.label_8 = self.make_label(self.unovaLoginOptions,"label_8",12,False,(20,65,181,201),None)
        self.label_9 = self.make_label(self.unovaLoginOptions,"label_9",16,True,(15,15,311,41),None)
        self.zekromColor = self.make_color_button(self.unovaLoginOptions,"zekrom-color",150,175)
        self.reshiramColor = self.make_color_button(self.unovaLoginOptions,"reshiram-color",150,90)
        self.zekromAura = self.make_color_button(self.unovaLoginOptions,"zekrom-aura",150,220)        
        self.reshiramAura = self.make_color_button(self.unovaLoginOptions,"reshiram-aura",150,130)

        self.addOwnLogin = QtWidgets.QFrame(self.LoginScreen)
        self.addOwnLogin.setGeometry(QtCore.QRect(5, 15, 436, 66))
        self.addOwnLogin.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.addOwnLogin.setFrameShadow(QtWidgets.QFrame.Raised)
        self.addOwnLogin.setObjectName("addOwnLogin")
        self.label_2 = self.make_label(self.addOwnLogin,"label_2",12,True,(5,15,241,30),None)

        self.label_2_status = QtWidgets.QLabel(self.LoginScreen)
        self.label_2_status.setGeometry(QtCore.QRect(25, 55, 400, 20))
        self.label_2_status.setText("") 
        self.label_2_status.setStyleSheet("color: green; font-size: 9pt;")
        if not self.ensure_archetype(MainWindow):
            sys.exit(0) 
        self.loginBrowse = QtWidgets.QPushButton(self.addOwnLogin)
        self.loginBrowse.setGeometry(QtCore.QRect(235, 20, 80, 25))
        self.loginBrowse.setObjectName("loginBrowse")
        self.loginBrowse.clicked.connect(self.handle_login_browse)        
        self.chooseLogin = QtWidgets.QFrame(self.LoginScreen)
        self.chooseLogin.setGeometry(QtCore.QRect(5, 90, 340, 320))
        self.chooseLogin.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.chooseLogin.setFrameShadow(QtWidgets.QFrame.Raised)
        self.chooseLogin.setObjectName("chooseLogin")
        self.loginDrop = QtWidgets.QComboBox(self.chooseLogin)
        self.loginDrop.setGeometry(QtCore.QRect(15, 35, 301, 25))
        self.loginDrop.setObjectName("loginDrop")

        self.label = self.make_label(self.chooseLogin,"label",16,True,(60,-10,226,51),None)
        self.loginPreviewFrame = QtWidgets.QFrame(self.LoginScreen)
        self.loginPreviewFrame.setGeometry(QtCore.QRect(360, 170, 731, 506))
        self.loginPreviewFrame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.loginPreviewFrame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.loginPreviewFrame.setObjectName("loginPreviewFrame")
        default_xml = os.path.join(self.assets_dir, "Allstars.xml")
        self.loginPreview = XmlAnimationPreview(default_xml,parent=self.loginPreviewFrame)
        self.loginPreview.setGeometry(QtCore.QRect(5, 5, 721, 496))
        self.loginPreview.setObjectName("loginPreview")
        self.tabWidget.addTab(self.LoginScreen, "")
        self.EncounterCounter = QtWidgets.QWidget()
        self.EncounterCounter.setObjectName("EncounterCounter")
        self.counterColorFrame = QtWidgets.QFrame(self.EncounterCounter)
        self.counterColorFrame.setGeometry(QtCore.QRect(15, 105, 306, 391))
        self.counterColorFrame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.counterColorFrame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.counterColorFrame.setObjectName("counterColorFrame")

        self.label_6 = self.make_label(self.counterColorFrame,"label_6",16,True,(15,15,311,41),None)
        self.label_7 = self.make_label(self.counterColorFrame,"label_7",12,False,(20,35,181,361),None)
        self.ballColor = self.make_color_button(self.counterColorFrame,"counter-ball-color",220,75)
        self.mainColor = self.make_color_button(self.counterColorFrame,"counter-main-color",220,205)
        self.fontColor = self.make_color_button(self.counterColorFrame,"counter-font",220,290)
        self.minMaxButtonColor = self.make_color_button(self.counterColorFrame,"counter-min-max-button-color",220,160)
        self.ballOutline = self.make_color_button(self.counterColorFrame,"ballOutline",220,115)
        self.subColor = self.make_color_button(self.counterColorFrame,"counter-sub-color",220,250)
        self.fontBorder = self.make_color_button(self.counterColorFrame,"counter-font-border",220,335)

        self.counterSelectorFrame = QtWidgets.QFrame(self.EncounterCounter)
        self.counterSelectorFrame.setGeometry(QtCore.QRect(15, 20, 531, 80))
        self.counterSelectorFrame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.counterSelectorFrame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.counterSelectorFrame.setObjectName("counterSelectorFrame")
        self.counterDrop = QtWidgets.QComboBox(self.counterSelectorFrame)
        self.counterDrop.setGeometry(QtCore.QRect(225, 25, 301, 25))
        self.counterDrop.setObjectName("counterDrop")
        self.counterDrop.setCurrentIndex(1)

        self.label_5 = self.make_label(self.counterSelectorFrame,"label_5",16,True,(5,5,211,61),None)

        self.counterPreviewFrame = QtWidgets.QFrame(self.EncounterCounter)
        self.counterPreviewFrame.setGeometry(QtCore.QRect(345, 125, 731, 506))
        self.counterPreviewFrame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.counterPreviewFrame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.counterPreviewFrame.setObjectName("counterPreviewFrame")
        default_xml = os.path.join(self.assets_dir, "Counter-Right.xml")
        self.counterPreview = CounterPreview(parent=self.counterPreviewFrame)
        self.counterPreview.setGeometry(QtCore.QRect(5, 5, 721, 496))
        self.counterPreview.setObjectName("counterPreview")

        self.counterText = QtWidgets.QLabel(self.counterPreviewFrame)
        self.counterText.setGeometry(QtCore.QRect(300, 170, 211, 200))
        font = QFont("Noto Sans", 14)
        font.setBold(True)
        self.counterText.setFont(font)
        self.counterText.setObjectName("counterText")
        self.fontColor.colorChanged.connect(lambda color: self.updateFontColor(color, self.counterText))

 
        self.addOwnVaritou = QtWidgets.QFrame(self.EncounterCounter)
        self.addOwnVaritou.setGeometry(QtCore.QRect(565, 20, 456, 86))
        self.addOwnVaritou.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.addOwnVaritou.setObjectName("addOwnVaritou")
        self.label_3 = self.make_label(self.addOwnVaritou,"label_3",12,True,(25,0,211,30),None)

        self.varitouBrowse = QtWidgets.QPushButton(self.addOwnVaritou)
        self.varitouBrowse.setGeometry(QtCore.QRect(235, 5, 80, 25))
        self.varitouBrowse.setObjectName("varitouBrowse")
        self.varitouBrowse.clicked.connect(self.handle_vartiou_browse)        
        
        self.label_16 = self.make_label(self.addOwnVaritou,"label_16",9,False,(25,35,386,17),None)

        self.customDrop = QtWidgets.QComboBox(self.addOwnVaritou)
        self.customDrop.setGeometry(QtCore.QRect(150, 55, 301, 25))
        self.customDrop.setObjectName("customDrop")

        self.label_18 = self.make_label(self.addOwnVaritou,"label_18",12,True,(5,50,141,30),None)

        self.tabWidget.addTab(self.EncounterCounter, "")
        self.WindowColors = QtWidgets.QWidget()
        self.WindowColors.setObjectName("WindowColors")
        self.windowPreviewFrame = QtWidgets.QFrame(self.WindowColors)
        self.windowPreviewFrame.setGeometry(QtCore.QRect(15, 25, 829, 653))
        self.windowPreviewFrame.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.windowPreviewFrame.setObjectName("windowPreviewFrame")
        self.windowPreview = CounterPreview(parent=self.windowPreviewFrame)
        self.windowPreview.setGeometry(QtCore.QRect(5, 5, 805, 577))
        self.windowPreview.setObjectName("windowPreview")

        self.hpBar = CounterPreview(parent=self.windowPreviewFrame)
        self.hpBar.setGeometry(QtCore.QRect(7, 592, 297, 63))
        self.hpBar.setObjectName("hpBar")       
        self.BerryPreview = QtWidgets.QWidget(self.windowPreviewFrame)
        self.BerryPreview.setGeometry(QtCore.QRect(347, 592, 307, 57))
        self.BerryPreview.setObjectName("BerryPreview")
        self.MainWindowFrame = QtWidgets.QFrame(self.WindowColors)
        self.MainWindowFrame.setGeometry(QtCore.QRect(868, 10, 233, 656))
        self.MainWindowFrame.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.MainWindowFrame.setObjectName("MainWindowFrame")
       
        self.label_4 = self.make_label(self.MainWindowFrame,"label_4",16,False,(8,319,146,137),None)        
        self.label_10 = self.make_label(self.MainWindowFrame,"label_10",16,False,(8,56,81,121),None)
        self.label_11 = self.make_label(self.MainWindowFrame,"label_11",16,False,(8,171,101,146),None)        
        self.label_12 = self.make_label(self.MainWindowFrame,"label_12",16,False,(8,515,143,139),None)
        self.label_13 = self.make_label(self.MainWindowFrame,"label_13",16,True,(46,1,155,61),None)
        self.label_14 = self.make_label(self.MainWindowFrame,"label_14",16,True,(-2,464,230,61),None)

        self.accentColorW = self.make_color_button(self.MainWindowFrame,"accent-color",158,152)
        self.subColorW = self.make_color_button(self.MainWindowFrame,"sub-color",158,94)
        self.mainColorW = self.make_color_button(self.MainWindowFrame,"main-color",158,66)        
        self.fontButtonW = self.make_color_button(self.MainWindowFrame,"font-button-color",158,378)        
        self.buttonColorW = self.make_color_button(self.MainWindowFrame,"button-color",158,124)
        self.fontSubW = self.make_color_button(self.MainWindowFrame,"font-sub-color",158,348)
        self.fontDisabledColorW = self.make_color_button(self.MainWindowFrame,"font-disabled-color",158,406)
        self.xpColorW = self.make_color_button(self.MainWindowFrame,"xp-color",158,264)
        self.friendshipColorW = self.make_color_button(self.MainWindowFrame,"friendship-color",158,292)
        self.fontMainW = self.make_color_button(self.MainWindowFrame,"font-main-color",158,320)
        self.hpHighW = self.make_color_button(self.MainWindowFrame,"hp-high-color",158,179)
        self.hpLowW = self.make_color_button(self.MainWindowFrame,"hp-low-color",158,234)
        self.hpMidW = self.make_color_button(self.MainWindowFrame,"hp-mid-color",158,206)
        self.waterW = self.make_color_button(self.MainWindowFrame,"water-warning",158,546)
        self.waterbg = self.make_color_button(self.MainWindowFrame,"water-background",158,518)
        self.berryProgress = self.make_color_button(self.MainWindowFrame,"berry-progress",158,576)
        self.berryWarning = self.make_color_button(self.MainWindowFrame,"berry-progress-warning",158,604)
        self.berryDisabled = self.make_color_button(self.MainWindowFrame,"berry-progress-disabled",158,632)
        self.iconColorW = self.make_color_button(self.MainWindowFrame,"icon-color",158,434)

        self.windowTextFontMain = QtWidgets.QLabel(self.windowPreviewFrame)
        self.windowTextFontMain.setGeometry(QtCore.QRect(40, -50, 211, 200))
        font = QFont("Noto Sans", 8)
        font.setBold(True)
        self.windowTextFontMain.setFont(font)
        self.windowTextFontMain.setObjectName("windowMainText")
        self.fontMainW.colorChanged.connect(lambda color: self.updateFontColor(color, self.windowTextFontMain))
        self.windowTextFontMain2 = QtWidgets.QLabel(self.windowPreviewFrame)
        self.windowTextFontMain2.setGeometry(QtCore.QRect(47, -27, 211, 200))
        font = QFont("Noto Sans", 7)
        self.windowTextFontMain2.setFont(font)
        self.windowTextFontMain2.setObjectName("windowMainText2")
        self.fontMainW.colorChanged.connect(lambda color: self.updateFontColor(color, self.windowTextFontMain2))


        self.windowTextFontSub = QtWidgets.QLabel(self.windowPreviewFrame)
        self.windowTextFontSub.setGeometry(QtCore.QRect(232, 147, 717, 61))
        font = QFont("Noto Sans", 8)
        self.windowTextFontSub.setFont(font)
        self.windowTextFontSub.setObjectName("windowSubText")
        self.fontSubW.colorChanged.connect(lambda color: self.updateFontColor(color, self.windowTextFontSub))     
        self.windowTextFontSub2 = QtWidgets.QLabel(self.windowPreviewFrame)
        self.windowTextFontSub2.setGeometry(QtCore.QRect(110, 115, 717, 61))
        font = QFont("Noto Sans", 8)
        self.windowTextFontSub2.setFont(font)
        self.windowTextFontSub2.setObjectName("windowSubText2")
        self.fontSubW.colorChanged.connect(lambda color: self.updateFontColor(color, self.windowTextFontSub2))    

        self.windowTextFontMinIV = QtWidgets.QLabel(self.windowPreviewFrame)
        self.windowTextFontMinIV.setGeometry(QtCore.QRect(428, 147, 61, 61))
        font = QFont("Noto Sans", 8)
        self.windowTextFontMinIV.setFont(font)
        self.windowTextFontMinIV.setObjectName("WindowMinIV")
        self.windowTextFontMinIV.setStyleSheet("color: #f46263;")
        self.windowTextFontMaxIV = QtWidgets.QLabel(self.windowPreviewFrame)
        self.windowTextFontMaxIV.setGeometry(QtCore.QRect(317, 147, 61, 61))
        font = QFont("Noto Sans", 8)
        self.windowTextFontMaxIV.setFont(font)
        self.windowTextFontMaxIV.setObjectName("WindowMaxIV")
        self.windowTextFontMaxIV.setStyleSheet("color: #6eb66e;") 
        
        self.windowTextFontButton1 = QtWidgets.QLabel(self.windowPreviewFrame)
        self.windowTextFontButton1.setGeometry(QtCore.QRect(160,45, 717, 61))
        font = QFont("Noto Sans", 8)
        self.windowTextFontButton1.setFont(font)
        self.windowTextFontButton1.setObjectName("TextFontButton1")
        self.fontButtonW.colorChanged.connect(lambda color: self.updateFontColor(color, self.windowTextFontButton1))     
        self.windowTextFontButton2 = QtWidgets.QLabel(self.windowPreviewFrame)
        self.windowTextFontButton2.setGeometry(QtCore.QRect(100, 80, 717, 61))
        font = QFont("Noto Sans", 8)
        self.windowTextFontButton2.setFont(font)
        self.windowTextFontButton2.setObjectName("TextFontButton2")
        self.fontButtonW.colorChanged.connect(lambda color: self.updateFontColor(color, self.windowTextFontButton2))    
        self.windowTextFontButton3 = QtWidgets.QLabel(self.windowPreviewFrame)
        self.windowTextFontButton3.setGeometry(QtCore.QRect(130, 147, 717, 61))
        font = QFont("Noto Sans", 8)
        self.windowTextFontButton3.setFont(font)
        self.windowTextFontButton3.setObjectName("TextFontButton3")
        self.fontButtonW.colorChanged.connect(lambda color: self.updateFontColor(color, self.windowTextFontButton3))    
        self.windowTextFontButton4 = QtWidgets.QLabel(self.windowPreviewFrame)
        self.windowTextFontButton4.setGeometry(QtCore.QRect(225, 493, 717, 61))
        font = QFont("Noto Sans", 8)
        self.windowTextFontButton4.setFont(font)
        self.windowTextFontButton4.setObjectName("TextFontButton4")
        self.fontButtonW.colorChanged.connect(lambda color: self.updateFontColor(color, self.windowTextFontButton4))    
        
        self.windowTextFontDisabled1 = QtWidgets.QLabel(self.windowPreviewFrame)
        self.windowTextFontDisabled1.setGeometry(QtCore.QRect(602, 80, 61, 61))
        font = QFont("Noto Sans", 8)
        self.windowTextFontDisabled1.setFont(font)
        self.windowTextFontDisabled1.setObjectName("TextFontDisabled1")
        self.fontDisabledColorW.colorChanged.connect(lambda color: self.updateFontColor(color, self.windowTextFontDisabled1))  
        self.windowTextFontDisabled2 = QtWidgets.QLabel(self.windowPreviewFrame)
        self.windowTextFontDisabled2.setGeometry(QtCore.QRect(160, 493, 100, 61))
        font = QFont("Noto Sans", 8)
        self.windowTextFontDisabled2.setFont(font)
        self.windowTextFontDisabled2.setObjectName("TextFontDisabled1")
        self.fontDisabledColorW.colorChanged.connect(lambda color: self.updateFontColor(color, self.windowTextFontDisabled2))  

        self.label_12.raise_()
        self.label_11.raise_()
        self.label_4.raise_()
        self.label_10.raise_()
        self.accentColorW.raise_()
        self.subColorW.raise_()
        self.mainColorW.raise_()
        self.fontButtonW.raise_()
        self.buttonColorW.raise_()
        self.fontSubW.raise_()
        self.fontDisabledColorW.raise_()
        self.xpColorW.raise_()
        self.friendshipColorW.raise_()
        self.fontMainW.raise_()
        self.hpHighW.raise_()
        self.hpLowW.raise_()
        self.hpMidW.raise_()
        self.label_13.raise_()
        self.waterW.raise_()
        self.label_14.raise_()
        self.waterbg.raise_()
        self.berryProgress.raise_()
        self.berryWarning.raise_()
        self.tabWidget.addTab(self.WindowColors, "")

        self.OtherScreen = QtWidgets.QWidget()
        self.OtherScreen.setObjectName("OtherScreen")
        self.cursoFrame = QtWidgets.QFrame(self.OtherScreen)
        self.cursoFrame.setGeometry(QtCore.QRect(10, 30, 561, 141))
        self.cursoFrame.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.cursoFrame.setObjectName("cursoFrame")
        self.cursorDrop = QtWidgets.QComboBox(self.cursoFrame)
        self.cursorDrop.setGeometry(QtCore.QRect(225, 25, 301, 25))
        self.cursorDrop.setObjectName("cursorDrop")
        self.label_15 = self.make_label(self.cursoFrame,"label_15",16,True,(5,5,211,61),None)
        self.cursorBrowse = QtWidgets.QPushButton(self.cursoFrame)
        self.cursorBrowse.setGeometry(QtCore.QRect(435, 70, 80, 25))
        self.cursorBrowse.setObjectName("cursorBrowse")
        self.label_17 = self.make_label(self.cursoFrame,"label_17",12,True,(195,65,241,30),None)
        self.label_30 = self.make_label(self.cursoFrame,"label_30",12,True,(195,96,241,30),None)
        self.cursorEditButton = QtWidgets.QPushButton(self.cursoFrame)
        self.cursorEditButton.setGeometry(QtCore.QRect(435, 101, 80, 25))
        self.cursorEditButton.setObjectName("cursorEdit")

        self.cursorPreviewFrame = QtWidgets.QFrame(self.OtherScreen)
        self.cursorPreviewFrame.setGeometry(QtCore.QRect(680, 10, 321, 166))
        self.cursorPreviewFrame.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.cursorPreviewFrame.setObjectName("cursorPreviewFrame")
        self.cursorPreview = OtherWidget(self.cursorPreviewFrame)
        self.cursorPreview.setGeometry(QtCore.QRect(5, 5, 310, 155))
        self.cursorPreview.setObjectName("cursorPreview")
        self.iconFrame = QtWidgets.QFrame(self.OtherScreen)
        self.iconFrame.setGeometry(QtCore.QRect(10, 225, 561, 80))
        self.iconFrame.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.iconFrame.setObjectName("iconFrame")
        self.iconDrop = QtWidgets.QComboBox(self.iconFrame)
        self.iconDrop.setGeometry(QtCore.QRect(225, 25, 301, 25))
        self.iconDrop.setObjectName("iconDrop")
        self.iconDrop.addItem("")
        self.iconDrop.addItem("")
        self.label_20 = self.make_label(self.iconFrame,"label_20",16,True,(5,5,211,61),None)
        self.speechBubblesFrame = QtWidgets.QFrame(self.OtherScreen)
        self.speechBubblesFrame.setGeometry(QtCore.QRect(10, 385, 561, 121))
        self.speechBubblesFrame.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.speechBubblesFrame.setObjectName("speechBubblesFrame")
        self.speechDrop = QtWidgets.QComboBox(self.speechBubblesFrame)
        self.speechDrop.setGeometry(QtCore.QRect(225, 25, 301, 25))
        self.speechDrop.setObjectName("speechDrop")
        self.label_23 = self.make_label(self.speechBubblesFrame,"label_23",16,True,(5,5,211,61),None)
        self.speechBrowse = QtWidgets.QPushButton(self.speechBubblesFrame)
        self.speechBrowse.setGeometry(QtCore.QRect(435, 70, 80, 25))
        self.speechBrowse.setObjectName("speechBrowse")
        self.label_24 = self.make_label(self.speechBubblesFrame,"label_24",12,True,(195,65,241,30),None)
        self.speechBubblePreviewFrame = QtWidgets.QFrame(self.OtherScreen)
        self.speechBubblePreviewFrame.setGeometry(QtCore.QRect(680, 365, 321, 166))
        self.speechBubblePreviewFrame.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.speechBubblePreviewFrame.setObjectName("speechBubblePreviewFrame")
        self.speechBubblePreview = QtWidgets.QWidget(self.speechBubblePreviewFrame)
        self.speechBubblePreview.setGeometry(QtCore.QRect(5, 5, 310, 155))
        self.speechBubblePreview.setObjectName("speechBubblePreview")




        self.tabWidget.addTab(self.OtherScreen, "")
        self.Archetype = QtWidgets.QWidget()
        self.Archetype.setObjectName("Archetype")
        self.Mods = QtWidgets.QWidget()
        self.Mods.setObjectName("Mods")

        self.modOrderFrame = QtWidgets.QFrame(self.Mods)
        self.modOrderFrame.setGeometry(QtCore.QRect(12, 136, 1087, 543))
        self.modOrderFrame.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.modOrderFrame.setObjectName("modOrderFrame")
        self.modButtonsFrame = QtWidgets.QFrame(self.Mods)
        self.modButtonsFrame.setGeometry(QtCore.QRect(238, 20, 585, 97))
        self.modButtonsFrame.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.modButtonsFrame.setObjectName("modButtonsFrame")

        self.modButtonLabel = self.make_label(self.modButtonsFrame,"modButtonLabel",12,True,(260,12,79,30),None)

        self.mods_widget = ModListWidget(mods_folder=self.modsLocation,parent=self.modOrderFrame)
        layout = QtWidgets.QVBoxLayout(self.modOrderFrame)
        layout.setContentsMargins(0, 0, 0, 0) 
        layout.addWidget(self.mods_widget)


        self.GetArchtype = QtWidgets.QFrame(self.Archetype)
        self.GetArchtype.setGeometry(QtCore.QRect(12, 19, 1089, 657))
        self.GetArchtype.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.GetArchtype.setObjectName("GetArchtype")
        self.label_25 = self.make_label(self.GetArchtype,"label_25",16,True,(5,5,236,61),None)
        self.downloadArch = QtWidgets.QPushButton(self.GetArchtype)
        self.downloadArch.setGeometry(QtCore.QRect(245, 15, 281, 46))
        font = QtGui.QFont()
        font.setPointSize(16)
        font.setBold(True)
        font.setWeight(75)
        self.downloadArch.setFont(font)
        self.downloadArch.setObjectName("downloadArch")

        self.label_27 = self.make_label(self.GetArchtype,"label_27",16,True,(5,134,210,61),None)
        self.setModFolder = QtWidgets.QPushButton(self.GetArchtype)
        self.setModFolder.setGeometry(QtCore.QRect(245, 144, 281, 46))
        font = QtGui.QFont()
        font.setPointSize(16)
        font.setBold(True)
        font.setWeight(75)
        self.setModFolder.setFont(font)
        self.setModFolder.setObjectName("setModFolder")

        self.labelBrowse = self.make_label(self.GetArchtype,"Set Game Path",16,True,(5,70,210,61),None)
        self.setGamePath = QtWidgets.QPushButton(self.GetArchtype)
        self.setGamePath.setGeometry(QtCore.QRect(245, 80, 280, 46))
        font = QtGui.QFont()
        font.setPointSize(16)
        font.setBold(True)
        font.setWeight(75)
        self.setGamePath.setFont(font)
        self.setGamePath.setObjectName("setGamePath")
        self.completeMod = QtWidgets.QPushButton(self.GetArchtype)
        self.completeMod.setGeometry(QtCore.QRect(595, 70, 280, 46))
        font = QtGui.QFont()
        font.setPointSize(16)
        font.setBold(True)
        font.setWeight(75)
        self.completeMod.setFont(font)
        self.completeMod.setObjectName("completeMod")

        self.playPokemmo = QtWidgets.QPushButton(self.GetArchtype)
        self.playPokemmo.setGeometry(QtCore.QRect(806, 606, 280, 46))
        font = QtGui.QFont()
        font.setPointSize(16)
        font.setBold(True)
        font.setWeight(75)
        self.playPokemmo.setFont(font)
        self.playPokemmo.setObjectName("playPokemmo")
        

        
        self.label_28 = self.make_label(self.GetArchtype,"label_28",16,True,(590,0,306,61),None)
        self.tabWidget.addTab(self.Mods, "")
        MainWindow.setCentralWidget(self.centralwidget)
        self.tabWidget.addTab(self.Archetype, "")
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
        self.menuFile.addAction(self.actionSave)
        self.menuFile.addAction(self.actionSaveAs)
        self.menuFile.addAction(self.actionLoad)
        self.menuFile.addAction(self.actionLoadDefault)
        self.menuHelp.addAction(self.actionAbout)
        self.menuFile.addSeparator()
        self.menuFile.addAction(self.actionExit)
        self.menubar.addAction(self.menuFile.menuAction())
        self.menubar.addAction(self.menuHelp.menuAction())

        self.status_label_archetype = QtWidgets.QLabel(self.GetArchtype)
        self.status_label_archetype.setGeometry(QtCore.QRect(4, 610, 795, 35))
        self.status_label_archetype.setText("") 
        self.status_label_archetype.setStyleSheet("color: green; font-size: 18pt;")

        self.status_label_custom_counter = QtWidgets.QLabel(self.counterPreview)
        self.status_label_custom_counter.setGeometry(QtCore.QRect(277, 10, 383, 17))
        self.status_label_custom_counter.setText("") 
        self.status_label_custom_counter.setStyleSheet("color: green; font-size: 8pt;")

        self.status_label_mods = QtWidgets.QLabel(self.modButtonsFrame)
        self.status_label_mods.setGeometry(QtCore.QRect(0, 0, 255, 30))
        self.status_label_mods.setText("") 
        self.status_label_mods.setStyleSheet("color: green; font-size: 12pt;")

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


        self.mainColor.colorChanged.connect(lambda c: self.counterPreview.set_layer_tint(0, QColor(c)))
        self.subColor.colorChanged.connect(lambda c: self.counterPreview.set_layer_tint(1, QColor(c)))
        self.minMaxButtonColor.colorChanged.connect(lambda c: self.counterPreview.set_layer_tint(2, QColor(c)))
        self.ballOutline.colorChanged.connect(lambda c: self.counterPreview.set_layer_tint(8, c))
        self.ballColor.colorChanged.connect(lambda c: self.counterPreview.set_layer_tint(7, c))

        self.buttonColorW.colorChanged.connect(lambda c:self.windowPreview.set_layer_tint(0, QColor(c)))
        self.iconColorW.colorChanged.connect(lambda c: self.windowPreview.set_layer_tint(1, QColor(c)))
        self.subColorW.colorChanged.connect(lambda c: self.windowPreview.set_layer_tint(3, QColor(c)))
        self.accentColorW.colorChanged.connect(lambda c: self.windowPreview.set_layer_tint(4, QColor(c)))
        self.mainColorW.colorChanged.connect(lambda c: self.windowPreview.set_layer_tint(5, QColor(c)))
        
        self.subColorW.colorChanged.connect(lambda c:self.hpBar.set_layer_tint(1, QColor(c)))
        self.hpHighW.colorChanged.connect(lambda c: self.hpBar.set_layer_tint(3, QColor(c)))
        self.hpMidW.colorChanged.connect(lambda c: self.hpBar.set_layer_tint(4, QColor(c)))
        self.hpLowW.colorChanged.connect(lambda c: self.hpBar.set_layer_tint(5, QColor(c)))
        self.xpColorW.colorChanged.connect(lambda c: self.hpBar.set_layer_tint(6, QColor(c)))

        
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
            (5,446,1071,143),
            None
        )
        self.status_label_archetype2.setTextFormat(QtCore.Qt.RichText)
        self.update_archetype_summary()

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
        base_folder=self.assets_dir,
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
            base_folder=self.assets_dir,
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
            base_folder=self.assets_dir,
            file_ext=".xml", 
            include_subfolders=False,
            file_filter=lambda f: f.startswith("Cursors-"),
        )  

    def update_bubbles_drop(self):

        self.populate_dropdown(
            combo=self.speechDrop,
            base_folder=self.assets_dir,
            file_ext=".xml",
            include_subfolders=False,
            file_filter=lambda f: f.startswith("Default-"),
        )  

    def poke_start(self, *args):
        self.save_config()
        try:
            with open("config.json", "r") as f:
                config = json.load(f)
        except Exception:
            self.status_label_archetype.setText("Error: The Game Path is not set")
            return

        gamepath = (
            config.get("paths", {})
                .get("game_path")
        )

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
            cmd = [script_path]
        else:
            script_path = os.path.join(gamepath, script_name + ".sh")
            if not os.access(script_path, os.X_OK):
                os.chmod(script_path, 0o755)
            cmd = ["bash", script_path]

        if not os.path.exists(script_path):
            self.status_label_archetype.setText(
                f"Error: Launch script not found:\n{script_path}"
            )
            return

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
            base_folder=self.assets_dir,
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

        self.update_single_preview(
            self.cursorPreview,
            self.assets_dir,
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

    def handle_zip_import(self, update_func, label_widget):
        file_path, _ = QFileDialog.getOpenFileName(None, "Select a Theme ZIP", "", "Zip Files (*.zip);;All Files (*)")
        if not file_path:
            return
        new_theme = self.theme_manager.add_theme_from_zip(file_path, parent_widget=self)
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
        shutil.copy2(file_path,self.modsLocation)

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
            up_to_date = self.check_remote_version(
                "https://github.com/ssjshields/archetype",
                "Archetype"
            )

            if up_to_date:
                archetype_status = '<span style="color:#28a745;">Up to date.</span>'
            else:
                archetype_status = '<span style="color:#ff9800;">Update available!</span>'

        except Exception:
            archetype_status = '<span style="color:#ff3b3b;">Could not check status.</span>'

        self.status_label_archetype2.setText(
            f"<b>Pokemmo Location:</b> {self.get_current_path("game_path",self.configPath)}<br>"
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
            
            for line in remote_refs.stdout.splitlines():
                if line.startswith("ref:"):
                    default_branch = line.split()[1].split("/")[-1]
                    break
            else:
                default_branch = "main"

            remote_hash_output = subprocess.run(
                ["git", "ls-remote", repo_url, f"refs/heads/{default_branch}"],
                check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
            )
            remote_hash = remote_hash_output.stdout.split()[0].strip()

            local_hash = None
            if os.path.exists(destination) and os.path.exists(os.path.join(destination, ".git")):
                local_hash_output = subprocess.run(
                    ["git", "-C", destination, "rev-parse", default_branch],
                    stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
                )
                if local_hash_output.returncode == 0:
                    local_hash = local_hash_output.stdout.strip()

            if local_hash == remote_hash:
                status_label.setText("Archetype is already up to date.")
                status_label.setStyleSheet("color: green; font-size: 18pt;")
            else:
                if local_hash:
                    subprocess.run(["git", "-C", destination, "pull"], check=True)
                    msg = "Updated"
                else:
                    if os.path.exists(destination):
                        import shutil
                        shutil.rmtree(destination)
                    subprocess.run(["git", "clone", repo_url, destination], check=True)
                    msg = "Downloaded"

                status_label.setText(f"Archetype {msg}")
                status_label.setStyleSheet("color: green; font-size: 18pt;")

        except subprocess.CalledProcessError as e:
            status_label.setText(f"Failed!: {e}")
            status_label.setStyleSheet("color: red; font-size: 18pt;")

        QTimer.singleShot(30000, lambda: status_label.setText(""))

    def downloadLatestArch(self):
        self.git_clone_or_pull("https://github.com/ssjshields/archetype", "Archetype", self.status_label_archetype)
        self.update_archetype_summary()

    def make_label(self, parent, text="", font_size=12, bold=False, geometry=None, align=None):
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
        return label

    def make_color_button(self,parent, name, x, y, width=48, height=23):
        btn = KColorButton(parent)
        btn.setGeometry(QtCore.QRect(x, y, width, height))
        btn.setObjectName(name)
        return btn

    def save_config(self):
        if os.path.exists(self.configPath):
            try:
                with open(self.configPath, "r", encoding="utf-8") as f:
                    existing_config = json.load(f)
            except Exception as e:
                print(f"Failed to load existing config: {e}")
                existing_config = {}
        else:
            existing_config = {}

        existing_game_path = existing_config.get("paths", {}).get("game_path")
        existing_mods_path = existing_config.get("paths", {}).get("mods_path")

        # self.customconfig=new_path
        config = {
            "colors": {
                "main-color": self.mainColorW.color().name(),
                "sub-color": self.subColorW.color().name(),
                "button-color": self.buttonColorW.color().name(),
                "accent-color": self.accentColorW.color().name(),
                "font-main-color": self.fontMainW.color().name(),
                "font-sub-color": self.fontSubW.color().name(),
                "font-button-color": self.fontButtonW.color().name(),
                "font-disabled-color": self.fontDisabledColorW.color().name(),
                "hp-high-color": self.hpHighW.color().name(),
                "hp-mid-color": self.hpMidW.color().name(),
                "hp-low-color": self.hpLowW.color().name(),
                "xp-color": self.xpColorW.color().name(),
                "friendship-color": self.friendshipColorW.color().name(),
                "icon-color": self.iconColorW.color().name(),
                "water-background": self.waterbg.color().name(),
                "water-warning": self.waterW.color().name(),
                "berry-progress": self.berryProgress.color().name(),
                "berry-progress-warning": self.berryWarning.color().name(),
                "berry-progress-disabled": self.berryDisabled.color().name(),
                "reshiram-color": self.reshiramColor.color().name(),
                "reshiram-aura": self.reshiramAura.color().name(),
                "zekrom-color": self.zekromColor.color().name(),
                "zekrom-aura": self.zekromAura.color().name(),
                "counter-ball-color": self.ballColor.color().name(),
                "counter-ball-outline":self.ballOutline.color().name(),
                "counter-min-max-button-color": self.minMaxButtonColor.color().name(),
                "counter-main-color": self.mainColor.color().name(),
                "counter-sub-color": self.subColor.color().name(),
                "counter-font": self.fontColor.color().name(),
                "counter-font-border":self.fontBorder.color().name(),
            },
            
            "paths": {
                "login_screen": self.loginDrop.currentText(),
                "encounter_counter": self.counterDrop.currentText(),
                "custom_counter_current": self.customDrop.currentText(),
                "game_path": self.gamePath or existing_game_path,
                "mods_path": self.modsLocation or existing_mods_path
            },

            "look":{
                "login_screen": os.path.join("assets/",self.loginDrop.currentText()),
                "arch_cursor": os.path.join("assets/",self.cursorDrop.currentText()),
                "arch_shape": os.path.join("assets/",self.iconDrop.currentText()),
                "speech_bubbles": os.path.join("assets/",self.speechDrop.currentText()),
            },
            "counter":{
                "encounter_counter":os.path.join("assets/",self.counterDrop.currentText()),
            },

            "state": {
                "current_tab": self.tabWidget.currentIndex(),
                "loginDrop": self.loginDrop.currentIndex(),
                "counterDrop": self.counterDrop.currentIndex(),
                "customDrop": self.customDrop.currentIndex(),
                "bubblesDrop": self.speechDrop.currentIndex(),
                "icon_drop": self.iconDrop.currentIndex(),
                "cursor_drop": self.cursorDrop.currentIndex(),
            },
            # "lastconfig":{
            #     "last_config_location":new_path
            # }
        }

        with open(self.configPath, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=4)

        print(f"Config saved: {self.configPath}")

    def save_config_as(self):
        new_path, _ = QtWidgets.QFileDialog.getSaveFileName(
            None,
            "Save Configuration As",
            os.path.expanduser("~"),
            "JSON Files (*.json);;All Files (*)"
        )

        if not new_path:
            print("Save As canceled.")
            return

        if not new_path.lower().endswith(".json"):
            new_path += ".json"

        if os.path.exists(self.configPath):
            try:
                with open(self.configPath, "r", encoding="utf-8") as f:
                    existing_config = json.load(f)
            except Exception as e:
                print(f"Failed to load existing config: {e}")
                existing_config = {}
        else:
            existing_config = {}

        existing_game_path = existing_config.get("paths", {}).get("game_path")

        config = {
            "colors": {
                "main-color": self.mainColorW.color().name(),
                "sub-color": self.subColorW.color().name(),
                "button-color": self.buttonColorW.color().name(),
                "accent-color": self.accentColorW.color().name(),
                "font-main-color": self.fontMainW.color().name(),
                "font-sub-color": self.fontSubW.color().name(),
                "font-button-color": self.fontButtonW.color().name(),
                "font-disabled-color": self.fontDisabledColorW.color().name(),
                "hp-high-color": self.hpHighW.color().name(),
                "hp-mid-color": self.hpMidW.color().name(),
                "hp-low-color": self.hpLowW.color().name(),
                "xp-color": self.xpColorW.color().name(),
                "friendship-color": self.friendshipColorW.color().name(),
                "icon-color": self.iconColorW.color().name(),
                "water-background": self.waterbg.color().name(),
                "water-warning": self.waterW.color().name(),
                "berry-progress": self.berryProgress.color().name(),
                "berry-progress-warning": self.berryWarning.color().name(),
                "berry-progress-disabled": self.berryDisabled.color().name(),
                "reshiram-color": self.reshiramColor.color().name(),
                "reshiram-aura": self.reshiramAura.color().name(),
                "zekrom-color": self.zekromColor.color().name(),
                "zekrom-aura": self.zekromAura.color().name(),
                "counter-ball-color": self.ballColor.color().name(),
                "counter-ball-outline":self.ballOutline.color().name(),
                "counter-min-max-button-color": self.minMaxButtonColor.color().name(),
                "counter-main-color": self.mainColor.color().name(),
                "counter-sub-color": self.subColor.color().name(),
                "counter-font": self.fontColor.color().name(),
                "counter-font-border":self.fontBorder.color().name(),
            },
            
            "paths": {
                "login_screen": self.loginDrop.currentText(),
                "encounter_counter": self.counterDrop.currentText(),
                "custom_counter_current": self.customDrop.currentText(),
                "game_path": self.gamePath or existing_game_path,
            },

            "look":{
                "login_screen": os.path.join("assets/",self.loginDrop.currentText()),
                "arch_cursor": os.path.join("assets/",self.cursorDrop.currentText()),
                "arch_shape": os.path.join("assets/",self.iconDrop.currentText()),
                "speech_bubbles": os.path.join("assets/",self.speechDrop.currentText()),
            },
            "counter":{
                "encounter_counter":os.path.join("assets/",self.counterDrop.currentText()),
            },

            "state": {
                "current_tab": self.tabWidget.currentIndex(),
                "loginDrop": self.loginDrop.currentIndex(),
                "counterDrop": self.counterDrop.currentIndex(),
                "customDrop": self.customDrop.currentIndex(),
                "bubblesDrop": self.speechDrop.currentIndex(),
                "icon_drop": self.iconDrop.currentIndex(),
                "cursor_drop": self.cursorDrop.currentIndex(),
            },
            # "lastconfig":{
            #     "last_config_location":new_path
            # }
        }

        try:
            with open(new_path, "w", encoding="utf-8") as f:
                json.dump(config, f, indent=4)
            print(f"Config saved as: {new_path}")
            self.configPath = new_path
        except Exception as e:
            print(f"Failed to save config as {new_path}: {e}")

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

    def _load_config_from_path(self, path):
        if not os.path.exists(path):
            print(f"No config file found at {path}, using defaults.")
            return

        with open(path, "r", encoding="utf-8") as f:
            config = json.load(f)

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
        ]

        for attr, state_key in combo_keys:
            combo = getattr(self, attr, None)
            if combo and isinstance(combo, QtWidgets.QComboBox):
                index = state.get(state_key, 0)
                if 0 <= index < combo.count():
                    combo.setCurrentIndex(index)
                else:
                    print(f"[Warning] Index {index} out of range for {attr}")
                    
        self.modsLocation=self.get_current_path("mods_path",self.configPath)

    def load_last_config(self):
        self._load_config_from_path(self.configPath)

    def load_default_config(self):
        self._load_config_from_path(self.defaultConfig)

    def load_config(self):
        file_path, _ = QtWidgets.QFileDialog.getOpenFileName(
            None,  
            "Select Config File",
            os.path.dirname(self.configPath) if hasattr(self, "configPath") else "",
            "JSON Files (*.json);;All Files (*)"
        )

        if not file_path:
            print("No config file selected, using defaults.")
            return

        if not os.path.exists(file_path):
            print(f"Selected file does not exist: {file_path}")
            return

        self._load_config_from_path(file_path)

        self.configPath = file_path

        print(f"Loaded config from: {file_path}")

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

                self.save_config()
                up_to_date = self.check_remote_version(
                    "https://github.com/ssjshields/archetype",
                    "Archetype"
                )

                if up_to_date:
                    archetype_status = "Up to Date."
                else:
                    archetype_status = "Update available!"

                self.status_label_archetype2.setText(
                    f"<b>Pokemmo Location:</b> {self.get_current_path("game_path",self.configPath)}<br>"
                    f"<b>Archetype Status:</b> {archetype_status}<br>"
                    f"<b>Mod Folder:</b>{os.path.abspath(self.modsLocation)}<br>"
                    f"<b>Mod Count:</b> {self.mod_count(self.modsLocation)}"
                )

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
                up_to_date = self.check_remote_version(
                    "https://github.com/ssjshields/archetype",
                    "Archetype"
                )

                if up_to_date:
                    archetype_status = "Up to Date."
                else:
                    archetype_status = "Update available!"

                self.status_label_archetype2.setText(
                    f"<b>Pokemmo Location:</b> {self.get_current_path("game_path",self.configPath)}<br>"
                    f"<b>Archetype Status:</b> {archetype_status}<br>"
                    f"<b>Mod Folder:</b>{os.path.abspath(self.modsLocation)}<br>"
                    f"<b>Mod Count:</b> {self.mod_count(self.modsLocation)}"
                )

    def complete_build(self):
        self.save_config()
        colors = CompleteBuild(self.configPath, os.path.join(self.themeFolder, "CHOOSE_YOUR_COLORS.xml"), category="colors")
        counter = CompleteBuild(self.configPath, os.path.join(self.themeFolder, "CHOOSE_YOUR_COUNTER.xml"), category="counter")
        look = CompleteBuild(self.configPath, os.path.join(self.themeFolder, "CHOOSE_YOUR_LOOK.xml"), category="look")

        print(self.counterDrop.currentText())
        colors.generate_xml()
        counter.generate_xml()
        look.generate_xml()
        if self.loginDrop.currentText() not in ("Unova.xml", "Allstars.xml"):           
            self.copy_files(os.path.join("./CustomThemes",self.loginDrop.currentText().removesuffix(".xml")) ,self.assets_dir)

        if self.counterDrop.currentText() == "Counter-Vartiou.xml":
            self.copy_files(os.path.join("./CustomCounters",self.customDrop.currentText(),"data/themes/default/res"),os.path.join(self.assets_dir,"jaejGI7pIp/res/counter/vartiou"))
        
        self.gamePath = self.get_current_path("game_path",self.configPath)

        print(f"current path is: {self.gamePath}")
        if os.path.exists(os.path.join(self.gamePath,"data/mods/Archetype")):
            shutil.rmtree(os.path.join(self.gamePath,"data/mods/Archetype"))
        self.symlink_create("./Archetype", os.path.join(self.gamePath,"data/mods/Archetype"))
        self.symlink_create(self.modsLocation,os.path.join(self.gamePath,"data/mods"))
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
                # Remove existing destination
                if os.path.lexists(dst_path):
                    if os.path.islink(dst_path) or os.path.isfile(dst_path):
                        os.remove(dst_path)
                    elif os.path.isdir(dst_path):
                        shutil.rmtree(dst_path)

                abs_src = os.path.abspath(src_path)
                abs_dst = os.path.abspath(dst_path)

                # ⭐ NEW: If it's a folder, create ONE symlink to the entire folder
                if os.path.isdir(src_path):
                    print(f"Creating FOLDER symlink: {abs_src} -> {abs_dst}")
                    os.symlink(abs_src, abs_dst)
                else:
                    print(f"Creating FILE symlink: {abs_src} -> {abs_dst}")
                    os.symlink(abs_src, abs_dst)

            except Exception as e:
                print(f"Failed to symlink {src_path} -> {dst_path}: {e}")

        print(f"Symlinks created from '{src_folder}' to '{dst_folder}'")

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
        target_png = os.path.join(self.assets_dir, f"Cursors-{cursor_name}.png")
        target_xml = os.path.join(self.assets_dir, f"Cursors-{cursor_name}.xml")
        extra_png = f"Cursors-{cursor_name}.png"

        while os.path.exists(target_png) or os.path.exists(target_xml):
            cursor_name = f"{base_name}_{counter}"
            target_png = os.path.join(self.assets_dir, f"Cursors-{cursor_name}.png")
            target_xml = os.path.join(self.assets_dir, f"Cursors-{cursor_name}.xml")
            counter += 1

        shutil.copy(file_path, target_png)

        source_xml = os.path.join(self.assets_dir, "Cursors-Black.xml")
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

        xml_path = os.path.join(self.assets_dir, cursor_name)

        dialog = CursorEdit(
            xml_path,
            on_save=self.update_cursor_preview
        )

        dialog.exec_()

    def ensure_archetype(self, parent=None):
        if os.path.exists(self.archetype_root):
            return True

        choice = QMessageBox.question(
            parent,
            "Archetype Missing",
            "Archetype is required in order to use Vextryyn's Mod Manager.\nThere are 2 ways to do this:\n\nOption 1: Go to https://github.com/ssjshields/archetype download and extract into the VMM folder\n\nOption 2: press Yes and this will download all the files for you",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.Yes
        )

        if choice == QMessageBox.No:
            return False 

        status_win = QtWidgets.QWidget()
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
        if os.path.exists(self.archetype_root):
            subprocess.run(["git", "-C", self.archetype_root, "pull"])
        else:
            subprocess.run(["git", "clone", repo_url, self.archetype_root])

        status_label.setText("Download complete!")
        QApplication.processEvents()
        status_win.close()
        return True

    def show_about_window(self):
        dlg = AboutWindow()
        dlg.exec_() 

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "Vextryyn's Mod Manager"))
        self.label_8.setText(_translate("MainWindow", "reshiram color\n"
        "\n"
        "reshiram aura\n"
        "\n"
        "zekrom color\n"
        "\n"
        "zekrom aura"))
        self.label_9.setText(_translate("MainWindow", "Unova Login Screen Options"))
        self.label_2.setText(_translate("MainWindow", "Add Your Own Login Screen"))
        self.loginBrowse.setText(_translate("MainWindow", "Browse..."))
        self.label.setText(_translate("MainWindow", "Choose Login Screen"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.LoginScreen), _translate("MainWindow", "Login Screen"))
        self.label_6.setText(_translate("MainWindow", "Encounter Counter Colors"))
        self.label_7.setText(_translate("MainWindow", " ball color\n"
        "\n"
        " ball outline\n"
        "\n"
        " min max button color\n"
        "\n"
        " main color\n"
        "\n"
        " sub color\n"
        "\n"
        " font\n"
        "\n"
        " font border"))
        self.label_5.setText(_translate("MainWindow", "Encounter Counter"))
        self.label_3.setText(_translate("MainWindow", " Add Vartiou here"))
        self.varitouBrowse.setText(_translate("MainWindow", "Browse..."))
        self.label_16.setText(_translate("MainWindow", "This will do the work getting what is needed, just choose the zip file"))
        self.label_18.setText(_translate("MainWindow", "Choose Custom"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.EncounterCounter), _translate("MainWindow", "Encounter Counter"))
        self.label_11.setText(_translate("MainWindow", "hp high \n"
        "hp mid\n"
        "hp low\n"
        "xp\n"
        "friendship"))
        self.label_10.setText(_translate("MainWindow", "main\n"
        "sub\n"
        "button\n"
        "accent"))
        self.label_4.setText(_translate("MainWindow", "font main\n"
        "font sub\n"
        "font button\n"
        "font disabled\nIcon"))
        self.label_13.setText(_translate("MainWindow", "Main Window"))

        self.counterText.setText(_translate("MainWindow","Pokemon        1\n\n\nPokemon        2\n\n\nPokemon        3"))
        self.windowTextFontMain.setText(_translate("MainWindow","           Global Trade Link"))
        self.windowTextFontMain2.setText(_translate("MainWindow","Pokemon Listings"))
        self.windowTextFontSub.setText(_translate("MainWindow"," Modest     20               11     16     23               $5,000                   Just now            28 days                      Buy"))
        self.windowTextFontSub2.setText(_translate("MainWindow","Pokemon\t           Nature\t\tIVs\t\t            Price\t     Start Date          End Date\tBuy"))
        self.windowTextFontMinIV.setText(_translate("MainWindow","0"))
        self.windowTextFontMaxIV.setText(_translate("MainWindow","31"))
        self.windowTextFontButton1.setText(_translate("MainWindow","Item Market       Item Listings       Your Listings       Create Listing       Trade Log"))
        self.windowTextFontButton2.setText(_translate("MainWindow","Select Template\t\t\t\t\t\t\t          Advanced Search             ↻               Newest"))
        self.windowTextFontButton3.setText(_translate("MainWindow","Lv. 36 Evee"))
        self.windowTextFontButton4.setText(_translate("MainWindow","2         3         4         5         6         7         8         9        10       11       12      13       14       >>"))
        self.windowTextFontDisabled1.setText(_translate("MainWindow","☒"))
        self.windowTextFontDisabled2.setText(_translate("MainWindow","<<      1"))
        self.label_14.setText(_translate("MainWindow", "Berry Watering Colors"))
        self.label_12.setText(_translate("MainWindow", "waterBG\nwaterwarning\nberryprogress\nberrywarning\nberrydisabled"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.WindowColors), _translate("MainWindow", "Window Colors"))
        self.label_15.setText(_translate("MainWindow", "Cursor Type"))
        self.cursorBrowse.setText(_translate("MainWindow", "Browse..."))
        self.cursorEditButton.setText(_translate("MainWindow", "Edit"))
        self.label_17.setText(_translate("MainWindow", "Add Custom Cursor"))
        self.label_30.setText(_translate("MainWindow", "Edit Cursor Data"))
        self.label_20.setText(_translate("MainWindow", "Icon Type"))
        self.label_23.setText(_translate("MainWindow", "Speech Bubbles"))
        self.speechBrowse.setText(_translate("MainWindow", "Browse..."))
        self.label_24.setText(_translate("MainWindow", "Add Custom Speech Bubbles"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.OtherScreen), _translate("MainWindow", "Other"))
        self.label_25.setText(_translate("MainWindow", "Get/Update Archetype"))
        self.label_27.setText(_translate("MainWindow", "Set Mods Folder"))
        self.downloadArch.setText(_translate("MainWindow", "Download"))
        self.setModFolder.setText(_translate("MainWindow", "Browse..."))
        self.playPokemmo.setText(_translate("MainWindow", "Play Pokemmo"))
        self.modButtonLabel.setText(_translate("MainWindow","Mod List"))
        self.setGamePath.setText(_translate("MainWindow", "Browse..."))
        self.completeMod.setText(_translate("MainWindow", "Complete"))
        self.label_28.setText(_translate("MainWindow", "Finish and add to Pokemmo"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.Archetype), _translate("MainWindow", "Archetype"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.Mods), _translate("MainWindow", "Mods"))
        self.menuFile.setTitle(_translate("MainWindow", "File"))
        self.menuHelp.setTitle(_translate("MainWindow", "Help"))
        self.actionSave.setText(_translate("MainWindow", "Save"))
        self.actionExit.setText(_translate("MainWindow", "Exit"))
        self.actionLoad.setText(_translate("MainWindow", "Load"))
        self.actionSaveAs.setText(_translate("MainWindow","Save As..."))
        self.actionLoadDefault.setText(_translate("MainWindow", "Load Defaults"))
        self.actionAbout.setText(_translate("MainWindow","About"))

from colorButton import ColorButton as KColorButton


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    system_theme(app)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())
