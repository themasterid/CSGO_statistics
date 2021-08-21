import json
import os
import sys
import webbrowser
from datetime import date, datetime, timedelta
from os import listdir
from os.path import isfile, join
from typing import List, Union

import requests
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtWidgets import QTableWidgetItem

from get_steam_avatar import create_avatar
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
TODAY = date.today()
UTF8 = 'utf-8'
ALL_S = 'all_stats/all_stats.json'

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


class MyWin(QtWidgets.QMainWindow):
    '''Main Window for application csstats.'''

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

        # STATS
        resault = self.get_info_profile(STEAMID)
        # ! print(resault)
        if (
            resault['response']['players'][0][CVS] == 1
        ):
            for i in range(1, 4):
                self.ui.tabWidget.setTabEnabled(i, False)
        elif (
            resault['response']['players'][0][CVS] == 3
        ):
            for i in range(1, 4):
                self.ui.tabWidget.setTabEnabled(i, True)

        self.ui.pushButton_update_stat.clicked.connect(self.get_statistics)
        self.ui.textBrowser_info.setText(
            self.get_table_statistics(STEAMID))

        # WEAPONS
        self.ui.pushButton_update_weapons.clicked.connect(
            self.on_start_weapons)
        self.ui.comboBox_weapons.activated.connect(self.open_table_weapons)
        self.ui.comboBox_weapons.addItems(
            self.get_items_combobox('all_weapons'))
        self.check_weapons_thread.list_all_weapons.connect(
            self.get_tables,
            QtCore.Qt.QueuedConnection)

        # FRIENDS
        self.ui.pushButton_update_friends.clicked.connect(
            self.on_start_friends)
        self.ui.comboBox_friends.activated.connect(self.open_table_friends)
        self.ui.comboBox_friends.addItems(
            self.get_items_combobox('all_friends'))
        self.check_friends_thread.list_all_friends.connect(
            self.get_tables,
            QtCore.Qt.QueuedConnection)
        self.ui.tableWidget_friends.itemDoubleClicked.connect(
            self.listwidgetclicked)

        # MATCHES
        self.ui.comboBox_matches.addItems(self.get_items_combobox_matches())
        self.ui.comboBox_matches.activated.connect(self.get_info_match)

        # BANS
        self.ui.pushButton_update_bans_start.clicked.connect(
            self.on_start_vacs)
        self.ui.pushButton_update_bans_stop.clicked.connect(self.on_stop_vacs)
        self.ui.comboBox_bans.activated.connect(self.open_table_bans)
        self.ui.comboBox_bans.addItems(self.get_items_combobox('all_bans'))
        self.check_vac_thread.list_all_users.connect(
            self.get_tables, QtCore.Qt.QueuedConnection)
        self.check_vac_thread.message_toolbar_bans.connect(
            self.on_change_check_vac, QtCore.Qt.QueuedConnection)
        self.check_vac_thread.int_for_progressbar_vac.connect(
            self.on_change_vac_rows, QtCore.Qt.QueuedConnection)
        self.ui.tableWidget_bans.itemDoubleClicked.connect(
            self.listwidgetclicked)

    # ! NOT DONE !
    # * open my profile by steamid
    def open_my_profile(self):
        (self.ui.tabWidget.setTabEnabled(i, True) for i in range(1, 4))
        self.ui.pushButton_update_stat.setEnabled(True)
        self.ui.label_rank.setPixmap(QPixmap(SG18))
        # ! self.get_info_profile(STEAMID)
        self.ui.textBrowser_info.setText(
            self.get_table_statistics(STEAMID))

    # ! NOT DONE !
    # * open steamid in browser
    def listwidgetclicked(self, item) -> Union[str, bool]:
        if len(item.text()) != 17:
            return 'ERR: not equal 17'

        try:
            int(item.text())
        except TypeError:
            return 'ERR: not int!'

        url: str = f'https://steamcommunity.com/profiles/{item.text()}'
        return webbrowser.open(url)

    # ! DONE !
    # * get items box for sort date
    def get_items_combobox(self, string_w: str) -> List[str]:
        # ! STEAMID GLOBAL CONST!
        path: str = f'date/{string_w}/{STEAMID}/'
        only_f: list = sorted(
            [f for f in listdir(path) if isfile(join(path, f))],
            reverse=True
        )
        return [i.split('.')[0] for i in only_f]

    # ! DONE !
    # * get items for combobox matches
    def get_items_combobox_matches(self) -> List[str]:
        match_items = self.open_json(ALL_S)
        return [(
            f'{vals + 1}) {match_items[vals]["date"]}'
            f', map | {match_items[vals]["competitive"]}'
            ' |') for vals in range(len(match_items))]

    def open_table_weapons(self):
        index_match_weapons = self.ui.comboBox_weapons.currentIndex()
        self.ui.tableWidget_weapons.clear()
        self.date_weapons = self.open_json(
            f'date/all_weapons/{STEAMID}/'
            f'{self.get_items_combobox("all_weapons")[index_match_weapons]}'
            '.json')
        self.ui.tableWidget_weapons.setColumnCount(len(self.date_weapons[0]))
        self.ui.tableWidget_weapons.setRowCount(len(self.date_weapons))
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

        self.ui.tableWidget_weapons.setGridStyle(1)
        self.ui.tableWidget_weapons.resizeColumnsToContents()

    def open_table_friends(self):
        index_match_friends = self.ui.comboBox_friends.currentIndex()
        self.ui.tableWidget_friends.clear()
        friend_info = self.open_json(
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

        rows_list = []
        for _ in range(len(friend_info)):
            rows_list.append(str(_ + 1))

        self.ui.tableWidget_friends.setVerticalHeaderLabels(rows_list)

        row = 0
        for tup in friend_info:
            col = 0
            for item in tup:
                cellinfo = QTableWidgetItem(item)
                cellinfo.setFlags(
                    QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)
                self.ui.tableWidget_friends.setItem(row, col, cellinfo)
                col += 1
            row += 1

        self.ui.tableWidget_friends.setGridStyle(1)
        self.ui.tableWidget_friends.resizeColumnsToContents()

    # ! NOT DONE !
    # * add bans in table
    def get_tables(self, list_s: list) -> None:
        """Заносим данные в таблицу банов/друзей/оружия."""
        strings: str = 'all_bans'
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
        all_users = self.open_json(
            f'date/all_bans/{STEAMID}/'
            f'{self.get_items_combobox("all_bans")[index_match]}'
            '.json')
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

        rows_list = []
        for _ in range(len(all_users)):
            rows_list.append(str(_ + 1))
        self.ui.tableWidget_weapons.setVerticalHeaderLabels(rows_list)

        row = 0
        for tup in all_users:
            col = 0
            for item in tup:
                cellinfo = QTableWidgetItem(item)
                cellinfo.setFlags(
                    QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)
                self.ui.tableWidget_bans.setItem(row, col, cellinfo)
                col += 1
            row += 1

        self.ui.tableWidget_bans.setGridStyle(1)
        self.ui.tableWidget_bans.resizeColumnsToContents()
        return

    def get_profile_check(self, steamid: str) -> str:
        steam_profile = (
            f'date/{steamid}/{steamid}'
            f'_profile_info_{TODAY}.json')
        url_pfile_inf = f'{GPS}{steamid}'
        directory = f"{steamid}"
        parent_dir = "date\\"
        path = os.path.join(
            parent_dir,
            directory)
        try:
            os.mkdir(path)
        except FileExistsError:
            pass

        try:
            open(
                f'date/{steamid}/{steamid}'
                '_profile_info_{TODAY}.json',
                'r')
        except FileNotFoundError:
            r_profile_inf = requests.get(url_pfile_inf).json()
            self.write_json_file(
                r_profile_inf,
                steam_profile)
            if r_profile_inf['response']['players'] == []:
                self.write_json_file(
                    'deleted',
                    f'date/deleted_/{steamid}'
                    f'_deleted_profile_info_{TODAY}.json')
                return 'Deleted'
            # 1 - the profile is not visible to you
            # (Private, Friends Only, etc),
            # 3 - the profile is "Public",
            # and the data is visible.
            # ! FIX OUTPUT DATA
            if r_profile_inf['response']['players'][0][CVS] == 1:
                self.write_json_file(
                    r_profile_inf,
                    steam_profile)
                return self.open_json(
                    steam_profile)
            elif r_profile_inf['response']['players'][0][CVS] == 3:
                self.write_json_file(
                    r_profile_inf,
                    steam_profile)
                return self.open_json(steam_profile)

        if os.path.exists(
            f'date/{steamid}/{steamid}'
            f'_profile_info_{TODAY}.json'
        ):
            return self.open_json(steam_profile)
        return 'Done'

    # Add thread GetInfoBanThread
    def get_info_match(self):
        file_mathes = ALL_S
        date_match = self.open_json(file_mathes)
        index_match = self.ui.comboBox_matches.currentIndex()

        competitive = (
            f"Карта {date_match[index_match]['competitive']}"
            )
        date_t = f"Дата {date_match[index_match]['date']}"
        self.waittime = (
            'Время ожидания ' + date_match[index_match]['wait_time']
            )
        self.matchduration = (
            'Время игры ' + date_match[index_match]['match_duration']
            )
        self.score = 'Счет ' + date_match[index_match]['score']
        self.score_center = date_match[index_match]['score']

        # FIX add all maps
        if date_match[index_match]['competitive'] == 'de_engage':
            pixmap = QPixmap('img/imgs_maps/de_engage.jpg')
            self.ui.label_image_map.setPixmap(pixmap)
        elif date_match[index_match]['competitive'] == 'Dust II':
            pixmap = QPixmap('img/imgs_maps/de_dust_2.jpg')
            self.ui.label_image_map.setPixmap(pixmap)
        elif date_match[index_match]['competitive'] == 'cs_office':
            pixmap = QPixmap('img/imgs_maps/cs_office.jpg')
            self.ui.label_image_map.setPixmap(pixmap)
        elif date_match[index_match]['competitive'] == 'Inferno':
            pixmap = QPixmap('img/imgs_maps/de_inferno.jpg')
            self.ui.label_image_map.setPixmap(pixmap)
        elif date_match[index_match]['competitive'] == 'Mirage':
            pixmap = QPixmap('img/imgs_maps/de_mirage.jpg')
            self.ui.label_image_map.setPixmap(pixmap)
        elif date_match[index_match]['competitive'] == 'de_vertigo':
            pixmap = QPixmap('img/imgs_maps/de_vertigo.jpg')
            self.ui.label_image_map.setPixmap(pixmap)
        elif date_match[index_match]['competitive'] == 'de_train':
            pixmap = QPixmap('img/imgs_maps/de_train.jpg')
            self.ui.label_image_map.setPixmap(pixmap)
        elif date_match[index_match]['competitive'] == 'de_ancient':
            pixmap = QPixmap('img/imgs_maps/de_ancient.jpg')
            self.ui.label_image_map.setPixmap(pixmap)
        elif date_match[index_match]['competitive'] == 'Cache':
            pixmap = QPixmap('img/imgs_maps/de_cache.jpg')
            self.ui.label_image_map.setPixmap(pixmap)
        elif date_match[index_match]['competitive'] == 'cs_apollo':
            pixmap = QPixmap('img/imgs_maps/cs_apollo.jpg')
            self.ui.label_image_map.setPixmap(pixmap)
        elif date_match[index_match]['competitive'] == 'Overpass':
            pixmap = QPixmap('img/imgs_maps/de_overpass.jpg')
            self.ui.label_image_map.setPixmap(pixmap)
        elif date_match[index_match]['competitive'] == 'Nuke':
            pixmap = QPixmap('img/imgs_maps/de_nuke.jpg')
            self.ui.label_image_map.setPixmap(pixmap)
        elif date_match[index_match]['competitive'] == 'Train':
            pixmap = QPixmap('img/imgs_maps/de_train.jpg')
            self.ui.label_image_map.setPixmap(pixmap)
        else:
            pixmap = QPixmap('img/imgs_maps/nomap.jpg')
            self.ui.label_image_map.setPixmap(pixmap)

        steamid_i = []
        name_i = []
        player_name_i = []
        vac_status = []
        for val in range(10):
            self.ui.progressBar_bans.setMaximum(9)
            self.ui.progressBar_bans.setProperty("value", val)
            steamid_i.append(
                date_match[index_match]['team'][val]['steamid64'])
            name_i.append(
                self.get_profile_check(
                    steamid_i[val]
                    )['response']['players'][0]['personaname'])
            create_avatar(steamid_i[val])
            vac_status.append(
                self.check_vac_thread.check_vac_banned(
                    steamid_i[val])['players'][0]['VACBanned'])
            player_name_i.append(
                date_match[index_match]['team'][val]['player_name'])

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
        self.ui.label_waittime.setText(self.waittime)
        self.ui.label_matchduration.setText(self.matchduration)
        self.ui.label_score.setText(self.score)

        if int(
            self.score_center.split(':')[0]
            ) < int(
            self.score_center.split(':')[1]
        ):
            self.score_center = 'Проиграли ' + self.score_center + ' Выиграли'
        elif int(
            self.score_center.split(':')[0]
            ) > int(
            self.score_center.split(':')[1]
        ):
            self.score_center = 'Выиграли ' + self.score_center + ' Проиграли'
        elif int(
            self.score_center.split(':')[0]
            ) == int(
            self.score_center.split(':')[1]
        ):
            self.score_center = 'Ничья ' + self.score_center + ' Ничья'

        self.ui.label_csore_center.setText(self.score_center)

        self.ui.pname1_avatar.setPixmap(
            QPixmap(f'date/{steamid_i[0]}/{steamid_i[0]}'
                    f'_avatarmedium_{TODAY}.jpg'))
        self.ui.pname2_avatar.setPixmap(
            QPixmap(f'date/{steamid_i[1]}/{steamid_i[1]}'
                    f'_avatarmedium_{TODAY}.jpg'))
        self.ui.pname3_avatar.setPixmap(
            QPixmap(f'date/{steamid_i[2]}/{steamid_i[2]}'
                    f'_avatarmedium_{TODAY}.jpg'))
        self.ui.pname4_avatar.setPixmap(
            QPixmap(f'date/{steamid_i[3]}/{steamid_i[3]}'
                    f'_avatarmedium_{TODAY}.jpg'))
        self.ui.pname5_avatar.setPixmap(
            QPixmap(f'date/{steamid_i[4]}/{steamid_i[4]}'
                    f'_avatarmedium_{TODAY}.jpg'))
        self.ui.pname6_avatar.setPixmap(
            QPixmap(f'date/{steamid_i[5]}/{steamid_i[5]}'
                    f'_avatarmedium_{TODAY}.jpg'))
        self.ui.pname7_avatar.setPixmap(
            QPixmap(f'date/{steamid_i[6]}/{steamid_i[6]}'
                    f'_avatarmedium_{TODAY}.jpg'))
        self.ui.pname8_avatar.setPixmap(
            QPixmap(f'date/{steamid_i[7]}/{steamid_i[7]}'
                    f'_avatarmedium_{TODAY}.jpg'))
        self.ui.pname9_avatar.setPixmap(
            QPixmap(f'date/{steamid_i[8]}/{steamid_i[8]}'
                    f'_avatarmedium_{TODAY}.jpg'))
        self.ui.pname10_avatar.setPixmap(
            QPixmap(f'date/{steamid_i[9]}/{steamid_i[9]}'
                    f'_avatarmedium_{TODAY}.jpg'))

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
        return

    def get_statistics(self):
        tmp_text_all = self.get_table_statistics(STEAMID)
        self.ui.textBrowser_info.setText(tmp_text_all)

    def get_info_profile(self, steamid: str):
        url_pfile_inf = f'{GPS}{steamid}'
        # ! STOP
        if self.check_profile(steamid) == 'ERR: not found!':
            return 'Not steamid'

        directory = f'{steamid}'
        parent_dir = 'date\\'
        path = os.path.join(parent_dir, directory)
        if os.path.exists(path):
            if os.path.isdir(path):
                # ! 'Объект найден'
                pass
        else:
            # ! 'Объект не найден'
            os.mkdir(path)

        # try:
        #    os.mkdir(path)
        # except FileExistsError:
        #    return '<папка создана>'

        try:
            open(
                f'date/{steamid}/{steamid}'
                f'_profile_info_{TODAY}.json', 'r'
                )
        except FileNotFoundError:
            r_profile_inf = requests.get(
                url_pfile_inf
                ).json()
            #  1 - the profile is not visible to you
            #  (Private, Friends Only, etc),
            #  3 - the profile is "Public",
            #  and the data is visible.
            if r_profile_inf['response']['players'][0][CVS] == 1:
                self.statusBar().showMessage(
                    'The profile is not visible to you'
                    ' (Private, Friends Only, etc)')
                steam_profile = (
                    f'date/{steamid}/{steamid}'
                    f'_profile_info_{TODAY}.json')
                self.profile_data_json = self.write_json_file(
                    r_profile_inf,
                    steam_profile)
            elif r_profile_inf['response']['players'][0][CVS] == 3:
                self.statusBar().showMessage(
                    'The profile is "Public", and the data is visible')
                steam_profile = (
                    f'date/{steamid}/{steamid}'
                    f'_profile_info_{TODAY}.json')
                self.profile_data_json = self.write_json_file(
                    r_profile_inf,
                    steam_profile)

        create_avatar(STEAMID)
        self.steamidprofile_json = (
            f'date/{steamid}/{steamid}'
            f'_profile_info_{TODAY}.json')
        self.profile_data_json = self.open_json(self.steamidprofile_json)

        #  0 - Offline, 1 - Online,
        #  2 - Busy,
        #  3 - Away,
        #  4 - Snooze,
        #  5 - looking to trade,
        #  6 - looking to play
        personastate = (
            self.profile_data_json['response']['players'][
                0]['personastate'])
        #  1 - the profile is not visible to you (Private, Friends Only, etc),
        #  3 - the profile is "Public", and the data is visible.
        communityvisibilitystate = (
            self.profile_data_json['response']['players'][0][CVS])
        if communityvisibilitystate == 1:
            for i in range(1, 4):
                self.ui.tabWidget.setTabEnabled(i, False)

            self.statusBar().showMessage(
                '1 - the profile is not visible to you'
                ' (Private, Friends Only, etc)')
            self.ui.label_avatar.setPixmap(
                QPixmap(f'date/{steamid}/{steamid}'
                        f'_avatarfull_{TODAY}.jpg'))
            self.ui.label_personaname.setText(
                self.profile_data_json
                ['response']['players'][0]
                ['personaname'] + ' (Приватный профиль)')
            return 'Done'

        elif communityvisibilitystate == 3:
            self.statusBar().showMessage(
                '3 - the profile is "Public", and the data is visible')
            if personastate == 1:
                self.online_status = " (Online)"
            elif personastate == 2:
                self.online_status = " (Online - Занят)"
            elif personastate == 3:
                self.online_status = " (Online - Отошел)"
            elif personastate == 4:
                self.online_status = " (Online - Спит)"
            elif personastate == 5:
                self.online_status = " (Online - Готов к обмену)"
            elif personastate == 6:
                self.online_status = " (Online - Готов играть)"
            else:
                self.online_status = " (Offline)"

            self.ui.label_avatar.setPixmap(
                QPixmap(f'date/{STEAMID}/{STEAMID}'
                        f'_avatarfull_{TODAY}.jpg'))
            self.ui.label_personaname.setText(
                self.profile_data_json
                ['response']['players'][0]['personaname'] + self.online_status)

            try:
                self.ui.label_realname.setText(
                    self.profile_data_json
                    ['response']['players'][0]['realname'])
            except KeyError:
                self.ui.label_realname.setText('██████████')

            self.ui.label_profileurl.setText(
                self.profile_data_json['response']['players'][0]['profileurl'])
            self.get_country_info(STEAMID)
            return self.profile_data_json

    def get_country_info(self, steamid):
        text_location = ""
        self.load_from_file = (
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

        url_pfile_inf = f'{GPS}{steamid}'
        directory = f"{steamid}"
        parent_dir = "date"
        path = os.path.join(parent_dir, directory)
        try:
            os.mkdir(path)
        except FileExistsError:
            pass

        try:
            open(self.load_from_file, 'r')
        except FileNotFoundError:
            self.req_profile = requests.get(url_pfile_inf).json()
            self.write_json_file(self.req_profile, self.load_from_file)
            self.profile_data_json = (
                self.open_json(self.load_from_file)
                )
            text_location = ''

        try:
            open(load_location_from_file_1, 'r')
        except FileNotFoundError:
            self.req_profile = requests.get(url_pfile_inf).json()
            self.write_json_file(self.req_profile, self.load_from_file)
            self.profile_data_json = self.open_json(self.load_from_file)

        try:
            loccountrycode = (
                self.profile_data_json
                ['response']['players'][0]['loccountrycode'])
            self.location_all_1 = (
                'https://steamcommunity.com/actions/QueryLocations/'
                )
            self.location_req_1 = requests.get(self.location_all_1).json()
            self.write_json_file(
                self.location_req_1,
                load_location_from_file_1)
            location_file_1 = self.open_json(
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
            self.write_json_file(
                self.location_req_2,
                self.load_location_from_file_2)
            self.location_file_2 = self.open_json(
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
            self.write_json_file(
                self.location_req_3,
                self.load_location_from_file_3)
            self.location_file_3 = self.open_json(
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
        self.profile_data_json = self.open_json(
            self.load_from_file)
        text_location = ''

        try:
            loccountrycode = (
                self.profile_data_json
                ['response']['players'][0]['loccountrycode'])
            location_file_1 = self.open_json(
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
                self.profile_data_json
                ['response']['players'][0]['locstatecode'])
            self.location_file_2 = self.open_json(
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
                self.profile_data_json['response']['players'][0]['loccityid']
            )
            self.location_file_3 = self.open_json(
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
        # ! FIX
        self.get_info_profile(steamid)
        create_avatar(steamid)
        self.file_profile_info = (
            f'date/{steamid}/{steamid}'
            f'_profile_info_{TODAY}.json'
        )
        url_profile_stat = f'{GPS}{steamid}'
        tmp_text_all = ''

        try:
            open(self.file_profile_info, 'r')
        except FileNotFoundError:
            f_pfile_info_req = requests.get(
                url_profile_stat).json()
            self.write_json_file(
                f_pfile_info_req,
                self.file_profile_info)

        if self.open_json(
            self.file_profile_info
        )['response']['players'] == []:
            self.statusBar().showMessage('ERR: 404 Not found!')
            return TEXT_NOT_FOUND

        #  * communityvisibilitystate
        #  * 1 - the profile is not visible to you (Private, Friends Only, etc)
        #  * 3 - the profile is "Public", and the data is visible.
        self.file_profile_info_json = self.open_json(
            self.file_profile_info
        )
        if self.file_profile_info_json['response']['players'][0][CVS] == 1:
            self.statusBar().showMessage(
                'The profile is not visible to'
                'you (Private, Friends Only, etc)')
            self.profile_data_json = self.open_json(
                self.file_profile_info)
            return NO_INFO_USERS
        elif self.file_profile_info_json['response']['players'][0][CVS] == 3:
            self.statusBar().showMessage(
                'The profile is "Public", and the data is visible')
            self.open_json(self.file_profile_info)

        self.profile_data_json = self.open_json(
            self.file_profile_info
            )

        # 0 - Offline,
        # 1 - Online,
        # 2 - Busy,
        # 3 - Away,
        # 4 - Snooze,
        # 5 - looking to trade,
        # 6 - looking to play
        personastate = self.file_profile_info_json[
            'response']['players'][0]['personastate']
        #  1 - the profile is not visible to you (Private, Friends Only, etc),
        #  3 - the profile is "Public", and the data is visible.
        communityvisibilitystate = (
            self.file_profile_info_json['response']['players'][0][CVS])

        if communityvisibilitystate == 1:
            self.statis_profile = "Закрытый"
            self.statusBar().showMessage(
                'The profile is not visible to you'
                '(Private, Friends Only, etc)'
            )
            # FIX THIS ADD AVATAR FROM DISC
            self.image = QImage()
            self.image.loadFromData(
                requests.get(
                    self.profile_data_json['response']['players'][0]['avatarfull']
                ).content)
            self.ui.label_avatar.setPixmap(QPixmap(self.image))
            self.ui.label_personaname.setText(
                self.profile_data_json['response']['players'][0]['personaname'] +
                ' (Приватный профиль)'
            )
            tmp_text_all = NO_INFO_USERS
            return tmp_text_all
        elif communityvisibilitystate == 3:
            self.statis_profile = "Открытый"
            self.statusBar().showMessage(
                'The profile is "Public", and the data is visible')
            if personastate == 1:
                self.online_status = " (Online)"
            elif personastate == 2:
                self.online_status = " (Online - Занят)"
            elif personastate == 3:
                self.online_status = " (Online - Отошел)"
            elif personastate == 4:
                self.online_status = " (Online - Спит)"
            elif personastate == 5:
                self.online_status = " (Online - Готов к обмену)"
            elif personastate == 6:
                self.online_status = " (Online - Готов играть)"
            else:
                self.online_status = " (Offline)"

        tmp_text_all += (
            'Стим ID - '
            f"{self.profile_data_json['response']['players'][0]['steamid']}\n"
            )
        tmp_text_all += f'Статус профиля - {self.statis_profile}\n'
        tmp_text_all += f'Статус Steam - {self.online_status}\n'
        tmp_name = (
            self.profile_data_json['response']
            ['players'][0]['personaname'])
        tmp_text_all += f"Никнейм - {str(tmp_name)}\n"
        tmp_pfile = (
            self.profile_data_json['response']
            ['players'][0]['profileurl'])
        tmp_text_all += f"Ссылка на профиль - {str(tmp_pfile)}\n"
        # TODO complite f-string next 3 rows
        # ! 06.08.2021
        try:
            tmp_text_all += 'Последний раз выходил - ' + str(datetime.fromtimestamp(self.profile_data_json['response']['players'][0]['lastlogoff'])) + "\n"
        except KeyError:
            tmp_text_all += 'Последний раз выходил - ██████████ \n'
        try:
            tmp_text_all += f'Реальное имя - {str(self.profile_data_json["response"]["players"][0]["realname"])}\n'
        except KeyError:
            tmp_text_all += 'Реальное имя - ██████████ \n'
        tmp_timec = (
            datetime.fromtimestamp(
                self.profile_data_json['response']
                ['players'][0]['timecreated'])
        )
        tmp_text_all += f'Дата создания профиля - {str(tmp_timec)}\n'
        tmp_text_all += (
            f"Страна - {self.ui.label_loccountrycode.text()}\n")

        return tmp_text_all

    def open_new_profile(self) -> str:
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
        if self.check_profile(steam_id) == 'ERR: not found!':
            return 'Not steamid'
        self.ui.textBrowser_info.setText(
            self.get_table_statistics(steam_id))
        return f'Steamid - {steam_id}'

    def check_profile(self, steamid: str) -> str:
        url_pfile_inf = f'{GPS}{steamid}'
        if requests.get(
            url_pfile_inf
                ).json()['response']['players'] == []:
            pixmap = QPixmap('img/error.jpg')
            self.ui.label_avatar.setPixmap(pixmap)
            self.ui.label_rank.setPixmap(pixmap)
            self.ui.label_personaname.setText('██████████')
            self.ui.label_realname.setText('██████████')
            self.ui.label_profileurl.setText('https://steamcommunity.com/')
            self.ui.label_loccountrycode.setText('██████████')
            self.statusBar().showMessage(
                'ERR: Not valid steamid!')
            self.ui.textBrowser_info.setText(TEXT_NOT_FOUND)
            for i in range(1, 5):
                self.ui.tabWidget.setTabEnabled(i, False)
            self.ui.pushButton_update_stat.setEnabled(False)
            return 'ERR: not found!'
        for i in range(1, 5):
            self.ui.tabWidget.setTabEnabled(i, True)
        self.ui.pushButton_update_stat.setEnabled(True)
        return 'OK'

    def click_avatar(self):
        webbrowser.open(self.ui.label_profileurl.text())

    def write_json_file(self, date_to_write, fname):
        self.date_to_write = date_to_write
        self.fname = fname
        with open(self.fname, 'w', encoding=UTF8) as self.write_json_file_:
            return json.dump(
                self.date_to_write,
                self.write_json_file_,
                ensure_ascii=False, indent=4)

    def open_json(self, fname):
        self.fname = fname
        try:
            open(self.fname, 'r', encoding=UTF8)
        except FileNotFoundError:
            print('ERR: file not found:', fname)
        with open(self.fname, 'r', encoding=UTF8) as self.read_json_file:
            return json.load(self.read_json_file)

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
        self.ui.progressBar_bans.setMaximum(all_users - 1)
        self.ui.progressBar_bans.setProperty(
            "value",
            self.info_progress_bar_vac)

    def close_event(self, event):
        self.hide()
        self.check_vac_thread.running = False
        self.check_vac_thread.wait(5000)
        event.accept()


class CheckWeaponsThread(QtCore.QThread, MyWin):
    list_all_weapons = QtCore.pyqtSignal(list)

    def __init__(self, parent=None):
        QtCore.QThread.__init__(self, parent)
        self.running = False

    def run(self):
        w_info = self.get_info_weapons(STEAMID)
        path = f'date/all_weapons/{STEAMID}/{TODAY}.json'
        if w_info == [('', '', '', '', '', '', '')]:
            return 'Error!'

        with open(path, 'w', encoding=UTF8) as fw:
            json.dump(w_info, fw, ensure_ascii=False, indent=4)
        return self.list_all_weapons.emit(w_info)

    def get_info_weapons(self, steamid):
        url_pfile_inf = f'{GPS}{steamid}'
        if (
            requests.get(url_pfile_inf).json()['response']
            ['players'][0][CVS] == 1
                ):
            return [('', '', '', '', '', '', '')]

        total_ksh_ak47 = [
            self.find_key_by_value('total_kills_ak47', steamid),
            self.find_key_by_value('total_shots_ak47', steamid),
            self.find_key_by_value('total_hits_ak47', steamid)]

        total_ksh_aug = [
            self.find_key_by_value('total_kills_aug', steamid),
            self.find_key_by_value('total_shots_aug', steamid),
            self.find_key_by_value('total_hits_aug', steamid)]

        total_ksh_awp = [
            self.find_key_by_value('total_kills_awp', steamid),
            self.find_key_by_value('total_shots_awp', steamid),
            self.find_key_by_value('total_hits_awp', steamid)]

        total_ksh_awp = [
            self.find_key_by_value('total_kills_awp', steamid),
            self.find_key_by_value('total_shots_awp', steamid),
            self.find_key_by_value('total_hits_awp', steamid)]

        total_ksh_deagle = [
            self.find_key_by_value('total_kills_deagle', steamid),
            self.find_key_by_value('total_shots_deagle', steamid),
            self.find_key_by_value('total_hits_deagle', steamid)]

        total_ksh_elite = [
            self.find_key_by_value('total_kills_elite', steamid),
            self.find_key_by_value('total_shots_elite', steamid),
            self.find_key_by_value('total_hits_elite', steamid)]

        total_ksh_famas = [
            self.find_key_by_value('total_kills_famas', steamid),
            self.find_key_by_value('total_shots_famas', steamid),
            self.find_key_by_value('total_hits_famas', steamid)]

        total_ksh_fiveseven = [
            self.find_key_by_value('total_kills_fiveseven', steamid),
            self.find_key_by_value('total_shots_fiveseven', steamid),
            self.find_key_by_value('total_hits_fiveseven', steamid)]

        total_ksh_g3sg1 = [
            self.find_key_by_value('total_kills_g3sg1', steamid),
            self.find_key_by_value('total_shots_g3sg1', steamid),
            self.find_key_by_value('total_hits_g3sg1', steamid)]

        total_ksh_galilar = [
            self.find_key_by_value('total_kills_galilar', steamid),
            self.find_key_by_value('total_shots_galilar', steamid),
            self.find_key_by_value('total_hits_galilar', steamid)]

        total_ksh_glock = [
            self.find_key_by_value('total_kills_glock', steamid),
            self.find_key_by_value('total_shots_glock', steamid),
            self.find_key_by_value('total_hits_glock', steamid)]

        total_ksh_m249 = [
            self.find_key_by_value('total_kills_m249', steamid),
            self.find_key_by_value('total_shots_m249', steamid),
            self.find_key_by_value('total_hits_m249', steamid)]

        total_ksh_m4a1 = [
            self.find_key_by_value('total_kills_m4a1', steamid),
            self.find_key_by_value('total_shots_m4a1', steamid),
            self.find_key_by_value('total_hits_m4a1', steamid)]

        total_ksh_mac10 = [
            self.find_key_by_value('total_kills_mac10', steamid),
            self.find_key_by_value('total_shots_mac10', steamid),
            self.find_key_by_value('total_hits_mac10', steamid)]

        total_ksh_mag7 = [
            self.find_key_by_value('total_kills_mag7', steamid),
            self.find_key_by_value('total_shots_mag7', steamid),
            self.find_key_by_value('total_hits_mag7', steamid)]

        total_ksh_mp7 = [
            self.find_key_by_value('total_kills_mp7', steamid),
            self.find_key_by_value('total_shots_mp7', steamid),
            self.find_key_by_value('total_hits_mp7', steamid)]

        total_ksh_mp9 = [
            self.find_key_by_value('total_kills_mp9', steamid),
            self.find_key_by_value('total_shots_mp9', steamid),
            self.find_key_by_value('total_hits_mp9', steamid)]

        total_ksh_negev = [
            self.find_key_by_value('total_kills_negev', steamid),
            self.find_key_by_value('total_shots_negev', steamid),
            self.find_key_by_value('total_hits_negev', steamid)]

        total_ksh_nova = [
            self.find_key_by_value('total_kills_nova', steamid),
            self.find_key_by_value('total_shots_nova', steamid),
            self.find_key_by_value('total_hits_nova', steamid)]

        total_ksh_hkp2000 = [
            self.find_key_by_value('total_kills_hkp2000', steamid),
            self.find_key_by_value('total_shots_hkp2000', steamid),
            self.find_key_by_value('total_hits_hkp2000', steamid)]

        total_ksh_p250 = [
            self.find_key_by_value('total_kills_p250', steamid),
            self.find_key_by_value('total_shots_p250', steamid),
            self.find_key_by_value('total_hits_p250', steamid)]

        total_ksh_p90 = [
            self.find_key_by_value('total_kills_p90', steamid),
            self.find_key_by_value('total_shots_p90', steamid),
            self.find_key_by_value('total_hits_p90', steamid)]

        total_ksh_bizon = [
            self.find_key_by_value('total_kills_bizon', steamid),
            self.find_key_by_value('total_shots_bizon', steamid),
            self.find_key_by_value('total_hits_bizon', steamid)]

        total_ksh_sawedoff = [
            self.find_key_by_value('total_kills_sawedoff', steamid),
            self.find_key_by_value('total_shots_sawedoff', steamid),
            self.find_key_by_value('total_hits_sawedoff', steamid)]

        total_ksh_scar20 = [
            self.find_key_by_value('total_kills_scar20', steamid),
            self.find_key_by_value('total_shots_scar20', steamid),
            self.find_key_by_value('total_hits_scar20', steamid)]

        total_ksh_sg556 = [
            self.find_key_by_value('total_kills_sg556', steamid),
            self.find_key_by_value('total_shots_sg556', steamid),
            self.find_key_by_value('total_hits_sg556', steamid)]

        total_ksh_ssg08 = [
            self.find_key_by_value('total_kills_ssg08', steamid),
            self.find_key_by_value('total_shots_ssg08', steamid),
            self.find_key_by_value('total_hits_ssg08', steamid)]

        total_ksh_tec9 = [
            self.find_key_by_value('total_kills_tec9', steamid),
            self.find_key_by_value('total_shots_tec9', steamid),
            self.find_key_by_value('total_hits_tec9', steamid)]

        total_ksh_ump45 = [
            self.find_key_by_value('total_kills_ump45', steamid),
            self.find_key_by_value('total_shots_ump45', steamid),
            self.find_key_by_value('total_hits_ump45', steamid)]

        total_ksh_xm1014 = [
            self.find_key_by_value('total_kills_xm1014', steamid),
            self.find_key_by_value('total_shots_xm1014', steamid),
            self.find_key_by_value('total_hits_xm1014', steamid)]

        total_summ = sum([
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
            total_ksh_xm1014[0]]
        )

        self.date_weapons = [
            (
                'AK-47',
                str(round(total_ksh_ak47[2] / total_ksh_ak47[1] * 100, 2)
                    ) + '%',
                str(
                    round(total_ksh_ak47[0] / total_ksh_ak47[2] * 100, 2)
                    ) + '%',
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
                str(round(total_ksh_elite[2] /
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
                    round(total_ksh_famas[2] / total_ksh_famas[1] * 100, 2)
                    ) + '%',
                str(
                    round(total_ksh_famas[0] / total_ksh_famas[2] * 100, 2)
                    ) + '%',
                str(total_ksh_famas[0]),
                str(total_ksh_famas[2]),
                str(total_ksh_famas[1]),
                str(round(total_ksh_famas[0] / total_summ * 100, 2)) + '%'),
            (
                'Five-SeveN',
                str(round(
                    total_ksh_fiveseven[2] / total_ksh_fiveseven[1] * 100, 2
                    )
                    ) + '%',
                str(round(
                    total_ksh_fiveseven[0] / total_ksh_fiveseven[2] * 100, 2
                    )
                    ) + '%',
                str(total_ksh_fiveseven[0]),
                str(total_ksh_fiveseven[2]),
                str(total_ksh_fiveseven[1]),
                str(
                    round(
                        total_ksh_fiveseven[0] / total_summ * 100, 2
                        )) + '%'),
            ('G3SG1',
             str(round(total_ksh_g3sg1[2] /
                       total_ksh_g3sg1[1] * 100, 2)) + '%',
             str(round(total_ksh_g3sg1[0] /
                       total_ksh_g3sg1[2] * 100, 2)) + '%',
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
            ('Glock-18',
             str(round(total_ksh_glock[2] /
                       total_ksh_glock[1] * 100, 2)) + '%',
             str(round(total_ksh_glock[0] /
                       total_ksh_glock[2] * 100, 2)) + '%',
             str(total_ksh_glock[0]),
             str(total_ksh_glock[2]),
             str(total_ksh_glock[1]),
             str(round(total_ksh_glock[0] / total_summ * 100, 2)) + '%'),
            ('M249',
             str(round(total_ksh_m249[2] / total_ksh_m249[1] * 100, 2)) + '%',
             str(round(total_ksh_m249[0] / total_ksh_m249[2] * 100, 2)) + '%',
             str(total_ksh_m249[0]),
             str(total_ksh_m249[2]),
             str(total_ksh_m249[1]),
             str(round(total_ksh_m249[0] / total_summ * 100, 2)) + '%'),
            ('M4A4/M4A1-S',
             str(round(total_ksh_m4a1[2] / total_ksh_m4a1[1] * 100, 2)) + '%',
             str(round(total_ksh_m4a1[0] / total_ksh_m4a1[2] * 100, 2)) + '%',
             str(total_ksh_m4a1[0]),
             str(total_ksh_m4a1[2]),
             str(total_ksh_m4a1[1]),
             str(round(total_ksh_m4a1[0] / total_summ * 100, 2)) + '%'),
            ('MAC-10',
             str(round(total_ksh_mac10[2] /
                       total_ksh_mac10[1] * 100, 2)) + '%',
             str(round(total_ksh_mac10[0] /
                       total_ksh_mac10[2] * 100, 2)) + '%',
             str(total_ksh_mac10[0]),
             str(total_ksh_mac10[2]),
             str(total_ksh_mac10[1]),
             str(round(total_ksh_mac10[0] / total_summ * 100, 2)) + '%'),
            ('MAG7',
             str(round(total_ksh_mag7[2] / total_ksh_mag7[1] * 100, 2)) + '%',
             str(round(total_ksh_mag7[0] / total_ksh_mag7[2] * 100, 2)) + '%',
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
             str(round(total_ksh_nova[2] / total_ksh_nova[1] * 100, 2)) + '%',
             str(round(total_ksh_nova[0] / total_ksh_nova[2] * 100, 2)) + '%',
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
             str(round(total_ksh_p250[2] / total_ksh_p250[1] * 100, 2)) + '%',
             str(round(total_ksh_p250[0] / total_ksh_p250[2] * 100, 2)) + '%',
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
            ('SSG 08',
             str(round(total_ksh_ssg08[2] /
                       total_ksh_ssg08[1] * 100, 2)) + '%',
             str(round(total_ksh_ssg08[0] /
                       total_ksh_ssg08[2] * 100, 2)) + '%',
             str(total_ksh_ssg08[0]),
             str(total_ksh_ssg08[2]),
             str(total_ksh_ssg08[1]),
             str(round(total_ksh_ssg08[0] / total_summ * 100, 2)) + '%'),
            ('TEC9',
             str(round(total_ksh_tec9[2] / total_ksh_tec9[1] * 100, 2)) + '%',
             str(round(total_ksh_tec9[0] / total_ksh_tec9[2] * 100, 2)) + '%',
             str(total_ksh_tec9[0]),
             str(total_ksh_tec9[2]),
             str(total_ksh_tec9[1]),
             str(round(total_ksh_tec9[0] / total_summ * 100, 2)) + '%'),
            ('UMP45',
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
            )]
        return self.date_weapons

    def find_key_by_value(self, finded, steamid):
        url_statistic = f'{GUSFG}{steamid}'
        get_statistic_json = (
            f'date/{steamid}/{steamid}'
            f'_all_statistic_{TODAY}.json')

        if requests.get(url_statistic).status_code == 500:
            return 'Error 500'

        try:
            open(get_statistic_json, 'r', encoding=UTF8)
        except FileNotFoundError:
            self.req_statistic = requests.get(url_statistic).json()
            self.write_json_file(self.req_statistic, get_statistic_json)

        self.statistic_file_json = self.open_json(get_statistic_json)
        finded_val = 0
        for _ in self.statistic_file_json['playerstats']['stats']:
            if _['name'] == finded:
                finded_val = _['value']
        return finded_val


class CheckFriendsThread(QtCore.QThread, MyWin):
    list_all_friends = QtCore.pyqtSignal(list)

    def __init__(self, parent=None):
        QtCore.QThread.__init__(self, parent)
        self.running = False
        self.get_vac_status = CheckVacThread()

    def run(self):
        self.running = True
        url_frs = f'{GPS}{STEAMID}'
        all_fr_jsn = f'date/{STEAMID}/{STEAMID}_all_friend_list_{TODAY}.json'
        friend_info = []
        try:
            open(all_fr_jsn, 'r')
        except FileNotFoundError:
            req_friends = requests.get(url_frs).json()
            self.write_json_file(req_friends, all_fr_jsn)

        if self.get_profile_check(STEAMID) == 'Deleted':
            return [('', '', '', '', '', '', '')]

        fr_steam = self.open_json(all_fr_jsn)

        try:
            fr_steam['friendslist']['friends']
        except KeyError:
            return 'Скрытый профиль!'

        friend_l = fr_steam['friendslist']['friends']
        for i in range(len(friend_l)):
            s_id_friend = (
                fr_steam
                ['friendslist']['friends'][i]['steamid'])
            self.friend_since_friend = (
                str(datetime.fromtimestamp(
                    fr_steam
                    ['friendslist']['friends'][i]['friend_since'])
                    ).split(' ')[0])
            vac_status = (
                self.get_vac_status.check_vac_banned(
                    s_id_friend))
            self.url_friend_info = f'{GPS}{s_id_friend}'
            try:
                open(f'date/{STEAMID}/{s_id_friend}.json', 'r', encoding=UTF8)
            except FileNotFoundError:
                self.req_friends = requests.get(self.url_friend_info).json()
                self.friend_steamid_json = (
                    f"date/{STEAMID}/"
                    f"{self.req_friends['response']['players'][0]['steamid']}"
                    ".json")
                self.write_json_file(
                    self.req_friends,
                    self.friend_steamid_json)
                self.friend = self.open_json(self.friend_steamid_json)
                friend_info.append(
                    [
                        s_id_friend,
                        self.friend['response']['players'][0]['personaname'],
                        self.friend_since_friend,
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

            self.friend_steamid_json = (
                f'date/{STEAMID}/{s_id_friend}.json')
            self.friend = self.open_json(self.friend_steamid_json)
            friend_info.append(
                [
                    s_id_friend,
                    self.friend['response']['players'][0]['personaname'],
                    self.friend_since_friend,
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
        self.running: bool = False

    def run(self) -> None:
        tmp_stmid: str = ''
        all_users = []
        vac_status = []
        tmp_users = []
        val: int = 0
        vacban_sts_all: list = []
        self.running = True
        date_match_users = self.open_json(
            ALL_S
            )

        for count in range(len(date_match_users)):
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

        while self.running:
            vac_status.append(
                self.check_vac_banned(all_users[val][0]))
            tmp_stmid = all_users[val][0]
            self.int_for_progressbar_vac.emit(
                val,
                len(all_users))
            try:
                name = self.open_json(
                    f'date/{tmp_stmid}/{tmp_stmid}'
                    f'_profile_info_{TODAY}.json'
                    )['response']['players'][0]['personaname']
            except IndexError:
                tmp_stmid = '76561197997566454'
                name = self.open_json(
                    f'date/{tmp_stmid}/{tmp_stmid}'
                    f'_profile_info_{TODAY}.json'
                    )['response']['players'][0]['personaname']

            day = vac_status[val]['players'][0]['DaysSinceLastBan']
            date_ban = TODAY - timedelta(days=day)
            if (
                str(all_users[val][1]) <= str(date_ban).split(' ')[0]
            ) and vac_status[val]['players'][0]['VACBanned']:
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
            # ! добавляем данные в таблицу банов в реальном реиме.
            self.list_all_users.emit(tmp_users, )
            if val == len(all_users):
                self.list_all_users.emit(tmp_users, )
                self.running = False

    def check_vac_banned(self, steamid):
        self.file_bans_users = (
            f'date/{steamid}/{steamid}'
            f'_ban_status_{TODAY}.json')

        url_steam_bans = f'{GPB}{steamid}'
        directory = f'{steamid}'
        parent_dir = f'date\\{steamid}'
        path = os.path.join(parent_dir, directory)
        self.get_profile_status(steamid)

        try:
            os.mkdir(path)
        except FileExistsError:
            pass

        try:
            open(
                f'date/{steamid}/{steamid}'
                f'_ban_status_{TODAY}.json', 'r')
        except FileNotFoundError:
            self.message_toolbar_bans.emit(steamid)
            self.request_bans = requests.get(url_steam_bans).json()
            self.write_json_file(self.request_bans, self.file_bans_users)
            return self.open_json(self.file_bans_users)

        self.message_toolbar_bans.emit(steamid)
        return self.open_json(self.file_bans_users)

    def get_profile_status(self, steamid):
        steam_profile = (
            f'date/{steamid}/{steamid}'
            f'_profile_info_{TODAY}.json')

        url_pfile_inf = f'{GPS}{steamid}'
        directory = f'{steamid}'
        parent_dir = 'date\\'
        path = os.path.join(parent_dir, directory)
        try:
            os.mkdir(path)
        except FileExistsError:
            pass

        try:
            open(steam_profile, 'r')
        except FileNotFoundError:
            r_profile_inf = requests.get(url_pfile_inf).json()
            self.write_json_file(
                r_profile_inf,
                steam_profile)
            # communityvisibilitystate 1
            # - the profile is not visible to
            # you (Private, Friends Only, etc),
            # communityvisibilitystate 3
            #  - the profile is 'Public', and the data is visible.
            if r_profile_inf['response']['players'] == []:
                self.write_json_file(
                    'deleted',
                    f'date/deleted_/{steamid}'
                    f'_deleted_profile_info_{TODAY}.json')
                return 0
            if r_profile_inf['response']['players'][0][CVS] == 1:
                self.write_json_file(
                    r_profile_inf,
                    steam_profile)
                return self.open_json(
                    steam_profile)
            elif r_profile_inf['response']['players'][0][CVS] == 3:
                self.write_json_file(
                    r_profile_inf,
                    steam_profile)
                return self.open_json(
                    steam_profile)

        if os.path.exists(steam_profile):
            return self.open_json(steam_profile)
        return 'Done'


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    myapp = MyWin()
    myapp.show()
    sys.exit(app.exec_())
