import os
import sys
import webbrowser
from datetime import date, datetime, timedelta
from os import listdir
from os.path import isfile, join
from typing import List, Union

import requests
import simplejson as json
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtWidgets import QTableWidgetItem

from res.codes import keys
from res.mainwindows import Ui_MainWindow

TEXT_NOT_FOUND = '''
            Извините!\n
            При обработке вашего запроса произошла ошибка:\n
            Указанный профиль не найден.'''
NO_INFO_USERS = '''
            Пользователь скрыл информацию, \n
            профиль является приватным.'''

STEAMID = keys['steamid']
KEY = keys['key']
KEY_STEAMID = '99999999999999999;XXXXXXXXXXXXXXXXX'
CVS = 'communityvisibilitystate'

GPS = (
    'https://api.steampowered.com/ISteamUser/'
    f'GetPlayerSummaries/v2/?key={KEY}&steamids='
)

GSF = (
    'http://api.steampowered.com/ISteamUser/GetFriendList/v0001/'
    f'?key={KEY}&steamid={STEAMID}&relationship=friend'
)

GUSFG = (
    'https://api.steampowered.com/ISteamUserStats/'
    'GetUserStatsForGame/v0002/'
    f'?appid=730&key={KEY}&steamid='
)

GPB = (
    'https://api.steampowered.com/ISteamUser/'
    f'GetPlayerBans/v1/?key={KEY}&steamids='
)

DATE_FMT = '%b-%d-%Y'
# ! Снять комментари после завершения.
TODAY = date.today()
# ! Если не успел :)
# ! TODAY = date(2021, 11, 19)
UTF8 = 'utf-8'
ALL_S = 'all_stats/jsons/all_stats.json'
DATE = 'date/'

IMG_MAPS = {
    'de_engage': 'img/imgs_maps/de_engage.jpg',
    'Dust II': 'img/imgs_maps/de_dust_2.jpg',
    'cs_office': 'img/imgs_maps/cs_office.jpg',
    'Inferno': 'img/imgs_maps/de_inferno.jpg',
    'Mirage': 'img/imgs_maps/de_mirage.jpg',
    'Vertigo': 'img/imgs_maps/de_vertigo.jpg',
    'de_train': 'img/imgs_maps/de_train.jpg',
    'Ancient': 'img/imgs_maps/de_ancient.jpg',
    'Cache': 'img/imgs_maps/de_cache.jpg',
    'cs_apollo': 'img/imgs_maps/cs_apollo.jpg',
    'Overpass': 'img/imgs_maps/de_overpass.jpg',
    'Nuke': 'img/imgs_maps/de_nuke.jpg',
    'Train': 'img/imgs_maps/de_train.jpg',
}

# ! MAKE DICT
SG0 = 'img/ranks/skillgroup0.png'
SG1 = 'img/ranks/skillgroup1.png'
SG2 = 'img/ranks/skillgroup2.png'
SG3 = 'img/ranks/skillgroup3.png'
SG4 = 'img/ranks/skillgroup4.png'
SG5 = 'img/ranks/skillgroup5.png'
SG6 = 'img/ranks/skillgroup6.png'
SG7 = 'img/ranks/skillgroup7.png'
SG8 = 'img/ranks/skillgroup8.png'
SG9 = 'img/ranks/skillgroup9.png'
SG10 = 'img/ranks/skillgroup10.png'
SG11 = 'img/ranks/skillgroup11.png'
SG12 = 'img/ranks/skillgroup12.png'
SG13 = 'img/ranks/skillgroup13.png'
SG14 = 'img/ranks/skillgroup14.png'
SG15 = 'img/ranks/skillgroup15.png'
SG16 = 'img/ranks/skillgroup16.png'
SG17 = 'img/ranks/skillgroup17.png'
SG18 = 'img/ranks/skillgroup18.png'


class ProfileStatus:

    NAMES = [
        "steamid",
        "communityvisibilitystate",
        "profilestate",
        "personaname",
        "profileurl",
        "avatar",
        "avatarmedium",
        "avatarfull",
        "avatarhash",
        "lastlogoff",
        "personastate",
        "realname",
        "primaryclanid",
        "timecreated",
        "personastateflags",
        "loccountrycode",
        "locstatecode",
        "loccityid"
    ]

    def __init__(self, steamid=''):
        self.steamid = steamid

    def get_profile_check(self, steamid):
        steam_profile = (
            f'date/{steamid}/{steamid}'
            f'_profile_info_{TODAY}.json'
        )
        path_ = os.path.join(DATE, steamid)

        try:
            os.mkdir(path_)
        except FileExistsError:
            pass

        try:
            open(steam_profile, 'r')
        except FileNotFoundError:
            req = requests.get(
                f'{GPS}{steamid}').json()
            self.write_json(req, steam_profile)

        req = self.open_json(steam_profile)
        if req['response']['players'][0] == []:
            deleted = [
                {
                    "steamid": "76561197997566454",
                    "communityvisibilitystate": None,
                    "profilestate": None,
                    "personaname": "[deleted]",
                    "profileurl": None,
                    "avatar": None,
                    "avatarmedium": None,
                    "avatarfull": None,
                    "avatarhash": None,
                    "lastlogoff": None,
                    "personastate": None,
                    "realname": None,
                    "primaryclanid": None,
                    "timecreated": None,
                    "personastateflags": None,
                    "loccountrycode": None,
                    "locstatecode": None,
                    "loccityid": None
                }
            ]
            self.get_file_folder(steamid, steam_profile, deleted)
            return self.open_json(steam_profile)

        if req['response']['players'][0][CVS] == 1:
            return self.open_json(steam_profile)
        if req['response']['players'][0][CVS] == 3:
            return self.open_json(steam_profile)
        if req['response']['players'][0][CVS] == 2:
            return self.open_json(steam_profile)

    def write_json(self, date_, fname):
        with open(
            fname, 'w', encoding=UTF8, buffering=1024**2
        ) as file_:
            return json.dump(
                date_,
                file_,
                ensure_ascii=False,
                indent=4)

    def open_json(self, fname):
        with open(
            fname, 'r', encoding=UTF8, buffering=1024**2
        ) as file_:
            return json.load(file_)

    def get_names(self, dates):
        lst = []
        for i in [dates]:
            dict_ = {j: i.get(j, None) for j in self.NAMES}
            lst.append(dict_)
        return lst

    def check_vac_banned(self, steamid):
        file_bans = (
            f'date/{steamid}/{steamid}'
            f'_ban_status_{TODAY}.json')
        path = os.path.join(f'date/{steamid}')

        try:
            os.mkdir(path)
        except FileExistsError:
            pass

        try:
            open(
                f'{DATE}/{steamid}/{steamid}'
                f'_ban_status_{TODAY}.json', 'r'
            )
        except FileNotFoundError:
            request = requests.get(
                f'{GPB}{steamid}').json()
            self.write_json(request, file_bans)
        return self.open_json(file_bans)

    def create_avatar(self, steamid):
        url_profile_info = f'{GPS}{steamid}'
        steamid_profile_json = (
            f'date/{steamid}/{steamid}'
            f'_profile_info_{TODAY}.json')
        directory = f'{steamid}'
        parent_dir = f'date/{steamid}/'
        file_profile = f'date/{steamid}/{steamid}_profile_info_{TODAY}.json'
        path = os.path.join(parent_dir, directory)
        try:
            os.mkdir(path)
        except FileExistsError:
            pass

        try:
            open(file_profile, 'r')
        except FileNotFoundError:
            req = requests.get(url_profile_info).json()
            if req['response']['players'] == []:
                return "Профиль не найден, либо был удален!"
            if (
                req['response']['players'][0]
                ['communityvisibilitystate'] == 1
            ):
                profile_data_json = self.resault.open_json(
                    steamid_profile_json)
            elif (
                req['response']['players'][0]
                ['communityvisibilitystate'] == 3
            ):
                profile_data_json = self.resault.open_json(
                    steamid_profile_json)

        if not os.path.exists(file_profile):
            req = requests.get(url_profile_info).json()
            self.write_json(req, steamid_profile_json)

        profile_data_json = self.open_json(steamid_profile_json)

        img1 = profile_data_json['response']['players'][0]['avatar']
        img2 = profile_data_json['response']['players'][0]['avatarmedium']
        img3 = profile_data_json['response']['players'][0]['avatarfull']

        if os.path.exists(
            f'date/{steamid}/{img1.split("/")[8]}'
            ) and os.path.exists(
                f'date/{steamid}/{img2.split("/")[8]}'
                ) and os.path.exists(
                    f'date/{steamid}/{img3.split("/")[8]}'
        ):
            profile_data_json = self.open_json(steamid_profile_json)
        if not(os.path.exists(
            f'date/{steamid}/{img1.split("/")[8]}'
            ) and os.path.exists(
                f'date/{steamid}/{img2.split("/")[8]}'
                ) and os.path.exists(
                    f'date/{steamid}/{img3.split("/")[8]}'
                    )
        ):
            req = requests.get(url_profile_info).json()
            self.write_json(req, steamid_profile_json)
            profile_data_json = self.open_json(steamid_profile_json)

            p1 = requests.get(img1)
            with open(
                f"date/{steamid}/{img1.split('/')[8]}", "wb"
            ) as out1:
                out1.write(p1.content)

            p2 = requests.get(img2)
            with open(
                f"date/{steamid}/{img2.split('/')[8]}", "wb"
            ) as out2:
                out2.write(p2.content)

            p3 = requests.get(img3)
            with open(
                f"date/{steamid}/{img3.split('/')[8]}", "wb"
            ) as out3:
                out3.write(p3.content)


