import json
import sys
import requests
from datetime import datetime
from PyQt5 import QtWidgets, QtCore
from res.mainwindows import Ui_MainWindow
<<<<<<< HEAD
from PyQt5.QtWidgets import QTableWidgetItem
=======
from PyQt5.QtWidgets import QTableWidgetItem, QHeaderView, QWidget, QLabel
>>>>>>> b363dc5eecb081cdef8eaff9242acbd58f144b20
from res.codes import keys
from PyQt5.QtGui import QImage, QPixmap



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
        
        # get info for profiles tab
        req_profile = f'https://api.steampowered.com/ISteamUser/GetPlayerSummaries/v2/?key={key}&steamids={steamid}'
        req_profiles = requests.get(req_profile).json()
        csgo_profiles_json = f'date/{steamid}_profiles.json'        
        csgo_profiles = self.open_json_file(req_profiles, csgo_profiles_json)
        
        # get info for statistics tab
        url_statistics = f'https://api.steampowered.com/ISteamUserStats/GetUserStatsForGame/v0002/?appid=730&key={key}&steamid={steamid}'

        if requests.get(url_statistics).status_code == 500:
            self.statusBar().showMessage(f'ERR: Status code = 500, Приватный профиль')

         
        try:
            self.req_statistic = requests.get(url_statistics).json()
        except json.decoder.JSONDecodeError:
            self.req_statistic = self.open_json_file(req_profiles, 'date/empty_statistics.json')
            self.req_statistics_json = 'date/empty_statistics.json'
            self.req_statistics = self.open_json_file(self.req_statistic, self.req_statistics_json)
            # user online? Delete this code or make func
            if req_profiles['response']['players'][0]['personastate'] == 1:
                online_status = " (В сети)"
            else:
                online_status = " (Не в сети)"      

            # put info in labels
            image = QImage()
            image.loadFromData(requests.get(req_profiles['response']['players'][0]['avatarfull']).content)
            self.ui.label_avatar.setPixmap(QPixmap(image))

            self.ui.label_personaname.setText(
                req_profiles['response']['players'][0]['personaname'] + online_status)
            try:
                self.ui.label_realname.setText('Реальное имя: ' +
                    req_profiles['response']['players'][0]['realname'])
            except KeyError:
                self.ui.label_realname.setText('Реальное имя: Пусто')

            self.ui.label_profileurl.setText('Ссылка на профиль: ' +
                req_profiles['response']['players'][0]['profileurl'])
            
            try:
                if req_profiles['response']['players'][0]['loccountrycode'] == "KZ":            
                    self.ui.label_loccountrycode.setText('Страна: Казахстан')
                elif req_profiles['response']['players'][0]['loccountrycode'] == "RU":
                    self.ui.label_loccountrycode.setText('Страна: Россия')
                else:
                    self.ui.label_loccountrycode.setText('Страна: Неизвестно')
            except KeyError:
                self.ui.label_loccountrycode.setText('Страна: Неизвестно')
            return

        self.req_statistics_json = f'date/{steamid}_statistics.json'
        self.req_statistics = self.open_json_file(self.req_statistic, self.req_statistics_json)

        # user online?
        if req_profiles['response']['players'][0]['personastate'] == 1:
            online_status = " (В сети)"
        else:
            online_status = " (Не в сети)"        
       
        # put info in labels
        image = QImage()
        image.loadFromData(requests.get(req_profiles['response']['players'][0]['avatarfull']).content)
        self.ui.label_avatar.setPixmap(QPixmap(image))

        self.ui.label_personaname.setText(
            req_profiles['response']['players'][0]['personaname'] + online_status)
        try:
            self.ui.label_realname.setText('Реальное имя: ' +
                req_profiles['response']['players'][0]['realname'])
        except KeyError:
            self.ui.label_realname.setText('Реальное имя: Пусто')

        self.ui.label_profileurl.setText('Ссылка на профиль: ' +
            req_profiles['response']['players'][0]['profileurl'])
        
        try:
            if req_profiles['response']['players'][0]['loccountrycode'] == "KZ":            
                self.ui.label_loccountrycode.setText('Страна: Казахстан')
            elif req_profiles['response']['players'][0]['loccountrycode'] == "RU":
                self.ui.label_loccountrycode.setText('Страна: Россия')
            else:
                self.ui.label_loccountrycode.setText('Страна: Неизвестно')
        except KeyError:
            self.ui.label_loccountrycode.setText('Страна: Неизвестно')


        tmp_text_all = ''
        try:
            tmp_text_all += 'Steam ID - ' + str(req_profiles['response']['players'][0]['steamid']) + "\n"
        except KeyError:
            tmp_text_all += ''

        try:
            tmp_text_all += 'communityvisibilitystate - ' + str(req_profiles['response']['players'][0]['communityvisibilitystate']) + "\n"
        except KeyError:
            tmp_text_all += ''

        try:    
            tmp_text_all += 'profilestate - ' + str(req_profiles['response']['players'][0]['profilestate']) + "\n"
        except KeyError:
            tmp_text_all += ''

        try:    
            tmp_text_all += 'personaname - ' + str(req_profiles['response']['players'][0]['personaname']) + "\n"
        except KeyError:
            tmp_text_all += ''

        try:
            tmp_text_all += 'commentpermission - ' + str(req_profiles['response']['players'][0]['commentpermission']) + "\n"
        except KeyError:
            tmp_text_all += ''

        try:
            tmp_text_all += 'profileurl - ' + str(req_profiles['response']['players'][0]['profileurl']) + "\n"
        except KeyError:
            tmp_text_all += ''

        try:
            tmp_text_all += 'avatar - ' + str(req_profiles['response']['players'][0]['avatar']) + "\n"
        except KeyError:
            tmp_text_all += ''

        try:
            tmp_text_all += 'avatarmedium - ' + str(req_profiles['response']['players'][0]['avatarmedium']) + "\n"
        except KeyError:
            tmp_text_all += ''

        try:
            tmp_text_all += 'avatarfull - ' + str(req_profiles['response']['players'][0]['avatarfull']) + "\n"
        except KeyError:
            tmp_text_all += ''

        try:
            tmp_text_all += 'avatarhash - ' + str(req_profiles['response']['players'][0]['avatarhash']) + "\n"
        except KeyError:
            tmp_text_all += ''

        try:
            tmp_text_all += 'lastlogoff - ' + str(datetime.fromtimestamp(req_profiles['response']['players'][0]['lastlogoff'])) + "\n"
        except KeyError:
            tmp_text_all += ''

        try:
            tmp_text_all += 'personastate - ' + str(req_profiles['response']['players'][0]['personastate']) + "\n"
        except KeyError:
            tmp_text_all += ''

        try:
            'realname - ' + str(req_profiles['response']['players'][0]['realname']) + "\n"
        except KeyError:
            tmp_text_all += ''
        
        try:
            tmp_text_all += 'primaryclanid - ' + str(req_profiles['response']['players'][0]['primaryclanid']) + "\n"
        except KeyError:
            tmp_text_all += ''

        try:
            tmp_text_all += 'timecreated - ' + str(datetime.fromtimestamp(req_profiles['response']['players'][0]['timecreated'])) + "\n"
        except KeyError:
            tmp_text_all += ''

        try:
            tmp_text_all += 'personastateflags - ' + str(req_profiles['response']['players'][0]['personastateflags']) + "\n"
        except KeyError:
            tmp_text_all += ''

        try:
            tmp_text_all += 'loccountrycode - ' + str(req_profiles['response']['players'][0]['loccountrycode']) + "\n"
        except KeyError:
            tmp_text_all += ''
        
        try:
            tmp_text_all += 'locstatecode - ' + str(req_profiles['response']['players'][0]['locstatecode']) + "\n"
        except KeyError:
            tmp_text_all += ''
        
        try:
            tmp_text_all += 'loccityid - ' +  str(req_profiles['response']['players'][0]['loccityid'])
        except KeyError:
            tmp_text_all += ''
        
        self.ui.textBrowser_info.setText(tmp_text_all)
        
        total_ksh_ak47 = [
            self.find_key_val('total_kills_ak47'),
            self.find_key_val('total_shots_ak47'),
            self.find_key_val('total_hits_ak47')]

        total_ksh_aug = [
            self.find_key_val('total_kills_aug'),
            self.find_key_val('total_shots_aug'),
            self.find_key_val('total_hits_aug')]

        total_ksh_awp = [
            self.find_key_val('total_kills_awp'),
            self.find_key_val('total_shots_awp'),
            self.find_key_val('total_hits_awp')]

        total_ksh_awp = [
            self.find_key_val('total_kills_awp'),
            self.find_key_val('total_shots_awp'),
            self.find_key_val('total_hits_awp')]

        total_ksh_deagle = [
            self.find_key_val('total_kills_deagle'),
            self.find_key_val('total_shots_deagle'),
            self.find_key_val('total_hits_deagle')]

        total_ksh_elite = [
            self.find_key_val('total_kills_elite'),
            self.find_key_val('total_shots_elite'),
            self.find_key_val('total_hits_elite')]

        total_ksh_famas = [
            self.find_key_val('total_kills_famas'),
            self.find_key_val('total_shots_famas'),
            self.find_key_val('total_hits_famas')]

        total_ksh_fiveseven = [
            self.find_key_val('total_kills_fiveseven'),
            self.find_key_val('total_shots_fiveseven'),
            self.find_key_val('total_hits_fiveseven')]

        total_ksh_g3sg1 = [
            self.find_key_val('total_kills_g3sg1'),
            self.find_key_val('total_shots_g3sg1'),
            self.find_key_val('total_hits_g3sg1')]

        total_ksh_galilar = [
            self.find_key_val('total_kills_galilar'),
            self.find_key_val('total_shots_galilar'),
            self.find_key_val('total_hits_galilar')]

        total_ksh_glock = [
            self.find_key_val('total_kills_glock'),
            self.find_key_val('total_shots_glock'),
            self.find_key_val('total_hits_glock')]

        total_ksh_m249 = [
            self.find_key_val('total_kills_m249'),
            self.find_key_val('total_shots_m249'),
            self.find_key_val('total_hits_m249')]

        total_ksh_m4a1 = [
            self.find_key_val('total_kills_m4a1'),
            self.find_key_val('total_shots_m4a1'),
            self.find_key_val('total_hits_m4a1')]

        total_ksh_mac10 = [
            self.find_key_val('total_kills_mac10'),
            self.find_key_val('total_shots_mac10'),
            self.find_key_val('total_hits_mac10')]

        total_ksh_mag7 = [
            self.find_key_val('total_kills_mag7'),
            self.find_key_val('total_shots_mag7'),
            self.find_key_val('total_hits_mag7')]

        total_ksh_mp7 = [
            self.find_key_val('total_kills_mp7'),
            self.find_key_val('total_shots_mp7'),
            self.find_key_val('total_hits_mp7')]

        total_ksh_mp9 = [
            self.find_key_val('total_kills_mp9'),
            self.find_key_val('total_shots_mp9'),
            self.find_key_val('total_hits_mp9')]

        total_ksh_negev = [
            self.find_key_val('total_kills_negev'),
            self.find_key_val('total_shots_negev'),
            self.find_key_val('total_hits_negev')]

        total_ksh_nova = [
            self.find_key_val('total_kills_nova'),
            self.find_key_val('total_shots_nova'),
            self.find_key_val('total_hits_nova')]

        total_ksh_hkp2000 = [
            self.find_key_val('total_kills_hkp2000'),
            self.find_key_val('total_shots_hkp2000'),
            self.find_key_val('total_hits_hkp2000')]

        total_ksh_p250 = [
            self.find_key_val('total_kills_p250'),
            self.find_key_val('total_shots_p250'),
            self.find_key_val('total_hits_p250')]

        total_ksh_p90 = [
            self.find_key_val('total_kills_p90'),
            self.find_key_val('total_shots_p90'),
            self.find_key_val('total_hits_p90')]

        total_ksh_bizon = [
            self.find_key_val('total_kills_bizon'),
            self.find_key_val('total_shots_bizon'),
            self.find_key_val('total_hits_bizon')]

        total_ksh_sawedoff = [
            self.find_key_val('total_kills_sawedoff'),
            self.find_key_val('total_shots_sawedoff'),
            self.find_key_val('total_hits_sawedoff')]

        total_ksh_scar20 = [
            self.find_key_val('total_kills_scar20'),
            self.find_key_val('total_shots_scar20'),
            self.find_key_val('total_hits_scar20')]

        total_ksh_sg556 = [
            self.find_key_val('total_kills_sg556'),
            self.find_key_val('total_shots_sg556'),
            self.find_key_val('total_hits_sg556')]

        total_ksh_ssg08 = [
            self.find_key_val('total_kills_ssg08'),
            self.find_key_val('total_shots_ssg08'),
            self.find_key_val('total_hits_ssg08')]

        total_ksh_tec9 = [
            self.find_key_val('total_kills_tec9'),
            self.find_key_val('total_shots_tec9'),
            self.find_key_val('total_hits_tec9')]

        total_ksh_ump45 = [
            self.find_key_val('total_kills_ump45'),
            self.find_key_val('total_shots_ump45'),
            self.find_key_val('total_hits_ump45')]

        total_ksh_xm1014 = [
            self.find_key_val('total_kills_xm1014'),
            self.find_key_val('total_shots_xm1014'),
            self.find_key_val('total_hits_xm1014')]

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
             str(round(total_ksh_deagle[2] / total_ksh_deagle[1] * 100, 2)) + "%",
             str(round(total_ksh_deagle[0] / total_ksh_deagle[2] * 100, 2)) + "%",
             str(total_ksh_deagle[0]),
             str(total_ksh_deagle[2]),
             str(total_ksh_deagle[1]),
             str(round(total_ksh_deagle[0] / total_summ * 100, 2)) + "%"),
            ('Dual Berettas',
             str(round(total_ksh_elite[2] / total_ksh_elite[1] * 100, 2)) + "%",
             str(round(total_ksh_elite[0] / total_ksh_elite[2] * 100, 2)) + "%",
             str(total_ksh_elite[0]),
             str(total_ksh_elite[2]),
             str(total_ksh_elite[1]),
             str(round(total_ksh_elite[0] / total_summ * 100, 2)) + "%"),
            ('Famas',
             str(round(total_ksh_famas[2] / total_ksh_famas[1] * 100, 2)) + "%",
             str(round(total_ksh_famas[0] / total_ksh_famas[2] * 100, 2)) + "%",
             str(total_ksh_famas[0]),
             str(total_ksh_famas[2]),
             str(total_ksh_famas[1]),
             str(round(total_ksh_famas[0] / total_summ * 100, 2)) + "%"),
            ('Five-SeveN',
             str(round(total_ksh_fiveseven[2] / total_ksh_fiveseven[1]  * 100, 2)) + "%",
             str(round(total_ksh_fiveseven[0]  / total_ksh_fiveseven[2]  * 100, 2)) + "%",
             str(total_ksh_fiveseven[0]),
             str(total_ksh_fiveseven[2]),
             str(total_ksh_fiveseven[1]),
             str(round(total_ksh_fiveseven[0] / total_summ * 100, 2)) + "%"),
            ('G3SG1',
             str(round(total_ksh_g3sg1[2] / total_ksh_g3sg1[1] * 100, 2)) + "%",
             str(round(total_ksh_g3sg1[0] / total_ksh_g3sg1[2] * 100, 2)) + "%",
             str(total_ksh_g3sg1[0]),
             str(total_ksh_g3sg1[2]),
             str(total_ksh_g3sg1[1]),
             str(round(total_ksh_g3sg1[0] / total_summ * 100, 2)) + "%"),
            ('Galil AR',
             str(round(total_ksh_galilar[2] / total_ksh_galilar[1] * 100, 2)) + "%",
             str(round(total_ksh_galilar[0] / total_ksh_galilar[2] * 100, 2)) + "%",
             str(total_ksh_galilar[0]),
             str(total_ksh_galilar[2]),
             str(total_ksh_galilar[1]),
             str(round(total_ksh_galilar[0] / total_summ * 100, 2)) + "%"),
            ('Glock-18',
             str(round(total_ksh_glock[2] / total_ksh_glock[1] * 100, 2)) + "%",
             str(round(total_ksh_glock[0] / total_ksh_glock[2] * 100, 2)) + "%",
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
             str(round(total_ksh_mac10[2] / total_ksh_mac10[1] * 100, 2)) + "%",
             str(round(total_ksh_mac10[0] / total_ksh_mac10[2] * 100, 2)) + "%",
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
             str(round(total_ksh_negev[2] / total_ksh_negev[1] * 100, 2)) + "%",
             str(round(total_ksh_negev[0] / total_ksh_negev[2] * 100, 2)) + "%",
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
             str(round(total_ksh_hkp2000[2] / total_ksh_hkp2000[1] * 100, 2)) + "%",
             str(round(total_ksh_hkp2000[0] / total_ksh_hkp2000[2] * 100, 2)) + "%",
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
             str(round(total_ksh_bizon[2] / total_ksh_bizon[1] * 100, 2)) + "%",
             str(round(total_ksh_bizon[0] / total_ksh_bizon[2] * 100, 2)) + "%",
             str(total_ksh_bizon[0]),
             str(total_ksh_bizon[2]),
             str(total_ksh_bizon[1]),
             str(round(total_ksh_bizon[0] / total_summ * 100, 2)) + "%"),
            ('Sawed-Off',
             str(round(total_ksh_sawedoff[2] / total_ksh_sawedoff[1] * 100, 2)) + "%",
             str(round(total_ksh_sawedoff[0] / total_ksh_sawedoff[2] * 100, 2)) + "%",
             str(total_ksh_sawedoff[0]),
             str(total_ksh_sawedoff[2]),
             str(total_ksh_sawedoff[1]),
             str(round(total_ksh_sawedoff[0] / total_summ * 100, 2)) + "%"),
            ('SCAR-20',
             str(round(total_ksh_scar20[2] / total_ksh_scar20[1] * 100, 2)) + "%",
             str(round(total_ksh_scar20[0] / total_ksh_scar20[2] * 100, 2)) + "%",
             str(total_ksh_scar20[0]),
             str(total_ksh_scar20[2]),
             str(total_ksh_scar20[1]),
             str(round(total_ksh_scar20[0] / total_summ * 100, 2)) + "%"),
            ('SG 553',
             str(round(total_ksh_sg556[2] / total_ksh_sg556[1] * 100, 2)) + "%",
             str(round(total_ksh_sg556[0] / total_ksh_sg556[2] * 100, 2)) + "%",
             str(total_ksh_sg556[0]),
             str(total_ksh_sg556[2]),
             str(total_ksh_sg556[1]),
             str(round(total_ksh_sg556[0] / total_summ * 100, 2)) + "%"),
            ('SSG 08',
             str(round(total_ksh_ssg08[2] / total_ksh_ssg08[1] * 100, 2)) + "%",
             str(round(total_ksh_ssg08[0] / total_ksh_ssg08[2] * 100, 2)) + "%",
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
             str(round(total_ksh_ump45[2] / total_ksh_ump45[1] * 100, 2)) + "%",
             str(round(total_ksh_ump45[0] / total_ksh_ump45[2] * 100, 2)) + "%",
             str(total_ksh_ump45[0]),
             str(total_ksh_ump45[2]),
             str(total_ksh_ump45[1]),
             str(round(total_ksh_ump45[0] / total_summ * 100, 2)) + "%"),
            ('XM1014',
             str(round(total_ksh_xm1014[2] / total_ksh_xm1014[1] * 100, 2)) + "%",
             str(round(total_ksh_xm1014[0] / total_ksh_xm1014[2] * 100, 2)) + "%",
             str(total_ksh_xm1014[0]),
             str(total_ksh_xm1014[2]),
             str(total_ksh_xm1014[1]),
             str(round(total_ksh_xm1014[0] / total_summ * 100, 2)) + "%")]

        self.ui.tableWidget.setColumnCount(len(date_weapons[0]))
        self.ui.tableWidget.setRowCount(len(date_weapons))
        self.ui.tableWidget.setHorizontalHeaderLabels(
            ('Оружие', 'Точность', 'Летальность',
             'Убийства', 'Попадания', 'Выстрелы', '% от всех\nубийств')
        )

        rows_list = []
        for _ in range(len(date_weapons)):
            rows_list.append(str(_ + 1))
        self.ui.tableWidget.setVerticalHeaderLabels(rows_list)

        row = 0
        for tup in date_weapons:
            col = 0
            for item in tup:
                cellinfo = QTableWidgetItem(item)
                cellinfo.setFlags(
                    QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled
                )
                self.ui.tableWidget.setItem(row, col, cellinfo)
                col += 1
            row += 1

        #self.ui.tableWidget.sectionSizeFromContents(QHeaderView.logicalIndex)
        #size = max(self.ui.tableWidget.sizeHintForColumn(0), 100)

        #self.ui.tableWidget.horizontalHeader().resizeSection(0, size)
        self.ui.tableWidget.horizontalHeader().setSectionResizeMode(
            0, QHeaderView.Stretch)
        
        self.ui.tableWidget.resizeColumnsToContents()
        self.ui.tableWidget.resizeRowsToContents()
        self.ui.tableWidget.setSortingEnabled(True)

    def open_json_file(self, r_request, path):
        try:
            open(path, 'r', encoding='utf-8')
        except FileNotFoundError:
            with open(path, 'w', encoding='utf-8') as write_data_json_file:
                json.dump(r_request, write_data_json_file, ensure_ascii=False, indent=4)
                write_data_json_file.close()
        with open(path, 'r', encoding='utf-8') as read_json_file:
            data_json = json.load(read_json_file)
            read_json_file.close()
        return data_json

    def find_key_val(self, finded):
        self.finded_val = 0
        self.req_statistics = self.open_json_file(self.req_statistic, self.req_statistics_json)        
        for _ in self.req_statistics['playerstats']['stats']:
            if _['name'] == finded:
                self.finded_val = _['value']
        return self.finded_val



if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    myapp = MyWin()
    myapp.show()
    sys.exit(app.exec_())
