import os
import zipfile
import shutil
import subprocess
# PyQt5 Imports
from PyQt5.QtCore import QTimer, QDateTime
from PyQt5.QtWidgets import (
    QWidget,
    QFileDialog,
    QMessageBox,
)

# Local Imports
from config_system import ConfigSystem

class MenuCompiler(QWidget):  # Inherit from QWidget
    service_def = ''  # sınıf değişkeni
    def __init__(self, ui_instance):
        super().__init__()  # Initialize QWidget
        self.ui = ui_instance
        self.config_system = ConfigSystem(self.ui) ## With for Offset Grabber Compile Menu
        self.apk_queue = [] 
        self.is_processing = False
        self.mainlaunch_add_button.clicked.connect(self.run_openmainactivity)
        self.openmanifest_add_button.clicked.connect(self.run_openmanifest)
        self.tfive_mod_button.clicked.connect(self.run_tfivelgl2)
        self.tfive2_mod_button.clicked.connect(self.run_tfivelgl3)
        self.tfive23_mod_button.clicked.connect(self.process_xapk)
        self.autodump_button.clicked.connect(self.run_autodump)
        self.updateradd_button.clicked.connect(self.updateradd)
        self.protectapk_button.clicked.connect(self.protectapk)
        self.compile_apk_button.clicked.connect(self.compile_apk)

        self.clear_log_button_2.clicked.connect(self.clear_log)
        self.signkill_button.clicked.connect(self.select_signkill_button)
        self.decompilenondex_button.clicked.connect(self.select_and_decompile_nondex_apk)
        #    Setting the dragEnterEvent and dropEvent
        self.drop_buttonMenu.dragEnterEvent = self.drop_buttonMenu_dragEnterEvent
        self.drop_buttonMenu.dropEvent = self.drop_buttonMenu_dropEvent
        self.current_file=None
        # Apktool programının yolu
        self.apktool_path = "./ResourceTool/jarcode/apktool.jar"
        self.setAcceptDrops(True)
        self.apkeditor_path = "./ResourceTool/jarcode/ApkEditor.jar"
        self.aapt2_path = os.path.join(os.getcwd(), 'ResourceTool', 'jarcode', 'aapt2')  # AAPT2 aracının yolu

        desktop_path = os.path.expanduser("~/Desktop")
        games_txt_path = os.path.join(desktop_path, "autoupdatetool", "ResourceTool", "txtcode", "games.txt")
        baksmali_jar_path = os.path.join(desktop_path, "autoupdatetool", "ResourceTool", "jarcode", "baksmali.jar")
        self.game_packages = self.load_game_packages(games_txt_path)
        self.baksmali_jar_path = baksmali_jar_path

        self.compile_timer = QTimer(self.ui)
        self.compile_timer.timeout.connect(self.update_compile_time)
        self.compile_start_time = None
    def __getattr__(self, name):
        """Delegate attribute access to the UI instance if not found in ConfigSystem."""
        return getattr(self.ui, name)
    def select_signkill_button(self):
        # Birden fazla APK seçimi
        options = QFileDialog.Options()
        options |= QFileDialog.ReadOnly
        apk_paths, _ = QFileDialog.getOpenFileNames(self, "APK'leri Seç", "", "APK Files (*.apk)", options=options)
        
        if not apk_paths:
            QMessageBox.warning(self, "Uyarı", "Hiçbir APK seçilmedi!")
            return
            pass


        
    def drop_buttonMenu_dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            event.ignore()


    def drop_buttonMenu_dropEvent(self, event):
        # Sürüklenen dosyaları al
        dropped_files = event.mimeData().urls()
        for file in dropped_files:
            apk_path = file.toLocalFile()
            print(f"Dropped file: {apk_path}")
            # APK dosyasını kuyruğa ekliyoruz
            self.apk_queue.append(apk_path)

        # Eğer şu anda işlem yapılmıyorsa ilk APK'yı işleme başla
        if not self.is_processing:
            self.process_next_apk()

    def process_next_apk(self):
        pass

    def start_decompile_apk(self, apk_path):
        pass

    def on_decompile_finished(self):
        pass


        

    def run_autodump(self):
        pass



    def process_xapk(self):
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getOpenFileName(self, "Select XAPK or APKS File", "", "XAPK Files (*.xapk);;APKS Files (*.apks)", options=options)
        
        pass

    def extract_xapk(self, file_path, extract_dir):
        with zipfile.ZipFile(file_path, 'r') as zip_ref:
            zip_ref.extractall(extract_dir)
    
    def find_base_apk(self, directory):
        apk_files = [os.path.join(directory, f) for f in os.listdir(directory) if f.endswith('.apk')]
        if not apk_files:
            return None

        for apk in apk_files:
            package_name = self.get_package_name(apk)
            if package_name:
                return apk
        return None

    def get_package_name(self, apk_file):
        process = subprocess.Popen([self.aapt2_path, 'dump', 'badging', apk_file], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output, error = process.communicate()
        if process.returncode != 0:
            return None
        
        for line in output.decode().splitlines():
            if line.startswith("package: name="):
                package_name = line.split("'")[1]
                return package_name
        return None

    def tfivedecompile(self, file_path, output_dir):
        pass


    def modify_manifest(self, manifest_path):
        pass

    def tfivecompile_ap(self, output_dir):
        pass

    
    def move_apk_to_extracted(self, output_dir, package_name):
        pass

    def create_xapk(self, original_xapk_path, extracted_dir, package_name):
        pass

    def cleanup(self, extracted_dir, decompiled_dir):
        if os.path.exists(extracted_dir):
            shutil.rmtree(extracted_dir)
        if os.path.exists(decompiled_dir):
            shutil.rmtree(decompiled_dir)
















    def protectapk(self):
        options = QFileDialog.Options()
        file_names, _ = QFileDialog.getOpenFileNames(self, "Select APK files", "", "APK Files (*.apk);;All Files (*)", options=options)
        pass



    def clear_log(self):
        self.log_text_2.clear()
        self.log_text2.clear()


    def select_and_decompile_nondex_apk(self):
        options = QFileDialog.Options()
        options |= QFileDialog.ReadOnly
        options |= QFileDialog.ExistingFiles
        file_dialog = QFileDialog(self, "Select APK file", "", "APK Files (*.apk)", options=options)
    def decompile_nondex_apk(self, file_path):
            def read_output():
                pass
    def get_package_name_from_manifest(self, manifest_file_path):
        pass



    def load_game_packages(self, games_txt_path):
        pass

    def apply_smali_file(self, output_dir, smali_file):
        pass
    def update_launch_activity_in_games_txt(self, package_name, launch_activity_name, smali_folder_name):
        pass
    def find_smali_folder_name(self, package_name, launch_activity_name, smali_folder):
        pass



    def get_launch_activity_name(self, output_dir, smali_output_dir_path):
        pass
        

    def get_apk_info(self, file_path):
        pass


                
    def compile_apk(self):
        # Masaüstü dizini
        pass


        
    def run_permission(self):
        pass
        
    def run_openmainactivity(self):
        pass

        
    def run_openmanifest(self):
        pass


    def compile_xapk(self, file_path):
        try:
            # .xapk veya .apks dosyasını APKEditor.jar ile .apk'ya çevir
            convert_process = subprocess.Popen(['java', '-jar', self.apkeditor_path, 'm', '-i', file_path], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            convert_process.communicate()  # İşlem tamamlanana kadar bekler
            return True  # Dönüşüm başarılı
        except subprocess.CalledProcessError as e:
            QMessageBox.critical(None, "XAPK/APKS to APK Error", f"Hata: {e}")
            return False  # Dönüşüm başarısız
        
            

    def decompile_apk(self, file_path):
        pass


            
    def update_compile_time(self):
        if self.compile_start_time:
            current_time = QDateTime.currentDateTime()
            elapsed_seconds = self.compile_start_time.secsTo(current_time)
            self.log_text_2.clear()  # Mevcut metni temizle
            self.log_text_2.setPlainText(f'{elapsed_seconds} İşlenen Süre')


    

        
    def open_manifest(self):
        pass

    def open_permission(self):
        pass

    def run_tfivelgl2(self):
        pass

    def run_tfivelgl3(self):
        pass
    def updateradd(self):
        pass