class MyWin(QtWidgets.QMainWindow):

    def __init__(self, parent=None):
        QtWidgets.QWidget.__init__(self, parent)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.ui.label_rank.setPixmap(QPixmap(SG18))
        self.ui.lineEdit_steamidfind.setInputMask(KEY_STEAMID)
        self.ui.lineEdit_steamidfind.setText('Введите Steam ID')
        self.check_vac_thread = CheckVacThread()
        self.check_friends_thread = CheckFriendsThread()
        self.check_weapons_thread = CheckWeaponsThread()
        self.ui.commandLinkButton_openurl.clicked.connect(self.click_avatar)
        self.ui.pushButton.clicked.connect(self.open_new_profile)
        self.ui.pushButton_my_profile.clicked.connect(self.open_my_profile)

        self.resault = ProfileStatus()

        # TODO
        # ! после авторизации добавить профиль.
        self.get_info_profile(STEAMID)
        # ! заменить этот блок на вывод с корректным стим id

        # STATS
        self.ui.pushButton_update_stat.clicked.connect(self.get_statistics)
        self.ui.textBrowser_info.setText(
            self.get_table_statistics(STEAMID))

        # WEAPONS
        self.ui.pushButton_update_weapons.clicked.connect(
            self.on_start_weapons)
        self.ui.comboBox_weapons.currentIndexChanged.connect(
            self.open_table_weapons)
        self.ui.comboBox_weapons.addItems(
            self.get_items_combobox('all_weapons'))
        self.ui.comboBox_weapons.setCurrentIndex(0)
        self.check_weapons_thread.list_all_weapons.connect(
            self.get_tables_weapons,
            QtCore.Qt.QueuedConnection)

        # FRIENDS
        self.ui.pushButton_update_friends.clicked.connect(
            self.on_start_friends)
        self.ui.comboBox_friends.currentIndexChanged.connect(
            self.open_table_friends)

        self.ui.comboBox_friends.addItems(
            self.get_items_combobox('all_friends'))
        self.check_friends_thread.list_all_friends.connect(
            self.get_tables_friends,
            QtCore.Qt.QueuedConnection)
        self.ui.tableWidget_friends.itemDoubleClicked.connect(
            self.listwidgetclicked)

        # MATCHES
        self.ui.comboBox_matches.setCurrentIndex(0)
        self.ui.comboBox_matches.currentIndexChanged.connect(
            self.get_info_match)
        self.ui.comboBox_matches.addItems(
            self.get_items_combobox_matches())

        # BANS
        self.ui.pushButton_update_bans_start.clicked.connect(
            self.on_start_vacs)
        self.ui.pushButton_update_bans_stop.clicked.connect(
            self.on_stop_vacs)
        self.ui.comboBox_bans.currentIndexChanged.connect(
            self.open_table_bans)
        self.ui.comboBox_bans.addItems(
            self.get_items_combobox('all_bans'))
        self.check_vac_thread.list_all_users.connect(
            self.get_tables_bans, QtCore.Qt.QueuedConnection)
        self.check_vac_thread.message_toolbar_bans.connect(
            self.on_change_check_vac, QtCore.Qt.QueuedConnection)
        self.check_vac_thread.int_for_progressbar_vac.connect(
            self.on_change_vac_rows, QtCore.Qt.QueuedConnection)

        self.check_weapons_thread.int_for_progressbar_w.connect(
            self.on_change_wp_rows, QtCore.Qt.QueuedConnection)

        self.ui.tableWidget_bans.itemDoubleClicked.connect(
            self.listwidgetclicked)

    # ! NOT DONE !
    # * open my profile by steamid
    def open_my_profile(self):
        (self.ui.tabWidget.setTabEnabled(_, True) for _ in range(1, 4))
        self.ui.pushButton_update_stat.setEnabled(True)
        self.ui.label_rank.setPixmap(QPixmap(SG18))
        # self.get_info_profile(STEAMID)
        self.ui.textBrowser_info.setText(
            self.get_table_statistics(STEAMID)
        )

    # ! DONE !
    # * open steamid in browser
    def listwidgetclicked(self, item) -> Union[str, bool]:
        try:
            int(item.text())
        except TypeError:
            return 'ERR: not int!'
        if len(item.text()) != 17:
            return 'ERR: not equal 17'
        return webbrowser.open(
            f'https://steamcommunity.com/profiles/{item.text()}'
        )

    # ! DONE !
    # * get items box for sort date
    def get_items_combobox(self, string_w):
        # ! STEAMID GLOBAL CONST!
        path = f'date/{string_w}/{STEAMID}/'
        only_f = sorted(
            [f for f in listdir(path) if isfile(join(path, f))],
            reverse=True
        )
        return [i.split('.')[0] for i in only_f]

    # ! DONE !
    # * get items for combobox matches
    def get_items_combobox_matches(self) -> List[str]:
        match_items = self.resault.open_json(ALL_S)
        return (
            (
                f'{_ + 1}) {match_items[_]["date"]}'
                f', map | {match_items[_]["competitive"]}'
                ' |'
            ) for _ in range(len(match_items)))

    def open_table_weapons(self):
        index_match_weapons = self.ui.comboBox_weapons.currentIndex()
        self.ui.tableWidget_weapons.clear()
        date_weapons = self.resault.open_json(
            f'date/all_weapons/{STEAMID}/'
            f'{self.get_items_combobox("all_weapons")[index_match_weapons]}'
            '.json')
        self.ui.tableWidget_weapons.setColumnCount(len(date_weapons[0]))
        self.ui.tableWidget_weapons.setRowCount(len(date_weapons))
        self.ui.tableWidget_weapons.setSortingEnabled(True)
        self.ui.tableWidget_weapons.setHorizontalHeaderLabels((
            'Оружие',
            'Точность',
            'Летальность',
            'Убийства',
            'Попадания',
            'Выстрелы',
            '% от всех\nубийств'
        ))

        self.ui.tableWidget_weapons.setVerticalHeaderLabels(
            [str(_) for _ in range(1, len(date_weapons))]
        )

        for row, tup in enumerate(date_weapons):
            for col, item in enumerate(tup):
                cellinfo = QTableWidgetItem(item)
                cellinfo.setFlags(
                    QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled
                )
                self.ui.tableWidget_weapons.setItem(row, col, cellinfo)
                col += 1
            row += 1

        self.ui.tableWidget_weapons.setGridStyle(1)
        self.ui.tableWidget_weapons.resizeColumnsToContents()

    def open_table_friends(self):
        index_match_friends = self.ui.comboBox_friends.currentIndex()
        self.ui.tableWidget_friends.clear()
        friend_info = self.resault.open_json(
            f'date/all_friends/{STEAMID}/'
            f'{self.get_items_combobox("all_friends")[index_match_friends]}'
            f'.json')
        self.ui.tableWidget_friends.setColumnCount(len(friend_info[0]))
        self.ui.tableWidget_friends.setRowCount(len(friend_info))
        self.ui.tableWidget_friends.setSortingEnabled(True)
        self.ui.tableWidget_friends.setHorizontalHeaderLabels((
            'SteamID',
            'Имя',
            'Друг с',
            'VAC статус',
            'Community Banned',
            'Economy Ban',
            'Game Bans'))

        self.ui.tableWidget_friends.setVerticalHeaderLabels(
            [str(_) for _ in range(1, len(friend_info))]
        )

        for row, tup in enumerate(friend_info):
            for col, item in enumerate(tup):
                cellinfo = QTableWidgetItem(item)
                cellinfo.setFlags(
                    QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)
                self.ui.tableWidget_friends.setItem(row, col, cellinfo)

        self.ui.tableWidget_friends.setGridStyle(1)
        self.ui.tableWidget_friends.resizeColumnsToContents()

    def get_tables_weapons(self, list_s):
        """Заносим данные в таблицу оружия."""
        strings = 'all_weapons'
        with open(
            f'date/{strings}/{STEAMID}/{TODAY}.json',
            'w', encoding=UTF8
        ) as file_all:
            json.dump(
                list_s,
                file_all,
                ensure_ascii=False,
                indent=4)

    def get_tables_bans(self, list_s):
        """Заносим данные в таблицу банов."""
        strings = 'all_bans'
        with open(
            f'date/{strings}/{STEAMID}/{TODAY}.json',
            'w', encoding=UTF8
        ) as file_all:
            json.dump(
                list_s,
                file_all,
                ensure_ascii=False,
                indent=4)

    def get_tables_friends(self, list_s):
        """Заносим данные в таблицу друзей."""
        strings = 'all_friends'
        with open(
            f'date/{strings}/{STEAMID}/{TODAY}.json',
            'w', encoding=UTF8
        ) as file_all:
            json.dump(
                list_s,
                file_all,
                ensure_ascii=False,
                indent=4)

    def open_table_bans(self):
        index_match = self.ui.comboBox_bans.currentIndex()
        self.ui.tableWidget_bans.clear()
        all_users = self.resault.open_json(
            f'date/all_bans/{STEAMID}/'
            f'{self.get_items_combobox("all_bans")[index_match]}'
            '.json')
        if all_users == []:
            return f'Нет данных в таблице банов: {all_users}'

        self.ui.tableWidget_bans.setColumnCount(len(all_users[0]))
        self.ui.tableWidget_bans.setRowCount(len(all_users))
        self.ui.tableWidget_bans.setSortingEnabled(True)
        self.ui.tableWidget_bans.setHorizontalHeaderLabels((
            'Стим ИД',
            'Имя',
            ' Дата матча ',
            'Бан в\nсообществе',
            '  VAC статус  ',
            'Число\nVAC\nбанов',
            '  Дата бана  ',
            'Число\nигровых\nбанов',
            'Бан\nторговой')
        )

        self.ui.tableWidget_weapons.setVerticalHeaderLabels(
            (str(_) for _ in range(1, len(all_users)))
        )

        for row, tup in enumerate(all_users):
            for col, item in enumerate(tup):
                cellinfo = QTableWidgetItem(item)
                cellinfo.setFlags(
                    QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)
                self.ui.tableWidget_bans.setItem(row, col, cellinfo)

        self.ui.tableWidget_bans.setGridStyle(1)
        self.ui.tableWidget_bans.resizeColumnsToContents()

    # ! Add thread GetInfoBanThread
    def get_info_match(self):
        index_match = self.ui.comboBox_matches.currentIndex()
        date_match = self.resault.open_json(ALL_S)[index_match]

        map_match = date_match['competitive']
        competitive = f'Карта {map_match}'
        date_t = f'Дата {date_match["date"]}'
        waittime = f'Время ожидания {date_match["wait_time"]}'
        matchduration = (
            f'Время игры {date_match["match_duration"]}')
        score_ = date_match['score']
        score = f'Счет {score_}'

        pixmap = QPixmap(
            IMG_MAPS.get(map_match, 'img/imgs_maps/nomap.jpg'))

        self.ui.label_image_map.setPixmap(pixmap)

        steamid_i = []
        name_i = []
        player_name_i = []
        vac_status = []
        imgs = []
        for val in range(10):
            self.ui.progressBar_bans.setMaximum(9)
            self.ui.progressBar_bans.setProperty('value', val)
            steamid_i.append(
                date_match['team'][val]['steamid64'])
            resault = self.resault.get_profile_check(steamid_i[val])
            img = resault['response']['players'][0]['avatarfull'].split('/')[8]
            imgs.append(img)
            name_i.append(resault['response']['players'][0]['personaname'])
            self.resault.create_avatar(steamid_i[val])
            vac_status.append(
                self.resault.check_vac_banned(
                    steamid_i[val])['players'][0]['VACBanned'])
            player_name_i.append(
                date_match['team'][val]['player_name'])

        self.ui.label_vac_status_1.setText(
            'VAC BAN' if vac_status[0] else '███████')
        self.ui.label_vac_status_2.setText(
            'VAC BAN' if vac_status[1] else '███████')
        self.ui.label_vac_status_3.setText(
            'VAC BAN' if vac_status[2] else '███████')
        self.ui.label_vac_status_4.setText(
            'VAC BAN' if vac_status[3] else '███████')
        self.ui.label_vac_status_5.setText(
            'VAC BAN' if vac_status[4] else '███████')
        self.ui.label_vac_status_6.setText(
            'VAC BAN' if vac_status[5] else '███████')
        self.ui.label_vac_status_7.setText(
            'VAC BAN' if vac_status[6] else '███████')
        self.ui.label_vac_status_8.setText(
            'VAC BAN' if vac_status[7] else '███████')
        self.ui.label_vac_status_9.setText(
            'VAC BAN' if vac_status[8] else '███████')
        self.ui.label_vac_status_10.setText(
            'VAC BAN' if vac_status[9] else '███████')

        self.ui.label_competitive.setText(competitive)
        self.ui.label_date.setText(date_t)
        self.ui.label_waittime.setText(waittime)
        self.ui.label_matchduration.setText(matchduration)
        self.ui.label_score.setText(score)

        if int(
            score_.split(':')[0]
        ) < int(
            score_.split(':')[1]
        ):
            score_ = f'Проиграли {score_} Выиграли'
        elif int(
            score_.split(':')[0]
        ) > int(
            score_.split(':')[1]
        ):
            score_ = f'Выиграли {score_} Проиграли'
        elif int(
            score_.split(':')[0]
        ) == int(
            score_.split(':')[1]
        ):
            score_ = f'Ничья {score_} Ничья'

        self.ui.label_csore_center.setText(score_)
        self.ui.pname1_avatar.setPixmap(
            QPixmap(f'date/{steamid_i[0]}/{imgs[0]}'))
        self.ui.pname2_avatar.setPixmap(
            QPixmap(f'date/{steamid_i[1]}/{imgs[1]}'))
        self.ui.pname3_avatar.setPixmap(
            QPixmap(f'date/{steamid_i[2]}/{imgs[2]}'))
        self.ui.pname4_avatar.setPixmap(
            QPixmap(f'date/{steamid_i[3]}/{imgs[3]}'))
        self.ui.pname5_avatar.setPixmap(
            QPixmap(f'date/{steamid_i[4]}/{imgs[4]}'))
        self.ui.pname6_avatar.setPixmap(
            QPixmap(f'date/{steamid_i[5]}/{imgs[5]}'))
        self.ui.pname7_avatar.setPixmap(
            QPixmap(f'date/{steamid_i[6]}/{imgs[6]}'))
        self.ui.pname8_avatar.setPixmap(
            QPixmap(f'date/{steamid_i[7]}/{imgs[7]}'))
        self.ui.pname9_avatar.setPixmap(
            QPixmap(f'date/{steamid_i[8]}/{imgs[8]}'))
        self.ui.pname10_avatar.setPixmap(
            QPixmap(f'date/{steamid_i[9]}/{imgs[9]}'))

        self.ui.pname1.setText(name_i[0])
        self.ui.pname2.setText(name_i[1])
        self.ui.pname3.setText(name_i[2])
        self.ui.pname4.setText(name_i[3])
        self.ui.pname5.setText(name_i[4])
        self.ui.pname6.setText(name_i[5])
        self.ui.pname7.setText(name_i[6])
        self.ui.pname8.setText(name_i[7])
        self.ui.pname9.setText(name_i[8])
        self.ui.pname10.setText(name_i[9])

        self.ui.label_pping1.setText(player_name_i[0][1][0])
        self.ui.label_pping2.setText(player_name_i[1][1][0])
        self.ui.label_pping3.setText(player_name_i[2][1][0])
        self.ui.label_pping4.setText(player_name_i[3][1][0])
        self.ui.label_pping5.setText(player_name_i[4][1][0])
        self.ui.label_pping6.setText(player_name_i[5][1][0])
        self.ui.label_pping7.setText(player_name_i[6][1][0])
        self.ui.label_pping8.setText(player_name_i[7][1][0])
        self.ui.label_pping9.setText(player_name_i[8][1][0])
        self.ui.label_pping10.setText(player_name_i[9][1][0])

        self.ui.label_kk1.setText(player_name_i[0][1][1])
        self.ui.label_kk2.setText(player_name_i[1][1][1])
        self.ui.label_kk3.setText(player_name_i[2][1][1])
        self.ui.label_kk4.setText(player_name_i[3][1][1])
        self.ui.label_kk5.setText(player_name_i[4][1][1])
        self.ui.label_kk6.setText(player_name_i[5][1][1])
        self.ui.label_kk7.setText(player_name_i[6][1][1])
        self.ui.label_kk8.setText(player_name_i[7][1][1])
        self.ui.label_kk9.setText(player_name_i[8][1][1])
        self.ui.label_kk10.setText(player_name_i[9][1][1])

        self.ui.label_aa1.setText(player_name_i[0][1][2])
        self.ui.label_aa2.setText(player_name_i[1][1][2])
        self.ui.label_aa3.setText(player_name_i[2][1][2])
        self.ui.label_aa4.setText(player_name_i[3][1][2])
        self.ui.label_aa5.setText(player_name_i[4][1][2])
        self.ui.label_aa6.setText(player_name_i[5][1][2])
        self.ui.label_aa7.setText(player_name_i[6][1][2])
        self.ui.label_aa8.setText(player_name_i[7][1][2])
        self.ui.label_aa9.setText(player_name_i[8][1][2])
        self.ui.label_aa10.setText(player_name_i[9][1][2])

        self.ui.label_dd1.setText(player_name_i[0][1][3])
        self.ui.label_dd2.setText(player_name_i[1][1][3])
        self.ui.label_dd3.setText(player_name_i[2][1][3])
        self.ui.label_dd4.setText(player_name_i[3][1][3])
        self.ui.label_dd5.setText(player_name_i[4][1][3])
        self.ui.label_dd6.setText(player_name_i[5][1][3])
        self.ui.label_dd7.setText(player_name_i[6][1][3])
        self.ui.label_dd8.setText(player_name_i[7][1][3])
        self.ui.label_dd9.setText(player_name_i[8][1][3])
        self.ui.label_dd10.setText(player_name_i[9][1][3])

        self.ui.label_mmvp1.setText(player_name_i[0][1][4])
        self.ui.label_mmvp2.setText(player_name_i[1][1][4])
        self.ui.label_mmvp3.setText(player_name_i[2][1][4])
        self.ui.label_mmvp4.setText(player_name_i[3][1][4])
        self.ui.label_mmvp5.setText(player_name_i[4][1][4])
        self.ui.label_mmvp6.setText(player_name_i[5][1][4])
        self.ui.label_mmvp7.setText(player_name_i[6][1][4])
        self.ui.label_mmvp8.setText(player_name_i[7][1][4])
        self.ui.label_mmvp9.setText(player_name_i[8][1][4])
        self.ui.label_mmvp10.setText(player_name_i[9][1][4])

        self.ui.label_hhsp1.setText(player_name_i[0][1][5])
        self.ui.label_hhsp2.setText(player_name_i[1][1][5])
        self.ui.label_hhsp3.setText(player_name_i[2][1][5])
        self.ui.label_hhsp4.setText(player_name_i[3][1][5])
        self.ui.label_hhsp5.setText(player_name_i[4][1][5])
        self.ui.label_hhsp6.setText(player_name_i[5][1][5])
        self.ui.label_hhsp7.setText(player_name_i[6][1][5])
        self.ui.label_hhsp8.setText(player_name_i[7][1][5])
        self.ui.label_hhsp9.setText(player_name_i[8][1][5])
        self.ui.label_hhsp10.setText(player_name_i[9][1][5])

        self.ui.label_sscore1.setText(player_name_i[0][1][6])
        self.ui.label_sscore2.setText(player_name_i[1][1][6])
        self.ui.label_sscore3.setText(player_name_i[2][1][6])
        self.ui.label_sscore4.setText(player_name_i[3][1][6])
        self.ui.label_sscore5.setText(player_name_i[4][1][6])
        self.ui.label_sscore6.setText(player_name_i[5][1][6])
        self.ui.label_sscore7.setText(player_name_i[6][1][6])
        self.ui.label_sscore8.setText(player_name_i[7][1][6])
        self.ui.label_sscore9.setText(player_name_i[8][1][6])
        self.ui.label_sscore10.setText(player_name_i[9][1][6])

    def get_statistics(self):
        self.ui.textBrowser_info.setText(
            self.get_table_statistics(STEAMID)
        )

    def get_info_profile(self, steamid):
        resault = self.resault.get_profile_check(steamid)
        self.resault.create_avatar(steamid)
        personastate = resault['response']['players'][0]['personastate']
        communityvisibilitystate = resault['response']['players'][0][CVS]
        img = resault['response']['players'][0]['avatarfull'].split('/')[8]
        if communityvisibilitystate == 1:
            (self.ui.tabWidget.setTabEnabled(i, False) for i in range(1, 4))
            self.statusBar().showMessage(
                '1 - the profile is not visible to you'
                ' (Private, Friends Only, etc)')
            self.ui.label_avatar.setPixmap(
                QPixmap(f'date/{steamid}/{img}'))
            self.ui.label_personaname.setText(
                f'{resault[0]["personaname"]} (Приватный профиль)')
        elif communityvisibilitystate == 3:
            self.statusBar().showMessage(
                '3 - the profile is "Public", and the data is visible')
            if personastate == 1:
                online_status = ' (Online)'
            elif personastate == 2:
                online_status = ' (Online - Занят)'
            elif personastate == 3:
                online_status = ' (Online - Отошел)'
            elif personastate == 4:
                online_status = ' (Online - Спит)'
            elif personastate == 5:
                online_status = ' (Online - Готов к обмену)'
            elif personastate == 6:
                online_status = ' (Online - Готов играть)'
            else:
                online_status = ' (Offline)'
            self.ui.label_avatar.setPixmap(
                QPixmap(f'date/{steamid}/{img}'))
            self.ui.label_personaname.setText(
                resault['response']['players'][0]['personaname']
                + online_status)
            try:
                self.ui.label_realname.setText(
                    resault['response']['players'][0]['realname'])
            except KeyError:
                self.ui.label_realname.setText('██████████')
            self.ui.label_profileurl.setText(
                resault['response']['players'][0]['profileurl'])
            self.get_country_info(steamid)
            return resault

    def get_country_info(self, steamid):
        resault = self.resault.get_profile_check(
            steamid)
        text_location = ''
        load_from_file = (
            f'date/{steamid}/{steamid}'
            f'_profile_info_{TODAY}.json')
        load_location_from_file_1 = (
            f'date/{steamid}/{steamid}'
            f'_profile_location_1_{TODAY}.json')
        self.load_location_from_file_2 = (
            f'date/{steamid}/{steamid}'
            f'_profile_location_2_{TODAY}.json')
        self.load_location_from_file_3 = (
            f'date/{steamid}/{steamid}'
            f'_profile_location_3_{TODAY}.json')

        path = os.path.join('date/')

        try:
            os.mkdir(path)
        except FileExistsError:
            pass

        url_pfile_inf = f'{GPS}{steamid}'

        try:
            open(load_from_file, 'r')
        except FileNotFoundError:
            request = requests.get(url_pfile_inf).json()
            self.resault.write_json(
                request, load_from_file)

        try:
            open(load_location_from_file_1, 'r')
        except FileNotFoundError:
            request = requests.get(url_pfile_inf).json()
            self.resault.write_json(
                request, load_from_file)

        try:
            loccountrycode = (
                resault['response']['players'][0]['loccountrycode'])
            location_all_1 = (
                'https://steamcommunity.com/actions/QueryLocations/'
            )
            location_req_1 = requests.get(location_all_1).json()
            self.resault.write_json(
                location_req_1,
                load_location_from_file_1)
            location_file_1 = self.resault.open_json(
                load_location_from_file_1)
            for _ in location_file_1:
                if _['countrycode'] == loccountrycode:
                    text_location += _['countryname'] + ', '
        except KeyError:
            text_location += '██████████'
            self.ui.label_loccountrycode.setText(text_location)
            return text_location

        try:
            self.req_profile = requests.get(url_pfile_inf).json()
            self.locstatecode = (
                self.req_profile['response']['players'][0]['locstatecode'])
            self.location_url_2 = (
                'https://steamcommunity.com/actions/QueryLocations/'
                f'{loccountrycode}/')
            self.location_req_2 = requests.get(self.location_url_2).json()
            self.resault.write_json(
                self.location_req_2,
                self.load_location_from_file_2)
            self.location_file_2 = self.resault.open_json(
                self.load_location_from_file_2)
            for _ in self.location_file_2:
                if _['statecode'] == self.locstatecode:
                    text_location += _['statename'] + ', '
        except KeyError:
            text_location += '██████████'
            self.ui.label_loccountrycode.setText(text_location)
            return text_location

        try:
            loccityid = (
                self.req_profile['response']['players'][0]['loccityid'])
            self.location_url_3 = (
                'https://steamcommunity.com/actions/QueryLocations/'
                f'{loccountrycode}/{self.locstatecode}')
            self.location_req_3 = requests.get(self.location_url_3).json()
            self.resault.write_json(
                self.location_req_3,
                self.load_location_from_file_3)
            self.location_file_3 = self.resault.open_json(
                self.load_location_from_file_3)
            for _ in self.location_file_3:
                if _['cityid'] == loccityid:
                    text_location += _['cityname']
            self.ui.label_loccountrycode.setText(text_location)
            return text_location
        except KeyError:
            text_location += '██████████'
            self.ui.label_loccountrycode.setText(text_location)

        # OpenFromFiles on Disc
        text_location = ''

        try:
            loccountrycode = (
                resault['response']['players'][0]['loccountrycode'])
            location_file_1 = self.resault.open_json(
                load_location_from_file_1)
            for _ in location_file_1:
                if _['countrycode'] == loccountrycode:
                    text_location += _['countryname'] + ', '
        except KeyError:
            text_location += '██████████'
            self.ui.label_loccountrycode.setText(text_location)
            return text_location

        try:
            self.locstatecode = (
                resault['response']['players'][0]['locstatecode'])
            self.location_file_2 = self.resault.open_json(
                self.load_location_from_file_2)
            for _ in self.location_file_2:
                if _['statecode'] == self.locstatecode:
                    text_location += _['statename'] + ', '
        except KeyError:
            text_location += '██████████'
            self.ui.label_loccountrycode.setText(text_location)
            return text_location

        try:
            loccityid = (
                resault['response']['players'][0]['loccityid']
            )
            self.location_file_3 = self.resault.open_json(
                self.load_location_from_file_3)
            for _ in self.location_file_3:
                if _['cityid'] == loccityid:
                    text_location += _['cityname']
            self.ui.label_loccountrycode.setText(text_location)
            return text_location
        except KeyError:
            text_location += '██████████'
            self.ui.label_loccountrycode.setText(text_location)
        return text_location

    def get_table_statistics(self, steamid):
        resault = self.resault.get_profile_check(steamid)
        self.resault.create_avatar(steamid)
        self.get_info_profile(steamid)
        profile_info = (
            f'date/{steamid}/{steamid}'
            f'_profile_info_{TODAY}.json'
        )
        tta = ''

        try:
            open(profile_info, 'r')
        except FileNotFoundError:
            # TODO добавить проверку доступности API
            req = requests.get(f'{GPS}{steamid}').json()
            self.resault.write_json(req, profile_info)

        if resault['response']['players'][0][CVS] == 1:
            self.statusBar().showMessage(
                'The profile is not visible to'
                'you (Private, Friends Only, etc)')
            return NO_INFO_USERS
        elif resault['response']['players'][0][CVS] == 3:
            self.statusBar().showMessage(
                'The profile is "Public", and the data is visible')
            self.resault.open_json(profile_info)

        personastate = resault['response']['players'][0]['personastate']
        communityvisibilitystate = resault['response']['players'][0][CVS]
        img = resault['response']['players'][0]['avatarfull'].split('/')[8]
        if communityvisibilitystate == 1:
            statis_profile = 'Закрытый'
            self.statusBar().showMessage(
                'The profile is not visible to you'
                '(Private, Friends Only, etc)'
            )
            self.image = QImage()
            self.ui.label_avatar.setPixmap(
                QPixmap(f'date/{steamid}/{img}'))
            self.ui.label_personaname.setText(
                resault['response']['players'][0]['personaname'] +
                ' (Приватный профиль)'
            )
            return NO_INFO_USERS

        if communityvisibilitystate == 3:
            statis_profile = 'Открытый'
            self.statusBar().showMessage(
                'The profile is "Public", and the data is visible')
            status_p = {
                0: " nothing",
                1: " (Online)",
                2: " (Online - Занят)",
                3: " (Online - Отошел)",
                4: " (Online - Спит)",
                5: " (Online - Готов к обмену)",
                6: " (Online - Готов играть)",
                7: " (Offline)"
            }
            online_status = status_p[personastate]

        tta += (
            'SteamID - '
            f'{resault["response"]["players"][0]["steamid"]}\n'
        )
        tta += f'Статус профиля - {statis_profile}\n'
        tta += f'Статус Steam - {online_status}\n'
        tmp_name = resault['response']['players'][0]['personaname']
        tta += f'Никнейм - {tmp_name}\n'
        tmp_pfile = resault['response']['players'][0]['profileurl']
        tta += f'Ссылка на профиль - {tmp_pfile}\n'
        text_last = 'Последний раз выходил - ██████████ \n'
        text_exit = 'Последний раз выходил - '

        try:
            tta += text_exit + str(
                datetime.fromtimestamp(
                    resault['response']['players'][0]['lastlogoff']
                )
            ) + '\n'
        except (KeyError, TypeError):
            tta += text_last

        try:
            tta += (
                'Реальное имя -'
                f'{resault["response"]["players"][0]["realname"]}'
                '\n')
        except KeyError:
            tta += 'Реальное имя - ██████████ \n'
        tmp_timec = (
            datetime.fromtimestamp(
                resault['response']['players'][0]['timecreated'])
        )
        tta += f'Дата создания профиля - {tmp_timec}\n'
        tta += (
            f'Страна - {self.ui.label_loccountrycode.text()}\n')

        return tta

    def open_new_profile(self):
        # TODO FIX not valid steam id in input
        steam_id = self.ui.lineEdit_steamidfind.text()
        if steam_id == '':
            self.statusBar().showMessage(
                'Enter steam id or str')
            return 'Enter steam id or str'

        try:
            int(steam_id)
        except TypeError:
            self.statusBar().showMessage(f'Steamid {steam_id} - not INT')
            return f'Steamid {steam_id} - not INT'

        self.ui.label_realname.setText('')
        self.ui.label_profileurl.setText('')
        self.ui.label_loccountrycode.setText('')
        self.ui.textBrowser_info.setText(
            self.get_table_statistics(steam_id))

    def click_avatar(self):
        webbrowser.open(self.ui.label_profileurl.text())

    # WEAPONS
    def on_start_weapons(self):
        if not self.check_weapons_thread.isRunning():
            self.check_weapons_thread.start()

    def on_stop_weapons(self):
        self.check_weapons_thread.running = False

    def on_change_check_weapons(self, weapons_info):
        self.statusBar().showMessage(f'{weapons_info}')

    def on_change_wp_rows(self, info_progress_bar_w, wstats):
        self.info_progress_bar_w = info_progress_bar_w
        self.ui.progressBar_bans.setMaximum(wstats)
        self.ui.progressBar_bans.setProperty(
            'value',
            self.info_progress_bar_w)

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
        self.ui.progressBar_bans.setMaximum(all_users - 1)
        self.ui.progressBar_bans.setProperty(
            'value',
            self.info_progress_bar_vac)

    def close_event(self, event):
        self.hide()
        self.check_vac_thread.running = False
        self.check_vac_thread.wait(5000)
        event.accept()


