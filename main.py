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

        self.toggleButton.clicked.connect(lambda: UIFunctions.toggleMenu(self, True))
        UIFunctions.uiDefinitions(self)

        self.menu_button_offset_grabber.setStyleSheet(UIFunctions.selectMenu(self.menu_button_offset_grabber.styleSheet()))

        # Access the QStackedWidget
        self.stacked_widget = self.findChild(QStackedWidget, "stackedWidget")  # Match the object name in Qt Designer
        self.config_system=None
        # Initialize individual pages
        self.init_pages()

        self.menu_buttons = [
        self.menu_button_offset_grabber,  # Replace with your actual button objects
        self.menu_button_menu_compiler,
    ]

        # Assign menu button clicks
        self.menu_button_offset_grabber.clicked.connect(lambda: self.handleMenuClick(self.menu_button_offset_grabber, 0))
        self.menu_button_menu_compiler.clicked.connect(lambda: self.handleMenuClick(self.menu_button_menu_compiler, 0))

    def init_pages(self):
        """Initialize backend logic for each page."""
        # Initialize ConfigSystem logic
        self.config_system = ConfigSystem(self)  # Assuming it's the first page


    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event):
        cs_file_path = None 
        for url in event.mimeData().urls():
            filename = url.toLocalFile()
            if os.path.isfile(filename):
                if filename.endswith('.csv'):
                    self.config_system.load_config(filename)
                elif filename.endswith('.cs'):
                    cs_file_path = filename 
                elif filename.endswith('.xml'):
                    self.offseth_textbox.setText(filename)
                elif filename.endswith('.cpp'):
                    self.maincpp_textbox.setText(filename)
                elif filename.endswith('.apk'):
                    self.config_system.handle_apk_drop(filename)
            elif os.path.isdir(filename):
                for root, dirs, files in os.walk(filename):
                    for file in files:
                        if file.endswith('.cs'):
                            cs_file_path = os.path.join(root, file)
                            break
                    if cs_file_path:
                        break
                else:
                    continue

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





    



if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    main_window = MainApp()
    main_window.show()
    sys.exit(app.exec_())
