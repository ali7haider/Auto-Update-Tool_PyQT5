import subprocess
from PyQt5.QtCore import Qt
import json
from datetime import datetime
from xml.etree import ElementTree as ET
from PyQt5.QtWidgets import (
    QWidget,
    QFileDialog,
    QMessageBox,
    QTableWidgetItem,
    QHeaderView

)
from PyQt5.QtCore import (
    Qt,
    QTimer,
    QSettings
)
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import  QWidget, QTableWidgetItem, QFileDialog, QMessageBox
from PyQt5.QtWidgets import *
from PyQt5.QtWidgets import QHeaderView
from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import Qt, QTimer, QSettings
from PyQt5.QtGui import QColor
import subprocess
import csv
import os
import sys
import re
from PyQt5.QtGui import QColor
from PyQt5.QtGui import  QColor
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget
import json
import os
from apk_processor_thread import APKProcessorThread
class ConfigSystem(QWidget):  # Inherit from QWidget
    def __init__(self, ui_instance):
        super().__init__()  # Initialize QWidget
        self.ui = ui_instance
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
            QMessageBox.information(self.ui, "Done", "All APKs Completed!")
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

    def write_output(self, text, color=''):
        self.log_text.setTextColor(QColor(color))
        self.log_text.append(text)


    def maincppopen_file_dialog(self):
        pass


    def offsetopen_file_dialog(self):
        pass

           
    def handle_apk_drop(self, apk_path):
        try:
            package_name = self.get_package_name_from_apk(apk_path)
            cpp_file_path = self.find_matching_cpp_file(package_name)

            if cpp_file_path:
                self.maincpp_textbox.setText(cpp_file_path)
            else:
                QMessageBox.warning(self, "Uyarı", "Main.cpp dosyası bulunamadı")
            
            csv_file_path = self.find_matching_csv_file(package_name)
            if csv_file_path:
                self.load_config(csv_file_path)
            else:
                QMessageBox.warning(self, "Uyarı", "CSV dosyası yok")
        except Exception as e:
            QMessageBox.warning(self, "Uyarı", f"Paket adı alınamadı: {e}")
        
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
    def find_matching_cpp_file(self, package_name):
        desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
        autoupdatetool_path = os.path.join(desktop_path, "autoupdatetool")
        maincpp_data_path = os.path.join(autoupdatetool_path, "Main.cpp Data")

        # 'Main.cpp Data' dizinindeki .cpp dosyalarını tarayarak package ismiyle eşleşeni bul
        matching_cpp_file = None
        for root, dirs, files in os.walk(maincpp_data_path):
            for file in files:
                if file.endswith(".cpp") and package_name in file:
                    matching_cpp_file = os.path.join(root, file)
                    break
            if matching_cpp_file:
                break

        return matching_cpp_file

    def find_matching_csv_file(self, package_name):
        desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
        autoupdatetool_path = os.path.join(desktop_path, "autoupdatetool")
        grabber_taslak_path = os.path.join(autoupdatetool_path, "Grabber Taslak")

        # 'Grabber Taslak' dizinindeki .csv dosyalarını tarayarak package ismiyle eşleşeni bul
        matching_csv_file = None
        for root, dirs, files in os.walk(grabber_taslak_path):
            for file in files:
                if file.endswith(".csv") and package_name in file:
                    matching_csv_file = os.path.join(root, file)
                    break
            if matching_csv_file:
                break

        return matching_csv_file