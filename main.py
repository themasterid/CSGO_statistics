import json
import sys
import requests
import os
from datetime import datetime
from PyQt5 import QtWidgets, QtCore, QtGui, QtGui
from res.mainwindows import Ui_MainWindow
from PyQt5.QtWidgets import QTableWidgetItem, QHeaderView
from res.codes import keys
from PyQt5.QtGui import QImage, QPixmap
import webbrowser

text_not_found = '''
            Извините!\n
            При обработке вашего запроса произошла ошибка:\n
            Указанный профиль не найден.
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

        # GET INFO PROFILE
        # GET TABLE STATISTICS
        # GET TABLE WEAPONS
        # GET TABLE FRIENDS
        # GET TABLE MATCHS
        # GET TABLE BANS
        # support
        
        pixmap_rank = QPixmap('img/globalelite.png')
        self.ui.label_rank.setPixmap(pixmap_rank)        
        self.ui.lineEdit_steamidfind.setInputMask("99999999999999999;XXXXXXXXXXXXXXXXX")
        self.ui.lineEdit_steamidfind.setText('Введите Steam ID')

        self.get_info_profile(self.steamid)
        tmp_text_all = self.get_table_statistics(self.steamid)
        self.ui.textBrowser_info.setText(tmp_text_all)

        self.ui.pushButton.clicked.connect(self.open_new_profile)
        self.ui.commandLinkButton_openurl.clicked.connect(self.click_avatar)

        self.ui.pushButton_update_stat.clicked.connect(self.get_statistics)

        self.ui.pushButton_update_weapons.clicked.connect(self.get_weapons)
        self.ui.pushButton_update_friends.clicked.connect(self.get_friends)

    def get_statistics(self):
        self.steamid = self.steamid
        self.get_info_profile(self.steamid)
        tmp_text_all = self.get_table_statistics(self.steamid)
        self.ui.textBrowser_info.setText(tmp_text_all)
   
    def get_weapons(self):
        self.steamid = self.steamid
        date_weapons = self.get_info_weapons(self.steamid)
        self.get_table_weapons(date_weapons)

    def get_friends(self):
        self.steamid = self.steamid
        self.get_friend_list(self.steamid)
        date_friends = self.get_friends_info(self.steamid)
        self.get_tale_friends(date_friends)

    def get_info_profile(self, steamid):
        self.steamid = steamid
        url_profile_info = f'https://api.steampowered.com/ISteamUser/GetPlayerSummaries/v2/?key={key}&steamids={self.steamid}'
        
        if requests.get(url_profile_info).json()['response']['players'] == []:
            pixmap = QPixmap('img/error.jpg')
            self.ui.label_avatar.setPixmap(pixmap)
            self.ui.label_rank.setPixmap(pixmap)
            self.ui.label_personaname.setText('Err: 404 Not Found!')
            self.ui.label_realname.setText('Err: 404 Not Found!')
            self.ui.label_profileurl.setText('https://steamcommunity.com/')
            self.ui.label_loccountrycode.setText('Err: 404 Not Found!')
            self.statusBar().showMessage(f'ERR: Not found!')
            tmp_text_all = text_not_found
            self.ui.textBrowser_info.setText(tmp_text_all)
            return 0

        directory = f"{self.steamid}"
        parent_dir = "C:\\Users\\broot\\Documents\\GitHub\\csgostats\\date\\"
        path = os.path.join(parent_dir, directory)
        try:
            os.mkdir(path)
        except FileExistsError:
            pass

        try:
            open(f'date/{self.steamid}/{self.steamid}_profile_info.json', 'r')
        except FileNotFoundError:
            req_profile_info = requests.get(url_profile_info).json()            
            # add 
            '''
            communityvisibilitystate
            1 - the profile is not visible to you (Private, Friends Only, etc),
            3 - the profile is "Public", and the data is visible.
            '''
            if req_profile_info['response']['players'][0]['communityvisibilitystate'] == 1:
                self.statusBar().showMessage(
                    'The profile is not visible to you (Private, Friends Only, etc)')
                steamid_profile_json = f'date/{self.steamid}/{self.steamid}_profile_info.json'
                profile_data_json = self.open_json_file(req_profile_info, steamid_profile_json)
            elif req_profile_info['response']['players'][0]['communityvisibilitystate'] == 3:
                self.statusBar().showMessage(
                    'The profile is "Public", and the data is visible')
                steamid_profile_json = f'date/{self.steamid}/{self.steamid}_profile_info.json'
                profile_data_json = self.open_json_file(req_profile_info, steamid_profile_json)
        
        steamidprofile_json = f'date/{self.steamid}/{self.steamid}_profile_info.json'
        profile_data_json = self.open_json_file(
            steamidprofile_json, steamidprofile_json)
        
        #  0 - Offline, 1 - Online, 2 - Busy, 3 - Away, 4 - Snooze, 5 - looking to trade, 6 - looking to play
        personastate = requests.get(url_profile_info).json()[
            'response']['players'][0]['personastate']
        #  1 - the profile is not visible to you (Private, Friends Only, etc),
        #  3 - the profile is "Public", and the data is visible.
        communityvisibilitystate = requests.get(url_profile_info).json()[
            'response']['players'][0]['communityvisibilitystate']
        
        if communityvisibilitystate == 1:
            self.statusBar().showMessage(
                '1 - the profile is not visible to you (Private, Friends Only, etc)')
            image = QImage()
            image.loadFromData(requests.get(profile_data_json['response']['players'][0]['avatarfull']).content)
            self.ui.label_avatar.setPixmap(QPixmap(image))
            self.ui.label_personaname.setText(profile_data_json['response']['players'][0]['personaname'] + ' (Приватный профиль)')
            return
        elif communityvisibilitystate == 3:
            self.statusBar().showMessage(
                '3 - the profile is "Public", and the data is visible')
            if personastate == 1:
                online_status = " (Online)"
            elif personastate == 2:
                online_status = " (Online - Занят)"
            elif personastate == 3:
                online_status = " (Online - Отошел)"
            elif personastate == 4:
                online_status = " (Online - Спит)"
            elif personastate == 5:
                online_status = " (Online - Готов к обмену)"
            elif personastate == 6:
                online_status = " (Online - Готов играть)"
            else:
                online_status = " (Offline)"

            image = QImage()
            image.loadFromData(requests.get(profile_data_json['response']['players'][0]['avatarfull']).content)
            self.ui.label_avatar.setPixmap(QPixmap(image))
            self.ui.label_personaname.setText(profile_data_json['response']['players'][0]['personaname'] + online_status)
            
            try:
                self.ui.label_realname.setText(
                                            profile_data_json['response']['players'][0]['realname'])
            except KeyError:
                self.ui.label_realname.setText('---')

            self.ui.label_profileurl.setText(profile_data_json['response']['players'][0]['profileurl'])
            
            self.get_country_info(steamid)

            return profile_data_json

    # STOP HERE!!! 12.02.2021
    def get_country_info(self, steamid):
        self.steamid = steamid
        url_profile_info = f'https://api.steampowered.com/ISteamUser/GetPlayerSummaries/v2/?key={key}&steamids={self.steamid}'
        req_profile = requests.get(url_profile_info).json()
        text_location = ''
        try:
            loccountrycode = req_profile['response']['players'][0]['loccountrycode']
            location_all = f'https://steamcommunity.com/actions/QueryLocations/'
            location_req = requests.get(location_all).json()            
            for _ in location_req:
                if _['countrycode'] == loccountrycode:
                    text_location += _['countryname'] + ', '
        except KeyError:
            text_location += '---'
            self.ui.label_loccountrycode.setText(text_location)
            return text_location
        
        try:
            locstatecode = req_profile['response']['players'][0]['locstatecode']
            location_url = f'https://steamcommunity.com/actions/QueryLocations/{loccountrycode}/'
            location_req = requests.get(location_url).json()
            
            for _ in location_req:
                if _['statecode'] == locstatecode:
                    text_location += _['statename'] + ', '
        except KeyError:
            text_location +=  '---'
            self.ui.label_loccountrycode.setText(text_location)
            return text_location

        try:
            loccityid = req_profile['response']['players'][0]['loccityid']
            location_url = f'https://steamcommunity.com/actions/QueryLocations/{loccountrycode}/{locstatecode}'
            location_req = requests.get(location_url).json()
            for _ in location_req:
                if _['cityid'] == loccityid:
                    text_location += _['cityname']
            self.ui.label_loccountrycode.setText(text_location)
            return text_location
        except KeyError:
            print('Error, locstatecode')
            text_location += '---'
            self.ui.label_loccountrycode.setText(text_location)
            return text_location

    def get_table_statistics(self, steamid):
        self.steamid = steamid
        url_profile_stat = f'https://api.steampowered.com/ISteamUser/GetPlayerSummaries/v2/?key={key}&steamids={self.steamid}'
        tmp_text_all = ''

        if requests.get(url_profile_stat).json()['response']['players'] == []:
            tmp_text_all = text_not_found
            self.statusBar().showMessage(f'ERR: 404 Not found!')
            return tmp_text_all
        try:
            open(f'date/{self.steamid}/{self.steamid}_profile_info.json', 'r')
        except FileNotFoundError:
            req_profile_info = requests.get(url_profile_stat).json()            
            #communityvisibilitystate
            #1 - the profile is not visible to you (Private, Friends Only, etc),
            #3 - the profile is "Public", and the data is visible.
            if req_profile_info['response']['players'][0]['communityvisibilitystate'] == 1:
                self.statusBar().showMessage(
                    'The profile is not visible to you (Private, Friends Only, etc)')
                steamid_profile_json = f'date/{self.steamid}/{self.steamid}_profile_info.json'
                profile_data_json = self.open_json_file(req_profile_info, steamid_profile_json)
                tmp_text_all = '''
                Пользователь скрыл информацию, \n
                профиль является приватным.
                '''
                return tmp_text_all
            elif req_profile_info['response']['players'][0]['communityvisibilitystate'] == 3:
                self.statusBar().showMessage(
                    'The profile is "Public", and the data is visible')
                steamid_profile_json = f'date/{self.steamid}/{self.steamid}_profile_info.json'
                profile_data_json = self.open_json_file(req_profile_info, steamid_profile_json)
        
        steamidprofile_json = f'date/{self.steamid}/{self.steamid}_profile_info.json'
        profile_data_json = self.open_json_file(
            steamidprofile_json, steamidprofile_json)
        
        #  0 - Offline, 1 - Online, 2 - Busy, 3 - Away, 4 - Snooze, 5 - looking to trade, 6 - looking to play
        personastate = requests.get(url_profile_stat).json()[
            'response']['players'][0]['personastate']
        #  1 - the profile is not visible to you (Private, Friends Only, etc),
        #  3 - the profile is "Public", and the data is visible.
        communityvisibilitystate = requests.get(url_profile_stat).json()[
            'response']['players'][0]['communityvisibilitystate']
        
        if communityvisibilitystate == 1:
            statis_profile = "ОткрытыйЗакрытый"
            self.statusBar().showMessage(
                'The profile is not visible to you (Private, Friends Only, etc)')
            image = QImage()
            image.loadFromData(requests.get(profile_data_json['response']['players'][0]['avatarfull']).content)
            self.ui.label_avatar.setPixmap(QPixmap(image))
            self.ui.label_personaname.setText(profile_data_json['response']['players'][0]['personaname'] + ' (Приватный профиль)')
            tmp_text_all = '''
            Пользователь скрыл информацию, \n
            профиль является приватным.
            '''
            return tmp_text_all
        elif communityvisibilitystate == 3:
            statis_profile = "Открытый"
            self.statusBar().showMessage(
                'The profile is "Public", and the data is visible')
            if personastate == 1:
                online_status = " (Online)"
            elif personastate == 2:
                online_status = " (Online - Занят)"
            elif personastate == 3:
                online_status = " (Online - Отошел)"
            elif personastate == 4:
                online_status = " (Online - Спит)"
            elif personastate == 5:
                online_status = " (Online - Готов к обмену)"
            elif personastate == 6:
                online_status = " (Online - Готов играть)"
            else:
                online_status = " (Offline)"

        tmp_text_all += 'Стим ID - ' + profile_data_json['response']['players'][0]['steamid'] + "\n"
        tmp_text_all += 'Статус профиля - ' + statis_profile + "\n"
        tmp_text_all += 'Статус Steam - ' + online_status + "\n"
        tmp_text_all += 'Никнейм - ' + str(profile_data_json['response']['players'][0]['personaname']) + "\n"
        #tmp_text_all += 'commentpermission - ' + str(profile_data_json['response']['players'][0]['commentpermission']) + "\n"
        tmp_text_all += 'Ссылка на профиль - ' + str(profile_data_json['response']['players'][0]['profileurl']) + "\n"
        try:
            tmp_text_all += 'Последний раз выходил - ' + str(datetime.fromtimestamp(profile_data_json['response']['players'][0]['lastlogoff'])) + "\n"
        except KeyError:
            tmp_text_all += 'Последний раз выходил - ' + 'неизвестно' + "\n"
        #tmp_text_all += 'personastate - ' + str(profile_data_json['response']['players'][0]['personastate']) + "\n"
        try:
            tmp_text_all += 'Реальное имя - ' + str(profile_data_json['response']['players'][0]['realname']) + "\n"
        except KeyError:
            tmp_text_all += 'Реальное имя - ' + 'неизвестно' + "\n"
        tmp_text_all += 'Дата создания профиля - ' + str(datetime.fromtimestamp(profile_data_json['response']['players'][0]['timecreated'])) + "\n"
        tmp_text_all += 'Страна - ' + self.ui.label_loccountrycode.text() + "\n"

        return tmp_text_all

    def get_table_weapons(self, date_weapons):
        self.date_weapons = date_weapons
        if self.date_weapons == [('', '', '', '', '', '', '')]:
            return 
        self.ui.tableWidget_weapons.setColumnCount(len(self.date_weapons[0]))
        self.ui.tableWidget_weapons.setRowCount(len(self.date_weapons))
        self.ui.tableWidget_weapons.setHorizontalHeaderLabels(
            ('Оружие', 'Точность', 'Летальность',
             'Убийства', 'Попадания', 'Выстрелы', '% от всех\nубийств'))

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

        #self.ui.tableWidget_weapons.sectionSizeFromContents(QHeaderView.logicalIndex)
        #size = max(self.ui.tableWidget_weapons.sizeHintForColumn(0), 100)

        #self.ui.tableWidget_weapons.horizontalHeader().resizeSection(0, size)
        self.ui.tableWidget_weapons.horizontalHeader().setSectionResizeMode(
            0, QHeaderView.Stretch)

        self.ui.tableWidget_weapons.resizeColumnsToContents()
        self.ui.tableWidget_weapons.resizeRowsToContents()
        self.ui.tableWidget_weapons.setSortingEnabled(True)
        return

    def get_tale_friends(self, date_friends):
        self.date_friends = date_friends
        self.ui.tableWidget_friends.setColumnCount(len(self.date_friends[0]))
        self.ui.tableWidget_friends.setRowCount(len(self.date_friends))
        self.ui.tableWidget_friends.setHorizontalHeaderLabels(
            ('Игрок', 'Ранг', 'Побед в ММ', 'Играли вместе', 'Матчи', 'Матчи с банами', 'Баны/матчи')
            )

        rows_list = []
        for _ in range(len(self.date_friends)):
            rows_list.append(str(_ + 1))
        self.ui.tableWidget_friends.setVerticalHeaderLabels(rows_list)

        row = 0
        for tup in self.date_friends:
            col = 0
            for item in tup:
                cellinfo = QTableWidgetItem(item)
                cellinfo.setFlags(
                    QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled
                )
                self.ui.tableWidget_friends.setItem(row, col, cellinfo)
                col += 1
            row += 1

        #self.ui.tableWidget_friends.sectionSizeFromContents(QHeaderView.logicalIndex)
        #size = max(self.ui.tableWidget_friends.sizeHintForColumn(0), 100)

        #self.ui.tableWidget_friends.horizontalHeader().resizeSection(0, size)
        self.ui.tableWidget_friends.horizontalHeader().setSectionResizeMode(
            0, QHeaderView.Stretch)

        self.ui.tableWidget_friends.resizeColumnsToContents()
        self.ui.tableWidget_friends.resizeRowsToContents()
        self.ui.tableWidget_friends.setSortingEnabled(True)

    def get_table_match(self):
        pass

    def get_table_bans(self):
        pass

    def get_friends_info(self, steamid):
        self.steamid = steamid
        url_profile_info = f'https://api.steampowered.com/ISteamUser/GetPlayerSummaries/v2/?key={key}&steamids={self.steamid}'
        if requests.get(url_profile_info).json()[
            'response']['players'][0]['communityvisibilitystate'] == 1:
            friend_info = [('', '', '', '', '', '', '')]
            return friend_info
        friend_info = []
        open_file_friends_steamid = f'date/{self.steamid}/{self.steamid}_all_friend_list.json'
        friend_steamid = self.open_json_file(
            open_file_friends_steamid, open_file_friends_steamid)
        for i in range(len(friend_steamid['friendslist']['friends'])):
            steam_id_friend = friend_steamid['friendslist']['friends'][i]['steamid']
            url_friend_info = f'https://api.steampowered.com/ISteamUser/GetPlayerSummaries/v2/?key={key}&steamids={steam_id_friend}'
            try:
                f = open(f'date/{self.steamid}/{steam_id_friend}.json', 'r', encoding='utf-8')
            except FileNotFoundError:
                req_friends = requests.get(url_friend_info).json()
                friend_name_json = f'date/{self.steamid}/' + \
                    req_friends['response']['players'][0]['steamid'] + ".json"
                friend = self.open_json_file(req_friends, friend_name_json)
                friend_info.append(str(i + 1) + ") " +
                                friend['response']['players'][0]['personaname'])

            friend_name_json = f'date/{self.steamid}/' + steam_id_friend + ".json"
            friend = self.open_json_file(friend_name_json, friend_name_json)
            friend_info.append(
                [friend['response']['players'][0]['personaname'], '', '', '', '', '', ''])
        return friend_info

    def get_friend_list(self, steamid):
        friend_list = []
        self.steamid = steamid
        try:
            open(f'date/{self.steamid}/{self.steamid}_all_friend_list.json', 'r')
        except FileNotFoundError:
            url_friends_list = f'https://api.steampowered.com/ISteamUser/GetFriendList/v1/?key={key}&steamid={self.steamid}'
            req_friends_list = requests.get(url_friends_list).json()
            steamid_file_json = f'date/{self.steamid}/{self.steamid}_all_friend_list.json'
            friend_list = self.open_json_file(
                req_friends_list, steamid_file_json)
            return friend_list

        steamid_file_json = f'date/{self.steamid}/{self.steamid}_all_friend_list.json'
        friend_list = self.open_json_file(
            steamid_file_json, steamid_file_json)
        
        #for i in range(len(friend_list['friendslist']['friends'])):
            #print(friend_list['friendslist']['friends'][i]['steamid'])
            #name_friend = self.get_info_profile(friend_list['friendslist']['friends'][i]['steamid'])
            #print(name_friend)
        return friend_list

    def open_new_profile(self):
        self.steamid = self.ui.lineEdit_steamidfind.text()
        steamid = self.steamid
        try:
            int(self.steamid)
        except:
            self.statusBar().showMessage(
                'Not INT')
            return
        
        self.ui.label_realname.setText('')
        self.ui.label_profileurl.setText('')
        self.ui.label_loccountrycode.setText('')
        if self.get_info_profile(self.steamid) == 0:
            return
        self.get_info_profile(self.steamid)
        #self.get_statistics
        self.ui.textBrowser_info.setText(self.get_table_statistics(self.steamid))        
        #self.date_weapons = self.get_info_weapons(self.steamid)
        #self.get_table_weapons(self.date_weapons) 
        steamid = self.steamid      
        return self.steamid

    def get_info_weapons(self, steamid):
        self.steamid = steamid
        url_profile_info = f'https://api.steampowered.com/ISteamUser/GetPlayerSummaries/v2/?key={key}&steamids={self.steamid}'
        if requests.get(url_profile_info).json()[
            'response']['players'][0]['communityvisibilitystate'] == 1:
            date_weapons = [('', '', '', '', '', '', '')]
            return date_weapons
        total_ksh_ak47 = [
            self.find_key_val('total_kills_ak47', self.steamid),
            self.find_key_val('total_shots_ak47', self.steamid),
            self.find_key_val('total_hits_ak47', self.steamid)]

        total_ksh_aug = [
            self.find_key_val('total_kills_aug', self.steamid),
            self.find_key_val('total_shots_aug', self.steamid),
            self.find_key_val('total_hits_aug', self.steamid)]

        total_ksh_awp = [
            self.find_key_val('total_kills_awp', self.steamid),
            self.find_key_val('total_shots_awp', self.steamid),
            self.find_key_val('total_hits_awp', self.steamid)]

        total_ksh_awp = [
            self.find_key_val('total_kills_awp', self.steamid),
            self.find_key_val('total_shots_awp', self.steamid),
            self.find_key_val('total_hits_awp', self.steamid)]

        total_ksh_deagle = [
            self.find_key_val('total_kills_deagle', self.steamid),
            self.find_key_val('total_shots_deagle', self.steamid),
            self.find_key_val('total_hits_deagle', self.steamid)]

        total_ksh_elite = [
            self.find_key_val('total_kills_elite', self.steamid),
            self.find_key_val('total_shots_elite', self.steamid),
            self.find_key_val('total_hits_elite', self.steamid)]

        total_ksh_famas = [
            self.find_key_val('total_kills_famas', self.steamid),
            self.find_key_val('total_shots_famas', self.steamid),
            self.find_key_val('total_hits_famas', self.steamid)]

        total_ksh_fiveseven = [
            self.find_key_val('total_kills_fiveseven', self.steamid),
            self.find_key_val('total_shots_fiveseven', self.steamid),
            self.find_key_val('total_hits_fiveseven', self.steamid)]

        total_ksh_g3sg1 = [
            self.find_key_val('total_kills_g3sg1', self.steamid),
            self.find_key_val('total_shots_g3sg1', self.steamid),
            self.find_key_val('total_hits_g3sg1', self.steamid)]

        total_ksh_galilar = [
            self.find_key_val('total_kills_galilar', self.steamid),
            self.find_key_val('total_shots_galilar', self.steamid),
            self.find_key_val('total_hits_galilar', self.steamid)]

        total_ksh_glock = [
            self.find_key_val('total_kills_glock', self.steamid),
            self.find_key_val('total_shots_glock', self.steamid),
            self.find_key_val('total_hits_glock', self.steamid)]

        total_ksh_m249 = [
            self.find_key_val('total_kills_m249', self.steamid),
            self.find_key_val('total_shots_m249', self.steamid),
            self.find_key_val('total_hits_m249', self.steamid)]

        total_ksh_m4a1 = [
            self.find_key_val('total_kills_m4a1', self.steamid),
            self.find_key_val('total_shots_m4a1', self.steamid),
            self.find_key_val('total_hits_m4a1', self.steamid)]

        total_ksh_mac10 = [
            self.find_key_val('total_kills_mac10', self.steamid),
            self.find_key_val('total_shots_mac10', self.steamid),
            self.find_key_val('total_hits_mac10', self.steamid)]

        total_ksh_mag7 = [
            self.find_key_val('total_kills_mag7', self.steamid),
            self.find_key_val('total_shots_mag7', self.steamid),
            self.find_key_val('total_hits_mag7', self.steamid)]

        total_ksh_mp7 = [
            self.find_key_val('total_kills_mp7', self.steamid),
            self.find_key_val('total_shots_mp7', self.steamid),
            self.find_key_val('total_hits_mp7', self.steamid)]

        total_ksh_mp9 = [
            self.find_key_val('total_kills_mp9', self.steamid),
            self.find_key_val('total_shots_mp9', self.steamid),
            self.find_key_val('total_hits_mp9', self.steamid)]

        total_ksh_negev = [
            self.find_key_val('total_kills_negev', self.steamid),
            self.find_key_val('total_shots_negev', self.steamid),
            self.find_key_val('total_hits_negev', self.steamid)]

        total_ksh_nova = [
            self.find_key_val('total_kills_nova', self.steamid),
            self.find_key_val('total_shots_nova', self.steamid),
            self.find_key_val('total_hits_nova', self.steamid)]

        total_ksh_hkp2000 = [
            self.find_key_val('total_kills_hkp2000', self.steamid),
            self.find_key_val('total_shots_hkp2000', self.steamid),
            self.find_key_val('total_hits_hkp2000', self.steamid)]

        total_ksh_p250 = [
            self.find_key_val('total_kills_p250', self.steamid),
            self.find_key_val('total_shots_p250', self.steamid),
            self.find_key_val('total_hits_p250', self.steamid)]

        total_ksh_p90 = [
            self.find_key_val('total_kills_p90', self.steamid),
            self.find_key_val('total_shots_p90', self.steamid),
            self.find_key_val('total_hits_p90', self.steamid)]

        total_ksh_bizon = [
            self.find_key_val('total_kills_bizon', self.steamid),
            self.find_key_val('total_shots_bizon', self.steamid),
            self.find_key_val('total_hits_bizon', self.steamid)]

        total_ksh_sawedoff = [
            self.find_key_val('total_kills_sawedoff', self.steamid),
            self.find_key_val('total_shots_sawedoff', self.steamid),
            self.find_key_val('total_hits_sawedoff', self.steamid)]

        total_ksh_scar20 = [
            self.find_key_val('total_kills_scar20', self.steamid),
            self.find_key_val('total_shots_scar20', self.steamid),
            self.find_key_val('total_hits_scar20', self.steamid)]

        total_ksh_sg556 = [
            self.find_key_val('total_kills_sg556', self.steamid),
            self.find_key_val('total_shots_sg556', self.steamid),
            self.find_key_val('total_hits_sg556', self.steamid)]

        total_ksh_ssg08 = [
            self.find_key_val('total_kills_ssg08', self.steamid),
            self.find_key_val('total_shots_ssg08', self.steamid),
            self.find_key_val('total_hits_ssg08', self.steamid)]

        total_ksh_tec9 = [
            self.find_key_val('total_kills_tec9', self.steamid),
            self.find_key_val('total_shots_tec9', self.steamid),
            self.find_key_val('total_hits_tec9', self.steamid)]

        total_ksh_ump45 = [
            self.find_key_val('total_kills_ump45', self.steamid),
            self.find_key_val('total_shots_ump45', self.steamid),
            self.find_key_val('total_hits_ump45', self.steamid)]

        total_ksh_xm1014 = [
            self.find_key_val('total_kills_xm1014', self.steamid),
            self.find_key_val('total_shots_xm1014', self.steamid),
            self.find_key_val('total_hits_xm1014', self.steamid)]

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

        date_weapons = [(
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
        return date_weapons

# support functions

    def check_profile(self, steamid):
        self.steamid = steamid
        url_profile_stat = f'https://api.steampowered.com/ISteamUser/GetPlayerSummaries/v2/?key={key}&steamids={self.steamid}'

        if requests.get(url_profile_stat).json()['response']['players'] == []:
            self.statusBar().showMessage(f'ERR: 404 Not found!')
            return 0

        personastate = requests.get(url_profile_stat).json()['response']['players'][0]['personastate']
        if personastate == 0:          
            return 0
        else:
            return 1

    def click_avatar(self):
        webbrowser.open(self.ui.label_profileurl.text())

    def write_json_file(self, date_to_write, fname):
        self.date_to_write = date_to_write
        self.fname = fname
        with open(self.fname, 'w', encoding='utf-8') as json_file:
            json.dump(self.date_to_write, json_file,
                      ensure_ascii=False, indent=4)
            json_file.close()

    def open_json_file(self, date_to_write, fname):
        self.date_to_write = date_to_write
        self.fname = fname
        try:
            open(self.fname, 'r', encoding='utf-8')
        except FileNotFoundError:
            self.write_json_file(self.date_to_write, self.fname)
        with open(self.fname, 'r', encoding='utf-8') as read_json_file:
            data_json = json.load(read_json_file)
            read_json_file.close()
        return data_json

    def find_key_val(self, finded, steamid):
        self.steamid = steamid
        self.url_all_statistic = f'https://api.steampowered.com/ISteamUserStats/GetUserStatsForGame/v0002/?appid=730&key={key}&steamid={self.steamid}'
        self.get_statistic_json = f'date/{self.steamid}/{self.steamid}_all_statistic.json'
        self.finded = finded
        try:
            open(self.get_statistic_json, 'r', encoding='utf-8')
        except:
            self.req_statistic = requests.get(self.url_all_statistic).json()
            self.statistic_file_json = self.open_json_file(self.req_statistic, self.get_statistic_json)
            
        #self.req_statistic = requests.get(self.url_all_statistic).json()
        self.statistic_file_json = self.open_json_file(self.get_statistic_json, self.get_statistic_json)
        self.finded_val = 0 
        for _ in self.statistic_file_json['playerstats']['stats']:
            if _['name'] == self.finded:
                self.finded_val = _['value']
        return self.finded_val



if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    myapp = MyWin()
    myapp.show()
    sys.exit(app.exec_())
