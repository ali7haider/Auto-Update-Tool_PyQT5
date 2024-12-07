import sys
import os
import re
import csv
import shutil
import binascii
import zipfile
import subprocess
from PyQt5.QtCore import QThread, pyqtSignal, QMetaObject, QVariant, Qt
import threading
import concurrent.futures
import traceback
import random
from PyQt5.QtCore import QEventLoop
from collections import deque
import mmap
import requests
import json
from datetime import datetime
from bs4 import BeautifulSoup
from xml.etree import ElementTree as ET
from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QFileDialog,
    QMessageBox,
    QTextEdit,
    QTableWidget,
    QTableWidgetItem,
    QTabWidget,
    QGridLayout,
    QMainWindow,
    QFrame,
    QHeaderView,
    QProgressDialog,
    QCheckBox,
)
from PyQt5.QtCore import (
    Qt,
    QMimeData,
    QRect,
    QTimer,
    QSettings,
    QDateTime,
    QThread,
    pyqtSignal,
)
from PyQt5.QtGui import QFont, QColor, QPainter, QPainterPath, QPen
from PyQt5 import QtCore
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QLabel, QTabWidget, QVBoxLayout, QTableWidget, QTableWidgetItem, QTextEdit, QFileDialog, QMessageBox, QGridLayout, QMainWindow, QFrame, QProgressDialog
from PyQt5.QtWidgets import QLineEdit
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QClipboard
from PyQt5.QtWidgets import QHeaderView
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QLineEdit, QPushButton, QListWidget
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QLineEdit, QPushButton, QListWidget, QCheckBox
from PyQt5.QtCore import Qt, QMimeData, QRect, QTimer, QSettings
from PyQt5.QtGui import QFont, QColor
from PyQt5 import QtCore
from datetime import datetime
import xml.etree.ElementTree as ET
import shutil
import threading
import subprocess
import csv
import os
import sys
import re
from PyQt5.QtGui import QColor
import time
from PyQt5.QtGui import QPalette, QColor
#from androguard.core.bytecodes.apk import APK
import asyncio
import aiohttp
from bs4 import BeautifulSoup
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QUrl
from PyQt5.QtWidgets import QMainWindow, QWidget, QLineEdit, QPushButton, QTextBrowser
from PyQt5.QtGui import QFont, QDesktopServices
import json
import os
from PyQt5.QtWidgets import QTextBrowser
from PyQt5 import uic
from config_system import ConfigSystem
from menu_compiler import MenuCompiler
from update_check import GameUpdateChecker
import resources_rc

GLOBAL_STATE = False
class MainApp(QMainWindow):
    def __init__(self):
        super().__init__()
        # Load the main UI
        uic.loadUi("main.ui", self)  # Replace with your main UI file
        from modules.ui_functions import UIFunctions
        self.ui=self
        self.setAcceptDrops(True)
        self.set_buttons_cursor()
        

        self.toggleButton.clicked.connect(lambda: UIFunctions.toggleMenu(self, True))
        UIFunctions.uiDefinitions(self)

        self.menu_button_offset_grabber.setStyleSheet(UIFunctions.selectMenu(self.menu_button_offset_grabber.styleSheet()))

        # Access the QStackedWidget
        self.stacked_widget = self.findChild(QStackedWidget, "stackedWidget")  # Match the object name in Qt Designer
        self.config_system=None
        self.menu_compiler=None
        # Initialize individual pages
        self.init_pages()

        self.menu_buttons = [
        self.menu_button_offset_grabber,  # Replace with your actual button objects
        self.menu_button_menu_compiler,
        self.menu_button_game_update,
    ]

        # Assign menu button clicks
        self.menu_button_offset_grabber.clicked.connect(self.show_config_system)
        self.menu_button_menu_compiler.clicked.connect(self.show_menu_compiler)
        self.menu_button_game_update.clicked.connect(self.show_game_update_menu)

    def init_pages(self):
        """Initialize backend logic for each page."""
        # Initialize ConfigSystem logic
        self.config_system = ConfigSystem(self)  # Assuming it's the first page
        self.menu_compiler = MenuCompiler(self)
        self.game_update_chceker= GameUpdateChecker(self)
        self.stackedWidget.setCurrentIndex(0)


    def show_config_system(self):
        self.current_page = self.config_system
        self.handleMenuClick(self.menu_button_offset_grabber, 0)

    def show_menu_compiler(self):
        self.current_page = self.menu_compiler
        self.handleMenuClick(self.menu_button_menu_compiler,2)
    def show_game_update_menu(self):
        self.current_page = self.game_update_chceker
        self.handleMenuClick(self.menu_button_game_update,3)
    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.accept()
        else:
            event.ignore()
    def dropEvent(self, event):
        """Handle drop event based on the active page."""
        if not event.mimeData().hasUrls():
            return event.ignore()

        for url in event.mimeData().urls():
            file_path = url.toLocalFile()

            if self.current_page == self.config_system:
                self.handle_config_system_drop(file_path)
            elif self.current_page == self.menu_compiler:
                self.handle_menu_compiler_drop(file_path)
            else:
                event.ignore()

    def handle_menu_compiler_drop(self, file_path):
        if file_path.endswith(".apk"):
            self.log_text_2.append(f"Dropped file: {file_path}")
            self.menu_compiler.current_file = file_path
            self.menu_compiler.decompile_apk(file_path)
        elif file_path.endswith((".xapk", ".apks")):
            self.log_text_2.append(f"Dropped file: {file_path}")
            self.menu_compiler.current_file = file_path
            self.menu_compiler.compile_xapk(file_path)
        else:
            QMessageBox.warning(None, "Hata", "Sadece APK, XAPK veya APKS Sürükle.")
    def handle_config_system_drop(self, file_path):
        """Handles a single file drop for the ConfigSystem page."""
        if os.path.isfile(file_path):
            if file_path.endswith('.csv'):
                self.config_system.load_config(file_path)
            elif file_path.endswith('.cs'):
                self.dump_path_textbox.setText(file_path)
            elif file_path.endswith('.xml'):
                self.offseth_textbox.setText(file_path)
            elif file_path.endswith('.cpp'):
                self.maincpp_textbox.setText(file_path)
            elif file_path.endswith('.apk'):
                self.config_system.handle_apk_drop(file_path)
        elif os.path.isdir(file_path):
            self.process_directory(file_path)

    def process_directory(self, directory):
        """Handles directory processing to locate .cs files."""
        cs_file_path = None
        for root, dirs, files in os.walk(directory):
            for file in files:
                if file.endswith('.cs'):
                    cs_file_path = os.path.join(root, file)
                    break
            if cs_file_path:
                break
        if cs_file_path:
            self.dump_path_textbox.setText(cs_file_path)
    def handleMenuClick(self, button, page_index):
        """
        Handles menu button clicks to update styles and switch pages.
        """
        from modules.ui_functions import UIFunctions

        # Deselect all buttons
        for btn in self.menu_buttons:
            btn.setStyleSheet(UIFunctions.deselectMenu(btn.styleSheet()))

        # Select the clicked button
        button.setStyleSheet(UIFunctions.selectMenu(button.styleSheet()))

        # Switch to the selected page
        self.stackedWidget.setCurrentIndex(page_index)


    def set_buttons_cursor(self):
        """Set the pointer cursor for all buttons in the UI."""
        buttons = self.findChildren(QPushButton)  # Find all QPushButton objects
        for button in buttons:
            button.setCursor(Qt.PointingHandCursor)


    



if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    main_window = MainApp()
    main_window.show()
    sys.exit(app.exec_())
