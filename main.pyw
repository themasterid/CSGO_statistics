import json
import sys
import requests
import os
from datetime import datetime
from PyQt5 import QtWidgets, QtCore
from res.mainwindows import Ui_MainWindow
from PyQt5.QtWidgets import QTableWidgetItem, QHeaderView
from res.codes import keys
from PyQt5.QtGui import QImage, QPixmap
import webbrowser
from get_steam_avatar import create_avatar
from datetime import date
from os import listdir
from os.path import isfile, join


text_not_found = '''
            Извините!\n
            При обработке вашего запроса произошла ошибка:\n
            Указанный профиль не найден.
            '''
no_info_users = '''
            Пользователь скрыл информацию, \n
            профиль является приватным.
            '''

steamid = keys['steamid']
key = keys['key']
steamidkey = keys['steamidkey']
#knowncode = keys['knowncode']

class MyWin(QtWidgets.QMainWindow):
    '''
    keys = {
    'steamid': 'XXXXXXXXXXXXXXXXX',
    'key': 'XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX',
    'steamidkey': 'XXXX-XXXX-XXXX',
    'knowncode': 'CSGO-xxxxx-xxxxx-xxxxx-xxxxx-xxxxx'
    }

    '''
    def __init__(self, parent=None):
        QtWidgets.QWidget.__init__(self, parent)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.steamid = steamid       
        self.pixmap_rank = QPixmap('img/ranks/skillgroup18.png')
        self.ui.label_rank.setPixmap(self.pixmap_rank)
        self.ui.lineEdit_steamidfind.setInputMask("99999999999999999;XXXXXXXXXXXXXXXXX")
        self.ui.lineEdit_steamidfind.setText('Введите Steam ID')
        
        self.check_vac_thread = CheckVacThread()
        self.check_friends_thread = CheckFriendsThread()
        self.check_weapons_thread = CheckWeaponsThread()

        self.ui.commandLinkButton_openurl.clicked.connect(self.click_avatar)
        self.ui.pushButton.clicked.connect(self.open_new_profile)
        self.ui.pushButton_my_profile.clicked.connect(self.open_my_profile)

        # STATS
        self.get_info_profile(self.steamid)
        self.ui.pushButton_update_stat.clicked.connect(self.get_statistics)
        self.ui.textBrowser_info.setText(self.get_table_statistics(self.steamid))

        # WEAPONS
        self.ui.pushButton_update_weapons.clicked.connect(self.on_start_weapons)
        #self.ui.pushButton_update_weapons.clicked.connect(self.on_stop_weapons)
        self.ui.comboBox_weapons.activated.connect(self.open_table_weapons)
        self.ui.comboBox_weapons.addItems(self.get_items_combobox_weapons())
        self.check_weapons_thread.list_all_weapons.connect(self.get_table_weapons, QtCore.Qt.QueuedConnection)
        # self.check_friends_thread.message_toolbar_friends.connect(self.on_change_check_friends, QtCore.Qt.QueuedConnection)

        # FRIENDS
        self.ui.pushButton_update_friends.clicked.connect(self.on_start_friends)
        #self.ui.pushButton_update_friends.clicked.connect(self.on_stop_friends)
        self.ui.comboBox_friends.activated.connect(self.open_table_friends)
        self.ui.comboBox_friends.addItems(self.get_items_combobox_friends())
        self.check_friends_thread.list_all_friends.connect(self.get_table_friends, QtCore.Qt.QueuedConnection)
        # self.check_friends_thread.message_toolbar_friends.connect(self.on_change_check_friends, QtCore.Qt.QueuedConnection)

        # MATCHES
        #self.ui.pushButton_update_matches.clicked.connect(self.update_users_names)
        self.ui.comboBox_matces.addItems(self.get_items_combobox_matches()) # заполняю даты матчей в список
        self.ui.comboBox_matces.activated.connect(self.get_info_match)

        # BANS
        self.ui.pushButton_update_bans_start.clicked.connect(self.on_start_vacs)
        self.ui.pushButton_update_bans_stop.clicked.connect(self.on_stop_vacs)
        self.ui.comboBox_bans.activated.connect(self.open_table_bans)
        self.ui.comboBox_bans.addItems(self.get_items_combobox_bans())
        self.check_vac_thread.list_all_users.connect(self.get_table_bans, QtCore.Qt.QueuedConnection)
        self.check_vac_thread.message_toolbar_bans.connect(self.on_change_check_vac, QtCore.Qt.QueuedConnection)
        self.check_vac_thread.int_for_progressbar_vac.connect(self.on_change_vac_rows, QtCore.Qt.QueuedConnection)
        self.ui.tableWidget_bans.itemClicked.connect(self.listwidgetclicked) # добавить проверку по строкам
        

    def open_my_profile(self):
        self.ui.tabWidget.setTabEnabled(1, True)
        self.ui.tabWidget.setTabEnabled(2, True)
        self.ui.tabWidget.setTabEnabled(3, True)
        self.ui.tabWidget.setTabEnabled(4, True)
        self.ui.pushButton_update_stat.setEnabled(True)
        self.pixmap_rank = QPixmap('img/ranks/skillgroup1.png')
        self.ui.label_rank.setPixmap(self.pixmap_rank)
        self.steamid = steamid
        self.get_info_profile(self.steamid)
        self.ui.textBrowser_info.setText(self.get_table_statistics(self.steamid))
        return

    def listwidgetclicked(self, item):
        print('Clicked {}'.format(item.text()))
        self.url = f"https://steamcommunity.com/profiles/{item.text()}"
        webbrowser.open(self.url)

    def get_items_combobox_friends(self):
        self.today = date.today()
        self.today_date = self.today.strftime("%b-%d-%Y")
        self.dir_path = 'all_friends'
        self.onlyfiles = [self.f for self.f in listdir(f'date/{self.dir_path}/{self.steamid}/') if isfile(join(f'date/{self.dir_path}/{self.steamid}/', self.f))]
        self.friends_list_files = []
        for self.files_i in self.onlyfiles:
            self.friends_list_files.append(self.files_i.split('.')[0])
        return self.friends_list_files

    def get_items_combobox_weapons(self):
        self.today = date.today()
        self.today_date = self.today.strftime("%b-%d-%Y")
        self.dir_path = 'all_weapons'
        self.onlyfiles = [self.f for self.f in listdir(f'date/{self.dir_path}/{self.steamid}/') if isfile(join(f'date/{self.dir_path}/{self.steamid}/', self.f))]
        self.weapons_list_files = []
        for self.files_i in self.onlyfiles:
            self.weapons_list_files.append(self.files_i.split('.')[0])
        return self.weapons_list_files

    def get_items_combobox_bans(self):
        self.today = date.today()
        self.today_date = self.today.strftime("%b-%d-%Y")
        self.dir_path = 'all_bans'
        self.onlyfiles = [self.f for self.f in listdir(f'date/{self.dir_path}/{self.steamid}/') if isfile(join(f'date/{self.dir_path}/{self.steamid}/', self.f))]
        self.ban_list_files = []
        for self.files_i in self.onlyfiles:
            self.ban_list_files.append(self.files_i.split('.')[0])
        return self.ban_list_files

    def open_table_weapons(self):
        self.index_weapons = self.ui.comboBox_weapons.currentIndex()
        self.ui.tableWidget_weapons.clear()
        self.date_weapons = self.open_json_file(f'date/all_weapons/{steamid}/{self.weapons_list_files[self.index_weapons]}.json')
        self.ui.tableWidget_weapons.setColumnCount(len(self.date_weapons[0]))
        self.ui.tableWidget_weapons.setRowCount(len(self.date_weapons))
        self.ui.tableWidget_weapons.setHorizontalHeaderLabels((
                'Оружие',
                'Точность',
                'Летальность',
                'Убийства',
                'Попадания',
                'Выстрелы',
                '% от всех\nубийств'
                ))

        rows_list = []
        for _ in range(len(self.date_weapons)):
            rows_list.append(str(_ + 1))
        
        self.ui.tableWidget_weapons.setVerticalHeaderLabels(rows_list)

        row = 0
        for tup in self.date_weapons:
            col = 0
            for item in tup:
                cellinfo = QTableWidgetItem(item)
                cellinfo.setFlags(
                    QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled
                )
                self.ui.tableWidget_weapons.setItem(row, col, cellinfo)
                col += 1
            row += 1

        self.ui.tableWidget_weapons.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.ui.tableWidget_weapons.resizeColumnsToContents()
        self.ui.tableWidget_weapons.resizeRowsToContents()
        self.ui.tableWidget_weapons.setSortingEnabled(True)
        return

    def open_table_friends(self):
        self.index_friends = self.ui.comboBox_friends.currentIndex()
        self.ui.tableWidget_friends.clear()
        self.friend_info = self.open_json_file(f'date/all_friends/{steamid}/{self.friends_list_files[self.index_friends]}.json')
        self.ui.tableWidget_friends.setColumnCount(len(self.friend_info[0])) # 7
        self.ui.tableWidget_friends.setRowCount(len(self.friend_info)) # 37
        self.ui.tableWidget_friends.setGridStyle(3)
        self.ui.tableWidget_friends.setHorizontalHeaderLabels(
            ('Игрок', '█████', '█████', '█████', '█████', '█████', '█████')
            )
        
        # add index rows 1,2,3,4...
        rows_list = []
        for _ in range(len(self.friend_info)):
            rows_list.append(str(_ + 1))
        self.ui.tableWidget_friends.setVerticalHeaderLabels(rows_list)
        
        row = 0
        for tup in self.friend_info:            
            col = 0
            for item in tup:
                cellinfo = QTableWidgetItem(item)
                cellinfo.setFlags(
                    QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled
                )
                self.ui.tableWidget_friends.setItem(row, col, cellinfo)
                col += 1
            row += 1

        self.ui.tableWidget_friends.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.ui.tableWidget_friends.resizeColumnsToContents()
        self.ui.tableWidget_friends.resizeRowsToContents()
        self.ui.tableWidget_friends.setSortingEnabled(True)
        return

    def get_table_bans(self, list_vacs):
        self.today = date.today()
        self.today_date = self.today.strftime("%b-%d-%Y")                
        with open(f'date/all_bans/{steamid}/{self.today_date}.json', 'w', encoding='utf-8') as self.file_all_bans:
            json.dump(list_vacs, self.file_all_bans, ensure_ascii=False, indent=4)
            self.file_all_bans.close()
        return

    def get_table_weapons(self, list_weapons):
        self.today = date.today()
        self.today_date = self.today.strftime("%b-%d-%Y")        
        with open(f'date/all_weapons/{steamid}/{self.today_date}.json', 'w', encoding='utf-8') as self.file_all_bans:
            json.dump(list_weapons, self.file_all_bans, ensure_ascii=False, indent=4)
            self.file_all_bans.close()
        return

    def get_table_friends(self, list_friends):
        self.today = date.today()
        self.today_date = self.today.strftime("%b-%d-%Y")        
        with open(f'date/all_friends/{steamid}/{self.today_date}.json', 'w', encoding='utf-8') as self.file_all_bans:
            json.dump(list_friends, self.file_all_bans, ensure_ascii=False, indent=4)
            self.file_all_bans.close()
        return

    def open_table_bans(self):
        self.index = self.ui.comboBox_bans.currentIndex()
        self.ui.tableWidget_bans.clear()
        all_users = self.open_json_file(f'date/all_bans/{steamid}/{self.ban_list_files[self.index]}.json')
        self.ui.tableWidget_bans.setColumnCount(len(all_users[0]))
        self.ui.tableWidget_bans.setRowCount(len(all_users))
        self.ui.tableWidget_bans.setGridStyle(3)
        self.ui.tableWidget_bans.selectedItems()
        self.ui.tableWidget_bans.setHorizontalHeaderLabels(
            ('Стим ИД', 'Имя', 'Бан в\nсообществе','VAC\nбан','Число\nVAC\nбанов','Дней в\nбане','Число\nигровых\nбанов','Бан\nторговой'))

        rows_list = []
        for _ in range(len(all_users)):
            rows_list.append(str(_ + 1))
        self.ui.tableWidget_weapons.setVerticalHeaderLabels(rows_list)

        row = 0
        for tup in all_users:
            col = 0
            for item in tup:
                cellinfo = QTableWidgetItem(item)
                cellinfo.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)
                self.ui.tableWidget_bans.setItem(row, col, cellinfo)
                col += 1
            row += 1

        self.ui.tableWidget_bans.resizeColumnsToContents()
        self.ui.tableWidget_bans.resizeRowsToContents()
        self.ui.tableWidget_bans.setSortingEnabled(True)
        return

    def update_users_names(self):
        self.today = date.today()
        self.today_date = self.today.strftime("%b-%d-%Y")
        # добавить информацию в файл all_stats.json после добавления нового матча с /gcpd/730/?tab=matchhistorycompetitive
        self.file_match_users = 'all_stats/all_stats.json'
        self.date_match_users = self.open_json_file(self.file_match_users)
        self.index_match = self.ui.comboBox_matces.currentIndex()
        self.list_steamids, self.list_player_files, self.date_name_users = [], [], []
        for _ in range(len(self.date_match_users[str(self.index_match)]['Team' + str(self.index_match)]) - 1):
            self.ui.progressBar_bans.setMaximum(len(self.date_match_users[str(self.index_match)]['Team' + str(self.index_match)]) - 1)
            self.ui.progressBar_bans.setProperty("value", _)
            self.list_steamids.append(self.date_match_users[str(self.index_match)]['Team' + str(self.index_match)][_ + 1]['steamid64'])
            self.list_player_files.append(f'date/{self.list_steamids[_]}/{self.list_steamids[_]}_profile_info_{self.today_date}.json')
            self.date_name_users.append(self.open_json_file(self.list_player_files[_], self.list_player_files[_])['response']['players'][0]['personaname'])
            self.date_match_users[str(self.index_match)]['Team' + str(self.index_match)][_ + 1]['PlayerName'][0] = self.date_name_users[_]
        
        self.write_json_file(self.date_match_users, self.file_match_users)

    def get_profile_test(self, steamid):
        # FIX THISE NAME SELF
        self.today = date.today()
        self.today_date = self.today.strftime("%b-%d-%Y")
        self.steamid = steamid
        self.steamid_profile_json = f'date/{self.steamid}/{self.steamid}_profile_info_{self.today_date}.json'
        self.url_profile_info = f'https://api.steampowered.com/ISteamUser/GetPlayerSummaries/v2/?key={key}&steamids={self.steamid}'
        self.directory = f"{self.steamid}"
        self.parent_dir = "date\\"
        self.path = os.path.join(self.parent_dir, self.directory)        
        try:
            os.mkdir(self.path)
        except FileExistsError:
            pass

        try:
            open(f'date/{self.steamid}/{self.steamid}_profile_info_{self.today_date}.json', 'r')
        except FileNotFoundError:
            #self.statusBar().showMessage('1. Файл не на диске, Качаю с сервера Valve! Записываю на диск.')
            #print(f'Файл date/{self.steamid}/{self.steamid}_profile_info_{self.today_date}.json не на диске, Качаю с сервера Valve! Записываю на диск.')
            self.req_profile_info = requests.get(self.url_profile_info).json()
            self.write_json_file(self.req_profile_info, self.steamid_profile_json)                     
            #  communityvisibilitystate
            #  1 - the profile is not visible to you (Private, Friends Only, etc),
            #  3 - the profile is "Public", and the data is visible.
            if self.req_profile_info['response']['players'] == []:
                self.write_json_file('deleted', f'date/deleted_/{self.steamid}_deleted_profile_info_{self.today_date}.json') 
                return 0
            # FIX OUTPUT DATA
            if self.req_profile_info['response']['players'][0]['communityvisibilitystate'] == 1:
                self.write_json_file(self.req_profile_info, self.steamid_profile_json)
                return self.open_json_file(self.steamid_profile_json)
            elif self.req_profile_info['response']['players'][0]['communityvisibilitystate'] == 3:
                self.write_json_file(self.req_profile_info, self.steamid_profile_json)
                return self.open_json_file(self.steamid_profile_json)
        
        if os.path.exists(f'date/{self.steamid}/{self.steamid}_profile_info_{self.today_date}.json'):
            #print(f'Файл date/{self.steamid}/{self.steamid}_profile_info_{self.today_date}.json на диске, пропускаю! Считываю c диска.')            
            #self.statusBar().showMessage('Файл на диске, пропускаю! Считываю c диска.')       
            return self.open_json_file(self.steamid_profile_json) 

    def get_info_match(self):
        self.today = date.today()
        self.today_date = self.today.strftime("%b-%d-%Y")
        self.file_all_mathes = 'all_stats/all_stats.json'
        self.date_match = self.open_json_file(self.file_all_mathes)
        self.index = self.ui.comboBox_matces.currentIndex()

        self.competitive = 'Карта ' + self.date_match[str(self.index)]['Competitive']
        self.date = 'Дата ' + self.date_match[str(self.index)]['date']
        self.waittime = 'Время ожидания ' + self.date_match[str(self.index)]['WaitTime']
        self.matchduration = 'Время игры ' + self.date_match[str(self.index)]['MatchDuration']
        self.score = 'Счет ' + self.date_match[str(self.index)]['Team' + str(self.index)][0]['score']
        self.score_center = self.date_match[str(self.index)]['Team' + str(self.index)][0]['score']
        
        # FIX add all maps
        if self.date_match[str(self.index)]['Competitive'] == 'de_engage':
            pixmap = QPixmap('img/imgs_maps/de_engage.jpg')
            self.ui.label_image_map.setPixmap(pixmap)
        else:
            pixmap = QPixmap('img/imgs_maps/de_inferno.jpg')
            self.ui.label_image_map.setPixmap(pixmap)

        self.steamid_i = []
        self.name_i = []
        self.player_name_i= []
        for self._ in range(10):
            self.ui.progressBar_bans.setMaximum(9)            
            self.ui.progressBar_bans.setProperty("value", self._)
            self.steamid_i.append(self.date_match[str(self.index)]['Team' + str(self.index)][self._ + 1]['steamid64'])
            self.name_i.append(self.get_profile_test(self.steamid_i[self._])['response']['players'][0]['personaname'])
            create_avatar(self.steamid_i[self._])
            self.player_name_i.append(self.date_match[str(self.index)]['Team' + str(self.index)][self._ + 1]['PlayerName'])

        self.ui.label_competitive.setText(self.competitive)
        self.ui.label_date.setText(self.date)
        self.ui.label_waittime.setText(self.waittime)
        self.ui.label_matchduration.setText(self.matchduration)
        self.ui.label_score.setText(self.score)

        if int(self.score_center.split(':')[0]) < int(self.score_center.split(':')[1]):
            self.score_center = 'Проиграли ' + self.score_center + ' Выиграли'
        elif int(self.score_center.split(':')[0]) > int(self.score_center.split(':')[1]):
            self.score_center = 'Выиграли ' + self.score_center + ' Проиграли'
        elif int(self.score_center.split(':')[0]) == int(self.score_center.split(':')[1]):
            self.score_center = 'Ничья ' + self.score_center + ' Ничья'

        self.ui.label_csore_center.setText(self.score_center)

        self.ui.label_playername1_avatar.setPixmap(QPixmap(f"date/{self.steamid_i[0]}/{self.steamid_i[0]}_avatarmedium_{self.today_date}.jpg"))
        self.ui.label_playername2_avatar.setPixmap(QPixmap(f"date/{self.steamid_i[1]}/{self.steamid_i[1]}_avatarmedium_{self.today_date}.jpg"))
        self.ui.label_playername3_avatar.setPixmap(QPixmap(f"date/{self.steamid_i[2]}/{self.steamid_i[2]}_avatarmedium_{self.today_date}.jpg"))
        self.ui.label_playername4_avatar.setPixmap(QPixmap(f"date/{self.steamid_i[3]}/{self.steamid_i[3]}_avatarmedium_{self.today_date}.jpg"))
        self.ui.label_playername5_avatar.setPixmap(QPixmap(f"date/{self.steamid_i[4]}/{self.steamid_i[4]}_avatarmedium_{self.today_date}.jpg"))
        self.ui.label_playername6_avatar.setPixmap(QPixmap(f"date/{self.steamid_i[5]}/{self.steamid_i[5]}_avatarmedium_{self.today_date}.jpg"))
        self.ui.label_playername7_avatar.setPixmap(QPixmap(f"date/{self.steamid_i[6]}/{self.steamid_i[6]}_avatarmedium_{self.today_date}.jpg"))
        self.ui.label_playername8_avatar.setPixmap(QPixmap(f"date/{self.steamid_i[7]}/{self.steamid_i[7]}_avatarmedium_{self.today_date}.jpg"))
        self.ui.label_playername9_avatar.setPixmap(QPixmap(f"date/{self.steamid_i[8]}/{self.steamid_i[8]}_avatarmedium_{self.today_date}.jpg"))
        self.ui.label_playername10_avatar.setPixmap(QPixmap(f"date/{self.steamid_i[9]}/{self.steamid_i[9]}_avatarmedium_{self.today_date}.jpg"))

        self.ui.label_playername1.setText(self.name_i[0])
        self.ui.label_playername2.setText(self.name_i[1])
        self.ui.label_playername3.setText(self.name_i[2])
        self.ui.label_playername4.setText(self.name_i[3])
        self.ui.label_playername5.setText(self.name_i[4])
        self.ui.label_playername6.setText(self.name_i[5])
        self.ui.label_playername7.setText(self.name_i[6])
        self.ui.label_playername8.setText(self.name_i[7])
        self.ui.label_playername9.setText(self.name_i[8])
        self.ui.label_playername10.setText(self.name_i[9])

        self.ui.label_pping1.setText(self.player_name_i[0][1])
        self.ui.label_pping2.setText(self.player_name_i[1][1])
        self.ui.label_pping3.setText(self.player_name_i[2][1])
        self.ui.label_pping4.setText(self.player_name_i[3][1])
        self.ui.label_pping5.setText(self.player_name_i[4][1])
        self.ui.label_pping6.setText(self.player_name_i[5][1])
        self.ui.label_pping7.setText(self.player_name_i[6][1])
        self.ui.label_pping8.setText(self.player_name_i[7][1])
        self.ui.label_pping9.setText(self.player_name_i[8][1])
        self.ui.label_pping10.setText(self.player_name_i[9][1])

        self.ui.label_kk1.setText(self.player_name_i[0][2])
        self.ui.label_kk2.setText(self.player_name_i[1][2])
        self.ui.label_kk3.setText(self.player_name_i[2][2])
        self.ui.label_kk4.setText(self.player_name_i[3][2])
        self.ui.label_kk5.setText(self.player_name_i[4][2])
        self.ui.label_kk6.setText(self.player_name_i[5][2])
        self.ui.label_kk7.setText(self.player_name_i[6][2])
        self.ui.label_kk8.setText(self.player_name_i[7][2])
        self.ui.label_kk9.setText(self.player_name_i[8][2])
        self.ui.label_kk10.setText(self.player_name_i[9][2])

        self.ui.label_aa1.setText(self.player_name_i[0][3])
        self.ui.label_aa2.setText(self.player_name_i[1][3])
        self.ui.label_aa3.setText(self.player_name_i[2][3])
        self.ui.label_aa4.setText(self.player_name_i[3][3])
        self.ui.label_aa5.setText(self.player_name_i[4][3])
        self.ui.label_aa6.setText(self.player_name_i[5][3])
        self.ui.label_aa7.setText(self.player_name_i[6][3])
        self.ui.label_aa8.setText(self.player_name_i[7][3])
        self.ui.label_aa9.setText(self.player_name_i[8][3])
        self.ui.label_aa10.setText(self.player_name_i[9][3])

        self.ui.label_dd1.setText(self.player_name_i[0][4])
        self.ui.label_dd2.setText(self.player_name_i[1][4])
        self.ui.label_dd3.setText(self.player_name_i[2][4])
        self.ui.label_dd4.setText(self.player_name_i[3][4])
        self.ui.label_dd5.setText(self.player_name_i[4][4])
        self.ui.label_dd6.setText(self.player_name_i[5][4])
        self.ui.label_dd7.setText(self.player_name_i[6][4])
        self.ui.label_dd8.setText(self.player_name_i[7][4])
        self.ui.label_dd9.setText(self.player_name_i[8][4])
        self.ui.label_dd10.setText(self.player_name_i[9][4])

        self.ui.label_mmvp1.setText(self.player_name_i[0][5])
        self.ui.label_mmvp2.setText(self.player_name_i[1][5])
        self.ui.label_mmvp3.setText(self.player_name_i[2][5])
        self.ui.label_mmvp4.setText(self.player_name_i[3][5])
        self.ui.label_mmvp5.setText(self.player_name_i[4][5])
        self.ui.label_mmvp6.setText(self.player_name_i[5][5])
        self.ui.label_mmvp7.setText(self.player_name_i[6][5])
        self.ui.label_mmvp8.setText(self.player_name_i[7][5])
        self.ui.label_mmvp9.setText(self.player_name_i[8][5])
        self.ui.label_mmvp10.setText(self.player_name_i[9][5])

        self.ui.label_hhsp1.setText(self.player_name_i[0][6])
        self.ui.label_hhsp2.setText(self.player_name_i[1][6])
        self.ui.label_hhsp3.setText(self.player_name_i[2][6])
        self.ui.label_hhsp4.setText(self.player_name_i[3][6])
        self.ui.label_hhsp5.setText(self.player_name_i[4][6])
        self.ui.label_hhsp6.setText(self.player_name_i[5][6])
        self.ui.label_hhsp7.setText(self.player_name_i[6][6])
        self.ui.label_hhsp8.setText(self.player_name_i[7][6])
        self.ui.label_hhsp9.setText(self.player_name_i[8][6])
        self.ui.label_hhsp10.setText(self.player_name_i[9][6])

        self.ui.label_sscore1.setText(self.player_name_i[0][7])
        self.ui.label_sscore2.setText(self.player_name_i[1][7])
        self.ui.label_sscore3.setText(self.player_name_i[2][7])
        self.ui.label_sscore4.setText(self.player_name_i[3][7])
        self.ui.label_sscore5.setText(self.player_name_i[4][7])
        self.ui.label_sscore6.setText(self.player_name_i[5][7])
        self.ui.label_sscore7.setText(self.player_name_i[6][7])
        self.ui.label_sscore8.setText(self.player_name_i[7][7])
        self.ui.label_sscore9.setText(self.player_name_i[8][7])
        self.ui.label_sscore10.setText(self.player_name_i[9][7])

        return

    def get_items_combobox_matches(self):
        self.file_allstats = 'all_stats/all_stats.json'
        self.match_items_data = self.open_json_file(self.file_allstats)
        self.match_items = []
        for _ in range(len(self.match_items_data)):
            self.match_items.append(str(_ + 1) + ") " + self.match_items_data[str(_)]['date'])
        return self.match_items

    def get_statistics(self):
        self.steamid = self.steamid
        self.get_info_profile(self.steamid)
        tmp_text_all = self.get_table_statistics(self.steamid)
        self.ui.textBrowser_info.setText(tmp_text_all)
   
    def get_info_profile(self, steamid):        
        self.today = date.today()
        self.today_date = self.today.strftime("%b-%d-%Y")
        # _{self.today_date}
        self.steamid = steamid
        self.url_profile_info = f'https://api.steampowered.com/ISteamUser/GetPlayerSummaries/v2/?key={key}&steamids={self.steamid}'
        self.check_profile(self.steamid)

        self.directory = f"{self.steamid}"
        self.parent_dir = "date\\"
        self.path = os.path.join(self.parent_dir, self.directory)
        try:
            os.mkdir(self.path)
        except FileExistsError:
            pass

        try:
            open(f'date/{self.steamid}/{self.steamid}_profile_info_{self.today_date}.json', 'r')
        except FileNotFoundError:
            self.req_profile_info = requests.get(self.url_profile_info).json()            
            #  communityvisibilitystate
            #  1 - the profile is not visible to you (Private, Friends Only, etc),
            #  3 - the profile is "Public", and the data is visible.
            if self.req_profile_info['response']['players'][0]['communityvisibilitystate'] == 1:
                self.statusBar().showMessage(
                    'The profile is not visible to you (Private, Friends Only, etc)')
                self.steamid_profile_json = f'date/{self.steamid}/{self.steamid}_profile_info_{self.today_date}.json'
                self.profile_data_json = self.write_json_file(self.req_profile_info, self.steamid_profile_json)
            elif self.req_profile_info['response']['players'][0]['communityvisibilitystate'] == 3:
                self.statusBar().showMessage(
                    'The profile is "Public", and the data is visible')
                self.steamid_profile_json = f'date/{self.steamid}/{self.steamid}_profile_info_{self.today_date}.json'
                self.profile_data_json = self.write_json_file(self.req_profile_info, self.steamid_profile_json)
        
        create_avatar(self.steamid)
        self.steamidprofile_json = f'date/{self.steamid}/{self.steamid}_profile_info_{self.today_date}.json'
        self.profile_data_json = self.open_json_file(self.steamidprofile_json)
        
        #  0 - Offline, 1 - Online, 2 - Busy, 3 - Away, 4 - Snooze, 5 - looking to trade, 6 - looking to play
        #request_status = requests.get(self.url_profile_info).json()
        self.personastate = self.profile_data_json['response']['players'][0]['personastate']
        #  1 - the profile is not visible to you (Private, Friends Only, etc),
        #  3 - the profile is "Public", and the data is visible.
        self.communityvisibilitystate = self.profile_data_json['response']['players'][0]['communityvisibilitystate']
        
        if self.communityvisibilitystate == 1:
            self.statusBar().showMessage(
                '1 - the profile is not visible to you (Private, Friends Only, etc)')
            
            #self.ui.label_playername1_avatar.setPixmap(QPixmap(f"date/{self.steamid}/{self.steamid}_avatarfull.jpg"))
            #image = QImage()
            #image.loadFromData(requests.get(profile_data_json['response']['players'][0]['avatarfull']).content)
            #self.ui.label_avatar.setPixmap(QPixmap(image))
            self.ui.label_avatar.setPixmap(QPixmap(f"date/{self.steamid}/{self.steamid}_avatarfull_{self.today_date}.jpg"))
            self.ui.label_personaname.setText(self.profile_data_json['response']['players'][0]['personaname'] + ' (Приватный профиль)')
            return
        elif self.communityvisibilitystate == 3:
            self.statusBar().showMessage(
                '3 - the profile is "Public", and the data is visible')
            if self.personastate == 1:
                self.online_status = " (Online)"
            elif self.personastate == 2:
                self.online_status = " (Online - Занят)"
            elif self.personastate == 3:
                self.online_status = " (Online - Отошел)"
            elif self.personastate == 4:
                self.online_status = " (Online - Спит)"
            elif self.personastate == 5:
                self.online_status = " (Online - Готов к обмену)"
            elif self.personastate == 6:
                self.online_status = " (Online - Готов играть)"
            else:
                self.online_status = " (Offline)"

            #image = QImage()
            #image.loadFromData(requests.get(profile_data_json['response']['players'][0]['avatarfull']).content)
            #self.ui.label_avatar.setPixmap(QPixmap(image))
            self.ui.label_avatar.setPixmap(QPixmap(f"date/{self.steamid}/{self.steamid}_avatarfull_{self.today_date}.jpg"))
            self.ui.label_personaname.setText(self.profile_data_json['response']['players'][0]['personaname'] + self.online_status)
            
            try:
                self.ui.label_realname.setText(
                                            self.profile_data_json['response']['players'][0]['realname'])
            except KeyError:
                self.ui.label_realname.setText('██████████')

            self.ui.label_profileurl.setText(self.profile_data_json['response']['players'][0]['profileurl'])            
            self.get_country_info(self.steamid)
            return self.profile_data_json

    def get_country_info(self, steamid):
        self.today = date.today()
        self.today_date = self.today.strftime("%b-%d-%Y")
        # _{self.today_date}
        self.steamid = steamid
        self.text_location = ""
        self.load_from_file = f'date/{self.steamid}/{self.steamid}_profile_info_{self.today_date}.json'
        self.load_location_from_file_1 = f'date/{self.steamid}/{self.steamid}_profile_location_1_{self.today_date}.json'
        self.load_location_from_file_2 = f'date/{self.steamid}/{self.steamid}_profile_location_2_{self.today_date}.json'
        self.load_location_from_file_3 = f'date/{self.steamid}/{self.steamid}_profile_location_3_{self.today_date}.json'

        self.url_profile_info = f'https://api.steampowered.com/ISteamUser/GetPlayerSummaries/v2/?key={key}&steamids={self.steamid}'
        self.directory = f"{self.steamid}"
        self.parent_dir = "date"
        self.path = os.path.join(self.parent_dir, self.directory)
        try:
            os.mkdir(self.path)
        except FileExistsError:
            pass

        try:
            open(self.load_from_file, 'r')
        except FileNotFoundError:
            self.req_profile = requests.get(self.url_profile_info).json()
            self.write_json_file(self.req_profile, self.load_from_file)
            self.profile_data_json = self.open_json_file(self.load_from_file) 
            self.text_location = ''

        try:
            open(self.load_location_from_file_1, 'r')
        except FileNotFoundError:
            self.req_profile = requests.get(self.url_profile_info).json()
            self.write_json_file(self.req_profile, self.load_from_file)
            self.profile_data_json = self.open_json_file(self.load_from_file)


        try:                            
            self.loccountrycode = self.profile_data_json['response']['players'][0]['loccountrycode']
            self.location_all_1 = f'https://steamcommunity.com/actions/QueryLocations/'
            self.location_req_1 = requests.get(self.location_all_1).json()
            self.write_json_file(self.location_req_1, self.load_location_from_file_1)
            self.location_file_1 = self.open_json_file(self.load_location_from_file_1)
            for _ in self.location_file_1:
                if _['countrycode'] == self.loccountrycode:
                    self.text_location += _['countryname'] + ', '
        except KeyError:
            self.text_location += '██████████'
            self.ui.label_loccountrycode.setText(self.text_location)
            return self.text_location

        try:
            self.req_profile = requests.get(self.url_profile_info).json()
            self.locstatecode = self.req_profile['response']['players'][0]['locstatecode']
            self.location_url_2 = f'https://steamcommunity.com/actions/QueryLocations/{self.loccountrycode}/'
            self.location_req_2 = requests.get(self.location_url_2).json()
            self.write_json_file(self.location_req_2, self.load_location_from_file_2)
            self.location_file_2 = self.open_json_file(self.load_location_from_file_2) 
            for _ in self.location_file_2:
                if _['statecode'] == self.locstatecode:
                    self.text_location += _['statename'] + ', '
        except KeyError:
            self.text_location +=  '██████████'
            self.ui.label_loccountrycode.setText(self.text_location)
            return self.text_location
        
        try:
            self.loccityid = self.req_profile['response']['players'][0]['loccityid']
            self.location_url_3 = f'https://steamcommunity.com/actions/QueryLocations/{self.loccountrycode}/{self.locstatecode}'
            self.location_req_3 = requests.get(self.location_url_3).json()
            self.write_json_file(self.location_req_3, self.load_location_from_file_3)
            self.location_file_3 = self.open_json_file(self.load_location_from_file_3) 
            for _ in self.location_file_3:
                if _['cityid'] == self.loccityid:
                    self.text_location += _['cityname']
            self.ui.label_loccountrycode.setText(self.text_location)
            return self.text_location
        except KeyError:
            self.text_location += '██████████'
            self.ui.label_loccountrycode.setText(self.text_location)
            #return self.text_location

        # OpenFromFiles on Disc
        self.profile_data_json = self.open_json_file(self.load_from_file) 
        self.text_location = ''

        try:
            self.loccountrycode = self.profile_data_json['response']['players'][0]['loccountrycode']
            self.location_file_1 = self.open_json_file(self.load_location_from_file_1)
            for _ in self.location_file_1:
                if _['countrycode'] == self.loccountrycode:
                    self.text_location += _['countryname'] + ', '
        except KeyError:
            self.text_location += '██████████'
            self.ui.label_loccountrycode.setText(self.text_location)
            return self.text_location

        try:
            self.locstatecode = self.profile_data_json['response']['players'][0]['locstatecode']
            self.location_file_2 = self.open_json_file(self.load_location_from_file_2)
            for _ in self.location_file_2:
                if _['statecode'] == self.locstatecode:
                    self.text_location += _['statename'] + ', '
        except KeyError:
            self.text_location +=  '██████████'
            self.ui.label_loccountrycode.setText(self.text_location)
            return self.text_location
        try:
            self.loccityid = self.profile_data_json['response']['players'][0]['loccityid']
            self.location_file_3 = self.open_json_file(self.load_location_from_file_3)
            for _ in self.location_file_3:
                if _['cityid'] == self.loccityid:
                    self.text_location += _['cityname']
            self.ui.label_loccountrycode.setText(self.text_location)
            return self.text_location
        except KeyError:
            self.text_location += '██████████'
            self.ui.label_loccountrycode.setText(self.text_location)
        return self.text_location

    def get_table_statistics(self, steamid):
        self.today = date.today()
        self.today_date = self.today.strftime("%b-%d-%Y")
        create_avatar(self.steamid) # create and get avatars for additional players from Valve servers
        self.steamid = steamid
        self.file_profile_info = f'date/{self.steamid}/{self.steamid}_profile_info_{self.today_date}.json'
        self.url_profile_stat = f'https://api.steampowered.com/ISteamUser/GetPlayerSummaries/v2/?key={key}&steamids={self.steamid}'
        self.tmp_text_all = ''

        try:
            open(self.file_profile_info, 'r')
        except FileNotFoundError:
            self.file_profile_info_req = requests.get(self.url_profile_stat).json()
            self.write_json_file(self.file_profile_info_req, self.file_profile_info)            

        if self.open_json_file(self.file_profile_info)['response']['players'] == []:
            self.tmp_text_all = text_not_found
            self.statusBar().showMessage(f'ERR: 404 Not found!')
            return self.tmp_text_all
                   
        #  communityvisibilitystate  
        #  1 - the profile is not visible to you (Private, Friends Only, etc),  
        #  3 - the profile is "Public", and the data is visible.
        self.file_profile_info_json = self.open_json_file(self.file_profile_info)
        if self.file_profile_info_json['response']['players'][0]['communityvisibilitystate'] == 1:
            self.statusBar().showMessage(
                'The profile is not visible to you (Private, Friends Only, etc)')
            self.steamid_profile_json = f'date/{self.steamid}/{self.steamid}_profile_info_{self.today_date}.json'
            self.profile_data_json = self.open_json_file(self.steamid_profile_json)
            self.tmp_text_all = no_info_users
            return self.tmp_text_all
        elif self.file_profile_info_json['response']['players'][0]['communityvisibilitystate'] == 3:
            self.statusBar().showMessage(
                'The profile is "Public", and the data is visible')
            self.steamid_profile_json = f'date/{self.steamid}/{self.steamid}_profile_info_{self.today_date}.json'
            self.open_json_file(self.steamid_profile_json)
        
        self.steamidprofile_json = f'date/{self.steamid}/{self.steamid}_profile_info_{self.today_date}.json'
        self.profile_data_json = self.open_json_file(self.steamidprofile_json)
        
        #  0 - Offline, 1 - Online, 2 - Busy, 3 - Away, 4 - Snooze, 5 - looking to trade, 6 - looking to play
        self.personastate = self.file_profile_info_json[
            'response']['players'][0]['personastate']
        #  1 - the profile is not visible to you (Private, Friends Only, etc),
        #  3 - the profile is "Public", and the data is visible.
        self.communityvisibilitystate = self.file_profile_info_json['response']['players'][0]['communityvisibilitystate']
        
        if self.communityvisibilitystate == 1:
            self.statis_profile = "Закрытый"
            self.statusBar().showMessage('The profile is not visible to you (Private, Friends Only, etc)')
            # FIX THIS ADD AVATAR FROM DISC           
            self.image = QImage()
            self.image.loadFromData(requests.get(self.profile_data_json['response']['players'][0]['avatarfull']).content)
            self.ui.label_avatar.setPixmap(QPixmap(self.image))
            self.ui.label_personaname.setText(self.profile_data_json['response']['players'][0]['personaname'] + ' (Приватный профиль)')
            self.tmp_text_all = no_info_users
            return self.tmp_text_all
        elif self.communityvisibilitystate == 3:
            self.statis_profile = "Открытый"
            self.statusBar().showMessage(
                'The profile is "Public", and the data is visible')
            if self.personastate == 1:
                self.online_status = " (Online)"
            elif self.personastate == 2:
                self.online_status = " (Online - Занят)"
            elif self.personastate == 3:
                self.online_status = " (Online - Отошел)"
            elif self.personastate == 4:
                self.online_status = " (Online - Спит)"
            elif self.personastate == 5:
                self.online_status = " (Online - Готов к обмену)"
            elif self.personastate == 6:
                self.online_status = " (Online - Готов играть)"
            else:
                self.online_status = " (Offline)"

        self.tmp_text_all += 'Стим ID - ' + self.profile_data_json['response']['players'][0]['steamid'] + "\n"
        self.tmp_text_all += 'Статус профиля - ' + self.statis_profile + "\n"
        self.tmp_text_all += 'Статус Steam - ' + self.online_status + "\n"
        self.tmp_text_all += 'Никнейм - ' + str(self.profile_data_json['response']['players'][0]['personaname']) + "\n"
        self.tmp_text_all += 'Ссылка на профиль - ' + str(self.profile_data_json['response']['players'][0]['profileurl']) + "\n"
        try:
            self.tmp_text_all += 'Последний раз выходил - ' + str(datetime.fromtimestamp(self.profile_data_json['response']['players'][0]['lastlogoff'])) + "\n"
        except KeyError:
            self.tmp_text_all += 'Последний раз выходил - ' + '██████████' + "\n"
        try:
            self.tmp_text_all += 'Реальное имя - ' + str(self.profile_data_json['response']['players'][0]['realname']) + "\n"
        except KeyError:
            self.tmp_text_all += 'Реальное имя - ' + '██████████' + "\n"
        self.tmp_text_all += 'Дата создания профиля - ' + str(datetime.fromtimestamp(self.profile_data_json['response']['players'][0]['timecreated'])) + "\n"
        self.tmp_text_all += 'Страна - ' + self.ui.label_loccountrycode.text() + "\n"

        return self.tmp_text_all

    def open_new_profile(self):
        self.steamid = self.ui.lineEdit_steamidfind.text()
        try:
            int(self.steamid)
        except:
            self.statusBar().showMessage(
                'Not INT')
            return
        
        self.ui.label_realname.setText('')
        self.ui.label_profileurl.setText('')
        self.ui.label_loccountrycode.setText('')
        if self.check_profile(self.steamid) == 0:
            return
        self.get_info_profile(self.steamid)
        #self.get_statistics
        self.ui.textBrowser_info.setText(self.get_table_statistics(self.steamid))        
        #self.date_weapons = self.get_info_weapons(self.steamid)
        #self.get_table_weapons(self.date_weapons) 
        return self.steamid

    def check_profile(self, steamid):
        self.steamid = steamid
        self.url_profile_info = f'https://api.steampowered.com/ISteamUser/GetPlayerSummaries/v2/?key={key}&steamids={self.steamid}'
        
        if requests.get(self.url_profile_info).json()['response']['players'] == []:
            pixmap = QPixmap('img/error.jpg')
            self.ui.label_avatar.setPixmap(pixmap)
            self.ui.label_rank.setPixmap(pixmap)
            self.ui.label_personaname.setText('██████████')
            self.ui.label_realname.setText('██████████')
            self.ui.label_profileurl.setText('https://steamcommunity.com/')
            self.ui.label_loccountrycode.setText('██████████')
            self.statusBar().showMessage(f'ERR: Profile Not Found!')
            tmp_text_all = text_not_found
            self.ui.textBrowser_info.setText(tmp_text_all)
            self.ui.tabWidget.setTabEnabled(1, False)
            self.ui.tabWidget.setTabEnabled(2, False)
            self.ui.tabWidget.setTabEnabled(3, False)
            self.ui.tabWidget.setTabEnabled(4, False)
            self.ui.pushButton_update_stat.setEnabled(False)
            return 0

    def click_avatar(self):
        webbrowser.open(self.ui.label_profileurl.text())

    def write_json_file(self, date_to_write, fname):
        self.date_to_write = date_to_write
        self.fname = fname
        with open(self.fname, 'w', encoding='utf-8') as self.write_json_file_:
            json.dump(self.date_to_write, self.write_json_file_,
                      ensure_ascii=False, indent=4)
            self.write_json_file_.close()
        return self.date_to_write

    def open_json_file(self, fname):
        self.fname = fname
        try:
            open(self.fname, 'r', encoding='utf-8')
        except FileNotFoundError:
            print('ERR: file not found:', fname)
        with open(self.fname, 'r', encoding='utf-8') as self.read_json_file:
            self.data_json = json.load(self.read_json_file)
            self.read_json_file.close()
        return self.data_json

    # WEAPONS
    def on_start_weapons(self):
        if not self.check_weapons_thread.isRunning():
            self.check_weapons_thread.start()

    def on_stop_weapons(self):
        self.check_weapons_thread.running = False

    def on_change_check_weapons(self, weapons_info):
        self.statusBar().showMessage(f'{weapons_info}')

    # FRIENDS
    def on_start_friends(self):
        if not self.check_friends_thread.isRunning():
            self.check_friends_thread.start()

    def on_stop_friends(self):
        self.check_friends_thread.running = False

    def on_change_check_friends(self, friends_info):
        self.statusBar().showMessage(f'{friends_info}')

    # VACS
    def on_start_vacs(self):
        if not self.check_vac_thread.isRunning():
            self.check_vac_thread.start()

    def on_stop_vacs(self):
        self.check_vac_thread.running = False

    def on_change_check_vac(self, vac_info):
        self.statusBar().showMessage(f'{vac_info}')

    def on_change_vac_rows(self, info_progress_bar_vac, all_users):
        self.info_progress_bar_vac = info_progress_bar_vac
        self.all_users = all_users
        self.ui.progressBar_bans.setMaximum(self.all_users)
        self.ui.progressBar_bans.setProperty("value", self.info_progress_bar_vac)

    def closeEvent(self, event):
        self.hide()
        self.check_vac_thread.running = False
        self.check_vac_thread.wait(5000)
        event.accept()

