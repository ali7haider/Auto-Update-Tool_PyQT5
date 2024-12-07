import subprocess
from PyQt5.QtCore import Qt
import json
import zipfile
import shutil
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
    QSettings,
    QDateTime
)
from PyQt5.QtGui import QFont, QDesktopServices,QColor

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
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QUrl
from PyQt5.QtWidgets import QWidget
import json
import os
import asyncio
import aiohttp
from bs4 import BeautifulSoup
import requests
import threading
import concurrent.futures
import traceback
import random
class GameUpdateChecker(QWidget):
    def __init__(self, ui_instance):
        super().__init__()  # Initialize QWidget
        self.ui = ui_instance

        #To push updates to the Trello Workspace Update Area
        self.api_key = '0c3a2f61fba8ce6628b9a4a93930da96clear'
        self.api_token = 'ATTA85534400a62dd5f9d2d1683eb497f6ff24140164014cd310594ba2418b07cc4e888EEADAclear'
        self.board_id = 'qaxNi23Mclear'
        self.list_id = '6346c426c8b0d4001ed9f0b1clear'
        self.user_id = '636a9e9cbd57dc0630bc97b2clear'
        self.check_button.clicked.connect(self.check_updates)
        self.clear_log_button_3.clicked.connect(self.clear_log)
        self.add_game_button.clicked.connect(self.add_game)
        self.check_thread = CheckThread()
        self.check_thread.update_signal.connect(self.update_result_log)
        self.check_thread.finish_signal.connect(self.finish_check)
    def __getattr__(self, name):
        """Delegate attribute access to the UI instance if not found in ConfigSystem."""
        return getattr(self.ui, name)
    def link_clicked(self, link):
        QDesktopServices.openUrl(QUrl(link))
        

    def clear_log(self):
        self.result_log.clear()



    def add_card_to_trello(self, card_name, card_description):
        # Card creation URL and parameters

        url = f"https://api.trello.com/1/cards"
        query = {
            'key': self.api_key,
            'token': self.api_token,
            'idList': self.list_id,
            'name': card_name,
            'desc': card_description
        }
        response = requests.post(url, params=query)
        
        if response.status_code == 200:
            card_id = response.json().get('id')
            print(f"Card '{card_name}' added to Trello.")
            
            # Add user to card
            if card_id:
                self.add_user_to_card(card_id, self.user_id)
        else:
            print(f"Failed to add card '{card_name}' to Trello: {response.text}")

    def add_user_to_card(self, card_id, user_id):
        # URL and parameters to add the user to the card

        url = f"https://api.trello.com/1/cards/{card_id}/idMembers"
        query = {
            'key': self.api_key,
            'token': self.api_token,
            'value': user_id
        }
        response = requests.post(url, params=query)
        
        if response.status_code == 200:
            print(f"User '{user_id}' added to card '{card_id}'.")
        else:
            print(f"Failed to add user '{user_id}' to card '{card_id}': {response.text}")

    def add_game(self):
        game_name = self.game_name_input.text()
        game_package = self.game_url_input.text()  

        if game_name and game_package:
            apkcombo_url = f"https://apkcombo.com/{game_package}/{game_package}/"
            apkpure_url = f"https://apkpure.net/{game_package}/{game_package}/"

            new_game = {
                "package": game_package,
                "version": "v1",
                "Apkcombo": apkcombo_url,
                "Apkpure": apkpure_url
            }
            oyunlar = self.load_oyunlar()
            oyunlar[game_name] = new_game
            self.save_oyunlar(oyunlar)
            self.game_name_input.clear()
            self.game_url_input.clear()

    def load_oyunlar(self):
        resource_tool_folder = os.path.join(os.path.expanduser('~'), 'Desktop', 'autoupdatetool', 'ResourceTool', 'txtcode')
        oyunlar_json_path = os.path.join(resource_tool_folder, 'oyunlar.json')

        try:
            with open(oyunlar_json_path, 'r') as file:
                oyunlar = json.load(file)
        except FileNotFoundError:
            oyunlar = {}
        return oyunlar

    def save_oyunlar(self, oyunlar):
        resource_tool_folder = os.path.join(os.path.expanduser('~'), 'Desktop', 'autoupdatetool', 'ResourceTool', 'txtcode')
        oyunlar_json_path = os.path.join(resource_tool_folder, 'oyunlar.json')

        with open(oyunlar_json_path, 'w') as file:
            json.dump(oyunlar, file, indent=4)

    def check_updates(self):
        oyunlar = self.load_oyunlar()
        self.check_thread.set_parameters(oyunlar)
        self.check_thread.update_signal.connect(self.update_result_log)
        self.check_thread.start()

    def update_result_log(self, message):
        game_name, apkcombo_version, apkpure_version = self.extract_game_name_and_versions(message)
        if game_name:
            current_version = self.get_current_version(game_name)
            if current_version:
                updated_version = None
                download_link = None

                if apkcombo_version and apkcombo_version != current_version:
                    updated_version = apkcombo_version
                    download_link = f"https://apkcombo.com/downloader/#package={self.get_game_package(game_name)}"
                    
                elif apkpure_version and apkpure_version != current_version:
                    updated_version = apkpure_version
                    url = f"https://apkpure.net/{self.get_game_package(game_name)}/{self.get_game_package(game_name)}/download"
                    response = requests.get(url)
                    soup = BeautifulSoup(response.content, 'html.parser')
                    if soup.find("a", title="XAPK"):
                        download_link = f"https://d.apkpure.com/b/XAPK/{self.get_game_package(game_name)}?version=latest"
                    elif soup.find("a", title="APK"):
                        download_link = f"https://d.apkpure.com/b/APK/{self.get_game_package(game_name)}?version=latest"


                if updated_version:
                    log_message = f"{game_name} {updated_version} <a style='color: green;' href=\"{download_link}\">Download</a>"
                    self.result_log.append(log_message)
                    self.update_game_version(game_name, updated_version)


                    # Create sanitized name for card title

                    cleaned_game_name = re.sub(r'\[.*?\]', '', game_name).strip()
                    card_name = f"{cleaned_game_name} {updated_version}"  # Game name and version number in card title
                    card_description = ""
                    if card_name:
                        self.add_card_to_trello(card_name, card_description)
            
    def extract_game_name_and_versions(self, message):
        parts = message.split(":")
        if len(parts) >= 2:
            game_name = parts[0].strip()
            apkcombo_version = None
            apkpure_version = None
            if "ApkCombo" in parts[1]:
                apkcombo_version = parts[1].split("ApkCombo")[1].strip().split(" ")[0]
            if "ApkPure" in parts[1]:
                apkpure_version = parts[1].split("ApkPure")[1].strip().split(" ")[0]
                
            return game_name, apkcombo_version, apkpure_version
            
        return None, None, None

    def get_game_package(self, game_name):
        oyunlar = self.load_oyunlar()
        game_info = oyunlar.get(game_name, None)
        if game_info:
            return game_info.get("package", None)
        return None

    def get_current_version(self, game_name):
        oyunlar = self.load_oyunlar()
        game_info = oyunlar.get(game_name, None)
        if game_info:
            return game_info.get("version", None)
        return None

    def update_game_version(self, game_name, version):
        oyunlar = self.load_oyunlar()
        if game_name in oyunlar:
            oyunlar[game_name]["version"] = version
            self.save_oyunlar(oyunlar)



    def extract_game_name_and_version(self, message):
        parts = message.split(" ")
        if len(parts) >= 3:
            game_name = " ".join(parts[:-1])
            version = parts[-1]
            return game_name, version
        return None, None

    def get_game_url(self, game_name):
        oyunlar = self.load_oyunlar()
        return oyunlar.get(game_name, None)


    def finish_check(self):
        self.result_log.append('\n')
        self.result_log.append("<font color='#66ff00'>Done</font>")
        



