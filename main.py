import json
import sys
import requests
from PyQt5 import QtWidgets, QtCore
from res.mainwindows import Ui_MainWindow
from PyQt5.QtWidgets import QTableWidgetItem
from codes import keys



steamid = keys['steamid']
key = keys['key']
steamidkey = keys['steamidkey']
knowncode = keys['knowncode']

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
        
        #url = f'https://api.steampowered.com/ICSGOPlayers_730/GetNextMatchSharingCode/v1?key={key}&steamid={steamid}&steamidkey={steamidkey}&knowncode={knowncode}'
        url = f'https://api.steampowered.com/ISteamUserStats/GetUserStatsForGame/v0002/?appid=730&key={key}&steamid={steamid}'
        r = requests.get(url).json()
        fname = '/home/master/code/csgostats/res/csgo.json'
        #self.write_json_file(r, fname)
        data_csgo = self.open_json_file(r, fname)

        total_kills_ak47 = data_csgo['playerstats']['stats'][20]['value']
        total_shots_ak47 = data_csgo['playerstats']['stats'][56]['value']
        total_hits_ak47 = data_csgo['playerstats']['stats'][70]['value']

        total_kills_aug = data_csgo['playerstats']['stats'][21]['value']
        total_shots_aug = data_csgo['playerstats']['stats'][57]['value']
        total_hits_aug = data_csgo['playerstats']['stats'][71]['value']

        total_kills_awp = data_csgo['playerstats']['stats'][19]['value']
        total_shots_awp = data_csgo['playerstats']['stats'][55]['value']
        total_hits_awp = data_csgo['playerstats']['stats'][69]['value']

        total_kills_deagle = data_csgo['playerstats']['stats'][12]['value']
        total_shots_deagle = data_csgo['playerstats']['stats'][51]['value']
        total_hits_deagle = data_csgo['playerstats']['stats'][65]['value']

        total_kills_elite = data_csgo['playerstats']['stats'][13]['value']
        total_shots_elite = data_csgo['playerstats']['stats'][53]['value']
        total_hits_elite = data_csgo['playerstats']['stats'][67]['value']

        total_kills_famas = data_csgo['playerstats']['stats'][22]['value']
        total_shots_famas = data_csgo['playerstats']['stats'][58]['value']
        total_hits_famas = data_csgo['playerstats']['stats'][72]['value']

        total_kills_fiveseven = data_csgo['playerstats']['stats'][14]['value']
        total_shots_fiveseven = data_csgo['playerstats']['stats'][54]['value']
        total_hits_fiveseven = data_csgo['playerstats']['stats'][68]['value']

        total_kills_g3sg1 = data_csgo['playerstats']['stats'][23]['value']
        total_shots_g3sg1 = data_csgo['playerstats']['stats'][59]['value']
        total_hits_g3sg1 = data_csgo['playerstats']['stats'][73]['value']

        total_kills_galilar = data_csgo['playerstats']['stats'][181]['value']
        total_shots_galilar = data_csgo['playerstats']['stats'][186]['value']
        total_hits_galilar = data_csgo['playerstats']['stats'][189]['value']

        total_kills_glock = data_csgo['playerstats']['stats'][11]['value']
        total_shots_glock = data_csgo['playerstats']['stats'][52]['value']
        total_hits_glock = data_csgo['playerstats']['stats'][66]['value']

        total_kills_m249 = data_csgo['playerstats']['stats'][24]['value']
        total_shots_m249 = data_csgo['playerstats']['stats'][64]['value']
        total_hits_m249 = data_csgo['playerstats']['stats'][78]['value']

        total_kills_m4a1 = data_csgo['playerstats']['stats'][180]['value']
        total_shots_m4a1 = data_csgo['playerstats']['stats'][185]['value']
        total_hits_m4a1 = data_csgo['playerstats']['stats'][188]['value']

        total_kills_mac10 = data_csgo['playerstats']['stats'][16]['value']
        total_shots_mac10 = data_csgo['playerstats']['stats'][61]['value']
        total_hits_mac10 = data_csgo['playerstats']['stats'][75]['value']

        total_kills_mag7 = data_csgo['playerstats']['stats'][177]['value']
        total_shots_mag7 = data_csgo['playerstats']['stats'][175]['value']
        total_hits_mag7 = data_csgo['playerstats']['stats'][176]['value']

        total_kills_mp7 = data_csgo['playerstats']['stats'][156]['value']
        total_shots_mp7 = data_csgo['playerstats']['stats'][154]['value']
        total_hits_mp7 = data_csgo['playerstats']['stats'][155]['value']

        total_kills_mp9 = data_csgo['playerstats']['stats'][157]['value']
        total_shots_mp9 = data_csgo['playerstats']['stats'][158]['value']
        total_hits_mp9 = data_csgo['playerstats']['stats'][159]['value']

        total_kills_negev = data_csgo['playerstats']['stats'][164]['value']
        total_shots_negev = data_csgo['playerstats']['stats'][165]['value']
        total_hits_negev = data_csgo['playerstats']['stats'][163]['value']

        total_kills_nova = data_csgo['playerstats']['stats'][161]['value']
        total_shots_nova = data_csgo['playerstats']['stats'][162]['value']
        total_hits_nova = data_csgo['playerstats']['stats'][160]['value']

        total_kills_hkp2000 = data_csgo['playerstats']['stats'][139]['value']
        total_shots_hkp2000 = data_csgo['playerstats']['stats'][140]['value']
        total_hits_hkp2000 = data_csgo['playerstats']['stats'][141]['value']

        total_kills_p250 = data_csgo['playerstats']['stats'][143]['value']
        total_shots_p250 = data_csgo['playerstats']['stats'][144]['value']
        total_hits_p250 = data_csgo['playerstats']['stats'][142]['value']

        total_kills_p90 = data_csgo['playerstats']['stats'][18]['value']
        total_shots_p90 = data_csgo['playerstats']['stats'][60]['value']
        total_hits_p90 = data_csgo['playerstats']['stats'][74]['value']

        total_kills_bizon = data_csgo['playerstats']['stats'][171]['value']
        total_shots_bizon = data_csgo['playerstats']['stats'][169]['value']
        total_hits_bizon = data_csgo['playerstats']['stats'][170]['value']

        total_kills_sawedoff = data_csgo['playerstats']['stats'][168]['value']
        total_shots_sawedoff = data_csgo['playerstats']['stats'][166]['value']
        total_hits_sawedoff = data_csgo['playerstats']['stats'][167]['value']

        total_kills_scar20 = data_csgo['playerstats']['stats'][149]['value']
        total_shots_scar20 = data_csgo['playerstats']['stats'][150]['value']
        total_hits_scar20 = data_csgo['playerstats']['stats'][148]['value']

        total_kills_sg556 = data_csgo['playerstats']['stats'][145]['value']
        total_shots_sg556 = data_csgo['playerstats']['stats'][146]['value']
        total_hits_sg556 = data_csgo['playerstats']['stats'][147]['value']

        total_kills_ssg08 = data_csgo['playerstats']['stats'][153]['value']
        total_shots_ssg08 = data_csgo['playerstats']['stats'][151]['value']
        total_hits_ssg08 = data_csgo['playerstats']['stats'][152]['value']

        total_kills_tec9 = data_csgo['playerstats']['stats'][172]['value']
        total_shots_tec9 = data_csgo['playerstats']['stats'][173]['value']
        total_hits_tec9 = data_csgo['playerstats']['stats'][174]['value']

        total_kills_ump45 = data_csgo['playerstats']['stats'][17]['value']
        total_shots_ump45 = data_csgo['playerstats']['stats'][62]['value']
        total_hits_ump45 = data_csgo['playerstats']['stats'][76]['value']

        total_kills_xm1014 = data_csgo['playerstats']['stats'][15]['value']
        total_shots_xm1014 = data_csgo['playerstats']['stats'][63]['value']
        total_hits_xm1014 = data_csgo['playerstats']['stats'][77]['value']

        total_summ = (total_kills_ak47 + total_kills_aug + total_kills_awp + total_kills_deagle + total_kills_elite +
                      total_kills_famas + total_kills_fiveseven + total_kills_g3sg1 + total_kills_galilar + total_kills_glock + total_kills_m249 +
                      total_kills_m4a1 + total_kills_mac10 + total_kills_mag7 + total_kills_mp7 + total_kills_mp9 + total_kills_negev +
                      total_kills_nova + total_kills_hkp2000 + total_kills_p250 + total_kills_p90 + total_kills_bizon + total_kills_sawedoff +
                      total_kills_scar20 + total_kills_sg556 + total_kills_ssg08 + total_kills_tec9 + total_kills_ump45 + total_kills_xm1014)

        data = [(
            'AK-47',
            str(round(total_hits_ak47 / total_shots_ak47 * 100, 2)) + "%",
            str(round(total_kills_ak47 / total_hits_ak47 * 100, 2)) + "%",
            str(total_kills_ak47),
            str(total_hits_ak47),
            str(total_shots_ak47),
            str(round(total_kills_ak47 / total_summ * 100, 2)) + "%"),
            ('AUG',
             str(round(total_hits_aug / total_shots_aug * 100, 2)) + "%",
             str(round(total_kills_aug / total_hits_aug * 100, 2)) + "%",
             str(total_kills_aug),
             str(total_hits_aug),
             str(total_shots_aug),
             str(round(total_kills_aug / total_summ * 100, 2)) + "%"),
            ('AWP',
             str(round(total_hits_awp / total_shots_awp * 100, 2)) + "%",
             str(round(total_kills_awp / total_hits_awp * 100, 2)) + "%",
             str(total_kills_awp),
             str(total_hits_awp),
             str(total_shots_awp),
             str(round(total_kills_awp / total_summ * 100, 2)) + "%"),
            ('Desert Eagle/R8',
             str(round(total_hits_deagle / total_shots_deagle * 100, 2)) + "%",
             str(round(total_kills_deagle / total_hits_deagle * 100, 2)) + "%",
             str(total_kills_deagle),
             str(total_hits_deagle),
             str(total_shots_deagle),
             str(round(total_kills_deagle / total_summ * 100, 2)) + "%"),
            ('Dual Berettas',
             str(round(total_hits_elite / total_shots_elite * 100, 2)) + "%",
             str(round(total_kills_elite / total_hits_elite * 100, 2)) + "%",
             str(total_kills_elite),
             str(total_hits_elite),
             str(total_shots_elite),
             str(round(total_kills_elite / total_summ * 100, 2)) + "%"),
            ('Famas',
             str(round(total_hits_famas / total_shots_famas * 100, 2)) + "%",
             str(round(total_kills_famas / total_hits_famas * 100, 2)) + "%",
             str(total_kills_famas),
             str(total_hits_famas),
             str(total_shots_famas),
             str(round(total_kills_famas / total_summ * 100, 2)) + "%"),
            ('Five-SeveN',
             str(round(total_hits_fiveseven / total_shots_fiveseven * 100, 2)) + "%",
             str(round(total_kills_fiveseven / total_hits_fiveseven * 100, 2)) + "%",
             str(total_kills_fiveseven),
             str(total_hits_fiveseven),
             str(total_shots_fiveseven),
             str(round(total_kills_fiveseven / total_summ * 100, 2)) + "%"),
            ('G3SG1',
             str(round(total_hits_g3sg1 / total_shots_g3sg1 * 100, 2)) + "%",
             str(round(total_kills_g3sg1 / total_hits_g3sg1 * 100, 2)) + "%",
             str(total_kills_g3sg1),
             str(total_hits_g3sg1),
             str(total_shots_g3sg1),
             str(round(total_kills_g3sg1 / total_summ * 100, 2)) + "%"),
            ('Galil AR',
             str(round(total_hits_galilar / total_shots_galilar * 100, 2)) + "%",
             str(round(total_kills_galilar / total_hits_galilar * 100, 2)) + "%",
             str(total_kills_galilar),
             str(total_hits_galilar),
             str(total_shots_galilar),
             str(round(total_kills_galilar / total_summ * 100, 2)) + "%"),
            ('Glock-18',
             str(round(total_hits_glock / total_shots_glock * 100, 2)) + "%",
             str(round(total_kills_glock / total_hits_glock * 100, 2)) + "%",
             str(total_kills_glock),
             str(total_hits_glock),
             str(total_shots_glock),
             str(round(total_kills_glock / total_summ * 100, 2)) + "%"),
            ('M249',
             str(round(total_hits_m249 / total_shots_m249 * 100, 2)) + "%",
             str(round(total_kills_m249 / total_hits_m249 * 100, 2)) + "%",
             str(total_kills_m249),
             str(total_hits_m249),
             str(total_shots_m249),
             str(round(total_kills_m249 / total_summ * 100, 2)) + "%"),
            ('M4A4/M4A1-S',
             str(round(total_hits_m4a1 / total_shots_m4a1 * 100, 2)) + "%",
             str(round(total_kills_m4a1 / total_hits_m4a1 * 100, 2)) + "%",
             str(total_kills_m4a1),
             str(total_hits_m4a1),
             str(total_shots_m4a1),
             str(round(total_kills_m4a1 / total_summ * 100, 2)) + "%"),
            ('MAC-10',
             str(round(total_hits_mac10 / total_shots_mac10 * 100, 2)) + "%",
             str(round(total_kills_mac10 / total_hits_mac10 * 100, 2)) + "%",
             str(total_kills_mac10),
             str(total_hits_mac10),
             str(total_shots_mac10),
             str(round(total_kills_mac10 / total_summ * 100, 2)) + "%"),
            ('MAG7',
             str(round(total_hits_mag7 / total_shots_mag7 * 100, 2)) + "%",
             str(round(total_kills_mag7 / total_hits_mag7 * 100, 2)) + "%",
             str(total_kills_mag7),
             str(total_hits_mag7),
             str(total_shots_mag7),
             str(round(total_kills_mag7 / total_summ * 100, 2)) + "%"),
            ('MP7/MP5-SD',
             str(round(total_hits_mp7 / total_shots_mp7 * 100, 2)) + "%",
             str(round(total_kills_mp7 / total_hits_mp7 * 100, 2)) + "%",
             str(total_kills_mp7),
             str(total_hits_mp7),
             str(total_shots_mp7),
             str(round(total_kills_mp7 / total_summ * 100, 2)) + "%"),
            ('MP9',
             str(round(total_hits_mp9 / total_shots_mp9 * 100, 2)) + "%",
             str(round(total_kills_mp9 / total_hits_mp9 * 100, 2)) + "%",
             str(total_kills_mp9),
             str(total_hits_mp9),
             str(total_shots_mp9),
             str(round(total_kills_mp9 / total_summ * 100, 2)) + "%"),
            ('Negev',
             str(round(total_hits_negev / total_shots_negev * 100, 2)) + "%",
             str(round(total_kills_negev / total_hits_negev * 100, 2)) + "%",
             str(total_kills_negev),
             str(total_hits_negev),
             str(total_shots_negev),
             str(round(total_kills_negev / total_summ * 100, 2)) + "%"),
            ('Nova',
             str(round(total_hits_nova / total_shots_nova * 100, 2)) + "%",
             str(round(total_kills_nova / total_hits_nova * 100, 2)) + "%",
             str(total_kills_nova),
             str(total_hits_nova),
             str(total_shots_nova),
             str(round(total_kills_nova / total_summ * 100, 2)) + "%"),
            ('P2000/USP-S',
             str(round(total_hits_hkp2000 / total_shots_hkp2000 * 100, 2)) + "%",
             str(round(total_kills_hkp2000 / total_hits_hkp2000 * 100, 2)) + "%",
             str(total_kills_hkp2000),
             str(total_hits_hkp2000),
             str(total_shots_hkp2000),
             str(round(total_kills_hkp2000 / total_summ * 100, 2)) + "%"),
            ('P250/CZ75-Auto',
             str(round(total_hits_p250 / total_shots_p250 * 100, 2)) + "%",
             str(round(total_kills_p250 / total_hits_p250 * 100, 2)) + "%",
             str(total_kills_p250),
             str(total_hits_p250),
             str(total_shots_p250),
             str(round(total_kills_p250 / total_summ * 100, 2)) + "%"),
            ('P90',
             str(round(total_hits_p90 / total_shots_p90 * 100, 2)) + "%",
             str(round(total_kills_p90 / total_hits_p90 * 100, 2)) + "%",
             str(total_kills_p90),
             str(total_hits_p90),
             str(total_shots_p90),
             str(round(total_kills_p90 / total_summ * 100, 2)) + "%"),
            ('PP-Bizon',
             str(round(total_hits_bizon / total_shots_bizon * 100, 2)) + "%",
             str(round(total_kills_bizon / total_hits_bizon * 100, 2)) + "%",
             str(total_kills_bizon),
             str(total_hits_bizon),
             str(total_shots_bizon),
             str(round(total_kills_bizon / total_summ * 100, 2)) + "%"),
            ('Sawed-Off',
             str(round(total_hits_sawedoff / total_shots_sawedoff * 100, 2)) + "%",
             str(round(total_kills_sawedoff / total_hits_sawedoff * 100, 2)) + "%",
             str(total_kills_sawedoff),
             str(total_hits_sawedoff),
             str(total_shots_sawedoff),
             str(round(total_kills_sawedoff / total_summ * 100, 2)) + "%"),
            ('SCAR-20',
             str(round(total_hits_scar20 / total_shots_scar20 * 100, 2)) + "%",
             str(round(total_kills_scar20 / total_hits_scar20 * 100, 2)) + "%",
             str(total_kills_scar20),
             str(total_hits_scar20),
             str(total_shots_scar20),
             str(round(total_kills_scar20 / total_summ * 100, 2)) + "%"),
            ('SG 553',
             str(round(total_hits_sg556 / total_shots_sg556 * 100, 2)) + "%",
             str(round(total_kills_sg556 / total_hits_sg556 * 100, 2)) + "%",
             str(total_kills_sg556),
             str(total_hits_sg556),
             str(total_shots_sg556),
             str(round(total_kills_sg556 / total_summ * 100, 2)) + "%"),
            ('SSG 08',
             str(round(total_hits_ssg08 / total_shots_ssg08 * 100, 2)) + "%",
             str(round(total_kills_ssg08 / total_hits_ssg08 * 100, 2)) + "%",
             str(total_kills_ssg08),
             str(total_hits_ssg08),
             str(total_shots_ssg08),
             str(round(total_kills_ssg08 / total_summ * 100, 2)) + "%"),
            ('TEC9',
             str(round(total_hits_tec9 / total_shots_tec9 * 100, 2)) + "%",
             str(round(total_kills_tec9 / total_hits_tec9 * 100, 2)) + "%",
             str(total_kills_tec9),
             str(total_hits_tec9),
             str(total_shots_tec9),
             str(round(total_kills_tec9 / total_summ * 100, 2)) + "%"),
            ('UMP45',
             str(round(total_hits_ump45 / total_shots_ump45 * 100, 2)) + "%",
             str(round(total_kills_ump45 / total_hits_ump45 * 100, 2)) + "%",
             str(total_kills_ump45),
             str(total_hits_ump45),
             str(total_shots_ump45),
             str(round(total_kills_ump45 / total_summ * 100, 2)) + "%"),
            ('XM1014',
             str(round(total_hits_xm1014 / total_shots_xm1014 * 100, 2)) + "%",
             str(round(total_kills_xm1014 / total_hits_xm1014 * 100, 2)) + "%",
             str(total_kills_xm1014),
             str(total_hits_xm1014),
             str(total_shots_xm1014),
             str(round(total_kills_xm1014 / total_summ * 100, 2)) + "%")]

        self.ui.tableWidget.setColumnCount(len(data[0]))
        self.ui.tableWidget.setRowCount(len(data))
        self.ui.tableWidget.setHorizontalHeaderLabels(
            ('Оружие', 'Точность', 'Летальность',
             'Убийства', 'Попадания', 'Выстрелы', '% от всех\nубийств')
        )

        rows_list = []
        for _ in range(len(data)):
            rows_list.append(str(_ + 1))
        self.ui.tableWidget.setVerticalHeaderLabels(rows_list)

        row = 0
        for tup in data:
            col = 0
            for item in tup:
                cellinfo = QTableWidgetItem(item)
                cellinfo.setFlags(
                    QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled
                )
                self.ui.tableWidget.setItem(row, col, cellinfo)
                col += 1
            row += 1
        self.ui.tableWidget.setSortingEnabled(True)

    def write_json_file(self, r, fname):
        with open(fname, 'w', encoding='utf-8') as write_data_json_file:
            json.dump(r, write_data_json_file, ensure_ascii=False, indent=4)
            write_data_json_file.close()

    def open_json_file(self, r, fname):
        try:
            open(fname, 'r', encoding='utf-8')
        except FileNotFoundError:
            self.write_json_file(r, fname)
        with open(fname, 'r', encoding='utf-8') as read_json_file:
            data_json = json.load(read_json_file)
            read_json_file.close()
        return data_json


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    myapp = MyWin()
    myapp.show()
    sys.exit(app.exec_())