class CheckWeaponsThread(QtCore.QThread, MyWin):
    """Get weapons info."""
    list_all_weapons = QtCore.pyqtSignal(tuple)
    int_for_progressbar_w = QtCore.pyqtSignal(int, int)

    def __init__(self, parent=None):
        QtCore.QThread.__init__(self, parent)
        self.running = False
        self.resault = ProfileStatus()

    def run(self):
        w_info = self.get_info_weapons(STEAMID)
        path = f'date/all_weapons/{STEAMID}/{TODAY}.json'

        with open(path, 'w', encoding=UTF8) as fw:
            json.dump(w_info, fw, ensure_ascii=False, indent=4)
        return self.list_all_weapons.emit(w_info)

    def get_info_weapons(self, steamid):
        tl_ks_ = 'total_kills_'
        tl_ss_ = 'total_shots_'
        tl_hs_ = 'total_hits_'

        ak47 = (f'{tl_ks_}ak47', f'{tl_ss_}ak47', f'{tl_hs_}ak47')
        total_ksh_ak47 = tuple(
            self.get_wkey(item, steamid) for item in ak47)

        aug = (f'{tl_ks_}aug', f'{tl_ss_}aug', f'{tl_hs_}aug')
        total_ksh_aug = tuple(
            self.get_wkey(item, steamid) for item in aug)

        awp = (f'{tl_ks_}awp', f'{tl_ss_}awp', f'{tl_hs_}awp')
        total_ksh_awp = tuple(
            self.get_wkey(item, steamid) for item in awp)

        deagle = (f'{tl_ks_}deagle', f'{tl_ss_}deagle', f'{tl_hs_}deagle')
        total_ksh_deagle = tuple(
            self.get_wkey(item, steamid) for item in deagle)

        elite = (f'{tl_ks_}elite', f'{tl_ss_}elite', f'{tl_hs_}elite')
        total_ksh_elite = tuple(
            self.get_wkey(item, steamid) for item in elite)

        famas = (f'{tl_ks_}famas', f'{tl_ss_}famas', f'{tl_hs_}famas')
        total_ksh_famas = tuple(
            self.get_wkey(item, steamid) for item in famas)

        fiveseven = (
            f'{tl_ks_}fiveseven',
            f'{tl_ss_}fiveseven',
            f'{tl_hs_}fiveseven')
        total_ksh_fiveseven = tuple(
            self.get_wkey(item, steamid) for item in fiveseven)

        g3sg1 = (f'{tl_ks_}g3sg1', f'{tl_ss_}g3sg1', f'{tl_hs_}g3sg1')
        total_ksh_g3sg1 = tuple(
            self.get_wkey(item, steamid) for item in g3sg1)

        galilar = (
            f'{tl_ks_}galilar', f'{tl_ss_}galilar', f'{tl_hs_}galilar')
        total_ksh_galilar = tuple(
            self.get_wkey(item, steamid) for item in galilar)

        glock = (f'{tl_ks_}glock', f'{tl_ss_}glock', f'{tl_hs_}glock')
        total_ksh_glock = tuple(
            self.get_wkey(item, steamid) for item in glock)

        m249 = (f'{tl_ks_}m249', f'{tl_ss_}m249', f'{tl_hs_}m249')
        total_ksh_m249 = tuple(
            self.get_wkey(item, steamid) for item in m249)

        m4a1 = (f'{tl_ks_}m4a1', f'{tl_ss_}m4a1', f'{tl_hs_}m4a1')
        total_ksh_m4a1 = tuple(
            self.get_wkey(item, steamid) for item in m4a1)

        mac10 = (f'{tl_ks_}mac10', f'{tl_ss_}mac10', f'{tl_hs_}mac10')
        total_ksh_mac10 = tuple(
            self.get_wkey(item, steamid) for item in mac10)

        mag7 = (f'{tl_ks_}mag7', f'{tl_ss_}mag7', f'{tl_hs_}mag7')
        total_ksh_mag7 = tuple(
            self.get_wkey(item, steamid) for item in mag7)

        mp7 = (f'{tl_ks_}mp7', f'{tl_ss_}mp7', f'{tl_hs_}mp7')
        total_ksh_mp7 = tuple(
            self.get_wkey(item, steamid) for item in mp7)

        mp9 = (f'{tl_ks_}mp9', f'{tl_ss_}mp9', f'{tl_hs_}mp9')
        total_ksh_mp9 = tuple(
            self.get_wkey(item, steamid) for item in mp9)

        negev = (f'{tl_ks_}negev', f'{tl_ss_}negev', f'{tl_hs_}negev')
        total_ksh_negev = tuple(
            self.get_wkey(item, steamid) for item in negev)

        nova = (f'{tl_ks_}nova', f'{tl_ss_}nova', f'{tl_hs_}nova')
        total_ksh_nova = tuple(
            self.get_wkey(item, steamid) for item in nova)

        hkp2000 = (
            f'{tl_ks_}hkp2000', f'{tl_ss_}hkp2000', f'{tl_hs_}hkp2000')
        total_ksh_hkp2000 = tuple(
            self.get_wkey(item, steamid) for item in hkp2000)

        p250 = (f'{tl_ks_}p250', f'{tl_ss_}p250', f'{tl_hs_}p250')
        total_ksh_p250 = tuple(
            self.get_wkey(item, steamid) for item in p250)

        p90 = (f'{tl_ks_}p90', f'{tl_ss_}p90', f'{tl_hs_}p90')
        total_ksh_p90 = tuple(
            self.get_wkey(item, steamid) for item in p90)

        bizon = (f'{tl_ks_}bizon', f'{tl_ss_}bizon', f'{tl_hs_}bizon')
        total_ksh_bizon = tuple(
            self.get_wkey(item, steamid) for item in bizon)

        sawedoff = (
            f'{tl_ks_}sawedoff', f'{tl_ss_}sawedoff', f'{tl_hs_}sawedoff')
        total_ksh_sawedoff = tuple(
            self.get_wkey(item, steamid) for item in sawedoff)

        scar20 = (f'{tl_ks_}scar20', f'{tl_ss_}scar20', f'{tl_hs_}scar20')
        total_ksh_scar20 = tuple(
            self.get_wkey(item, steamid) for item in scar20)

        sg556 = (f'{tl_ks_}sg556', f'{tl_ss_}sg556', f'{tl_hs_}sg556')
        total_ksh_sg556 = tuple(
            self.get_wkey(item, steamid) for item in sg556)

        ssg08 = (f'{tl_ks_}ssg08', f'{tl_ss_}ssg08', f'{tl_hs_}ssg08')
        total_ksh_ssg08 = tuple(
            self.get_wkey(item, steamid) for item in ssg08)

        tec9 = (f'{tl_ks_}tec9', f'{tl_ss_}tec9', f'{tl_hs_}tec9')
        total_ksh_tec9 = tuple(
            self.get_wkey(item, steamid) for item in tec9)

        ump45 = (f'{tl_ks_}ump45', f'{tl_ss_}ump45', f'{tl_hs_}ump45')
        total_ksh_ump45 = tuple(
            self.get_wkey(item, steamid) for item in ump45)

        xm1014 = (f'{tl_ks_}xm1014', f'{tl_ss_}xm1014', f'{tl_hs_}xm1014')
        total_ksh_xm1014 = tuple(
            self.get_wkey(item, steamid) for item in xm1014)

        total_summ = sum((
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
            total_ksh_xm1014[0])
        )

        return (
            (
                'AK-47',
                str(round(
                    total_ksh_ak47[2] / total_ksh_ak47[1] * 100, 2
                )) + '%',
                str(round(
                    total_ksh_ak47[0] / total_ksh_ak47[2] * 100, 2
                )) + '%',
                str(total_ksh_ak47[0]),
                str(total_ksh_ak47[2]),
                str(total_ksh_ak47[1]),
                str(round(total_ksh_ak47[0] / total_summ * 100, 2)) + '%'),
            (
                'AUG',
                str(round(total_ksh_aug[2] / total_ksh_aug[1] * 100, 2)) + '%',
                str(round(total_ksh_aug[0] / total_ksh_aug[2] * 100, 2)) + '%',
                str(total_ksh_aug[0]),
                str(total_ksh_aug[2]),
                str(total_ksh_aug[1]),
                str(round(total_ksh_aug[0] / total_summ * 100, 2)) + '%'),
            (
                'AWP',
                str(round(total_ksh_awp[2] / total_ksh_awp[1] * 100, 2)) + '%',
                str(round(total_ksh_awp[0] / total_ksh_awp[2] * 100, 2)) + '%',
                str(total_ksh_awp[0]),
                str(total_ksh_awp[2]),
                str(total_ksh_awp[1]),
                str(round(total_ksh_awp[0] / total_summ * 100, 2)) + '%'),
            (
                'Desert Eagle/R8',
                str(round(total_ksh_deagle[2] /
                    total_ksh_deagle[1] * 100, 2)) + '%',
                str(round(total_ksh_deagle[0] /
                    total_ksh_deagle[2] * 100, 2)) + '%',
                str(total_ksh_deagle[0]),
                str(total_ksh_deagle[2]),
                str(total_ksh_deagle[1]),
                str(round(total_ksh_deagle[0] / total_summ * 100, 2)) + '%'),
            (
                'Dual Berettas',
                str(
                    round(total_ksh_elite[2] /
                          total_ksh_elite[1] * 100, 2)) + '%',
                str(round(total_ksh_elite[0] /
                          total_ksh_elite[2] * 100, 2)) + '%',
                str(total_ksh_elite[0]),
                str(total_ksh_elite[2]),
                str(total_ksh_elite[1]),
                str(round(total_ksh_elite[0] / total_summ * 100, 2)) + '%'),
            (
                'Famas',
                str(
                    round(
                     total_ksh_famas[2] / total_ksh_famas[1] * 100, 2
                    )) + '%',
                str(
                    round(
                     total_ksh_famas[0] / total_ksh_famas[2] * 100, 2
                    )) + '%',
                str(total_ksh_famas[0]),
                str(total_ksh_famas[2]),
                str(total_ksh_famas[1]),
                str(round(total_ksh_famas[0] / total_summ * 100, 2)) + '%'),
            (
                'Five-SeveN',
                str(round(
                    total_ksh_fiveseven[2] / total_ksh_fiveseven[1] * 100, 2
                )) + '%',
                str(round(
                    total_ksh_fiveseven[0] / total_ksh_fiveseven[2] * 100, 2
                )) + '%',
                str(total_ksh_fiveseven[0]),
                str(total_ksh_fiveseven[2]),
                str(total_ksh_fiveseven[1]),
                str(
                    round(
                     total_ksh_fiveseven[0] / total_summ * 100, 2
                    )) + '%'),
            (
                'G3SG1',
                str(
                    round(
                     total_ksh_g3sg1[2] / total_ksh_g3sg1[1] * 100, 2
                    )) + '%',
                str(
                    round(
                     total_ksh_g3sg1[0] / total_ksh_g3sg1[2] * 100, 2
                    )) + '%',
                str(total_ksh_g3sg1[0]),
                str(total_ksh_g3sg1[2]),
                str(total_ksh_g3sg1[1]),
                str(round(total_ksh_g3sg1[0] / total_summ * 100, 2)) + '%'),
            ('Galil AR',
                str(round(total_ksh_galilar[2] /
                    total_ksh_galilar[1] * 100, 2)) + '%',
                str(round(total_ksh_galilar[0] /
                    total_ksh_galilar[2] * 100, 2)) + '%',
                str(total_ksh_galilar[0]),
                str(total_ksh_galilar[2]),
                str(total_ksh_galilar[1]),
                str(round(total_ksh_galilar[0] / total_summ * 100, 2)) + '%'),
            (
                'Glock-18',
                str(round(total_ksh_glock[2] /
                          total_ksh_glock[1] * 100, 2)) + '%',
                str(round(total_ksh_glock[0] /
                          total_ksh_glock[2] * 100, 2)) + '%',
                str(total_ksh_glock[0]),
                str(total_ksh_glock[2]),
                str(total_ksh_glock[1]),
                str(round(total_ksh_glock[0] / total_summ * 100, 2)) + '%'),
            (
                'M249',
                str(round(total_ksh_m249[2] /
                          total_ksh_m249[1] * 100, 2)) + '%',
                str(round(total_ksh_m249[0] /
                          total_ksh_m249[2] * 100, 2)) + '%',
                str(total_ksh_m249[0]),
                str(total_ksh_m249[2]),
                str(total_ksh_m249[1]),
                str(round(total_ksh_m249[0] / total_summ * 100, 2)) + '%'),
            (
                'M4A4/M4A1-S',
                str(round(total_ksh_m4a1[2] /
                          total_ksh_m4a1[1] * 100, 2)) + '%',
                str(round(total_ksh_m4a1[0] /
                          total_ksh_m4a1[2] * 100, 2)) + '%',
                str(total_ksh_m4a1[0]),
                str(total_ksh_m4a1[2]),
                str(total_ksh_m4a1[1]),
                str(round(total_ksh_m4a1[0] / total_summ * 100, 2)) + '%'),
            (
                'MAC-10',
                str(round(total_ksh_mac10[2] /
                    total_ksh_mac10[1] * 100, 2)) + '%',
                str(round(total_ksh_mac10[0] /
                    total_ksh_mac10[2] * 100, 2)) + '%',
                str(total_ksh_mac10[0]),
                str(total_ksh_mac10[2]),
                str(total_ksh_mac10[1]),
                str(round(total_ksh_mac10[0] / total_summ * 100, 2)) + '%'),
            ('MAG7',
                str(round(total_ksh_mag7[2] /
                          total_ksh_mag7[1] * 100, 2)) + '%',
                str(round(total_ksh_mag7[0] /
                          total_ksh_mag7[2] * 100, 2)) + '%',
                str(total_ksh_mag7[0]),
                str(total_ksh_mag7[2]),
                str(total_ksh_mag7[1]),
                str(round(total_ksh_mag7[0] / total_summ * 100, 2)) + '%'),
            ('MP7/MP5-SD',
                str(round(total_ksh_mp7[2] / total_ksh_mp7[1] * 100, 2)) + '%',
                str(round(total_ksh_mp7[0] / total_ksh_mp7[2] * 100, 2)) + '%',
                str(total_ksh_mp7[0]),
                str(total_ksh_mp7[2]),
                str(total_ksh_mp7[1]),
                str(round(total_ksh_mp7[0] / total_summ * 100, 2)) + '%'),
            ('MP9',
                str(round(total_ksh_mp9[2] / total_ksh_mp9[1] * 100, 2)) + '%',
                str(round(total_ksh_mp9[0] / total_ksh_mp9[2] * 100, 2)) + '%',
                str(total_ksh_mp9[0]),
                str(total_ksh_mp9[2]),
                str(total_ksh_mp9[1]),
                str(round(total_ksh_mp9[0] / total_summ * 100, 2)) + '%'),
            ('Negev',
                str(round(total_ksh_negev[2] /
                    total_ksh_negev[1] * 100, 2)) + '%',
                str(round(total_ksh_negev[0] /
                    total_ksh_negev[2] * 100, 2)) + '%',
                str(total_ksh_negev[0]),
                str(total_ksh_negev[2]),
                str(total_ksh_negev[1]),
                str(round(total_ksh_negev[0] / total_summ * 100, 2)) + '%'),
            ('Nova',
                str(round(total_ksh_nova[2] /
                          total_ksh_nova[1] * 100, 2)) + '%',
                str(round(total_ksh_nova[0] /
                          total_ksh_nova[2] * 100, 2)) + '%',
                str(total_ksh_nova[0]),
                str(total_ksh_nova[2]),
                str(total_ksh_nova[1]),
                str(round(total_ksh_nova[0] / total_summ * 100, 2)) + '%'),
            ('P2000/USP-S',
                str(round(total_ksh_hkp2000[2] /
                    total_ksh_hkp2000[1] * 100, 2)) + '%',
                str(round(total_ksh_hkp2000[0] /
                    total_ksh_hkp2000[2] * 100, 2)) + '%',
                str(total_ksh_hkp2000[0]),
                str(total_ksh_hkp2000[2]),
                str(total_ksh_hkp2000[1]),
                str(round(total_ksh_hkp2000[0] / total_summ * 100, 2)) + '%'),
            ('P250/CZ75-Auto',
                str(round(total_ksh_p250[2] /
                          total_ksh_p250[1] * 100, 2)) + '%',
                str(round(total_ksh_p250[0] /
                          total_ksh_p250[2] * 100, 2)) + '%',
                str(total_ksh_p250[0]),
                str(total_ksh_p250[2]),
                str(total_ksh_p250[1]),
                str(round(total_ksh_p250[0] / total_summ * 100, 2)) + '%'),
            ('P90',
                str(round(total_ksh_p90[2] / total_ksh_p90[1] * 100, 2)) + '%',
                str(round(total_ksh_p90[0] / total_ksh_p90[2] * 100, 2)) + '%',
                str(total_ksh_p90[0]),
                str(total_ksh_p90[2]),
                str(total_ksh_p90[1]),
                str(round(total_ksh_p90[0] / total_summ * 100, 2)) + '%'),
            ('PP-Bizon',
                str(round(total_ksh_bizon[2] /
                    total_ksh_bizon[1] * 100, 2)) + '%',
                str(round(total_ksh_bizon[0] /
                    total_ksh_bizon[2] * 100, 2)) + '%',
                str(total_ksh_bizon[0]),
                str(total_ksh_bizon[2]),
                str(total_ksh_bizon[1]),
                str(round(total_ksh_bizon[0] / total_summ * 100, 2)) + '%'),
            ('Sawed-Off',
                str(round(total_ksh_sawedoff[2] /
                    total_ksh_sawedoff[1] * 100, 2)) + '%',
                str(round(total_ksh_sawedoff[0] /
                    total_ksh_sawedoff[2] * 100, 2)) + '%',
                str(total_ksh_sawedoff[0]),
                str(total_ksh_sawedoff[2]),
                str(total_ksh_sawedoff[1]),
                str(round(total_ksh_sawedoff[0] / total_summ * 100, 2)) + '%'),
            ('SCAR-20',
                str(round(total_ksh_scar20[2] /
                    total_ksh_scar20[1] * 100, 2)) + '%',
                str(round(total_ksh_scar20[0] /
                    total_ksh_scar20[2] * 100, 2)) + '%',
                str(total_ksh_scar20[0]),
                str(total_ksh_scar20[2]),
                str(total_ksh_scar20[1]),
                str(round(total_ksh_scar20[0] / total_summ * 100, 2)) + '%'),
            ('SG 553',
                str(round(total_ksh_sg556[2] /
                    total_ksh_sg556[1] * 100, 2)) + '%',
                str(round(total_ksh_sg556[0] /
                    total_ksh_sg556[2] * 100, 2)) + '%',
                str(total_ksh_sg556[0]),
                str(total_ksh_sg556[2]),
                str(total_ksh_sg556[1]),
                str(round(total_ksh_sg556[0] / total_summ * 100, 2)) + '%'),
            (
                'SSG 08',
                str(round(total_ksh_ssg08[2] /
                    total_ksh_ssg08[1] * 100, 2)) + '%',
                str(round(total_ksh_ssg08[0] /
                    total_ksh_ssg08[2] * 100, 2)) + '%',
                str(total_ksh_ssg08[0]),
                str(total_ksh_ssg08[2]),
                str(total_ksh_ssg08[1]),
                str(round(total_ksh_ssg08[0] / total_summ * 100, 2)) + '%'),
            ('TEC9',
                str(round(total_ksh_tec9[2] /
                          total_ksh_tec9[1] * 100, 2)) + '%',
                str(round(total_ksh_tec9[0] /
                          total_ksh_tec9[2] * 100, 2)) + '%',
                str(total_ksh_tec9[0]),
                str(total_ksh_tec9[2]),
                str(total_ksh_tec9[1]),
                str(round(total_ksh_tec9[0] / total_summ * 100, 2)) + '%'),
            (
                'UMP45',
                str(round(total_ksh_ump45[2] /
                    total_ksh_ump45[1] * 100, 2)) + '%',
                str(round(total_ksh_ump45[0] /
                    total_ksh_ump45[2] * 100, 2)) + '%',
                str(total_ksh_ump45[0]),
                str(total_ksh_ump45[2]),
                str(total_ksh_ump45[1]),
                str(round(total_ksh_ump45[0] / total_summ * 100, 2)) + '%'),
            (
                'XM1014',
                str(
                    round(total_ksh_xm1014[2] / total_ksh_xm1014[1] * 100, 2)
                ) + '%',
                str(
                    round(total_ksh_xm1014[0] / total_ksh_xm1014[2] * 100, 2)
                ) + '%',
                str(total_ksh_xm1014[0]),
                str(total_ksh_xm1014[2]),
                str(total_ksh_xm1014[1]),
                str(round(total_ksh_xm1014[0] / total_summ * 100, 2)) + '%'
            ))

    def get_wkey(self, finded, steamid):
        get_weapons = (
            f'date/{steamid}/{steamid}'
            f'_all_statistic_{TODAY}.json')

        try:
            open(get_weapons, 'r', encoding=UTF8)
        except FileNotFoundError:
            self.resault.write_json(
                requests.get(f'{GUSFG}{steamid}').json(),
                get_weapons)

        wstats = self.resault.open_json(get_weapons)
        finded_val = 0
        for count, item in enumerate(wstats['playerstats']['stats']):
            self.int_for_progressbar_w.emit(count, len(wstats))
            if item['name'] == finded:
                finded_val = item['value']
        return finded_val


