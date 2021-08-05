from PyQt5 import QtWidgets, QtCore

import res.constants
from res.codes import keys


class CheckVacThread(QtCore.QThread):
    list_all_users = QtCore.pyqtSignal(list)
    message_toolbar_bans = QtCore.pyqtSignal(str)
    int_for_progressbar_vac = QtCore.pyqtSignal(int, int)

    def __init__(self, parent=None):
        QtCore.QThread.__init__(self, parent)
        self.running = False
        self.name: str = ''
        date_match_all: list = []

    def run(self) -> None:
        tmp_stmid: str = ''
        all_users = []
        vac_status = []
        tmp_users = []
        val: int = 0
        vacban_sts_all: list = []
        self.running: bool = True
        date_match_users = self.open_json_file(
            'all_stats/all_stats.json'
            )

        for count in range(len(date_match_users)):
            for i in range(10):
                vacban_sts_all.append(
                    [date_match_users[count]['team'][i]['steamid64'],
                     date_match_users[count]['date']])

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
                name = self.open_json_file(
                    f'date/{tmp_stmid}/{tmp_stmid}_profile_info_{TODAY}.json'
                    )['response']['players'][0]['personaname']
            except IndexError:
                tmp_stmid = '76561197997566454'
                name = self.open_json_file(
                    f'date/{tmp_stmid}/{tmp_stmid}_profile_info_{TODAY}.json'
                    )['response']['players'][0]['personaname']

            day = vac_status[val]['players'][0]['DaysSinceLastBan']
            date_ban = TODAY - timedelta(days=day)
            if (
                str(all_users[val][1]) <= str(date_ban).split(' ')[0]
            ) and vac_status[val]['players'][0]["VACBanned"]:
                tmp_users.append(
                    [
                        tmp_stmid,
                        name,
                        str(all_users[val][1]),
                        (
                            'Забанен' if vac_status[val]
                            ['players'][0]["CommunityBanned"] else ''
                            ),
                        (
                            'Забанен' if vac_status[val]
                            ['players'][0]["VACBanned"] else ''
                            ),
                        (
                            str(
                                vac_status[val]
                                ['players'][0]
                                ["NumberOfVACBans"]) if vac_status[val]
                            ['players'][0]["NumberOfVACBans"] else ""
                            ),
                        (
                            str(date_ban).split(' ')[0] if vac_status[val]
                            ['players'][0]
                            ["DaysSinceLastBan"] else f'Новый! {TODAY}'
                            ),
                        (
                            str(
                                vac_status[val]['players'][0]
                                ["NumberOfGameBans"]) if vac_status[val]
                            ['players'][0]["NumberOfGameBans"] else ""
                            ),
                        (
                            "" if vac_status[val]
                            ['players'][0]["EconomyBan"] == "none" else 'BAN')
                        ]
                    )

            val += 1
            if val == len(all_users):
                self.list_all_users.emit(tmp_users, )
                self.running = False
                # break

    def check_vac_banned(self, STEAMID):
        self.file_bans_users = (
            f'date/{STEAMID}/{STEAMID}'
            f'_ban_status_{TODAY}.json')

        url_steam_bans = f'{GPB}{STEAMID}'
        self.directory = f"{STEAMID}"
        self.parent_dir = f'date\\{STEAMID}'
        self.path = os.path.join(self.parent_dir, self.directory)
        self.get_profile_status(STEAMID)

        try:
            os.mkdir(self.path)
        except FileExistsError:
            pass

        try:
            open(
                f'date/{STEAMID}/{STEAMID}'
                f'_ban_status_{TODAY}.json', 'r')
        except FileNotFoundError:
            self.message_toolbar_bans.emit(STEAMID)
            self.request_bans = requests.get(url_steam_bans).json()
            self.write_json_file(self.request_bans, self.file_bans_users)
            return self.open_json_file(self.file_bans_users)

        self.message_toolbar_bans.emit(STEAMID)
        return self.open_json_file(self.file_bans_users)

    def get_profile_status(self, STEAMID):
        steamid_profile_json = (
            f'date/{STEAMID}/{STEAMID}'
            f'_profile_info_{TODAY}.json')
        url_pfile_inf = f'{GPS}{STEAMID}'
        self.directory = f"{STEAMID}"
        self.parent_dir = "date\\"
        self.path = os.path.join(self.parent_dir, self.directory)
        try:
            os.mkdir(self.path)
        except FileExistsError:
            pass

        try:
            open(
                f'date/{STEAMID}/{STEAMID}'
                f'_profile_info_{TODAY}.json', 'r')
        except FileNotFoundError:
            self.req_profile_info = requests.get(url_pfile_inf).json()
            self.write_json_file(
                self.req_profile_info,
                steamid_profile_json)
            # communityvisibilitystate 1
            # - the profile is not visible to
            # you (Private, Friends Only, etc),
            # communityvisibilitystate 3
            #  - the profile is "Public", and the data is visible.
            if self.req_profile_info['response']['players'] == []:
                self.write_json_file(
                    'deleted',
                    f'date/deleted_/{STEAMID}'
                    f'_deleted_profile_info_{TODAY}.json')
                return 0
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
                return self.open_json_file(
                    steamid_profile_json)

        if os.path.exists(
                f'date/{STEAMID}/{STEAMID}'
                f'_profile_info_{TODAY}.json'):
            return self.open_json_file(steamid_profile_json)