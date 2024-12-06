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

import resources_rc

GLOBAL_STATE = False
class MainApp(QMainWindow):
    def __init__(self):
        super().__init__()
        # Load the main UI
        uic.loadUi("main.ui", self)  # Replace with your main UI file
        from modules.ui_functions import UIFunctions
        self.ui=self

        self.toggleButton.clicked.connect(lambda: UIFunctions.toggleMenu(self, True))
        UIFunctions.uiDefinitions(self)

        self.menu_button_offset_grabber.setStyleSheet(UIFunctions.selectMenu(self.menu_button_offset_grabber.styleSheet()))

        # Access the QStackedWidget
        self.stacked_widget = self.findChild(QStackedWidget, "stackedWidget")  # Match the object name in Qt Designer

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
        self.offset_grabber_page = ConfigSystem(self)  # Assuming it's the first page


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


class APKProcessorThread(QThread):
    log_signal = pyqtSignal(str)
    success_signal = pyqtSignal(bool)

    def __init__(self, apk_path, config_system, parent=None):
        super().__init__(parent)
        self.apk_path = apk_path
        self.config_system = config_system
        self.processing_success = False

    def run(self):
        try:
            self.process_apk(self.apk_path)
            if self.processing_success:
                self.success_signal.emit(True)
            else:
                self.success_signal.emit(False)
        except Exception as e:
            self.log_signal.emit(f"İşlem sırasında hata oluştu: {str(e)}")
            self.success_signal.emit(False)

    def process_apk(self, apk_path):
        try:
            with zipfile.ZipFile(apk_path, 'r') as apk:
                libil2cpp_candidates = [
                    "lib/arm64-v8a/libil2cpp.so",
                    "lib/armeabi-v7a/libil2cpp.so",
                ]
                target_lib_folder = None

                package_name = self.get_package_name_from_apk(apk_path)
                if not package_name:
                    self.log_signal.emit("Package name alınamadı.")
                    return

                available_libs = [candidate.split('/')[1] for candidate in libil2cpp_candidates if candidate in apk.namelist()]

                if len(available_libs) > 1:
                    target_lib_folder = available_libs[0]
                elif len(available_libs) == 1:
                    target_lib_folder = available_libs[0]
                else:
                    self.log_signal.emit("APK içinde libil2cpp.so bulunamadı!")
                    return

                libil2cpp_path = f"lib/{target_lib_folder}/libil2cpp.so"
                if libil2cpp_path in apk.namelist():
                    self.libil2cpp_path = os.path.join(os.getcwd(), "libil2cpp.so")
                    with apk.open(libil2cpp_path) as source, open(self.libil2cpp_path, 'wb') as target:
                        target.write(source.read())

                metadata_candidate = "assets/bin/Data/Managed/Metadata/global-metadata.dat"
                if metadata_candidate in apk.namelist():
                    self.metadata_path = os.path.join(os.getcwd(), "global-metadata.dat")
                    with apk.open(metadata_candidate) as source, open(self.metadata_path, 'wb') as target:
                        target.write(source.read())
                else:
                    self.log_signal.emit("global-metadata.dat bulunamadı!")
                    return
                
                self.package_dir = os.path.join(os.getcwd(), "Il2CppDumper", package_name)
                os.makedirs(self.package_dir, exist_ok=True)

                if self.libil2cpp_path and self.metadata_path:
                    self.run_dumper(package_name, target_lib_folder)
                else:
                    self.log_signal.emit("Gerekli dosyalar bulunamadı!")
        except Exception as e:
            self.log_signal.emit(f"APK işlenirken hata oluştu: {str(e)}")

    def run_dumper(self, package_name, target_lib_folder):
        if not self.libil2cpp_path or not self.metadata_path:
            self.log_signal.emit("Eksik dosyalar var, işlem gerçekleştirilemiyor.")
            self.processing_success = False
            return
        
        exe_path = os.path.join(os.getcwd(), "Il2CppDumper", "Il2CppDumper.exe")
        if not os.path.exists(exe_path):
            self.processing_success = False
            return
        
        try:
            process = subprocess.Popen(
                [exe_path, self.libil2cpp_path, self.metadata_path],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )

            stdout, stderr = process.communicate()
            if process.returncode == 0:
                self.config_system.move_dump_to_package_folder(package_name, target_lib_folder)
                self.processing_success = True
            else:
                self.log_signal.emit(f"Hata oluştu: {stderr}")
                if "Dump Error Manual Try" in stderr:
                    self.processing_success = False 
                    self.log_signal.emit("Dump Error Manual Try hatası oluştu.")
                else:
                    self.processing_success = True

        except Exception as e:
            self.log_signal.emit(f"Hata: {str(e)}")
            self.processing_success = False

    def get_package_name_from_apk(self, apk_path):
        try:
            aapt2_path = os.path.join(os.path.expanduser("~"), "Desktop", "autoupdatetool", "aapt2.exe")
            result = subprocess.run([aapt2_path, "dump", "badging", apk_path], capture_output=True, text=True, encoding='utf-8')

            if result.returncode == 0:
                output = result.stdout
                if output is None or output.strip() == "":
                    raise Exception("aapt2 çıktısı boş veya None döndü")
                package_name_match = re.search(r"package: name='([^']+)'", output)
                if package_name_match:
                    package_name = package_name_match.group(1)
                    return package_name
                else:
                    raise Exception("APK içinde paket adı bulunamadı.")
            else:
                raise Exception(f"aapt2 komutu başarısız oldu. Çıkış kodu: {result.returncode}, Hata: {result.stderr}")
        except Exception as e:
            raise Exception(f"APK'den paket adı alınamadı: {e}")            