class CheckFriendsThread(QtCore.QThread, MyWin, ProfileStatus):
    list_all_friends = QtCore.pyqtSignal(list)

    def __init__(self, parent=None):
        QtCore.QThread.__init__(self, parent)
        self.running = False
        self.get_vac_status = CheckVacThread()
        self.resault = ProfileStatus()

    def run(self):
        self.running = True
        all_fr_jsn = f'date/{STEAMID}/{STEAMID}_all_friend_list_{TODAY}.json'
        friend_info = []

        try:
            open(all_fr_jsn, 'r')
        except FileNotFoundError:
            self.resault.write_json(
                requests.get(GSF).json(),
                all_fr_jsn
            )

        fr_steam = self.resault.open_json(all_fr_jsn)
        friend_l = fr_steam['friendslist']['friends']
        for i in range(len(friend_l)):
            s_id_friend = (
                fr_steam
                ['friendslist']['friends'][i]['steamid'])
            friend_since_friend = (
                str(datetime.fromtimestamp(
                    fr_steam
                    ['friendslist']['friends'][i]['friend_since'])
                    ).split(' ')[0])

            vac_status = self.resault.check_vac_banned(s_id_friend)

            try:
                open(
                    f'date/{STEAMID}/{s_id_friend}.json',
                    'r',
                    encoding=UTF8
                )
            except FileNotFoundError:
                req_friends = requests.get(
                    f'{GPS}{s_id_friend}'
                ).json()
                friend_steamid_json = (
                    f'date/{STEAMID}/'
                    f'{req_friends["response"]["players"][0]["steamid"]}'
                    '.json')
                self.resault.write_json(
                    req_friends,
                    friend_steamid_json)
                friend = self.resault.open_json(friend_steamid_json)
                friend_info.append(
                    [
                        s_id_friend,
                        friend['response']['players'][0]['personaname'],
                        friend_since_friend,
                        (
                            'VAC БАН'
                            if vac_status['players'][0]['VACBanned']
                            else ''
                        ),
                        (
                            'Community Banned'
                            if vac_status['players'][0]['CommunityBanned']
                            else ''
                        ),
                        (
                            ''
                            if vac_status['players'][0]['EconomyBan'] == 'none'
                            else 'Economy Ban'
                        ),
                        (
                            str(vac_status['players'][0]['NumberOfGameBans'])
                            if vac_status['players'][0]['NumberOfGameBans']
                            else ''
                        )
                    ]
                )
                continue

            friend_steamid_json = (
                f'date/{STEAMID}/{s_id_friend}.json')

            friend = self.resault.open_json(friend_steamid_json)

            friend_info.append(
                [
                    s_id_friend,
                    friend['response']['players'][0]['personaname'],
                    friend_since_friend,
                    (
                        'VAC БАН'
                        if vac_status['players'][0]['VACBanned']
                        else ''
                    ),
                    (
                        'Community Banned'
                        if vac_status['players'][0]['CommunityBanned'] else ''
                    ),
                    (
                        ''
                        if vac_status['players'][0]['EconomyBan'] == 'none'
                        else 'Economy Ban'
                    ),
                    (
                        str(vac_status['players'][0]['NumberOfGameBans'])
                        if vac_status['players'][0]['NumberOfGameBans']
                        else ''
                    )
                ])
        self.list_all_friends.emit(friend_info)