class CheckWeaponsThread(QtCore.QThread, MyWin):
    list_all_weapons = QtCore.pyqtSignal(list)

    def __init__(self, parent=None):        
        QtCore.QThread.__init__(self, parent)
        self.running = False
        self.today = date.today()
        self.today_date = self.today.strftime("%b-%d-%Y")

    def run(self):        
        self.steamid = steamid
        self.weapons_info = self.get_info_weapons(self.steamid)
        if self.weapons_info == [('', '', '', '', '', '', '')]:
            return 
        today = date.today()
        today_date = today.strftime("%b-%d-%Y")
        with open(f'date/all_weapons/{self.steamid}/{today_date}.json', 'w', encoding='utf-8') as self.file_all_weapons:
            json.dump(self.weapons_info, self.file_all_weapons, ensure_ascii=False, indent=4)
            self.file_all_weapons.close()        
        
        self.list_all_weapons.emit(self.weapons_info)

    def get_info_weapons(self, steamid):
        self.steamid = steamid
        self.url_profile_info = f'https://api.steampowered.com/ISteamUser/GetPlayerSummaries/v2/?key={key}&steamids={self.steamid}'
        if requests.get(self.url_profile_info).json()[
            'response']['players'][0]['communityvisibilitystate'] == 1:
            self.date_weapons = [('', '', '', '', '', '', '')]
            return self.date_weapons
        total_ksh_ak47 = [
            self.find_key_by_value('total_kills_ak47', self.steamid),
            self.find_key_by_value('total_shots_ak47', self.steamid),
            self.find_key_by_value('total_hits_ak47', self.steamid)]

        total_ksh_aug = [
            self.find_key_by_value('total_kills_aug', self.steamid),
            self.find_key_by_value('total_shots_aug', self.steamid),
            self.find_key_by_value('total_hits_aug', self.steamid)]

        total_ksh_awp = [
            self.find_key_by_value('total_kills_awp', self.steamid),
            self.find_key_by_value('total_shots_awp', self.steamid),
            self.find_key_by_value('total_hits_awp', self.steamid)]

        total_ksh_awp = [
            self.find_key_by_value('total_kills_awp', self.steamid),
            self.find_key_by_value('total_shots_awp', self.steamid),
            self.find_key_by_value('total_hits_awp', self.steamid)]

        total_ksh_deagle = [
            self.find_key_by_value('total_kills_deagle', self.steamid),
            self.find_key_by_value('total_shots_deagle', self.steamid),
            self.find_key_by_value('total_hits_deagle', self.steamid)]

        total_ksh_elite = [
            self.find_key_by_value('total_kills_elite', self.steamid),
            self.find_key_by_value('total_shots_elite', self.steamid),
            self.find_key_by_value('total_hits_elite', self.steamid)]

        total_ksh_famas = [
            self.find_key_by_value('total_kills_famas', self.steamid),
            self.find_key_by_value('total_shots_famas', self.steamid),
            self.find_key_by_value('total_hits_famas', self.steamid)]

        total_ksh_fiveseven = [
            self.find_key_by_value('total_kills_fiveseven', self.steamid),
            self.find_key_by_value('total_shots_fiveseven', self.steamid),
            self.find_key_by_value('total_hits_fiveseven', self.steamid)]

        total_ksh_g3sg1 = [
            self.find_key_by_value('total_kills_g3sg1', self.steamid),
            self.find_key_by_value('total_shots_g3sg1', self.steamid),
            self.find_key_by_value('total_hits_g3sg1', self.steamid)]

        total_ksh_galilar = [
            self.find_key_by_value('total_kills_galilar', self.steamid),
            self.find_key_by_value('total_shots_galilar', self.steamid),
            self.find_key_by_value('total_hits_galilar', self.steamid)]

        total_ksh_glock = [
            self.find_key_by_value('total_kills_glock', self.steamid),
            self.find_key_by_value('total_shots_glock', self.steamid),
            self.find_key_by_value('total_hits_glock', self.steamid)]

        total_ksh_m249 = [
            self.find_key_by_value('total_kills_m249', self.steamid),
            self.find_key_by_value('total_shots_m249', self.steamid),
            self.find_key_by_value('total_hits_m249', self.steamid)]

        total_ksh_m4a1 = [
            self.find_key_by_value('total_kills_m4a1', self.steamid),
            self.find_key_by_value('total_shots_m4a1', self.steamid),
            self.find_key_by_value('total_hits_m4a1', self.steamid)]

        total_ksh_mac10 = [
            self.find_key_by_value('total_kills_mac10', self.steamid),
            self.find_key_by_value('total_shots_mac10', self.steamid),
            self.find_key_by_value('total_hits_mac10', self.steamid)]

        total_ksh_mag7 = [
            self.find_key_by_value('total_kills_mag7', self.steamid),
            self.find_key_by_value('total_shots_mag7', self.steamid),
            self.find_key_by_value('total_hits_mag7', self.steamid)]

        total_ksh_mp7 = [
            self.find_key_by_value('total_kills_mp7', self.steamid),
            self.find_key_by_value('total_shots_mp7', self.steamid),
            self.find_key_by_value('total_hits_mp7', self.steamid)]

        total_ksh_mp9 = [
            self.find_key_by_value('total_kills_mp9', self.steamid),
            self.find_key_by_value('total_shots_mp9', self.steamid),
            self.find_key_by_value('total_hits_mp9', self.steamid)]

        total_ksh_negev = [
            self.find_key_by_value('total_kills_negev', self.steamid),
            self.find_key_by_value('total_shots_negev', self.steamid),
            self.find_key_by_value('total_hits_negev', self.steamid)]

        total_ksh_nova = [
            self.find_key_by_value('total_kills_nova', self.steamid),
            self.find_key_by_value('total_shots_nova', self.steamid),
            self.find_key_by_value('total_hits_nova', self.steamid)]

        total_ksh_hkp2000 = [
            self.find_key_by_value('total_kills_hkp2000', self.steamid),
            self.find_key_by_value('total_shots_hkp2000', self.steamid),
            self.find_key_by_value('total_hits_hkp2000', self.steamid)]

        total_ksh_p250 = [
            self.find_key_by_value('total_kills_p250', self.steamid),
            self.find_key_by_value('total_shots_p250', self.steamid),
            self.find_key_by_value('total_hits_p250', self.steamid)]

        total_ksh_p90 = [
            self.find_key_by_value('total_kills_p90', self.steamid),
            self.find_key_by_value('total_shots_p90', self.steamid),
            self.find_key_by_value('total_hits_p90', self.steamid)]

        total_ksh_bizon = [
            self.find_key_by_value('total_kills_bizon', self.steamid),
            self.find_key_by_value('total_shots_bizon', self.steamid),
            self.find_key_by_value('total_hits_bizon', self.steamid)]

        total_ksh_sawedoff = [
            self.find_key_by_value('total_kills_sawedoff', self.steamid),
            self.find_key_by_value('total_shots_sawedoff', self.steamid),
            self.find_key_by_value('total_hits_sawedoff', self.steamid)]

        total_ksh_scar20 = [
            self.find_key_by_value('total_kills_scar20', self.steamid),
            self.find_key_by_value('total_shots_scar20', self.steamid),
            self.find_key_by_value('total_hits_scar20', self.steamid)]

        total_ksh_sg556 = [
            self.find_key_by_value('total_kills_sg556', self.steamid),
            self.find_key_by_value('total_shots_sg556', self.steamid),
            self.find_key_by_value('total_hits_sg556', self.steamid)]

        total_ksh_ssg08 = [
            self.find_key_by_value('total_kills_ssg08', self.steamid),
            self.find_key_by_value('total_shots_ssg08', self.steamid),
            self.find_key_by_value('total_hits_ssg08', self.steamid)]

        total_ksh_tec9 = [
            self.find_key_by_value('total_kills_tec9', self.steamid),
            self.find_key_by_value('total_shots_tec9', self.steamid),
            self.find_key_by_value('total_hits_tec9', self.steamid)]

        total_ksh_ump45 = [
            self.find_key_by_value('total_kills_ump45', self.steamid),
            self.find_key_by_value('total_shots_ump45', self.steamid),
            self.find_key_by_value('total_hits_ump45', self.steamid)]

        total_ksh_xm1014 = [
            self.find_key_by_value('total_kills_xm1014', self.steamid),
            self.find_key_by_value('total_shots_xm1014', self.steamid),
            self.find_key_by_value('total_hits_xm1014', self.steamid)]

        total_summ = sum(
            [
                total_ksh_ak47[0],
                total_ksh_aug[0],
                total_ksh_awp[0],
                total_ksh_deagle[0],
                total_ksh_elite[0],
                total_ksh_famas[0],
                total_ksh_fiveseven[0],
                total_ksh_g3sg1[0],
                total_ksh_galilar[0],
                total_ksh_glock[0],
                total_ksh_m249[0],
                total_ksh_m4a1[0],
                total_ksh_mac10[0],
                total_ksh_mag7[0],
                total_ksh_mp7[0],
                total_ksh_mp9[0],
                total_ksh_negev[0],
                total_ksh_nova[0],
                total_ksh_hkp2000[0],
                total_ksh_p250[0],
                total_ksh_p90[0],
                total_ksh_bizon[0],
                total_ksh_sawedoff[0],
                total_ksh_scar20[0],
                total_ksh_sg556[0],
                total_ksh_ssg08[0],
                total_ksh_tec9[0],
                total_ksh_ump45[0],
                total_ksh_xm1014[0]
            ]
        )

        self.date_weapons = [(
            'AK-47',
            str(round(total_ksh_ak47[2] / total_ksh_ak47[1] * 100, 2)) + "%",
            str(round(total_ksh_ak47[0] / total_ksh_ak47[2] * 100, 2)) + "%",
            str(total_ksh_ak47[0]),
            str(total_ksh_ak47[2]),
            str(total_ksh_ak47[1]),
            str(round(total_ksh_ak47[0] / total_summ * 100, 2)) + "%"),
            ('AUG',
             str(round(total_ksh_aug[2] / total_ksh_aug[1] * 100, 2)) + "%",
             str(round(total_ksh_aug[0] / total_ksh_aug[2] * 100, 2)) + "%",
             str(total_ksh_aug[0]),
             str(total_ksh_aug[2]),
             str(total_ksh_aug[1]),
             str(round(total_ksh_aug[0] / total_summ * 100, 2)) + "%"),
            ('AWP',
             str(round(total_ksh_awp[2] / total_ksh_awp[1] * 100, 2)) + "%",
             str(round(total_ksh_awp[0] / total_ksh_awp[2] * 100, 2)) + "%",
             str(total_ksh_awp[0]),
             str(total_ksh_awp[2]),
             str(total_ksh_awp[1]),
             str(round(total_ksh_awp[0] / total_summ * 100, 2)) + "%"),
            ('Desert Eagle/R8',
             str(round(total_ksh_deagle[2] /
                       total_ksh_deagle[1] * 100, 2)) + "%",
             str(round(total_ksh_deagle[0] /
                       total_ksh_deagle[2] * 100, 2)) + "%",
             str(total_ksh_deagle[0]),
             str(total_ksh_deagle[2]),
             str(total_ksh_deagle[1]),
             str(round(total_ksh_deagle[0] / total_summ * 100, 2)) + "%"),
            ('Dual Berettas',
             str(round(total_ksh_elite[2] /
                       total_ksh_elite[1] * 100, 2)) + "%",
             str(round(total_ksh_elite[0] /
                       total_ksh_elite[2] * 100, 2)) + "%",
             str(total_ksh_elite[0]),
             str(total_ksh_elite[2]),
             str(total_ksh_elite[1]),
             str(round(total_ksh_elite[0] / total_summ * 100, 2)) + "%"),
            ('Famas',
             str(round(total_ksh_famas[2] /
                       total_ksh_famas[1] * 100, 2)) + "%",
             str(round(total_ksh_famas[0] /
                       total_ksh_famas[2] * 100, 2)) + "%",
             str(total_ksh_famas[0]),
             str(total_ksh_famas[2]),
             str(total_ksh_famas[1]),
             str(round(total_ksh_famas[0] / total_summ * 100, 2)) + "%"),
            ('Five-SeveN',
             str(round(total_ksh_fiveseven[2] /
                       total_ksh_fiveseven[1] * 100, 2)) + "%",
             str(round(total_ksh_fiveseven[0] /
                       total_ksh_fiveseven[2] * 100, 2)) + "%",
             str(total_ksh_fiveseven[0]),
             str(total_ksh_fiveseven[2]),
             str(total_ksh_fiveseven[1]),
             str(round(total_ksh_fiveseven[0] / total_summ * 100, 2)) + "%"),
            ('G3SG1',
             str(round(total_ksh_g3sg1[2] /
                       total_ksh_g3sg1[1] * 100, 2)) + "%",
             str(round(total_ksh_g3sg1[0] /
                       total_ksh_g3sg1[2] * 100, 2)) + "%",
             str(total_ksh_g3sg1[0]),
             str(total_ksh_g3sg1[2]),
             str(total_ksh_g3sg1[1]),
             str(round(total_ksh_g3sg1[0] / total_summ * 100, 2)) + "%"),
            ('Galil AR',
             str(round(total_ksh_galilar[2] /
                       total_ksh_galilar[1] * 100, 2)) + "%",
             str(round(total_ksh_galilar[0] /
                       total_ksh_galilar[2] * 100, 2)) + "%",
             str(total_ksh_galilar[0]),
             str(total_ksh_galilar[2]),
             str(total_ksh_galilar[1]),
             str(round(total_ksh_galilar[0] / total_summ * 100, 2)) + "%"),
            ('Glock-18',
             str(round(total_ksh_glock[2] /
                       total_ksh_glock[1] * 100, 2)) + "%",
             str(round(total_ksh_glock[0] /
                       total_ksh_glock[2] * 100, 2)) + "%",
             str(total_ksh_glock[0]),
             str(total_ksh_glock[2]),
             str(total_ksh_glock[1]),
             str(round(total_ksh_glock[0] / total_summ * 100, 2)) + "%"),
            ('M249',
             str(round(total_ksh_m249[2] / total_ksh_m249[1] * 100, 2)) + "%",
             str(round(total_ksh_m249[0] / total_ksh_m249[2] * 100, 2)) + "%",
             str(total_ksh_m249[0]),
             str(total_ksh_m249[2]),
             str(total_ksh_m249[1]),
             str(round(total_ksh_m249[0] / total_summ * 100, 2)) + "%"),
            ('M4A4/M4A1-S',
             str(round(total_ksh_m4a1[2] / total_ksh_m4a1[1] * 100, 2)) + "%",
             str(round(total_ksh_m4a1[0] / total_ksh_m4a1[2] * 100, 2)) + "%",
             str(total_ksh_m4a1[0]),
             str(total_ksh_m4a1[2]),
             str(total_ksh_m4a1[1]),
             str(round(total_ksh_m4a1[0] / total_summ * 100, 2)) + "%"),
            ('MAC-10',
             str(round(total_ksh_mac10[2] /
                       total_ksh_mac10[1] * 100, 2)) + "%",
             str(round(total_ksh_mac10[0] /
                       total_ksh_mac10[2] * 100, 2)) + "%",
             str(total_ksh_mac10[0]),
             str(total_ksh_mac10[2]),
             str(total_ksh_mac10[1]),
             str(round(total_ksh_mac10[0] / total_summ * 100, 2)) + "%"),
            ('MAG7',
             str(round(total_ksh_mag7[2] / total_ksh_mag7[1] * 100, 2)) + "%",
             str(round(total_ksh_mag7[0] / total_ksh_mag7[2] * 100, 2)) + "%",
             str(total_ksh_mag7[0]),
             str(total_ksh_mag7[2]),
             str(total_ksh_mag7[1]),
             str(round(total_ksh_mag7[0] / total_summ * 100, 2)) + "%"),
            ('MP7/MP5-SD',
             str(round(total_ksh_mp7[2] / total_ksh_mp7[1] * 100, 2)) + "%",
             str(round(total_ksh_mp7[0] / total_ksh_mp7[2] * 100, 2)) + "%",
             str(total_ksh_mp7[0]),
             str(total_ksh_mp7[2]),
             str(total_ksh_mp7[1]),
             str(round(total_ksh_mp7[0] / total_summ * 100, 2)) + "%"),
            ('MP9',
             str(round(total_ksh_mp9[2] / total_ksh_mp9[1] * 100, 2)) + "%",
             str(round(total_ksh_mp9[0] / total_ksh_mp9[2] * 100, 2)) + "%",
             str(total_ksh_mp9[0]),
             str(total_ksh_mp9[2]),
             str(total_ksh_mp9[1]),
             str(round(total_ksh_mp9[0] / total_summ * 100, 2)) + "%"),
            ('Negev',
             str(round(total_ksh_negev[2] /
                       total_ksh_negev[1] * 100, 2)) + "%",
             str(round(total_ksh_negev[0] /
                       total_ksh_negev[2] * 100, 2)) + "%",
             str(total_ksh_negev[0]),
             str(total_ksh_negev[2]),
             str(total_ksh_negev[1]),
             str(round(total_ksh_negev[0] / total_summ * 100, 2)) + "%"),
            ('Nova',
             str(round(total_ksh_nova[2] / total_ksh_nova[1] * 100, 2)) + "%",
             str(round(total_ksh_nova[0] / total_ksh_nova[2] * 100, 2)) + "%",
             str(total_ksh_nova[0]),
             str(total_ksh_nova[2]),
             str(total_ksh_nova[1]),
             str(round(total_ksh_nova[0] / total_summ * 100, 2)) + "%"),
            ('P2000/USP-S',
             str(round(total_ksh_hkp2000[2] /
                       total_ksh_hkp2000[1] * 100, 2)) + "%",
             str(round(total_ksh_hkp2000[0] /
                       total_ksh_hkp2000[2] * 100, 2)) + "%",
             str(total_ksh_hkp2000[0]),
             str(total_ksh_hkp2000[2]),
             str(total_ksh_hkp2000[1]),
             str(round(total_ksh_hkp2000[0] / total_summ * 100, 2)) + "%"),
            ('P250/CZ75-Auto',
             str(round(total_ksh_p250[2] / total_ksh_p250[1] * 100, 2)) + "%",
             str(round(total_ksh_p250[0] / total_ksh_p250[2] * 100, 2)) + "%",
             str(total_ksh_p250[0]),
             str(total_ksh_p250[2]),
             str(total_ksh_p250[1]),
             str(round(total_ksh_p250[0] / total_summ * 100, 2)) + "%"),
            ('P90',
             str(round(total_ksh_p90[2] / total_ksh_p90[1] * 100, 2)) + "%",
             str(round(total_ksh_p90[0] / total_ksh_p90[2] * 100, 2)) + "%",
             str(total_ksh_p90[0]),
             str(total_ksh_p90[2]),
             str(total_ksh_p90[1]),
             str(round(total_ksh_p90[0] / total_summ * 100, 2)) + "%"),
            ('PP-Bizon',
             str(round(total_ksh_bizon[2] /
                       total_ksh_bizon[1] * 100, 2)) + "%",
             str(round(total_ksh_bizon[0] /
                       total_ksh_bizon[2] * 100, 2)) + "%",
             str(total_ksh_bizon[0]),
             str(total_ksh_bizon[2]),
             str(total_ksh_bizon[1]),
             str(round(total_ksh_bizon[0] / total_summ * 100, 2)) + "%"),
            ('Sawed-Off',
             str(round(total_ksh_sawedoff[2] /
                       total_ksh_sawedoff[1] * 100, 2)) + "%",
             str(round(total_ksh_sawedoff[0] /
                       total_ksh_sawedoff[2] * 100, 2)) + "%",
             str(total_ksh_sawedoff[0]),
             str(total_ksh_sawedoff[2]),
             str(total_ksh_sawedoff[1]),
             str(round(total_ksh_sawedoff[0] / total_summ * 100, 2)) + "%"),
            ('SCAR-20',
             str(round(total_ksh_scar20[2] /
                       total_ksh_scar20[1] * 100, 2)) + "%",
             str(round(total_ksh_scar20[0] /
                       total_ksh_scar20[2] * 100, 2)) + "%",
             str(total_ksh_scar20[0]),
             str(total_ksh_scar20[2]),
             str(total_ksh_scar20[1]),
             str(round(total_ksh_scar20[0] / total_summ * 100, 2)) + "%"),
            ('SG 553',
             str(round(total_ksh_sg556[2] /
                       total_ksh_sg556[1] * 100, 2)) + "%",
             str(round(total_ksh_sg556[0] /
                       total_ksh_sg556[2] * 100, 2)) + "%",
             str(total_ksh_sg556[0]),
             str(total_ksh_sg556[2]),
             str(total_ksh_sg556[1]),
             str(round(total_ksh_sg556[0] / total_summ * 100, 2)) + "%"),
            ('SSG 08',
             str(round(total_ksh_ssg08[2] /
                       total_ksh_ssg08[1] * 100, 2)) + "%",
             str(round(total_ksh_ssg08[0] /
                       total_ksh_ssg08[2] * 100, 2)) + "%",
             str(total_ksh_ssg08[0]),
             str(total_ksh_ssg08[2]),
             str(total_ksh_ssg08[1]),
             str(round(total_ksh_ssg08[0] / total_summ * 100, 2)) + "%"),
            ('TEC9',
             str(round(total_ksh_tec9[2] / total_ksh_tec9[1] * 100, 2)) + "%",
             str(round(total_ksh_tec9[0] / total_ksh_tec9[2] * 100, 2)) + "%",
             str(total_ksh_tec9[0]),
             str(total_ksh_tec9[2]),
             str(total_ksh_tec9[1]),
             str(round(total_ksh_tec9[0] / total_summ * 100, 2)) + "%"),
            ('UMP45',
             str(round(total_ksh_ump45[2] /
                       total_ksh_ump45[1] * 100, 2)) + "%",
             str(round(total_ksh_ump45[0] /
                       total_ksh_ump45[2] * 100, 2)) + "%",
             str(total_ksh_ump45[0]),
             str(total_ksh_ump45[2]),
             str(total_ksh_ump45[1]),
             str(round(total_ksh_ump45[0] / total_summ * 100, 2)) + "%"),
            ('XM1014',
             str(round(total_ksh_xm1014[2] /
                       total_ksh_xm1014[1] * 100, 2)) + "%",
             str(round(total_ksh_xm1014[0] /
                       total_ksh_xm1014[2] * 100, 2)) + "%",
             str(total_ksh_xm1014[0]),
             str(total_ksh_xm1014[2]),
             str(total_ksh_xm1014[1]),
             str(round(total_ksh_xm1014[0] / total_summ * 100, 2)) + "%")]
        return self.date_weapons    

    def find_key_by_value(self, finded, steamid):
        self.today = date.today()        
        self.today_date = self.today.strftime("%b-%d-%Y")
        self.steamid = steamid
        self.url_all_statistic = f'https://api.steampowered.com/ISteamUserStats/GetUserStatsForGame/v0002/?appid=730&key={key}&steamid={self.steamid}'
        self.get_statistic_json = f'date/{self.steamid}/{self.steamid}_all_statistic_{self.today_date}.json'
        self.finded = finded
        try:
            open(self.get_statistic_json, 'r', encoding='utf-8')
        except:
            self.req_statistic = requests.get(self.url_all_statistic).json()
            self.write_json_file(self.req_statistic, self.get_statistic_json)
            
        self.statistic_file_json = self.open_json_file(self.get_statistic_json)
        self.finded_val = 0 
        for _ in self.statistic_file_json['playerstats']['stats']:
            if _['name'] == self.finded:
                self.finded_val = _['value']
        return self.finded_val

