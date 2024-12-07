import zipfile
import subprocess
from PyQt5.QtCore import QThread, pyqtSignal

from PyQt5.QtCore import (
    QThread,
    pyqtSignal,
)

import subprocess
import os
import re
from PyQt5.QtCore import  QThread, pyqtSignal
import os

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