class CheckVacThread(QtCore.QThread, MyWin):
    list_all_users = QtCore.pyqtSignal(list)
    message_toolbar_bans = QtCore.pyqtSignal(str)
    int_for_progressbar_vac = QtCore.pyqtSignal(int, int)

    def __init__(self, parent=None):
        QtCore.QThread.__init__(self, parent)
        self.running = False
        self.resault = ProfileStatus()

    def run(self):
        tmp_stmid = ''
        all_users = []
        vac_status = []
        tmp_users = []
        vacban_sts_all = []
        self.running = True
        date_match_users = self.resault.open_json(
            ALL_S
        )

        for count, _ in enumerate(date_match_users):
            for i in range(10):
                vacban_sts_all.append(
                    [
                        date_match_users[count]['team'][i]['steamid64'],
                        date_match_users[count]['date']
                    ]
                )

        for line in vacban_sts_all:
            if line not in all_users:
                all_users.append(line)

        self.resault = ProfileStatus()
        val = 0
        all_u = len(all_users)
        while self.running:
            tmp_stmid = all_users[val][0]
            vac_check = self.resault.check_vac_banned(tmp_stmid)
            if vac_check['players'] == []:
                tmp_stmid = '76561197997566454'
                vac_check = self.resault.check_vac_banned(tmp_stmid)
            vac_status.append(vac_check)
            self.int_for_progressbar_vac.emit(
                val,
                all_u)
            self.message_toolbar_bans.emit(
                'CheckVacThread: Загружаю данные, '
                f'с API Steam для: <{tmp_stmid}>'
                f' {val} из {all_u}'
            )
            resault = self.resault.get_profile_check(tmp_stmid)

            if resault is None:
                tmp_stmid = '76561197997566454'
                resault = self.resault.get_profile_check(tmp_stmid)

            name = resault['response']['players'][0]['personaname']
            day = vac_status[val]['players'][0]['DaysSinceLastBan']
            date_ban = TODAY - timedelta(days=day)
            if (
                str(all_users[val][1]) <= str(date_ban).split(' ')[0]
                and
                vac_status[val]['players'][0]['VACBanned']
            ):
                tmp_users.append(
                    [
                        tmp_stmid,
                        name,
                        str(all_users[val][1]),
                        (
                            'Забанен' if vac_status[val]
                            ['players'][0]['CommunityBanned'] else ''
                        ),
                        (
                            'Забанен' if vac_status[val]
                            ['players'][0]['VACBanned'] else ''
                        ),
                        (
                            str(
                                vac_status[val]
                                ['players'][0]
                                ['NumberOfVACBans']) if vac_status[val]
                            ['players'][0]['NumberOfVACBans'] else ''
                        ),
                        (
                            str(date_ban).split(' ')[0] if vac_status[val]
                            ['players'][0]
                            ['DaysSinceLastBan'] else f'Новый! {TODAY}'
                        ),
                        (
                            str(
                                vac_status[val]['players'][0]
                                ['NumberOfGameBans']) if vac_status[val]
                            ['players'][0]['NumberOfGameBans'] else ''
                        ),
                        (
                            '' if vac_status[val]
                            ['players'][0]['EconomyBan'] == 'none' else 'BAN')
                    ]
                )

            val += 1
            # ! добавляем данные в таблицу банов в реальном режиме.
            self.list_all_users.emit(tmp_users, )
            if val == len(all_users):
                self.list_all_users.emit(tmp_users, )
                self.running = False


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    myapp = MyWin()
    myapp.show()
    sys.exit(app.exec_())