class ConfigSystem:
    def __init__(self, ui_instance):
        """Initialize with the UI instance of the page."""
        self.ui = ui_instance
        self.setAcceptDrops(True)

        self.libil2cpp_path = None
        self.metadata_path = None
        self.drop_button.dragEnterEvent = self.button_drag_enter_event
        self.drop_button.dropEvent = self.button_drop_event
        self.can_process = True
        self.processing_success = False
        self.apk_queue = []
        self.is_processing = False 
        self.ndkpath = ""
        self.workdir = ""
        settings = QSettings('MyOrganization', 'MyApplication')
        self.filename = settings.value('filename', '.', type=str)
        self.table_widget.itemSelectionChanged.connect(self.handle_item_selected)
        self.table_widget.keyPressEvent = self.handle_key_pressed

        # Kaydedilen son dosya yollarını al
        self.settings = QSettings('MyOrganization', 'MyApplication')
        self.last_maincpp_file_path = self.settings.value('last_maincpp_file_path', '', type=str)
        self.last_offset_file_path = self.settings.value('last_offset_file_path', '', type=str)

        # Load saved NDK Path if available
        self.load_setting()
        self.setup_table_widget()

        # Connect signals to slots
        self.ndk_browse_button.clicked.connect(self.browse_ndk)
        self.save_ndk_checkbox.toggled.connect(self.save_ndk_path)
        self.add_to_list_button.clicked.connect(self.add_to_table)
        self.load_config_button.clicked.connect(self.load_config)
        self.save_config_button.clicked.connect(self.save_config)
        #self.start_generation_button2.clicked.connect(self.start_generation2)
        self.clear_log_button.clicked.connect(self.clear_log)
        sys.stdout = self.LogStream(self.log_text)

        


      

    class LogStream(object):
        def __init__(self, text_edit):
            self.text_edit = text_edit

        def write(self, message):
            self.text_edit.insertPlainText(message)

        def flush(self):
            pass  # No action needed, just need to define the method

    def __getattr__(self, name):
        """Delegate attribute access to the UI instance if not found in ConfigSystem."""
        return getattr(self.ui, name)

    def load_setting(self):
        try:
            resource_tool_folder = os.path.join(os.path.expanduser('~'), 'Desktop', 'autoupdatetool', 'ResourceTool', 'txtcode')
            setup_file = os.path.join(resource_tool_folder, 'settingndkpath.json')

            if os.path.exists(setup_file):
                with open(setup_file, "r") as file:
                    settings = json.load(file)
                    self.ndkpath = settings.get("NDK Path", "")
                    if self.ndkpath:
                        self.ndk_textbox.setText(self.ndkpath)
        except Exception as e:
            print(f"Error loading settings: {e}")

    def browse_ndk(self):
        try:
            path = QFileDialog.getExistingDirectory(self.ui, "Select NDK Directory")  # Use self.ui as parent
            if path:
                self.ndk_textbox.setText(path)
        except Exception as e:
            print(f"Error browsing NDK: {e}")

    def save_ndk_path(self):
        try:
            resource_tool_folder = os.path.join(os.path.expanduser('~'), 'Desktop', 'autoupdatetool', 'ResourceTool', 'txtcode')
            self.ndkpath = self.ndk_textbox.text()

            if self.save_ndk_checkbox.isChecked():
                settings = {"NDK Path": self.ndkpath}
                setup_file = os.path.join(resource_tool_folder, 'settingndkpath.json')

                with open(setup_file, "w") as file:
                    json.dump(settings, file)
        except Exception as e:
            print(f"Error saving NDK Path: {e}")

    def add_to_table(self):
        try:
            classname_text = self.classname_textbox.text()
            method_text = self.method_textbox.text()

            if not any([classname_text, method_text]):
                QMessageBox.warning(self.ui, "Warning", "Please fill at least one row.")
            else:
                row_count = self.table_widget.rowCount()
                self.table_widget.insertRow(row_count)

                classname_item = QTableWidgetItem(classname_text)
                method_item = QTableWidgetItem(method_text)

                self.table_widget.setItem(row_count, 1, classname_item)
                self.table_widget.setItem(row_count, 2, method_item)
        except Exception as e:
            print(f"Error adding to table: {e}")
    def save_config(self):
        try:
            # Önceki kaydedilen dosya yolu yükleniyor
            settings = QSettings('MyOrganization', 'MyApplication')
            filename = settings.value('filename', '.', type=str)

            # Dosya yolunu sormak yerine, kaydedilen son dosya yolunu kullanıyoruz
            filename, _ = QFileDialog.getSaveFileName(self.ui, 'Save Configuration', filename, 'CSV Files (*.csv)')

            if filename:
                with open(filename, 'w') as file:
                    writer = csv.writer(file)
                    for row in range(self.table_widget.rowCount()):
                        row_data = []
                        for column in range(self.table_widget.columnCount()):
                            item = self.table_widget.item(row, column)
                            if item is not None:
                                row_data.append(item.text())
                            else:
                                row_data.append('')
                        writer.writerow(row_data)

                # Dosya yolu kaydediliyor
                settings.setValue('filename', filename)
        except Exception as e:
            print(e)
    def load_config(self, filename=''):
        try:
            if not filename:
                settings = QSettings('MyOrganization', 'MyApplication')
                filename = settings.value('filename', '.', type=str)

                file_dialog = QFileDialog()
                filename, _ = file_dialog.getOpenFileName(self.ui, "Open Config File", filename, "CSV Files (*.csv)")

            if filename:
                with open(filename, 'r') as file:
                    reader = csv.reader(file)
                    self.table_widget.setRowCount(0)
                    for row_data in reader:
                        if not any(row_data):
                            continue
                        self.table_widget.insertRow(self.table_widget.rowCount())
                        for column, text in enumerate(row_data):
                            self.table_widget.setItem(self.table_widget.rowCount()-1, column, QTableWidgetItem(text))

                settings = QSettings('MyOrganization', 'MyApplication')
                settings.setValue('filename', filename)
        except Exception as e:
            print(f"Error loading config: {e}")

    def setup_table_widget(self):
        try:
            header = self.table_widget.horizontalHeader()
            header.setSectionResizeMode(QHeaderView.Stretch)
            self.table_widget.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
            self.table_widget.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        except Exception as e:
            print(f"Error setting up table widget: {e}")

    def start_generation2(self):
        try:
            # Here is the Function of the Offset Grabber Button. If you add it, I will combine it.
            pass
        except Exception as e:
            print(f"Error in start_generation2: {e}")

    def clear_log(self):
        try:
            self.log_text.clear()
        except Exception as e:
            print(f"Error clearing log: {e}")

    def button_drag_enter_event(self, event):
        try:
            if event.mimeData().hasUrls():
                event.accept()
            else:
                event.ignore()
        except Exception as e:
            print(f"Error in drag enter event: {e}")

    def button_drop_event(self, event):
        try:
            for url in event.mimeData().urls():
                filename = url.toLocalFile()
                if filename.endswith('.apk'):
                    self.apk_queue.append(filename)
                    if not self.is_processing:
                        self.start_next_apk()
                else:
                    self.log_text.append(f"Geçersiz dosya sürüklendi: {filename}")
        except Exception as e:
            print(f"Error in drop event: {e}")

    def start_next_apk(self):
        try:
            if self.apk_queue:
                self.is_processing = True
                apk_path = self.apk_queue.pop(0)
                self.handle_apk_drop(apk_path)
                self.apk_thread = APKProcessorThread(apk_path, self.ui)
                self.apk_thread.log_signal.connect(self.log_text.append)
                self.apk_thread.success_signal.connect(self.on_apk_processed)
                self.apk_thread.start()
            else:
                self.is_processing = False
                self.show_completion_message()
        except Exception as e:
            print(f"Error starting next APK: {e}")

    def on_apk_processed(self, success):
        try:
            if success:
                self.log_text.append("APK işleme başarılı.")
            else:
                self.log_text.append("APK işleme sırasında hata oluştu.")
            
            QTimer.singleShot(0, self.start_next_apk)
        except Exception as e:
            print(f"Error on APK processed: {e}")

    def show_completion_message(self):
        try:
            QMessageBox.information(self, "Done", "All APKs Completed!")
        except Exception as e:
            print(f"Error showing completion message: {e}")

    def handle_item_selected(self):
        try:
            selected_items = self.table_widget.selectedItems()
            if selected_items:
                self.selected_row_index = selected_items[0].row()
        except Exception as e:
            print(f"Error handling item selected: {e}")

    def cppupdated(self):
        try:
            # Here is the Function of the CPP Update Button. If you add it, I will combine it.
            pass
        except Exception as e:
            print(f"Error in cppupdated: {e}")

    def xmlupdated(self):
        try:
            # Here is the Function of the Xml Update Button. If you add it, I will combine it.
            pass
        except Exception as e:
            print(f"Error in xmlupdated: {e}")

    def handle_key_pressed(self, event):
        try:
            if event.key() == Qt.Key_Delete:
                if hasattr(self, 'selected_row_index'):
                    self.table_widget.removeRow(self.selected_row_index)
        except Exception as e:
            print(f"Error handling key pressed: {e}")

    def add_to_table(self):
        try:
            classname_text = self.classname_textbox.text()
            method_text = self.method_textbox.text()

            if not any([classname_text, method_text]):
                QMessageBox.warning(self.ui, "Warning", "Please fill at least one row.")
            else:
                row_count = self.table_widget.rowCount()
                self.table_widget.insertRow(row_count)

                classname_item = QTableWidgetItem(classname_text)
                method_item = QTableWidgetItem(method_text)

                self.table_widget.setItem(row_count, 1, classname_item)
                self.table_widget.setItem(row_count, 2, method_item)
        except Exception as e:
            print(f"Error adding to table: {e}")





if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    main_window = MainApp()
    main_window.show()
    sys.exit(app.exec_())
