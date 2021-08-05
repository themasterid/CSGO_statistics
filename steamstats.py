from typing import Optional

import time
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
        steamid: Optional[str],
        communityvisibilitystate: Optional[str],
        profilestate: int = None,
        personaname: str = None,
        profileurl: str = None,
        avatar: str = None,
        avatarmedium: str = None,
        avatarfull: str = None,
        avatarhash: str = None,
        lastlogoff: str = None,
        personastate: int = None,
        realname: str = None,
        primaryclanid: str = None,
        timecreated: int = None,
        personastateflags: int = None,
        loccountrycode: str = None,
        locstatecode: str = None,
        loccityid: int = None
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
    def __init__(self) -> None:
        self.records: list = []

    def add_records(self, record: Record):
        self.records.append(record)


start_time = time.time()
steamid_l = [
    '76561198084621617',
    '76561198084621618',
    '76561198084621619',
    '76561198084621620',
    '76561198084621621',
    '76561198084621622',
    '66561198084621622'
    ]
calc = Calculator()
for i in steamid_l:
    url = f'{GPS}{i}'
    r = requests.get(url).json()
    print("--- %s seconds ---" % (time.time() - start_time))
    if r['response']['players'] == []:
        print('Not found!')
        continue

    steamid = r['response']['players'][0]['steamid']
    communityvisibilitystate = r['response']['players'][0]['communityvisibilitystate']
    try:
        profilestate = r['response']['players'][0]['profilestate']
    except KeyError:
        profilestate = None

    personaname = r['response']['players'][0]['personaname']
    profileurl = r['response']['players'][0]['profileurl']
    avatar = r['response']['players'][0]['avatar']
    avatarmedium = r['response']['players'][0]['avatarmedium']
    avatarfull = r['response']['players'][0]['avatarfull']
    avatarhash = r['response']['players'][0]['avatarhash']
    try:
        lastlogoff = r['response']['players'][0]['lastlogoff']
    except KeyError:
        lastlogoff = None
    personastate = r['response']['players'][0]['personastate']
    try:
        realname = r['response']['players'][0]['realname']
    except KeyError:
        realname = None
    primaryclanid = r['response']['players'][0]['primaryclanid']
    timecreated = r['response']['players'][0]['timecreated']
    personastateflags = r['response']['players'][0]['personastateflags']
    try:
        loccountrycode = r['response']['players'][0]['loccountrycode']
    except KeyError:
        loccountrycode = None
    try:
        locstatecode = r['response']['players'][0]['locstatecode']
    except KeyError:
        locstatecode = None
    try:
        loccityid = r['response']['players'][0]['loccityid']
    except KeyError:
        loccityid = None

    calc.add_records(
        Record(
            steamid,
            communityvisibilitystate,
            profilestate,
            personaname,
            profileurl,
            avatar,
            avatarmedium,
            avatarfull,
            avatarhash,
            lastlogoff,
            personastate,
            realname,
            primaryclanid,
            timecreated,
            personastateflags,
            loccountrycode,
            locstatecode,
            loccityid
            )
        )

# for i in calc.records:
#    print(i.__dict__)
#    print()
print("--- %s seconds ---" % (time.time() - start_time))