class CheckFriendsThread(QtCore.QThread, MyWin):
    list_all_friends = QtCore.pyqtSignal(list)

    def __init__(self, parent=None):        
        QtCore.QThread.__init__(self, parent)
        self.running = False
        self.today = date.today()
        self.today_date = self.today.strftime("%b-%d-%Y")

    def run(self):
        self.running = True        
        self.file_all_users = 'all_stats/all_stats.json'
        self.date_match_users = self.open_json_file(self.file_all_users)
        self.steamid = steamid
        self.url_friends_list = f'https://api.steampowered.com/ISteamUser/GetFriendList/v1/?key={key}&steamid={self.steamid}'
        self.all_friend_list_json = f'date/{self.steamid}/{self.steamid}_all_friend_list_{self.today_date}.json'
        self.friend_info = []
        try:
            open(f'date/{self.steamid}/{self.steamid}_all_friend_list_{self.today_date}.json', 'r')
        except FileNotFoundError:            
            self.req_friends_list = requests.get(self.url_friends_list).json()
            self.write_json_file(self.req_friends_list, self.all_friend_list_json)

        if self.get_profile_test(self.steamid) == 0:
            self.friend_info = [('', '', '', '', '', '', '')]
            return self.friend_info  
        
        self.friend_steamid = self.open_json_file(self.all_friend_list_json)
        
        for i in range(len(self.friend_steamid['friendslist']['friends'])):
            self.steam_id_friend = self.friend_steamid['friendslist']['friends'][i]['steamid']
            self.url_friend_info = f'https://api.steampowered.com/ISteamUser/GetPlayerSummaries/v2/?key={key}&steamids={self.steam_id_friend}'
            try:
                f = open(f'date/{self.steamid}/{self.steam_id_friend}.json', 'r', encoding='utf-8')
            except FileNotFoundError:
                self.req_friends = requests.get(self.url_friend_info).json()
                self.friend_steamid_json = f"date/{self.steamid}/{self.req_friends['response']['players'][0]['steamid']}.json"
                self.write_json_file(self.req_friends, self.friend_steamid_json)
                friend = self.open_json_file(self.friend_steamid_json)
                self.friend_info.append([friend['response']['players'][0]['personaname'], '█████', '█████', '█████', '█████', '█████', '█████'])
                continue

            self.friend_steamid_json = f'date/{self.steamid}/{self.steam_id_friend}.json'
            self.friend = self.open_json_file(self.friend_steamid_json)
            self.friend_info.append([self.friend['response']['players'][0]['personaname'], '█████', '█████', '█████', '█████', '█████', '█████'])

        self.list_all_friends.emit(self.friend_info)

