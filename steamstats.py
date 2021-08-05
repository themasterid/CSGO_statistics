import requests
from res.codes import keys


KEY = keys['key']
GPS = (
    'https://api.steampowered.com/ISteamUser/'
    f'GetPlayerSummaries/v2/?key={KEY}&steamids='
)


class Record:
    """Класс для хранения значений."""
    def __init__(
        self,
        steamid: str,
        communityvisibilitystate: int,
        profilestate: int,
        personaname: str,
        profileurl: str,
        avatar: str,
        avatarmedium: str,
        avatarfull: str,
        avatarhash: str,
        lastlogoff: str,
        personastate: int,
        realname: str,
        primaryclanid: str,
        timecreated: int,
        personastateflags: int,
        loccountrycode: str,
        locstatecode: str,
        loccityid: int
    ) -> None:
        self.steamid = steamid
        self.communityvisibilitystate = communityvisibilitystate
        self.profilestate = profilestate
        self.personaname = personaname
        self.profileurl = profileurl
        self.avatar = avatar
        self.avatarmedium = avatarmedium
        self.avatarfull = avatarfull
        self.avatarhash = avatarhash
        self.personastate = personastate
        self.realname = realname
        self.primaryclanid = primaryclanid
        self.timecreated = timecreated
        self.personastateflags = personastateflags
        self.loccountrycode = loccountrycode
        self.locstatecode = locstatecode
        self.loccityid = loccityid


class Calculator:
    """Класс для записи значений."""
    def __init__(self, steam_id: str) -> None:
        self.steam_id = steam_id
        self.records: list = []

    def add_records(self, record: Record) -> None:
        self.records.append(record)


'''
{
    'response':
    {'players': [
        {
            'steamid': '76561198084621617',
            'communityvisibilitystate': 3,
            'profilestate': 1,
            'personaname': 'MΞCHANIC',
            'profileurl': 'https://steamcommunity.com/id/Mechanic_ID/',
            'avatar': 'https://steamcdn-a.akamaihd.net/steamcommunity/public/images/avatars/f2/f254aa627953de54330823a2995d314766e1d843.jpg',
            'avatarmedium': 'https://steamcdn-a.akamaihd.net/steamcommunity/public/images/avatars/f2/f254aa627953de54330823a2995d314766e1d843_medium.jpg',
            'avatarfull': 'https://steamcdn-a.akamaihd.net/steamcommunity/public/images/avatars/f2/f254aa627953de54330823a2995d314766e1d843_full.jpg',
            'avatarhash': 'f254aa627953de54330823a2995d314766e1d843',
            'lastlogoff': 1628124037,
            'personastate': 1,
            'realname': '███████████████',
            'primaryclanid': '103582791429521408',
            'timecreated': 1361598026,
            'personastateflags': 0,
            'loccountrycode': 'RU',
            'locstatecode': '11',
            'loccityid': 39665
            }
        ]
}
'''


steamid = '76561198084621617'
url = f'{GPS}{steamid}'
r = requests.get(url).json()
print(r['response']['players'][0]['steamid'])
print(r['response']['players'][0]['communityvisibilitystate'])
print(r['response']['players'][0]['profilestate'])
print(r['response']['players'][0]['personaname'])
print(r['response']['players'][0]['profileurl'])
print(r['response']['players'][0]['avatar'])
print(r['response']['players'][0]['avatarmedium'])
print(r['response']['players'][0]['avatarfull'])
print(r['response']['players'][0]['avatarhash'])
print(r['response']['players'][0]['lastlogoff'])
print(r['response']['players'][0]['personastate'])
print(r['response']['players'][0]['realname'])
print(r['response']['players'][0]['primaryclanid'])
print(r['response']['players'][0]['timecreated'])
print(r['response']['players'][0]['personastateflags'])
print(r['response']['players'][0]['loccountrycode'])
print(r['response']['players'][0]['locstatecode'])
print(r['response']['players'][0]['loccityid'])

calc = Calculator(steamid)
'''
calc.add_records(
    Record(
        steamid="76561198084621617",
        communityvisibilitystate=3,
        profilestate=1,
        personaname="MΞCHANIC",
        profileurl="https://steamcommunity.com/id/Mechanic_ID/",
        avatar="https://steamcdn-a.akamaihd.net/steamcommunity/public/images/avatars/f2/f254aa627953de54330823a2995d314766e1d843.jpg",
        avatarmedium="https://steamcdn-a.akamaihd.net/steamcommunity/public/images/avatars/f2/f254aa627953de54330823a2995d314766e1d843_medium.jpg",
        avatarfull="https://steamcdn-a.akamaihd.net/steamcommunity/public/images/avatars/f2/f254aa627953de54330823a2995d314766e1d843_full.jpg",
        avatarhash="f254aa627953de54330823a2995d314766e1d843",
        lastlogoff=1628124037,
        personastate=1,
        realname="███████████████",
        primaryclanid="103582791429521408",
        timecreated=1361598026,
        personastateflags=0,
        loccountrycode="RU",
        locstatecode="11",
        loccityid=39665
        )
    )
print(calc.records[0].__dict__)
'''