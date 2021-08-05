from PyQt5 import QtWidgets, QtCore

from MainCheckVacThread import CheckVacThread

import res.constants
from res.codes import keys

class CheckFriendsThread(QtCore.QThread):
    list_all_friends = QtCore.pyqtSignal(list)

    def __init__(self, parent=None):
        QtCore.QThread.__init__(self, parent)
        self.running = False
        self.get_vac_status = CheckVacThread()

    def run(self) -> None:
        self.running = True
        url_frs = f'{GPS}{STEAMID}'
        all_fr_jsn = f'date/{STEAMID}/{STEAMID}_all_friend_list_{TODAY}.json'
        friend_info = []
        try:
            open(
                f'date/{STEAMID}/{STEAMID}'
                f'_all_friend_list_{TODAY}.json', 'r')
        except FileNotFoundError:
            self.req_friends_list = requests.get(url_frs).json()
            self.write_json_file(
                self.req_friends_list,
                all_fr_jsn)

        if self.get_profile_check(STEAMID) == 0:
            friend_info = [('', '', '', '', '', '', '')]
            return friend_info

        fr_steam = self.open_json_file(all_fr_jsn)

        try:
            fr_steam['friendslist']['friends']
        except KeyError:
            print('Скрытый профиль!')
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
                self.friend = self.open_json_file(self.friend_steamid_json)
                friend_info.append([
                    s_id_friend,
                    self.friend['response']['players'][0]['personaname'],
                    self.friend_since_friend,
                    'VAC БАН' if vac_status['players'][0]['VACBanned'] else '',
                    'Community Banned' if vac_status['players'][0]["CommunityBanned"] else '',
                    "" if vac_status['players'][0]["EconomyBan"] == "none" else "Economy Ban",
                    str(vac_status['players'][0]["NumberOfGameBans"]) if vac_status['players'][0]["NumberOfGameBans"] else ""])
                continue

            self.friend_steamid_json = (
                f'date/{STEAMID}/{s_id_friend}.json')
            self.friend = self.open_json_file(self.friend_steamid_json)
            friend_info.append([
                    s_id_friend,
                    self.friend['response']['players'][0]['personaname'],
                    self.friend_since_friend,
                    'VAC БАН' if vac_status['players'][0]['VACBanned'] else '',
                    'Community Banned' if vac_status['players'][0]["CommunityBanned"] else '',
                    "" if vac_status['players'][0]["EconomyBan"] == "none" else "Economy Ban",
                    str(vac_status['players'][0]["NumberOfGameBans"]) if vac_status['players'][0]["NumberOfGameBans"] else ""])
            self.list_all_friends.emit(friend_info)
