from datetime import date

from res.codes import keys

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
TODAY = date.today()  # ! .strftime(DATE_FMT)
UTF8 = 'utf-8'