class CheckVacThread(QtCore.QThread, MyWin):
    list_all_users = QtCore.pyqtSignal(list)
    message_toolbar_bans = QtCore.pyqtSignal(str)
    int_for_progressbar_vac = QtCore.pyqtSignal(int, int)

    def __init__(self, parent=None):        
        QtCore.QThread.__init__(self, parent)
        self.running = False
        self._ = 0
        self.today = date.today()
        self.today_date = self.today.strftime("%b-%d-%Y")
        self.vac_banned_status_all = []
        self.all_users = []
        self.vac_banned_status = []
        self.tmp_all_users = []
        self.tmp_steamid = ""
        self.name = ''

    def run(self):
        self.running = True        
        self.file_all_users = 'all_stats/all_stats.json'
        self.date_match_users = self.open_json_file(self.file_all_users)

        for _ in range(len(self.date_match_users)):
            for i in range(10):
                self.vac_banned_status_all.append(self.date_match_users[str(_)]['Team' + str(_)][i + 1]['steamid64'])

        for line in self.vac_banned_status_all:
            if line not in self.all_users:
                self.all_users.append(line)

        while self.running:
            self.vac_banned_status.append(self.check_vac_banned(self.all_users[self._]))
            self.tmp_steamid = self.all_users[self._]
            self.int_for_progressbar_vac.emit(self._, len(self.all_users)) # get info for progress bar
            self.name = self.open_json_file(f"date/{self.tmp_steamid}/{self.tmp_steamid}_profile_info_{self.today_date}.json")['response']['players'][0]['personaname']
            self.tmp_all_users.append([
                    self.tmp_steamid,
                    self.name,
                    'Community Banned' if self.vac_banned_status[self._]['players'][0]["CommunityBanned"] else '',
                    'VAC Banned' if self.vac_banned_status[self._]['players'][0]["VACBanned"] else '',
                    str(self.vac_banned_status[self._]['players'][0]["NumberOfVACBans"]) if self.vac_banned_status[self._]['players'][0]["NumberOfVACBans"] else "",
                    str(self.vac_banned_status[self._]['players'][0]["DaysSinceLastBan"]) if self.vac_banned_status[self._]['players'][0]["DaysSinceLastBan"] else "",
                    str(self.vac_banned_status[self._]['players'][0]["NumberOfGameBans"]) if self.vac_banned_status[self._]['players'][0]["NumberOfGameBans"] else "",
                    "" if self.vac_banned_status[self._]['players'][0]["EconomyBan"] == "none" else "Economy Ban"])
            self._ += 1
            if self._ == len(self.all_users):
                self.list_all_users.emit(self.tmp_all_users)
                break

    def check_vac_banned(self, steamid):
        self.steamid = steamid
        self.file_bans_users = f'date/{self.steamid}/{self.steamid}_ban_status_{self.today_date}.json'
        self.url_steam_bans = f'https://api.steampowered.com/ISteamUser/GetPlayerBans/v1/?key={key}&steamids={self.steamid}'       
        self.directory = f"{self.steamid}"
        self.parent_dir = f'date\\{self.steamid}'
        self.path = os.path.join(self.parent_dir, self.directory)
        self.get_profile_status(self.steamid)

        try:
            os.mkdir(self.path)
        except FileExistsError:
            pass

        try:
            open(f'date/{self.steamid}/{self.steamid}_ban_status_{self.today_date}.json', 'r')
        except FileNotFoundError:
            self.message_toolbar_bans.emit('Создаю на диске ' + f'date/{self.steamid}/{self.steamid}_ban_status_{self.today_date}.json')
            self.request_bans = requests.get(self.url_steam_bans).json()
            self.write_json_file(self.request_bans, self.file_bans_users)
            return self.open_json_file(self.file_bans_users)

        self.message_toolbar_bans.emit('Открываю с диска ' + f'date/{self.steamid}/{self.steamid}_ban_status_{self.today_date}.json')
        return self.open_json_file(self.file_bans_users)

    def get_profile_status(self, steamid):
        self.steamid = steamid
        self.steamid_profile_json = f'date/{self.steamid}/{self.steamid}_profile_info_{self.today_date}.json'
        self.url_profile_info = f'https://api.steampowered.com/ISteamUser/GetPlayerSummaries/v2/?key={key}&steamids={self.steamid}'
        self.directory = f"{self.steamid}"
        self.parent_dir = "date\\"
        self.path = os.path.join(self.parent_dir, self.directory)        
        try:
            os.mkdir(self.path)
        except FileExistsError:
            pass

        try:
            open(f'date/{self.steamid}/{self.steamid}_profile_info_{self.today_date}.json', 'r')
        except FileNotFoundError:
            self.req_profile_info = requests.get(self.url_profile_info).json()
            self.write_json_file(self.req_profile_info, self.steamid_profile_json)                     
            #  communityvisibilitystate 1 - the profile is not visible to you (Private, Friends Only, etc),
            #  communityvisibilitystate 3 - the profile is "Public", and the data is visible.
            if self.req_profile_info['response']['players'] == []:
                self.write_json_file('deleted', f'date/deleted_/{self.steamid}_deleted_profile_info_{self.today_date}.json') 
                return 0
            if self.req_profile_info['response']['players'][0]['communityvisibilitystate'] == 1:
                self.write_json_file(self.req_profile_info, self.steamid_profile_json)
                return self.open_json_file(self.steamid_profile_json)
            elif self.req_profile_info['response']['players'][0]['communityvisibilitystate'] == 3:
                self.write_json_file(self.req_profile_info, self.steamid_profile_json)
                return self.open_json_file(self.steamid_profile_json)
        
        if os.path.exists(f'date/{self.steamid}/{self.steamid}_profile_info_{self.today_date}.json'):
            return self.open_json_file(self.steamid_profile_json) 


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    myapp = MyWin()
    myapp.show()
    sys.exit(app.exec_())
