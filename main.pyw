import json
import sys
import os
from os.path import isfile, join
#from datetime import date
from os import listdir
from datetime import datetime
import webbrowser
import requests

from PyQt5 import QtWidgets, QtCore
from PyQt5.QtWidgets import QTableWidgetItem
from PyQt5.QtGui import QImage, QPixmap


from res.mainwindows import Ui_MainWindow
#from res.codes import keys

from res.constants import (
    TEXT_NOT_FOUND, NO_INFO_USERS,
    STEAMID, KEY, KEY_STEAMID, CVS, GPS,
    GUSFG, GPB, TODAY, UTF8)

from get_steam_avatar import create_avatar
from MainCheckVacThread import CheckVacThread
from MainCheckFriendsThread import CheckFriendsThread


class MyWin(QtWidgets.QMainWindow):
    """Main Window for application csstats."""

    def __init__(self, parent=None):
        QtWidgets.QWidget.__init__(self, parent)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.pixmap_rank = QPixmap('img/ranks/skillgroup0.png')
        self.ui.label_rank.setPixmap(self.pixmap_rank)
        self.ui.lineEdit_steamidfind.setInputMask(KEY_STEAMID)
        self.ui.lineEdit_steamidfind.setText('Введите Steam ID')
        self.check_vac_thread = CheckVacThread()
        self.check_friends_thread = CheckFriendsThread()
        self.check_weapons_thread = CheckWeaponsThread()
        self.ui.commandLinkButton_openurl.clicked.connect(self.click_avatar)
        self.ui.pushButton.clicked.connect(self.open_new_profile)
        self.ui.pushButton_my_profile.clicked.connect(self.open_my_profile)

        # STATS
        self.get_info_profile(STEAMID)
        if (
            self.get_info_profile(STEAMID)
            ['response']['players'][0][CVS] == 1
        ):
            for i in range(1, 4):
                self.ui.tabWidget.setTabEnabled(i, False)
        elif (
            self.get_info_profile(STEAMID)
            ['response']['players'][0][CVS] == 3
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

    def open_my_profile(self):
        (self.ui.tabWidget.setTabEnabled(i, True) for i in range(1, 4))
        self.ui.pushButton_update_stat.setEnabled(True)
        self.pixmap_rank = QPixmap('img/ranks/skillgroup1.png')
        self.ui.label_rank.setPixmap(self.pixmap_rank)
        self.get_info_profile(STEAMID)
        self.ui.textBrowser_info.setText(
            self.get_table_statistics(STEAMID))

    def listwidgetclicked(self, item) -> str:
        try:
            int(item.text())
        except TypeError:
            return 'not int'

        if len(item.text()) != 17:
            return 'error not equal 17'

        self.url = f"https://steamcommunity.com/profiles/{item.text()}"
        return webbrowser.open(self.url)

    def get_items_combobox(self, string_w):
        self.onlyfiles = sorted([
            self.f for self.f in listdir(
                    f'date/{string_w}/{STEAMID}/'
            ) if isfile(join(f'date/{string_w}/{STEAMID}/', self.f))
        ], reverse=True)

        self.list_files = []
        for self.files_i in self.onlyfiles:
            self.list_files.append(self.files_i.split('.')[0])
        return self.list_files

    def get_items_combobox_matches(self):
        self.match_items_data = self.open_json_file('all_stats/all_stats.json')
        self.match_items = []
        for vals, items in enumerate(self.match_items_data):
            self.match_items.append(
                str(vals + 1) + ") " + self.match_items_data[
                    vals]['date'] + ", map |" + self.match_items_data[
                        vals]['competitive'] + "|")
        return self.match_items

    def open_table_weapons(self):
        index_match_weapons = self.ui.comboBox_weapons.currentIndex()
        self.ui.tableWidget_weapons.clear()
        self.date_weapons = self.open_json_file(
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
        friend_info = self.open_json_file(
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

    def get_tables(self, list_s):
        strings = 'all_bans'
        with open(
            f'date/{strings}/{STEAMID}/{TODAY}.json',
            'w', encoding=UTF8
        ) as self.file_all:
            return json.dump(
                list_s,
                self.file_all,
                ensure_ascii=False,
                indent=4)

    def open_table_bans(self):
        index_match = self.ui.comboBox_bans.currentIndex()
        self.ui.tableWidget_bans.clear()
        all_users = self.open_json_file(
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

    def get_profile_check(self, STEAMID):
        steamid_profile_json = (
            f'date/{STEAMID}/{STEAMID}'
            f'_profile_info_{TODAY}.json')
        url_pfile_inf = f'{GPS}{STEAMID}'
        self.directory = f"{STEAMID}"
        self.parent_dir = "date\\"
        self.path = os.path.join(
            self.parent_dir,
            self.directory)
        try:
            os.mkdir(self.path)
        except FileExistsError:
            pass

        try:
            open(
                f'date/{STEAMID}/{STEAMID}'
                '_profile_info_{TODAY}.json',
                'r')
        except FileNotFoundError:
            self.req_profile_info = requests.get(url_pfile_inf).json()
            self.write_json_file(
                self.req_profile_info,
                steamid_profile_json)
            if self.req_profile_info['response']['players'] == []:
                self.write_json_file(
                    'deleted',
                    f'date/deleted_/{STEAMID}'
                    f'_deleted_profile_info_{TODAY}.json')
                return 0
            # 1 - the profile is not visible to you
            # (Private, Friends Only, etc),
            # 3 - the profile is "Public",
            # and the data is visible.
            # FIX OUTPUT DATA
            if self.req_profile_info['response']['players'][0][CVS] == 1:
                self.write_json_file(
                    self.req_profile_info,
                    steamid_profile_json)
                return self.open_json_file(
                    steamid_profile_json)
            elif self.req_profile_info['response']['players'][0][CVS] == 3:
                self.write_json_file(
                    self.req_profile_info,
                    steamid_profile_json)
                return self.open_json_file(steamid_profile_json)

        if os.path.exists(
            f'date/{STEAMID}/{STEAMID}'
            f'_profile_info_{TODAY}.json'
        ):
            return self.open_json_file(steamid_profile_json)

    # Add thread GetInfoBanThread
    def get_info_match(self):
        file_mathes = 'all_stats/all_stats.json'
        date_match = self.open_json_file(file_mathes)
        index_match = self.ui.comboBox_matches.currentIndex()

        self.competitive = (
            'Карта ' + date_match[index_match]['competitive']
            )
        self.date = (
            'Дата ' + date_match[index_match]['date']
            )
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
            'Забанен VAC' if vac_status[0] else 'Банов нет')
        self.ui.label_vac_status_2.setText(
            'Забанен VAC' if vac_status[1] else 'Банов нет')
        self.ui.label_vac_status_3.setText(
            'Забанен VAC' if vac_status[2] else 'Банов нет')
        self.ui.label_vac_status_4.setText(
            'Забанен VAC' if vac_status[3] else 'Банов нет')
        self.ui.label_vac_status_5.setText(
            'Забанен VAC' if vac_status[4] else 'Банов нет')
        self.ui.label_vac_status_6.setText(
            'Забанен VAC' if vac_status[5] else 'Банов нет')
        self.ui.label_vac_status_7.setText(
            'Забанен VAC' if vac_status[6] else 'Банов нет')
        self.ui.label_vac_status_8.setText(
            'Забанен VAC' if vac_status[7] else 'Банов нет')
        self.ui.label_vac_status_9.setText(
            'Забанен VAC' if vac_status[8] else 'Банов нет')
        self.ui.label_vac_status_10.setText(
            'Забанен VAC' if vac_status[9] else 'Банов нет')

        self.ui.label_competitive.setText(self.competitive)
        self.ui.label_date.setText(self.date)
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

        self.ui.label_playername1_avatar.setPixmap(
            QPixmap(f'date/{steamid_i[0]}/{steamid_i[0]}'
                    f'_avatarmedium_{TODAY}.jpg'))
        self.ui.label_playername2_avatar.setPixmap(
            QPixmap(f'date/{steamid_i[1]}/{steamid_i[1]}'
                    f'_avatarmedium_{TODAY}.jpg'))
        self.ui.label_playername3_avatar.setPixmap(
            QPixmap(f'date/{steamid_i[2]}/{steamid_i[2]}'
                    f'_avatarmedium_{TODAY}.jpg'))
        self.ui.label_playername4_avatar.setPixmap(
            QPixmap(f'date/{steamid_i[3]}/{steamid_i[3]}'
                    f'_avatarmedium_{TODAY}.jpg'))
        self.ui.label_playername5_avatar.setPixmap(
            QPixmap(f'date/{steamid_i[4]}/{steamid_i[4]}'
                    f'_avatarmedium_{TODAY}.jpg'))
        self.ui.label_playername6_avatar.setPixmap(
            QPixmap(f'date/{steamid_i[5]}/{steamid_i[5]}'
                    f'_avatarmedium_{TODAY}.jpg'))
        self.ui.label_playername7_avatar.setPixmap(
            QPixmap(f'date/{steamid_i[6]}/{steamid_i[6]}'
                    f'_avatarmedium_{TODAY}.jpg'))
        self.ui.label_playername8_avatar.setPixmap(
            QPixmap(f'date/{steamid_i[7]}/{steamid_i[7]}'
                    f'_avatarmedium_{TODAY}.jpg'))
        self.ui.label_playername9_avatar.setPixmap(
            QPixmap(f'date/{steamid_i[8]}/{steamid_i[8]}'
                    f'_avatarmedium_{TODAY}.jpg'))
        self.ui.label_playername10_avatar.setPixmap(
            QPixmap(f'date/{steamid_i[9]}/{steamid_i[9]}'
                    f'_avatarmedium_{TODAY}.jpg'))

        self.ui.label_playername1.setText(name_i[0])
        self.ui.label_playername2.setText(name_i[1])
        self.ui.label_playername3.setText(name_i[2])
        self.ui.label_playername4.setText(name_i[3])
        self.ui.label_playername5.setText(name_i[4])
        self.ui.label_playername6.setText(name_i[5])
        self.ui.label_playername7.setText(name_i[6])
        self.ui.label_playername8.setText(name_i[7])
        self.ui.label_playername9.setText(name_i[8])
        self.ui.label_playername10.setText(name_i[9])

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
        self.get_info_profile(STEAMID)
        tmp_text_all = self.get_table_statistics(STEAMID)
        self.ui.textBrowser_info.setText(tmp_text_all)

    def get_info_profile(self, STEAMID):
        url_pfile_inf = f'{GPS}{STEAMID}'
        self.check_profile(STEAMID)

        self.directory = f'{STEAMID}'
        self.parent_dir = 'date\\'
        self.path = os.path.join(self.parent_dir, self.directory)
        try:
            os.mkdir(self.path)
        except FileExistsError:
            pass

        try:
            open(
                f'date/{STEAMID}/{STEAMID}'
                f'_profile_info_{TODAY}.json', 'r'
                )
        except FileNotFoundError:
            self.req_profile_info = requests.get(
                url_pfile_inf
                ).json()
            #  1 - the profile is not visible to you
            #  (Private, Friends Only, etc),
            #  3 - the profile is "Public",
            #  and the data is visible.
            if self.req_profile_info['response']['players'][0][CVS] == 1:
                self.statusBar().showMessage(
                    'The profile is not visible to you'
                    ' (Private, Friends Only, etc)')
                steamid_profile_json = (
                    f'date/{STEAMID}/{STEAMID}'
                    f'_profile_info_{TODAY}.json')
                self.profile_data_json = self.write_json_file(
                    self.req_profile_info,
                    steamid_profile_json)
            elif self.req_profile_info['response']['players'][0][CVS] == 3:
                self.statusBar().showMessage(
                    'The profile is "Public", and the data is visible')
                steamid_profile_json = (
                    f'date/{STEAMID}/{STEAMID}'
                    f'_profile_info_{TODAY}.json')
                self.profile_data_json = self.write_json_file(
                    self.req_profile_info,
                    steamid_profile_json)

        create_avatar(STEAMID)
        self.steamidprofile_json = (
            f'date/{STEAMID}/{STEAMID}'
            f'_profile_info_{TODAY}.json')
        self.profile_data_json = self.open_json_file(self.steamidprofile_json)

        #  0 - Offline, 1 - Online,
        #  2 - Busy,
        #  3 - Away,
        #  4 - Snooze,
        #  5 - looking to trade,
        #  6 - looking to play
        self.personastate = (
            self.profile_data_json['response']['players'][
                0]['personastate'])
        #  1 - the profile is not visible to you (Private, Friends Only, etc),
        #  3 - the profile is "Public", and the data is visible.
        self.communityvisibilitystate = (
            self.profile_data_json['response']['players'][0][CVS])
        if self.communityvisibilitystate == 1:
            for i in range(1, 4):
                self.ui.tabWidget.setTabEnabled(i, False)

            self.statusBar().showMessage(
                '1 - the profile is not visible to you'
                ' (Private, Friends Only, etc)')
            self.ui.label_avatar.setPixmap(
                QPixmap(f'date/{STEAMID}/{STEAMID}'
                        f'_avatarfull_{TODAY}.jpg'))
            self.ui.label_personaname.setText(
                self.profile_data_json
                ['response']['players'][0]
                ['personaname'] + ' (Приватный профиль)')
            return 'Done'

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
            f'date/{STEAMID}/{STEAMID}'
            f'_profile_info_{TODAY}.json')
        self.load_location_from_file_1 = (
            f'date/{STEAMID}/{STEAMID}'
            f'_profile_location_1_{TODAY}.json')
        self.load_location_from_file_2 = (
            f'date/{STEAMID}/{STEAMID}'
            f'_profile_location_2_{TODAY}.json')
        self.load_location_from_file_3 = (
            f'date/{STEAMID}/{STEAMID}'
            f'_profile_location_3_{TODAY}.json')

        url_pfile_inf = f'{GPS}{STEAMID}'
        self.directory = f"{STEAMID}"
        self.parent_dir = "date"
        self.path = os.path.join(self.parent_dir, self.directory)
        try:
            os.mkdir(self.path)
        except FileExistsError:
            pass

        try:
            open(self.load_from_file, 'r')
        except FileNotFoundError:
            self.req_profile = requests.get(url_pfile_inf).json()
            self.write_json_file(self.req_profile, self.load_from_file)
            self.profile_data_json = (
                self.open_json_file(self.load_from_file)
                )
            text_location = ''

        try:
            open(self.load_location_from_file_1, 'r')
        except FileNotFoundError:
            self.req_profile = requests.get(url_pfile_inf).json()
            self.write_json_file(self.req_profile, self.load_from_file)
            self.profile_data_json = self.open_json_file(self.load_from_file)

        try:
            self.loccountrycode = (
                self.profile_data_json
                ['response']['players'][0]['loccountrycode'])
            self.location_all_1 = (
                'https://steamcommunity.com/actions/QueryLocations/'
                )
            self.location_req_1 = requests.get(self.location_all_1).json()
            self.write_json_file(
                self.location_req_1,
                self.load_location_from_file_1)
            self.location_file_1 = self.open_json_file(
                self.load_location_from_file_1)
            for _ in self.location_file_1:
                if _['countrycode'] == self.loccountrycode:
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
                f'{self.loccountrycode}/')
            self.location_req_2 = requests.get(self.location_url_2).json()
            self.write_json_file(
                self.location_req_2,
                self.load_location_from_file_2)
            self.location_file_2 = self.open_json_file(
                self.load_location_from_file_2)
            for _ in self.location_file_2:
                if _['statecode'] == self.locstatecode:
                    text_location += _['statename'] + ', '
        except KeyError:
            text_location += '██████████'
            self.ui.label_loccountrycode.setText(text_location)
            return text_location

        try:
            self.loccityid = (
                self.req_profile['response']['players'][0]['loccityid'])
            self.location_url_3 = (
                'https://steamcommunity.com/actions/QueryLocations/'
                f'{self.loccountrycode}/{self.locstatecode}')
            self.location_req_3 = requests.get(self.location_url_3).json()
            self.write_json_file(
                self.location_req_3,
                self.load_location_from_file_3)
            self.location_file_3 = self.open_json_file(
                self.load_location_from_file_3)
            for _ in self.location_file_3:
                if _['cityid'] == self.loccityid:
                    text_location += _['cityname']
            self.ui.label_loccountrycode.setText(text_location)
            return text_location
        except KeyError:
            text_location += '██████████'
            self.ui.label_loccountrycode.setText(text_location)

        # OpenFromFiles on Disc
        self.profile_data_json = self.open_json_file(
            self.load_from_file)
        text_location = ''

        try:
            self.loccountrycode = (
                self.profile_data_json
                ['response']['players'][0]['loccountrycode'])
            self.location_file_1 = self.open_json_file(
                self.load_location_from_file_1)
            for _ in self.location_file_1:
                if _['countrycode'] == self.loccountrycode:
                    text_location += _['countryname'] + ', '
        except KeyError:
            text_location += '██████████'
            self.ui.label_loccountrycode.setText(text_location)
            return text_location

        try:
            self.locstatecode = (
                self.profile_data_json
                ['response']['players'][0]['locstatecode'])
            self.location_file_2 = self.open_json_file(
                self.load_location_from_file_2)
            for _ in self.location_file_2:
                if _['statecode'] == self.locstatecode:
                    text_location += _['statename'] + ', '
        except KeyError:
            text_location += '██████████'
            self.ui.label_loccountrycode.setText(text_location)
            return text_location
        try:
            self.loccityid = self.profile_data_json['response']['players'][0]['loccityid']
            self.location_file_3 = self.open_json_file(self.load_location_from_file_3)
            for _ in self.location_file_3:
                if _['cityid'] == self.loccityid:
                    text_location += _['cityname']
            self.ui.label_loccountrycode.setText(text_location)
            return text_location
        except KeyError:
            text_location += '██████████'
            self.ui.label_loccountrycode.setText(text_location)
        return text_location

    def get_table_statistics(self, steamid):
        create_avatar(STEAMID)
        self.file_profile_info = (
            f'date/{STEAMID}/{STEAMID}'
            f'_profile_info_{TODAY}.json')
        self.url_profile_stat = f'{GPS}{STEAMID}'
        self.tmp_text_all = ''

        try:
            open(self.file_profile_info, 'r')
        except FileNotFoundError:
            self.file_profile_info_req = requests.get(
                self.url_profile_stat).json()
            self.write_json_file(
                self.file_profile_info_req,
                self.file_profile_info)

        if self.open_json_file(
            self.file_profile_info)['response']['players'] == []:
            self.tmp_text_all = TEXT_NOT_FOUND
            self.statusBar().showMessage('ERR: 404 Not found!')
            return self.tmp_text_all

        #  * communityvisibilitystate
        #  * 1 - the profile is not visible to you (Private, Friends Only, etc)
        #  * 3 - the profile is "Public", and the data is visible.
        self.file_profile_info_json = self.open_json_file(
            self.file_profile_info
        )
        if self.file_profile_info_json['response']['players'][0][CVS] == 1:
            self.statusBar().showMessage(
                'The profile is not visible to'
                'you (Private, Friends Only, etc)')
            steamid_profile_json = (
                f'date/{STEAMID}/{STEAMID}'
                f'_profile_info_{TODAY}.json')
            self.profile_data_json = self.open_json_file(
                steamid_profile_json)
            self.tmp_text_all = NO_INFO_USERS
            return self.tmp_text_all
        elif self.file_profile_info_json['response']['players'][0][CVS] == 3:
            self.statusBar().showMessage(
                'The profile is "Public", and the data is visible')
            steamid_profile_json = (
                f'date/{STEAMID}/{STEAMID}'
                f'_profile_info_{TODAY}.json')
            self.open_json_file(steamid_profile_json)

        self.steamidprofile_json = f'date/{STEAMID}/{STEAMID}_profile_info_{TODAY}.json'
        self.profile_data_json = self.open_json_file(self.steamidprofile_json)

        # 0 - Offline,
        # 1 - Online,
        # 2 - Busy,
        # 3 - Away,
        # 4 - Snooze,
        # 5 - looking to trade,
        # 6 - looking to play
        self.personastate = self.file_profile_info_json[
            'response']['players'][0]['personastate']
        #  1 - the profile is not visible to you (Private, Friends Only, etc),
        #  3 - the profile is "Public", and the data is visible.
        self.communityvisibilitystate = self.file_profile_info_json['response']['players'][0][CVS]

        if self.communityvisibilitystate == 1:
            self.statis_profile = "Закрытый"
            self.statusBar().showMessage('The profile is not visible to you (Private, Friends Only, etc)')
            # FIX THIS ADD AVATAR FROM DISC           
            self.image = QImage()
            self.image.loadFromData(requests.get(self.profile_data_json['response']['players'][0]['avatarfull']).content)
            self.ui.label_avatar.setPixmap(QPixmap(self.image))
            self.ui.label_personaname.setText(self.profile_data_json['response']['players'][0]['personaname'] + ' (Приватный профиль)')
            self.tmp_text_all = NO_INFO_USERS
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

        self.tmp_text_all += (
            'Стим ID - '
            f"{self.profile_data_json['response']['players'][0]['steamid']}\n"
            )
        self.tmp_text_all += f'Статус профиля - {self.statis_profile}\n'
        self.tmp_text_all += f'Статус Steam - {self.online_status}\n'
        tmp_name = (
            self.profile_data_json['response']
            ['players'][0]['personaname'])
        self.tmp_text_all += f"Никнейм - {str(tmp_name)}\n"
        tmp_pfile = (
            self.profile_data_json['response']
            ['players'][0]['profileurl'])
        self.tmp_text_all += f"Ссылка на профиль - {str(tmp_pfile)}\n"
        # TODO complite f-string next 3 rows
        # ! 06.08.2021
        try:
            self.tmp_text_all += 'Последний раз выходил - ' + str(datetime.fromtimestamp(self.profile_data_json['response']['players'][0]['lastlogoff'])) + "\n"
        except KeyError:
            self.tmp_text_all += 'Последний раз выходил - ' + '██████████' + "\n"
        try:
            self.tmp_text_all += 'Реальное имя - ' + str(self.profile_data_json['response']['players'][0]['realname']) + "\n"
        except KeyError:
            self.tmp_text_all += 'Реальное имя - ' + '██████████' + "\n"
        tmp_timec = (
            datetime.fromtimestamp(
                self.profile_data_json['response']
                ['players'][0]['timecreated'])
        )
        self.tmp_text_all += f'Дата создания профиля - {str(tmp_timec)}\n'
        self.tmp_text_all += (
            f"Страна - {self.ui.label_loccountrycode.text()}\n")

        return self.tmp_text_all

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
        self.get_info_profile(steam_id)
        self.ui.textBrowser_info.setText(
            self.get_table_statistics(steam_id))
        return f'Steamid - {steam_id}'

    def check_profile(self, steamid: str) -> str:
        # ! fix STEAMID pep8
        STEAMID = steamid
        url_pfile_inf = f'{GPS}{STEAMID}'

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
            tmp_text_all = TEXT_NOT_FOUND
            self.ui.textBrowser_info.setText(tmp_text_all)
            self.ui.tabWidget.setTabEnabled(1, False)
            self.ui.tabWidget.setTabEnabled(2, False)
            self.ui.tabWidget.setTabEnabled(3, False)
            self.ui.tabWidget.setTabEnabled(4, False)
            self.ui.pushButton_update_stat.setEnabled(False)
            return 'ERR: not found!'

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

    def open_json_file(self, fname):
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
            pass

        with open(path, 'w', encoding=UTF8) as fw:
            json.dump(w_info, fw, ensure_ascii=False, indent=4)
        return self.list_all_weapons.emit(w_info)

    def get_info_weapons(self, STEAMID):
        url_pfile_inf = f'{GPS}{STEAMID}'
        if requests.get(url_pfile_inf).json()['response']['players'][0][CVS] == 1:
            return [('', '', '', '', '', '', '')]

        total_ksh_ak47 = [
            self.find_key_by_value('total_kills_ak47', STEAMID),
            self.find_key_by_value('total_shots_ak47', STEAMID),
            self.find_key_by_value('total_hits_ak47', STEAMID)]

        total_ksh_aug = [
            self.find_key_by_value('total_kills_aug', STEAMID),
            self.find_key_by_value('total_shots_aug', STEAMID),
            self.find_key_by_value('total_hits_aug', STEAMID)]

        total_ksh_awp = [
            self.find_key_by_value('total_kills_awp', STEAMID),
            self.find_key_by_value('total_shots_awp', STEAMID),
            self.find_key_by_value('total_hits_awp', STEAMID)]

        total_ksh_awp = [
            self.find_key_by_value('total_kills_awp', STEAMID),
            self.find_key_by_value('total_shots_awp', STEAMID),
            self.find_key_by_value('total_hits_awp', STEAMID)]

        total_ksh_deagle = [
            self.find_key_by_value('total_kills_deagle', STEAMID),
            self.find_key_by_value('total_shots_deagle', STEAMID),
            self.find_key_by_value('total_hits_deagle', STEAMID)]

        total_ksh_elite = [
            self.find_key_by_value('total_kills_elite', STEAMID),
            self.find_key_by_value('total_shots_elite', STEAMID),
            self.find_key_by_value('total_hits_elite', STEAMID)]

        total_ksh_famas = [
            self.find_key_by_value('total_kills_famas', STEAMID),
            self.find_key_by_value('total_shots_famas', STEAMID),
            self.find_key_by_value('total_hits_famas', STEAMID)]

        total_ksh_fiveseven = [
            self.find_key_by_value('total_kills_fiveseven', STEAMID),
            self.find_key_by_value('total_shots_fiveseven', STEAMID),
            self.find_key_by_value('total_hits_fiveseven', STEAMID)]

        total_ksh_g3sg1 = [
            self.find_key_by_value('total_kills_g3sg1', STEAMID),
            self.find_key_by_value('total_shots_g3sg1', STEAMID),
            self.find_key_by_value('total_hits_g3sg1', STEAMID)]

        total_ksh_galilar = [
            self.find_key_by_value('total_kills_galilar', STEAMID),
            self.find_key_by_value('total_shots_galilar', STEAMID),
            self.find_key_by_value('total_hits_galilar', STEAMID)]

        total_ksh_glock = [
            self.find_key_by_value('total_kills_glock', STEAMID),
            self.find_key_by_value('total_shots_glock', STEAMID),
            self.find_key_by_value('total_hits_glock', STEAMID)]

        total_ksh_m249 = [
            self.find_key_by_value('total_kills_m249', STEAMID),
            self.find_key_by_value('total_shots_m249', STEAMID),
            self.find_key_by_value('total_hits_m249', STEAMID)]

        total_ksh_m4a1 = [
            self.find_key_by_value('total_kills_m4a1', STEAMID),
            self.find_key_by_value('total_shots_m4a1', STEAMID),
            self.find_key_by_value('total_hits_m4a1', STEAMID)]

        total_ksh_mac10 = [
            self.find_key_by_value('total_kills_mac10', STEAMID),
            self.find_key_by_value('total_shots_mac10', STEAMID),
            self.find_key_by_value('total_hits_mac10', STEAMID)]

        total_ksh_mag7 = [
            self.find_key_by_value('total_kills_mag7', STEAMID),
            self.find_key_by_value('total_shots_mag7', STEAMID),
            self.find_key_by_value('total_hits_mag7', STEAMID)]

        total_ksh_mp7 = [
            self.find_key_by_value('total_kills_mp7', STEAMID),
            self.find_key_by_value('total_shots_mp7', STEAMID),
            self.find_key_by_value('total_hits_mp7', STEAMID)]

        total_ksh_mp9 = [
            self.find_key_by_value('total_kills_mp9', STEAMID),
            self.find_key_by_value('total_shots_mp9', STEAMID),
            self.find_key_by_value('total_hits_mp9', STEAMID)]

        total_ksh_negev = [
            self.find_key_by_value('total_kills_negev', STEAMID),
            self.find_key_by_value('total_shots_negev', STEAMID),
            self.find_key_by_value('total_hits_negev', STEAMID)]

        total_ksh_nova = [
            self.find_key_by_value('total_kills_nova', STEAMID),
            self.find_key_by_value('total_shots_nova', STEAMID),
            self.find_key_by_value('total_hits_nova', STEAMID)]

        total_ksh_hkp2000 = [
            self.find_key_by_value('total_kills_hkp2000', STEAMID),
            self.find_key_by_value('total_shots_hkp2000', STEAMID),
            self.find_key_by_value('total_hits_hkp2000', STEAMID)]

        total_ksh_p250 = [
            self.find_key_by_value('total_kills_p250', STEAMID),
            self.find_key_by_value('total_shots_p250', STEAMID),
            self.find_key_by_value('total_hits_p250', STEAMID)]

        total_ksh_p90 = [
            self.find_key_by_value('total_kills_p90', STEAMID),
            self.find_key_by_value('total_shots_p90', STEAMID),
            self.find_key_by_value('total_hits_p90', STEAMID)]

        total_ksh_bizon = [
            self.find_key_by_value('total_kills_bizon', STEAMID),
            self.find_key_by_value('total_shots_bizon', STEAMID),
            self.find_key_by_value('total_hits_bizon', STEAMID)]

        total_ksh_sawedoff = [
            self.find_key_by_value('total_kills_sawedoff', STEAMID),
            self.find_key_by_value('total_shots_sawedoff', STEAMID),
            self.find_key_by_value('total_hits_sawedoff', STEAMID)]

        total_ksh_scar20 = [
            self.find_key_by_value('total_kills_scar20', STEAMID),
            self.find_key_by_value('total_shots_scar20', STEAMID),
            self.find_key_by_value('total_hits_scar20', STEAMID)]

        total_ksh_sg556 = [
            self.find_key_by_value('total_kills_sg556', STEAMID),
            self.find_key_by_value('total_shots_sg556', STEAMID),
            self.find_key_by_value('total_hits_sg556', STEAMID)]

        total_ksh_ssg08 = [
            self.find_key_by_value('total_kills_ssg08', STEAMID),
            self.find_key_by_value('total_shots_ssg08', STEAMID),
            self.find_key_by_value('total_hits_ssg08', STEAMID)]

        total_ksh_tec9 = [
            self.find_key_by_value('total_kills_tec9', STEAMID),
            self.find_key_by_value('total_shots_tec9', STEAMID),
            self.find_key_by_value('total_hits_tec9', STEAMID)]

        total_ksh_ump45 = [
            self.find_key_by_value('total_kills_ump45', STEAMID),
            self.find_key_by_value('total_shots_ump45', STEAMID),
            self.find_key_by_value('total_hits_ump45', STEAMID)]

        total_ksh_xm1014 = [
            self.find_key_by_value('total_kills_xm1014', STEAMID),
            self.find_key_by_value('total_shots_xm1014', STEAMID),
            self.find_key_by_value('total_hits_xm1014', STEAMID)]

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

    def find_key_by_value(self, finded, STEAMID):
        self.url_all_statistic = f'{GUSFG}{STEAMID}'
        self.get_statistic_json = (
            f'date/{STEAMID}/{STEAMID}'
            f'_all_statistic_{TODAY}.json')
        self.finded = finded

        if requests.get(self.url_all_statistic).status_code == 500:
            return 'Error 500'

        try:
            open(self.get_statistic_json, 'r', encoding=UTF8)
        except:
            self.req_statistic = requests.get(self.url_all_statistic).json()
            self.write_json_file(self.req_statistic, self.get_statistic_json)

        self.statistic_file_json = self.open_json_file(self.get_statistic_json)
        self.finded_val = 0
        for _ in self.statistic_file_json['playerstats']['stats']:
            if _['name'] == self.finded:
                self.finded_val = _['value']
        return self.finded_val


class CheckMatchesThread(QtCore.QThread, MyWin):
    pass


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    myapp = MyWin()
    myapp.show()
    sys.exit(app.exec_())