class CheckThread(QThread):
    update_signal = pyqtSignal(str)
    finish_signal = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.oyunlar = {}

    def set_parameters(self, oyunlar):
        self.oyunlar = oyunlar

    def run(self):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(self.run_async())

    def emit_signal(self, message):
        self.update_signal.emit(message)

    async def run_async(self):
        async with aiohttp.ClientSession() as session:
            tasks = [self.check_game_update(session, oyun, url) for oyun, url in self.oyunlar.items()]
            results = await asyncio.gather(*tasks)

            for result_message in results:
                if result_message:
                    self.emit_signal(result_message)

            self.emit_signal("All updates finished.")
            self.finish_signal.emit()

    async def check_game_update(self, session, oyun, url):
        apkcombo_version = None
        apkpure_version = None

        try:
            if "Apkcombo" in url:
                async with session.get(url["Apkcombo"]) as response:
                    response.raise_for_status()
                    html_content = await response.text()
                    soup = BeautifulSoup(html_content, 'lxml')
                    apkcombo_version = soup.select_one(
                        "#main > div.container > div > div.column.is-main > div.app_header.mt-14 > div.info > div.version"
                    )

                    if apkcombo_version:
                        apkcombo_version = apkcombo_version.text.strip()
                    else:
                        error_message = f"No version found for {oyun} on ApkCombo"
                        self.emit_signal(error_message)
                        print(error_message)
                        return None

            if "Apkpure" in url:
                await asyncio.sleep(random.uniform(20, 30))  # Here you can set the waiting time between 20-30 seconds
                async with session.get(url["Apkpure"], ssl=False) as response:
                    response.raise_for_status()
                    html_content = await response.text()
                    soup = BeautifulSoup(html_content, 'html.parser')

                    apkpure_element = soup.select_one(
                        "body > main > div.details.container > div.detail_top > div.detail_banner.detail_banner--exp > div.apk_info > div > p.details_sdk > span"
                    )

                    if apkpure_element:
                        apkpure_version = apkpure_element.text.strip()
                    else:
                        apkpure_element_alt = soup.select_one(
                            "body > main > section > div.information-box > div > div > div:nth-child(1) > div.additional-info"
                        )

                        if apkpure_element_alt:
                            apkpure_version = apkpure_element_alt.text.strip()
                        else:
                            error_message = f"No Apkpure version found for {oyun}"
                            self.emit_signal(error_message)
                            print(error_message)
                            return None

            if apkcombo_version and apkpure_version:
                if apkcombo_version != apkpure_version:
                    if apkcombo_version > apkpure_version:
                        return f"{oyun}: ApkCombo v{apkcombo_version}"
                    else:
                        return f"{oyun}: ApkPure v{apkpure_version}"
                else:
                    return f"{oyun}: ApkCombo v{apkcombo_version}"
            elif apkcombo_version:
                return f"{oyun}: ApkCombo v{apkcombo_version}"
            elif apkpure_version:
                return f"{oyun}: ApkPure v{apkpure_version}"

        except aiohttp.ClientResponseError as e:
            # URL geçersiz veya hata durumlarında
            error_message = f"HTTP Error {e.status} for {oyun}: {str(e)}"
            self.emit_signal(error_message)
            print(error_message)
            return None

        except aiohttp.ClientError as e:
            # Genel istemci hataları
            traceback_str = traceback.format_exc()
            error_message = f"Error occurred while checking game: {oyun}, Error: {e}"
            self.emit_signal(error_message)
            self.emit_signal(traceback_str)
            print(error_message)
            print(traceback_str)

            if isinstance(e, aiohttp.ClientConnectionError):
                retry_message = f"Connection reset. Retrying shortly."
                self.emit_signal(retry_message)
                print(retry_message)
                return await self.check_game_update(session, oyun, url)

            if response.status == 429:
                # 429 hatası alırsak, daha fazla bekleme süresi ekleyebiliriz
                retry_message = f"Too many requests. Retrying in 30 seconds."
                self.emit_signal(retry_message)
                print(retry_message)
                return await self.check_game_update(session, oyun, url)

            if response.status == 410:
                gone_message = f"{oyun}: URL no longer available (410 Gone)."
                self.emit_signal(gone_message)
                print(gone_message)
                return None

        return None

