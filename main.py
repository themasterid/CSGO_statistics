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
       
        pixmap_rank = QPixmap('img/ranks/skillgroup18.png')
        self.ui.label_rank.setPixmap(pixmap_rank)
        self.ui.lineEdit_steamidfind.setInputMask("99999999999999999;XXXXXXXXXXXXXXXXX")
        self.ui.lineEdit_steamidfind.setText('Введите Steam ID')

        self.get_info_profile(self.steamid)
        tmp_text_all = self.get_table_statistics(self.steamid)
        self.ui.textBrowser_info.setText(tmp_text_all)

        self.ui.pushButton.clicked.connect(self.open_new_profile)
        self.ui.commandLinkButton_openurl.clicked.connect(self.click_avatar)
        match_date_list = self.get_matches()
        self.ui.comboBox_matces.addItems(match_date_list)
        self.ui.comboBox_matces.currentIndexChanged.connect(self.get_info_match)

        self.ui.pushButton_update_stat.clicked.connect(self.get_statistics)
        self.ui.pushButton_update_weapons.clicked.connect(self.get_weapons)
        self.ui.pushButton_update_friends.clicked.connect(self.get_friends)

    def get_profile_test(self, steamid):
        self.steamid = steamid
        url_profile_info = f'https://api.steampowered.com/ISteamUser/GetPlayerSummaries/v2/?key={key}&steamids={self.steamid}'
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
            #  communityvisibilitystate
            #  1 - the profile is not visible to you (Private, Friends Only, etc),
            #  3 - the profile is "Public", and the data is visible.
            if req_profile_info['response']['players'][0]['communityvisibilitystate'] == 1:
                self.statusBar().showMessage(
                    'The profile is not visible to you (Private, Friends Only, etc)')
                steamid_profile_json = f'date/{self.steamid}/{self.steamid}_profile_info.json'
                profile_data_json = self.open_json_file(req_profile_info, steamid_profile_json)
                return profile_data_json
            elif req_profile_info['response']['players'][0]['communityvisibilitystate'] == 3:
                self.statusBar().showMessage(
                    'The profile is "Public", and the data is visible')
                steamid_profile_json = f'date/{self.steamid}/{self.steamid}_profile_info.json'
                profile_data_json = self.open_json_file(req_profile_info, steamid_profile_json)
                return profile_data_json

        if os.path.exists(f'date/{self.steamid}/{self.steamid}_profile_info.json'):
            steamidprofile_json = f'date/{self.steamid}/{self.steamid}_profile_info.json'           
            profile_data_json = self.open_json_file('', steamidprofile_json)
            return profile_data_json 
        else:
            req_profile_info = requests.get(url_profile_info).json()
            steamidprofile_json = f'date/{self.steamid}/{self.steamid}_profile_info.json'
            profile_data_json = self.open_json_file(req_profile_info, steamidprofile_json)
            return profile_data_json

    def get_info_match(self):
        file_p = 'all_stats/76561198084621617/all_stats_.json'
        self.date_match = self.open_json_file(file_p, file_p)
        index = self.ui.comboBox_matces.currentIndex()

        competitive = 'Карта ' + self.date_match[str(index)]['Competitive']
        date = 'Дата ' + self.date_match[str(index)]['date']
        waittime = 'Время ожидания ' + self.date_match[str(index)]['WaitTime']
        matchduration = 'Время игры ' + self.date_match[str(index)]['MatchDuration']
        score = 'Счет ' + self.date_match[str(index)]['Team' + str(index)][0]['score']
        
        if self.date_match[str(index)]['Competitive'] == 'de_engage':
            pixmap = QPixmap('all_stats/76561198084621617/Match_files/de_engage.jpg')
            self.ui.label_image_map.setPixmap(pixmap)
        else:
            pixmap = QPixmap('all_stats/76561198084621617/Match_files/mymaps_de_inferno_thumb.jpg')
            self.ui.label_image_map.setPixmap(pixmap)

        self.steamid1 = self.date_match[str(index)]['Team' + str(index)][1]['steamid64']
        name1 = self.get_profile_test(self.steamid1)['response']['players'][0]['personaname']

        self.steamid2 = self.date_match[str(index)]['Team' + str(index)][2]['steamid64']
        name2 = self.get_profile_test(self.steamid2)['response']['players'][0]['personaname']
        
        self.steamid3 = self.date_match[str(index)]['Team' + str(index)][3]['steamid64']
        name3 = self.get_profile_test(self.steamid3)['response']['players'][0]['personaname']
        
        self.steamid4 = self.date_match[str(index)]['Team' + str(index)][4]['steamid64']
        name4 = self.get_profile_test(self.steamid4)['response']['players'][0]['personaname']
        
        self.steamid5 = self.date_match[str(index)]['Team' + str(index)][5]['steamid64']
        name5 = self.get_profile_test(self.steamid5)['response']['players'][0]['personaname']
        
        self.steamid6 = self.date_match[str(index)]['Team' + str(index)][6]['steamid64']
        name6 = self.get_profile_test(self.steamid6)['response']['players'][0]['personaname']
        
        self.steamid7 = self.date_match[str(index)]['Team' + str(index)][7]['steamid64']
        name7 = self.get_profile_test(self.steamid7)['response']['players'][0]['personaname']
        
        self.steamid8 = self.date_match[str(index)]['Team' + str(index)][8]['steamid64']
        name8 = self.get_profile_test(self.steamid8)['response']['players'][0]['personaname']
        
        self.steamid9 = self.date_match[str(index)]['Team' + str(index)][9]['steamid64']
        name9 = self.get_profile_test(self.steamid9)['response']['players'][0]['personaname']
        
        self.steamid10 = self.date_match[str(index)]['Team' + str(index)][10]['steamid64']
        name10 = self.get_profile_test(self.steamid10)['response']['players'][0]['personaname']

        player_name1 = self.date_match[str(index)]['Team' + str(index)][1]['PlayerName']
        player_name2 = self.date_match[str(index)]['Team' + str(index)][2]['PlayerName']
        player_name3 = self.date_match[str(index)]['Team' + str(index)][3]['PlayerName']
        player_name4 = self.date_match[str(index)]['Team' + str(index)][4]['PlayerName']
        player_name5 = self.date_match[str(index)]['Team' + str(index)][5]['PlayerName']
        player_name6 = self.date_match[str(index)]['Team' + str(index)][6]['PlayerName']
        player_name7 = self.date_match[str(index)]['Team' + str(index)][7]['PlayerName']
        player_name8 = self.date_match[str(index)]['Team' + str(index)][8]['PlayerName']
        player_name9 = self.date_match[str(index)]['Team' + str(index)][9]['PlayerName']
        player_name10 = self.date_match[str(index)]['Team' + str(index)][10]['PlayerName']

        self.ui.label_competitive.setText(competitive)
        self.ui.label_date.setText(date)
        self.ui.label_waittime.setText(waittime)
        self.ui.label_matchduration.setText(matchduration)
        self.ui.label_score.setText(score)

        image1 = QImage()
        image1.loadFromData(requests.get(self.get_profile_test(self.steamid1)['response']['players'][0]['avatar']).content)
        self.ui.label_playername1_avatar.setPixmap(QPixmap(image1))
        
        image2 = QImage()
        image2.loadFromData(requests.get(self.get_profile_test(self.steamid2)['response']['players'][0]['avatar']).content)
        self.ui.label_playername2_avatar.setPixmap(QPixmap(image2))
        
        image3 = QImage()
        image3.loadFromData(requests.get(self.get_profile_test(self.steamid3)['response']['players'][0]['avatar']).content)
        self.ui.label_playername3_avatar.setPixmap(QPixmap(image3))
        
        image4 = QImage()
        image4.loadFromData(requests.get(self.get_profile_test(self.steamid4)['response']['players'][0]['avatar']).content)
        self.ui.label_playername4_avatar.setPixmap(QPixmap(image4))
        
        image5 = QImage()
        image5.loadFromData(requests.get(self.get_profile_test(self.steamid5)['response']['players'][0]['avatar']).content)
        self.ui.label_playername5_avatar.setPixmap(QPixmap(image5))
        
        image6 = QImage()
        image6.loadFromData(requests.get(self.get_profile_test(self.steamid6)['response']['players'][0]['avatar']).content)
        self.ui.label_playername6_avatar.setPixmap(QPixmap(image6))
        
        image7 = QImage()
        image7.loadFromData(requests.get(self.get_profile_test(self.steamid7)['response']['players'][0]['avatar']).content)
        self.ui.label_playername7_avatar.setPixmap(QPixmap(image7))
        
        image8 = QImage()
        image8.loadFromData(requests.get(self.get_profile_test(self.steamid8)['response']['players'][0]['avatar']).content)
        self.ui.label_playername8_avatar.setPixmap(QPixmap(image8))
        
        image9 = QImage()
        image9.loadFromData(requests.get(self.get_profile_test(self.steamid9)['response']['players'][0]['avatar']).content)
        self.ui.label_playername9_avatar.setPixmap(QPixmap(image9))
        
        image10 = QImage()
        image10.loadFromData(requests.get(self.get_profile_test(self.steamid10)['response']['players'][0]['avatar']).content)
        self.ui.label_playername10_avatar.setPixmap(QPixmap(image10))

        #self.ui.label_playername1_avatar.setPixmap(QPixmap(self.date_match[str(index)]['Team' + str(index)][1]['avatar']))
        #self.ui.label_playername2_avatar.setPixmap(QPixmap(self.date_match[str(index)]['Team' + str(index)][2]['avatar']))
        #self.ui.label_playername3_avatar.setPixmap(QPixmap(self.date_match[str(index)]['Team' + str(index)][3]['avatar']))
        #self.ui.label_playername4_avatar.setPixmap(QPixmap(self.date_match[str(index)]['Team' + str(index)][4]['avatar']))
        #self.ui.label_playername5_avatar.setPixmap(QPixmap(self.date_match[str(index)]['Team' + str(index)][5]['avatar']))
        #self.ui.label_playername6_avatar.setPixmap(QPixmap(self.date_match[str(index)]['Team' + str(index)][6]['avatar']))
        #self.ui.label_playername7_avatar.setPixmap(QPixmap(self.date_match[str(index)]['Team' + str(index)][7]['avatar']))
        #self.ui.label_playername8_avatar.setPixmap(QPixmap(self.date_match[str(index)]['Team' + str(index)][8]['avatar']))
        #self.ui.label_playername9_avatar.setPixmap(QPixmap(self.date_match[str(index)]['Team' + str(index)][9]['avatar']))
        #self.ui.label_playername10_avatar.setPixmap(QPixmap(self.date_match[str(index)]['Team' + str(index)][10]['avatar']))

        #self.ui.label_playername1.setToolTip('<img src="https://cdn.cloudflare.steamstatic.com/steamcommunity/public/images/avatars/09/093a719aa08d7404f4e567c0521ee3ab5513054f_full.jpg">')

        self.ui.label_playername1.setText(name1)
        self.ui.label_playername2.setText(name2)
        self.ui.label_playername3.setText(name3)
        self.ui.label_playername4.setText(name4)
        self.ui.label_playername5.setText(name5)
        self.ui.label_playername6.setText(name6)
        self.ui.label_playername7.setText(name7)
        self.ui.label_playername8.setText(name8)
        self.ui.label_playername9.setText(name9)
        self.ui.label_playername10.setText(name10)

        #self.ui.label_playername1.setText(player_name2[0])
        #self.ui.label_playername2.setText(player_name2[0])
        #self.ui.label_playername3.setText(player_name3[0])
        #self.ui.label_playername4.setText(player_name4[0])
        #self.ui.label_playername5.setText(player_name5[0])
        #self.ui.label_playername6.setText(player_name6[0])
        #self.ui.label_playername7.setText(player_name7[0])
        #self.ui.label_playername8.setText(player_name8[0])
        #self.ui.label_playername9.setText(player_name9[0])
        #self.ui.label_playername10.setText(player_name10[0])

        self.ui.label_pping1.setText(player_name1[1])
        self.ui.label_pping2.setText(player_name2[1])
        self.ui.label_pping3.setText(player_name3[1])
        self.ui.label_pping4.setText(player_name4[1])
        self.ui.label_pping5.setText(player_name5[1])
        self.ui.label_pping6.setText(player_name6[1])
        self.ui.label_pping7.setText(player_name7[1])
        self.ui.label_pping8.setText(player_name8[1])
        self.ui.label_pping9.setText(player_name9[1])
        self.ui.label_pping10.setText(player_name10[1])

        self.ui.label_kk1.setText(player_name1[2])
        self.ui.label_kk2.setText(player_name2[2])
        self.ui.label_kk3.setText(player_name3[2])
        self.ui.label_kk4.setText(player_name4[2])
        self.ui.label_kk5.setText(player_name5[2])
        self.ui.label_kk6.setText(player_name6[2])
        self.ui.label_kk7.setText(player_name7[2])
        self.ui.label_kk8.setText(player_name8[2])
        self.ui.label_kk9.setText(player_name9[2])
        self.ui.label_kk10.setText(player_name10[2])

        self.ui.label_aa1.setText(player_name1[3])
        self.ui.label_aa2.setText(player_name2[3])
        self.ui.label_aa3.setText(player_name3[3])
        self.ui.label_aa4.setText(player_name4[3])
        self.ui.label_aa5.setText(player_name5[3])
        self.ui.label_aa6.setText(player_name6[3])
        self.ui.label_aa7.setText(player_name7[3])
        self.ui.label_aa8.setText(player_name8[3])
        self.ui.label_aa9.setText(player_name9[3])
        self.ui.label_aa10.setText(player_name10[3])

        self.ui.label_dd1.setText(player_name1[4])
        self.ui.label_dd2.setText(player_name2[4])
        self.ui.label_dd3.setText(player_name3[4])
        self.ui.label_dd4.setText(player_name4[4])
        self.ui.label_dd5.setText(player_name5[4])
        self.ui.label_dd6.setText(player_name6[4])
        self.ui.label_dd7.setText(player_name7[4])
        self.ui.label_dd8.setText(player_name8[4])
        self.ui.label_dd9.setText(player_name9[4])
        self.ui.label_dd10.setText(player_name10[4])

        self.ui.label_mmvp1.setText(player_name1[5])
        self.ui.label_mmvp2.setText(player_name2[5])
        self.ui.label_mmvp3.setText(player_name3[5])
        self.ui.label_mmvp4.setText(player_name4[5])
        self.ui.label_mmvp5.setText(player_name5[5])
        self.ui.label_mmvp6.setText(player_name6[5])
        self.ui.label_mmvp7.setText(player_name7[5])
        self.ui.label_mmvp8.setText(player_name8[5])
        self.ui.label_mmvp9.setText(player_name9[5])
        self.ui.label_mmvp10.setText(player_name10[5])

        self.ui.label_hhsp1.setText(player_name1[6])
        self.ui.label_hhsp2.setText(player_name2[6])
        self.ui.label_hhsp3.setText(player_name3[6])
        self.ui.label_hhsp4.setText(player_name4[6])
        self.ui.label_hhsp5.setText(player_name5[6])
        self.ui.label_hhsp6.setText(player_name6[6])
        self.ui.label_hhsp7.setText(player_name7[6])
        self.ui.label_hhsp8.setText(player_name8[6])
        self.ui.label_hhsp9.setText(player_name9[6])
        self.ui.label_hhsp10.setText(player_name10[6])

        self.ui.label_sscore1.setText(player_name1[7])
        self.ui.label_sscore2.setText(player_name2[7])
        self.ui.label_sscore3.setText(player_name3[7])
        self.ui.label_sscore4.setText(player_name4[7])
        self.ui.label_sscore5.setText(player_name5[7])
        self.ui.label_sscore6.setText(player_name6[7])
        self.ui.label_sscore7.setText(player_name7[7])
        self.ui.label_sscore8.setText(player_name8[7])
        self.ui.label_sscore9.setText(player_name9[7])
        self.ui.label_sscore10.setText(player_name10[7])

        return


    def get_matches(self):
        file_p = 'all_stats/76561198084621617/all_stats_.json'
        match_date = self.open_json_file(file_p, file_p)
        match_dates = []
        for _ in range(len(match_date)):
            match_dates.append(match_date[str(_)]['date'])
        return match_dates

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
        self.get_tale_friends()

    def get_info_profile(self, steamid):
        self.steamid = steamid
        url_profile_info = f'https://api.steampowered.com/ISteamUser/GetPlayerSummaries/v2/?key={key}&steamids={self.steamid}'
        
        self.check_profile(self.steamid)

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
            #  communityvisibilitystate
            #  1 - the profile is not visible to you (Private, Friends Only, etc),
            #  3 - the profile is "Public", and the data is visible.
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
        profile_data_json = self.open_json_file(steamidprofile_json, steamidprofile_json)
        
        #  0 - Offline, 1 - Online, 2 - Busy, 3 - Away, 4 - Snooze, 5 - looking to trade, 6 - looking to play
        #request_status = requests.get(url_profile_info).json()
        personastate = profile_data_json['response']['players'][0]['personastate']
        #  1 - the profile is not visible to you (Private, Friends Only, etc),
        #  3 - the profile is "Public", and the data is visible.
        communityvisibilitystate = profile_data_json['response']['players'][0]['communityvisibilitystate']
        
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
            #  communityvisibilitystate  
            #  1 - the profile is not visible to you (Private, Friends Only, etc),  
            #  3 - the profile is "Public", and the data is visible.  
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
        tmp_text_all += 'Ссылка на профиль - ' + str(profile_data_json['response']['players'][0]['profileurl']) + "\n"
        try:
            tmp_text_all += 'Последний раз выходил - ' + str(datetime.fromtimestamp(profile_data_json['response']['players'][0]['lastlogoff'])) + "\n"
        except KeyError:
            tmp_text_all += 'Последний раз выходил - ' + 'неизвестно' + "\n"
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

        self.ui.tableWidget_weapons.horizontalHeader().setSectionResizeMode(
            0, QHeaderView.Stretch)

        self.ui.tableWidget_weapons.resizeColumnsToContents()
        self.ui.tableWidget_weapons.resizeRowsToContents()
        self.ui.tableWidget_weapons.setSortingEnabled(True)
        return

    def get_tale_friends(self):        
        self.steamid = steamid
        self.friend_info = []
        try:
            open(f'date/{self.steamid}/{self.steamid}_all_friend_list.json', 'r')
        except FileNotFoundError:
            url_friends_list = f'https://api.steampowered.com/ISteamUser/GetFriendList/v1/?key={key}&steamid={self.steamid}'
            req_friends_list = requests.get(url_friends_list).json()
            steamid_file_json = f'date/{self.steamid}/{self.steamid}_all_friend_list.json'
            self.open_json_file(req_friends_list, steamid_file_json)

        #steamid_file_json = f'date/{self.steamid}/{self.steamid}_all_friend_list.json'

        self.steamid = steamid
        url_profile_info = f'https://api.steampowered.com/ISteamUser/GetPlayerSummaries/v2/?key={key}&steamids={self.steamid}'        
        
        if requests.get(url_profile_info).json()['response']['players'][0]['communityvisibilitystate'] == 1:
            self.friend_info = [('', '', '', '', '', '', '')]
            return self.friend_info        
        
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
                self.friend_info.append([friend['response']['players'][0]['personaname'], 'Глобал', '758', '35', '1245', '26', '35%'])
                continue

            friend_name_json = f'date/{self.steamid}/' + steam_id_friend + ".json"
            friend = self.open_json_file(friend_name_json, friend_name_json)
            self.friend_info.append([friend['response']['players'][0]['personaname'], 'Глобал', '758', '35', '1245', '26', '35%'])
        #return friend_info

        self.ui.tableWidget_friends.setColumnCount(len(self.friend_info[0])) # 7
        self.ui.tableWidget_friends.setRowCount(len(self.friend_info)) # 37
        self.ui.tableWidget_friends.setGridStyle(3)
        self.ui.tableWidget_friends.setHorizontalHeaderLabels(
            ('Игрок', 'Ранг', 'Побед в ММ', 'Играли вместе', 'Матчи', 'Матчи с банами', 'Баны/матчи')
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

    def get_table_match(self):
        pass

    def get_table_bans(self):
        pass

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
        if self.check_profile(self.steamid) == 0:
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
